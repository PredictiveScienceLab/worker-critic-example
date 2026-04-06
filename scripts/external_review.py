from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.4-pro"
DEFAULT_REASONING_EFFORT = "xhigh"

REVIEW_INSTRUCTIONS = """You are a strict reviewer for a proposal overview figure.

You will receive:
1. The LaTeX source of an NSF project description.
2. The editable SVG source for a proposed figure.
3. Previous review history from earlier rounds, when available.

Decide whether the figure is ready for inclusion near the beginning of a proposal draft.

Use the previous review history as continuity context. Do not repeat already-resolved issues unless they are still present in the current SVG. Treat this as a continuing review thread rather than a fresh review with no memory.

Evaluate it against these criteria:
- fidelity to the proposal text;
- coverage of the central objective or problem;
- coverage of key inputs, data sources, or measurement modalities, when applicable;
- coverage of the main methodological, computational, or theoretical engine;
- coverage of the major research components, work packages, or specific aims;
- coverage of expected outputs, validation path, or intended impact;
- clarity of the main scientific story;
- visual hierarchy and readability at proposal scale;
- suitability for a wide, shallow NSF proposal figure;
- overall polish and clutter level.

Return exactly this format:

STATUS: Approved. or Revise.
JUSTIFICATION:
<short paragraph>

CHANGES:
- <change 1>
- <change 2>

If no changes are needed, write:
CHANGES:
- None.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review a proposal figure with gpt-5.4-pro via the Responses API.")
    parser.add_argument("--proposal", type=Path, required=True, help="Path to the proposal LaTeX source.")
    parser.add_argument("--svg", type=Path, required=True, help="Path to the editable SVG source.")
    parser.add_argument("--output-md", type=Path, required=True, help="Path to write the raw markdown review.")
    parser.add_argument("--output-json", type=Path, required=True, help="Path to write the parsed JSON review.")
    parser.add_argument(
        "--history-dir",
        type=Path,
        help="Optional directory containing prior markdown reviews to include as continuity context.",
    )
    parser.add_argument(
        "--history-limit",
        type=int,
        default=0,
        help="If > 0, include only the most recent N prior markdown reviews from --history-dir.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model name.")
    parser.add_argument(
        "--reasoning-effort",
        default=DEFAULT_REASONING_EFFORT,
        choices=("medium", "high", "xhigh"),
        help="Reasoning effort for the reviewer.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_review_history(history_dir: Path | None, *, exclude_path: Path, history_limit: int) -> list[tuple[str, str]]:
    if history_dir is None or not history_dir.exists():
        return []

    review_paths = sorted(history_dir.glob("*-review.md"))
    exclude_resolved = exclude_path.resolve()
    filtered = [path for path in review_paths if path.resolve() != exclude_resolved]

    if history_limit > 0:
        filtered = filtered[-history_limit:]

    return [(path.name, read_text(path).strip()) for path in filtered]


def build_review_prompt(proposal_text: str, svg_text: str, review_history: list[tuple[str, str]]) -> str:
    sections = [
        REVIEW_INSTRUCTIONS.strip(),
        "<proposal_latex>",
        proposal_text.strip(),
        "</proposal_latex>",
        "<svg_source>",
        svg_text.strip(),
        "</svg_source>",
    ]

    if review_history:
        history_lines = ["<previous_reviews>"]
        for filename, review_text in review_history:
            history_lines.extend(
                [
                    f"<review file=\"{filename}\">",
                    review_text,
                    "</review>",
                ]
            )
        history_lines.append("</previous_reviews>")
        sections.extend(history_lines)
    else:
        sections.extend(
            [
                "<previous_reviews>",
                "None.",
                "</previous_reviews>",
            ]
        )

    return "\n\n".join(sections)


def extract_output_text(response) -> str:
    text = getattr(response, "output_text", "")
    if text:
        return text.strip()

    chunks: list[str] = []
    for item in getattr(response, "output", []):
        for content in getattr(item, "content", []):
            if getattr(content, "type", None) == "output_text":
                chunks.append(getattr(content, "text", ""))
    return "\n".join(chunk for chunk in chunks if chunk).strip()


def parse_review(text: str) -> dict[str, object]:
    status_match = re.search(r"^\s*STATUS:\s*(Approved\.|Revise\.)\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    justification_match = re.search(
        r"^\s*JUSTIFICATION:\s*(.*?)^\s*CHANGES:\s*$",
        text,
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    changes_match = re.search(r"^\s*CHANGES:\s*$([\s\S]*)", text, flags=re.IGNORECASE | re.MULTILINE)

    status = status_match.group(1) if status_match else "UNKNOWN"
    normalized_status = status.lower()
    justification = justification_match.group(1).strip() if justification_match else ""

    changes: list[str] = []
    if changes_match:
        for line in changes_match.group(1).splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                changes.append(stripped[2:].strip())

    return {
        "status": status,
        "approved": normalized_status == "approved.",
        "justification": justification,
        "changes": changes,
        "raw_text": text,
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    proposal_text = read_text(args.proposal)
    svg_text = read_text(args.svg)
    review_history = load_review_history(
        args.history_dir,
        exclude_path=args.output_md,
        history_limit=args.history_limit,
    )
    prompt_text = build_review_prompt(proposal_text, svg_text, review_history)

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=args.model,
        store=False,
        reasoning={"effort": args.reasoning_effort},
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt_text},
                ],
            }
        ],
    )

    review_text = extract_output_text(response)
    parsed_review = parse_review(review_text)

    ensure_parent(args.output_md)
    ensure_parent(args.output_json)
    args.output_md.write_text(review_text + "\n", encoding="utf-8")
    args.output_json.write_text(json.dumps(parsed_review, indent=2) + "\n", encoding="utf-8")

    print(f"Model: {args.model}")
    print(f"Status: {parsed_review['status']}")
    print(f"Markdown review: {args.output_md}")
    print(f"Parsed review: {args.output_json}")


if __name__ == "__main__":
    main()
