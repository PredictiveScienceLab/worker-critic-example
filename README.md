# worker-critic-example
An example of a worker-critic agentic workflow

## Prompt files

- `prompts/generate-master-figure.md`: base prompt for figure generation.
- `prompts/critic-review-addendum.md`: additive instructions for the reviewed variant.
- `prompts/generate-master-figure-with-critic.md`: generated prompt equal to the base prompt plus the review addendum.

Regenerate the reviewed prompt with:

```bash
uv run python scripts/build_prompts.py
```
