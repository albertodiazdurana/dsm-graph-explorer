# Cluster Quality and Graph Density for the Intrinsic-ToC

**Date:** 2026-07-21
**Linked BL:** [BL-302 Phase 2 (Leiden Clustering)](../plans/BL-302-phase-2-leiden-clustering.md)
**Author:** Alberto Diaz Durana (with AI assistance)
**Status:** Active
**Validation depth:** Multi-pass (per DSM_0.2 §10.1), three independent external
research agents, one internal prior-art pass, and a degree-preserving null-model
measurement run locally. Several load-bearing claims were arrived at independently
by more than one source; those convergences are marked in the findings.

---

## Purpose / Question

Sprint 18 (BL-302 Phase 2) plans to emit structural concept clusters into
`--knowledge-summary`, computed by Leiden community detection over the reference
graph. Session 56 set out to implement that and instead found the premise in
doubt: the reference graph is far sparser than the plan assumes, and the
clusters it yields are close to what a random graph with the same degree
sequence produces.

This file records what was measured, what the external literature and practice
say, and which design options survive, so that the direction decision, and any
future attempt to revisit it, rests on evidence rather than on the plausible
inferences that failed repeatedly during the session.

## What was measured

All figures below come from runs made during Session 56 on 2026-07-21. This
section records measurements only; interpretation is deferred to §3 to §5.

### Method

Graphs were produced by the shipped pipeline, not by a bespoke script:

```
dsm-validate <path> --graph-stats --graph-export <out.graphml>
```

Note for anyone reproducing this: `python src/cli.py <anything>` silently
produces no output and exits 0, including for `--help`. Only the installed
`dsm-validate` entry point works. This cost three probes to discover and is
recorded here rather than left as folklore.

Clustering used `leidenalg` 0.12.0 with `igraph` 1.0.0 and `networkx` 3.6.1,
partition type `ModularityVertexPartition`, seed 42. The partition type is
load-bearing: it is modularity, not CPM, which is what makes the resolution-limit
literature in §4 apply to this configuration specifically rather than generically.

Two corpora were measured. GE is this repository, the tool itself. DSM Central
is the intended target corpus, named as such in the S49 GraphRAG fit study.
Both runs had Sprint 18 P1 default exclusions active, so dependency directories
are already removed.

### Corpus composition

| | GE | DSM Central |
|---|---|---|
| Files scanned (excluded) | 187 (45) | 996 (131) |
| Nodes | 2,632 | 13,166 |
| of which FILE | 187 | 996 |
| of which SECTION | 2,445 | 12,170 |
| Edges | 2,563 | 13,286 |
| of which CONTAINS | 2,445 | 12,170 |
| of which REFERENCES | **118** | **1,116** |
| Orphan sections | 2,422 of 2,445 (99.1%) | 12,047 of 12,170 (99.0%) |
| REFERENCES per section | 4.8% | 9.2% |

The reference network is a small fraction of the graph in both corpora, and the
orphan rate is effectively identical at a 5x scale difference.

Restricted to REFERENCES edges and projected to undirected, GE yields 120 nodes
and 118 edges in 9 connected components, sized 88, 10, 7, 4, 3, 2, 2, 2, 2.

### CONTAINS weight sweep (GE)

Clustering the full graph with REFERENCES weighted 1.0 and CONTAINS weighted W.
NMI is measured against directory labels, so a high value means the partition
agrees with the folder tree.

| W | nodes | clusters | coverage | modularity | NMI vs directories |
|---|---|---|---|---|---|
| 0.0 | 120 | 15 | 4.3% | 0.7616 | 0.461 |
| 0.01 | 2,630 | 185 | 98.9% | 0.8119 | 0.767 |
| 0.05 | 2,630 | 179 | 98.9% | 0.8937 | 0.765 |
| 0.1 | 2,630 | 175 | 98.9% | 0.9239 | 0.762 |
| 0.25 | 2,630 | 177 | 98.9% | 0.9456 | 0.765 |
| 0.5 | 2,630 | 169 | 98.9% | 0.9547 | 0.755 |
| 1.0 | 2,630 | 167 | 98.9% | 0.9599 | 0.758 |

Coverage moves from 4.3% to 98.9% between W=0 and W=0.01 and does not move
again. NMI is flat across every nonzero weight, including W=0.01 where CONTAINS
is weighted 100x below REFERENCES.

