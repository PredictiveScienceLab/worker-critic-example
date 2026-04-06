2026-04-06

- Turn the benchmark spec into concrete prompts for the critique runs.
- Design the `gpt-5.4-pro` review prompt and response schema for the external critic arm.
- Decide what internal representation should be used to generate a reliable final `PNG`.
- Build the simple external reviewer call that uses `OPENAI_API_KEY` and `gpt-5.4-pro`.
- Define the iteration cap and stopping rule for the critique conditions.
