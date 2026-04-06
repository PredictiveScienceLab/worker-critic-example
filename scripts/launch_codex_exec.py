from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"
WORKTREES_DIR = REPO_ROOT / "bench_worktrees"
RUN_AGENTS_TEMPLATE = REPO_ROOT / "run-AGENTS.md"
REASONING_EFFORT = "xhigh"
MODEL = "gpt-5.4"
SPARSE_PATTERNS = (
    "/.gitignore",
    "/LICENSE",
    "/README.md",
    "/inputs/",
    "/main.py",
    "/prompts/",
    "/pyproject.toml",
    "/run-AGENTS.md",
    "/scripts/",
    "/uv.lock",
)


@dataclass(frozen=True)
class Condition:
    prompt_path: Path
    objective: str


CONDITIONS = {
    "base": Condition(
        prompt_path=PROMPTS_DIR / "generate-master-figure.md",
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex` "
            "without using a critic subagent or an external reviewer."
        ),
    ),
    "critic": Condition(
        prompt_path=PROMPTS_DIR / "generate-master-figure-with-critic.md",
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex`, "
            "using the same-model critic loop until the critic explicitly returns `Approved.`."
        ),
    ),
    "external": Condition(
        prompt_path=PROMPTS_DIR / "generate-master-figure-with-external-review.md",
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex`, "
            "using the external `gpt-5.4-pro` review loop until the reviewer explicitly returns "
            "`Approved.`."
        ),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a detached codex exec run in an isolated worktree.")
    parser.add_argument("condition", choices=sorted(CONDITIONS), help="Benchmark condition to run.")
    parser.add_argument("--label", default="", help="Optional suffix to append to the run id.")
    return parser.parse_args()


def run(cmd: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def make_run_id(condition: str, label: str) -> str:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    suffix = f"-{label}" if label else ""
    return f"{stamp}-{condition}{suffix}"


def create_worktree(worktree_path: Path) -> None:
    WORKTREES_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "config", "extensions.worktreeConfig", "true"],
        cwd=REPO_ROOT,
        check=True,
    )
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_path), "HEAD"],
        cwd=REPO_ROOT,
        check=True,
    )


def configure_sparse_checkout(worktree_path: Path) -> None:
    subprocess.run(
        ["git", "sparse-checkout", "init", "--no-cone"],
        cwd=worktree_path,
        check=True,
    )
    subprocess.run(
        ["git", "sparse-checkout", "set", "--no-cone", *SPARSE_PATTERNS],
        cwd=worktree_path,
        check=True,
    )


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_run_agents_template() -> str:
    return RUN_AGENTS_TEMPLATE.read_text(encoding="utf-8").strip()


def build_run_addendum(run_id: str) -> str:
    run_root = f"runs/{run_id}"
    return f"""
## Run bookkeeping

In addition to the required deliverables, save all substantial intermediate results for this run under:

- `{run_root}/progress.md`
- `{run_root}/intermediate/`
- `{run_root}/reviews/`
- `{run_root}/final/`

Requirements:

- Write a short chronological progress log to `{run_root}/progress.md`.
- If you need durable run-local memory, create it yourself under `{run_root}/`, preferably in `{run_root}/memory.md` and `{run_root}/todo.md`.
- Before replacing any substantial figure draft, save the prior draft in `{run_root}/intermediate/` using zero-padded filenames.
- Save any critic or reviewer responses in `{run_root}/reviews/` using zero-padded filenames.
- At the end, copy the final `PNG`, `SVG`, and notes file into `{run_root}/final/`.
- Do not delete or overwrite earlier intermediate files; create new numbered files instead.
""".strip()


def build_run_agents(condition: Condition, run_id: str) -> str:
    run_root = f"runs/{run_id}"
    template = load_run_agents_template()
    return template.format(objective=condition.objective, run_root=run_root)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def launch_codex(prompt_text: str, worktree_path: Path, run_root: Path) -> int:
    stdout_path = run_root / "codex-events.jsonl"
    stderr_path = run_root / "codex-stderr.log"
    last_message_path = run_root / "codex-last-message.md"

    stdout_handle = stdout_path.open("w", encoding="utf-8")
    stderr_handle = stderr_path.open("w", encoding="utf-8")

    process = subprocess.Popen(
        [
            "codex",
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--json",
            "-C",
            str(worktree_path),
            "-m",
            MODEL,
            "-c",
            f'model_reasoning_effort="{REASONING_EFFORT}"',
            "-o",
            str(last_message_path),
            "-",
        ],
        cwd=worktree_path,
        stdin=subprocess.PIPE,
        stdout=stdout_handle,
        stderr=stderr_handle,
        text=True,
        start_new_session=True,
        env=os.environ.copy(),
    )

    assert process.stdin is not None
    process.stdin.write(prompt_text)
    process.stdin.close()

    stdout_handle.close()
    stderr_handle.close()
    return process.pid


def main() -> None:
    args = parse_args()
    condition = CONDITIONS[args.condition]
    run_id = make_run_id(args.condition, args.label)
    worktree_path = WORKTREES_DIR / run_id
    run_root = worktree_path / "runs" / run_id
    prompt_source = load_prompt(condition.prompt_path)
    prompt_used = prompt_source + "\n\n" + build_run_addendum(run_id) + "\n"

    create_worktree(worktree_path)
    configure_sparse_checkout(worktree_path)
    run_root.mkdir(parents=True, exist_ok=True)

    run_agents = build_run_agents(condition, run_id)
    write_text(worktree_path / "AGENTS.md", run_agents + "\n")
    write_text(run_root / "run-agents-used.md", run_agents + "\n")
    write_text(run_root / "prompt-source.md", prompt_source + "\n")
    write_text(run_root / "prompt-used.md", prompt_used)

    pid = launch_codex(prompt_used, worktree_path, run_root)

    launch_metadata = {
        "run_id": run_id,
        "condition": args.condition,
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "git_commit": run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT),
        "worktree": str(worktree_path),
        "run_root": str(run_root),
        "pid": pid,
        "prompt_source": str(condition.prompt_path.relative_to(REPO_ROOT)),
        "run_agents": "AGENTS.md",
        "launched_at": datetime.now().astimezone().isoformat(),
    }
    write_text(run_root / "launch.json", json.dumps(launch_metadata, indent=2) + "\n")
    write_text(run_root / "pid.txt", f"{pid}\n")

    print(json.dumps(launch_metadata, indent=2))


if __name__ == "__main__":
    main()
