# Proposal Figure Autoresearch Program

Your job is to improve one figure: a wide master figure for the NSF proposal in `inputs/project_description.tex`.

## Objective

Raise the score reported by `proposal_autoresearch/prepare.py`.

The evaluator averages four 0-10 criteria:

1. `semantic_fidelity`
2. `core_coverage`
3. `one_glance_clarity`
4. `readability_layout`

A run is only considered accepted if:

- the average score is at least `8.5`, and
- every individual criterion is at least `8.0`.

## Files

- `proposal_autoresearch/plot.py` is the only file you should modify.
- `proposal_autoresearch/prepare.py` is the fixed evaluation harness. Do not edit it.
- `inputs/project_description.tex` is the source proposal.
- `artifacts/autoresearch-proposal/current/figure.svg` and `figure.png` are the outputs of `proposal_autoresearch/plot.py`.
- `artifacts/autoresearch-proposal/current/review.json` and `review.md` are the outputs of `proposal_autoresearch/prepare.py`.

## Figure brief

The figure should make these ideas visible:

- the clinical and imaging problem;
- the three key modalities: PC-MRI, 4D Flow MRI, and Color Doppler Echo;
- the core scientific engine: Information Field Theory with physics-informed priors, measurement operators, co-registration, and scalable inference;
- the proposal structure through the four specific aims;
- the evidence path: verification, validation, and demonstration;
- the intended outputs and impact, including uncertainty-aware geometry, flow, and pressure reconstruction.

The ideal figure is:

- understandable in about five seconds;
- faithful to the proposal text;
- legible at proposal-print scale;
- visually coherent without becoming a dense infographic board.

This is a master figure, not a poster, not a slide, and not a checklist.

## Planning requirement

Before you change the drawing logic, decide these two things inside `proposal_autoresearch/plot.py`:

1. one sentence for the five-second takeaway;
2. the five visual elements that must remain in the figure.

These planning aids do not need to be rendered, but they should guide the layout.

## Hard design constraints

- Outside the main title, use no more than about `90` visible words.
- Do not use paragraph text in the aim strip. Aim cards should be labels or one very short line.
- The center hero must visually depict fused posterior reconstruction, not just name the method.
- No non-title text smaller than `18 px` at the exported `1800x1020` size.
- Avoid text blocks longer than `3` lines inside compact cards.
- If an element does not improve five-second comprehension, remove it.
- Keep one dominant scaffold: left inputs/problem, center reconstruction engine + posterior, right evidence/impact.

## Workflow

1. Edit `proposal_autoresearch/plot.py`.
2. Run `uv run python proposal_autoresearch/plot.py`.
3. Run `uv run python proposal_autoresearch/prepare.py`.
4. Read `artifacts/autoresearch-proposal/current/review.md` and `review.json`.
5. Keep changes only if the score improves, or if the average ties but the weakest criterion improves.

## Constraints

- Do not change the task.
- Do not change the scoring rubric.
- Do not edit `proposal_autoresearch/prepare.py`.
- Do not add extra files unless they are outputs inside `artifacts/autoresearch-proposal/current/`.
- Prefer clearer structure over more wording.
- Prefer proposal fidelity over decorative novelty.
- Treat layout/readability as the main optimization target once fidelity and coverage are preserved.
