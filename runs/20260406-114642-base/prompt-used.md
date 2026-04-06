You are an agent preparing a master figure for an NSF project description.

Read the LaTeX source at:

- `inputs/project_description.tex`

and create a single figure that summarizes the proposal at a glance.

All paths below are relative to the repository root.

## Goal

Produce a proposal-quality overview figure for the beginning of an NSF project description. Read the proposal source, infer the main scientific story, and communicate it clearly in one figure.

## Output requirements

Create these files:

- `artifacts/master-figure/master-figure.png`
- `artifacts/master-figure/master-figure.svg`
- `artifacts/master-figure/notes.md`

The `PNG` is the final deliverable. The `SVG` is the editable working source. The `notes.md` file should briefly state:

- the figure concept you chose;
- the main content elements included;
- any important omissions or simplifications.

## Figure contract

- Final deliverable format: `PNG`
- Internal working representation: `SVG`
- Save the editable `SVG` alongside the final `PNG`
- Target size: about `1950 x 900 px`
- Target aspect ratio: about `2.1:1` to `2.2:1`
- Intended placement: full text width near the start of the proposal
- Intended visual density: one-glance overview, not a dense infographic
- Background: light, proposal-friendly, suitable for print and PDF export

## Content requirements

The figure must be derived from the proposal text and include the most important elements needed for a one-glance overview. Read the proposal and infer what to show. At minimum, the figure should communicate:

- the central objective, problem, or scientific question;
- the key inputs, data sources, or measurement modalities, if applicable;
- the main methodological, computational, or theoretical engine;
- the major research components, work packages, or specific aims;
- the expected outputs, validation path, or intended impact.

Use the proposal's own language where possible, but shorten aggressively so the figure remains readable at proposal scale.

## Quality bar

Before finishing, verify that the figure:

- accurately reflects the proposal text;
- captures the main scientific story without obvious omissions;
- has a clear visual hierarchy;
- fits the target aspect ratio cleanly;
- uses readable text at proposal scale;
- looks polished enough to include in a proposal draft.

Then write the files and report what you produced.

## Run bookkeeping

In addition to the required deliverables, save all substantial intermediate results for this run under:

- `runs/20260406-114642-base/progress.md`
- `runs/20260406-114642-base/intermediate/`
- `runs/20260406-114642-base/reviews/`
- `runs/20260406-114642-base/final/`

Requirements:

- Write a short chronological progress log to `runs/20260406-114642-base/progress.md`.
- Before replacing any substantial figure draft, save the prior draft in `runs/20260406-114642-base/intermediate/` using zero-padded filenames.
- Save any critic or reviewer responses in `runs/20260406-114642-base/reviews/` using zero-padded filenames.
- At the end, copy the final `PNG`, `SVG`, and notes file into `runs/20260406-114642-base/final/`.
- Do not delete or overwrite earlier intermediate files; create new numbered files instead.
