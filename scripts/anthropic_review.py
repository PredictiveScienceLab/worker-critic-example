from __future__ import annotations

import argparse
import os
from pathlib import Path

from anthropic import Anthropic

from review_prompt import build_review_prompt, load_review_history, read_text, write_review_outputs


DEFAULT_MODEL = "claude-opus-4-6"
DEFAULT_MAX_TOKENS = 2500


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review a proposal figure with Claude Opus via Anthropic Foundry."
    )
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
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Anthropic model name.")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help="Maximum output tokens for the review response.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    proposal_text = read_text(args.proposal)
    svg_text = read_text(args.svg)
    review_history = load_review_history(
        args.history_dir,
        exclude_path=args.output_md,
        history_limit=args.history_limit,
    )
    prompt_text = build_review_prompt(proposal_text, svg_text, review_history)

    api_key = os.environ.get("ANTHROPIC_FOUNDRY_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("Neither ANTHROPIC_FOUNDRY_API_KEY nor ANTHROPIC_API_KEY is set.")

    base_url = os.environ.get("ANTHROPIC_FOUNDRY_BASE_URL")
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = Anthropic(**client_kwargs)
    response = client.messages.create(
        model=args.model,
        max_tokens=args.max_tokens,
        messages=[{"role": "user", "content": prompt_text}],
    )

    chunks: list[str] = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            chunks.append(block.text)

    review_text = "\n".join(chunk.strip() for chunk in chunks if chunk.strip()).strip()
    parsed_review = write_review_outputs(args.output_md, args.output_json, review_text)

    print(f"Model: {args.model}")
    print(f"Status: {parsed_review['status']}")
    print(f"Markdown review: {args.output_md}")
    print(f"Parsed review: {args.output_json}")


if __name__ == "__main__":
    main()
