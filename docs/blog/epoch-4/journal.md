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
