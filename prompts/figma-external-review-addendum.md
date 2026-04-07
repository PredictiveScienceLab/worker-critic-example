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
