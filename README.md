# worker-critic-example
An example of a worker-critic agentic workflow

## Prompt files

- `prompts/generate-master-figure.md`: base prompt for figure generation.
- `prompts/critic-review-addendum.md`: additive instructions for the reviewed variant.
- `prompts/external-review-addendum.md`: additive instructions for the external-review variant.
- `prompts/generate-master-figure-with-critic.md`: generated prompt equal to the base prompt plus the review addendum.
- `prompts/generate-master-figure-with-external-review.md`: generated prompt equal to the base prompt plus the external-review addendum.

Condition B is defined as a persistent two-session loop: one continuing worker session plus one continuing same-model critic session that reviews the current SVG and is reused across review rounds rather than respawned each time.
Condition C is defined as one continuing worker session plus repeated external `gpt-5.4-pro` review calls that receive the current SVG and prior review history.

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
  --history-dir runs/<run-id>/reviews \
  --output-md artifacts/master-figure-external-review/review.md \
  --output-json artifacts/master-figure-external-review/review.json
```

This script reads `OPENAI_API_KEY` from the environment, sends the proposal text plus the current SVG source to the Responses API, optionally includes prior markdown reviews from `--history-dir`, and writes both the raw review and a parsed JSON summary.

## Detached runs

Launch an isolated background Codex run with:

```bash
uv run python scripts/launch_codex_exec.py base
uv run python scripts/launch_codex_exec.py critic
uv run python scripts/launch_codex_exec.py external
```

Each launch creates an isolated temp workspace under `/tmp/worker-critic-example-runs/<run-id>/` by seeding a minimal snapshot of this repo, initializing a fresh git repo there, writing a run-local launch script, and then starting `codex exec` inside a named `tmux` session with `gpt-5.4`, `model_reasoning_effort="xhigh"`, and `--dangerously-bypass-approvals-and-sandbox`.

Each run saves:

- the exact prompt sent to Codex;
- a generated run-local `AGENTS.md` derived from `run-AGENTS.md`;
- a JSON launch record, tmux session name, and pane PID;
- a tmux wrapper log plus Codex exit code when the run finishes;
- Codex JSONL event output;
- Codex stderr;
- the last assistant message;
- all intermediate artifacts requested by the run-specific bookkeeping addendum.

To inspect or attach to a live run:

```bash
tmux list-sessions
tmux attach -t worker-critic-<run-id>
tmux capture-pane -pt worker-critic-<run-id>
```

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

## Claude Code runs

The repo also has a Claude-based harness that keeps session continuity explicitly across review rounds.

Launch an isolated background Claude run with:

```bash
uv run python scripts/launch_claude_exec.py base
uv run python scripts/launch_claude_exec.py critic
uv run python scripts/launch_claude_exec.py external
```

This launcher:

- creates an isolated temp repo under `/tmp/worker-critic-example-runs/<run-id>/`;
- renders a run-local `CLAUDE.md` from `run-CLAUDE.md`;
- starts a tmux-backed runner that uses persistent Claude sessions;
- keeps one worker session across the whole run;
- for Condition B, keeps one persistent Claude critic session across review rounds;
- for Condition C, keeps one persistent worker session and uses `scripts/anthropic_review.py` for the external Foundry reviewer.

The Claude runner is implemented in `scripts/run_claude_condition.py`.
The Azure Foundry reviewer is implemented in `scripts/anthropic_review.py`.
The shared review prompt is `prompts/review-master-figure.md`.

Current Foundry note:

- local smoke tests on April 6, 2026 confirmed `claude-opus-4-6` on this endpoint;
- the explicit Sonnet model names I tried (`claude-sonnet-4-6`, `claude-sonnet-4-5`, and `claude-sonnet-4`) were rejected by the current deployment;
- so the Claude launcher defaults to `claude-opus-4-6` for the worker and critic unless you override `--worker-model` or `--critic-model`.

Example override:

```bash
uv run python scripts/launch_claude_exec.py critic \
  --worker-model claude-opus-4-6 \
  --critic-model claude-opus-4-6
```

The external reviewer can be called directly with:

```bash
uv run python scripts/anthropic_review.py \
  --proposal inputs/project_description.tex \
  --svg artifacts/master-figure/master-figure.svg \
  --history-dir runs/<run-id>/reviews \
  --output-md artifacts/master-figure-external-review/review.md \
  --output-json artifacts/master-figure-external-review/review.json \
  --model claude-opus-4-6
```

## Comparison artifacts

After the three runs finish, collect the final figures and build the comparison media with:

```bash
uv run python scripts/build_comparison_artifacts.py \
  --run-prefix 20260406-192417 \
  --output-dir artifacts/20260406-192417-comparison
```

This copies the final PNGs and notes from the `/tmp` run workspaces into a repo-local directory and generates:

- `final-comparison.png`: labeled side-by-side final figures;
- `gifs/base-progress.gif`: base-condition draft progression;
- `gifs/critic-progress.gif`: same-model-critic draft progression;
- `gifs/external-progress.gif`: external-review draft progression;
- `summary.md`: source run roots, frame counts, and copied artifact paths.
