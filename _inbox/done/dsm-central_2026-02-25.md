### [2026-02-25] Sprint 7 Architecture Alignment Analysis

**Type:** Action Item
**Priority:** Medium
**Source:** DSM Central

Sprint 7 (NetworkX graph prototype) was analyzed for alignment with the 3-layer
knowledge architecture (Session 66 decision) and four downstream backlog items
(BL-090, BL-137, BL-139, BL-144).

**One concrete design recommendation for Sprint 7:**

Store `context_excerpt` on SECTION nodes in `graph_builder.py`. The `Section`
dataclass already has this field (populated in Sprint 6, ~50 words of prose after
each heading). The exp004 benchmark code (`build_graph()`, line 66-74) stores
`title`, `number`, `file`, `line`, `level` but omits `context_excerpt`. Adding it
bridges Layer 1 (structural mapping) to BL-139 Layer 2 (semantic characterization,
Step 3: "Fill with context").

**Two optional trade-offs (decide during implementation):**
- String enums for node/edge types (code quality, not architectural necessity)
- Similarity scores on REFERENCES edges (useful but creates semantic-graph module coupling)

**Three proposals retracted after evidence review:**
- PARENT_OF edges (premature; Sprint 8+ adds when needed)
- Class-based builder (contradicts architecture decision's BL-144 separation)
- Metadata dict (NetworkX nodes are already schemaless dicts)

**Cross-backlog awareness:**
- BL-137 (Information Lifecycle): unfiltered graph captures operational artifacts
  (backlog, handoffs, feedback) as nodes; serves as audit substrate with different config
- BL-090 (Modularization): two steps removed (Sprint 7 → Sprint 8+ → BL-090); no design changes

**Full analysis:** `~/dsm-agentic-ai-data-science-methodology/docs/decisions/2026-02-25_sprint7-architecture-alignment.md`
