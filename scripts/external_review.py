from __future__ import annotations

import argparse
import base64
import json
import os
import re
from pathlib import Path

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.4-pro"
DEFAULT_REASONING_EFFORT = "xhigh"
DEFAULT_IMAGE_DETAIL = "original"

REVIEW_INSTRUCTIONS = """You are a strict reviewer for a proposal overview figure.

You will receive:
1. The LaTeX source of an NSF project description.
2. The editable SVG source for a proposed figure.
3. A PNG rendering of that figure.

Decide whether the figure is ready for inclusion near the beginning of a proposal draft.

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
    parser.add_argument("--png", type=Path, required=True, help="Path to the PNG render of the figure.")
    parser.add_argument("--output-md", type=Path, required=True, help="Path to write the raw markdown review.")
    parser.add_argument("--output-json", type=Path, required=True, help="Path to write the parsed JSON review.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model name.")
    parser.add_argument(
        "--reasoning-effort",
        default=DEFAULT_REASONING_EFFORT,
        choices=("medium", "high", "xhigh"),
        help="Reasoning effort for the reviewer.",
    )
    parser.add_argument(
        "--image-detail",
        default=DEFAULT_IMAGE_DETAIL,
        choices=("low", "high", "original"),
        help="Image detail setting for the PNG input.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def encode_data_url(path: Path) -> str:
    mime_type = "image/png"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{payload}"


def build_review_prompt(proposal_text: str, svg_text: str) -> str:
    return "\n\n".join(
        [
            REVIEW_INSTRUCTIONS.strip(),
            "<proposal_latex>",
            proposal_text.strip(),
            "</proposal_latex>",
            "<svg_source>",
            svg_text.strip(),
            "</svg_source>",
        ]
    )


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
    png_data_url = encode_data_url(args.png)
    prompt_text = build_review_prompt(proposal_text, svg_text)

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
                    {
                        "type": "input_image",
                        "image_url": png_data_url,
                        "detail": args.image_detail,
                    },
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