### File-level projection

Sections collapsed into their parent file; an edge exists between two files when
any section-level reference links them.

| | GE | DSM Central |
|---|---|---|
| Files | 187 | 996 |
| File-file edges | 62 | 525 |
| Files with any cross-reference | 42 (22.5%) | 264 (26.5%) |
| Connected components | 146 | 733 |
| Clusters on the connected core | 5 | 9 |
| Cluster sizes | 16, 9, 9, 4, 4 | 54, 41, 39, 31, 29, 28, 21, 14, 7 |
| Modularity | 0.4434 | 0.4469 |
| NMI vs directories | 0.506 | 0.163 |
| Distinct partitions across 8 seeds | 5 | 8 |

Roughly a quarter of files carry any cross-reference in both corpora.

## The null-model test

### Why this test

Modularity is high in random graphs purely from degree fluctuations (Guimera,
Sales-Pardo and Amaral, *Phys. Rev. E* 70:025101(R), 2004), so a good modularity
score is not by itself evidence of topical structure. Peixoto's descriptive-vs-
inferential critique gives the operational litmus: would the output look equally
plausible if the graph carried no topical signal? Both external research agents
prescribed this test independently, from different briefs.

### Method

The Central file-level graph was rewired with `igraph.rewire` at 10x edge count,
which preserves the degree sequence exactly (verified: real degree sum 1,050,
null degree sum 1,050) while destroying any topical structure. Clustering was
then run identically on real and rewired graphs. 50 replicates for modularity,
10 for NMI.

**Scope limitation, stated because it matters.** The null test operates on the
simplified, unweighted graph, since degree-preserving rewiring is defined there.
The file-level figures in §2 come from the weighted graph (edge weight = count of
section-level references between two files). The two therefore cluster different
objects and their numbers differ: 9 clusters at modularity 0.4469 weighted, 10
clusters at 0.4331 unweighted. The real-vs-null comparison below is internally
like-for-like, both unweighted. What is **not** established is that the weighted
partition would also fail the null; that was not measured.

### Results

| | REAL | NULL (rewired) |
|---|---|---|
| Modularity | 0.4331 | 0.4211 +/- 0.0045 (n=50) |
| Clusters | 10 | 12.5 mean |
| Largest cluster sizes | 43, 33, 31, 31, 27, 26, 25, 21, 20 | 33, 32, 31, 30, 28, 27, 18, 18, 17 |
| NMI vs directories | 0.1812 | 0.1881 +/- 0.0069 (n=10) |

### Two findings

**1. The topical signal is real but small.** No null replicate reached the real
graph's modularity (0/50) and z = 2.68, so structure beyond the degree sequence
is present. But the excess is **2.8%**, and cluster count and size distribution
are not visibly distinguishable from the null. The honest statement is that the
partition is largely, though not entirely, explained by the degree sequence
alone. This is neither "the clusters are meaningless" nor "the clusters are
real"; it is a faint signal that a validation gate should be designed to detect
rather than assumed away.

**2. The quality metric used earlier in the session was invalid.** Low NMI
against directory labels was treated during Session 56 as evidence that
clustering had found something the folder tree does not encode, and Central's low
value was reported as the strongest result for the file-level design. The null
graph scores the same or higher (0.1881 vs 0.1812). Low NMI-vs-directories is
what any graph with this degree sequence produces; it measured the absence of
folder agreement, not the presence of topical structure. Any future evaluation
must compare against a null rather than against an absolute threshold.

### Seed stability

On the real graph across 10 seeds, modularity ranges 0.4266 to 0.4330 and
NMI 0.1645 to 0.1848, with pairwise partition NMI averaging 0.8612 (minimum
0.7705). Partitions are therefore similar but not identical between seeds, which
bears on regeneration churn discussed in §4.

## What the external evidence says

Gathered by three independent research agents briefed on separate questions.
Evidence-quality flags from those reports are preserved inline; full sources in
§8. Selection here is limited to findings that bear on the Sprint 18 decision.

### Practice: what comparable systems actually do

**Aider's repo map** is the closest shipped analogue, an index of a repository
built for an LLM agent to orient itself. It builds a graph of source files, ranks
with **personalized PageRank**, and emits a token-budgeted tree of the most
referenced identifiers. Aider had the same graph shape available and chose
centrality, not community detection. *(Moderate: practitioner, verifiable
artifact.)*

