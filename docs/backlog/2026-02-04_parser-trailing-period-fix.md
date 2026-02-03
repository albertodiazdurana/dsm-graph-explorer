# Bug: Parser Doesn't Match Section Headings with Trailing Periods

**Date:** 2026-02-04
**Priority:** High
**Type:** Bug Fix
**Discovered by:** DSM Central repository validation (Phase 2 remediation attempt)

---

## Problem

The markdown parser's regex patterns do not match DSM's actual heading format. DSM uses trailing periods in section numbers:

```markdown
### 2.3.7. Data Leakage Prevention
### A.1.2. Environment Details
```

But the parser expects headings without trailing periods:

```markdown
### 2.3.7 Data Leakage Prevention
### A.1.2 Environment Details
```

This causes valid sections to be missed during parsing, which means valid cross-references report as "broken" during validation.

---

## Impact

- **DSM_1.0 main document:** 128 sections with trailing period format not being parsed
- **DSM_1.0 Appendices:** 114 sections with trailing period format not being parsed
- **Total:** 242 sections missed → majority of the 448 "errors" are false positives

The current integrity report is not actionable because it conflates real broken references with parser pattern mismatches.

---

## Evidence

```bash
# Sections exist but aren't found by parser
$ grep "2.3.7" DSM_1.0_*.md
974:### 2.3.7. Data Leakage Prevention    # EXISTS with trailing period
1401:Cross-reference: Section 2.3.7       # Reference is VALID

# Validator reports as broken
| DSM_0_START_HERE_Complete_Guide.md | 144 | section | 2.3.7 | Broken section reference |
```

---

## Proposed Fix

Update regex patterns in `src/parser/markdown_parser.py` to handle optional trailing period:

**Current pattern (line ~XX):**
```python
NUMBERED_HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(\d+(?:\.\d+)*)\s+(.+)$')
```

**Fixed pattern:**
```python
NUMBERED_HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(\d+(?:\.\d+)*)\.?\s+(.+)$')
#                                                                  ^^^  optional period
```

Similarly for appendix patterns:
```python
# Handle A.1.2. format (with trailing period)
APPENDIX_SUBSECTION_PATTERN = re.compile(r'^(#{1,6})\s+([A-E](?:\.\d+)+)\.?\s+(.+)$')
```

---

## Acceptance Criteria

1. Parser extracts sections with trailing periods (e.g., `### 2.3.7.`)
2. Parser still extracts sections without trailing periods (backward compatible)
3. Existing tests pass
4. New tests added for trailing period format
5. Re-run against DSM repository produces significantly fewer errors

---

## Expected Outcome

After fix:
- 448 errors → estimated ~50-100 actual broken references
- Actionable error list for Phase 2 remediation
- Integrity report becomes useful for DSM maintenance

---

## Related

- DEC-001: Parser library choice (regex approach)
- DEC-003: Error remediation strategy (blocked until this is fixed)
- DSM Central checkpoint: 2026-02-04_graph-explorer-epoch1-integration_checkpoint.md

---

**Reported by:** DSM Central (Alberto + Claude)
**Assigned to:** Graph Explorer Epoch 2
**Sprint:** Sprint 4 (Exclusion & Severity) or earlier hotfix
