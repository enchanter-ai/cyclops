# docs/assets — rendered diagrams

These SVGs are **pre-rendered** so GitHub's mobile app (which does not render
` ```mermaid ` blocks) shows them correctly. `README.md` and `architecture.md`
reference the files here as `<img>`.

## Files

| File | Source | Regenerate |
|------|--------|-----------|
| `flow-engine.svg` | `flow-engine.mmd` | `npx @mermaid-js/mermaid-cli -i flow-engine.mmd -o flow-engine.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js flow-engine.svg` |
| `how-it-works.svg` | `how-it-works.mmd` | `npx @mermaid-js/mermaid-cli -i how-it-works.mmd -o how-it-works.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js how-it-works.svg` |
| `lifecycle.svg` | `lifecycle.mmd` | `npx @mermaid-js/mermaid-cli -i lifecycle.mmd -o lifecycle.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js lifecycle.svg` |
| `arch-overview.svg` | `arch-overview.mmd` | `npx @mermaid-js/mermaid-cli -i arch-overview.mmd -o arch-overview.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js arch-overview.svg` |
| `module-graph.svg` | `module-graph.mmd` | `npx @mermaid-js/mermaid-cli -i module-graph.mmd -o module-graph.svg -c mermaid.config.json -b "#0a1628" -w 1400 && node apply-blueprint.js module-graph.svg` |

The `apply-blueprint.js` step overlays an engineering-blueprint grid (navy
`#0a1628` paper, `#1e3a5f` major lines / `#16304f` minor lines) onto the rendered
diagram so it reads as a CAD drawing rather than a neutral dark card.

Run the commands from `docs/assets/` (paths are relative).
