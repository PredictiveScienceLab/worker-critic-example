"""Fixed evaluation harness for the autoresearch-style figure loop.

This file is intentionally not meant to be modified by the coding agent.
It renders the current figure (via plot.py), then asks a Codex reviewer to
score the artifact across explicit criteria on a 0-10 scale.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PROGRAM_PATH = REPO_ROOT / "program.md"
PLOT_PATH = REPO_ROOT / "plot.py"
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "autoresearch" / "current"
SVG_PATH = ARTIFACT_DIR / "figure.svg"
PNG_PATH = ARTIFACT_DIR / "figure.png"
RAW_REVIEW_PATH = ARTIFACT_DIR / "review-raw.txt"
REVIEW_JSON_PATH = ARTIFACT_DIR / "review.json"
REVIEW_MD_PATH = ARTIFACT_DIR / "review.md"

MODEL = "gpt-5.4"
REASONING_EFFORT = "xhigh"
PASS_AVERAGE = 8.5
PASS_MIN = 8.0


@dataclass(frozen=True)
class Criterion:
    key: str
    title: str
    description: str
    scoring_guidance: str


CRITERIA = [
    Criterion(
        key="semantic_fidelity",
        title="Semantic Fidelity",
        description=(
            "Does the figure accurately communicate the worker-critic pattern: a worker creates drafts, "
            "a critic reviews them, feedback loops back into revision, and the process stops at approval?"
        ),
        scoring_guidance=(
            "Cap at 4 if two or more core elements are missing or misleading. "
            "Cap at 6 if the loop exists but persistence or approval is unclear. "
            "A 10 means the full pattern is obvious and precise without ambiguity."
        ),
    ),
    Criterion(
        key="one_glance_clarity",
        title="One-Glance Clarity",
        description=(
            "Can a technically literate reader understand the main idea in about five seconds, with a clear reading order and minimal confusion?"
        ),
        scoring_guidance=(
            "Cap at 5 if the main message is not clear on a fast glance. "
            "Cap at 7 if the story is understandable but still too text-heavy or visually busy. "
            "A 10 means the figure lands immediately."
        ),
    ),
    Criterion(
        key="readability_layout",
        title="Readability and Layout",
        description=(
            "Are text, spacing, alignment, contrast, and hierarchy strong enough for publication-scale reading, with no overlaps, clipping, or crowding?"
        ),
        scoring_guidance=(
            "Cap at 4 if any obvious overlap, clipping, or illegible text appears. "
            "Cap at 6 if text is technically legible but cramped or unevenly spaced. "
            "A 10 means the layout is calm, balanced, and easy to read."
        ),
    ),
    Criterion(
        key="visual_coherence",
        title="Visual Coherence",
        description=(
            "Do typography, color, shape language, and emphasis feel deliberate and internally consistent rather than ad hoc?"
        ),
        scoring_guidance=(
            "Cap at 6 if the figure feels inconsistent or visually noisy in multiple places. "
            "An 8 means solid polish with minor rough edges. "
            "A 10 means publication-quality craft with no obvious weak spot."
        ),
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and evaluate the current worker-critic figure.")
    parser.add_argument("--model", default=MODEL, help="Codex model for the reviewer.")
    parser.add_argument(
        "--reasoning-effort",
        default=REASONING_EFFORT,
        help="Codex reasoning effort for the reviewer.",
    )
    parser.add_argument(
        "--skip-render",
        action="store_true",
        help="Do not rerun plot.py before evaluation.",
    )
    return parser.parse_args()


def render_figure() -> None:
    subprocess.run([sys.executable, str(PLOT_PATH)], cwd=REPO_ROOT, check=True)


def collect_svg_facts(svg_path: Path) -> dict[str, object]:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    svg_text = svg_path.read_text(encoding="utf-8")
    texts = re.findall(r"<text\b", svg_text)
    lower = svg_text.lower()
    width = root.attrib.get("width")
    height = root.attrib.get("height")
    return {
        "svg_width": width,
        "svg_height": height,
        "svg_text_nodes": len(texts),
        "contains_worker": "worker" in lower,
        "contains_critic": "critic" in lower,
        "contains_feedback": "feedback" in lower or "revise" in lower,
        "contains_approved": "approved" in lower or "final" in lower,
    }


def build_prompt(svg_facts: dict[str, object]) -> str:
    criteria_lines = []
    for criterion in CRITERIA:
        criteria_lines.append(f"- `{criterion.key}` ({criterion.title}): {criterion.description}")
        criteria_lines.append(f"  Guidance: {criterion.scoring_guidance}")
    criteria_block = "\n".join(criteria_lines)

    facts_block = json.dumps(svg_facts, indent=2, sort_keys=True)
    return f"""
You are a strict but fair design critic reviewing one figure artifact.

Task:
- Read `program.md` to understand the target.
- Inspect `plot.py` only to understand how the figure is being generated.
- Inspect the current artifact at `{SVG_PATH.relative_to(REPO_ROOT)}`.
- If `{PNG_PATH.relative_to(REPO_ROOT)}` exists, inspect it too.
- Do not edit any files.

