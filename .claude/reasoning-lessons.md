# Reasoning Lessons

Per-session lessons extracted from session transcripts. Appended by
the wrap-up skill at each session end. See DSM_0.2 Module A Reasoning
Lessons Protocol for the extraction rules.

Categories: [pattern], [ecosystem], [infrastructure], [skill], [methodology]

## S47 (2026-04-13 / 2026-04-14)

- [auto] S47 [pattern]: Concept gate granularity matters. Passing the concept gate at the BL level does not cover module-level design decisions (thresholds, condensation rules, output budgets). When an artifact has parameters that affect output, those parameters are concept-gate material.
- [auto] S47 [pattern]: "Don't design for hypothetical future requirements" applies to implementation even when vision documents span future phases. Plans should have vision; code should target reachable deliverables. Distinguish vision (document) from architecture-enabling-future (don't implement without concrete need).
- [auto] S47 [pattern]: Boundary protocols (sprint, epoch) need automatic triggers, not just checklists. Verbal "substantially complete" is not procedural closure. Three related gaps surfaced in a single session: sprint trigger, checkbox reconciliation, epoch boundary absence.
- [auto] S47 [pattern]: Verification (reading) and documentation (writing) are asymmetric. After verifying items complete, explicit write-back is required to prevent stale state. Applies to sprint checklists, MEMORY.md stale claims, last-align.txt markers.
- [auto] S47 [ecosystem]: The agent IS the query engine. No MCP, no local LLM needed for the navigable-ToC pattern. Design outputs so Claude (or any LLM) can search patterns, extract values, follow links like a human reads a book's ToC. DEC-009 codifies this.
- [auto] S47 [pattern]: When uncertain whether to refactor for future flexibility, check: is the second use case concrete? If no, defer. The hierarchy-fix-only approach worked; the data/format split would have been speculative work.
- [auto] S47 [infrastructure]: Graph query functions should be separable from output formatters by necessity (future MCP/JSON), but only split when the second format is actually built. Today, returning markdown directly is acceptable.
- [auto] S47 [methodology]: Three-file atomic feedback (local methodology + local backlogs + brief Central notification) works. Central gets pointers, not duplicates; spokes keep the full record.
- [auto] S47 [pattern]: User-initiated protocol-gap discovery is valuable. Entries 59-63 all surfaced from "you didn't do X, why not?" challenges. The resulting proposals capture systemic gaps, not one-off mistakes.
- [STAA] S47 [ecosystem]: Scope-ownership check before artifact creation. When creating a backlog/plan file, ask "who originated the request?" (hub vs. spoke). Implementation location is not ownership location.
- [STAA] S47 [pattern]: Completion of the last deliverable of a named scope unit (sprint, epoch) is itself a gate, not just a session endpoint. Check scope-unit closure before suggesting session wrap-up.
- [STAA] S47 [pattern]: When vision expands mid-implementation, split the conceptual capture (vision doc) from the code change (minimal fix). Do not retrofit bounded deliverables to expanded vision.
- [STAA] S47 [pattern]: At session/sprint start, when a checklist has N independent unknowns, batch the read-only checks in one parallel tool call. Verified efficient in S47 Sprint 15 boundary check.
- [STAA] S47 [pattern]: A single "y" advances one gate. Four-gate PGB means each concept/implementation/run gate is independent; prior approval does not carry forward.
- [STAA] S47 [methodology]: Sessions that exercise multiple boundary/gate protocols tend to surface gaps in clusters (S47: 5 proposals). Reserve end-of-session time for consolidated feedback writing.