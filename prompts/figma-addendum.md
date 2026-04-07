## Figma execution

For this condition, create the figure natively in Figma instead of drawing it as a local SVG first.

Target this Figma file:

- `https://www.figma.com/design/dEAATgaM88OTU7As2ywPfb/test?node-id=0-1&m=dev&t=Bi5ZdMgqg6ozttpS-1`

Use the Figma MCP server to inspect the file, create the figure, and export or capture the final result.

If the `figma-use` and `figma-generate-design` skills are available in the session, load them before any `use_figma` calls. If they are not available, still use the Figma MCP tools directly and follow the same incremental workflow: inspect first, build in small steps, validate after each major change, and keep track of all created node IDs.

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
