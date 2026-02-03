# DEC-003: DSM Repository Error Remediation Strategy

**Date:** 2026-02-03
**Status:** Exploring Options
**Context:** DSM Graph Explorer found 448 broken cross-references in the DSM repository

---

## Situation

Running `dsm-graph-explorer` against the DSM repository (122 files, 7,400+ lines) found 448 broken cross-references. Before deciding how to address them, we need to understand what we're dealing with.

## Error Distribution Analysis

### By File (Top 10)

| File | Errors | Category |
|------|--------|----------|
| references/Methodology_Implementation_Status_Check.md | 70 | Archive |
| CHANGELOG.md | 65 | Historical |
| references/Methodology_Update_Comprehensive_Guide.md | 60 | Archive |
| DSM_1.0_Data_Science_Collaboration_Methodology_v1.1.md | 56 | Active |
| DSM_0_START_HERE_Complete_Guide.md | 47 | Active |
| README.md | 41 | Active |
| DSM_1.0_Methodology_Appendices.md | 20 | Active |
| docs/checkpoints/* | ~50 | Historical |
| DSM_4.0_Software_Engineering_Adaptation_v1.0.md | 15 | Active |
| plan/archive/* | ~10 | Archive |

### By Category

| Category | Errors | % | Description |
|----------|--------|---|-------------|
| **Active documentation** | ~180 | 40% | Core DSM files users read |
| **Historical** | ~115 | 26% | CHANGELOG + checkpoints (valid when written) |
| **Archive/Reference** | ~153 | 34% | Old reference docs, archived plans |

---

## Options

### Option A: Full Remediation

**What:** Fix all 448 errors across all files.

**Pros:**
- Clean validation output (0 errors)
- All references resolve

**Cons:**
- High effort (~448 manual edits)
- Historical files lose context (changelog entries should reference sections as they existed)
- Archive files may not be worth maintaining

**Verdict:** Not recommended. Historical drift is intentional documentation of evolution.

---

### Option B: Triage by Category

**What:** Different treatment for different file categories.

| Category | Treatment |
|----------|-----------|
| Active | Fix broken references |
| Historical | Accept drift (informational) |
| Archive | Deprecate or exclude from validation |

**Implementation:**
1. Fix ~180 errors in active documentation
2. Add `--exclude` patterns for historical/archive files
3. Document that CHANGELOG drift is expected

**Pros:**
- Focused effort on what matters
- Historical context preserved
- Archive files don't pollute reports

**Cons:**
- Still significant work (~180 fixes)
- Need to decide which files are "active"

**Verdict:** Recommended approach. Matches how documentation actually works.

---

### Option C: Exclusion-First

**What:** Configure the tool to exclude historical/archive files, then assess remaining errors.

**Implementation:**
1. Add `--exclude` flag to CLI
2. Create `.dsm-graph-explorer.yml` config file
3. Exclude: `CHANGELOG.md`, `docs/checkpoints/*`, `references/*`, `plan/archive/*`
4. Run validation on remaining files
5. Fix actionable errors

**Pros:**
- Quick reduction from 448 → ~180 errors
- Can be done incrementally
- Config file documents what's excluded and why

**Cons:**
- Requires tool enhancement
- Excluded files still have broken refs (just hidden)

**Verdict:** Good first step. Implement exclusion, then tackle Option B.

---

### Option D: Severity-Based Approach

**What:** Enhance tool to assign severity based on file location/age.

| Severity | Files | Action |
|----------|-------|--------|
| ERROR | Core docs (DSM_*.md, README) | Must fix |
| WARNING | Supporting docs | Should fix |
| INFO | Historical/archive | Informational only |

**Implementation:**
1. Add file classification logic to validator
2. Config file maps patterns to severity
3. `--strict` only fails on ERROR severity

**Pros:**
- Nuanced reporting
- CI can enforce core docs without blocking on historical drift
- Clear prioritization

**Cons:**
- More complex implementation
- Need to define classification rules

**Verdict:** Good future enhancement. Implement after Option C.

---

### Option E: Section Rename Tracking (Future)

**What:** Track section renames to update references automatically.

**Implementation:**
1. Maintain `section-renames.yml` mapping old → new section numbers
2. Tool suggests fixes based on rename history
3. Semi-automated remediation

**Pros:**
- Prevents future drift
- Makes remediation easier
- Documents evolution explicitly

**Cons:**
- Requires discipline to maintain rename log
- Retroactive mapping is hard

**Verdict:** Future enhancement. Useful after initial remediation.

---

## Recommended Path

### Phase 1: Quick Win (Now)

1. **Add exclusion support** to CLI (`--exclude` flag or config file)
2. **Create baseline config** excluding:
   - `CHANGELOG.md`
   - `docs/checkpoints/*`
   - `references/*`
   - `plan/archive/*`
3. **Run validation** on remaining files → expect ~180 errors

### Phase 2: Active Remediation (Next)

1. **Prioritize by file importance:**
   - P1: DSM_0_START_HERE_Complete_Guide.md (47 errors)
   - P1: README.md (41 errors)
   - P2: DSM_1.0_*.md (76 errors)
   - P2: DSM_4.0_*.md (15 errors)
   - P3: Other active docs
2. **Fix in batches** (10-20 at a time)
3. **Validate after each batch**

### Phase 3: Prevention (Future)

1. **CI integration** with `--strict` on core docs
2. **Pre-commit hook** for new references
3. **Section rename tracking** for major refactors

---

## Decision

**Selected approach:** Option C (Exclusion-First) → Option B (Triage by Category)

**Rationale:**
- Exclusion gives immediate clarity on actionable errors
- Triage ensures effort goes to files users actually read
- Historical drift is preserved as documentation of evolution

**Next action:** Implement `--exclude` flag in CLI

---

## Open Questions

1. Should `references/` folder be deprecated entirely?
2. What's the threshold for "active" vs "archive"?
3. Should we generate a `fixes.md` file with suggested edits?

---

**Author:** Alberto Diaz Durana (with AI assistance)
**Last Updated:** 2026-02-03
