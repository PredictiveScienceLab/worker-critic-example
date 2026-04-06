2026-04-06

# Use Case: Proposal Master Figure Benchmark

## Source document

- Proposal source: `/Users/ibilion/Downloads/project_description.tex`
- Proposal type: NSF project description
- Existing figure reference in source: `figs/overview-with-specific-aims.pdf`

## Benchmark task

Given the LaTeX source of the proposal, generate a single master figure that summarizes the proposal at a glance.

The figure should:

- span the full text width of the page;
- occupy about one third of a page in height;
- communicate the proposal objective, scientific pipeline, and four specific aims;
- be suitable for inclusion near the beginning of an NSF proposal.

## What the figure must communicate

At minimum, the generated figure should cover:

- the proposal objective: scalable Bayesian reconstruction of cardiovascular hemodynamic fields and cardiac structure from advanced imaging;
- the data modalities: PC-MRI, 4D Flow MRI, and Color Doppler Echo;
- the modeling core: information field theory, physics-informed priors, measurement operators, and posterior inference;
- the four specific aims:
  - Aim 1: theoretical formulation of the reconstruction problem;
  - Aim 2: parameterization of time-evolving fields;
  - Aim 3: scalable posterior inference algorithms;
  - Aim 4: verification, validation, and clinical demonstration;
- the end goal: uncertainty-aware hemodynamic reconstruction for scientific and clinical use.

## Experimental conditions

To avoid ambiguity, use the explicit model/runtime names below.

### Condition A: Baseline

- Generator: `gpt-5.4`
- Reasoning effort: `xhigh`
- No subagent critique
- One agent produces the figure directly

### Condition B: Same-model critique

- Generator: `gpt-5.4`
- Reasoning effort: `xhigh`
- Critic subagent: `gpt-5.4`
- The critic reviews the draft figure and requests revisions until approval or iteration cap

### Condition C: Stronger-critic variant

- Generator: `gpt-5.4`
- Reasoning effort: `xhigh`
- Critic subagent: stronger than the generator if the runtime exposes such a model
- If no stronger model is actually available inside the Codex runtime, treat this as a conceptual third arm until a callable model is selected

## Controlled variables

Hold these constant across conditions:

- same proposal input;
- same figure size target;
- same output format;
- same initial generator instructions;
- same iteration cap for critique conditions;
- same approval rubric.

## Suggested output format

Prefer a structured editable format:

- primary: `SVG`
- secondary export if needed: `PDF`

Avoid making the benchmark depend on opaque raster image generation.

## Approval rubric for the critic

The critic should approve only if the figure satisfies all of the following:

- Content fidelity: accurately reflects the proposal objective and scientific story.
- Coverage: includes the modalities, IFT/Bayesian core, and all four aims.
- Visual hierarchy: the reader can identify the main flow in seconds.
- Readability: labels are legible at proposal scale and not overcrowded.
- Layout discipline: the figure fits a wide, shallow aspect ratio without looking compressed.
- Professional quality: consistent styling, restrained color use, and no obvious clutter.

## What we will compare in the post

- quality of the first draft;
- number and type of issues found by critique;
- quality of the final approved artifact;
- whether same-model critique is enough or whether a stronger critic materially improves the result.