**Microsoft GraphRAG**, the flagship system running Leiden over documents, does
**not use explicit document cross-references at all**. It uses an LLM to derive
an entity knowledge graph from source text, then runs hierarchical Leiden over
that derived graph. The most prominent system doing what Sprint 18 proposes
concluded the explicit-link graph was not the substrate to cluster, and replaced
the substrate rather than tuning the algorithm. *(Strong: peer-reviewed,
arXiv:2404.16130, plus published dataflow docs.)*

**llms.txt**, the emerging convention for exposing documentation to agents, is a
hand-curated hierarchical index, not a clustered one. Its measured benefit is
itself thin: roughly 10% adoption, and reporting indicates most sites saw no
measurable change. *(Thin.)*

### Algorithmic criticisms that apply to this configuration

**The resolution limit is live here.** Modularity maximization cannot resolve
communities below a scale set by total graph size (Fortunato and Barthelemy,
*PNAS* 2007). On a 12,170-section graph, a genuinely distinct small topic will be
absorbed into a larger one. This applies because §2 records the partition type as
`ModularityVertexPartition`.

**Leiden does not fix the resolution limit.** Traag, Waltman and van Eck (2019)
fix a different defect, Louvain's arbitrarily badly connected communities.
Resolution-limit-freeness is a property of the quality function rather than the
optimizer, and CPM has it while modularity does not (Traag, Van Dooren and
Nesterov, 2011). The assumption that choosing Leiden had addressed this was held
during Session 56 and is false. *(Strong, peer-reviewed.)*

**Degeneracy.** Modularity typically admits an exponential number of distinct
high-scoring partitions that disagree substantially on module composition and
size distribution (Good, de Montjoye and Clauset, *Phys. Rev. E* 2010). Emitting
one partition therefore presents an arbitrary draw from a large set of
equally-scoring, mutually contradictory alternatives as though it were a finding.
*(Strong.)*

**Instability under perturbation** is documented (Peel et al., 2025), and the
existence of consensus and ensemble methods is itself an admission that a single
run is not reliable. This compounds the seed variation measured in §3: an
artifact regenerated per commit can reshuffle membership and cluster count from
small corpus changes, producing large diffs and defeating any durable reference
to a named cluster. *(Strong.)*

### Coverage norms

**No like-for-like benchmark exists.** The coverage agent searched specifically
for link-density or orphan-rate measurements in hand-authored technical or
internal documentation corpora and found none published. The claim that 26.5% is
anomalously low is therefore **not established**, and this file does not assert
it. *(Absent, and reported as a finding.)*

For orientation only, and not like-for-like: English Wikipedia has ~5% articles
with no incoming link and ~0.5% with no outgoing link, at average degree ~20.6,
sustained by an active de-orphaning program with a 20-year backlog. Web-graph
connectivity figures (27.7% largest SCC in 2000, 51.3% in 2014) are crawl-biased,
since unlinked pages are largely undiscoverable. A filesystem walk has no such
bias, so the measurement in §2 is the more honest one and is not comparable to
either. *(Strong for the figures, with the comparability caveat.)*

**Partial coverage is the shipping norm.** GitHub launched precise code
navigation supporting exactly one language, with search-based fallback, and has
stated it will never support most languages. Sourcegraph ships explicit precise
and search-based tiers. Neither publishes a coverage percentage; both disclose
via named tiers and rule-based limits. Disclosure measurably improves decision
quality while measurably lowering felt trust (CHI 2025). *(Strong.)*

**Isolated nodes are already singleton clusters** under Leiden, so "covers 25%"
is partly a reporting choice rather than an algorithmic outcome. OSLOM's
"homeless nodes" is the citable precedent for treating unassigned as a
first-class output class. Neither networkx nor igraph documents guidance here.

### Constructing edges without an LLM

**Bibliographic coupling and co-citation cannot help the isolated majority.**
Both are closed over the linked subgraph: a file with no outgoing references gets
no coupling edges either. They can densify the connected core, not extend it.
This eliminates the cheapest family of options. *(Strong.)*

