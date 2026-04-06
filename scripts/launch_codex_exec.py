from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"
TMP_RUNS_DIR = Path("/tmp") / "worker-critic-example-runs"
RUN_AGENTS_TEMPLATE = REPO_ROOT / "run-AGENTS.md"
REASONING_EFFORT = "xhigh"
MODEL = "gpt-5.4"
SEED_PATHS = (
    ".python-version",
    ".gitignore",
    "LICENSE",
    "README.md",
    "inputs",
    "main.py",
    "prompts",
    "pyproject.toml",
    "run-AGENTS.md",
    "scripts",
    "uv.lock",
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
            "using one persistent same-model critic session that is reused across review rounds "
            "until the critic explicitly returns `Approved.`."
        ),
    ),
    "external": Condition(
        prompt_path=PROMPTS_DIR / "generate-master-figure-with-external-review.md",
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex`, "
            "using one persistent worker session and an external `gpt-5.4-pro` review loop that "
            "receives the current SVG plus prior review history until the reviewer explicitly "
            "returns `Approved.`."
        ),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a detached codex exec run in an isolated temp workspace.")
    parser.add_argument("condition", choices=sorted(CONDITIONS), help="Benchmark condition to run.")
    parser.add_argument("--label", default="", help="Optional suffix to append to the run id.")
    parser.add_argument(
        "--workspace-root",
        default=str(TMP_RUNS_DIR),
        help="Parent directory for detached temp workspaces.",
    )
    return parser.parse_args()


def run(cmd: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def make_run_id(condition: str, label: str) -> str:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    suffix = f"-{label}" if label else ""
    return f"{stamp}-{condition}{suffix}"


def copy_seed_path(relative_path: str, destination_root: Path) -> None:
    source = REPO_ROOT / relative_path
    destination = destination_root / relative_path
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def create_workspace(workspace_path: Path) -> None:
    workspace_path.parent.mkdir(parents=True, exist_ok=True)
    if workspace_path.exists():
        raise FileExistsError(f"Workspace already exists: {workspace_path}")

    workspace_path.mkdir(parents=True, exist_ok=False)
    for relative_path in SEED_PATHS:
        copy_seed_path(relative_path, workspace_path)

    subprocess.run(["git", "init", "-b", "main"], cwd=workspace_path, check=True)


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


def seed_initial_commit(workspace_path: Path) -> str:
    subprocess.run(["git", "add", *SEED_PATHS, "AGENTS.md"], cwd=workspace_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Seed isolated detached run workspace"],
        cwd=workspace_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return run(["git", "rev-parse", "HEAD"], cwd=workspace_path)


def launch_codex(prompt_text: str, workspace_path: Path, run_root: Path) -> int:
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
            str(workspace_path),
            "-m",
            MODEL,
            "-c",
            f'model_reasoning_effort="{REASONING_EFFORT}"',
            "-o",
            str(last_message_path),
            "-",
        ],
        cwd=workspace_path,
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
    workspace_root = Path(args.workspace_root).expanduser()
    workspace_path = workspace_root / run_id
    run_root = workspace_path / "runs" / run_id
    prompt_source = load_prompt(condition.prompt_path)
    prompt_used = prompt_source + "\n\n" + build_run_addendum(run_id) + "\n"

    create_workspace(workspace_path)
    run_root.mkdir(parents=True, exist_ok=True)

    run_agents = build_run_agents(condition, run_id)
    write_text(workspace_path / "AGENTS.md", run_agents + "\n")
    write_text(run_root / "run-agents-used.md", run_agents + "\n")
    write_text(run_root / "prompt-source.md", prompt_source + "\n")
    write_text(run_root / "prompt-used.md", prompt_used)
    workspace_commit = seed_initial_commit(workspace_path)

    pid = launch_codex(prompt_used, workspace_path, run_root)

    launch_metadata = {
        "run_id": run_id,
        "condition": args.condition,
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "source_git_commit": run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT),
        "workspace_git_commit": workspace_commit,
        "workspace_root": str(workspace_root),
        "workspace": str(workspace_path),
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
