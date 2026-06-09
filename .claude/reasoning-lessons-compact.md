# Reasoning Lessons (compact mirror)

<!-- Do not edit; auto-generated from .claude/reasoning-lessons.md by /dsm-wrap-up Step 0 or /dsm-staa Step 8 -->

**Source:** `.claude/reasoning-lessons.md`
**Last regenerated:** 2026-06-09T13:32+02:00
**Source mtime at regeneration:** 2026-06-09T13:29+02:00

---

- Concept gate granularity matters. Passing the concept gate at the BL level does not cover module-level design decisions (thresholds, condensation rules, output budgets). When an artifact has parameters that affect output, those parameters are concept-gate material.
- "Don't design for hypothetical future requirements" applies to implementation even when vision documents span future phases. Plans should have vision; code should target reachable deliverables. Distinguish vision (document) from architecture-enabling-future (don't implement without concrete need).
- Boundary protocols (sprint, epoch) need automatic triggers, not just checklists. Verbal "substantially complete" is not procedural closure. Three related gaps surfaced in a single session: sprint trigger, checkbox reconciliation, epoch boundary absence.
- Verification (reading) and documentation (writing) are asymmetric. After verifying items complete, explicit write-back is required to prevent stale state. Applies to sprint checklists, MEMORY.md stale claims, last-align.txt markers.
- The agent IS the query engine. No MCP, no local LLM needed for the navigable-ToC pattern. Design outputs so Claude (or any LLM) can search patterns, extract values, follow links like a human reads a book's ToC. DEC-009 codifies this.
- When uncertain whether to refactor for future flexibility, check: is the second use case concrete? If no, defer. The hierarchy-fix-only approach worked; the data/format split would have been speculative work.
- Graph query functions should be separable from output formatters by necessity (future MCP/JSON), but only split when the second format is actually built. Today, returning markdown directly is acceptable.
- Three-file atomic feedback (local methodology + local backlogs + brief Central notification) works. Central gets pointers, not duplicates; spokes keep the full record.
- User-initiated protocol-gap discovery is valuable. Entries 59-63 all surfaced from "you didn't do X, why not?" challenges. The resulting proposals capture systemic gaps, not one-off mistakes.
- Scope-ownership check before artifact creation. When creating a backlog/plan file, ask "who originated the request?" (hub vs. spoke). Implementation location is not ownership location.
- Completion of the last deliverable of a named scope unit (sprint, epoch) is itself a gate, not just a session endpoint. Check scope-unit closure before suggesting session wrap-up.
- When vision expands mid-implementation, split the conceptual capture (vision doc) from the code change (minimal fix). Do not retrofit bounded deliverables to expanded vision.
- At session/sprint start, when a checklist has N independent unknowns, batch the read-only checks in one parallel tool call. Verified efficient in S47 Sprint 15 boundary check.
- A single "y" advances one gate. Four-gate PGB means each concept/implementation/run gate is independent; prior approval does not carry forward.
- Sessions that exercise multiple boundary/gate protocols tend to surface gaps in clusters (S47: 5 proposals). Reserve end-of-session time for consolidated feedback writing.
- Scale-test output-size designs before coding. A 3-file TDD fixture passed 22 tests, but generate_hierarchy (list-all-files-and-sections) would emit ~4,700 lines on the real 4,703-node DSM Central target; the toy fixture certified an unbounded-output bug as healthy. When output size is itself a design parameter, include a scale-representative case or compute projected size for the real target before implementing, so unbounded designs fail at design time, not after green tests.

## S48 (2026-04-20)

- User direct instruction beats mode default. When user requests collaboration gates mid-Auto-mode, gates win; "minimize interruptions" is the default, not the override.
- /dsm-align across a major DSM version jump (v1.4.17 → v1.6.0) must re-chmod +x hooks regardless of byte-diff result. Hooks present but mode 644 = silent S180 failure; chmod is idempotent, apply unconditionally.
- Counter-evidence table (per BL-385 §8.2.1) works well paired with rebuttals in a single row. Six counter-claims weighed vs. rebuttals on the TOON decision kept the Gate 2 presentation auditable without sprawl.
- "Phase 1.5" BL naming signals prep-step sequencing between Phase 1 and Phase 2 without ambiguating Phase 2's scope. Useful when a format/infrastructure migration gates the next planned phase.
- Earn-the-assertion before writing a DEC. Reading Central's 364-line research file before writing DEC-010 surfaced methodology caveats (tokenizer proxy uncertainty, author-authored benchmarks, ±3% projection margin) that shaped counter-evidence. Accepting the headline claim on faith would have lost this nuance.
- Dedicated small sprint beats mixed sprint when boundary clarity matters. Sprint 17 = TOON migration alone (1-1.5 sessions) preserves DEC-010 C3 validation gate as a clean boundary. Sprint size is not the sole criterion; boundary clarity is.
- Pre-existing uncommitted files in session baseline get enumerated with origin trace in commit scope, not silently included. Honest commit messaging exposes the STAA content as "previously uncommitted" rather than hiding its provenance.
- "proceed" is not a protocol waiver. The agent rationalized a bare "proceed" at session start into skipping the collaboration gates and was interrupted ("also stop for the collaboration gates"). "proceed" authorizes the next step under the active protocol; when no gate has yet been established this session, default to presenting Gate 1, not to momentum.
- Decide-vs-implement reframe. For a large recommendation (TOON migration, ~1 session of code), the correct session output was a decision artifact (DEC-010 + scoped BL), not code. When a request could be read as "do the work," first check whether the right output is a decision + scoped BL; separate deciding from implementing.
- Protocol corrections are session-scoped, not turn-scoped. After the gate correction on Item 1, Items 2-3 ran a clean Gate1-2-3 rhythm with no re-prompting. Propagate a mid-session protocol correction to all remaining work units without waiting to be told again.
- Counter-evidence generates guardrails, not just verdicts. Engaging the 6 TOON counter-claims (all rebutted, net "does not defeat the case") produced conditions C1-C4; the scale counter-claim directly yielded the C3 validation gate. Treat counter-evidence as a source of conditions/mitigations, not a yes/no check.
- Close the STAA loop in one pass. S47's STAA output sat uncommitted ~6 days and its MEMORY "pending" marker was never cleared, so completed analysis read as undone. A STAA run must commit its reasoning-lessons appends and clear the MEMORY "STAA pending" marker in the same pass.
- Map config tier to cognitive load and flag switch points proactively. The agent recommended Standard for mechanical cleanup and Deep for novel decision work; the user explicitly valued proactive switch signals ("Inform me when I should switch"). Tie config recommendations to the cognitive load of upcoming work.
## S49 (2026-04-23 / resumed 2026-06-09)

- Resuming an unwrapped session: branch number > MEMORY "latest session" number signals an incomplete prior wrap-up. DSM session numbering is branch+MEMORY-based, not wall-clock, so a ~6-week gap between conversations still continues the SAME session N (here S49), not a new one.
- Mark resumption gaps explicitly in the transcript. When /dsm-go Steps 5.5/6 (archive+reset) are deliberately skipped to preserve in-flight gate context, the transcript spans the gap with mixed dates/models (opus-4-7 April → opus-4-8 June); an explicit boundary marker prevents it being misread as continuous.
- The session transcript is append-only by hook enforcement (validate-transcript-edit.sh). Mid-file insertion is blocked (do-not-edit-history); a boundary/resumption marker must be appended at the current end referencing where the gap occurred, never retroactively inserted at the gap line.
- Bash-heredoc append is the correct fallback for the transcript when the file ends in non-unique lines (e.g., two identical "====" marker rules) that break the Edit tool's anchor-uniqueness requirement while still satisfying the append-only hook.
- /dsm-align drift is real across multi-version gaps. After v1.6.0 → v1.14.0 (8 minor versions) the §17.1 reinforcement block had 4 substantive deltas (replace_all guard, chunked-drafting bullet, dated inbox-archive rule, space-comma punctuation); per-delta targeted edits beat a full-block rewrite for auditability.
- Anchor an artifact's Date Created to its origin session, not its physical write date. BL-GE-001 used 2026-04-23 (S49 origin) though written 2026-06-09, honoring provenance and keeping the S49 record coherent.
- Two-track local BL numbering (BL-GE-{NNN}) prevents collision with DSM Central's BL registry; Central-imported BLs (BL-302) keep their IDs, local-origin BLs get the GE prefix from 001.
