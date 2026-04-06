## Review pass

Before finalizing the figure, send the current draft to an external reviewer that uses `gpt-5.4-pro` through the OpenAI Responses API.

Have the external reviewer inspect both the `SVG` and the exported `PNG` and decide whether the figure is ready for inclusion in a proposal draft.

Ask the reviewer to return:

- `APPROVED` or `REVISE`;
- a short justification;
- if revision is needed, a concise list of concrete changes.

If the reviewer returns `REVISE`, update the `SVG`, re-export the `PNG`, and send the revised figure to the same external reviewer again. Repeat until the reviewer returns `APPROVED`.

For this run, write the final files to:

- `artifacts/master-figure-external-review/master-figure.png`
- `artifacts/master-figure-external-review/master-figure.svg`
- `artifacts/master-figure-external-review/notes.md`

In `notes.md`, include the figure concept, the main content elements included, any important omissions or simplifications, and a brief record of the external review rounds and the changes made before approval.
