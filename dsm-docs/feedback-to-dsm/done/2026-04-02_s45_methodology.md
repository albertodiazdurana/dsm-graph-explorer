# Session 45 Methodology Feedback

**Date:** 2026-04-02
**Session:** 45
**Sprint:** 15 (Protocol Usage Analysis)

---

## Entry 56: Procedural vs Behavioral Protocol Measurement Gap

**Context:** EXP-009 validated a four-layer protocol usage analysis (declared,
prescribed, observed, designed) against 7 ground truth sections identified by
DSM Central as universally required. The result was 4/7 (57%), below the 60%
threshold.

**Finding:** The 4 passing sections are all procedural protocols (Session
Transcript, Pre-Generation Brief, Branching Strategy, Ecosystem Path Registry).
They prescribe named, observable actions. The 3 failing sections are all
behavioral protocols (Read-Only Access, Inclusive Language, Active Suggestion).
They prescribe qualities of behavior whose compliance is implicit.

Reference-counting measures protocol salience (how often a protocol is
explicitly named), not protocol compliance (whether the agent behaves according
to it). These are different questions, and the distinction matters for BL-090:
behavioral protocols should always-load regardless of reference frequency,
because their effect is invisible to the agent when absent.

**Implication for DSM:** The ground truth set for protocol usage validation
should distinguish procedural from behavioral protocols. Behavioral protocols
require a different measurement approach (content audit, runtime instrumentation)
rather than reference counting.

## Entry 57: Ground Truth ID Stability in Evolving Documents

**Context:** EXP-009's ground truth IDs were hardcoded as bare slugs
(`session-transcript-protocol`), but the section index generates IDs with
section number prefixes (`7-session-transcript-protocol`). When DSM_0.2 sections
are renumbered, hardcoded IDs break.

**Finding:** Ground truth validation should use suffix matching or canonical
names rather than exact IDs that embed positional information. This is a general
principle: any experiment that validates against evolving documents needs
ID-matching resilience.

**Implication for DSM:** Experiment protocols in Appendix C.1 could recommend
that ground truth identifiers use stable names (protocol titles, not section
numbers) when referencing evolving documents.