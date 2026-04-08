# Configuration Reference

**Project:** DSM Graph Explorer
**Config file:** `.dsm-graph-explorer.yml`

---

## Overview

DSM Graph Explorer reads configuration from a `.dsm-graph-explorer.yml` file in the repository root. The file controls which files are scanned, how severity levels are assigned, and whether validation failures block CI.

**Auto-discovery:** When no `--config` flag is provided, the tool searches for `.dsm-graph-explorer.yml` in the current directory and parent directories. If no config file is found, all fields use their default values.

---

## Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `exclude` | list of strings | `[]` | Glob patterns for files to skip during validation |
| `severity` | list of mappings | `[]` | File pattern to severity level mappings (first match wins) |
| `default_severity` | `ERROR`, `WARNING`, or `INFO` | `WARNING` | Severity assigned to files that don't match any severity pattern |
| `strict` | boolean | `false` | Exit with code 1 if any ERROR-level issues are found |

---

## Field Details

### exclude

A list of glob patterns. Files matching any pattern are skipped entirely (not scanned, not reported). Empty patterns are silently ignored.

```yaml
exclude:
  - htmlcov/*
  - outputs/*
  - dsm-docs/_references/*
```

### severity

A list of pattern-to-level mappings. Each entry has a `pattern` (glob string, cannot be empty) and a `level` (`ERROR`, `WARNING`, or `INFO`).

**Matching rules:**
- **First match wins.** Order matters; place specific patterns before general ones.
- Patterns without `/` match the **filename only** (e.g., `*.md` matches `README.md` and `dsm-docs/plan/foo.md`).
- Patterns with `/` match the **full relative path** (e.g., `dsm-docs/plan/*.md` matches `dsm-docs/plan/foo.md` but not `dsm-docs/foo.md`).
- Uses Python's `fnmatch` syntax: `*` matches within a path segment, `**` matches across segments, `?` matches a single character, `[seq]` matches characters in a sequence.

```yaml
severity:
  - pattern: "dsm-docs/plan/*.md"
    level: INFO
  - pattern: "README.md"
    level: WARNING
  - pattern: "*.md"
    level: WARNING
```

### default_severity

The severity level assigned to files that don't match any `severity` pattern. Must be one of `ERROR`, `WARNING`, or `INFO`.

```yaml
default_severity: WARNING
```

### strict

When `true`, the tool exits with code 1 if any ERROR-level issues are found. WARNING and INFO findings do not cause failure regardless of this setting.

```yaml
strict: false
```

---

## CLI Interaction

CLI flags combine with the config file, not replace it.

| CLI flag | Behavior |
|----------|----------|
| `--config PATH` | Load config from a specific file instead of auto-discovery. Fails if the file does not exist. |
| `--exclude PATTERN` | Added to `exclude` patterns from the config file (cumulative). Repeatable. |
| `--strict` | Overrides `strict` to `true`. If omitted, the config file value is used. |

The `severity` and `default_severity` fields can only be set via the config file.

---

## Pattern Syntax Reference

| Pattern | Matches | Does Not Match |
|---------|---------|----------------|
| `*.md` | `README.md`, `dsm-docs/plan/foo.md` (filename match) | `script.py` |
| `dsm-docs/plan/*.md` | `dsm-docs/plan/foo.md` | `dsm-docs/plan/sub/foo.md` |
| `dsm-docs/**/*.md` | `dsm-docs/plan/foo.md`, `dsm-docs/a/b/c.md` | `README.md` |
| `README.md` | `README.md` | `dsm-docs/README.md` |
| `**/archive/*` | `archive/x.md`, `dsm-docs/archive/y.md` | |

---

## Examples

**Hub repository** (contains DSM documents, all references should resolve):

```yaml
exclude:
  - CHANGELOG.md
  - dsm-docs/checkpoints/*

severity:
  - pattern: "DSM_*.md"
    level: ERROR
  - pattern: "dsm-docs/**/*.md"
    level: INFO
  - pattern: "*.md"
    level: WARNING

default_severity: WARNING
strict: true
```

**Spoke repository** (references DSM sections defined elsewhere):

```yaml
exclude:
  - htmlcov/*
  - outputs/*

severity:
  - pattern: "dsm-docs/**/*.md"
    level: INFO
  - pattern: "*.md"
    level: WARNING

default_severity: WARNING
strict: false
```

Cross-repo references (e.g., `Section 2.5.6` referencing DSM central) will appear as unresolved. Setting `dsm-docs/**/*.md` to INFO keeps them visible without blocking CI. See the [remediation guide](remediation-guide.md) for details on managing cross-repo references.
