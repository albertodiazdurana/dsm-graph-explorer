# DSM Central Feedback: Inputs for Epoch 2

**Date:** 2026-02-04
**From:** DSM Central repository session
**To:** Graph Explorer Epoch 2 planning
**Type:** Cross-project alignment feedback

---

## Summary

DSM Central attempted Phase 2 remediation using Graph Explorer's integrity report. The process revealed a parser bug (now fixed) and validated the exclusion strategy from DEC-003. This document captures inputs for Epoch 2 development.

---

## Parser Bug Resolution

### What Happened
When attempting to remediate the 448 "broken references," DSM Central discovered most were false positives:
- DSM uses `### 2.3.7. Title` (trailing period)
- Parser expected `### 2.3.7 Title` (no trailing period)
- 242 sections were invisible to the parser

### Fix Applied
- Regex updated with `\.?` for optional trailing period
- 5 new tests added for trailing period format
- Result: **448 errors → 6 errors** (98.7% reduction)

### Backlog Item Updated
The `2026-02-04_parser-trailing-period-fix.md` backlog item can be marked as **resolved**.

---

## Remaining 6 Errors Analysis

All 6 reference "Section 2.6" which doesn't exist. Located in `plan/` folder:

| File | Count | Context |
|------|-------|---------|
| `plan/Data_Science_Frameworks_Standards_Overview.md` | 1 | Proposal table |
| `plan/DSM_vs_CRISP-DM_Comparison_Analysis.md` | 3 | Recommendations |
| `plan/archive/BACKLOG-003_deployment-mlops.md` | 2 | Implementation notes |

**Decision:** These are proposals ("Add Section 2.6 or expand DSM 4.0"), not references to existing content. No remediation needed — exclude `plan/` folder.

---

## Validated Exclusion Strategy

DEC-003's exclusion-first approach is confirmed correct. Recommended exclusion list for Epoch 2:

```yaml
exclude:
  - CHANGELOG.md           # Historical drift (valid when written)
  - docs/checkpoints/*     # Milestone snapshots
  - references/*           # Archive folder
  - plan/*                 # Planning docs with proposals
  - plan/archive/*         # Archived backlog items
```

With these exclusions: **0 errors** in active DSM documentation.

---

## Inputs for Epoch 2 Sprint 4

### Priority: `--exclude` Flag
The exclusion flag is the highest priority for Epoch 2. Without it:
- Every run reports 6 "errors" that aren't actionable
- CI integration would fail on proposals, not real issues
- Users can't focus on active documentation

### Suggested Implementation
1. CLI flag: `--exclude PATTERN` (repeatable)
2. Config file: `.dsm-graph-explorer.yml` with `exclude:` list
3. Default exclusions for known non-actionable patterns

### Test Case
```bash
# Should report 0 errors after exclusions
dsm-validate D:\data-science\agentic-ai-data-science-methodology \
  --exclude "plan/*" \
  --exclude "CHANGELOG.md" \
  --exclude "references/*"
```

---

## DSM Methodology Feedback

### BACKLOG-049 Created
**Fixture Validation Against Real Data** — The parser bug happened because the test fixture was created from assumption, not observation. DSM 4.0 should add guidance:

> Before writing tests against synthetic fixtures, verify the fixture format matches actual production data. Run at least one capability experiment on real data in Sprint 1 to validate assumptions.

This is tracked in DSM Central at `plan/backlog/BACKLOG-049_fixture-validation-against-real-data.md`.

---

## Cross-Project Learning

### Pattern Validated
The hub-and-spoke governance model worked:
1. Graph Explorer produced integrity report
2. DSM Central attempted remediation
3. Bug discovered through real-world use
4. Fix applied in Graph Explorer
5. Feedback flows back to both projects

### For Graph Explorer Blog
Good material for the "dog-fooding" narrative:
- Tool validated its own methodology repository
- Real-world use found a bug that 145 tests missed
- The fixture assumption → production mismatch is a universal lesson

---

## Action Items for Graph Explorer

| # | Action | Priority | Sprint | Status |
|---|--------|----------|--------|--------|
| 1 | Mark `2026-02-04_parser-trailing-period-fix.md` as resolved | High | Now | **DONE** (moved to done/) |
| 2 | Implement `--exclude` flag | High | Sprint 4 | Pending |
| 3 | Add default exclusion config for DSM repos | Medium | Sprint 4 | Pending |
| 4 | Update epoch-2-plan.md with validated exclusion list | Medium | Sprint 4 | Pending |
| 5 | Add fixture validation lesson to blog journal | Low | Sprint 4 | Pending |

---

**Feedback Status:** Ready for Epoch 2 planning
**Created by:** DSM Central (Alberto + Claude)
