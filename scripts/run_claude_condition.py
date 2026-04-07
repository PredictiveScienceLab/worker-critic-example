from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

from review_prompt import build_review_prompt, load_review_history, read_text, write_review_outputs


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"
RUN_CLAUDE_TEMPLATE = REPO_ROOT / "run-CLAUDE.md"

DEFAULT_WORKER_MODEL = os.environ.get("CLAUDE_WORKER_MODEL") or os.environ.get(
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "claude-opus-4-6",
)
DEFAULT_EXTERNAL_CRITIC_MODEL = os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "claude-opus-4-6")
DEFAULT_EFFORT = "max"

WORKING_ARTIFACT_DIR = Path("artifacts/master-figure")
WORKING_PNG = WORKING_ARTIFACT_DIR / "master-figure.png"
WORKING_SVG = WORKING_ARTIFACT_DIR / "master-figure.svg"
WORKING_NOTES = WORKING_ARTIFACT_DIR / "notes.md"


@dataclass(frozen=True)
class Condition:
    objective: str
    reviewed_artifact_dir: Path


CONDITIONS = {
    "base": Condition(
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex` "
            "without using any critic."
        ),
        reviewed_artifact_dir=WORKING_ARTIFACT_DIR,
    ),
    "critic": Condition(
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex` "
            "and revise it across review rounds while one persistent Claude critic session "
            "reviews the SVG until it explicitly returns `Approved.`."
        ),
        reviewed_artifact_dir=Path("artifacts/master-figure-reviewed"),
    ),
    "external": Condition(
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex` "
            "and revise it across review rounds while an external Claude Opus reviewer "
            "reviews the SVG until it explicitly returns `Approved.`."
        ),
        reviewed_artifact_dir=Path("artifacts/master-figure-external-review"),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one benchmark condition using Claude Code.")
    parser.add_argument("condition", choices=sorted(CONDITIONS), help="Benchmark condition to execute.")
    parser.add_argument("--run-id", required=True, help="Run identifier, usually the temp workspace directory name.")
    parser.add_argument(
        "--worker-model",
        default=DEFAULT_WORKER_MODEL,
        help="Claude Code model to use for the worker session.",
    )
    parser.add_argument(
        "--critic-model",
        default="",
        help="Claude Code model for the persistent critic in Condition B. Defaults to the worker model.",
    )
    parser.add_argument(
        "--external-critic-model",
        default=DEFAULT_EXTERNAL_CRITIC_MODEL,
        help="Anthropic Foundry model for the external reviewer in Condition C.",
    )
    parser.add_argument(
        "--effort",
        default=DEFAULT_EFFORT,
        choices=("low", "medium", "high", "max"),
        help="Claude Code reasoning effort.",
    )
    parser.add_argument(
        "--max-review-rounds",
        type=int,
        default=0,
        help="Optional review-round cap. Leave at 0 to require explicit approval only.",
    )
    return parser.parse_args()


def run_root_for(run_id: str) -> Path:
    return REPO_ROOT / "runs" / run_id


def ensure_layout(run_root: Path, reviewed_artifact_dir: Path) -> None:
    for path in (
        WORKING_ARTIFACT_DIR,
        reviewed_artifact_dir,
        run_root / "prompts",
        run_root / "logs",
        run_root / "messages",
        run_root / "intermediate",
        run_root / "reviews",
        run_root / "final",
    ):
        path.mkdir(parents=True, exist_ok=True)


def next_index(directory: Path, suffix: str) -> int:
    existing = sorted(directory.glob(f"*{suffix}"))
    if not existing:
        return 1
    last = existing[-1].name.split("-", 1)[0]
    try:
        return int(last) + 1
    except ValueError:
        return len(existing) + 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_progress(run_root: Path, line: str) -> None:
    progress_path = run_root / "progress.md"
    if not progress_path.exists():
        write_text(progress_path, "# Progress Log\n\n")
    with progress_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {line}\n")


def load_worker_system_prompt(condition: Condition, run_id: str) -> str:
    rendered_path = REPO_ROOT / "CLAUDE.md"
    if rendered_path.exists():
        return read_text(rendered_path).strip()
    template = read_text(RUN_CLAUDE_TEMPLATE).strip()
    return template.format(objective=condition.objective, run_root=f"runs/{run_id}")


def build_initial_worker_prompt(run_id: str) -> str:
    return (
        read_text(PROMPTS_DIR / "generate-master-figure.md").strip()
        + "\n\n"
        + f"""
## Run bookkeeping

This run uses `artifacts/master-figure/` as its working artifact directory.

In addition to the required deliverables, maintain the run record under:

- `runs/{run_id}/progress.md`
- `runs/{run_id}/intermediate/`
- `runs/{run_id}/reviews/`
- `runs/{run_id}/final/`

Requirements:

- Keep a short chronological execution log in `runs/{run_id}/progress.md`.
- If you need durable memory, create it yourself under `runs/{run_id}/`, preferably in `memory.md` and `todo.md`.
- Save zero-padded intermediate SVG and PNG drafts under `runs/{run_id}/intermediate/` whenever you make a substantial visual revision inside this invocation.
- Keep the current working files at:
  - `artifacts/master-figure/master-figure.svg`
  - `artifacts/master-figure/master-figure.png`
  - `artifacts/master-figure/notes.md`
- This invocation should produce the best current draft. Do not spawn your own reviewer or external API critic; any later review loop is orchestrated outside this Claude call.
""".strip()
    )


def build_revision_worker_prompt(run_id: str, review_text: str, round_index: int) -> str:
    return f"""
Continue the same master-figure task in this workspace.

Latest review round: {round_index}

The current working files are:

- `artifacts/master-figure/master-figure.svg`
- `artifacts/master-figure/master-figure.png`
- `artifacts/master-figure/notes.md`

Revise those working files in place so they address the latest review. Preserve parts of the figure that are already working well.

Before replacing a substantial draft, save the outgoing version under `runs/{run_id}/intermediate/` using the next zero-padded filenames.

Update `notes.md` with a brief record of what changed in response to this review.

Latest review:

<review_round>
{review_text.strip()}
</review_round>

When you finish the revision, keep the updated files in `artifacts/master-figure/` and reply with a short summary of the changes you made.
""".strip()


CRITIC_SYSTEM_PROMPT = """
You are a persistent figure critic. Your only job is to review the proposal figure materials sent to you and return the required verdict format. Do not edit files yourself. Treat later review prompts in the same session as continuations of one review thread.
""".strip()


def build_claude_command(
    *,
    prompt: str,
    session_id: str,
    model: str,
    effort: str,
    resume: bool,
    system_prompt: str | None,
) -> list[str]:
    cmd = [
        "claude",
        "-p",
        "--verbose",
        "--output-format",
        "stream-json",
        "--model",
        model,
        "--effort",
        effort,
        "--permission-mode",
        "bypassPermissions",
        "--dangerously-skip-permissions",
        "--setting-sources",
        "project",
    ]
    if resume:
        cmd.extend(["--resume", session_id])
    else:
        cmd.extend(["--session-id", session_id])
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])
    cmd.append(prompt)
    return cmd


def extract_last_assistant_text(stream_output: str) -> str:
    last_text = ""
    for line in stream_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "assistant":
            continue
        if record.get("parent_tool_use_id") is not None:
            continue
        message = record.get("message", {})
        for content in message.get("content", []):
            if content.get("type") == "text":
                text = content.get("text", "").strip()
                if text:
                    last_text = text
    return last_text


def invoke_claude(
    *,
    prompt: str,
    session_id: str,
    model: str,
    effort: str,
    resume: bool,
    system_prompt: str | None,
    log_stem: Path,
) -> str:
    stdout_path = log_stem.with_suffix(".jsonl")
    stderr_path = log_stem.with_suffix(".stderr.log")
    command_path = log_stem.with_suffix(".command.sh")
    env = dict(os.environ)
    env["CLAUDE_CODE_USE_FOUNDRY"] = "1"

    cmd = build_claude_command(
        prompt=prompt,
        session_id=session_id,
        model=model,
        effort=effort,
        resume=resume,
        system_prompt=system_prompt,
    )
    write_text(command_path, " ".join(subprocess.list2cmdline([part]) for part in cmd))

    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    write_text(stdout_path, completed.stdout)
    write_text(stderr_path, completed.stderr)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Claude invocation failed for {log_stem.name}: {completed.returncode}\n{completed.stderr.strip()}"
        )

    return extract_last_assistant_text(completed.stdout)


def ensure_working_files() -> None:
    missing = [path for path in (WORKING_PNG, WORKING_SVG, WORKING_NOTES) if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing expected working files: {', '.join(str(path) for path in missing)}")


def archive_current_artifacts(run_root: Path) -> int:
    ensure_working_files()
    index = next_index(run_root / "intermediate", "-master-figure.svg")
    svg_dest = run_root / "intermediate" / f"{index:04d}-master-figure.svg"
    png_dest = run_root / "intermediate" / f"{index:04d}-master-figure.png"
    shutil.copy2(WORKING_SVG, svg_dest)
    shutil.copy2(WORKING_PNG, png_dest)
    return index


def append_review_history_to_notes(
    source_notes: Path,
    destination_notes: Path,
    review_paths: list[Path],
) -> None:
    if not review_paths:
        if source_notes.resolve() != destination_notes.resolve():
            shutil.copy2(source_notes, destination_notes)
        return
    content = source_notes.read_text(encoding="utf-8").rstrip()
    review_blocks = []
    for review_path in review_paths:
        review_blocks.append(f"## {review_path.name}\n\n{review_path.read_text(encoding='utf-8').rstrip()}")
    combined = content + "\n\n# Review History\n\n" + "\n\n".join(review_blocks) + "\n"
    write_text(destination_notes, combined)


def finalize_outputs(run_root: Path, reviewed_artifact_dir: Path) -> None:
    reviewed_artifact_dir.mkdir(parents=True, exist_ok=True)
    reviewed_png = reviewed_artifact_dir / "master-figure.png"
    reviewed_svg = reviewed_artifact_dir / "master-figure.svg"
    if WORKING_PNG.resolve() != reviewed_png.resolve():
        shutil.copy2(WORKING_PNG, reviewed_png)
    if WORKING_SVG.resolve() != reviewed_svg.resolve():
        shutil.copy2(WORKING_SVG, reviewed_svg)

    review_paths = sorted((run_root / "reviews").glob("*-review.md"))
    append_review_history_to_notes(WORKING_NOTES, reviewed_artifact_dir / "notes.md", review_paths)

    final_dir = run_root / "final"
    shutil.copy2(reviewed_artifact_dir / "master-figure.png", final_dir / "master-figure.png")
    shutil.copy2(reviewed_artifact_dir / "master-figure.svg", final_dir / "master-figure.svg")
    shutil.copy2(reviewed_artifact_dir / "notes.md", final_dir / "notes.md")


def record_sessions(run_root: Path, worker_session_id: str, critic_session_id: str | None) -> None:
    write_text(run_root / "worker-session-id.txt", worker_session_id + "\n")
    if critic_session_id:
        write_text(run_root / "critic-session-id.txt", critic_session_id + "\n")


def same_model_critic_review(
    *,
    proposal_path: Path,
    svg_path: Path,
    run_root: Path,
    critic_session_id: str,
    model: str,
    effort: str,
    round_index: int,
) -> tuple[str, dict[str, object]]:
    review_history = load_review_history(run_root / "reviews", history_limit=0)
    prompt_text = build_review_prompt(read_text(proposal_path), read_text(svg_path), review_history)
    prompt_path = run_root / "prompts" / f"critic-{round_index:04d}.md"
    write_text(prompt_path, prompt_text)
    log_stem = run_root / "logs" / f"critic-{round_index:04d}"
    review_text = invoke_claude(
        prompt=prompt_text,
        session_id=critic_session_id,
        model=model,
        effort=effort,
        resume=round_index > 1,
        system_prompt=CRITIC_SYSTEM_PROMPT,
        log_stem=log_stem,
    )
    message_path = run_root / "messages" / f"critic-{round_index:04d}.md"
    write_text(message_path, review_text + "\n")
    parsed = write_review_outputs(
        run_root / "reviews" / f"{round_index:04d}-review.md",
        run_root / "reviews" / f"{round_index:04d}-review.json",
        review_text,
    )
    return review_text, parsed


def external_critic_review(
    *,
    proposal_path: Path,
    svg_path: Path,
    run_root: Path,
    model: str,
    round_index: int,
) -> tuple[str, dict[str, object]]:
    log_stem = run_root / "logs" / f"external-review-{round_index:04d}"
    command = [
        "uv",
        "run",
        "python",
        "scripts/anthropic_review.py",
        "--proposal",
        str(proposal_path),
        "--svg",
        str(svg_path),
        "--output-md",
        str(run_root / "reviews" / f"{round_index:04d}-review.md"),
        "--output-json",
        str(run_root / "reviews" / f"{round_index:04d}-review.json"),
        "--history-dir",
        str(run_root / "reviews"),
        "--model",
        model,
    ]
    write_text(log_stem.with_suffix(".command.sh"), " ".join(subprocess.list2cmdline([part]) for part in command))
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        env=dict(os.environ),
    )
    write_text(log_stem.with_suffix(".stdout.log"), completed.stdout)
    write_text(log_stem.with_suffix(".stderr.log"), completed.stderr)
    if completed.returncode != 0:
        raise RuntimeError(
            f"External critic failed for round {round_index}: {completed.returncode}\n{completed.stderr.strip()}"
        )

    review_md = run_root / "reviews" / f"{round_index:04d}-review.md"
    review_json = run_root / "reviews" / f"{round_index:04d}-review.json"
    review_text = read_text(review_md).strip()
    parsed = json.loads(read_text(review_json))
    return review_text, parsed


def run_worker_call(
    *,
    worker_session_id: str,
    model: str,
    effort: str,
    prompt_text: str,
    system_prompt: str | None,
    resume: bool,
    run_root: Path,
    call_index: int,
) -> str:
    prompt_path = run_root / "prompts" / f"worker-{call_index:04d}.md"
    write_text(prompt_path, prompt_text)
    log_stem = run_root / "logs" / f"worker-{call_index:04d}"
    message = invoke_claude(
        prompt=prompt_text,
        session_id=worker_session_id,
        model=model,
        effort=effort,
        resume=resume,
        system_prompt=system_prompt,
        log_stem=log_stem,
    )
    write_text(run_root / "messages" / f"worker-{call_index:04d}.md", message + "\n")
    write_text(run_root / "claude-last-message.md", message + "\n")
    ensure_working_files()
    archive_index = archive_current_artifacts(run_root)
    append_progress(run_root, f"Worker invocation {call_index} completed; archived working draft as {archive_index:04d}.")
    return message


def main() -> None:
    args = parse_args()
    condition = CONDITIONS[args.condition]
    run_root = run_root_for(args.run_id)
    ensure_layout(run_root, condition.reviewed_artifact_dir)
    append_progress(run_root, f"Starting Claude condition `{args.condition}` with worker model `{args.worker_model}`.")

    worker_session_id = str(uuid.uuid4())
    critic_session_id = str(uuid.uuid4()) if args.condition == "critic" else None
    record_sessions(run_root, worker_session_id, critic_session_id)

    worker_system_prompt = load_worker_system_prompt(condition, args.run_id)
    worker_call_index = 1
    worker_message = run_worker_call(
        worker_session_id=worker_session_id,
        model=args.worker_model,
        effort=args.effort,
        prompt_text=build_initial_worker_prompt(args.run_id),
        system_prompt=worker_system_prompt,
        resume=False,
        run_root=run_root,
        call_index=worker_call_index,
    )
    append_progress(run_root, f"Initial worker draft complete: {worker_message or 'no summary text returned'}.")

    if args.condition == "base":
        finalize_outputs(run_root, condition.reviewed_artifact_dir)
        append_progress(run_root, "Base condition completed without critique.")
        return

    review_round = 0
    while True:
        review_round += 1
        if args.max_review_rounds and review_round > args.max_review_rounds:
            raise RuntimeError(f"Reached review-round cap of {args.max_review_rounds} without approval.")

        append_progress(run_root, f"Starting review round {review_round}.")
        if args.condition == "critic":
            review_text, parsed = same_model_critic_review(
                proposal_path=Path("inputs/project_description.tex"),
                svg_path=WORKING_SVG,
                run_root=run_root,
                critic_session_id=critic_session_id or "",
                model=args.critic_model or args.worker_model,
                effort=args.effort,
                round_index=review_round,
            )
        else:
            review_text, parsed = external_critic_review(
                proposal_path=Path("inputs/project_description.tex"),
                svg_path=WORKING_SVG,
                run_root=run_root,
                model=args.external_critic_model,
                round_index=review_round,
            )

        append_progress(run_root, f"Review round {review_round} returned `{parsed['status']}`.")
        if parsed.get("approved"):
            finalize_outputs(run_root, condition.reviewed_artifact_dir)
            append_progress(run_root, f"Condition `{args.condition}` approved in round {review_round}.")
            break

        worker_call_index += 1
        worker_message = run_worker_call(
            worker_session_id=worker_session_id,
            model=args.worker_model,
            effort=args.effort,
            prompt_text=build_revision_worker_prompt(args.run_id, review_text, review_round),
            system_prompt=None,
            resume=True,
            run_root=run_root,
            call_index=worker_call_index,
        )
        append_progress(
            run_root,
            f"Worker completed revision after review round {review_round}: {worker_message or 'no summary text returned'}.",
        )


if __name__ == "__main__":
    main()
