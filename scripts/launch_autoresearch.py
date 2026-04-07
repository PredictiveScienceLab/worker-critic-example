from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "artifacts" / "autoresearch" / "runs"
TMUX_PREFIX = "autoresearch-worker-critic"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch an autoresearch run inside tmux.")
    parser.add_argument("--iterations", type=int, default=20, help="Number of iterations to run.")
    parser.add_argument(
        "--workspace-root",
        default="/tmp/autoresearch-worker-critic",
        help="Parent directory for isolated iteration workspaces.",
    )
    parser.add_argument("--run-id", default="", help="Optional explicit run id.")
    parser.add_argument("--refresh-baseline", action="store_true", help="Refresh the baseline before the run.")
    return parser.parse_args()


def ensure_tmux_available() -> None:
    if shutil.which("tmux") is None:
        raise RuntimeError("tmux is required but was not found on PATH.")


def make_run_id(explicit: str) -> str:
    if explicit:
        return explicit
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-autoresearch"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_wrapper(run_id: str, run_root: Path, workspace_root: str, iterations: int, refresh_baseline: bool) -> Path:
    script_path = run_root / "launch-in-tmux.sh"
    stdout_path = run_root / "runner.stdout.log"
    stderr_path = run_root / "runner.stderr.log"
    exit_code_path = run_root / "runner-exit-code.txt"
    finished_at_path = run_root / "runner-finished-at.txt"
    wrapper_log_path = run_root / "tmux-wrapper.log"

    refresh_flag = " --refresh-baseline" if refresh_baseline else ""
    command = (
        f"uv run python scripts/run_autoresearch.py "
        f"--iterations {iterations} "
        f"--run-id {shlex.quote(run_id)} "
        f"--workspace-root {shlex.quote(workspace_root)}"
        f"{refresh_flag}"
    )

    script = f"""#!/usr/bin/env bash
set -uo pipefail

cd {shlex.quote(str(REPO_ROOT))}

{{
  printf '[%s] launching autoresearch\\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  {command} > {shlex.quote(str(stdout_path))} 2> {shlex.quote(str(stderr_path))}
  exit_code=$?
  printf '%s\\n' "$exit_code" > {shlex.quote(str(exit_code_path))}
  date -u '+%Y-%m-%dT%H:%M:%SZ' > {shlex.quote(str(finished_at_path))}
  printf '[%s] autoresearch exited with code %s\\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$exit_code"
  exit "$exit_code"
}} >> {shlex.quote(str(wrapper_log_path))} 2>&1
"""
    write_text(script_path, script)
    script_path.chmod(0o755)
    return script_path


def main() -> None:
    args = parse_args()
    ensure_tmux_available()
    run_id = make_run_id(args.run_id)
    run_root = RUNS_DIR / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    session_name = f"{TMUX_PREFIX}-{run_id}"
    script_path = build_wrapper(run_id, run_root, args.workspace_root, args.iterations, args.refresh_baseline)

    subprocess.run(
        [
            "tmux",
            "new-session",
            "-d",
            "-s",
            session_name,
            "-c",
            str(REPO_ROOT),
            str(script_path),
        ],
        check=True,
    )
    pane_pid = int(
        subprocess.run(
            ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_pid}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    payload = {
        "run_id": run_id,
        "iterations": args.iterations,
        "tmux_session": session_name,
        "pane_pid": pane_pid,
        "run_root": str(run_root),
        "workspace_root": args.workspace_root,
        "refresh_baseline": args.refresh_baseline,
        "launched_at": datetime.now().astimezone().isoformat(),
    }
    write_text(run_root / "launch.json", json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
