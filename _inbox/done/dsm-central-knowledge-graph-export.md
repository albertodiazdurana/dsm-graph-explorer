# Knowledge Graph Export Feature Request

**From:** DSM Central (Session 163)
**Date:** 2026-04-02
**Priority:** Medium
**Type:** Feature request

## Context

EXP-002 (Knowledge Graph Feasibility Assessment) confirmed that GE Sprint 14 can
build a rich structural graph from DSM Central (4,703 nodes, 5,041 edges), but the
only portable export (GraphML) is not agent-consumable. A 4MB XML file wastes
context budget without providing navigational value to an LLM.

## Request

Add a new CLI flag `--knowledge-summary PATH` that produces an agent-consumable
markdown file (~150-200 lines) derived from the structural graph. This provides
top-down project navigation complementing DSM_0.2's bottom-up entry.

### Proposed Output Sections

1. **Document Hierarchy** - tree view with module relationships
2. **Hub Documents** - top 10 by reference connectivity, with 1-line purpose
3. **Concept Clusters** - document groups from co-reference patterns
4. **Navigation by Project Type** - recommended reading order per DSM type
5. **Cross-Reference Hotspots** - sections referenced 10+ times
6. **Orphan Detection** - files with zero incoming references

### Design Constraints

- Markdown output (agents read natively)
- ~150-200 lines target (context-budget friendly)
- Derived from graph topology (hub scores, clustering, reference chains)
- Placement: `.claude/knowledge-graph.md` (gitignored, regenerated on demand)

## Evidence

- Full experiment report: DSM Central `data/experiments/EXP-002-knowledge-graph-feasibility/results.md`
- Graph artifact: `data/experiments/EXP-002-knowledge-graph-feasibility/dsm-central-graph.graphml`

## Tracking

- DSM Central BL: BACKLOG-302 (agent-consumable-knowledge-graph-export)
- Parent: BL-002 (DSM Graph Explorer)
- Iteration plan: v1 in GE, iterate based on agent feedback across sessions

## Additional: GraphML None-Value Bug

`export_graphml()` crashes when section attributes contain `None` (unnumbered
headings have `number=None`). NetworkX's GraphML writer rejects `NoneType`.
Workaround: replace None with empty string before `nx.write_graphml()`.
Sprint 15 fix candidate.