**BM25 kNN is the literature-backed statistical route.** BM25 outperforms other
text-based relatedness measures for clustering (Waltman et al., 2020), and von
Luxburg (2007) names the kNN graph the explicit first choice, with k on the order
of log(n), so 7 to 10 for these corpora. Unlike cosine thresholding, a kNN graph
has a guaranteed density floor of n*k rather than an unpredictable edge count.
Threshold-based construction has no principled selection rule and inflates
clustering coefficients, meaning Leiden will find communities in thresholded
noise. Both are purely statistical, requiring no model downloads. *(Strong.)*

**Growing the graph before clustering is documented to work**: link-prediction
enhanced consensus clustering improved results by 7% on artificial networks and
17% on Facebook ego networks (Burgess, Adar and Cafarella, 2015). *(Strong.)*

### The decisive evidence gap

**No study exists on whether topical clusters help LLM agents navigate a document
repository.** Every usability study weighing against clustering measured humans
browsing an interface, and their transfer to an agent consumer is exactly what is
contested. The gap cuts in both directions and cannot be closed by further
literature search. *(Absent, and reported as a finding.)*

## Designs eliminated, and why

This section records what was ruled out and on what evidence. The eliminations
are more useful than the survivors: without them, a later session re-proposes
the same options and re-spends the same effort.

### Edge-composition designs

**Drop CONTAINS, cluster the REFERENCES network alone.** Proposed and approved
during Session 56 on the argument that CONTAINS is dense structural scaffolding
that would make clusters recover the folder tree. The argument about CONTAINS was
correct; what was never checked was what remains after removing it. Answer: 120
of 2,632 nodes, 4.6% coverage, fragmenting into 9 disconnected components. High
modularity (0.7616) is an artifact of partitioning a near-forest. **Eliminated on
coverage.**

**Weight CONTAINS low rather than dropping it.** Proposed as the corrected
design, on the reasoning that a small weight would retain coverage without
letting scaffolding dominate. A falsification condition was pre-registered before
measurement: if NMI against directory labels rose flatly with coverage rather
than showing a transition, no good weight exists and the family is dead. NMI came
back **flat at 0.755 to 0.767 across every nonzero weight**, including W=0.01
where CONTAINS is weighted 100x below REFERENCES, while coverage snapped from
4.3% to 98.9% between W=0 and W=0.01 and never moved again. Weighting is a
switch, not a dial. The sweep also produced 167 to 185 clusters at every weight,
unusable for a table of contents independent of the NMI result. **Eliminated by
its own pre-registered condition.** Any proposal to revisit weighted CONTAINS
should begin by re-reading the sweep in §2.

**CONTAINS at full weight.** Recovers the directory structure, which a file
listing already provides. **Eliminated as adding nothing over `ls`.**

### Coverage fixes

**Bibliographic coupling and co-citation.** Attractive because they manufacture
edges from existing link structure with no inference and no dependencies. But
both are closed over the linked subgraph: a file with no outgoing references
receives no coupling edges. They densify the connected core without extending it,
and the connected core is not where the problem is. **Eliminated as a coverage
fix**, though still available as a core-densification technique.

### Metrics

**NMI against directory labels, as a quality signal.** Used through most of
Session 56 as evidence that clustering found structure the folder tree does not
encode. A degree-preserving null scores the same or higher (§3). **Eliminated as
invalid.** It measured the absence of folder agreement, not the presence of
topical structure.

**Modularity, as a validation gate.** Across the weight sweep modularity rose
steadily from 0.8119 to 0.9599 while cluster meaning did not improve and NMI
stayed flat. It also cannot distinguish the real graph from a rewired one by more
than 2.8%. **Eliminated as a gate metric**, consistent with BL-302 Phase 2's own
instruction that a cluster set fails "regardless of modularity score".

### What survives, bounded

**File-level projection** is the only design not eliminated. It produces the most
interpretable clusters of the options tested and the lowest agreement with the
folder tree. It is bounded by two measured facts rather than endorsed: it covers
26.5% of files on the target corpus, and its partition exceeds a degree-preserving
null by only 2.8%. Surviving elimination is not selection; options are in §7.

### A note on how the eliminations happened

Both eliminated edge-composition designs were recommended by the AI assistant and
approved on that recommendation, and both failed the same way: the graph was
reasoned about rather than measured, and each time a single cheap measurement
reversed the conclusion. The measurements taken during the session held up; the
design inferences layered on them did not. A reader weighing the surviving option
should apply that base rate to it as well.

