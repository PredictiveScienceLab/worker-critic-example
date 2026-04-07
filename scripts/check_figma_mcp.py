#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "gpt-5.4"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a minimal Codex+Figma MCP preflight check."
    )
    parser.add_argument("--file-key", required=True, help="Figma file key to probe.")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Codex model to use for the probe. Defaults to {DEFAULT_MODEL}.",
    )
    return parser.parse_args()


def make_prompt(file_key: str) -> str:
    return f"""Use the Figma MCP server against file `{file_key}`.

Make exactly one `use_figma` call with a tiny read-only script that returns the current page name and child count.
Do not call `get_screenshot`.
Do not call `get_metadata`.
After the single `use_figma` call, stop.
"""


def parse_jsonl_events(stdout: str) -> dict[str, str | bool]:
    latest_match: dict[str, str | bool] | None = None
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if item.get("type") != "mcp_tool_call":
            continue
        if item.get("server") != "figma" or item.get("tool") != "use_figma":
            continue
        status = item.get("status")
        if status == "in_progress":
            continue
        error = item.get("error")
        result = item.get("result")
        if status == "completed" and not error:
            latest_match = {
                "ok": True,
                "status": "completed",
                "message": "Figma MCP `use_figma` succeeded.",
                "result": json.dumps(result) if result is not None else "",
            }
            continue
        message = ""
        if isinstance(error, str) and error:
            message = error
        elif isinstance(result, dict):
            parts: list[str] = []
            for content_item in result.get("content", []):
                if isinstance(content_item, dict):
                    text = content_item.get("text")
                    if isinstance(text, str) and text:
                        parts.append(text)
            message = "\n".join(parts).strip()
        if not message:
            message = "Figma MCP `use_figma` failed without an explicit error message."
        latest_match = {"ok": False, "status": str(status), "message": message}
    if latest_match is not None:
        return latest_match
    return {
        "ok": False,
        "status": "missing",
        "message": "Did not observe a Figma `use_figma` call in the Codex JSON output.",
    }


def main() -> None:
    args = parse_args()
    prompt = make_prompt(args.file_key)

    with TemporaryDirectory(prefix="figma-mcp-preflight-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        completed = subprocess.run(
            [
                "codex",
                "exec",
                "--dangerously-bypass-approvals-and-sandbox",
                "--json",
                "-C",
                str(temp_dir),
                "-m",
                args.model,
                "-c",
                'model_reasoning_effort="medium"',
                "-",
            ],
            input=prompt,
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
            check=False,
        )

    summary = parse_jsonl_events(completed.stdout)
    summary["codex_exit_code"] = completed.returncode
    print(json.dumps(summary, indent=2))

    if not summary.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
