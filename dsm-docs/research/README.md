# dsm-docs/research/

Literature review, state-of-art research, and experiment design documents.

Created in Phase 0.5 (research phase) before implementation. Referenced when making
architecture decisions. **Reference:** DSM 4.0 recommends research grounding before
implementation.

> **Restructured S58 (2026-08-04).** This index previously held a single generic
> `File | Purpose` table listing three entries, two of which had already moved to
> `done/`, and omitted every research file added since Epoch 2. The five sub-tables below
> are the structure `/dsm-research-add` inserts into; the flat table was not, so the skill
> had no heading to write under. Filenames predating the `YYYY-MM-DD_{topic}.md`
> convention are tolerated and listed as-is, never renamed.

## Active research

### 1. Tied to an active backlog item (research is the BL's primary deliverable)

| Date | File | Linked BL | Status |
|------|------|-----------|--------|
| , | *(none currently)* | , | , |

### 2. Informs an active BL but is not its primary deliverable

| Date | File | Linked BL | Status |
|------|------|-----------|--------|
| 2026-04-13 | [Intrinsic-ToC Vision: Graph-to-File Mapping for Agent Navigation](2026-04-13_intrinsic-toc-vision.md) | BL-GE-002 | Active |
| 2026-07-21 | [Cluster Quality and Graph Density for the Intrinsic-ToC](2026-07-21_cluster-quality-graph-density.md) | BL-GE-002 | Active |

The vision file is the conceptual anchor for all `--knowledge-summary` work, not for
BL-GE-002 alone; it is linked to the current sprint's BL because this table takes one
link. It also governs BL-GE-001 and the closed BL-302 phases.

The cluster-quality file was authored as BL-302 Phase 2's primary deliverable, and that BL
closed without delivery ([DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md)).
It is kept **active** rather than moved to `done/` because BL-GE-002 §P1 and §P4 reuse its
coverage measurement and null-model methodology directly, and DEC-012 §Conditions 2 makes
its ~25% figure the reference point for the clustering revisit trigger.

### 3. Findings ready for promotion to a BL (no BL filed yet)

| Date | File | Action | Status |
|------|------|--------|--------|
| 2026-04-02 | [DSM Central EXP-001: Document Reachability](dsm-central-exp-001-reachability.md) | File BL "EXP-001 reference-graph validation" or move to done | New finding |
| 2026-04-02 | [DSM Central EXP-002: Knowledge Graph Feasibility](dsm-central-exp-002-knowledge-graph-feasibility.md) | File BL or move to done | New finding |

EXP-001 is scheduled work with no BL behind it: [epoch-5-plan.md](../plans/epoch-5-plan.md)
§Sprint 20 lists "validate GE parser output against EXP-001's 286-edge reference graph",
and per the Actionable Work Items rule a plan line is not itself a work item. A BL is
required before Sprint 20 can start.

EXP-002 is the origin document for BL-302 (Central `BACKLOG-302`). Both BL-302 phases are
now closed, so this is more likely a `done/` candidate than a promotion candidate. It is
parked here rather than moved because that is a disposition call, not a filing one.

### 4. Tool / methodology assessments awaiting decision

| Date | File | Decision needed | Status |
|------|------|-----------------|--------|
| 2026-03-10 | [Experiment Documentation Standards](experiment-documentation-standards.md) | Whether the four-element structure is settled practice, or still open | Awaiting decision |

Fed `feedback-to-dsm` methodology Entry 34 and backlogs Proposal #29 (S24). No disposition
has been recorded since.

### 5. Untracked carryover

| Date | File | Decision needed | Status |
|------|------|-----------------|--------|
| , | *(none currently)* | , | , |

---

## Completed

Nine files in [`done/`](done/), covering Epochs 1-4 plus the S49/S50 GraphRAG and
Semantic-Concept-Layer studies. Moved there by `/dsm-research-done`.