## The inherited premise defect

Sprint 18 exists because Session 49's GraphRAG fit study recommended adopting
GraphRAG's ideas without its machinery. The reasoning was sound on its own terms:
Leiden community detection is a structural technique compatible with DEC-009,
while GraphRAG's LLM entity extraction, LLM-authored community summaries, and
vector index are not. The study concluded "adopt ideas only" and noted Leiden was
already on the Sprint 18 roadmap.

What the separation missed is that the extraction was not packaging around the
clustering idea. It was **what produced a clusterable substrate**. GraphRAG does
not cluster documents by their cross-references; it derives an entity graph and
clusters that (§4). Removing the extraction and keeping the clustering leaves
Leiden running over a graph that was never the intended input, which is what §2
and §3 measured.

This is the second instance in this project of a forward-looking claim outliving
the context that made it true. Session 55 found BL-302 line 77 asserting that
Phase 2 required TOON-native nesting, a claim written before any TOON emitter
existed to check it against, which survived the abandonment of TOON and still
shaped Sprint 18. The recurring lesson is to re-check an inherited scope's
**premises**, not only its status.

A smaller instance of the same drift appeared within Session 56 itself: the S49
study named DSM Central as the target corpus, and most of the session's
measurement was done against GE, the tool's own repository, before the
discrepancy was noticed on re-reading the source.

## Options and open questions

Recorded as an option space, not a plan. Per the Actionable Work Items rule, only
items in `dsm-docs/plans/` are actionable; nothing here authorizes work.

### Options

**A. Pivot to centrality.** Emit hub and authority ranking instead of clusters,
following Aider's pattern. Cheapest of the four: `networkx` already ships
`pagerank` and `hits`, no new dependency, graph already built. The Intrinsic-ToC
vision's own connectivity vocabulary is hubs, orphans and hotspots, so this is
closer to the stated purpose than clustering is. Forecloses clustering for this
epoch.

**B. Grow the graph, then cluster.** Two sub-paths. A BM25 kNN similarity layer
(k on the order of log n) is statistical, DEC-009-compatible, and has a
guaranteed density floor; note §4's warning that thresholded similarity graphs
inflate clustering coefficients, so any such graph needs its own null test.
Author-declared concept edges via BL-GE-001 are DEC-009-compatible by
construction. Both are materially more work than A or C.

**C. Proceed on the connected core.** Ship clusters for the ~25% of files that
have cross-references, with CPM rather than modularity (resolution-limit-free),
consensus clustering for stability, unassigned files reported as an explicit
class rather than hidden, and coverage disclosed. §4 establishes that partial
coverage with disclosure is the shipping norm, so this is defensible; §3
establishes the signal being shipped is 2.8% over null.

**D. Settle it empirically.** A three-arm agent A/B in the shape of EXP-011: ToC
alone, ToC plus clusters, ToC plus centrality. This is the only option that
addresses the decisive evidence gap in §4 rather than arguing around it, and both
non-control arms are cheap to build. Cost is in agent runs. **Current lean as of
Session 56**, not yet recorded in a DEC or a plan edit.

### Open questions

1. **The P4 gate is ambiguous and must be resolved before any experiment runs.**
   BL-302 Phase 2 states that a cluster set which "cuts across obvious
   boundaries" fails. Read as folder boundaries, the surviving file-level design
   fails on the property that recommended it; read as topical coherence, it
   passes. The two readings give opposite verdicts and the ambiguity cannot be
   resolved after seeing results without motivated reasoning.
2. **Does DEC-009 need revisiting?** Its revisit clause requires a concrete
   problem statement, and the coverage measurement supplies one. But BL-GE-001's
   author-declared extraction policy is DEC-009-compatible by construction, and
   BM25 is purely statistical, so both paths in option B may sit inside the
   existing constraint. Revisiting may be unnecessary rather than blocked.
3. **Is Sprint 18 sequenced correctly?** BL-GE-001 (Layer 4.5, Semantic Concept
   Layer) is accepted via DEC-011 and scheduled for Epoch 6. Its `used-in` and
   `defined-in` edges are precisely the connectivity the isolated majority lacks,
   and BL-GE-001 already names BL-302 as a dependency. Sprint 18 in Epoch 5 may
   therefore depend on work planned an epoch later.
