from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEW_TEMPLATE_PATH = REPO_ROOT / "prompts" / "review-master-figure.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_review_template() -> str:
    return read_text(REVIEW_TEMPLATE_PATH).strip()


def load_review_history(
    history_dir: Path | None,
    *,
    exclude_path: Path | None = None,
    history_limit: int = 0,
) -> list[tuple[str, str]]:
    if history_dir is None or not history_dir.exists():
        return []

    review_paths = sorted(history_dir.glob("*-review.md"))
    if exclude_path is not None:
        exclude_resolved = exclude_path.resolve()
        review_paths = [path for path in review_paths if path.resolve() != exclude_resolved]

    if history_limit > 0:
        review_paths = review_paths[-history_limit:]

    return [(path.name, read_text(path).strip()) for path in review_paths]


def build_review_prompt(
    proposal_text: str,
    svg_text: str,
    review_history: list[tuple[str, str]],
) -> str:
    sections = [
        load_review_template(),
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


def write_review_outputs(markdown_path: Path, json_path: Path, review_text: str) -> dict[str, object]:
    parsed = parse_review(review_text)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(review_text.rstrip() + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
    return parsed
