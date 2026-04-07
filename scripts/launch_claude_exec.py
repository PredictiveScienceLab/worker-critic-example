from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TMP_RUNS_DIR = Path("/tmp") / "worker-critic-example-runs"
RUN_CLAUDE_TEMPLATE = REPO_ROOT / "run-CLAUDE.md"
DEFAULT_WORKER_MODEL = os.environ.get("CLAUDE_WORKER_MODEL") or os.environ.get(
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "claude-opus-4-6",
)
DEFAULT_EXTERNAL_CRITIC_MODEL = os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "claude-opus-4-6")
DEFAULT_EFFORT = "max"
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
    "run-CLAUDE.md",
    "scripts",
    "uv.lock",
)


@dataclass(frozen=True)
class Condition:
    objective: str


CONDITIONS = {
    "base": Condition(
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex` "
            "without any critic."
        ),
    ),
    "critic": Condition(
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex` and "
            "revise it in response to one persistent Claude critic session until the critic "
            "explicitly returns `Approved.`."
        ),
    ),
    "external": Condition(
        objective=(
            "Create a proposal-ready master figure from `inputs/project_description.tex` and "
            "revise it in response to an external Claude Opus reviewer until the reviewer "
            "explicitly returns `Approved.`."
        ),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a detached Claude Code benchmark run in an isolated temp workspace.")
    parser.add_argument("condition", choices=sorted(CONDITIONS), help="Benchmark condition to run.")
    parser.add_argument("--label", default="", help="Optional suffix to append to the run id.")
    parser.add_argument(
        "--workspace-root",
        default=str(TMP_RUNS_DIR),
        help="Parent directory for detached temp workspaces.",
    )
    parser.add_argument(
        "--worker-model",
        default=DEFAULT_WORKER_MODEL,
        help="Claude Code model for the worker session.",
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


def run(cmd: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def ensure_tmux_available() -> None:
    if shutil.which("tmux") is None:
        raise RuntimeError("tmux is required but was not found on PATH.")


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


def render_claude_md(condition: Condition, run_id: str) -> str:
    template = RUN_CLAUDE_TEMPLATE.read_text(encoding="utf-8").strip()
    return template.format(objective=condition.objective, run_root=f"runs/{run_id}")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def seed_initial_commit(workspace_path: Path) -> str:
    subprocess.run(["git", "add", *SEED_PATHS, "CLAUDE.md"], cwd=workspace_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Seed isolated Claude benchmark workspace"],
        cwd=workspace_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return run(["git", "rev-parse", "HEAD"], cwd=workspace_path)


def make_tmux_session_name(run_id: str) -> str:
    return f"worker-critic-claude-{run_id}"


def build_tmux_launch_script(
    *,
    workspace_path: Path,
    run_root: Path,
    run_id: str,
    args: argparse.Namespace,
) -> Path:
    stdout_path = run_root / "claude-run.stdout.log"
    stderr_path = run_root / "claude-run.stderr.log"
    last_message_path = run_root / "claude-last-message.md"
    exit_code_path = run_root / "claude-exit-code.txt"
    wrapper_log_path = run_root / "tmux-wrapper.log"
    finished_at_path = run_root / "claude-finished-at.txt"
    script_path = run_root / "launch-in-tmux.sh"

    command = [
        "uv",
        "run",
        "python",
        "scripts/run_claude_condition.py",
        args.condition,
        "--run-id",
        run_id,
        "--worker-model",
        args.worker_model,
        "--external-critic-model",
        args.external_critic_model,
        "--effort",
        args.effort,
        "--max-review-rounds",
        str(args.max_review_rounds),
    ]
    if args.critic_model:
        command.extend(["--critic-model", args.critic_model])

    command_str = " ".join(shlex.quote(part) for part in command)
    script = f"""#!/usr/bin/env bash
set -uo pipefail

cd {shlex.quote(str(workspace_path))}

{{
  printf '[%s] launching Claude run\\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  {command_str} \\
    > {shlex.quote(str(stdout_path))} \\
    2> {shlex.quote(str(stderr_path))}
  exit_code=$?
  printf '%s\\n' "$exit_code" > {shlex.quote(str(exit_code_path))}
  date -u '+%Y-%m-%dT%H:%M:%SZ' > {shlex.quote(str(finished_at_path))}
  if [ -f {shlex.quote(str(run_root / "claude-last-message.md"))} ]; then
    cp {shlex.quote(str(run_root / "claude-last-message.md"))} {shlex.quote(str(last_message_path))}
  fi
  printf '[%s] Claude run exited with code %s\\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$exit_code"
  exit "$exit_code"
}} >> {shlex.quote(str(wrapper_log_path))} 2>&1
"""
    write_text(script_path, script)
    script_path.chmod(0o755)
    return script_path


def launch_via_tmux(workspace_path: Path, run_root: Path, run_id: str, args: argparse.Namespace) -> tuple[str, int]:
    session_name = make_tmux_session_name(run_id)
    script_path = build_tmux_launch_script(
        workspace_path=workspace_path,
        run_root=run_root,
        run_id=run_id,
        args=args,
    )

    subprocess.run(
        [
            "tmux",
            "new-session",
            "-d",
            "-s",
            session_name,
            "-c",
            str(workspace_path),
            str(script_path),
        ],
        check=True,
    )

    pane_pid = int(
        run(
            [
                "tmux",
                "list-panes",
                "-t",
                session_name,
                "-F",
                "#{pane_pid}",
            ]
        )
    )
    return session_name, pane_pid


def main() -> None:
    args = parse_args()
    ensure_tmux_available()

    condition = CONDITIONS[args.condition]
    run_id = make_run_id(args.condition, args.label)
    workspace_root = Path(args.workspace_root).expanduser()
    workspace_path = workspace_root / run_id
    run_root = workspace_path / "runs" / run_id

    create_workspace(workspace_path)
    run_root.mkdir(parents=True, exist_ok=True)

    rendered_claude_md = render_claude_md(condition, run_id)
    write_text(workspace_path / "CLAUDE.md", rendered_claude_md)
    write_text(run_root / "run-claude-used.md", rendered_claude_md + "\n")

    seed_commit = seed_initial_commit(workspace_path)
    session_name, pane_pid = launch_via_tmux(workspace_path, run_root, run_id, args)

    launch_record = {
        "run_id": run_id,
        "condition": args.condition,
        "workspace_path": str(workspace_path),
        "run_root": str(run_root),
        "worker_model": args.worker_model,
        "critic_model": args.critic_model or args.worker_model,
        "external_critic_model": args.external_critic_model,
        "effort": args.effort,
        "max_review_rounds": args.max_review_rounds,
        "seed_commit": seed_commit,
        "tmux_session": session_name,
        "pane_pid": pane_pid,
    }
    write_text(run_root / "launch.json", json.dumps(launch_record, indent=2) + "\n")
    write_text(run_root / "pid.txt", f"{pane_pid}\n")

    print(json.dumps(launch_record, indent=2))


if __name__ == "__main__":
    main()
