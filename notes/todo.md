2026-04-06

- Design the `gpt-5.4-pro` review prompt and response schema for the external critic arm.
- Build the simple external reviewer call that uses `OPENAI_API_KEY` and `gpt-5.4-pro`.
- Define the iteration cap and stopping rule for the critique conditions.
- Add a generated prompt for the stronger external-review variant using the same base prompt plus an external-review addendum.
