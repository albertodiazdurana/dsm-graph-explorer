# Intrinsic-ToC Vision: Graph-to-File Mapping for Agent Navigation

**Date:** 2026-04-13
**Session:** 47
**Author:** Alberto Diaz Durana (with AI assistance)
**Status:** Active research
**Purpose:** Conceptual foundation for BL-302 and its future phases
**Target Outcome:** Design reference for all --knowledge-summary development

---

## 1. The Problem

A repository is a graph of interconnected files, sections, references, and
concepts. An AI agent dropped into a repository needs to quickly understand:
what is here, what is important, how things connect, and where to look for
specific facts. Today, agents rely on READMEs (written for humans, not
machines), file listings (no semantic context), and trial-and-error navigation.

The DSM ecosystem compounds this: multiple repos (TAB, spokes, portfolio,
external contributions) form a network. An agent working in one repo needs to
navigate to another repo's content to answer cross-cutting questions.

## 2. The Intrinsic-ToC Concept

An **Intrinsic-ToC** (Table of Contents) is a graph materialized into an
LLM-readable file. It maps a repository's knowledge graph into a structured,
parseable markdown document that an agent can read for orientation and use as
a starting point for deeper navigation.

### What "intrinsic" means

Intrinsic captures everything that belongs to the repository itself:

- **Structural:** Directory layout, file counts, package organization
- **Semantic:** What each module does, how components relate
- **Quantitative:** Test counts, coverage, section counts, reference counts
- **Methodological:** Which DSM principles apply, which epoch/sprint, how many
  decisions and experiments
- **Connectivity:** Which files are hubs (most referenced), which are orphans
  (disconnected), which sections are load-bearing (hotspots)

The Intrinsic-ToC is not a README (prose for humans) or a GraphML file (XML for
visualization tools). It is a **structured index for LLMs**: machine-parseable,
human-readable, derived from the repository's actual structure.

### Analogy

> "A README for LLMs." The README tells a human developer what the project is.
> The Intrinsic-ToC tells an AI agent what the project contains and how to
> navigate it.

### Naming

- **Intrinsic-ToC:** The static file produced by GE for a single repository
- **Avatar / Ontology:** The cross-repo graph-network that connects all repos
- **Knowledge Summary:** The CLI command (`--knowledge-summary`) that produces
  the Intrinsic-ToC

## 3. The Agent-as-Navigator Model

A critical design decision: **the agent IS the query engine.** There is no
separate MCP server, no API, no local LLM (DEC-009). The main agent (Claude,
or any LLM) reads the Intrinsic-ToC and navigates the file structure itself,
the same way a human reads a book's table of contents and then turns to the
relevant page.

This means the Intrinsic-ToC must be:

1. **Self-contained for orientation.** The agent reads it once and knows what
   the repo contains, what's important, and where to look.
2. **Parseable for extraction.** The agent can search for specific patterns
   (`refs-in:`, `path:`, section numbers) to extract exact values.
3. **Linkable for drill-down.** Each entry points to actual files and lines so
   the agent can navigate deeper.
4. **Cross-referenceable.** Entries reference related content in other repos'
   Intrinsic-ToCs, enabling cross-repo navigation.

### Chain-of-Search Example

Question: "When we built the parser in this repo, which tests did we implement,
how many, and which TAB principles guided us?"

```
1. Agent reads GE's Intrinsic-ToC
   → Finds: "parser/ — Markdown parsing + cross-ref extraction"
   → Follows path to: src/parser/, tests/test_parser.py
   → Reads test count, coverage for parser module

2. Agent follows cross-reference to the avatar (graph-network)
   → Connects GE's parser to TAB's methodology sections
   → Finds: "DSM 4.0 §3 Development Protocol, §4 Tests vs Experiments"

3. Agent reads TAB's Intrinsic-ToC
   → Finds: "§3 Development Protocol" with path + line reference
   → Drills into the actual DSM section for the principles

4. Agent synthesizes: "The parser was built in Epochs 1-2 following
   TDD (§3) with capability experiments (§4). 45 tests, 92% coverage."
```

The Intrinsic-ToC enables this chain without any query API. The agent reads
structured files and follows links, using its own reasoning to traverse.

## 4. Architecture Layers

The Intrinsic-ToC is the first layer of a four-layer architecture:

### Layer 1: Static Intrinsic-ToC (Sprint 16)

