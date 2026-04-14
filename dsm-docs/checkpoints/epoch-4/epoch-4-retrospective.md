# Epoch 4 Retrospective

**Project:** DSM Graph Explorer
**Epoch:** 4
**Sprints covered:** 13-16
**Date:** 2026-04-14
**Duration:** 2026-03-13 to 2026-04-14 (~1 month)
**Sessions:** 14 (S34-S47)

## Epoch Summary

Epoch 4 focused on ecosystem integration and agent-consumable outputs.
Starting from Epoch 3's graph infrastructure (FalkorDBLite adoption,
cross-reference resolution), Epoch 4 delivered four sprints that made GE
useful as an ecosystem tool, not just a validator:

| Sprint | Theme | Key Delivery |
|--------|-------|--------------|
| 13 | BL-090 resilience | Multi-file DSM_0.2 support, heading-based sections, EXP-007 (531 tests) |
| 14 | Incremental updates | `update_files()`, FalkorDB indexes, `to_networkx()` (547 tests) |
| 15 | Protocol usage analysis | Four-layer methodology, EXP-009 CONDITIONAL PASS (664 tests) |
| 16 | Knowledge summary export | `--knowledge-summary` CLI, BL-302 Phase 1, Intrinsic-ToC vision (689 tests) |

## What worked across sprints

- **TDD discipline remained strong.** All four sprints wrote tests before
  implementation, even when the tests initially failed (red-green cycle).
  Test count grew from 531 to 689 without coverage drop (91% maintained).

- **Capability experiments anchored each sprint.** EXP-007 validated
  parser resilience, EXP-008 validated heading reference detection, EXP-009
  validated protocol usage analysis. Each experiment produced
  documentation (failure modes, threshold calibrations, ground truth sets)
  that would have been hard to capture without the experiment framing.

- **Inbox-driven planning.** DSM Central requests (EXP-002, BL-230, BL-303)
  became GE's concrete work items. The hub-spoke inbox pattern produced
  cleaner scope than ad hoc prioritization would have.

- **Per-session feedback files.** The shift from append-only `backlogs.md`
  to per-session files (YYYY-MM-DD_sN_*.md) made feedback easier to push,
  track, and archive. The three-file atomic protocol (methodology + backlogs
  + notification) worked well.

- **Cross-spoke knowledge transfer.** S47's response to heating-systems'
  playbook request demonstrated the ecosystem's knowledge-sharing value,
  even without formal tooling.

## What didn't work

- **Boundary protocol gaps surfaced late.** Three sprint/epoch boundary
  protocol gaps were discovered in S47 (Entries 61, 62, 63). Earlier
  sprints completed without these protocols being tight, and the
  inconsistency accumulated silently. Sprint 15 boundary was verified
  complete but its checkboxes were never ticked; Sprint 16 close almost
  defaulted to session wrap-up without running the boundary checklist.

- **PGB concept gate was applied inconsistently.** S47 Entry 59 captured
  the gap: the concept gate at the backlog level passed, but module-level
  design decisions (condensation rules, thresholds) were not reviewed
  before code was written. The hierarchy component was built unbounded.

- **Speculative architecture crept in.** S47 also surfaced "design for
  hypothetical future requirements" (Entry 60) when the agent proposed
  data/format separation with no concrete second format planned.

- **Sprint 15 tried to do too much.** The four-layer methodology was a
  larger scope than initially planned. EXP-009 conditional pass revealed
  the limits of reference counting as a measurement (behavioral vs
  procedural protocols).

## Methodology effectiveness

**Most useful DSM sections at epoch scale:**

- **DSM 4.0 §3 Development Protocol (TDD):** Stayed reliable across all
  four sprints. Every new module followed the same red-green pattern.
- **DSM_0.2 §17 CLAUDE.md Configuration:** The `@` reference + alignment
  template system kept the project aligned with methodology evolution
  (v1.3.39 → v1.4.17) without manual sync work.
