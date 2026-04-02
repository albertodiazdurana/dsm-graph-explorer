# DSM Central EXP-002: Knowledge Graph Feasibility Assessment

**Date reviewed:** 2026-04-02
**Source:** DSM Central Session 163, `data/experiments/EXP-002-knowledge-graph-feasibility/results.md`
**DSM Central BL:** BACKLOG-302 (agent-consumable-knowledge-graph-export)
**GE parent:** BL-002

---

## Summary

EXP-002 tested whether GE Sprint 14 can generate a knowledge graph artifact from
DSM Central sufficient for agent-consumable top-down project navigation.

**Result: PARTIAL PASS.** The graph infrastructure is proven, but the export
format is not agent-consumable.

## Key Findings (GE-relevant)

### Graph Infrastructure: Sufficient

GE Sprint 14 produced a structurally rich graph from DSM Central:

| Metric | Value |
|--------|-------|
| Total nodes | 4,703 |
| File nodes | 202 |
| Section nodes | 4,501 |
| Total edges | 5,041 |
| CONTAINS edges | ~4,501 (file to section) |
| REFERENCES edges | ~540 (cross-refs) |
| GraphML size | 4.1 MB |

Node metadata available per section: `title`, `number`, `file`, `line`, `level`,
`context_excerpt` (~50 words). This is sufficient for generating a concise
agent-readable summary without reading full files.

### Hub Documents Identified

| File | Incoming refs | Role |
|------|--------------|------|
| DSM_1.0.A_Core_Workflow.md | 149 | Central methodology workflow |
| CONTRIBUTING.md | 94 | Contribution governance |
| DSM_1.0.D_Session_Quality.md | 54 | Session quality practices |
| DSM_0.0_START_HERE_Complete_Guide.md | 44 | Human entry point |
| DSM_0.2.B_Artifact_Creation.md | 36 | Artifact creation protocols |

### Format Gap

GraphML XML (4MB) is designed for visualization tools (Gephi, yEd), not LLM
consumption. A 4MB XML file would consume ~15-20% of an agent's context window
and provide worse navigational value than a 200-line markdown summary.

### Bug Found

`export_graphml()` crashes when section attributes contain `None` (unnumbered
headings have `number=None`). NetworkX's GraphML writer rejects `NoneType`.
Workaround: replace None with empty string before `nx.write_graphml()`.

## Feature Request: --knowledge-summary

DSM Central requests a new CLI flag `--knowledge-summary PATH` producing
agent-consumable markdown (~150-200 lines) with:

1. **Document Hierarchy** - tree view with module relationships
2. **Hub Documents** - top 10 by reference connectivity, with 1-line purpose
3. **Concept Clusters** - document groups from co-reference patterns
4. **Navigation by Project Type** - recommended reading order per DSM type
5. **Cross-Reference Hotspots** - sections referenced 10+ times
6. **Orphan Detection** - files with zero incoming references

Design constraints: markdown output, ~150-200 lines, derived from graph
topology (hub scores, clustering, reference chains), placed at
`.claude/knowledge-graph.md` (gitignored, regenerated on demand).

## GE Action Items

1. **Bug fix (small):** Replace None with empty string in `export_graphml()`.
   Independent of the feature, could ship in any sprint.
2. **Feature (Sprint 16 candidate):** `--knowledge-summary` flag. The graph
   infrastructure is proven, the gap is a presentation layer. Estimated scope:
   1 sprint. Requires: summary generation logic, markdown formatter, CLI flag.
3. **Validation opportunity:** The 4,703-node graph artifact
   (`dsm-central-graph.graphml`) can serve as a regression test fixture for
   future parser changes.

## Artifacts

- Full experiment report: DSM Central `data/experiments/EXP-002-knowledge-graph-feasibility/results.md`
- Graph artifact: DSM Central `data/experiments/EXP-002-knowledge-graph-feasibility/dsm-central-graph.graphml`