4. **Does the weighted partition also fail the null?** Not measured (§3).
5. **What is the regeneration churn?** Cluster membership drift across recent
   commits was not measured, and §4 identifies it as the failure mode that would
   make a regenerated artifact unreviewable.

## Sources

### Provenance and verification status

External sources were gathered by three research agents on 2026-07-21, briefed on
separate questions (non-LLM edge construction; an adversarial case against
clustering; coverage norms and orphan handling). Evidence-quality flags below are
carried from those reports.

Claims verified directly during Session 56, not taken on report: the null-model
results in §3, the graph statistics in §2, library versions and partition type,
`nx.pagerank` and `nx.hits` availability, `leidenalg` and `igraph` wheel
availability, and the `networkx` Leiden dispatch stub raising `NotImplementedError`
without a backend. Cited papers were **not** individually re-read; they are
reported at the confidence their gathering agent assigned.

### Internal (decisive, and easily overlooked)

- [Intrinsic-ToC Vision](2026-04-13_intrinsic-toc-vision.md), S47. Defines the
  artifact's purpose; its connectivity vocabulary is hubs, orphans, hotspots.
- [GraphRAG Fit Analysis](done/2026-04-23_graphrag-fit.md), S49. Source of the
  "adopt ideas only" decision and of the Central-as-target scoping (§6).
- [BL-GE-001 Semantic Concept Layer](../plans/BL-GE-001_semantic-concept-layer.md)
  and [DEC-011](../decisions/DEC-011-semantic-concept-layer-adoption.md). Layer
  4.5, author-declared extraction policy, Epoch 6 scheduling.
- [DEC-009 No Local LLM Dependencies](../decisions/DEC-009-no-local-llm-dependencies.md).
  The binding constraint, including its revisit clause.
- [BL-302 Phase 2](../plans/BL-302-phase-2-leiden-clustering.md) and the
  [Sprint 18 plan](../plans/epoch-5-sprint-18-plan.md). Scope under examination;
  source of the ambiguous P4 gate.
- [EXP-011](../../data/experiments/EXP-011-agent-navigation-toc/EXP-011.md).
  Precedent harness for an agent-navigation A/B (option D).
- `src/semantic/similarity.py`. Existing TF-IDF capability, not currently wired
  to the graph.

### Practice

- Aider repo map, https://aider.chat/docs/repomap.html *(Moderate)*
- Edge et al., *From Local to Global: A Graph RAG Approach*, arXiv:2404.16130,
  https://arxiv.org/abs/2404.16130 and https://microsoft.github.io/graphrag/index/default_dataflow/ *(Strong)*
- llms.txt convention, https://www.mintlify.com/blog/what-is-llms-txt *(Thin)*

### Community detection: limits and reliability

- Fortunato and Barthelemy, *Resolution limit in community detection*, PNAS 2007,
  https://www.pnas.org/doi/10.1073/pnas.0605965104 *(Strong)*
- Traag, Waltman and van Eck, *From Louvain to Leiden*, Sci. Rep. 9:5233, 2019,
  https://www.nature.com/articles/s41598-019-41695-z *(Strong)*
- Traag, Van Dooren and Nesterov, *Narrow scope for resolution-limit-free
  community detection*, Phys. Rev. E 84:016114, 2011,
  https://arxiv.org/abs/1104.3083 *(Strong; source of the CPM recommendation)*
- Good, de Montjoye and Clauset, *Performance of modularity maximization in
  practical contexts*, Phys. Rev. E 81:046106, 2010,
  https://arxiv.org/abs/0910.0165 *(Strong; degeneracy)*
- Guimera, Sales-Pardo and Amaral, *Modularity from fluctuations in random graphs*,
  Phys. Rev. E 70:025101(R), 2004, https://arxiv.org/pdf/cond-mat/0403660
  *(Strong; basis for the null test)*
- Peixoto, *Descriptive vs. Inferential Community Detection*, arXiv:2112.00183,
  https://arxiv.org/abs/2112.00183 *(Strong; the litmus test run in §3)*
- Lancichinetti and Fortunato, *Consensus clustering in complex networks*,
  Sci. Rep. 2:336, 2012, https://www.nature.com/articles/srep00336 *(Strong)*
- Peel et al., *Identifying robust features of community structure*,
  Phys. Rev. E 111:044303, 2025, https://arxiv.org/html/2409.12852 *(Strong)*