The goal is a single figure for a Substack post that explains the worker-critic pattern in one glance.
The figure should make these ideas visible:
- a worker produces drafts;
- a critic evaluates the drafts;
- feedback flows back into revision;
- the worker and critic are persistent/continuing roles;
- the loop stops only when the result is approved.

Scoring criteria (0 to 10, where 10 is best):
{criteria_block}

Additional factual checks from the current SVG:
```json
{facts_block}
```

Instructions:
- Be conservative. Scores of 9-10 should be rare.
- Use the scoring guidance literally.
- If a criterion has a cap condition that applies, do not score above that cap.
- Return only valid JSON, with no markdown fences and no extra commentary.

Return this exact schema:
{{
  "criteria": {{
    "semantic_fidelity": {{"score": 0.0, "reason": "string"}},
    "one_glance_clarity": {{"score": 0.0, "reason": "string"}},
    "readability_layout": {{"score": 0.0, "reason": "string"}},
    "visual_coherence": {{"score": 0.0, "reason": "string"}}
  }},
  "strengths": ["string", "string"],
  "improvements": ["string", "string"],
  "summary": "string"
}}
""".strip()


def run_codex_review(prompt: str, model: str, reasoning_effort: str) -> str:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [
            "codex",
            "exec",
            "-m",
            model,
            "-c",
            f'model_reasoning_effort="{reasoning_effort}"',
            "-o",
            str(RAW_REVIEW_PATH),
            "-",
        ],
        cwd=REPO_ROOT,
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Codex review failed.\n"
            f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}"
        )
    return RAW_REVIEW_PATH.read_text(encoding="utf-8")


def extract_json(text: str) -> dict[str, object]:
    stripped = text.strip()
    if stripped.startswith("```"):
        fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, re.DOTALL)
        if fenced:
            stripped = fenced.group(1)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or start >= end:
            raise
        return json.loads(stripped[start : end + 1])


def validate_scores(payload: dict[str, object]) -> dict[str, float]:
    criteria = payload.get("criteria")
    if not isinstance(criteria, dict):
        raise ValueError("Review JSON must include a `criteria` object.")

    scores: dict[str, float] = {}
    for criterion in CRITERIA:
        value = criteria.get(criterion.key)
        if not isinstance(value, dict):
            raise ValueError(f"Missing criterion entry for {criterion.key}.")
        score = value.get("score")
        if not isinstance(score, (int, float)):
            raise ValueError(f"Criterion {criterion.key} must have a numeric score.")
        score = float(score)
        if score < 0 or score > 10:
            raise ValueError(f"Criterion {criterion.key} score out of range: {score}")
        scores[criterion.key] = score
    return scores


def write_markdown_report(payload: dict[str, object], average_score: float, accepted: bool) -> None:
    lines = [
        "# Figure Review",
        "",
        f"- Average score: `{average_score:.2f} / 10`",
        f"- Accepted: `{accepted}`",
        "",
        "## Criteria",
        "",
    ]
    criteria = payload["criteria"]
    for criterion in CRITERIA:
        entry = criteria[criterion.key]
        lines.append(f"- `{criterion.title}`: `{float(entry['score']):.2f}`")
        lines.append(f"  {entry['reason']}")
    strengths = payload.get("strengths", [])
    if strengths:
        lines.extend(["", "## Strengths", ""])
        lines.extend([f"- {item}" for item in strengths])
    improvements = payload.get("improvements", [])
    if improvements:
        lines.extend(["", "## Improvements", ""])
        lines.extend([f"- {item}" for item in improvements])
    summary = payload.get("summary")
    if summary:
        lines.extend(["", "## Summary", "", str(summary)])
    REVIEW_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if not args.skip_render:
        render_figure()

    if not SVG_PATH.exists():
        raise FileNotFoundError(f"Expected SVG artifact at {SVG_PATH}")

    svg_facts = collect_svg_facts(SVG_PATH)
    prompt = build_prompt(svg_facts)
    raw_review = run_codex_review(prompt, args.model, args.reasoning_effort)
    payload = extract_json(raw_review)
    scores = validate_scores(payload)

    average_score = statistics.mean(scores.values())
    accepted = average_score >= PASS_AVERAGE and min(scores.values()) >= PASS_MIN

    result = {
        "artifact": {
            "svg": str(SVG_PATH),
            "png": str(PNG_PATH),
        },
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "average_score": round(average_score, 2),
        "accepted": accepted,
        "pass_average_threshold": PASS_AVERAGE,
        "pass_min_threshold": PASS_MIN,
        "review": payload,
    }
    REVIEW_JSON_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(payload, average_score, accepted)

    print(f"Average score: {average_score:.2f} / 10")
    print(f"Accepted: {accepted}")
    print(f"Wrote {REVIEW_JSON_PATH}")
    print(f"Wrote {REVIEW_MD_PATH}")


if __name__ == "__main__":
    main()
