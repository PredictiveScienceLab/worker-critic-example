## Review pass

Before finalizing the figure, ask one critic subagent that uses the same model as you to review the current draft.

Have the critic inspect both the `SVG` and the exported `PNG` and decide whether the figure is ready for inclusion in a proposal draft.

Ask the critic to return:

- `Approved.` or `Revise.`;
- a short justification;
- if revision is needed, a concise list of concrete changes.

Only stop when the critic explicitly says `Approved.`.

If the critic says `Revise.`, update the `SVG`, re-export the `PNG`, and ask the same critic to review the revised figure again. Repeat until the critic says `Approved.`.

For this run, write the final files to:

- `artifacts/master-figure-reviewed/master-figure.png`
- `artifacts/master-figure-reviewed/master-figure.svg`
- `artifacts/master-figure-reviewed/notes.md`

In `notes.md`, include the figure concept, the main content elements included, any important omissions or simplifications, and a brief record of the critique rounds and the changes made before approval.
