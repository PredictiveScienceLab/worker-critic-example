from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "autoresearch"
CURRENT_DIR = ARTIFACT_ROOT / "current"
RUNS_DIR = ARTIFACT_ROOT / "runs"
SEED_FILES = (
    ".python-version",
    "plot.py",
    "prepare.py",
    "program.md",
    "pyproject.toml",
    "uv.lock",
)
WRITER_MODEL = "gpt-5.4"
WRITER_REASONING_EFFORT = "xhigh"
EPSILON = 1e-6


@dataclass(frozen=True)
class ScoreSnapshot:
    average: float
    weakest: float
    scores: dict[str, float]
    accepted: bool
    summary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an autoresearch-style loop over plot.py.")
    parser.add_argument("--iterations", type=int, default=20, help="Number of writer iterations to run.")
    parser.add_argument("--run-id", default="", help="Optional explicit run id.")
    parser.add_argument(
        "--workspace-root",
        default="/tmp/autoresearch-worker-critic",
        help="Parent directory for isolated iteration workspaces.",
    )
    parser.add_argument("--writer-model", default=WRITER_MODEL, help="Codex model for the writer.")
    parser.add_argument(
        "--writer-reasoning-effort",
        default=WRITER_REASONING_EFFORT,
        help="Reasoning effort for the writer.",
    )
    parser.add_argument(
        "--refresh-baseline",
        action="store_true",
        help="Re-render and re-score the repo baseline before starting.",
    )
    return parser.parse_args()


def timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def run(cmd: list[str], *, cwd: Path, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def append_progress(path: Path, line: str) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"- [{timestamp()}] {line}\n")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_score_snapshot(review_path: Path) -> ScoreSnapshot:
    payload = read_json(review_path)
    review = payload["review"]
    criteria = review["criteria"]
    scores = {key: float(value["score"]) for key, value in criteria.items()}
    return ScoreSnapshot(
        average=float(payload["average_score"]),
        weakest=min(scores.values()),
        scores=scores,
        accepted=bool(payload["accepted"]),
        summary=str(review["summary"]),
    )


def make_run_id(explicit: str) -> str:
    if explicit:
        return explicit
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-autoresearch"


def refresh_repo_baseline(progress_path: Path) -> None:
    append_progress(progress_path, "Refreshing repo baseline with `uv run python plot.py` and `uv run python prepare.py`.")
    plot_result = run(["uv", "run", "python", "plot.py"], cwd=REPO_ROOT)
    if plot_result.returncode != 0:
        raise RuntimeError(
            "Refreshing baseline plot failed.\n"
            f"stdout:\n{plot_result.stdout}\n\nstderr:\n{plot_result.stderr}"
        )
    prepare_result = run(["uv", "run", "python", "prepare.py"], cwd=REPO_ROOT)
    if prepare_result.returncode != 0:
        raise RuntimeError(
            "Refreshing baseline review failed.\n"
            f"stdout:\n{prepare_result.stdout}\n\nstderr:\n{prepare_result.stderr}"
        )


def ensure_baseline_exists() -> None:
    required = (
        REPO_ROOT / "plot.py",
        REPO_ROOT / "prepare.py",
        REPO_ROOT / "program.md",
        CURRENT_DIR / "figure.svg",
        CURRENT_DIR / "figure.png",
        CURRENT_DIR / "review.json",
        CURRENT_DIR / "review.md",
    )
    missing = [path for path in required if not path.exists()]
    if missing:
        joined = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Autoresearch baseline is incomplete. Missing:\n{joined}")


def copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def copy_file(source: Path, destination: Path) -> None:
    ensure_dir(destination.parent)
    shutil.copy2(source, destination)


def seed_run_baseline(run_root: Path) -> tuple[Path, Path]:
    baseline_root = run_root / "baseline"
    best_root = run_root / "best"
    copy_file(REPO_ROOT / "plot.py", baseline_root / "plot.py")
    copy_tree(CURRENT_DIR, baseline_root / "current")
    copy_file(REPO_ROOT / "plot.py", best_root / "plot.py")
    copy_tree(CURRENT_DIR, best_root / "current")
    return baseline_root, best_root