- Lancichinetti et al., *OSLOM*, PLOS ONE 2011,
  https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0018961
  *(Strong; "homeless nodes" precedent)*
- Fortunato and Hric, *Community detection in networks: A user guide*,
  Physics Reports 659, 2016, https://arxiv.org/pdf/1608.00163 *(Strong)*

### Coverage, connectivity and partial-coverage products

- *Orphan Articles: The Dark Matter of Wikipedia*, arXiv:2306.03940,
  https://arxiv.org/html/2306.03940v2 *(Strong)*
- Consonni, Laniado and Montresor, *WikiLinkGraphs*, ICWSM 2019,
  https://arxiv.org/abs/1902.04298 *(Strong)*
- Broder et al., *Graph structure in the Web*, WWW9 2000; Meusel et al., 2014,
  https://webdatacommons.org/hyperlinkgraph/2012-08/topology.html
  *(Strong for figures; crawl-bias caveat applies)*
- GitHub, precise code navigation launch and language-support position,
  https://github.blog/2022-04-29-bringing-code-navigation-to-communities/ *(Strong)*
- Sourcegraph code-navigation tiers,
  https://sourcegraph.com/docs/code-search/code-navigation/precise_code_navigation *(Strong)*
- Bo, Wan and Anderson, *To Rely or Not to Rely?*, CHI 2025,
  https://arxiv.org/abs/2412.15584 *(Strong; disclosure improves decisions,
  lowers felt trust)*
- Ge, Delgado-Battenfeld and Jannach, *Beyond accuracy: coverage and serendipity*,
  RecSys 2010, https://dl.acm.org/doi/abs/10.1145/1864708.1864761 *(Strong)*
- W3C, graceful degradation includes disclosure,
  https://www.w3.org/wiki/Graceful_degradation_versus_progressive_enhancement

### Edge construction without models

- von Luxburg, *A Tutorial on Spectral Clustering*, 2007,
  https://arxiv.org/abs/0711.0189 *(Strong; kNN as first choice, k ~ log n)*
- Waltman, Boyack, Colavizza and van Eck, *A principled methodology for comparing
  relatedness measures*, QSS 2020, https://arxiv.org/abs/1901.06815
  *(Strong; BM25 and bibliographic coupling)*
- Masuda et al., *Correlation networks: beyond thresholding*, Physics Reports 2025,
  https://arxiv.org/html/2311.09536v2 *(Strong; threshold sensitivity, inflated
  clustering coefficient)*
- Burgess, Adar and Cafarella, *Link-Prediction Enhanced Consensus Clustering*,
  arXiv:1506.01461, https://arxiv.org/abs/1506.01461 *(Strong; +7% / +17%)*
- Bolelli, Ertekin and Giles, *Clustering Scientific Literature Using Sparse
  Citation Graph Analysis*, PKDD 2006,
  https://clgiles.ist.psu.edu/papers/pkdd2006-clustering-literature.pdf
  *(Moderate; gathering agent flagged it doubtful at this edge count)*
- `sklearn.neighbors.kneighbors_graph`,
  https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.kneighbors_graph.html

### Consulted and deliberately not used

Listed so a later reader knows these were weighed rather than missed.

- Hearst, *Clustering versus faceted categories* (CACM 2006) and the
  Pirolli 1996 / Pratt 1999 / Rodden 2001 studies. All measured humans browsing
  an interface; their transfer to an agent consumer is precisely what is
  contested, so leaning on them would beg the question.
- Clusty / Vivisimo commercial history. Market narrative, not controlled
  evidence.
- Serrano et al., disparity filter backbone (PNAS 2009); Amsler networks;
  extended direct citation. Relevant only after a decision to construct edges.
- Reporting that grep outperformed embeddings in coding agents, and two 2026
  preprints on agentic search. Gathering agent flagged all three as unverified.

### Explicit gaps, reported as findings

- **No published link-density or orphan-rate measurement exists for hand-authored
  technical or internal documentation corpora.** Searched for specifically. The
  26.5% connected fraction in §2 therefore has no like-for-like benchmark, and
  this file does not claim it is anomalous.
- **No study exists on whether topical clusters help LLM agents navigate a
  document repository.** This gap is why §7 option D is an experiment rather than
  a literature question.
