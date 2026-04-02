# EXP-009 Stage A: Protocol Usage Validation Results

**Date:** 2026-04-02
**Session:** 45
**DSM_0.2 version:** v1.4.1
**Spoke:** dsm-graph-explorer

---

## 1. Experiment Setup

### Inputs

| Layer | Source | Count |
|-------|--------|-------|
| Section index (Designed) | DSM_0.2 core + modules A-D (v1.4.1) | 177 sections, 42 dispatch entries |
| Layer 1 (Declared) | `.claude/CLAUDE.md` | 6 references |
| Layer 2 (Prescribed) | 17 skill definition files (`~/.claude/commands/dsm-*.md`) | 82 references |
| Layer 3 (Observed) | 18 session transcripts (Sessions 26-44) | 137 references across 19 sessions |

### Success Criteria (from DSM Central Session 141)

- **Ground truth recall:** 7 universally-required sections must be classified as high-usage
- **Threshold:** ≥60% recall (≥5 of 7 sections pass)
- **Classification rule:** high-usage = referenced by ≥2 layers

## 2. Results Summary

| Metric | Value |
|--------|-------|
| Total sections indexed | 177 |
| High-usage sections | 18 (10.2%) |
| Low-usage sections | 159 (89.8%) |
| Designed-vs-observed gaps | 65 |
| Under-classified (on-demand but high) | 9 |
| Over-loaded (always-load but low) | 56 |

## 3. Ground Truth Validation

### 3.1 Reported Result: 0/7 FAIL

The automated validation reports all 7 ground truth sections as "fail":

```
session-transcript-protocol        → fail
pre-generation-brief-protocol      → fail
three-level-branching-strategy     → fail
read-only-access-within-repository → fail
ecosystem-path-registry            → fail
inclusive-language                  → fail
active-suggestion-protocol         → fail
```

### 3.2 Root Cause: ID Matching Bug

The ground truth IDs hardcoded in `cli.py` (line 682-690) use bare slugs
(e.g., `session-transcript-protocol`), but `section_index.py` generates IDs
with section number prefixes (e.g., `7-session-transcript-protocol`). The
validation lookup performs exact string matching, finds no match, and reports
"fail" for every entry.

This is an instrumentation bug, not an experiment result. The four-layer
pipeline ran correctly, the classification logic produced valid scores, but
the final validation step compared against IDs that don't exist in the index.

**Evidence:** Manual ID lookup confirms the sections exist with different IDs:

| Ground Truth ID | Actual Section ID | Score | Inferred |
|---|---|---|---|
| `session-transcript-protocol` | `7-session-transcript-protocol` | 16 | high |
| `pre-generation-brief-protocol` | `8-pre-generation-brief-protocol` | 5 | high |
| `three-level-branching-strategy` | `20-three-level-branching-strategy` | 5 | high |
| `read-only-access-within-repository` | `5-read-only-access-within-repository` | 0 | low |
| `ecosystem-path-registry` | `18-ecosystem-path-registry` | 11 | high |
| `inclusive-language` | `13-inclusive-language` | 1 | low |
| `active-suggestion-protocol` | `16-active-suggestion-protocol` | 0 | low |

### 3.3 Corrected Result: 4/7 (57%)

With manual ID correction, 4 of 7 ground truth sections classify as high-usage:

| Section | D | P | O | Score | Classification | GT Pass? |
|---|---|---|---|---|---|---|
| Session Transcript Protocol | 1 | 8 | 7 | 16 | high | Yes |
| Ecosystem Path Registry | 0 | 8 | 3 | 11 | high | Yes |
| Pre-Generation Brief Protocol | 1 | 0 | 4 | 5 | high | Yes |
| Three-Level Branching Strategy | 0 | 0 | 5 | 5 | high | Yes |
| Inclusive Language | 0 | 0 | 1 | 1 | low | No |
| Read-Only Access | 0 | 0 | 0 | 0 | low | No |
| Active Suggestion Protocol | 0 | 0 | 0 | 0 | low | No |

**57% ground truth recall, below the ≥60% threshold.**

## 4. Gap Analysis Highlights

### 4.1 Under-Classified (on-demand but high usage, 9 sections)

These sections live in modules (classified as on-demand by the dispatch table)
but are heavily used in practice. They are candidates for reclassification to
always-load:

