# DSM Cross-Reference Remediation Guide

**Date:** 2026-02-09
**Project:** DSM Graph Explorer

---

## Overview

`dsm-validate` scans markdown files for cross-references (`Section X.Y.Z`, `Appendix X.Y`, `DSM X.Y`) and checks that each reference points to an actual section heading in the scanned documents. It reports three severity levels:

- **ERROR** — A section or appendix reference that cannot be found in any scanned document.
- **WARNING** — A DSM document reference (`DSM X.Y`) not in the known identifiers list.
- **INFO** — An issue in a file classified as informational by the config file.

In `--strict` mode, the tool exits with code 1 if any ERROR-level issues are found. WARNING and INFO findings do not cause failure.

---

## How to Read the Output

```
DSM Integrity Report

  Errors:             10
  Warnings:           0
  Info:               0
  Version mismatches: 0

Scanned 125 file(s) in 0.08s. Found 10 error(s), 0 warning(s), 0 info(s), 0 version mismatch(es).
```

Each finding shows:
- **File** — The source file containing the reference
- **Line** — Line number where the reference appears
- **Type** — `section`, `appendix`, or `dsm`
- **Target** — The referenced identifier (e.g., `2.5.6`, `A.1`, `4.0`)
- **Message** — Description of the issue

---

## Error Types and Fixes

### Broken Section Reference (ERROR)

**Message:** `Broken section reference: X.Y.Z not found in any document`

**What it means:** The file references `Section X.Y.Z`, but no scanned document has a heading numbered `X.Y.Z`.

**Common causes:**
1. Section was renumbered (e.g., `2.3` became `2.4` after a new section was inserted)
2. Section was removed entirely
3. Typo in the reference (e.g., `Section 2.56` instead of `Section 2.5.6`)
4. Cross-repo reference (the section exists in another repository)

**How to fix:**
- **Renumbered:** Search for the section by title to find its new number, then update the reference.
- **Removed:** Remove the reference or replace it with the successor section.
- **Typo:** Correct the section number.
- **Cross-repo:** If the reference is to a section in another repository (e.g., DSM central), set the file's severity to INFO in the config. See [Managing Severity](#managing-severity).

### Broken Appendix Reference (ERROR)

**Message:** `Broken appendix reference: X.Y not found in any document`

**What it means:** The file references `Appendix X.Y`, but no scanned document has an appendix heading numbered `X.Y`.

**Common causes and fixes:** Same as broken section references (renumbered, removed, typo, or cross-repo).

### Unknown DSM Document (WARNING)

**Message:** `Unknown DSM document: DSM X.Y not in known identifiers list`

**What it means:** The file references `DSM X.Y`, but that version number is not in the tool's known identifiers list.

**Known DSM identifiers:** 0, 0.1, 0.2, 1, 1.0, 1.1, 2, 2.0, 2.1, 3, 4, 4.0

**Common causes:**
1. New DSM document version not yet added to the known list
2. Typo in the version number (e.g., `DSM 5.0` when `DSM 4.0` was intended)

**How to fix:**
- **New version:** Open an issue or PR to add the new version to `KNOWN_DSM_IDS` in `src/validator/cross_ref_validator.py`.
- **Typo:** Correct the version number in the source file.

---

## Understanding Cross-Repo References

When you run `dsm-validate` on a repository that *references* DSM sections but doesn't *contain* the DSM documents, all those references will appear as broken. This is expected behavior: the validator can only check references against documents it scans.

**Example:** The `dsm-graph-explorer` repository references "Section 2.5.6 (Blog Process)" in its docs, but Section 2.5.6 is defined in the DSM central repository. Since `dsm-validate` only scans `dsm-graph-explorer`, it reports the reference as broken.

**Solution:** Use the config file to set cross-repo-heavy files to INFO severity:

```yaml
# .dsm-graph-explorer.yml
severity:
  - pattern: "docs/**/*.md"
    level: INFO
  - pattern: "*.md"
    level: WARNING
```

This keeps the findings visible (for reference) but prevents them from blocking CI in `--strict` mode.

---

## Managing Exclusions

### When to Exclude Files

