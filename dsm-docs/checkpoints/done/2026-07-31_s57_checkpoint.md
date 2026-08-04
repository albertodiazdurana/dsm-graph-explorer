**Consumed at:** Session 58 start (2026-08-04)

# Session 57 Checkpoint
**Date:** 2026-07-31
**Branch:** session-57/2026-07-30
**Last commit:** (see `git log --oneline -1`; wrap-up commit is the session's final)

## Work completed this session

Resolved the Sprint 18 direction by re-deriving the project's aim from the Intrinsic-ToC
vision rather than continuing to rank the four candidate designs against each other.
Clustering appears nowhere in the vision, and Layer 1's four specified components were
verified to ship already, so **DEC-012 closes BL-302 Phase 2 as out-of-vision-scope** and
replaces Sprint 18 with a new Sprint 19 (BL-GE-002, graph source expansion). Along the
way: resolved the P4 gate ambiguity to a null-controlled degeneracy floor, ran
`/dsm-align` to v1.19.0, removed a self-contradiction the alignment exposed in CLAUDE.md,
reconciled the Sprint Boundary Checklist to 11 items, and merged the S56 STAA commit
separately via PR #15.

## Pending next session

**1. Artifact 4, edit `dsm-docs/plans/epoch-5-plan.md`. Do this FIRST.**
The repository is currently **inconsistent with its own accepted decision**. DEC-012 is
Accepted and both BL-302 Phase 2 and the Sprint 18 plan are closed against it, but the
epoch plan still describes Sprint 18 as live work, still lists "BL-302 Phase 2 delivered"
as a success criterion, and still numbers Sprint 19 as hop distance. A reader who opens
the epoch plan alone gets the wrong picture of the whole epoch. Two edits are required:
reframe the Phase 2 criterion using the precedent already written two bullets above it
(the DEC-010 C3 case, "the phase reaching a recorded resolution, not the gate passing"),
and apply the renumbering 19 → graph expansion, 20 → hop distance, 21 → ecosystem.
**Blocks artifacts 5 and 6:** both reference "Sprint 19", and until the epoch plan is
renumbered that number still belongs to hop distance, so writing them first would create
two documents pointing at different sprints under the same number.

**2. Artifact 5, create `dsm-docs/plans/BL-GE-002_graph-source-expansion.md`.**
Depends on artifact 4. Formalises Intrinsic-ToC Vision §9 Open Question 4 ("the graph
indexes markdown only; when should it expand to Python source, YAML configs and other
file types? This gates Layer 4"). Per the Actionable Work Items rule the vision question
is input, not a work item, so nothing can be implemented until this BL exists. **Scope
decided in S57 and must be honoured:** config/YAML files and cross-file link extraction
only. **Python AST work is explicitly out of scope** and must be written into the BL as
an out-of-scope item with its reason, not merely omitted, because an unstated exclusion
is how clustering crept in originally. Must also state the boundary against BL-GE-001:
BL-GE-001 adds concept *edges* between existing nodes, BL-GE-002 adds *nodes* from new
file types. Both raise graph density by different mechanisms; if the boundary is not
stated at authoring time the two will overlap and have to be untangled later.

**3. Artifact 6, create the Sprint 19 plan.**
Depends on artifacts 4 and 5. Must follow DSM_2.0.C §1 Template 8 (all five sections plus
the three header-block fields) and must carry the **reconciled 11-item** Sprint Boundary
Checklist, not the canonical 9, since items 10 and 11 are marked local additions now
present in both `.claude/CLAUDE.md` and the sprint-18 plan. If the 9-item form is copied
from Template 8 verbatim without the two local items, the divergence reconciled this
session reopens immediately.

**4. Run or explicitly defer the Sprint 18 boundary checklist.**
Sprint 18 is closed, so its boundary is due, and the checklist is now 11 items. Several
are genuinely N/A for a sprint that shipped no feature, but that judgement should be
recorded rather than assumed. **Note a real blocker inside it:** canonical item 5
requires `dsm-docs/guides/smoke-tests.md` to be current, and **that file does not exist in
this repository**, so the item has never been actionable here. Decide whether to create
it, mark it permanently N/A for this project, or raise it with Central.

**5. Decide what happens to option A (centrality upgrade).**
Recorded in DEC-012 as *unresolved, not rejected*, and it has measured support: a
pre-registered check showed PageRank materially reorders the shipped degree-based hub
list (GE 9/10 positions changed, DSM Central 5/10 with 2 new entrants, global Pearson r
0.92). It is a small, cheap Layer 1 quality improvement that needs no new dependency,
`networkx` already ships `pagerank` and `hits`. It needs a human decision because it is
polish on a component whose specified form already ships, so it competes with Sprint 19
for the same time rather than blocking it. **If skipped:** nothing breaks, but the
measurement rots, and the next session to consider centrality will re-run the same check.

**6. Persist the PageRank check as a reproducible script, or record that it was not.**
The check was run inline via a heredoc because the cross-repo write hook correctly blocked
the scratchpad path, so **no script exists on disk**. The recorded project preference is
that experiments be reproducible scripts. **If skipped:** DEC-012 counter-evidence item 1
cites numbers that nobody can regenerate, which is exactly the failure the reproducibility
preference exists to prevent. Cheapest fix is a gated file under `scripts/`.

**7. Untriaged, carried from S55:** `test_cli_git_ref.py::test_old_ref_has_fewer_findings`
still fails and was confirmed pre-existing on clean HEAD. Not blocking anything, but it
has now been carried across three sessions and will keep appearing in every test summary
until it is triaged or marked expected-fail.

**8. Flagged, not actioned:** `dsm-docs/research/README.md` does not match the structure
`/dsm-research-add` assumes and omits every research file added since Epoch 2.

## Open branches

None. The STAA branch `staa/2026-07-30-s56-lessons` was merged via PR #15 and deleted
(local and remote). No Level 3 branches were opened this session; all work was done
directly on `session-57/2026-07-30`.
