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

## S48 (2026-04-20)

- [auto] S48 [pattern]: User direct instruction beats mode default. When user requests collaboration gates mid-Auto-mode, gates win; "minimize interruptions" is the default, not the override.
- [auto] S48 [infrastructure]: /dsm-align across a major DSM version jump (v1.4.17 → v1.6.0) must re-chmod +x hooks regardless of byte-diff result. Hooks present but mode 644 = silent S180 failure; chmod is idempotent, apply unconditionally.
- [auto] S48 [methodology]: Counter-evidence table (per BL-385 §8.2.1) works well paired with rebuttals in a single row. Six counter-claims weighed vs. rebuttals on the TOON decision kept the Gate 2 presentation auditable without sprawl.
- [auto] S48 [pattern]: "Phase 1.5" BL naming signals prep-step sequencing between Phase 1 and Phase 2 without ambiguating Phase 2's scope. Useful when a format/infrastructure migration gates the next planned phase.
- [auto] S48 [methodology]: Earn-the-assertion before writing a DEC. Reading Central's 364-line research file before writing DEC-010 surfaced methodology caveats (tokenizer proxy uncertainty, author-authored benchmarks, ±3% projection margin) that shaped counter-evidence. Accepting the headline claim on faith would have lost this nuance.
- [auto] S48 [pattern]: Dedicated small sprint beats mixed sprint when boundary clarity matters. Sprint 17 = TOON migration alone (1-1.5 sessions) preserves DEC-010 C3 validation gate as a clean boundary. Sprint size is not the sole criterion; boundary clarity is.
- [auto] S48 [infrastructure]: Pre-existing uncommitted files in session baseline get enumerated with origin trace in commit scope, not silently included. Honest commit messaging exposes the STAA content as "previously uncommitted" rather than hiding its provenance.