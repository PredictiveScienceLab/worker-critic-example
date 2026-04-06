2026-04-06

- Chose the post's primary demo: generate a proposal master figure from proposal LaTeX and improve it with subagent critique.
- Grounded the demo in `inputs/project_description.tex` and defined three benchmark arms: no critique, same-model critique, and a stronger-critic variant if available.
- Refined the third arm to use an external `gpt-5.4-pro` review call over the OpenAI Responses API and fixed the artifact contract around a proposal-ready `PNG`.
- Wrote the reusable generation prompt in `prompts/generate-master-figure.md` with fixed input path, output paths, and figure contract.
- Copied the proposal source into the repo and converted benchmark path references to repo-relative paths.
- Locked the benchmark to `SVG` as the internal representation and `PNG` as the evaluated export.
- Replaced the hand-written reviewed prompt with a prompt builder in `scripts/build_prompts.py` that appends `prompts/critic-review-addendum.md` to the shared base prompt and emits `prompts/generate-master-figure-with-critic.md`.
- Added the external-review variant by appending `prompts/external-review-addendum.md` to the same base prompt and emitting `prompts/generate-master-figure-with-external-review.md`.
- Implemented `scripts/external_review.py`, a simple `gpt-5.4-pro` Responses API caller for Condition C, and documented its CLI usage in the README.
- Locked the stopping rule across critique conditions: stop only on an explicit `Approved.` from the reviewer.
