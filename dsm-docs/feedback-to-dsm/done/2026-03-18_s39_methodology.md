# Session 39 Methodology Feedback

## Entry 48: Experiment Coverage Gap in Epoch Planning

**Date:** 2026-03-18
**Session:** 39
**Context:** Epoch 4 plan defined EXP-007 for Sprint 13 but no experiments for Sprints 14-15 or the heading refs work that emerged between sprints.

**Observation:** Epochs 2-3 maintained a pattern of one experiment per capability-introducing sprint (EXP-003b through EXP-006). This pattern was effective but implicit; it was never codified as a planning requirement. When Epoch 4 was planned, Sprint 14 was framed as "carry-forward SHOULDs" and Sprint 15 as analysis tooling. Both introduce new capabilities (incremental updates, protocol usage analysis) but neither has a defined experiment.

The gap became visible when heading reference detection was implemented (Session 38-39) with unit tests but no capability experiment. The feature emerged organically from EXP-007 findings and was never added to the epoch plan, so no experiment was scoped for it.

**Root cause:** The experiment requirement is tied to the epoch plan's "Experiment Definitions" section, but there is no checklist item or gate that enforces experiment coverage across all capability-introducing sprints. Sprint planning focuses on tasks and phases, not on validating the capability against real data.

**Impact:** Without experiments, new features are validated only by synthetic unit tests. Real-data validation happens informally (if at all), which contradicts DSM 4.0 Section 4's distinction between tests and experiments.

**Recommendation:** See Proposal #43.

## Entry 49: Branching Strategy Missing from Development Protocol

**Date:** 2026-03-18
**Session:** 39
**Context:** All Epoch 1-4 work has been committed directly to `master`. No sprint branches, no feature branches.

**Observation:** The project has no branching strategy. All work lands on `master` in sequential commits. This creates three risks:

1. **Reversibility:** Rolling back a sprint or feature requires `git revert` across many commits. A sprint branch makes rollback a single merge revert.
2. **Collaboration:** If multiple contributors work in parallel (e.g., parallel DSM sessions), they cannot isolate their changes without branches.
3. **Safety:** Experimental or incomplete work on `master` means every commit must be production-ready. Branches allow work-in-progress without polluting the main line.

**Root cause:** Neither DSM 4.0 (Development Protocol) nor DSM 2.0 (PM Guidelines) prescribe a branching strategy. The single-contributor workflow made branches feel unnecessary, but this is a scalability and safety gap.

**Impact:** Low for now (single contributor), but becomes critical if parallel sessions or external contributors are introduced. Even for a single contributor, reversibility and safety benefits justify the overhead.

**Recommendation:** See Proposal #44.

## Entry 50: Agent Should Actively Suggest When Asked

**Date:** 2026-03-18
**Session:** 39
**Context:** User asked "Any Q or S?" (questions or suggestions) after providing branching strategy feedback. Agent filed feedback silently without offering suggestions, despite having considered a naming convention idea internally.

**Observation:** When the human explicitly invites questions or suggestions, the agent should engage collaboratively, not proceed passively. In this case, the agent had considered suggesting a `sprint-N/short-description` naming convention and a checkpoint branch field but chose not to surface them. Both turned out to be exactly what the user wanted.

The DSM collaboration model (DSM_0.2) emphasizes human-AI collaboration where both parties contribute. Passive acceptance of directives without engaging when invited contradicts the collaborative spirit. The agent's internal reasoning should become external output when the user creates space for it.

**Root cause:** The agent defaults to compliance over collaboration. When given a clear directive, it executes rather than engaging, even when explicitly invited to contribute. This may stem from the "explain then execute" protocol being interpreted as one-directional (agent explains its plan, user approves) rather than bidirectional (both parties refine the approach).

**Impact:** Missed opportunities for improvement. The user must discover gaps independently rather than benefiting from the agent's analysis. Reduces the quality of feedback entries and proposals.

**Recommendation:** DSM_0.2 should explicitly state that when the human invites input ("Any Q or S?", "thoughts?", "what do you think?"), the agent MUST offer at least one substantive suggestion or question before proceeding. This is not optional politeness; it is a collaboration protocol requirement.

## Entry 51: Experiment Framework Exists in DSM But Not Operationalized

**Date:** 2026-03-18
**Session:** 39
**Context:** EXP-008 was run as ad-hoc inline Python in Bash commands with no reproducible script. Investigation revealed DSM Appendix C.1.3-C.1.6 has comprehensive experiment templates, folder conventions, and a required EXPERIMENTS_REGISTRY.md, but this project has never followed them.

**Observation:** DSM provides a detailed experiment lifecycle:
- 7-element framework (Hypothesis, Baseline, Method, Variables, Success Criteria, Results, Decision)
- Folder naming convention: `s{SS}_d{DD}_exp{NNN}/` with README.md, scripts, results data
- `EXPERIMENTS_REGISTRY.md` as a required central index
- Limitation Discovery Protocol (C.1.5) for findings
- Post-experiment contribution assessment (4.4.2)

But across 8 experiments (EXP-003 through EXP-008), this project has never fully followed the framework:
- EXP-003-006: standalone .py scripts at `data/experiments/` root, no subfolders, no README, no registry
- EXP-007: has a subfolder with design.md and results.md (closer), but custom naming, no script, no registry
- EXP-008: ad-hoc Bash commands, no script, no 7-element structure, no registry

