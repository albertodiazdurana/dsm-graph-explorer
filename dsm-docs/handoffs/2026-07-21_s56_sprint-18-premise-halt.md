# Handoff: Sprint 18 premise halted pending direction decision

**Date:** 2026-07-21
**Session:** 56
**Author:** Alberto Diaz Durana (with AI assistance)
**Repository:** `dsm-graph-explorer`
**Branch at handoff:** `sprint-18/leiden-clustering` (off `session-56/2026-07-21`)
**Full record:** [`dsm-docs/research/2026-07-21_cluster-quality-graph-density.md`](../research/2026-07-21_cluster-quality-graph-density.md)

---

## Bottom line

**Do not resume coding Sprint 18 P2 from this branch.** The sprint's premise, that
Leiden community detection over the reference graph yields clusters corresponding
to recognizable project areas, was measured during S56 and does not hold as
written. P2 is halted mid-implementation by decision, not by an error.

The branch name is now misleading. It says `leiden-clustering`; the work it
carries is a dependency addition plus a research file that argues clustering may
not be the right instrument.

## What was done

1. **Sprint 18 P2 library decision resolved and implemented.** `leidenalg` +
   `igraph` added as a new `cluster` optional extra in `pyproject.toml`,
   installed and verified working. The S55 framing of that decision
   (`leidenalg` vs `networkx.community` as "true Leiden vs Louvain-family") was
   false in both directions: networkx 3.6 exposes `leiden_communities` but only
   as a backend dispatch stub that raises `NotImplementedError`, and `leidenalg`
   requires `igraph`, so it is two packages, both prebuilt abi3 wheels, 8.4 MB,
   no build toolchain.
2. **The graph was measured**, on GE and on DSM Central (the intended target
   corpus per the S49 GraphRAG study).
3. **A degree-preserving null-model test was run**, which is what halted the
   sprint.
4. **Three external research passes** (non-LLM edge construction; an adversarial
   case against clustering; coverage norms and orphan handling).
5. **Research file written**, 8 sections, 4,447 words, with sources and
   evidence-quality flags.

## The measurements that matter

| | GE | DSM Central |
|---|---|---|
| Nodes | 2,632 | 13,166 |
| CONTAINS / REFERENCES edges | 2,445 / **118** | 12,170 / **1,116** |
| Orphan sections | 99.1% | 99.0% |
| Files with any cross-reference | 42 of 187 (22.5%) | 264 of 996 (26.5%) |

Null-model test on Central's file-level graph, 50 replicates, degree sequence
preserved exactly:

- Real modularity **0.4331** vs null **0.4211 +/- 0.0045**, z = 2.68, 0/50 nulls
  reached real. Signal is present but the **excess is 2.8%**.
- Real NMI vs directories **0.1812** vs null **0.1881**. The metric used through
  most of the session as a quality signal is **null-indistinguishable and
  therefore invalid**.

## Decided vs merely leaning

**Decided:** the library (`leidenalg`, shipped in `pyproject.toml`); that
modularity and NMI-vs-directories are not valid gate metrics; that
drop-CONTAINS, weighted-CONTAINS and full-weight-CONTAINS are eliminated
(see research file §5, with the pre-registered falsification condition that
killed weighted CONTAINS).

**Leaning only, with no DEC and no plan edit:** option **D**, a three-arm
agent A/B in the shape of EXP-011 (ToC alone / ToC + clusters / ToC + centrality)
to settle empirically whether clusters help an agent navigate. Options A
(pivot to centrality), B (grow the graph first), and C (ship the connected core
with CPM, consensus and disclosure) remain open. Research file §7 has all four
with costs.

**Nothing in the research file authorizes work.** Per the Actionable Work Items
rule, only `dsm-docs/plans/` does, and no plan has been edited.

## Blocking items, in order

1. **Resolve the P4 gate ambiguity. This blocks any experiment design.**
   BL-302 Phase 2 §P4 says a cluster set that "cuts across obvious boundaries"
   fails the gate. Read as folder boundaries, the one surviving design fails on
   the property that recommended it; read as topical coherence, it passes. The
   two readings give opposite verdicts and cannot be resolved after seeing
   results without motivated reasoning.
2. **Edit the plan.** Sprint 18's plan and BL-302 Phase 2 still describe
   "compute clusters / emit clusters" as P2/P3. Under any of options A to D that
   description is wrong. Until edited, the actionable record contradicts the
   evidence.
3. **Design EXP-012 with pre-registration** if D is chosen: arms, tasks, ground
   truth written before running, and a gate that is not modularity. Both
   non-control arms are cheap to build (`nx.pagerank` and `nx.hits` are already
   available, no new dependency; the cluster arm exists from this session's
   work). Cost is in agent runs.

## Loose state

- `pyproject.toml`: `cluster` extra added. Committed this session; keep it
  regardless of direction, since option D's cluster arm needs it.
- Branch `sprint-18/leiden-clustering` carries no clustering implementation.
  Consider renaming or retiring it when the plan is edited.
- `src/semantic/similarity.py` (TF-IDF, Sprint 6) exists and is **not wired to
  the graph**. Relevant to option B; no new dependency needed.
- Pre-existing unrelated failure `test_cli_git_ref.py::test_old_ref_has_fewer_findings`
  remains untriaged, carried from S55.
- `dsm-docs/research/README.md` does not match the structure `/dsm-research-add`
  assumes (no numbered sub-tables) and is stale, omitting every research file
  added since Epoch 2. Not restructured; flagged as a separate decision.

## Open questions recorded but not measured

- Does the **weighted** file-level partition also fail the null? Only the
  unweighted graph was null-tested.
- What is the **regeneration churn**, i.e. how much does cluster membership drift
  across commits? Identified in the literature as the failure mode that would
  make a regenerated artifact unreviewable.
- Is Sprint 18 **sequenced correctly**? BL-GE-001 (Layer 4.5, Semantic Concept
  Layer, DEC-011 accepted) is scheduled for Epoch 6 and supplies exactly the
  edges the isolated majority of files lack. It already names BL-302 as a
  dependency.
