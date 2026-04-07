"""Fixed evaluation harness for proposal-figure autoresearch.

This file is intentionally fixed. It renders the current proposal figure via
`proposal_autoresearch/plot.py` and asks a Codex reviewer to score it against
explicit criteria.
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

TASK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = TASK_ROOT.parent
PROGRAM_PATH = TASK_ROOT / "program.md"
PLOT_PATH = TASK_ROOT / "plot.py"
PROPOSAL_PATH = REPO_ROOT / "inputs" / "project_description.tex"
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "autoresearch-proposal" / "current"
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
            "Does the figure faithfully represent the proposal objective and scientific story: multimodal Bayesian reconstruction "
            "of cardiovascular geometry, flow, and pressure using Information Field Theory, without overstating claims or inventing methods?"
        ),
        scoring_guidance=(
            "Cap at 4 if the objective is wrong, Information Field Theory is missing, or the figure invents unsupported claims. "
            "Cap at 6 if a major scientific element is blurred or misrepresented. "
            "A 10 means the proposal story is accurate, disciplined, and unmistakable."
        ),
    ),
    Criterion(
        key="core_coverage",
        title="Core Coverage",
        description=(
            "Does the figure visibly cover the essential proposal components: PC-MRI, 4D Flow MRI, Echo; the IFT engine with priors, measurement operators, co-registration, and inference; the four aims or their equivalent plan coverage; and the verification-validation-demonstration path plus outputs or impact?"
        ),
        scoring_guidance=(
            "Cap at 4 if two or more core component groups are missing. "
            "Cap at 6 if one major group is missing or hard to locate. "
            "A 10 means all essential groups are present and easy to find."
        ),
    ),
    Criterion(
        key="one_glance_clarity",
        title="One-Glance Clarity",
        description=(
            "Can an NSF reviewer understand the main arc in about five seconds: clinical/imaging problem on the left, IFT engine in the middle, and validation or impact on the right?"
        ),
        scoring_guidance=(
            "Cap at 5 if the main story is not clear on a quick glance. "
            "Cap at 7 if the story is understandable but too text-heavy or visually busy. "
            "A 10 means the main argument lands immediately."
        ),
    ),
    Criterion(
        key="readability_layout",
        title="Readability and Layout",
        description=(
            "Are text size, spacing, hierarchy, alignment, and visual balance strong enough for a proposal master figure at print scale?"
        ),
        scoring_guidance=(
            "Cap at 4 if any obvious overlap, clipping, or illegible text appears. "
            "Cap at 6 if the figure is technically readable but cramped, noisy, or uneven. "
            "A 10 means calm, publication-quality composition with no obvious weak spot."
        ),
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and evaluate the current proposal master figure.")
    parser.add_argument("--model", default=MODEL, help="Codex model for the reviewer.")
    parser.add_argument("--reasoning-effort", default=REASONING_EFFORT, help="Reviewer reasoning effort.")
    parser.add_argument("--skip-render", action="store_true", help="Do not rerun plot.py before evaluation.")
    return parser.parse_args()


def render_figure() -> None:
    subprocess.run([sys.executable, str(PLOT_PATH)], cwd=REPO_ROOT, check=True)


def collect_svg_facts(svg_path: Path) -> dict[str, object]:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    svg_text = svg_path.read_text(encoding="utf-8")
    lower = svg_text.lower()
    aim_count = len(re.findall(r"aim\s*[1-4]", lower))
    return {
        "svg_width": root.attrib.get("width"),
        "svg_height": root.attrib.get("height"),
        "svg_text_nodes": len(re.findall(r"<text\\b", svg_text)),
        "contains_pc_mri": "pc-mri" in lower or "pc mri" in lower,
        "contains_4d_flow_mri": "4d flow" in lower,
        "contains_echo": "echo" in lower or "doppler" in lower,
        "contains_information_field_theory": "information field theory" in lower or "ift" in lower,
        "contains_priors": "prior" in lower,
        "contains_measurement_models": "measurement" in lower or "operator" in lower,
        "contains_inference": "inference" in lower or "posterior" in lower,
        "contains_verify": "verify" in lower or "verification" in lower,
        "contains_validate": "validate" in lower or "validation" in lower,
        "contains_demonstrate": "demonstrate" in lower or "demonstration" in lower,
        "aim_label_count": aim_count,
        "contains_uncertainty": "uncertainty" in lower,
        "contains_geometry_flow_pressure": all(term in lower for term in ("geometry", "flow", "pressure")),
    }


def build_prompt(svg_facts: dict[str, object]) -> str:
    criteria_lines = []
    for criterion in CRITERIA:
        criteria_lines.append(f"- `{criterion.key}` ({criterion.title}): {criterion.description}")
        criteria_lines.append(f"  Guidance: {criterion.scoring_guidance}")
    criteria_block = "\n".join(criteria_lines)

    facts_block = json.dumps(svg_facts, indent=2, sort_keys=True)
    return f"""
You are a strict but fair NSF proposal-figure critic reviewing one artifact.

Task:
- Read `proposal_autoresearch/program.md`.
- Read the proposal source `inputs/project_description.tex`.
- Inspect `proposal_autoresearch/plot.py` only to understand how the figure is being generated.
- Inspect the current artifact at `artifacts/autoresearch-proposal/current/figure.svg`.
- If `artifacts/autoresearch-proposal/current/figure.png` exists, inspect it too.
- Do not edit any files.

Proposal facts that must remain true:
- The objective is a scalable Bayesian methodology to reconstruct cardiovascular hemodynamic fields and cardiac structure from multimodal imaging.
- The key modalities are PC-MRI, 4D Flow MRI, and Color Doppler Echo.
- The central framework is Information Field Theory with physics-informed priors and measurement models.
- The four aims are: formulation of the inverse problem; parameterization of time-evolving fields; scalable joint-posterior algorithms; and verification / validation / demonstration.
- The figure should foreground uncertainty-aware geometry, flow, and pressure reconstruction plus the evidence path from synthetic to in vitro to clinical data.

Scoring criteria (0 to 10, where 10 is best):
{criteria_block}

Additional factual checks from the current SVG:
```json
{facts_block}
```

Instructions:
- Be conservative. Scores of 9-10 should be rare.
- Use the scoring guidance literally.
- If a cap condition applies, do not score above that cap.
- Prefer reviewer utility over decorative taste.
- Return only valid JSON, with no markdown fences and no extra commentary.

Return this exact schema:
{{
  "criteria": {{
    "semantic_fidelity": {{"score": 0.0, "reason": "string"}},
    "core_coverage": {{"score": 0.0, "reason": "string"}},
    "one_glance_clarity": {{"score": 0.0, "reason": "string"}},
    "readability_layout": {{"score": 0.0, "reason": "string"}}
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
        numeric = float(score)
        if numeric < 0 or numeric > 10:
            raise ValueError(f"Criterion {criterion.key} score out of range: {numeric}")
        scores[criterion.key] = numeric
    return scores


def write_markdown_report(payload: dict[str, object], average_score: float, accepted: bool) -> None:
    lines = [
        "# Proposal Figure Review",
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

    svg_facts = collect_svg_facts(SVG_PATH)
    prompt = build_prompt(svg_facts)
    payload = extract_json(run_codex_review(prompt, args.model, args.reasoning_effort))
    scores = validate_scores(payload)
    average_score = statistics.mean(scores.values())
    accepted = average_score >= PASS_AVERAGE and min(scores.values()) >= PASS_MIN

    result = {
        "artifact": {"svg": str(SVG_PATH), "png": str(PNG_PATH)},
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
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
