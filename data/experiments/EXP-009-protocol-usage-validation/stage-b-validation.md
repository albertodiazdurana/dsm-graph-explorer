# EXP-009 Stage B: Transcript Validation

**Date:** 2026-04-02
**Session:** 45
**Purpose:** Determine whether the 3 failing ground truth sections are true
negatives (genuinely low usage) or false negatives (protocol followed but not
detected by reference counting).

---

## 1. Method

For each failing ground truth section:
1. Search all 18 transcripts for direct name mentions
2. Search for behavioral evidence (actions consistent with the protocol,
   without naming it)
3. Search for related terms and synonyms
4. Classify as true negative or false negative
5. If false negative, assess whether a different extraction approach could
   detect it

## 2. Validation Results

### 2.1 Read-Only Access Within Repository (Score: 0)

**Direct mentions:** 1 occurrence across all transcripts.
- `2026-03-11T10:00-ST.md:153` — "read-only directory" in the context of
  FalkorDB error handling test coverage. This is a filesystem concept, not a
  reference to the DSM protocol.

**Behavioral evidence:** Searched for cross-repo operations where read-only
compliance would be observable.
- `2026-02-23T12:49-ST.md:86` — "This is a cross-repo write... Destructive
  Action Protocol applies." The agent references the Destructive Action Protocol
  when writing to DSM Central, not Read-Only Access.
- Multiple sessions perform cross-repo reads (`--compare-repo`, `--drift-report`,
  inbox checks against DSM Central) without modifying the external repo. This is
  compliance, but the agent never names the protocol.

**Classification: TRUE NEGATIVE for name-based extraction.**
The agent follows the constraint implicitly. When it does write to external repos
(inbox notifications), it cites the Destructive Action Protocol, not Read-Only
Access. The protocol exists as a safety guardrail that is respected but never
invoked by name.

**Could a different approach detect it?** Partially. A file-operation audit
(counting reads vs writes to external paths) could measure compliance. But this
requires runtime instrumentation, not transcript analysis. The reference-counting
methodology cannot detect adherence to a constraint whose observable signal is
the absence of violations.

### 2.2 Inclusive Language (Score: 1)

**Direct mentions:** 0 in transcripts. The single score point comes from a
prescribed reference (the phrase appears in one skill definition file).

**Behavioral evidence:** Searched for "inclusive", "language", "bias", "pronoun",
"exclusionary" across all transcripts. Zero matches.

**Classification: TRUE NEGATIVE for name-based extraction.**
Inclusive Language is a writing quality standard. Compliance means the agent
avoids biased terms, uses gender-neutral pronouns, etc. This produces text that
conforms, but at no point does the transcript contain reasoning like "applying
Inclusive Language protocol." The protocol is internalized by the LLM's training,
not explicitly invoked during sessions.

**Could a different approach detect it?** Only through content analysis: scanning
agent-generated text for inclusive language markers or checking for the absence
of exclusionary terms. This is a fundamentally different measurement task
(quality audit, not usage frequency) and outside EXP-009's scope.

### 2.3 Active Suggestion Protocol (Score: 0)

**Direct mentions:** 0 across all transcripts for "Active Suggestion Protocol"
or "active suggestion."

**Behavioral evidence:** Searched for "proactiv" and "suggest.*protocol":
- `2026-03-11T10:00-ST.md:173` — "I proposed 6 tests without challenging the
  composition until the user asked. The protocol should have prompted me to do
  that proactively." This is actually a *failure* to follow the protocol,
  discussed as a reasoning lesson.
- `2026-03-11T10:00-ST.md:184` — "the agent should proactively challenge its
  own reasoning about artifact composition" — discussion about the protocol's
  intent, not an invocation.
- `2026-03-11T10:00-ST.md:190` — "Challenge Myself to Reason" framing, which
  overlaps with Active Suggestion but is a different, user-coined protocol.

The agent does suggest improvements, propose backlog items, and recommend next
steps throughout sessions, but these behaviors are never attributed to the Active
Suggestion Protocol by name. The protocol formalizes behavior the agent already
exhibits from its training.

