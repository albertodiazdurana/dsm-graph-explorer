# Epoch 4 Blog Journal

## 2026-03-16 — Sprint 13: When Your Validator Can't Validate Itself

Sprint 13 started with a straightforward goal: test GE's resilience against the
DSM_0.2 modular split (BL-090). The split had already landed in DSM Central
(v1.3.61), so instead of simulating it, we tested against real data.

EXP-007 compared the pre-split single file (2,625 lines) against the post-split
five files (2,573 lines). No parser regression, which was the expected result.
But the unexpected finding was more interesting: GE detected zero sections in
DSM_0.2. A 2,625-line document with dozens of headings, and GE saw nothing.

The root cause: GE's parser only recognized numbered sections (`### 2.1 Title`).
DSM_0.2 uses plain markdown headings (`## Title`). The validator built to check
DSM's integrity couldn't parse DSM's own structure.

The fix was surprisingly small. The parser already extracted all headings
(numbered and unnumbered) into Section objects. The bottleneck was a single guard
in graph_builder.py: `if section.number:`. Removing that guard and adding a
title-based slug ID (`h:session-transcript-protocol`) was the entire change.

This is an interesting pattern: the tool's own methodology documents revealed a
fundamental limitation in the tool. Dog-fooding at its finest.

Also completed the BL-170 architecture audit requested by DSM Central. The audit
confirmed that GE operates entirely on local data (subprocess git + filesystem
reads), making it 100% compatible with Private Projects.

## 2026-03-17 — Sprint 14: Making the Graph Database Practical

Sprint 14 was a "carry-forward SHOULDs" sprint, three enhancements that make
the FalkorDB integration practical rather than just functional.

The biggest item was incremental graph updates. Until now, every `--graph-db`
run deleted the entire named graph and rewrote everything from scratch. For a
small DSM repository that's fine, but for larger codebases it's wasteful. The
new `update_files()` method takes a list of changed files, removes only their
nodes and edges, and re-inserts them from the fresh NetworkX graph. REFERENCES
edges are rebuilt entirely since they cross file boundaries, but that's cheap
compared to the node operations.

The design decision was file-level granularity rather than node-level diffing.
A file either changed or it didn't. This keeps the logic simple and matches how
the system works: files get parsed, parsed data becomes graph nodes. If a file
changed, all its nodes might have changed, so delete and reinsert. The CLI
detects staleness by comparing git refs: if the stored ref differs from the
current one, it triggers the incremental path.

The other two items were smaller: adding FalkorDB indexes on `Section.node_id`
and `Section.heading` (a follow-up to Sprint 13's heading-based sections), and
a `to_networkx()` roundtrip method that reads a FalkorDB graph back into
NetworkX format.

Also processed the DSM Central feedback audit, which mapped all 42 of GE's
backlog proposals to their processing status. A nice milestone: 33 out of 42
proposals have been implemented in DSM Central. The feedback loop works.
