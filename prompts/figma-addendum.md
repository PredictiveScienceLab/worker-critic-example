## Figma execution

For this condition, create the figure natively in Figma instead of drawing it as a local SVG first.

Target the Figma file specified in the run-specific instructions appended to this prompt.

Use the Figma MCP server to inspect the file, create the figure, and export or capture the final result.

If the `figma-use` and `figma-generate-design` skills are available in the session, load them before any `use_figma` calls. If they are not available, still use the Figma MCP tools directly and follow the same incremental workflow: inspect first, build in small steps, validate after each major change, and keep track of all created node IDs.

Use as few Figma MCP calls as possible. Do not spend calls on exploratory screenshots before you know native editing works. Prefer:

1. one minimal inspection step;
2. one or more `use_figma` calls to create the figure incrementally;
3. export or capture only after the frame is in place.

Never use `figma.notify()` inside `use_figma` code.

Do not overwrite or rearrange unrelated existing content in the file. Create one dedicated top-level frame for this condition, name it clearly, and place it away from existing nodes if the page is not empty.

For this condition, override the default output paths and source-of-truth expectation from the base prompt:

- the editable source of truth is the Figma frame, not a separately authored local SVG;
- the required local outputs should be written under `artifacts/master-figure-figma/`.

Create these files:

- `artifacts/master-figure-figma/master-figure.png`
- `artifacts/master-figure-figma/notes.md`
- `artifacts/master-figure-figma/figma.json`

If you can export an SVG cleanly from the Figma frame without rebuilding the figure outside Figma, also save:

- `artifacts/master-figure-figma/master-figure.svg`

The `figma.json` file should include at least:

- the Figma file URL;
- the file key;
- the page id and page name used;
- the root frame id and frame name for the figure;
- any important created child node ids you may need later;
- the local artifact paths you produced.

The `notes.md` file should still include:

- the figure concept you chose;
- the main content elements included;
- any important omissions or simplifications;
- a self-contained caption draft.

Before finishing, verify in Figma that the frame reads clearly at proposal scale, then export or capture the final frame as the required local `PNG`.

If any Figma MCP call returns a tool-limit, rate-limit, plan-limit, paywall, or permission blocker, stop immediately and record that blocker in `artifacts/master-figure-figma/figma.json` and `artifacts/master-figure-figma/notes.md`. Do not silently downgrade this condition into a non-Figma local rendering run.
