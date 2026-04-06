You are an agent preparing a master figure for an NSF project description.

Read the LaTeX source at:

- `inputs/project_description.tex`

and create a single figure that summarizes the proposal at a glance.

All paths below are relative to the repository root.

## Goal

Produce a proposal-quality overview figure for the beginning of an NSF project description. Read the proposal source, infer the main scientific story, and communicate it clearly in one figure.

Aim for a figure that works like a conceptual graphic abstract: one glance should communicate the proposed work, what is new, and why it matters.

## Output requirements

Create these files:

- `artifacts/master-figure/master-figure.png`
- `artifacts/master-figure/master-figure.svg`
- `artifacts/master-figure/notes.md`

The `PNG` is the final deliverable. The `SVG` is the editable working source. The `notes.md` file should briefly state:

- the figure concept you chose;
- the main content elements included;
- any important omissions or simplifications.
- a self-contained caption draft that explains the figure on its own, identifies what is new or innovative, and names the main intended impact when appropriate.

## Figure contract

- Final deliverable format: `PNG`
- Internal working representation: `SVG`
- Save the editable `SVG` alongside the final `PNG`
- Target size: about `1950 x 900 px`
- Target aspect ratio: about `2.1:1` to `2.2:1`
- Intended placement: full text width near the start of the proposal
- Intended visual density: one-glance overview, not a dense infographic
- Background: light, proposal-friendly, suitable for print and PDF export
- Prefer a conceptual schematic or methodology diagram over a plain data plot
- Keep on-figure text legible at print scale; target effective font sizes of about `10 pt` or larger at final placement
- Use consistent, professional fonts and labeling throughout
- Use color only to clarify distinct parts of the story; maintain strong print contrast
- Avoid too many sub-panels, tiny labels, blurry raster elements, or decorative clutter that does not help the scientific story

## Content requirements

The figure must be derived from the proposal text and include the most important elements needed for a one-glance overview. Read the proposal and infer what to show. At minimum, the figure should communicate:

- the central objective, problem, or scientific question;
- the key inputs, data sources, or measurement modalities, if applicable;
- the main methodological, computational, or theoretical engine;
- the major research components, work packages, or specific aims;
- the expected outputs, validation path, or intended impact.
- what is new, distinctive, or innovative in the proposed work.

Use the proposal's own language where possible, but shorten aggressively so the figure remains readable at proposal scale.

If the proposal has an important intellectual-merit cue, broader-impact cue, training component, or enabling capability that can be shown cleanly, include it directly in the figure labeling or as a compact inset only if it improves the one-glance story.

## Quality bar

Before finishing, verify that the figure:

- accurately reflects the proposal text;
- captures the main scientific story without obvious omissions;
- has a clear visual hierarchy;
- fits the target aspect ratio cleanly;
- uses readable text at proposal scale;
- reads clearly at `100%` zoom and in print without tiny or blurry text;
- is self-explanatory enough that a reviewer can understand the main idea quickly;
- has a caption draft in `notes.md` that explains the visual without depending on the body text;
- looks polished enough to include in a proposal draft.
- does not rely on excessive panel count or clutter to convey the idea.

Then write the files and report what you produced.

## Review pass

Maintain one continuous worker session for the entire run. Do not restart the task from scratch after each external review round.

Before finalizing the figure, send the current draft to an external reviewer that uses `gpt-5.4-pro` through the OpenAI Responses API.

Have the external reviewer inspect the current `SVG` source and decide whether the figure is ready for inclusion in a proposal draft.

For every external review round after the first, provide the reviewer with the previous review history so it understands what it already asked for and what changes were made in response. Treat each external review as a continuation of the same review process, not as a fresh review with no memory.

Ask the reviewer to return:

- `Approved.` or `Revise.`;
- a short justification;
- if revision is needed, a concise list of concrete changes.

Only stop when the reviewer explicitly says `Approved.`.

If the reviewer says `Revise.`, update the `SVG`, re-export the `PNG`, and send the revised figure to the external reviewer again with the accumulated prior review history. Repeat until the reviewer says `Approved.`.

Do not send `PNG` files to the external reviewer. The reviewer should receive the proposal context, the current `SVG`, and the previous review history only.

For this run, write the final files to:

- `artifacts/master-figure-external-review/master-figure.png`
- `artifacts/master-figure-external-review/master-figure.svg`
- `artifacts/master-figure-external-review/notes.md`

In `notes.md`, include the figure concept, the main content elements included, any important omissions or simplifications, and a brief record of the external review rounds and the changes made before approval.
