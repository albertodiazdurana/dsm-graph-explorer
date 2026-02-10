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
  - docs/_references/*
```

### severity

A list of pattern-to-level mappings. Each entry has a `pattern` (glob string, cannot be empty) and a `level` (`ERROR`, `WARNING`, or `INFO`).

**Matching rules:**
- **First match wins.** Order matters; place specific patterns before general ones.
- Patterns without `/` match the **filename only** (e.g., `*.md` matches `README.md` and `docs/plan/foo.md`).
- Patterns with `/` match the **full relative path** (e.g., `docs/plan/*.md` matches `docs/plan/foo.md` but not `docs/foo.md`).
- Uses Python's `fnmatch` syntax: `*` matches within a path segment, `**` matches across segments, `?` matches a single character, `[seq]` matches characters in a sequence.

```yaml
severity:
  - pattern: "docs/plan/*.md"
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
| `*.md` | `README.md`, `docs/plan/foo.md` (filename match) | `script.py` |
| `docs/plan/*.md` | `docs/plan/foo.md` | `docs/plan/sub/foo.md` |
| `docs/**/*.md` | `docs/plan/foo.md`, `docs/a/b/c.md` | `README.md` |
| `README.md` | `README.md` | `docs/README.md` |
| `**/archive/*` | `archive/x.md`, `docs/archive/y.md` | |

---

## Examples

**Hub repository** (contains DSM documents, all references should resolve):

```yaml
exclude:
  - CHANGELOG.md
  - docs/checkpoints/*

severity:
  - pattern: "DSM_*.md"
    level: ERROR
  - pattern: "docs/**/*.md"
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
  - pattern: "docs/**/*.md"
    level: INFO
  - pattern: "*.md"
    level: WARNING

default_severity: WARNING
strict: false
```

Cross-repo references (e.g., `Section 2.5.6` referencing DSM central) will appear as unresolved. Setting `docs/**/*.md` to INFO keeps them visible without blocking CI. See the [remediation guide](remediation-guide.md) for details on managing cross-repo references.
