Use [baseline-generation.md](./baseline-generation.md) as the base prompt for Condition B.

All instructions from the baseline prompt remain in force except for the changes below.

## Condition label

Replace:

- `You are the generator for Condition A of the proposal-figure benchmark.`

With:

- `You are the generator for Condition B of the proposal-figure benchmark.`

## Model/runtime assumptions

Replace the baseline assumptions block with:

- Model: `gpt-5.4`
- Reasoning effort: `xhigh`
- Use one critic subagent, also `gpt-5.4`
- No external reviewers

## Output requirements

Use the same output naming convention as Condition A, but write files under:

- `artifacts/same-model-critique/master-figure.png`
- `artifacts/same-model-critique/master-figure.svg`
- `artifacts/same-model-critique/notes.md`

## Critique loop

After producing the first complete draft of the figure, run a same-model critique loop.

The critic subagent should:

- review the current `SVG` and exported `PNG`;
- check the figure against the same scientific and visual requirements used in the baseline prompt;
- decide whether the figure should be approved;
- if not approved, return concrete revision instructions focused on the most important deficiencies.

The generator should then:

- revise the `SVG`;
- re-export the `PNG`;
- ask the same critic to review the revised figure again;
- continue until the critic approves the result.

## Critic instructions

When you call the critic subagent, instruct it to behave as a strict reviewer.

The critic should evaluate:

- content fidelity to the proposal;
- coverage of modalities, IFT/Bayesian core, and all four aims;
- visual hierarchy and readability at proposal scale;
- suitability for a wide, shallow NSF proposal figure;
- overall polish and clutter level.

The critic should return:

- `APPROVED` or `REVISE`;
- a short justification;
- if revision is needed, a concise list of concrete changes.

## Constraints

Replace the baseline constraint:

- `Do not use subagents.`

With:

- `Use exactly one critic subagent for review and iteration.`

All other baseline constraints remain unchanged.
