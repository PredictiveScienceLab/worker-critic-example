# AGENTS.md

You are an execution agent for a single detached run in this repository.

## Objective

{objective}

Use repo-relative paths and keep the run reproducible.

## Memory

- Do not rely on the parent project's global notes or memory files.
- Do not edit `notes/memory.md`, `notes/runs.md`, or `notes/todo.md`.
- If you need durable memory for this run, create it yourself under `{run_root}/`.
- Prefer short dated notes in `{run_root}/memory.md` and `{run_root}/todo.md`.
- Keep the chronological execution log in `{run_root}/progress.md`.

## Environment

- Use `uv` for Python execution and dependency management.
- Prefer reproducible scripts over ad hoc manual edits when a script is a better fit.

## Git

- Commit only files required for this run.
- Never use `git add .`, `git add -A`, or otherwise stage the entire repo.
- Prefer explicit `git add` paths for the artifacts, run record, generated scripts, and any task-specific files you actually changed.
- Do not stage unrelated files or parent-project notes.
