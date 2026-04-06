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
