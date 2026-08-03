# Handoff: Sprint 18 closed, Sprint 19 not yet written

**Date:** 2026-07-31
**Session:** 57
**Author:** Alberto Diaz Durana (with AI assistance)
**Repository:** `dsm-graph-explorer`
**Decision of record:** [DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md) (Accepted)

---

## Read this first

The repository is **mid-transaction**. DEC-012 is Accepted, and two of the six artifacts
that implement it are done. **`dsm-docs/plans/epoch-5-plan.md` has not been updated**, so
it still describes Sprint 18 as live work, still lists "BL-302 Phase 2 delivered" as an
Epoch 5 success criterion, and still numbers Sprint 19 as hop distance.

If you open the epoch plan and trust it, you will get the wrong picture of the entire
epoch. The checkpoint's pending item 1 is the consistency repair and should be done
before anything else.

| Artifact | State |
|---|---|
| DEC-012 (decision record) | **Done**, Accepted |
| BL-302 Phase 2 (closure + P4 resolution) | **Done** |
| epoch-5-sprint-18-plan.md (closure + dispositions) | **Done** |
| epoch-5-plan.md (criterion + renumbering) | **PENDING, do first** |
| BL-GE-002 (new work item) | **PENDING**, depends on the above |
| Sprint 19 plan | **PENDING**, depends on both |

## What was decided, and why it is not just a scope cut

Sprint 18 was Leiden clustering. S56 halted it on measurement: the partition beats a
degree-preserving null by only **2.8%** on a graph where ~25% of files carry any
cross-reference, and the quality metric in use was null-indistinguishable, therefore
invalid.

S57 did not resolve this by picking among the four candidate designs. It re-derived the
aim from the Intrinsic-ToC vision, and found:

- **Clustering appears nowhere in the vision.** §4 lists what Layer 1 maps (project
  structure, hub documents, cross-reference hotspots, orphan files); §2 defines
  connectivity as hubs, orphans, hotspots. Clustering is in neither, nor in the §4
  condensation budget. It entered via S49's GraphRAG fit study, whose premise S56 refuted.
- **Layer 1 as specified already ships.** Verified in code: `generate_knowledge_summary`
  calls all four emitters. Phase 2 would have added an unspecified fifth.
- **The vision already asked the density question.** §9 Q4, unanswered since 2026-04, and
  it gates Layer 4. The 25% coverage is a consequence of that open question, not a new
  defect.

So Sprint 18 was optional scope against the vision, and the replacement work answers a
question the vision itself raised. DEC-012 carries the full justification,
counter-evidence and revisit trigger; do not re-derive it.

## Two things the next session must not re-litigate

**The P4 gate is resolved.** "Cuts across obvious boundaries" is struck. The gate is now a
**null-controlled degeneracy floor**: the partition must exceed a degree-preserving
rewire by a pre-registered margin and must not collapse. The original wording is
preserved in an amendment block because the research file quotes it. A provenance search
(`git log -S` plus the authoring session's transcript) found the clause written once with
no recorded deliberation, so there is no author intent to recover, and reopening the
question will not produce one.

**Clustering is not refuted as a technique.** DEC-012 scopes the finding to this
substrate at this coverage. The revisit trigger is explicit: if BL-GE-002 or BL-GE-001
raises coverage materially above ~25%, clustering may be re-proposed, and must then clear
the degeneracy floor rather than an absolute modularity threshold.

## Calibration note on the analysis behind this

Three recommendations were made across S56 and S57 on the Sprint 18 question, and **all
three had a key supporting claim overturned by cheap measurement**, twice after the
recommendation had already been approved. The pattern is consistent and worth carrying
forward: the *measurements* in this chain held up, the *inferences layered on them* did
not.

The most recent instance is recorded in DEC-012 counter-evidence item 1. The agent argued
that PageRank would collapse to the shipped degree ranking on a graph this sparse, making
a centrality upgrade cosmetic. A pre-registered check refuted that on both corpora. That
is why **option A (centrality) is recorded as unresolved rather than rejected**, and why
every justification in DEC-012 carries a provenance tag.

Practical consequence: when Sprint 19 produces a claim about graph structure, measure it
before building on it.

## Session 57 also changed how we work

`/dsm-align` moved this project from DSM v1.18.0 to v1.19.0, which replaced the App
Development Protocol (BL-478). Two changes bite immediately:

- **The IDE permission window is not the concept gate.** Describe a file and get concept
  approval in conversation before creating it, including when writes are auto-approved.
- **One bite per stop**, where a bite is the smallest increment the user can verify, and
  code is test-first.

The alignment also exposed a self-contradiction in `.claude/CLAUDE.md` (one bullet said
test-first, the next said test-after); the duplicated bullets were deleted rather than
reworded, so the managed block is now the single statement of that rule.

**The Sprint Boundary Checklist is now 11 items**, canonical 9 plus 2 marked `**Local:**`.
It had diverged (7 in CLAUDE.md, 9 in the sprint plans) and the "7 vs 9" framing was
misleading: neither list was a subset of the other. Use the 11-item form in the Sprint 19
plan.

## Open branches

None. `staa/2026-07-30-s56-lessons` merged via PR #15 and deleted. All S57 work was
committed directly on `session-57/2026-07-30`.