- **DSM_3 Inbox Protocol:** The per-inbox-entry lifecycle (arrive →
  process → done/) produced clean coordination with DSM Central and
  portfolio.

**Least useful / gap-prone:**

- **Sprint Boundary Checklist (CLAUDE.md):** Present but no automatic
  trigger; completion was verbal, not procedural.
- **Epoch-level protocols:** Missing entirely (Entry 63).
- **PGB concept gate granularity:** Underspecified for complex artifacts
  (Entry 59).

**Gaps that appeared repeatedly across sprints:**

- Boundary checklists marked in CLAUDE.md but never reconciled with actual
  completion state in the epoch plan (Entry 62). Affected both Sprint 15
  and Sprint 16.
- Verbal acknowledgment of completion substituting for procedural closure.
  Affected sprint transitions at S40/41 boundary (lightweight sessions)
  and the S46/47 boundary.

## Key decisions and outcomes

| DEC | Description | Retrospective |
|-----|-------------|---------------|
| DEC-008 (S39) | Heading-based section IDs with slug fallback | Right call. Unblocked EXP-008 and the full DSM_0.2 modular split. No regressions. |
| DEC-009 (S47) | No local LLM dependencies | Too soon to fully validate, but removing three speculative COULDs (spaCy, sentence-transformers, LLM validation) tightened Epoch 5 planning. Direction seems right given the agent-as-LLM architecture. |

## Metrics Summary

| Metric | Epoch 3 end | Epoch 4 end | Delta |
|--------|-------------|-------------|-------|
| Tests | 531 | 689 | +158 |
| Coverage | 95% | 91% | -4 pp |
| Source modules | 18 | 25 | +7 |
| Test files | 19 | 26 | +7 |
| CLI flags | ~10 | ~14 | +4 (--knowledge-summary, --protocol-usage, --usage-compare, --compare-repos) |
| Experiments | 6 | 9 | +3 (EXP-007, 008, 009) |
| Decisions | 8 | 9 | +1 (DEC-009) |
| Feedback entries | ~46 | 62 | +16 |
| Backlog proposals | ~42 | 56 | +14 |

Coverage dropped 4 percentage points as new modules entered with
realistic (not 100%) coverage patterns. Still well above the 80% target.

## Recommendations for DSM

Four proposals pushed to Central in S47:

- **Proposal #52:** PGB concept gate granularity (§17.1)
- **Proposal #53:** Vision-directed, deliverable-scoped (DSM_6.0 §1.9)
- **Proposal #54:** Sprint Boundary Checklist automatic trigger
- **Proposal #55:** Verification-triggered checkbox reconciliation
- **Proposal #56:** Epoch Boundary Checklist + skill (this retrospective
  itself was produced without canonical guidance)

All five proposals surfaced from real Epoch 4 incidents, not theoretical
concerns.

## Ecosystem Impact

- **DSM Central:** Received `--knowledge-summary` implementation that
  addresses EXP-002 PARTIAL PASS; produced a 253-line summary of its own
  repository.
- **Heating-systems-conversational-ai:** Received the contribution playbook
  response based on GE's FalkorDBLite experience (S47).
- **Portfolio:** Notified of Sprint 15, Sprint 16, and epoch completion.
- **FalkorDBLite (external):** Issue #85 still open, awaiting maintainer
  response (one full epoch of silence).

## What carries forward to Epoch 5

- **5-theme deferred requirements** (Intrinsic-ToC evolution, Avatar,
  graph infrastructure, open source, parser extensions) as Epoch 5 input.
- **BL-302 Phase 2-3** (Leiden clustering, project-type navigation) as
  the natural continuation of Sprint 16.
- **4 open questions for DSM Central** (line budget, hierarchy cap, format
  validation, regeneration cadence) to inform Sprint 17 scoping.
- **Intrinsic-ToC vision** as the conceptual anchor for graph-related work.
