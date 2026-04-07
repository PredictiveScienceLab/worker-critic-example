# Figure Autoresearch Program

Your job is to improve one figure: a single, wide visual for a Substack post that explains the **worker-critic pattern** in one glance.

## Objective

Raise the score reported by `prepare.py`.

The current evaluation averages four 0-10 criteria:

1. `semantic_fidelity`
2. `one_glance_clarity`
3. `readability_layout`
4. `visual_coherence`

The score is computed by the script, not by you. A run is only considered accepted if:

- the average score is at least `8.5`, and
- every individual criterion is at least `8.0`.

## Files

- `plot.py` is the **only file you should modify**.
- `prepare.py` is the fixed evaluation harness. Do not edit it.
- `artifacts/autoresearch/current/figure.svg` and `figure.png` are the outputs of `plot.py`.
- `artifacts/autoresearch/current/review.json` and `review.md` are the outputs of `prepare.py`.

## Figure brief

The figure should make these ideas visible:

- a worker produces drafts;
- a critic reviews those drafts;
- feedback flows back into revision;
- the worker and critic are persistent roles, not one-shot calls;
- the loop stops only when the result is approved.

The ideal figure is:

- understandable in about five seconds;
- legible at publication scale;
- visually coherent, not cluttered;
- explicit about the direction of information flow.

## Workflow

1. Edit `plot.py`.
2. Run `uv run python plot.py`.
3. Run `uv run python prepare.py`.
4. Read `review.md` and `review.json`.
5. Keep changes only if the score improves, or if the average ties but the weakest criterion improves.

## Constraints

- Do not change the task.
- Do not change the scoring rubric.
- Do not add extra files unless they are outputs inside `artifacts/autoresearch/current/`.
- Prefer clearer structure over more decoration.
- Prefer fewer words over denser explanations.