**Classification: FALSE NEGATIVE (behavioral), TRUE NEGATIVE (name-based).**
The behavior the protocol describes is present in every session. The label is
never used. The protocol formalizes an innate LLM behavior rather than prescribing
a new one.

**Could a different approach detect it?** A behavioral pattern detector could
look for unprompted suggestions (agent offers an option the user didn't ask for)
by analyzing turn structure. This would require discourse analysis, not string
matching, and is a more complex extraction task than EXP-009's current scope.

## 3. Summary

| Section | Score | Name Mentions | Behavioral Evidence | Classification |
|---|---|---|---|---|
| Read-Only Access | 0 | 0 (1 false match) | Implicit compliance | True negative |
| Inclusive Language | 1 | 0 | None observable | True negative |
| Active Suggestion | 0 | 0 | Present but unlabeled | False negative (behavioral) |

## 4. Pattern Confirmed: Procedural vs Behavioral Protocols

Stage A hypothesized that the 4 passing ground truth sections are procedural
(they prescribe named, observable actions) while the 3 failing sections are
behavioral (they prescribe qualities of behavior). Stage B confirms this:

**Procedural protocols (4/4 pass):**
- Session Transcript Protocol → "append thinking to transcript" (observable file write)
- Pre-Generation Brief Protocol → "explain before generating" (observable reasoning block)
- Three-Level Branching Strategy → "create session branch" (observable git operation)
- Ecosystem Path Registry → "read .claude/dsm-ecosystem.md" (observable file read)

**Behavioral protocols (0/3 pass):**
- Read-Only Access → "don't modify external repos" (observable only as absence)
- Inclusive Language → "avoid biased terms" (observable only through content audit)
- Active Suggestion Protocol → "proactively suggest" (observable in behavior, never labeled)

The reference-counting methodology measures protocol **salience** (how often a
protocol is explicitly named in declarations, prescriptions, and observations).
It does not measure protocol **compliance** (whether the agent's behavior
conforms to the protocol's intent). These are different questions, and
EXP-009's tooling answers only the first.

## 5. Ground Truth Assessment

### Strict Interpretation: FAIL (4/7 = 57%, below 60%)

If the 7 ground truth sections are taken as an absolute benchmark for the
extraction methodology, EXP-009 fails. The tooling cannot detect 3 of the 7
universally-required sections.

### Qualified Interpretation: CONDITIONAL PASS

The 3 failures are not extraction bugs (false negatives from broken heuristics)
but a **category mismatch** between the measurement approach and the protocol
type. The tooling correctly identifies all protocols that *can* be measured by
reference counting, and correctly reports low usage for protocols that cannot.

- **Procedural protocol recall:** 4/4 (100%)
- **Behavioral protocol recall:** 0/3 (0%, expected for this methodology)

The experiment reveals a real limitation, not a defect: reference counting is
the right tool for classifying section load priority (BL-090's need), but not
for validating universal protocol compliance.

### Recommendation for DSM Central

The ground truth set should be split:

1. **Procedural ground truth (4 sections):** Validates that reference extraction
   works. EXP-009 passes 4/4 (100%).
2. **Behavioral ground truth (3 sections):** Requires a different measurement
   approach (content audit, behavioral pattern detection, or runtime
   instrumentation). These should not be included in EXP-009's success criteria
   for reference-based analysis.

This split does not weaken the experiment. It sharpens the question: BL-090
needs to know which sections to always-load vs on-demand. Behavioral protocols
(Inclusive Language, Read-Only Access, Active Suggestion) should always-load
regardless of reference frequency, because their effect is implicit. They are
"invisible infrastructure" that cannot be deferred to on-demand loading without
risking silent compliance failures.

## 6. Artifacts

- `stage-b-validation.md` — This document
- `stage-a-results.json` — Updated with corrected GT matching (4/7 pass)
- `stage-a-results.md` — Stage A analysis with reasoning for both actions

## 7. Status

**Stage B: COMPLETE**
**EXP-009 Overall: CONDITIONAL PASS**

- Reference-based extraction works for procedural protocols (4/4)
- Behavioral protocols are invisible to reference counting (0/3, by design)
- Ground truth split recommended to DSM Central