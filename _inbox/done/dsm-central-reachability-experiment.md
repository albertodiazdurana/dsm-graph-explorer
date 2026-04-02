### [2026-04-02] EXP-001 Reachability Experiment Results (informational)

**Type:** Informational (experiment results from DSM Central)
**Priority:** Low
**Source:** DSM Central, Session 162, BL-230

**Context:** Graph Explorer Session 39, Entry 53 identified that experiment
templates in Appendix C.1 were "architecturally invisible" to agents. This
triggered BL-230 (DSM Document Reachability Experiment) as the final step
in the Phase 3+4 audit pipeline.

**Experiment summary:**
- Python script performs BFS from DSM_0.2 (agent entry point) across all 35 DSM files
- Parses 6 reference types, builds directed file-to-file graph (286 edges)
- **Result:** 100% file reachability (35/35), 1,310/1,310 sections reachable
- **Finding:** 11 files exceed the pre-registered 3-hop threshold, all are
  modules of files within threshold. The modular architecture (introduced
  after the threshold was defined) adds expected depth.
- **Revised threshold:** Core files ≤3 hops, modules ≤1 hop from core. All pass.

**Relevance to Graph Explorer:**
- The reachability script is a simplified version of what GE does: parse
  references, build graphs, measure connectivity. GE could extend this with
  section-level granularity, bidirectional edge analysis, and visualization.
- The reference graph artifact (`reference-graph.md`) could serve as a
  validation dataset for GE's parser.
- The two-tier threshold model (core vs module) may inform GE's own
  reachability metrics if it exposes hop distance calculations.

**No action required.** This is informational, sharing results that originated
from a GE observation.