def build_agents_md() -> str:
    return """# AGENTS.md

You are improving one figure in an autoresearch-style loop.

## Objective

Improve `plot.py` so the fixed evaluator in `prepare.py` gives the figure a higher score.

## Rules

- Edit only `plot.py`.
- Do not edit `prepare.py`, `program.md`, or files outside `artifacts/autoresearch/current/`.
- Use `uv run python plot.py` to render locally when needed.
- Do not run or modify your own reviewer. The outer loop will evaluate the result.
- Keep changes focused on the worker-critic figure, not on surrounding repo infrastructure.

## Workspace

- This is an isolated temporary git repo for one iteration.
- You may use local git status and diffs to inspect your changes.
- If you want short durable notes, write them under `notes/`.
""".strip() + "\n"


def seed_iteration_workspace(workspace: Path, best_root: Path) -> None:
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=False)

    for relative in SEED_FILES:
        source = REPO_ROOT / relative
        destination = workspace / relative
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            copy_file(source, destination)

    copy_file(best_root / "plot.py", workspace / "plot.py")
    copy_tree(best_root / "current", workspace / "artifacts" / "autoresearch" / "current")
    write_text(workspace / "AGENTS.md", build_agents_md())
    write_text(workspace / "notes" / "memory.md", "")
    write_text(workspace / "notes" / "todo.md", "")

    subprocess.run(["git", "init", "-b", "main"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "autoresearch"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.email", "autoresearch@example.invalid"], cwd=workspace, check=True)
    subprocess.run(["git", "add", "."], cwd=workspace, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Seed iteration workspace"],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    )


def weakest_criterion(scores: dict[str, float]) -> tuple[str, float]:
    key = min(scores, key=scores.get)
    return key, float(scores[key])


def should_accept(candidate: ScoreSnapshot, best: ScoreSnapshot) -> tuple[bool, str]:
    if candidate.average > best.average + EPSILON:
        return True, "higher average score"
    if math.isclose(candidate.average, best.average, abs_tol=EPSILON) and candidate.weakest > best.weakest + EPSILON:
        return True, "same average, higher weakest criterion"
    return False, "no score improvement"


def build_writer_prompt(iteration: int, total: int, best_review: dict[str, object]) -> str:
    criteria = best_review["review"]["criteria"]
    weakest_key = min(criteria, key=lambda key: float(criteria[key]["score"]))
    weakest_score = float(criteria[weakest_key]["score"])
    average = float(best_review["average_score"])
    summary = str(best_review["review"]["summary"])
    return f"""
You are running iteration {iteration} of {total} of an autoresearch-style improvement loop.

Read:
- `AGENTS.md`
- `program.md`
- `artifacts/autoresearch/current/review.md`
- `artifacts/autoresearch/current/review.json`
- `plot.py`

Current best score:
- average: {average:.2f}
- weakest criterion: `{weakest_key}` = {weakest_score:.2f}
- reviewer summary: {summary}

Task:
- make one coherent improvement pass by editing only `plot.py`
- prioritize the reviewer feedback, especially the weakest criterion
- keep the figure as one wide panel explaining the worker-critic pattern in one glance
- reduce clutter before adding detail
- you may run `uv run python plot.py` to inspect your changes

Do not:
- edit `prepare.py`
- edit `program.md`
- invoke your own reviewer or change the scoring rubric

When you stop, leave `plot.py` in the best state you reached this iteration.
""".strip()


def run_writer(
    workspace: Path,
    iteration_root: Path,
    *,
    prompt: str,
    model: str,
    reasoning_effort: str,
) -> subprocess.CompletedProcess[str]:
    prompt_path = iteration_root / "writer-prompt.md"
    stdout_path = iteration_root / "codex-events.jsonl"
    stderr_path = iteration_root / "codex-stderr.log"
    last_message_path = iteration_root / "codex-last-message.md"
    write_text(prompt_path, prompt + "\n")
    with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
        completed = subprocess.run(
            [
                "codex",
                "exec",
                "--dangerously-bypass-approvals-and-sandbox",
                "--json",
                "-C",
                str(workspace),
                "-m",
                model,
                "-c",
                f'model_reasoning_effort="{reasoning_effort}"',
                "-o",
                str(last_message_path),
                "-",
            ],
            cwd=workspace,
            input=prompt,
            text=True,
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=False,
        )
    write_text(iteration_root / "writer-exit-code.txt", f"{completed.returncode}\n")
    return completed


def evaluate_candidate(workspace: Path, iteration_root: Path) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    plot_result = run(["uv", "run", "python", "plot.py"], cwd=workspace)
    write_text(iteration_root / "plot-stdout.log", plot_result.stdout)
    write_text(iteration_root / "plot-stderr.log", plot_result.stderr)
    write_text(iteration_root / "plot-exit-code.txt", f"{plot_result.returncode}\n")
    if plot_result.returncode != 0:
        return plot_result, subprocess.CompletedProcess(args=[], returncode=999, stdout="", stderr="")

    prepare_result = run(["uv", "run", "python", "prepare.py"], cwd=workspace)
    write_text(iteration_root / "prepare-stdout.log", prepare_result.stdout)
    write_text(iteration_root / "prepare-stderr.log", prepare_result.stderr)
    write_text(iteration_root / "prepare-exit-code.txt", f"{prepare_result.returncode}\n")
    return plot_result, prepare_result


def archive_iteration_state(workspace: Path, iteration_root: Path) -> None:
    current_source = workspace / "artifacts" / "autoresearch" / "current"
    current_dest = iteration_root / "current"
    copy_tree(current_source, current_dest)
    copy_file(workspace / "plot.py", iteration_root / "plot.py")


def write_status(path: Path, payload: dict[str, object]) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def main() -> None:
    args = parse_args()
    run_id = make_run_id(args.run_id)
    run_root = RUNS_DIR / run_id
    ensure_dir(run_root)
    progress_path = run_root / "progress.md"
    status_path = run_root / "status.json"
    write_text(progress_path, f"# Autoresearch Run `{run_id}`\n\n")

    write_status(
        status_path,
        {
            "run_id": run_id,
            "state": "starting",
            "iterations_total": args.iterations,
            "iterations_completed": 0,
            "started_at": timestamp(),
        },
    )

    if args.refresh_baseline:
        refresh_repo_baseline(progress_path)
    ensure_baseline_exists()
    baseline_root, best_root = seed_run_baseline(run_root)
    best_review_path = best_root / "current" / "review.json"
    best_review_payload = read_json(best_review_path)
    best_snapshot = load_score_snapshot(best_review_path)
    append_progress(
        progress_path,
        f"Seeded baseline with average score {best_snapshot.average:.2f} and weakest criterion {best_snapshot.weakest:.2f}.",
    )

    metadata = {
        "run_id": run_id,
        "iterations_total": args.iterations,
        "writer_model": args.writer_model,
        "writer_reasoning_effort": args.writer_reasoning_effort,
        "source_git_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "baseline_average_score": best_snapshot.average,
        "baseline_weakest_score": best_snapshot.weakest,
        "launched_at": timestamp(),
        "workspace_root": str(Path(args.workspace_root).expanduser()),
        "baseline_root": str(baseline_root),
        "best_root": str(best_root),
    }
    write_text(run_root / "launch.json", json.dumps(metadata, indent=2) + "\n")

    workspace_parent = Path(args.workspace_root).expanduser()
    ensure_dir(workspace_parent)
    iterations_dir = run_root / "iterations"
    ensure_dir(iterations_dir)

    best_iteration = 0
    for iteration in range(1, args.iterations + 1):
        iteration_name = f"{iteration:03d}"
        iteration_root = iterations_dir / iteration_name
        ensure_dir(iteration_root)
        workspace = workspace_parent / f"{run_id}-{iteration_name}"
        append_progress(progress_path, f"Starting iteration {iteration_name}.")
        write_status(
            status_path,
            {
                "run_id": run_id,
                "state": "running",
                "iterations_total": args.iterations,
                "iterations_completed": iteration - 1,
                "current_iteration": iteration,
                "phase": "writer",
                "best_average_score": best_snapshot.average,
                "best_iteration": best_iteration,
                "updated_at": timestamp(),
            },
        )

        seed_iteration_workspace(workspace, best_root)
        prompt = build_writer_prompt(iteration, args.iterations, best_review_payload)
        writer_result = run_writer(
            workspace,
            iteration_root,
            prompt=prompt,
            model=args.writer_model,
            reasoning_effort=args.writer_reasoning_effort,
        )

        if writer_result.returncode != 0:
            append_progress(progress_path, f"Iteration {iteration_name} writer failed with exit code {writer_result.returncode}.")
            archive_iteration_state(workspace, iteration_root)
            continue

        write_status(
            status_path,
            {
                "run_id": run_id,
                "state": "running",
                "iterations_total": args.iterations,
                "iterations_completed": iteration - 1,
                "current_iteration": iteration,
                "phase": "evaluation",
                "best_average_score": best_snapshot.average,
                "best_iteration": best_iteration,
                "updated_at": timestamp(),
            },
        )
        plot_result, prepare_result = evaluate_candidate(workspace, iteration_root)
        archive_iteration_state(workspace, iteration_root)

        if plot_result.returncode != 0:
            append_progress(progress_path, f"Iteration {iteration_name} render failed with exit code {plot_result.returncode}.")
            continue

        if prepare_result.returncode != 0:
            append_progress(progress_path, f"Iteration {iteration_name} evaluation failed with exit code {prepare_result.returncode}.")
            continue

        candidate_review_path = iteration_root / "current" / "review.json"
        candidate_review_payload = read_json(candidate_review_path)
        candidate_snapshot = load_score_snapshot(candidate_review_path)
        accepted, reason = should_accept(candidate_snapshot, best_snapshot)
        weakest_key, weakest_value = weakest_criterion(candidate_snapshot.scores)

        result_payload = {
            "iteration": iteration,
            "accepted": accepted,
            "decision_reason": reason,
            "average_score": candidate_snapshot.average,
            "weakest_criterion": weakest_key,
            "weakest_score": weakest_value,
            "scores": candidate_snapshot.scores,
            "summary": candidate_snapshot.summary,
        }
        write_text(iteration_root / "result.json", json.dumps(result_payload, indent=2) + "\n")

        if accepted:
            copy_file(iteration_root / "plot.py", best_root / "plot.py")
            copy_tree(iteration_root / "current", best_root / "current")
            best_review_payload = candidate_review_payload
            best_snapshot = candidate_snapshot
            best_iteration = iteration
            append_progress(
                progress_path,
                f"Iteration {iteration_name} accepted ({reason}); new best average {best_snapshot.average:.2f}, weakest {best_snapshot.weakest:.2f}.",
            )
        else:
            append_progress(
                progress_path,
                f"Iteration {iteration_name} rejected ({reason}); candidate average {candidate_snapshot.average:.2f}, weakest {candidate_snapshot.weakest:.2f}.",
            )

    final_root = run_root / "final"
    copy_file(best_root / "plot.py", final_root / "plot.py")
    copy_tree(best_root / "current", final_root / "current")
    summary_payload = {
        "run_id": run_id,
        "iterations_total": args.iterations,
        "best_iteration": best_iteration,
        "baseline_average_score": load_score_snapshot(baseline_root / "current" / "review.json").average,
        "final_average_score": best_snapshot.average,
        "final_weakest_score": best_snapshot.weakest,
        "accepted": best_snapshot.accepted,
        "finished_at": timestamp(),
    }
    write_text(run_root / "summary.json", json.dumps(summary_payload, indent=2) + "\n")
    append_progress(
        progress_path,
        f"Run finished. Best iteration: {best_iteration}. Final average score: {best_snapshot.average:.2f}.",
    )
    write_status(
        status_path,
        {
            "run_id": run_id,
            "state": "completed",
            "iterations_total": args.iterations,
            "iterations_completed": args.iterations,
            "best_iteration": best_iteration,
            "final_average_score": best_snapshot.average,
            "final_weakest_score": best_snapshot.weakest,
            "updated_at": timestamp(),
        },
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - runner should persist failure details
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