A markdown file (~150-200 lines) produced by `--knowledge-summary`. Derived
from graph topology + filesystem metadata. Regenerated on demand. Placed at
`.claude/knowledge-graph.md` (gitignored).

**What it maps:**
- Project structure (directories, packages, file counts)
- Hub documents (most-referenced files, ranked by connectivity)
- Cross-reference hotspots (load-bearing sections)
- Orphan files (disconnected content)

**Data sources:** Graph (references, sections), filesystem (directories, file
counts), pyproject.toml (stack, version), dsm-docs/ (decisions, experiments).

**Condensation rules:** The graph may have thousands of nodes. The ToC has a
~200-line budget. Each component uses a different condensation strategy:

| Component | Budget | Strategy |
|-----------|--------|----------|
| Project Map | ~70 lines | Directory-level summary, top-3 files per dir |
| Hub Documents | ~15 lines | Top-10 files by incoming refs |
| Hotspots | ~25 lines | Sections with 10+ incoming refs, cap at 20 |
| Orphans | ~20 lines | Cap at 15 files, count remainder |
| Header + spacing | ~20 lines | Fixed |

### Layer 2: Agent Navigation (future)

The agent reads the Intrinsic-ToC and navigates files directly. No new
infrastructure needed, this is the agent's native behavior. The quality of
Layer 2 depends entirely on how well Layer 1 is structured.

Improvements to Layer 1 that enable better Layer 2:
- Consistent, searchable entry formats
- File + line references for every item
- Cross-repo pointers (e.g., "related: TAB §3")
- Extractable facts (metrics in consistent format)

### Layer 3: Ecosystem Graph / Avatar (future)

The graph-network that connects all repos in the DSM ecosystem. Each repo
contributes its Intrinsic-ToC as a node. Cross-repo references become edges.

**Components:**
- GE's existing cross-repo analysis (`--compare-repos`) as foundation
- Ecosystem path registry (`.claude/dsm-ecosystem.md`) as the node list
- Cross-repo references extracted from CLAUDE.md `@` imports, inbox entries,
  feedback files, and explicit citations

**The avatar** is the aggregate: the full ontology of all repos, their
structures, their connections, and how they evolve over time.

### Layer 4: Code Ontologies (future)

Knowledge graphs built from code, not just markdown:
- AST parsing (functions, classes, imports, call graphs)
- Code-to-document relationships (which code implements which spec section)
- Test-to-requirement tracing (which tests validate which requirements)
- Unified knowledge trees merging document structure with code structure

Related work: code-review-graph uses Tree-sitter to parse 19+ languages into
AST-based graphs with function/class/import nodes and call/inheritance edges.

## 5. Intrinsic vs Relational Data

The Intrinsic-ToC contains two types of data:

### Intrinsic data (belongs to the file itself)

- Path, filename
- Section count, heading titles
- File size, line count
- Module purpose (what it does)
- Tech stack associations (language, framework)
- Methodology context (epoch, sprint, DSM principles applied)

### Relational data (comes from connections)

- Incoming reference count (how many other files reference this one)
- Outgoing reference count (how many files this one references)
- Parent/child file relationships (directory hierarchy)
- Cross-repo connections (which other repos reference this file)
- Hub score (centrality in the graph)

**Sprint 16 materialization strategy:**
- Intrinsic data: materialized for ALL files in the Project Map
- Relational data: materialized for TOP files only (hubs, hotspots sections)
- Full relational data: stays in the graph, accessible when the agent queries
  the graph directly (future) or when we expand the ToC budget

## 6. Design Principles

### Parseable over pretty

The ToC is read by LLMs, not rendered in a browser. Consistent patterns
matter more than visual formatting:

```
# Prefer:
- parser/ | 4 modules | tests: 45 | coverage: 92% | path: src/parser/

# Over:
- **parser/** — A markdown parsing module with comprehensive test coverage
```

The first format lets an agent search for `tests:` or `path:` to extract
exact values. The second requires natural language understanding to parse.

### Bounded output

Every component has a line budget and a condensation rule. The ToC scales
to any repo size by filtering, not by growing:
- Large repos: more aggressive filtering (higher thresholds, fewer top-N)
- Small repos: most content included (lower thresholds, natural fit)

### Data/format separation

The module separates data extraction from formatting:
- **Data functions** return structured Python objects (lists, dicts)
- **Format functions** render those objects as markdown
- Same data can feed different formats: markdown (Sprint 16), JSON (future),
  MCP response (future Layer 3)

### Graph as foundation, not as boundary

