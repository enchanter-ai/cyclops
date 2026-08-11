# cyclops — Differentiation Playbook (Bloom Security interview)

Synthesized from deep research by two independent Opus-class agents (a
techniques/academia lens and a market/competitor lens). Every differentiator is
mapped to Bloom's founders' lineage — **Dig Security** (DSPM: *which* and *how
much* sensitive data) and **XM Cyber** (attack-path *choke points*). Prior art is
credited by name; overclaiming is called out explicitly.

## The honest baseline (what already ships — do not claim as ours)

- **"Toxic agent flows" and Toxic Flow Analysis** — **Invariant Labs**. They coined
  the term and shipped the first analyzer (hybrid static+runtime flow graph).
- **The "lethal trifecta"** (untrusted input + sensitive data + exfil sink) — **Simon
  Willison**, June 2025, adopted by Invariant.
- **A runtime MCP proxy that intercepts tool calls, does PII detection and data-flow
  constraints** — **mcp-scan proxy mode already ships this.** Do not claim "first
  runtime proxy."
- **Taint tracking / value-level provenance** — established in the literature.
- **The risk taxonomy** (Excessive Agency, Sensitive Information Disclosure) — **OWASP
  GenAI / LLM Top 10 (2025)**, codes `LLM06:2025` and `LLM02:2025`. cyclops names the
  classes it enforces by their OWASP code; it does not author the taxonomy.
- **Bloom markets graph-based contextual assessment** — do not claim they "don't do
  graphs"; their live per-flow depth is simply undisclosed (stealth).

cyclops's stated core (argument-level provenance flagging the trifecta) is a
*cleaner runtime instantiation of ideas Invariant already demonstrated.* The
differentiation is the combination below, not the mechanism.

## The wedge

Move from **"toxic flow: yes/no"** (where Invariant already lives) to
**"how many bytes of what-class data leaked, through what encoding, and which one
tool to pull to break the path"** — endpoint-resident, cross-client, deterministic.
That is the Dig + XM Cyber dialect, at agent runtime, and it is not shipping
anywhere the research could find.

## Ranked differentiators

| # | Idea | Why a CTO leans in | In cyclops now? | Prior art it extends |
|---|------|--------------------|------------------|----------------------|
| 1 | **Leak-volume severity (bytes/bits at the sink)** | Turns a boolean alert into a triage number — Dig's "how much data" | **BUILT** (`severity.py`; distinctive secret-token bytes, aggregated per sink) | QIF foundations (Smith, NIFuzz) — ported to agent runtime |
| 2 | **Encoding-unmask** (decode base64/hex before matching) | Visibly kills the evasion that defeats DLP/substring | **BUILT** (`overlap.py`; `poisoned-encoded` scenario) | Beats signature EDR/DLP; makes live what NeuroTaint does offline |
| 3 | **Data-value provenance** (the actual secret bytes traverse file→sink) | The "smoking gun" evidentiary fact for an IR report | **BUILT** (argument-level derivation) | Extends Invariant's tool-*type* flow to data-*value* |
| 4 | **Deterministic, model-free detector** | No LLM in the decision path → not injectable, offline, replayable | **BUILT** (pure graph rules) | Beats LLM-judge guardrails |
| 5 | **Choke-point** (which one tool to remove breaks the flow) | XM Cyber's own concept, on the tool graph | **BUILT (single-path)** — full ranking is roadmap | Extends Invariant TFA (scores flows, not choke points) |
| 6 | **Detect *or* prevent** (deny egress before it leaves) | A PEP, not just a detector — Bloom's enforce posture | **BUILT** (`--mode prevent`) | — |
| 7 | **Cross-client endpoint taint** (tap every MCP client, stitch flows across apps) | Bloom's endpoint thesis; Invariant's per-app gateway can't see it | ROADMAP | Extends Invariant (per-app) → endpoint-scoped |
| 8 | **Trifecta reachability preview** (static: which tool *pairs* form a path, before any attack) | Exposure-management thinking (XM Cyber) | ROADMAP | Extends mcp-scan (per-tool) → cross-tool path |
| 9 | **Semantic/causal taint** (catch paraphrased/summarized secrets via embedding similarity) | Beats the paraphrase evasion | ROADMAP (FP risk at days-scale) | Ports NeuroTaint offline→live |
| 10 | **Flow-forensics receipt** (signed causal incident timeline) | Endpoint-native IR narrative | ROADMAP | New packaging |
| 11 | **Honest benchmark** (AgentDojo recall @ fixed FPR) | A measured number from a candidate is disarming | ROADMAP | Standard bench |
| 12 | **Multi-class flow engine** (typed `FlowClass` + OWASP tag; `EXFILTRATION` ⊂ engine, `EXCESSIVE_AGENCY` added as `untrusted → privileged action`) | One deterministic graph, more than one OWASP risk class blocked before the sink — not just exfil | **BUILT** (`enums/flow_class.py`, `graph.find_toxic_flows`, `excessive-agency` scenario) | Extends the single trifecta to a rule engine over the OWASP LLM Top 10 |

## The one demo moment

**Show a live encoded-exfil catch, scored in bytes, that ends on a choke-point —
while a substring/DLP view stays silent.**

1. A benign-looking agent reads a web page carrying a hidden instruction, reads a
   sensitive key, then makes a "normal" POST where the secret is **base64-encoded**.
2. A naive substring/DLP view shows **nothing** (encoded → clean).
3. cyclops **decodes, re-matches, and fires** — with a **"~N bytes of sensitive
   data reaching an external sink"** readout — then names the **one tool to remove**
   to break this and any latent path.

Why it lands for a Dig + XM Cyber CTO: it fuses both prior companies into one frame
— Dig's *which/how-much data* and XM Cyber's *choke point on the path* — while
visibly defeating the encoding legacy tooling can't see. It matches Bloom's own
launch thesis ("the same tool can be acceptable on one endpoint and high-risk on
another") but proves it at **runtime with data-flow evidence**.

At runtime the proxy fronts the real MCP servers declared in `downstream.toml`, taps
the encoded-exfil chain live, denies it in `prevent` mode, and writes the byte-scored,
choke-point-named verdict to `out/session.json` — the reproducible product moment.

## Coverage gaps to name proactively (credibility, not weakness)

- **Bloom's live-detection depth is undisclosed** — position #1/#3/#7 as public-record
  gaps, not proof of absence.
- **Non-MCP agents** (native function-calling that never speaks MCP) fall outside a
  pure-MCP-proxy tap — a real scope limit.
- **Heavily-transformed/steganographic sinks** weaken byte-level taint; semantic
  propagation is the hard research edge (#9).
- **Multi-turn / memory-poisoning** flows are only partially covered.

## Sources

Invariant Toxic Flow Analysis; Invariant Guardrails; mcp-scan docs; Simon Willison
"lethal trifecta"; Progent (arXiv 2504.11703); NeuroTaint (arXiv 2604.23374);
Dual-Graph Defense (arXiv 2605.26497); Context-to-Execution Integrity (arXiv
2607.06000); QIF foundations (Smith); NIFuzz (arXiv 2501.14500); AgentDojo;
Agent-Sentry (arXiv 2603.22868); Bloom launch (1011vc / unite.ai / TNW).
