# docs/assets — rendered diagrams

These SVGs are **pre-rendered** so GitHub's mobile app (which does not render
` ```mermaid ` blocks) shows them correctly. `README.md` and `architecture.md`
reference the files here as `<img>`.

## Files

| File | Source | Regenerate |
|------|--------|-----------|
| `pipeline.svg` | `pipeline.mmd` | `npx @mermaid-js/mermaid-cli -i pipeline.mmd -o pipeline.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js pipeline.svg` |
| `flow-engine.svg` | `flow-engine.mmd` | `npx @mermaid-js/mermaid-cli -i flow-engine.mmd -o flow-engine.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js flow-engine.svg` |
| `module-graph.svg` | `module-graph.mmd` | `npx @mermaid-js/mermaid-cli -i module-graph.mmd -o module-graph.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js module-graph.svg` |

Every diagram uses the wixie house style: engineering-drawing cards (title block,
colored phase containers with inner step cards, gate-labelled edges, legend) on a
navy blueprint grid. Palette: node `#0f1d33`, phase strokes `#bc8cff` / `#58a6ff`
/ `#3fb950` / `#d8853b` / `#d75952` / `#b88522`, title & legend `#06111f`, grid
`#1e3a5f` on `#0a1628`.

The `apply-blueprint.js` step overlays the navy `#0a1628` grid (major `#1e3a5f`,
minor `#16304f`) onto the rendered diagram so it reads as a CAD drawing rather
than a neutral dark card. Run the commands from `docs/assets/` (paths relative).
