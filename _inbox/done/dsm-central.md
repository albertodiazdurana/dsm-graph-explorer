### [2026-02-28] Literate CQRS Knowledge research complete, insights for Graph Explorer

**Type:** Notification
**Priority:** Medium
**Source:** DSM Central
**Acknowledged:** 2026-02-28 (Session 18)
**Disposition:** Acknowledged. Sprint 7 already complete. Architecture insights (entity inventory format, git ref parameter, typed cross-repo edges, bi-temporal model) noted for Epoch 3-4 planning.

Five research threads on the Literate CQRS Knowledge Architecture are now
complete (3,279 lines, 25+ sources). The research validates and expands the
architectural vision behind Graph Explorer. Key findings relevant to Sprint 7+:

**1. Compilation approach (Thread 3: Compilation Survey)**

The markdown-to-graph tool landscape divides into two camps: deterministic
(parse structural signals directly) and LLM-extracted (infer entities from
prose). Graph Explorer's current approach (structural parsing of headings,
cross-references, patterns) is in the deterministic camp. The research
confirms this is the right starting point: reproducible, predictable, and
sufficient for DSM's structured markdown. LLM extraction is a future
enhancement for prose-embedded relationships, not a replacement.

No existing tool combines deterministic structural parsing with a CQRS
architecture where human-authored markdown is the write model and the graph
is the agent's read model. Graph Explorer is building something new, not
reimplementing an existing tool.

**2. Git as event store (Thread 4: Event Sourcing + Git)**

Git commits are events; the markdown at any commit is reconstructible state.
The compilation pipeline is a projection function in the Event Sourcing
sense. This means temporal knowledge graphs (how did the graph look at
version X?) are achievable without dedicated temporal graph infrastructure,
by recompiling from git history. Practical implication for Graph Explorer:
consider accepting a git ref (commit, tag) as an optional parameter to
compile the graph at a historical point, enabling diff-based graph queries
("what changed between v1.3.0 and v1.3.25?").

**3. Multi-repo federation (Thread 5: Multi-Repository Graph Patterns)**

The DSM ecosystem is a polyrepo system. The recommended architecture is
per-repo compilation with interface exchange: each repo publishes an
inventory of its referenceable entities (sections, protocols, backlog items),
and cross-repo references are validated at compile time against these
inventories. DSM's existing cross-repo mechanisms (inbox, @ imports, Ecosystem
Path Registry) already constitute choreography-based eventually consistent
federation. Graph Explorer should formalize these as typed cross-repo edges.

Practical implication: start with single-repo compilation (current Sprint 7
scope), but design the entity inventory format now so multi-repo extension
is additive, not a rewrite.

**4. Zep/Graphiti differentiation (Thread 2: Deep Dive)**

Graphiti is the closest technical parallel (temporal knowledge graph with
incremental updates). Key differences: Graphiti is agent-centric (LLM
extracts from conversation), lacks a human-authored write model, and uses
LLM-based entity resolution. Graph Explorer is human-centric (deterministic
compilation from authored markdown) with provenance tracing to git. The
bi-temporal model (event time vs transaction time) is worth adopting for
future temporal queries.

**5. Architectural framing (Thread 0: Introduction)**

The entire architecture derives from DSM_6.0 collaboration principles: five
principles map to five architectural constraints that make CQRS the necessary
consequence, not an arbitrary design choice. This framing strengthens the
"why" behind Graph Explorer's architecture.

**Full research:** `~/dsm-agentic-ai-data-science-methodology/docs/research/Literate-CQRS-Knowledge/`

**Next step from DSM Central:** Advance Graph Explorer Sprint 7 to produce
working compilation + queries, then write a blog post using concrete examples
from the implementation.
