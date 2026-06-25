# Blog Journal

Append-only capture file for blog-worthy observations. Entries accumulate
across sessions and are extracted into materials files at project/epoch end.
Reference: DSM_0.1 Blog Artifacts (three-document pipeline).

## Entries

### [2026-04-02] Sprint 15 Complete: Protocol Usage Analysis

Sprint 15 (Sessions 42-45) built a four-layer protocol usage methodology for
measuring how DSM_0.2 sections are actually used across spoke projects.

**What we built:** Six new analysis modules (`section_index`, `declared_refs`,
`prescribed_refs`, `observed_refs`, `usage_report`, `usage_diff`) implementing
four measurement layers: declared (CLAUDE.md references), prescribed (skill
definitions), observed (session transcripts), and designed (module dispatch
table). CLI commands `--protocol-usage` and `--usage-compare` with Rich table
output. 547 → 664 tests, 91% coverage.

**EXP-009 result: CONDITIONAL PASS.** Ground truth validation scored 4/7 (57%,
below 60% threshold). Stage B transcript analysis revealed the split:
procedural protocols (explicit naming, 4/4 pass) vs behavioral protocols
(implicit compliance, 0/3 pass). Reference counting measures protocol
salience, not compliance, which is a fundamental limitation for behavioral
standards like "Read-Only Access" or "Inclusive Language."

**Key insight:** The procedural-vs-behavioral distinction is not a bug in the
tooling, it reflects a real property of protocol design. Protocols that require
explicit naming ("use Section X") are measurable by reference counting.
Protocols enforced by absence of violations are invisible to the same method.
This has implications for how DSM Central designs future protocols: if you want
measurability, require explicit references.

**Bug found:** GT ID matching in `usage_report.py` used exact match when it
needed suffix matching. Fixed during EXP-009 execution.

### [2026-04-14] Sprint 16 Complete: Knowledge Summary Export (BL-302 Phase 1)

Sprint 16 (Session 47) delivered the first working experiment of the
Intrinsic-ToC vision: a `--knowledge-summary PATH` CLI command that maps a
repository's reference graph into an agent-consumable markdown file.

**What we built:** A `knowledge_summary` module with 5 functions (hierarchy,
hub documents, hotspots, orphans, orchestrator). CLI integration reuses the
existing graph build pipeline. GraphML None-value bug fixed as a bundled
prerequisite. 25 new tests, 689 total, 91% coverage.

**Validation against DSM Central:** 811 files, 8,991 sections, 1,254 cross-
references → 253-line markdown summary. The hierarchy component produced 188
lines (52 directories, all legitimate content), 26% over the 200-line target
but still bounded and informative. The other components (hubs, hotspots,
orphans) stayed within budget because they use fixed top-N caps.

**Key insight:** The Intrinsic-ToC concept emerged during design discussion.
The static markdown is layer 1 of a four-layer architecture (static ToC →
agent navigation → ecosystem/avatar → code ontologies). The agent IS the
query engine, reading the ToC like a human reads a book's table of contents
and navigating to specific files. No MCP, no local LLM.

**Decision DEC-009:** GE will not add local LLM or NLP dependencies. The
consuming AI agent is the LLM; GE's value is structural analysis. Three
Epoch 3 COULDs dropped (LLM second-pass, spaCy NER, embeddings).

**Methodology feedback to DSM Central (4 entries, 4 proposals):** PGB gate
granularity, vision-directed planning, sprint boundary automatic trigger,
sprint checklist reconciliation. Each entry traces to specific S47 evidence.

**Research artifacts:**
- Intrinsic-ToC Vision (conceptual framework, 10 sections)
- Sprint 16 Phase 1 Findings (empirical results, 4 open questions for Central)

**Narrative thread:** "When the agent's own tool produces agent-readable
output." Sprint 16 is GE turning inward: the tool that analyzes repositories
now produces output specifically structured for the kind of agent that will
read it. The `key: value` format (`path:`, `sections:`) is the concrete
manifestation, parseable without natural language understanding.

### [2026-06-25] Sessions 49-50: Concepts as nodes, and a drift the graph could have caught

Two research-and-decision sessions, no production code, but the shape of the
next epoch got decided.

**GraphRAG, weighed and declined (S49).** Three parallel research agents
surveyed GraphRAG for the Intrinsic-ToC graph. Verdict: adopt the ideas, not
the stack. The decisive datum was not a benchmark average but a single fact,
Leiden clustering was already on the Sprint 18 roadmap, so the one technique
worth borrowing was already coming. The full stack ($33K indexing, 34%
entity-miss, 41x build time) also contradicts DEC-009 (no local LLM
dependencies). Convergence plus one decisive fact beat a scorecard.

**A fourth node type (S49 research, S50 decision).** The graph has three node
types: files, sections, terms. The Semantic Concept Layer (Layer 4.5) proposes
a fourth, the concept, an idea that recurs across files and repos but is not
itself any of them (`DEC-009`, `Intrinsic-ToC`, `session baseline`). S49
explored the design space; S50 closed it with DEC-011, adopt for Epoch 6, with
one firm commitment (a `dsm-version` drift-detection slice) and the rest of the
schema recorded as non-binding leanings. Decide the model, defer the details
until the minimal slice teaches us, the same lesson DEC-009 taught about not
over-committing architecture early.

**Narrative thread:** "The tool watching itself." DEC-011's headline product is
drift detection, surfacing when a concept's value disagrees across the files
that mention it. The worked example is `dsm-version`. The irony wrote itself:
*this very session* opened with the agent detecting, by hand, that
`last-align.txt` said v1.14.0 while the DSM CHANGELOG said 1.17.0, then running
`/dsm-align` to reconcile it. That hand-check is exactly the query a concept
node would answer. The session that decided to build the drift detector spent
its first ten minutes being the drift detector.