| Section | Module | Score | Observation |
|---|---|---|---|
| Reasoning Lessons | A | 24 | Referenced in 19 prescribed + 5 observed |
| 17. Project Type Detection | A | 7 | Used at every session start |
| 19. Session-Start Inbox Check | A | 5 | Used at every session start |
| Project Inbox | A | 5 | Related to inbox check |
| {filename} (naming convention) | B | 7 | Referenced in artifact creation skills |
| Contents (4 module TOCs) | A-D | 4-5 each | Navigation artifact |

### 4.2 Over-Loaded (always-load but low usage, 56 sections)

These sections are in the core file (classified as always-load) but are rarely
or never referenced. The high count (56 out of ~80 core sections) suggests that
the core file contains many sections that could be moved to modules without
impacting agent effectiveness. This is the primary actionable signal for BL-090.

Notable over-loaded sections:
- Sub-sections of Heading Parsability (14.1-14.6): detailed rules rarely referenced by name
- CLAUDE.md template sub-sections (17.1-17.2): referenced as a whole, not by sub-section
- Branching strategy sub-sections (20.1-20.6): referenced as "Three-Level Branching", not by level
- Experiment Execution Protocol (§9): used but not referenced by section name in transcripts

### 4.3 Top Scoring Sections

| Section | Module | D | P | O | Score |
|---|---|---|---|---|---|
| 24. References | core | 0 | 7 | 84 | 91 |
| Reasoning Lessons | A | 0 | 19 | 5 | 24 |
| 7. Session Transcript Protocol | core | 1 | 8 | 7 | 16 |
| 18. Ecosystem Path Registry | core | 0 | 8 | 3 | 11 |

**Note:** "24. References" scores 91 primarily from 84 observed mentions. This
is likely a false positive: the word "References" appears frequently in
transcripts in contexts unrelated to DSM_0.2 §24. Stage B should validate this.

## 5. Analysis: Why 3 Ground Truth Sections Fail

The 3 failing ground truth sections each have a distinct failure mode. Understanding
these modes is necessary before deciding whether to adjust the extraction heuristics
or accept the result.

### 5.1 Read-Only Access (Score: 0)

**No references in any layer.** This protocol instructs agents not to modify files
in external repositories during cross-repo analysis. GE does perform cross-repo
analysis (`--compare-repo`, `--drift-report`), but the Read-Only Access protocol
is a constraint, not an action. Agents follow it implicitly (by using read-only
file operations) without naming it. The protocol is also not reinforced in GE's
CLAUDE.md and does not appear in any skill definition by name.

**Hypothesis:** This is a true negative for GE's declared and prescribed layers
(the protocol is not explicitly referenced) and a possible false negative for the
observed layer (agents may follow the constraint without mentioning it by name).

### 5.2 Inclusive Language (Score: 1)

**One prescribed reference, zero declared and observed.** Inclusive Language is a
passive writing standard ("avoid biased or exclusionary terms"). Unlike procedural
protocols (Session Transcript, Branching Strategy), it does not generate observable
actions. An agent following it produces text that complies, but the transcript
would not contain "I am now applying Inclusive Language" because compliance is the
absence of violations, not the presence of actions.

**Hypothesis:** This is a protocol whose usage is invisible to reference-based
extraction. It is genuinely universal (DSM Central is correct that all spokes
should follow it), but measuring compliance requires content analysis, not
reference counting.

### 5.3 Active Suggestion Protocol (Score: 0)

**No references in any layer.** This protocol instructs agents to proactively
suggest improvements. GE's CLAUDE.md does not reinforce it, no skill definition
references it by name, and transcripts do not contain the phrase. However, agents
in GE sessions do make suggestions (proposing backlog items, recommending
experiments, offering alternatives). The behavior exists but the label does not
appear.

**Hypothesis:** Similar to Inclusive Language, this is a behavioral protocol
whose compliance is observable in action but not in name references. The agent
suggests improvements because it is trained to be helpful, and the DSM protocol
formalizes this behavior, but neither the agent nor the skill definitions cite
it.

### 5.4 Pattern: Procedural vs Behavioral Protocols

The 4 passing sections are all **procedural protocols**: they prescribe specific,
named actions (write a transcript, create a branch, build a section index, check
the brief). These generate observable references because agents must invoke them
by name or follow explicit steps that mention the protocol.

