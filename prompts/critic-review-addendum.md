## Review pass

Maintain one continuous worker session for the entire run. Do not restart the task from scratch after each review round.

Before finalizing the figure, spawn exactly one critic subagent that uses the same model as you to review the current draft.

Keep that critic subagent alive across review rounds. Reuse the same critic session each time by sending it the revised draft and asking for another review. Do not spawn a fresh critic for each round unless the original critic session becomes unavailable.

Have the critic inspect both the `SVG` and the exported `PNG` and decide whether the figure is ready for inclusion in a proposal draft.

Ask the critic to return:

- `Approved.` or `Revise.`;
- a short justification;
- if revision is needed, a concise list of concrete changes.

Only stop when the critic explicitly says `Approved.`.

If the critic says `Revise.`, update the `SVG`, re-export the `PNG`, and ask the same critic to review the revised figure again. Repeat until the critic says `Approved.`.

When interacting with the critic, preserve continuity:

- keep the critic agent id and reuse it;
- send the revised draft, the current notes, and the previous review history back into that same critic session;
- treat each review as a continuation of the same critic conversation, not as an independent fresh judgment.

For this run, write the final files to:

- `artifacts/master-figure-reviewed/master-figure.png`
- `artifacts/master-figure-reviewed/master-figure.svg`
- `artifacts/master-figure-reviewed/notes.md`

In `notes.md`, include the figure concept, the main content elements included, any important omissions or simplifications, and a brief record of the critique rounds and the changes made before approval.
