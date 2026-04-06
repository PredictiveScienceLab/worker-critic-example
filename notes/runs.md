2026-04-06

- Chose the post's primary demo: generate a proposal master figure from proposal LaTeX and improve it with subagent critique.
- Grounded the demo in `/Users/ibilion/Downloads/project_description.tex` and defined three benchmark arms: no critique, same-model critique, and a stronger-critic variant if available.
- Refined the third arm to use an external `gpt-5.4-pro` review call over the OpenAI Responses API and fixed the artifact contract around a proposal-ready `PNG`.
- Wrote the reusable baseline generation prompt in `prompts/baseline-generation.md` with fixed input path, output paths, and figure contract.
