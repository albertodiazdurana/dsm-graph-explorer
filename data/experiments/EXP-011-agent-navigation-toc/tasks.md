# EXP-011 Task Set + Answer Key

**Corpus:** GE's own `dsm-docs/` (116 files, 1650 sections, 67 cross-references)
**ToC snapshot:** frozen in `arm-inputs/toc-markdown.md` and `arm-inputs/toc-toon.toon`
(generated 2026-07-06 via `dsm-validate dsm-docs --knowledge-summary <out> --format {markdown,toon}`,
relative-path invocation). Token counts: markdown 2,903 / TOON 3,123 (`cl100k_base`).

The three arms differ ONLY in what the navigating agent receives in context:
- **A0 (control):** no ToC. Repo access only.
- **A1 (markdown ToC):** `arm-inputs/toc-markdown.md` pasted into context.
- **A2 (TOON ToC):** `arm-inputs/toc-toon.toon` pasted into context.

Each (arm × task) is run by a fresh, isolated subagent with no prior knowledge of this repo.
Answers must be derivable only by inspecting the repo's **current state** (rankings, counts,
section lists) — not from model general knowledge (contamination guard).

---

## Grading

- **success**: answer matches the key below (binary correct / incorrect; `partial` when one of two
  required parts is right).
- **tool_calls**: count of Read/Grep/Glob/Bash calls the subagent made to reach its answer
  (0 is valid and a win — the ToC already held the answer).
- **tokens_to_answer**: best-effort/approximate (per-subagent metering is weak); tool_calls is the
  primary cost metric. Flagged as a limit in `EXP-011.md` §4 Environment.

Answer key is **pre-registered** (written before any run) to prevent post-hoc rationalization.

---

## Category (a) — ToC-answerable (structural; ToC-arms should answer with few/zero tool calls)

### T1 — Most-referenced file
**Q:** Which file in the repository has the most incoming references, and how many does it have?
**Key:** `dsm-docs/blog/epoch-1/materials.md`, **52** incoming references.
**Notes:** Directly in both ToCs (Hub Documents, rank 1). A0 must reconstruct the reference graph
across 116 files — expensive or impractical; a strong ToC-advantage signal (or an A0 give-up/guess).

### T2 — Top cross-reference hotspot
**Q:** Which section is the single biggest cross-reference hotspot? Give the file, section, and count.
**Key:** `dsm-docs/blog/epoch-1/materials.md`, §3 **"Growth Through Feedback"**, **22** references.
**Notes:** In both ToCs (Cross-Reference Hotspots, row 1). Verified via `--graph-stats` (`[22x] Section 3`).

### T3 — Orphan-file count *(trap: tests F4 / H2)*
**Q:** How many orphan files (files with no incoming references) does the corpus have?
**Key:** **≈112** (markdown ToC lists 15 and says "... and 97 more" → 15 + 97 = 112).
**Notes:** A1 (markdown) can compute 112. A2 (TOON) renders `orphans[15]{file,sections}:` with **no
total field** (F4) → expected to answer **15**, undercounting by ~97. This is the sharpest single
test of whether the TOON schema's information loss harms the consuming agent.

---

## Category (b) — ToC-narrows-search (ToC points; agent may read for detail)

### T4 — Largest directory
**Q:** Which directory contains the most markdown files, and how many?
**Key:** `dsm-docs/checkpoints/done/`, **19** files.
**Notes:** In the ToC Document Hierarchy (`**dsm-docs/checkpoints/done/** (19 files, 148 sections)`).
A0 must `ls`/glob and compare directory counts.

### T5 — Intrinsic-ToC vision file
**Q:** Which research file documents the Intrinsic-ToC vision, and how many sections does it have?
**Key:** `dsm-docs/research/2026-04-13_intrinsic-toc-vision.md`, **32** sections.
**Notes:** ToC hierarchy lists the file + section count; agent may open it to confirm.

### T6 — decisions/ file count
**Q:** How many files are in the `decisions/` directory?
**Key:** **13** files.
**Accept also:** "11 DEC-* records" *with the reasoning that the 13 files include `README.md` and
`2026-04-02_s44_align-report.md`.* An answer of "13 DEC records" (over-trusting the ToC's file count
as a DEC count) is **incorrect** — a secondary trap on ToC over-trust.

---

## Category (c) — ToC-irrelevant control (ToC covers `dsm-docs/*.md` only; all arms must navigate)

### T7 — TOON emitter location
**Q:** Which source file implements the TOON emitter, and what function assembles the TOON summary?
**Key:** `src/analysis/knowledge_summary.py`, function `_generate_toon_summary`.
**Notes:** Outside the ToC's scope (`src/*.py` is not summarized). All three arms must grep `src/`.
Tests that the ToC neither helps nor misleads on out-of-scope questions.

### T8 — C3 gate threshold
**Q:** What token-savings threshold must the TOON migration meet (the "C3" validation gate), and which
decision record defines it?
**Key:** **≥10% measured token savings** (i.e. −10% tokens) on the Central corpus, defined in
**DEC-010** (`dsm-docs/decisions/DEC-010-toon-migration-format.md`).
**Notes:** Semantic content inside a `.md` file. The ToC does not even name DEC-010 (the decisions/
hierarchy shows only DEC-004/003/005 + "and 10 more"), so all arms must locate and read the file.

---

## Run log (filled during execution)

| Task | Arm | Answer given | success | tool_calls | tokens_to_answer (approx) | notes |
|------|-----|--------------|---------|------------|---------------------------|-------|
| _(populated by the run; rolled up per-arm into `results.md`)_ | | | | | | |
