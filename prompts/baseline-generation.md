You are the generator for Condition A of the proposal-figure benchmark.

Model/runtime assumptions:

- Model: `gpt-5.4`
- Reasoning effort: `xhigh`
- No subagents
- No external reviewers

Your task is to read the NSF proposal LaTeX source at:

- `inputs/project_description.tex`

and create a single master figure that summarizes the proposal at a glance.

All paths below are relative to the repository root.

## Goal

Produce a proposal-quality overview figure for the beginning of an NSF project description. The figure should quickly communicate the problem, the methodological core, the four specific aims, and the intended impact.

## Output requirements

Create these files:

- `artifacts/baseline/master-figure.png`
- `artifacts/baseline/master-figure.svg`
- `artifacts/baseline/notes.md`

The `PNG` is the benchmarked artifact. The `SVG` is the editable working source. The `notes.md` file should briefly state:

- the figure concept you chose;
- the main content elements included;
- any important omissions or simplifications.

## Figure contract

- Final deliverable format: `PNG`
- Locked internal working representation: `SVG`
- Save the editable `SVG` alongside the final `PNG`
- Target size: about `1950 x 900 px`
- Target aspect ratio: about `2.1:1` to `2.2:1`
- Intended placement: full text width near the start of the proposal
- Intended visual density: one-glance overview, not a dense infographic
- Background: light, proposal-friendly, suitable for print and PDF export

## Content requirements

The figure must accurately reflect the proposal and include all of the following:

- The proposal objective:
  scalable Bayesian reconstruction of cardiovascular hemodynamic fields and cardiac structure from advanced medical imaging.
- The input data modalities:
  `PC-MRI`, `4D Flow MRI`, and `Color Doppler Echo`.
- The methodological core:
  `information field theory`, physics-informed priors, measurement operators, and posterior inference.
- The four specific aims:
  `Aim 1` theoretical formulation of the reconstruction problem;
  `Aim 2` parameterization of time-evolving fields;
  `Aim 3` scalable posterior inference algorithms;
  `Aim 4` verification, validation, and clinical demonstration.
- The end goal:
  uncertainty-aware hemodynamic reconstruction for scientific and clinical use.

## Design guidance

- Make the main narrative readable in a few seconds.
- Use concise labels, not paragraph text.
- Preserve semantic fidelity to the proposal; do not invent scientific claims.
- Use a restrained academic visual style, not startup marketing graphics.
- Avoid poster-like clutter, decorative gradients, or unnecessary ornament.
- Prefer a clear pipeline or systems view over an arbitrary collage.
- Ensure all labels remain legible when the figure is scaled to proposal width.
- Use color sparingly and consistently to separate major conceptual groups.
- Make the figure look like it belongs in an NSF proposal, not a slide deck.

## Layout guidance

Choose a layout that fits the wide, shallow canvas well. A good solution will usually include:

- a clear left-to-right or center-out reading order;
- a compact representation of the imaging inputs;
- a central inference/modeling block;
- four aim blocks or milestones that are visually integrated into the main flow;
- a clear output or impact block.

Do not force a tall layout into a shallow aspect ratio.

## Ground truth emphasis from the proposal

The proposal is centered on using information field theory to fuse noisy imaging data with physics, avoid dependence on expensive CFD solvers, quantify uncertainty, and reconstruct cardiovascular hemodynamics and structure.

The figure should make it easy to understand that:

- multiple imaging modalities feed the inference problem;
- physics and Bayesian field inference are the core scientific engine;
- the four aims define the research plan;
- the project ends in verification, validation, and real clinical demonstration.

## Constraints

- Do not use subagents.
- Do not call any external review model.
- Do not ask for clarification.
- Make reasonable design decisions yourself.
- Use `SVG` as the source of truth for the figure and export the benchmarked `PNG` from it.

## Quality bar

Before finishing, verify for yourself that the figure:

- covers all required scientific elements;
- has a clear visual hierarchy;
- fits the target aspect ratio cleanly;
- uses readable text at proposal scale;
- looks polished enough to show in a proposal draft.

Then write the files and report what you produced.
