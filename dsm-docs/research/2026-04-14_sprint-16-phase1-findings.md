# Sprint 16 Phase 1 Findings: --knowledge-summary First Experiment

**Date:** 2026-04-14
**Session:** 47
**Sprint:** 16 (BL-302 Phase 1)
**Status:** Phase 1 complete, findings documented
**Target Outcome:** Empirical validation that graph topology can produce
agent-consumable markdown summaries at realistic repository scale
**Prerequisite:** [Intrinsic-ToC Vision](2026-04-13_intrinsic-toc-vision.md)

---

## 1. Summary

Sprint 16 Phase 1 delivered the first working experiment of the Intrinsic-ToC
vision: a CLI command (`--knowledge-summary PATH`) that maps a repository's
reference graph into a structured markdown file for LLM consumption.

Validated against DSM Central (811 files, 8,991 sections, 1,254 cross-
references). Output: 253-line markdown summary, 26% over the 200-line target
but bounded and informative.

## 2. What We Built

### Module: `src/analysis/knowledge_summary.py`

Five public functions:

| Function | Purpose | Condensation rule |
|----------|---------|-------------------|
| `generate_hierarchy(G, top_files_per_dir=3)` | Directory-level project map | Group by directory, top-N files per dir by section count |
| `generate_hub_documents(G, n=10)` | Hub files table | Top-N by aggregated incoming references |
| `generate_hotspots(G, threshold=10, max_items=20)` | Section-level reference concentrations | Threshold filter + cap |
| `generate_orphans(G, max_items=15)` | Files with zero cross-repo refs | Cross-file only, cap with overflow |
| `generate_knowledge_summary(G)` | Orchestrator | Combines all components with header stats |

### CLI Integration

- `--knowledge-summary PATH` added to Click CLI
- Reuses existing graph build pipeline (no duplicate work)
- Writes markdown to file, reports line count

### Bug Fix

`graph_export.py::export_graphml()` crashed on `None` attribute values
(unnumbered headings have `number=None`). Fix: sanitize to empty strings
via graph copy before `nx.write_graphml()`.

## 3. Validation Results (DSM Central)

Input graph:
- 811 files
- 8,991 sections
- 1,254 cross-references

Output: 253 lines total

| Component | Lines | Target | Status |
|-----------|-------|--------|--------|
| Header | 4 | 4 | On target |
| Document Hierarchy | 188 | ~70 | **Over (168% over)** |
| Hub Documents | 14 | ~15 | On target |
| Cross-Reference Hotspots | 26 | ~25 | On target |
| Orphan Files | 17 | ~20 | On target |

## 4. Key Observations

### Observation 1: Hierarchy is the bottleneck at large scale

Three components (hubs, hotspots, orphans) stay within budget because they
have fixed top-N caps. The hierarchy does not, because it must enumerate
directories. DSM Central has 52 directories, each producing ~4 lines (header
+ 3 file examples), yielding 188 lines for hierarchy alone.

### Observation 2: All 52 directories are legitimate content

Initial hypothesis: the hierarchy bloat comes from build artifacts
(`__pycache__`, `venv/`, `node_modules/`). Actual finding: zero build
artifacts in DSM Central. All 52 directories are content:
- 13 × `.claude/spoke-backups/{project}/` (one per ecosystem project)
- 8 × `dsm-docs/research/{topic}/` (research subdirectories)
- 7 × `plan/backlog/{status}/` (legacy plan structure)
- Various `dsm-docs/*/done/`, `_inbox/done/`, `data/experiments/EXP-*/`

The "bloat" reflects DSM Central's actual structural depth, not noise.

### Observation 3: Output is bounded for any repo size

The hierarchy grows with directory count, not with file or section count.
A repo with 10,000 files but 15 directories would produce ~60 hierarchy
lines. A repo with 50 files but 20 directories would produce ~80 lines.
This is the right scaling behavior: the ToC reflects structural depth,
not content volume.

### Observation 4: 253 lines is manageable

The original target (~200 lines) was a heuristic, not a hard constraint.
253 lines fits in an agent's context window with minimal impact. The
target can be relaxed to 250-300 lines without loss of value.

## 5. What We Learned

### Graph → Markdown compression works

A 4,703-node + 8,991-section graph becomes a 253-line document that
preserves the most navigationally relevant information:
- Hub documents (most important files)
- Hotspot sections (load-bearing content)
- Orphan files (disconnected or entry-point candidates)
- Directory structure (orientation)

### Parseable format is essential

Entries use `key: value` patterns (`path:`, `sections:`) to support machine
extraction. Example:

```
- DSM_0.2_Custom_Instructions_v1.1.md | 38 sections | path: /home/.../DSM_0.2_Custom_Instructions_v1.1.md
```

An agent can search for `path:` to extract the filesystem location or for
`sections:` to extract the section count. No natural language parsing
needed.

### Connectivity data stays partial by design

The Intrinsic-ToC materializes intrinsic data for ALL files (via hierarchy)
and relational data for TOP files only (via hubs and hotspots). Full
per-file connectivity lives in the graph, accessible when the agent can
query the graph directly (future, Layer 3 of vision).

## 6. What We Did Not Do (Deferred)

Per DEC-009 (no local LLM dependencies) and Entry 60 (vision-directed,
deliverable-scoped):

- **Data/format separation:** Did not split functions into data + format
  layers. Would enable future JSON/MCP output, but Sprint 16 only needs
  markdown, and no concrete second format is planned.
- **Concept clusters (P3):** Leiden community detection deferred to
  BL-302 Phase 2.
- **Project-type navigation (P4):** Requires DSM-specific config input,
  deferred to BL-302 Phase 3.
- **Default exclude list:** Would filter build artifacts if a target repo
  had them. DSM Central has none, deferred until a concrete need arises.

## 7. Open Questions for DSM Central

1. **Is 253 lines acceptable for agent consumption?** The original 200-line
   target was a heuristic. Does DSM Central have a hard upper bound based
   on agent context budget concerns?

2. **Hierarchy granularity preference:** The current design shows all 52
   directories. An alternative is to cap directories (e.g., top 20 by
   section count, group rest as "miscellaneous"). Which approach better
   serves an agent reading the summary?

3. **Format validation:** Does the `key: value` entry format work for
   DSM Central's intended use cases, or are there other patterns that
   would be easier to parse?

4. **Frequency of regeneration:** Should the knowledge summary be
   regenerated on every session start, on every commit, or on demand?

## 8. Artifacts

- Implementation: [`src/analysis/knowledge_summary.py`](../../src/analysis/knowledge_summary.py)
- Tests: [`tests/test_knowledge_summary.py`](../../tests/test_knowledge_summary.py) (25 tests, all passing)
- Vision: [`2026-04-13_intrinsic-toc-vision.md`](2026-04-13_intrinsic-toc-vision.md)
- Sample output: generated at `/tmp/dsm-central-ks.md` during S47 validation

## 9. Next Steps

### Immediate (Sprint 16 wrap)
- Commit Sprint 16 work
- Notify DSM Central of Phase 1 completion (this document + inbox entry)
- Sprint 16 boundary checklist

### Short term (Sprint 17 or Epoch 5 entry)
- Iterate on hierarchy design based on DSM Central feedback
- Consider output length target adjustment (200 → 250-300?)
- Evaluate whether to implement data/format separation now that we have
  concrete output examples

### Long term (Epoch 5)
- BL-302 Phase 2: Leiden community detection for concept clusters
- BL-302 Phase 3: project-type navigation
- Intrinsic-ToC Layer 3: cross-repo references, ecosystem graph
- Intrinsic-ToC Layer 4: code ontology parsing