**Root cause:** The framework is documented in Appendix C.1 (deep in the methodology) but there is no operational checklist or agent protocol that triggers consultation of C.1 when an experiment begins. The agent does not proactively check templates before running experiments.

**Impact:** Experiments are not reproducible, not consistently structured, and not indexed. New sessions cannot reliably find or rerun past experiments.

**Recommendation:** See Proposal #45.

## Entry 52: Reproducibility Is a Baseline Requirement, Not a Question

**Date:** 2026-03-18
**Session:** 39
**Context:** After running EXP-008 as ad-hoc Bash commands, the agent asked the user "Should I create a reproducible .py script?" The user correctly pointed out this should be obvious.

**Observation:** Experiments must be reproducible by the same principle that tests must be automated. Asking whether to make an experiment reproducible is equivalent to asking "should I write automated tests or just test manually?" The answer is always yes.

The agent defaulted to the minimum effort (ad-hoc execution) and asked permission to do the right thing (reproducible script). This inverts the correct default: reproducibility should be the starting point, with ad-hoc execution only as an emergency fallback.

**Root cause:** The agent does not treat experiment execution with the same rigor as test execution. Tests are always written as files; experiments are sometimes run as throwaway commands. This asymmetry is a blind spot.

**Impact:** Non-reproducible experiments waste effort (must be re-designed from scratch if results need verification) and undermine the scientific validity of the findings.

**Recommendation:** DSM_0.2 or DSM 4.0 should state: "Experiments MUST be implemented as executable scripts saved in `data/experiments/`. Ad-hoc execution in terminals is not acceptable. This is the experiment equivalent of the TDD principle: the experiment script IS the reproducible method."

## Entry 53: Experiment Templates Architecturally Invisible to the Agent

**Date:** 2026-03-18
**Session:** 39
**Context:** The agent ran EXP-008 without consulting DSM Appendix C.1.3-C.1.6 because it did not know the templates existed. Investigation found the root cause is a discoverability gap in the DSM module architecture.

**Observation:** The experiment framework lives in `DSM_1.0_Methodology_Appendices.md` (Appendix C.1.3-C.1.6). The agent's context loads DSM_0.2 via `@` reference, which contains a brief mention at line 345: "For experiments, use the Design Decisions template in Appendix C.1.3." DSM_0.2.D also points to C.1 for evaluation phases.

However, neither mention acts as a behavioral trigger. The chain breaks because:

1. **DSM_0.2 mentions C.1 passively**, as a reference, not as a protocol step ("before starting an experiment, read C.1")
2. **DSM_0.2.D is not always loaded** (it's a module, loaded on demand)
3. **The Appendices file is never auto-loaded** via `@` reference
4. **The agent works with what's in context** and does not proactively scan unloaded DSM files for applicable templates

The result: a comprehensive experiment framework exists but is architecturally invisible to the agent in the most common workflow. The agent only discovers C.1 if it proactively searches (which requires knowing to search, which requires knowing C.1 exists).

**Root cause:** The DSM modular architecture (BL-090 split) optimizes for context budget by keeping the Appendices out of the core load. But this creates a tradeoff: operational templates in unloaded files are effectively undiscoverable unless the loaded modules contain strong behavioral triggers, not just passive references.

**Impact:** The agent reinvents experiment structure from scratch each time instead of following established templates. 8 experiments across 4 epochs, none fully conforming to C.1.

**Recommendation:** See Proposal #45 (add experiment protocol to DSM_0.2 as a behavioral trigger). Additionally, consider adding a "Template Lookup Protocol" to DSM_0.2 core: when starting any templated activity (experiment, decision record, blog post), the agent MUST check the relevant Appendix section before proceeding. This transforms passive references into active triggers.

## Entry 54: Design for Parsability, Heading Convention for Cross-Reference Quality

**Date:** 2026-03-18
**Session:** 39
**Context:** EXP-008 showed heading reference detection has ~27% FP rate with a 3-word minimum filter. Root cause: generic short headings ("When to Use", "Overview") match common prose. Since DSM is authored by this team, we can prescribe heading conventions that make detection reliable at the source.

**Observation:** The "Take a Bite" philosophy applies to documentation conventions: since we author the DSM documents ourselves, we have the advantage of prescribing formats that are both human-readable and machine-parsable. Rather than building increasingly complex NLP filters to handle ambiguous headings, we can define conventions that eliminate ambiguity at the source.

Three complementary conventions would dramatically improve heading reference detection:

1. **Minimum token rule:** Any referenceable heading, regardless of level, MUST contain at least 4 non-stopword tokens. This eliminates the main FP source: generic phrases like "When to Use" (2 non-stopwords) becoming "When to Use This Protocol" (4 non-stopwords).

2. **Heading uniqueness:** Headings used as cross-referenceable concepts should be unique across the document set. If "Overview" appears in 15 files, it is useless as a cross-reference target.

3. **Protocol-scoped naming:** Headings should include the protocol/concept name for self-description. "Session Transcript Protocol" is self-describing; "Protocol" alone is not.

**Impact:** These conventions improve both human readability (clearer, more descriptive headings) and machine parsability (fewer false positives, reliable cross-reference detection). The parser can enforce these conventions via linting (a new convention check alongside E001-W003).

**Recommendation:** See Proposal #46.