The graph indexes markdown files today. The Intrinsic-ToC describes the whole
project: code, tests, config, docs. Non-graph data comes from the filesystem,
pyproject.toml, and dsm-docs/ contents. The graph enriches, it doesn't limit.

### Extensible without restructuring

New metadata layers (temporal, methodology, metrics) can be added to existing
entries without changing the overall structure. The format supports key-value
pairs that can grow per entry.

## 7. Related Work

Three external projects informed this vision (DSM Central BL-355, 2026-04-13):

### Karpathy LLM Wiki

**Pattern:** Persistent knowledge base with `index.md` (content-oriented
catalog) and `log.md` (chronological record). LLM maintains the wiki,
human curates sources.

**Relevance:** Validates the Intrinsic-ToC concept. Karpathy's `index.md` is
an Intrinsic-ToC maintained by an LLM. Key difference: Karpathy's wiki is
curated (LLM updates it), ours is computed (derived from graph topology).
Both serve the same purpose: structured navigation for LLM consumption.

**Key insight:** "Knowledge compilation over retrieval." Pre-synthesize
navigation aids rather than re-deriving them per query. The Intrinsic-ToC
follows this principle.

### code-review-graph

**Pattern:** AST-based knowledge graph with community detection (Leiden),
blast-radius analysis, and MCP integration for AI tool consumption.

**Relevance:** Directly applicable to Layer 4 (code ontologies). Their Leiden
algorithm informs BL-302 Phase 2 (concept clusters). Their MCP integration
is a reference for future queryable access. Claims 8.2x token reduction by
querying the graph instead of reading the entire codebase.

**Key insight:** Graph-guided context selection reduces token waste. The
Intrinsic-ToC achieves the same for document navigation.

### PageIndex (VectifyAI)

**Pattern:** Hierarchical tree index with LLM reasoning at each navigation
node. Vectorless, reasoning-based RAG.

**Relevance:** Validates tree-based navigation over flat search. Their
approach uses LLM at each node (conflicts with DEC-009), but the tree
structure concept informs our hierarchy design.

**Key insight:** "AlphaGo-inspired tree search" for documents. Navigate a
structured hierarchy rather than similarity-search a flat index.

## 8. Sprint 16 Scope (First Experiment)

Sprint 16 is the first experiment in this vision: mapping DSM Central's
markdown graph (4,703 nodes, 5,041 edges) into a static Intrinsic-ToC.

**What we're testing:**
1. Can graph topology produce a useful orientation document?
2. Do the condensation rules (top-N, thresholds, directory grouping) produce
   readable output at real scale?
3. Is the format parseable enough for agent navigation?

**Deliverables:**
- `knowledge_summary.py` module with data/format separation
- `--knowledge-summary PATH` CLI flag
- Validated against DSM Central repository
- Tests covering all components

**What Sprint 16 does NOT include:**
- Cross-repo references (Layer 3)
- Code ontology parsing (Layer 4)
- Non-markdown metadata enrichment (filesystem, pyproject.toml)
- Temporal/methodology metadata (when built, which principles)

These are future extensions. Sprint 16 proves the core: graph → file.

## 9. Open Questions

1. **Hierarchy granularity:** Directory-level summary is proposed. Should hub
   files get expanded sections while other files stay collapsed?

2. **Cross-repo pointers:** When should the Intrinsic-ToC include references
   to other repos? Sprint 16 scope is single-repo, but the format should
   support cross-repo links from the start.

3. **Regeneration frequency:** The ToC is "static because TAB structure
   doesn't change often." But how often should it be regenerated? On every
   commit? On demand? At session start?

4. **Graph expansion:** The current graph indexes markdown only. When (and how)
   should it expand to include Python source, YAML configs, and other file
   types? This gates Layer 4.

5. **Avatar materialization:** The ecosystem graph (Layer 3) needs a persistent
   store. Is this a FalkorDB database? A set of linked Intrinsic-ToCs? A
   separate graph file?

## 10. Relationship to Portfolio Vision

This research connects to the broader portfolio vision
(https://github.com/users/albertodiazdurana/projects/1):

- The Intrinsic-ToC is a building block for project-level navigation
- The avatar/ontology connects projects into an ecosystem view
- The chain-of-search pattern enables cross-project queries
- The code ontology layer (future) enables code-level navigation across
  the entire portfolio

GE's role: the tool that produces Intrinsic-ToCs and builds the graph
infrastructure for the avatar. Not just a validator, but a knowledge
cartographer.