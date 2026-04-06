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
