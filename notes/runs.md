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
- Added `scripts/launch_codex_exec.py` to launch detached `codex exec` runs and persist run prompts, logs, session outputs, and intermediate artifacts.
- Tightened the detached-run harness so each run gets a generated condition-specific `AGENTS.md` and run-local memory instructions under `runs/<run-id>/` instead of inheriting the repo's global notes.
- Moved the shared detached-run agent instructions into `run-AGENTS.md` so the user can edit one file that applies to A, B, and C; the launcher now renders that template into each run workspace.
- Switched detached runs from source-repo git worktrees to isolated temp repos under `/tmp`, with their own `.git` directories and workspace-local `uv` environments.
- Tightened Condition B so it explicitly requires one continuous worker session and one continuous same-model critic session reused across review rounds, with the critic reviewing only the SVG source.
- Tightened Condition C so it explicitly requires one continuous worker session, passes prior review history into each external `gpt-5.4-pro` review call, and sends only the SVG source to the external reviewer.
