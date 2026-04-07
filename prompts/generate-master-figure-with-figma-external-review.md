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

## Figma execution

For this condition, create the figure natively in Figma instead of drawing it as a local SVG first.

Target the Figma file specified in the run-specific instructions appended to this prompt.

Use the Figma MCP server to inspect the file, create the figure, and export or capture the final result.

If the `figma-use` and `figma-generate-design` skills are available in the session, load them before any `use_figma` calls. If they are not available, still use the Figma MCP tools directly and follow the same incremental workflow: inspect first, build in small steps, validate after each major change, and keep track of all created node IDs.

Use as few Figma MCP calls as possible. Do not spend calls on exploratory screenshots before you know native editing works. Prefer:

1. one minimal inspection step;
2. one or more `use_figma` calls to create the figure incrementally;
3. export or capture only after the frame is in place.

Never use `figma.notify()` inside `use_figma` code.

Do not overwrite or rearrange unrelated existing content in the file. Create one dedicated top-level frame for this condition, name it clearly, and place it away from existing nodes if the page is not empty.

For this condition, override the default output paths and source-of-truth expectation from the base prompt:

- the editable source of truth is the Figma frame, not a separately authored local SVG;
- the required local outputs should be written under `artifacts/master-figure-figma/`.

Create these files:

- `artifacts/master-figure-figma/master-figure.png`
- `artifacts/master-figure-figma/notes.md`
- `artifacts/master-figure-figma/figma.json`

If you can export an SVG cleanly from the Figma frame without rebuilding the figure outside Figma, also save:

- `artifacts/master-figure-figma/master-figure.svg`

The `figma.json` file should include at least:

- the Figma file URL;
- the file key;
- the page id and page name used;
- the root frame id and frame name for the figure;
- any important created child node ids you may need later;
- the local artifact paths you produced.

The `notes.md` file should still include:

- the figure concept you chose;
- the main content elements included;
- any important omissions or simplifications;
- a self-contained caption draft.

Before finishing, verify in Figma that the frame reads clearly at proposal scale, then export or capture the final frame as the required local `PNG`.

If any Figma MCP call returns a tool-limit, rate-limit, plan-limit, paywall, or permission blocker, stop immediately and record that blocker in `artifacts/master-figure-figma/figma.json` and `artifacts/master-figure-figma/notes.md`. Do not silently downgrade this condition into a non-Figma local rendering run.

## Figma external review pass

Maintain one continuous worker session for the entire run. Do not restart the task from scratch after each external review round.

Before finalizing the figure, export the current Figma frame to a local `SVG` and send that exported `SVG` to an external reviewer that uses `gpt-5.4-pro` through the OpenAI Responses API.

Have the external reviewer inspect the current exported `SVG` source and decide whether the figure is ready for inclusion in a proposal draft.

For every external review round after the first, provide the reviewer with the previous review history so it understands what it already asked for and what changes were made in response. Treat each external review as a continuation of the same review process, not as a fresh review with no memory.

Ask the reviewer to return:

- `Approved.` or `Revise.`;
- a short justification;
- if revision is needed, a concise list of concrete changes.

Only stop when the reviewer explicitly says `Approved.`.

If the reviewer says `Revise.`, update the Figma frame, re-export the `SVG` and `PNG`, and send the revised `SVG` to the external reviewer again with the accumulated prior review history. Repeat until the reviewer says `Approved.`.

Do not send `PNG` files to the external reviewer. The reviewer should receive the proposal context, the current exported `SVG`, and the previous review history only.

For this condition, override the default Figma output paths from the earlier instructions. Write the final files to:

- `artifacts/master-figure-figma-external-review/master-figure.png`
- `artifacts/master-figure-figma-external-review/master-figure.svg`
- `artifacts/master-figure-figma-external-review/notes.md`
- `artifacts/master-figure-figma-external-review/figma.json`

In `notes.md`, include the figure concept, the main content elements included, any important omissions or simplifications, and a brief record of the external review rounds and the changes made before approval.

In `figma.json`, include the same Figma metadata required by the Figma instructions, plus the local review artifact paths and the review round count.
