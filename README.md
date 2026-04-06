# worker-critic-example
An example of a worker-critic agentic workflow

## Prompt files

- `prompts/generate-master-figure.md`: base prompt for figure generation.
- `prompts/critic-review-addendum.md`: additive instructions for the reviewed variant.
- `prompts/external-review-addendum.md`: additive instructions for the external-review variant.
- `prompts/generate-master-figure-with-critic.md`: generated prompt equal to the base prompt plus the review addendum.
- `prompts/generate-master-figure-with-external-review.md`: generated prompt equal to the base prompt plus the external-review addendum.

Condition B is defined as a persistent two-session loop: one continuing worker session plus one continuing same-model critic session that is reused across review rounds rather than respawned each time.

Regenerate the derived prompts with:

```bash
uv run python scripts/build_prompts.py
```

## External review

Run the external `gpt-5.4-pro` reviewer with:

```bash
uv run python scripts/external_review.py \
  --proposal inputs/project_description.tex \
  --svg artifacts/master-figure/master-figure.svg \
  --png artifacts/master-figure/master-figure.png \
  --output-md artifacts/master-figure-external-review/review.md \
  --output-json artifacts/master-figure-external-review/review.json
```

This script reads `OPENAI_API_KEY` from the environment, sends the proposal text plus the figure assets to the Responses API, and writes both the raw review and a parsed JSON summary.

## Detached runs

Launch an isolated background Codex run with:

```bash
uv run python scripts/launch_codex_exec.py base
uv run python scripts/launch_codex_exec.py critic
uv run python scripts/launch_codex_exec.py external
```

Each launch creates an isolated temp workspace under `/tmp/worker-critic-example-runs/<run-id>/` by seeding a minimal snapshot of this repo, initializing a fresh git repo there, and then running `codex exec` with `gpt-5.4`, `model_reasoning_effort="xhigh"`, and `--dangerously-bypass-approvals-and-sandbox`.

Each run saves:

- the exact prompt sent to Codex;
- a generated run-local `AGENTS.md` derived from `run-AGENTS.md`;
- a JSON launch record and PID;
- Codex JSONL event output;
- Codex stderr;
- the last assistant message;
- all intermediate artifacts requested by the run-specific bookkeeping addendum.

The shared template at `run-AGENTS.md` is the single file used for A, B, and C. The launcher fills in the condition-specific objective and `runs/<run-id>/` paths, then writes the rendered file to the temp workspace as `AGENTS.md`.

These temp workspaces are intentionally independent of the source repo:

- each run gets its own `.git` directory;
- no git worktree is attached to the source repo;
- no parent `notes/` files are exposed to the run;
- `uv` operates inside the temp workspace and can create its own local `.venv`.

Use a different temp parent if needed:

```bash
uv run python scripts/launch_codex_exec.py base --workspace-root /tmp/my-run-root
```
