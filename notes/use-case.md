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

## Artifact contract

- Final deliverable format: `PNG`
- Intended placement: `\includegraphics[width=\textwidth]{...}` near the start of the proposal
- Target layout: wide, shallow, readable at proposal scale
- Target aspect ratio: about `2.1:1` to `2.2:1`
- Suggested export size: `1950 x 900 px` at `300 dpi`, or a higher-resolution equivalent with the same aspect ratio
- Preferred content density: one-glance overview, not a dense infographic
- Optional working source: keep an editable source format during generation if useful, but evaluate the exported `PNG`

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
- Critic: external review call to `gpt-5.4-pro`
- Critic reasoning effort: `xhigh`
- Call mechanism: OpenAI `Responses API`
- Authentication: `OPENAI_API_KEY` from the local environment
- Critic mode: plain review call only, not a full agent
- Critic input: the generated `PNG`, the proposal summary/context, and the approval rubric
- Privacy preference: set `store: false` for the review call

## Controlled variables

Hold these constant across conditions:

- same proposal input;
- same figure size target;
- same output format;
- same initial generator instructions;
- same iteration cap for critique conditions;
- same approval rubric.

## Suggested output format

Benchmark on the exported `PNG`.

To keep iteration practical, the generator may use any internal working representation that produces a consistent final `PNG`.

## Approval rubric for the critic

The critic should approve only if the figure satisfies all of the following:

- Content fidelity: accurately reflects the proposal objective and scientific story.
- Coverage: includes the modalities, IFT/Bayesian core, and all four aims.
- Visual hierarchy: the reader can identify the main flow in seconds.
- Readability: labels are legible at proposal scale and not overcrowded.
- Layout discipline: the figure fits a wide, shallow aspect ratio without looking compressed.
- Professional quality: consistent styling, restrained color use, and no obvious clutter.
- Proposal fitness: looks like an NSF proposal overview figure rather than a conference poster panel.

## External critic API notes

For Condition C, the external critic call should use the official model ID `gpt-5.4-pro`.

The review request should:

- send the figure as image input;
- include a concise textual summary of the proposal and the figure-generation task;
- ask for a strict pass/fail review against the rubric;
- request concrete revision instructions rather than a rewritten figure;
- return a compact structured review that the generator can act on.

## What we will compare in the post

- quality of the first draft;
- number and type of issues found by critique;
- quality of the final approved artifact;
- whether same-model critique is enough or whether a stronger critic materially improves the result.
