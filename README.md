# worker-critic-example
An example of a worker-critic agentic workflow

## Prompt files

- `prompts/generate-master-figure.md`: base prompt for figure generation.
- `prompts/critic-review-addendum.md`: additive instructions for the reviewed variant.
- `prompts/external-review-addendum.md`: additive instructions for the external-review variant.
- `prompts/generate-master-figure-with-critic.md`: generated prompt equal to the base prompt plus the review addendum.
- `prompts/generate-master-figure-with-external-review.md`: generated prompt equal to the base prompt plus the external-review addendum.

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

Each launch creates a detached git worktree under `bench_worktrees/<run-id>/`, runs `codex exec` with `gpt-5.4`, `model_reasoning_effort="xhigh"`, and `--dangerously-bypass-approvals-and-sandbox`, and saves:

- the exact prompt sent to Codex;
- a generated run-local `AGENTS.md` tailored to that condition;
- a JSON launch record and PID;
- Codex JSONL event output;
- Codex stderr;
- the last assistant message;
- all intermediate artifacts requested by the run-specific bookkeeping addendum.

The launcher now also configures each run worktree as a sparse checkout so the agent only sees the files needed for the run instead of inheriting the parent repo's global notes. Any durable memory for the run should be created under `runs/<run-id>/` by the run itself.
