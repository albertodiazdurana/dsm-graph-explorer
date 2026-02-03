# DEC-002: CLI Design Choices

**Date:** 2026-02-03
**Status:** Accepted
**Sprint:** Sprint 3 (CLI & Real-World Run)
**Decision maker:** Alberto Diaz Durana

---

## Context

Sprint 3 implements the CLI interface for DSM Graph Explorer. Several design decisions were made regarding arguments, exit codes, output options, and validation behaviour.

## Decisions Made

### 1. CLI Framework: Click

**Decision:** Use Click for the CLI framework.

**Rationale:**
- Industry standard for Python CLIs
- Decorator-based syntax is clean and readable
- Excellent testing support via `CliRunner` (used in 19 tests)
- Already a project dependency (specified in pyproject.toml)

**Alternatives considered:** argparse (stdlib but verbose), typer (Click wrapper, unnecessary indirection)

---

### 2. Default Path: Current Directory

**Decision:** When no paths are provided, default to `.` (current directory).

**Rationale:**
- Intuitive for users who cd into a repo before validating
- Matches behaviour of common tools (git, ruff, black)
- User can always override with explicit paths

**Implementation:** `if not paths: paths = (".",)`

---

### 3. Exit Codes: Opt-in Strict Mode

**Decision:** Exit 0 by default; exit 1 with `--strict` flag when errors are found.

**Rationale:**
- Default behaviour is informational — users viewing a report shouldn't cause CI failures
- `--strict` enables CI integration where broken refs should fail the build
- Clean separation of "report" mode vs "enforce" mode

**Alternatives considered:**
- Always exit non-zero on errors (too aggressive for interactive use)
- Separate error levels (adds complexity without clear benefit)

---

### 4. Output Location: User-specified, No Default

**Decision:** `--output` flag specifies report path; no default output location.

**Rationale:**
- Users may not want a file — console output may be sufficient
- Avoids cluttering repo with auto-generated reports
- User chooses location (e.g., `outputs/reports/`, `.tmp/`, etc.)
- Auto-creates parent directories if they don't exist

---

### 5. Glob Pattern: Configurable with Sensible Default

**Decision:** `--glob` option with default `**/*.md`.

**Rationale:**
- `**/*.md` matches all markdown files recursively — standard pattern
- Users can narrow (e.g., `docs/**/*.md`) or widen (e.g., `**/*.txt`)
- Glob is applied when path is a directory; file paths are used directly

---

### 6. Version Consistency: Opt-in

**Decision:** `--version-files` is repeatable and opt-in.

**Rationale:**
- Not all validation runs need version consistency checking
- Some repos don't have version strings to compare
- Repeatable flag allows specifying multiple files: `--version-files README.md --version-files DSM_0.md`

---

### 7. Known DSM Identifiers: Expanded List

**Decision:** Expand `KNOWN_DSM_IDS` from 5 to 11 entries after real-world validation.

**Original list:** `["0", "1.0", "1.1", "2.0", "4.0"]`

**Expanded list:**
```python
KNOWN_DSM_IDS = [
    "0",      # START_HERE guide
    "0.1",    # File naming quick reference
    "1",      # DSM 1 (short form)
    "1.0",    # DSM 1.0 methodology
    "1.1",    # DSM 1.1 methodology update
    "2",      # DSM 2 (short form)
    "2.0",    # DSM 2.0 PM guidelines
    "2.1",    # DSM 2.1 PM supplement
    "3",      # DSM 3 multi-agent collaboration
    "4",      # DSM 4 (short form)
    "4.0",    # DSM 4.0 software engineering adaptation
]
```

**Rationale:**
- Real-world run against DSM repo revealed 152 warnings for unknown IDs
- DSM documents use both long forms (DSM 1.0) and short forms (DSM 1)
- Additional documents (DSM 0.1, 2.1, 3) weren't in original list
- Expansion reduced warnings from 152 → 0

**Lesson learned:** Design decisions need validation against real data. Initial assumptions were incomplete.

---

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| Click | Clean, testable, standard | Another dependency |
| Default `.` | Intuitive | Could be surprising if run from wrong dir |
| `--strict` opt-in | Flexible | CI must remember to add flag |
| No default output | Clean | Users must specify path for reports |
| `**/*.md` default | Covers most cases | May scan unwanted files in node_modules, etc. |
| Expanded IDs | No false warnings | Must update list as new DSM docs are added |

---

## Implementation

- **CLI entry point:** `src/cli.py` → `main()` function
- **pyproject.toml:** `dsm-validate = "cli:main"`
- **Tests:** `tests/test_cli.py` — 19 tests covering all options

---

**References:**
- Sprint 3 checkpoint: `docs/checkpoints/2026-02-03_sprint3-complete.md`
- CLI source: `src/cli.py`
- Integrity report: `outputs/reports/dsm-integrity-report.md`