The 3 failing sections are all **behavioral protocols**: they prescribe qualities
of behavior (be inclusive, suggest improvements, don't modify external files).
Compliance is implicit. A reference-counting methodology cannot distinguish
between "the agent is following Read-Only Access" and "the agent happens to only
read files."

This is a fundamental limitation of the extraction approach, not a bug. Reference
counting measures protocol salience (how often the protocol is explicitly
invoked), not protocol compliance (whether the agent behaves according to it).

## 6. Recommended Actions

### Action 1: Fix the Ground Truth ID Matching Bug

**What:** Update the `ground_truth` list in `cli.py` (line 682-690) to use the
actual section IDs generated by `section_index.py`, or change the validation
lookup to use substring/suffix matching instead of exact matching.

**Why this is the right fix (and alternatives considered):**

The bug is in the validation instrumentation, not in the pipeline. Fixing it is
necessary before EXP-009 can produce a valid ground truth score. Without this
fix, re-running the experiment against different spokes or DSM versions will
always report 0/7, making the validation meaningless.

- **Alternative A: Change `section_index.py` to omit number prefixes from IDs.**
  Rejected. Number prefixes disambiguate sections with identical headings across
  modules (e.g., "Contents" appears in all 4 modules). Removing them would break
  uniqueness.

- **Alternative B: Add number prefixes to the hardcoded GT list.** Quick fix, but
  brittle: if DSM_0.2 renumbers sections, the GT list breaks again. Better to make
  the lookup robust.

- **Alternative C: Substring matching in the validation lookup.** The GT ID
  `session-transcript-protocol` is a suffix of the actual ID
  `7-session-transcript-protocol`. A suffix match would find the correct section
  regardless of numbering changes. This is the most resilient approach.

**Recommended: Alternative C** (suffix matching), with a fallback to exact match
for IDs that are already complete.

### Action 2: Stage B Validation Focused on the 3 Failing GT Sections

**What:** Manually review transcript excerpts for the 3 failing ground truth
sections (Read-Only Access, Inclusive Language, Active Suggestion Protocol) to
determine whether they are true negatives or false negatives.

**Why this is the right next step (and alternatives considered):**

The corrected ground truth score is 57% (4/7), just below the 60% threshold.
The experiment cannot conclude until we understand whether the 3 failures reflect
a real extraction gap or a legitimate limitation of reference-based measurement.

- **Alternative A: Lower the threshold from 60% to 50%.** Rejected. The threshold
  was set by DSM Central with explicit reasoning: with only ~5 active spokes, a
  lower threshold would be too permissive. Changing the threshold to fit the
  result would undermine the experiment's integrity.

- **Alternative B: Add more transcripts.** We already used all 18 available
  transcripts (19 sessions). Coverage is not the issue; the 3 failing sections
  have zero or near-zero mentions across the entire corpus.

- **Alternative C: Change the classification heuristic (≥2 layers → ≥1 layer).**
  This would reclassify sections with a single prescribed or observed reference
  as high-usage. It would promote Inclusive Language (1 prescribed ref) to high,
  bringing the score to 5/7 (71%, passing). However, it would also promote dozens
  of other single-reference sections, inflating the high-usage count and
  diluting the signal for BL-090. The heuristic should reflect genuine usage
  patterns, not be tuned to pass a specific validation set.

- **Alternative D: Accept the result as FAIL.** Premature. The experiment's
  Stage B is specifically designed to investigate this scenario. The 57% score
  is close enough to the threshold that the distinction between "extraction gap"
  and "genuine low usage" determines the outcome. Skipping Stage B would leave
  the result ambiguous.

**Recommended: Proceed with Stage B**, structured as:
1. For each failing GT section, search transcripts for behavioral evidence
   (actions that comply with the protocol without naming it)
2. Classify each as "true negative" (protocol genuinely not salient for GE)
   or "false negative" (protocol followed but not detectable by reference counting)
3. If any are false negatives, document the extraction limitation and propose
   whether a different measurement approach (e.g., behavioral pattern matching)
   could detect them
4. Report final ground truth score with qualifications

## 7. Artifacts

- `stage-a-results.json` — Full UsageReport (Pydantic JSON, 177 sections)
- `stage-a-results.md` — This document

## 8. Status

**Stage A: COMPLETE (instrumentation bug found, corrected score 57%)**
**Stage B: PENDING (focused validation of 3 failing GT sections)**
**Overall EXP-009: IN PROGRESS**
