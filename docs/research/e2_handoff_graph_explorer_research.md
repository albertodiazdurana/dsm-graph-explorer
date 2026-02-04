# DSM Graph Explorer: Epoch 2 Research Handoff

**Date:** February 4, 2026
**Project:** https://github.com/albertodiazdurana/dsm-graph-explorer
**Status:** Epoch 2 Planning
**Prerequisite:** Epoch 1 Complete (Parser MVP, Validator, CLI)

---

## 1. Epoch 2 Objectives

**Goal:** Transform the validator from a one-off report tool into a CI-integrated, configurable validation system with graph exploration capabilities.

**Key Features:**
- Exclusion patterns and severity levels
- YAML configuration file support
- GitHub Actions CI integration
- Semantic validation (TF-IDF)
- NetworkX graph prototype

---

## 2. Sprint 4: Exclusion & Severity Research

### 2.1 CLI Multiple Options (Click)

**Source:** [Click Options Documentation](https://click.palletsprojects.com/en/stable/options/)

Click supports repeatable options using `multiple=True`:

```python
@click.option('--exclude', '-e', multiple=True, help='Exclude pattern (repeatable)')
def validate(exclude):
    # exclude is a tuple: ('plan/*', 'CHANGELOG.md')
    for pattern in exclude:
        ...
```

**Key points:**
- Returns a tuple, not a list
- Default must be tuple/list: `default=('*.bak',)`
- Can combine with `type=click.Path()` for path validation

**Current CLI:** Uses Click 8.1+, already has `--glob` and `--version-files` options.

### 2.2 Glob Pattern Matching (fnmatch)

**Source:** [Python fnmatch](https://docs.python.org/3/library/fnmatch.html), [Python glob](https://docs.python.org/3/library/glob.html)

For file exclusion, use `fnmatch` from stdlib:

```python
import fnmatch

def should_exclude(filepath: str, patterns: list[str]) -> bool:
    """Check if filepath matches any exclusion pattern."""
    return any(fnmatch.fnmatch(filepath, p) for p in patterns)
```

**Pattern syntax:**
- `*` — matches everything
- `?` — matches single character
- `[seq]` — matches any character in seq
- `[!seq]` — matches any character not in seq

**Examples for DSM:**
- `plan/*` — exclude plan folder
- `CHANGELOG.md` — exclude specific file
- `**/archive/*` — exclude archive subfolders
- `*.bak` — exclude backup files

**Note:** Python 3.14 adds `fnmatch.filterfalse()` for exclusion, but we target 3.12+.

### 2.3 YAML Configuration with Pydantic

**Sources:**
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Pydantic YAML Guide](https://www.sarahglasmacher.com/how-to-validate-config-yaml-pydantic/)

Using Pydantic for config validation provides type safety and clear error messages:

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import yaml

class SeverityConfig(BaseModel):
    """Severity mapping for file patterns."""
    pattern: str
    level: str = Field(pattern=r'^(ERROR|WARNING|INFO)$')

class Config(BaseModel):
    """DSM Graph Explorer configuration."""
    exclude: list[str] = Field(default_factory=list)
    severity: list[SeverityConfig] = Field(default_factory=list)
    strict: bool = False

def load_config(path: str) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(**data)
```

**Config file format (`.dsm-graph-explorer.yml`):**

```yaml
exclude:
  - plan/*
  - CHANGELOG.md
  - references/*

severity:
  - pattern: "docs/checkpoints/*"
    level: INFO
  - pattern: "*.md"
    level: ERROR

strict: true
```

**Dependencies:**
- `pydantic>=2.0` (already widely used, type-safe)
- `pyyaml>=6.0` (use `safe_load()` always)

**Alternative:** `pydantic-settings-yaml` for deeper integration, but manual load is simpler.

### 2.4 Severity Level Design

**Proposed enum:**

```python
from enum import Enum

class Severity(str, Enum):
    ERROR = "ERROR"      # Core docs, must fix
    WARNING = "WARNING"  # Should fix, but not blocking
    INFO = "INFO"        # Historical drift, informational only
```

**Default severity mappings:**
| Pattern | Severity | Rationale |
|---------|----------|-----------|
| `DSM_*.md` | ERROR | Core methodology documents |
| `docs/checkpoints/*` | INFO | Historical snapshots |
| `plan/*` | INFO | Planning documents with proposals |
| `CHANGELOG.md` | INFO | Historical entries |
| `references/*` | INFO | Archived reference materials |
| `*.md` (default) | WARNING | Catch-all for other docs |

**`--strict` behavior:**
- Without `--strict`: exit 0 always
- With `--strict`: exit 1 if any ERROR-level issues

---

## 3. Sprint 5: CI Integration Research

### 3.1 GitHub Actions Workflow

**Sources:**
- [GitHub Docs: Building and testing Python](https://docs.github.com/actions/guides/building-and-testing-python)
- [2025 GitHub Actions Python Setup](https://ber2.github.io/posts/2025_github_actions_python/)

**Modern template (2025 best practices):**

```yaml
name: DSM Validation

on:
  pull_request:
    paths:
      - '**/*.md'
  push:
    branches: [main, master]
    paths:
      - '**/*.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dsm-graph-explorer
        run: pip install dsm-graph-explorer

      - name: Validate documentation
        run: dsm-validate . --strict --config .dsm-graph-explorer.yml
```

**Key considerations:**
- Trigger on `**/*.md` changes only (efficient)
- Use `--strict` for CI (fail on errors)
- Support config file for exclusions
- Consider caching pip dependencies

### 3.2 Pre-commit Hook

**Integration with pre-commit framework:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dsm-validate
        name: Validate DSM cross-references
        entry: dsm-validate
        args: [--strict]
        language: system
        files: \.md$
        pass_filenames: false
```

**Alternative: Simple shell hook:**

```bash
#!/bin/sh
# .git/hooks/pre-commit
dsm-validate . --strict
```

---

## 4. Sprint 6: Semantic Validation Research (TF-IDF)

### 4.1 TF-IDF with scikit-learn

**Sources:**
- [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [TF-IDF and Cosine Similarity](https://medium.com/@mifthulyn07/comparing-text-documents-using-tf-idf-and-cosine-similarity-in-python-311863c74b2c)

**Basic implementation:**

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts using TF-IDF."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

# Example usage
ref_context = "See Section 2.3.7 for data leakage prevention"
section_title = "2.3.7. Data Leakage Prevention"
score = compute_similarity(ref_context, section_title)  # ~0.7+
```

**Key decisions:**
- Compare reference sentence context vs section title + first paragraph
- Threshold ~0.3 for WARNING (tunable via config)
- Pre-process: lowercase, remove punctuation, strip numbers?

### 4.2 Semantic Drift Detection

**Use case:** Section 2.3.7 was renamed from "Data Leakage" to "Reproducibility Practices" but the number stayed the same. Old references still say "See Section 2.3.7 for data leakage" — this is semantic drift.

**Detection approach:**
1. Extract 1-2 sentences around reference mention
2. Get target section title and first paragraph
3. Compute TF-IDF similarity
4. Flag if similarity < threshold

**Expected results:**
- True match: "Section 2.3.7 data leakage" ↔ "2.3.7. Data Leakage Prevention" → 0.8+
- Semantic drift: "Section 2.3.7 data leakage" ↔ "2.3.7. Reproducibility Practices" → 0.2

**Dependency:** `scikit-learn>=1.3.0` (optional, only for semantic validation)

---

## 5. Sprint 7: Graph Prototype Research (NetworkX)

### 5.1 NetworkX Basics

**Sources:**
- [NetworkX Tutorial](https://networkx.org/documentation/stable/tutorial.html)
- [NetworkX GraphML](https://networkx.org/documentation/stable/reference/readwrite/graphml.html)

**Graph construction:**

```python
import networkx as nx

# Create directed graph (references have direction)
G = nx.DiGraph()

# Add file nodes
G.add_node("DSM_1.0.md", type="FILE", title="Data Science Methodology")

# Add section nodes
G.add_node("2.3.7", type="SECTION", title="Data Leakage Prevention", file="DSM_1.0.md")

# Add edges
G.add_edge("DSM_1.0.md", "2.3.7", type="CONTAINS")
G.add_edge("DSM_0_START_HERE.md:45", "2.3.7", type="REFERENCES", line=45)
```

### 5.2 Node and Edge Types

**Node types:**
| Type | Attributes | Example |
|------|------------|---------|
| `FILE` | path, title | `DSM_1.0.md` |
| `SECTION` | number, title, file, line | `2.3.7` |

**Edge types:**
| Type | Meaning | Example |
|------|---------|---------|
| `CONTAINS` | File contains section | `DSM_1.0.md` → `2.3.7` |
| `REFERENCES` | Cross-reference | `START_HERE.md:45` → `2.3.7` |
| `PARENT_OF` | Section hierarchy | `2.3` → `2.3.7` |

### 5.3 Graph Queries

**Most referenced sections:**

```python
def most_referenced(G, n=10):
    """Find the n most referenced sections."""
    sections = [node for node, data in G.nodes(data=True) if data.get('type') == 'SECTION']
    return sorted(sections, key=lambda s: G.in_degree(s), reverse=True)[:n]
```

**Orphan sections (never referenced):**

```python
def orphan_sections(G):
    """Find sections with no incoming REFERENCES edges."""
    orphans = []
    for node, data in G.nodes(data=True):
        if data.get('type') == 'SECTION':
            refs = [e for e in G.in_edges(node, data=True) if e[2].get('type') == 'REFERENCES']
            if not refs:
                orphans.append(node)
    return orphans
```

### 5.4 Export to GraphML

```python
# Export for visualization in Gephi, yEd, etc.
nx.write_graphml(G, "dsm_references.graphml")

# Import back
G2 = nx.read_graphml("dsm_references.graphml")
```

**Visualization tools:**
- **Gephi** — Desktop app, great for large graphs
- **yEd** — Desktop app, good for hierarchical layouts
- **pyvis** — Python library for interactive HTML graphs
- **Neo4j Browser** — Future epoch, requires database

**Dependency:** `networkx>=3.2.0` (optional, only for graph features)

---

## 6. Dependency Summary

### Required (Epoch 2 Core)

```toml
dependencies = [
    "click>=8.1.0",      # CLI (existing)
    "rich>=13.7.0",      # Terminal formatting (existing)
    "pydantic>=2.0",     # Config validation (NEW)
    "pyyaml>=6.0",       # YAML parsing (NEW)
]
```

### Optional Groups

```toml
[project.optional-dependencies]
semantic = [
    "scikit-learn>=1.3.0",  # TF-IDF (Sprint 6)
]
graph = [
    "networkx>=3.2.0",      # Graph analysis (Sprint 7)
]
all = [
    "scikit-learn>=1.3.0",
    "networkx>=3.2.0",
]
```

---

## 7. Risk Assessment & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TF-IDF false positives | Medium | Medium | Configurable threshold, optional feature |
| Config complexity | Medium | Low | Good defaults, clear documentation |
| Pydantic learning curve | Low | Low | Well-documented, widespread adoption |
| NetworkX memory for large repos | Low | Low | Lazy loading, pagination |
| fnmatch edge cases | Low | Low | Comprehensive test coverage |

---

## 8. Experiment Plan

### EXP-001: Exclusion Pattern Validation

**Goal:** Verify exclusion logic correctly filters files.

**Test cases:**
1. Exact match: `CHANGELOG.md` excludes only that file
2. Wildcard: `plan/*` excludes all files in plan/
3. Nested: `**/archive/*` excludes archive/ at any depth
4. Multiple patterns: combine 1-3
5. No match: pattern that matches nothing

### EXP-002: Severity Classification

**Goal:** Validate severity assignment by pattern.

**Test cases:**
1. Default severity (no config)
2. Explicit pattern match
3. Most specific pattern wins (longest match)
4. Fallback to default

### EXP-003: TF-IDF Threshold Tuning

**Goal:** Find optimal similarity threshold for semantic drift.

**Approach:**
1. Create synthetic test cases (true matches, drift, unrelated)
2. Test thresholds: 0.2, 0.3, 0.4, 0.5
3. Measure precision/recall at each threshold
4. Select threshold with best F1 score

**Expected outcome:** Threshold ~0.3 based on literature.

### EXP-004: Graph Query Performance

**Goal:** Verify graph queries work efficiently on DSM-sized repos.

**Test cases:**
1. Build graph from DSM repository (~30 files, ~500 sections)
2. Query most-referenced sections
3. Query orphan sections
4. Export to GraphML
5. Measure memory usage and query time

---

## 9. References

### Click & CLI
- [Click Options Documentation](https://click.palletsprojects.com/en/stable/options/)
- [Click Advanced Patterns](https://click.palletsprojects.com/en/stable/advanced/)

### Configuration
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [PyYAML](https://pypi.org/project/PyYAML/)
- [Pydantic YAML Guide](https://www.sarahglasmacher.com/how-to-validate-config-yaml-pydantic/)
- [pydantic-yaml](https://github.com/NowanIlfideme/pydantic-yaml)

### Pattern Matching
- [Python fnmatch](https://docs.python.org/3/library/fnmatch.html)
- [Python glob](https://docs.python.org/3/library/glob.html)
- [wcmatch (enhanced)](https://facelessuser.github.io/wcmatch/fnmatch/)

### Semantic Validation
- [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [TF-IDF Cosine Similarity Tutorial](https://medium.com/@mifthulyn07/comparing-text-documents-using-tf-idf-and-cosine-similarity-in-python-311863c74b2c)
- [Duke Lab: Document Similarity](https://courses.cs.duke.edu/spring14/compsci290/assignments/lab02.html)

### Graph Analysis
- [NetworkX Tutorial](https://networkx.org/documentation/stable/tutorial.html)
- [NetworkX GraphML](https://networkx.org/documentation/stable/reference/readwrite/graphml.html)
- [NetworkX 2025 Guide](https://medium.com/@jainsnehasj6/networkx-for-python-a-practical-guide-to-graphs-visualization-and-traversals-35106cfee2ea)

### CI/CD
- [GitHub Actions Python](https://docs.github.com/actions/guides/building-and-testing-python)
- [2025 GitHub Actions Setup](https://ber2.github.io/posts/2025_github_actions_python/)
- [pytest-action](https://github.com/marketplace/actions/run-pytest)

---

## 10. Next Steps

1. [ ] Review research with project lead
2. [ ] Create detailed sprint plan based on this research
3. [ ] Set up optional dependency groups in pyproject.toml
4. [ ] Run EXP-001 and EXP-002 early in Sprint 4
5. [ ] Prototype TF-IDF (EXP-003) before Sprint 6 implementation