- **Generated files** — HTML coverage reports, build artifacts
- **Archives** — Deprecated documents preserved for history
- **Third-party docs** — Vendored documentation from other projects
- **Reference materials** — Files kept for context but not maintained

### How to Exclude

**CLI (one-time):**
```bash
dsm-validate . --exclude 'plan/*' --exclude 'CHANGELOG.md'
```

**Config file (persistent):**
```yaml
# .dsm-graph-explorer.yml
exclude:
  - CHANGELOG.md
  - docs/checkpoints/*
  - references/*
  - plan/archive/*
```

### Pattern Syntax

Exclusion patterns use fnmatch:
- `*` — matches any characters except path separator
- `**` — matches any characters including path separators
- `?` — matches a single character
- `[seq]` — matches any character in sequence

**Examples:**
| Pattern | Matches | Does Not Match |
|---------|---------|---------------|
| `CHANGELOG.md` | `CHANGELOG.md` | `docs/CHANGELOG.md` |
| `plan/*` | `plan/foo.md` | `plan/sub/foo.md` |
| `**/archive/*` | `archive/x.md`, `docs/archive/y.md` | — |
| `docs/**/*.md` | `docs/plan/foo.md`, `docs/a/b/c.md` | `README.md` |

---

## Managing Severity

### How Severity Works

1. The validator assigns a **base severity**: ERROR for broken section/appendix refs, WARNING for unknown DSM docs.
2. If the config has `severity` mappings, `apply_severity_overrides()` remaps the severity based on the **source file** path. First matching pattern wins.
3. In `--strict` mode, only ERROR-level findings cause a non-zero exit code.

### Recommended Config for DSM Repositories

For the DSM central repository (where all sections are defined):

```yaml
# .dsm-graph-explorer.yml
exclude:
  - CHANGELOG.md
  - docs/checkpoints/*
  - references/*
  - plan/*
  - plan/archive/*

severity:
  - pattern: "DSM_*.md"
    level: ERROR
  - pattern: "docs/checkpoints/*"
    level: INFO
  - pattern: "plan/*"
    level: INFO
  - pattern: "*.md"
    level: WARNING

strict: true
default_severity: WARNING
```

For spoke repositories (projects that reference DSM sections but don't contain them):

```yaml
# .dsm-graph-explorer.yml
severity:
  - pattern: "docs/**/*.md"
    level: INFO
  - pattern: "*.md"
    level: WARNING

strict: false
default_severity: WARNING
```

---

## CI Integration

### GitHub Actions

Copy the workflow file to your repository:

```yaml
# .github/workflows/dsm-validate.yml
name: DSM Documentation Validation

on:
  push:
    paths: ['**/*.md', '.dsm-graph-explorer.yml']
  pull_request:
    paths: ['**/*.md', '.dsm-graph-explorer.yml']

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install dsm-graph-explorer
      - run: dsm-validate . --strict
```

**Note:** The workflow auto-discovers `.dsm-graph-explorer.yml` in the repo root. No `--config` flag needed.

**For the dsm-graph-explorer repo itself**, replace `pip install dsm-graph-explorer` with `pip install .` since the tool is installed from the local checkout.

### Pre-commit Hook

**Manual installation:**
```bash
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Pre-commit framework:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dsm-validate
        name: Validate DSM cross-references
        entry: dsm-validate --strict
        language: system
        types: [markdown]
        pass_filenames: true
```

The hook only validates staged `.md` files. If `dsm-validate` is not installed, it prints a warning and allows the commit to proceed.

---

## Best Practices

### Writing Cross-References

- Use consistent patterns: `Section X.Y.Z`, not `see X.Y.Z` or `X.Y.Z`
- Add context: `Section 2.4 (Human Baseline)` helps readers even if the number changes
- Prefer stable identifiers (section titles) over numbers where possible

### Handling Section Renumbering

1. Before renaming a section, search for references to the old number
2. Update all references in the same commit as the rename
3. Document the rename in the commit message

### Maintaining Config

- Keep `.dsm-graph-explorer.yml` in version control
- Review exclusions when adding new file categories
- Update severity mappings when project structure changes
- Periodically run without exclusions to see the full picture: `dsm-validate . --config /dev/null`
