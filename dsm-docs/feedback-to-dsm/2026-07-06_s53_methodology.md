# Session 53 Methodology Feedback (STAA-surfaced)

**Date:** 2026-07-06
**Project:** DSM Graph Explorer
**Session:** 53 (finding surfaced during `/dsm-staa` Step 8, S52+S53 analysis)

---

## Entry 64: §8.1 canonical mirror transform drops the first session heading on flat-structured spoke files

**Section:** DSM_0.2.A §8.1 (Canonical regeneration transform, BL-447)
**Score:** 7/10 (transform works and preserves all content, but produces wrap-up-vs-STAA output drift, the exact class BL-447 set out to eliminate)
**Context:** `/dsm-staa` Step 8 mirror regeneration for this spoke, whose `reasoning-lessons.md` uses `## S{N}` session headings and no `### ` category headings.

### Observation

Running the canonical §8.1 awk verbatim on this spoke's live file drops the first `## S47` session heading from the compact mirror. The mirror body opens directly with S47's entries (un-sectioned), and the first heading it shows is `## S48`. Every subsequent `## S{N}` heading survives; only the first is lost.

The mirror produced by the S53 `/dsm-wrap-up` (regenerated 2026-07-06T02:03) retained `## S47`. So the wrap-up's output and a faithful run of the §8.1 awk diverge on the leading heading, two regenerators producing two shapes from the same source. That divergence is precisely what BL-447's "single source of truth" rule was written to prevent.

### Root cause

The transform is shape-tolerant by starting emission at the first `### ` category heading or the first `[auto]`/`[STAA]` entry line, dropping everything before (`!found { next }`). On a flat-structured spoke (session `## S{N}` headings, no `### ` category headings), the first content line is an entry, and the `## S47` heading sits above it, so it falls in the drop region. Headings after the first entry pass through via the final `{ print }`, which is why only the first is lost. The `## Categories`-tolerance was designed for category-structured files; the session-heading-structured case was not covered.

Impact is cosmetic (no lesson content lost; both sanity checks pass), but the shape-drift is real and recurring: it will silently differ every time a wrap-up and a STAA regenerate the same flat file.

### Proposal #57: Teach the §8.1 transform to preserve session headings

Add a session-heading match rule to the canonical awk, before the `!found` drop:

```awk
/^## S[0-9]+ / { found=1; print; next }
```

This makes the transform start emitting at the first `## S{N}` heading (as it already does for `### ` category headings and entry lines), preserving the first session heading and eliminating the wrap-up-vs-STAA shape drift on flat files. Content behavior is otherwise unchanged; the entry-count and size-floor sanity checks are unaffected. Because §8.1 is the single source of truth, the one-line addition propagates to both `/dsm-wrap-up` Step 0 and `/dsm-staa` Step 8 automatically.

Verification done this session: ran the canonical awk to a temp file and observed `## S47` dropped; confirmed the live mirror (from S53 wrap-up) still contains it. The proposed one-line fix is reasoned but not yet test-run across all spoke shapes; at adoption, confirm it does not over-capture on category-structured files (it will not: `## S[0-9]+ ` cannot match a `## Categories` header).

### Numbering caveat

Set as Entry 64 / Proposal 57 per MEMORY's "continue from 64 / 57". If S52's wrap-up already consumed 64/57 (its feedback files are not in `done/` to cross-check), bump both at push time.
