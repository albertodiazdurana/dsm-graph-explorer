# Architecture Audit: BL-170 Part B

**Date:** 2026-03-16
**Requested by:** DSM Central (BL-170)
**Scope:** Artifact inventory, git access method, cross-pattern availability

---

## 1. Artifact Inventory

Which artifact types does GE index to build graph nodes?

### Graph Node Types

| Type | Label | Location | Description |
|------|-------|----------|-------------|
| FILE | `type="FILE"` | src/graph/graph_builder.py:5,59 | One node per parsed markdown document |
| SECTION | `type="SECTION"` | src/graph/graph_builder.py:7,66 | One node per numbered section heading |
| Document | FalkorDB label | src/graph/graph_store.py:20,183 | Persistent equivalent of FILE |
| Section | FalkorDB label | src/graph/graph_store.py:22-23,202 | Persistent equivalent of SECTION |
| RepoEntity | FalkorDB label | src/graph/cross_repo.py:17-18 | Anchor node for cross-repo bridge edges |

### Entity Classification Types

| Type | Values | Location |
|------|--------|----------|
| EntityType | `section`, `protocol`, `backlog-item` | src/inventory/inventory_parser.py:24,173-180 |
| RepoType | `dsm-hub`, `dsm-spoke`, `external` | src/inventory/inventory_parser.py:25 |

### Cross-Reference Types

| Type | Values | Location |
|------|--------|----------|
| CrossReference.type | `section`, `appendix`, `dsm` | src/parser/cross_ref_extractor.py:22,113-117 |
| EdgeType (cross-repo) | `INBOX_NOTIFICATION`, `AT_IMPORT`, `ECOSYSTEM_LINK`, `MAPS_TO` | src/graph/cross_repo.py:46-52 |

### Comparison/Diff Types

| Type | Values | Location |
|------|--------|----------|
| MatchType | `IDENTICAL`, `RENAMED`, `MODIFIED`, `ADDED`, `REMOVED` | src/graph/repo_diff.py:51-58 |
| Severity | `ERROR`, `WARNING`, `INFO` | src/validator/cross_ref_validator.py:28-33 |

**Total distinct types:** 5 node labels + 3 entity types + 3 repo types + 3 cross-ref types + 4 edge types + 5 match types + 3 severities = **26 classified values across 7 categories**.

---

## 2. Git Access Method

How does GE access git data?

### Method: Local git commands via subprocess

GE calls the `git` binary through `subprocess.run()`. There is no git library (GitPython, pygit2, dulwich) and no remote API (GitHub API, REST calls).

**Core implementation:** `src/git_ref/git_resolver.py:17-36`

```
subprocess.run(["git", "-C", str(repo_path), *args],
               capture_output=True, text=True, timeout=30)
```

### Git Commands Used

| Command | Function | Location | Purpose |
|---------|----------|----------|---------|
| `git rev-parse --show-toplevel` | `find_repo_root()` | git_resolver.py:52 | Locate repository root |
| `git rev-parse --verify <ref>` | `resolve_ref()` | git_resolver.py:72 | Resolve SHA, tag, branch |
| `git ls-tree -r --name-only <sha>` | `list_files_at_ref()` | git_resolver.py:96 | List files at a commit |
| `git show <sha>:<filepath>` | `read_file_at_ref()` | git_resolver.py:124 | Read file content at a commit |

### Filesystem Access (non-git mode)

When `--git-ref` is not provided, GE reads files directly from disk:

| Operation | Location | Method |
|-----------|----------|--------|
| Directory scan | src/cli.py:35-56 | `Path.glob("**/*.md")` |
| File reading | src/parser/markdown_parser.py:55 | `path.open(encoding="utf-8")` |
| Config loading | src/config/config_loader.py:165 | `open(config_path, encoding="utf-8")` |
| Inventory loading | src/inventory/inventory_parser.py:131 | `path.read_text(encoding="utf-8")` |

### Network Access

**None.** GE makes zero HTTP requests, has no API client code, and requires no internet connection. The `pyproject.toml` dependencies (lines 20-25) include no networking or git libraries.

### Local-Only Support

**Yes, fully supported.** All CLI inputs are local filesystem paths (`click.Path(exists=True)`). The `--git-ref` option works against the local repository's object store. No remote tracking branch or origin is required.

---

## 3. Cross-Pattern Availability

Which features would be unavailable or degraded for Private Projects (local git, no remote)?

### Fully Available (filesystem only, no git required)

| Feature | CLI Flag | Reason |
|---------|----------|--------|
| Markdown parsing | (default) | Reads `.md` files from disk |
| Cross-reference validation | `--strict` | Filesystem reads only |
| Severity/exclusion config | `--config` | YAML from disk |
| File filtering | `--exclude`, `--include` | Path pattern matching |
| Semantic similarity | `--semantic` | In-memory TF-IDF, no external data |
| Convention linting | `--lint` | Reads file content from disk |
| Entity inventory | `--inventory`, `--export-inventory` | YAML files on disk |
| Graph building (NetworkX) | `--graph-stats`, `--graph-export` | In-memory from parsed documents |

### Fully Available (requires local git)

| Feature | CLI Flag | Reason |
|---------|----------|--------|
| Temporal snapshots | `--git-ref` | Uses `git show`, `git ls-tree` on local repo |
| Graph diff | `--graph-diff` | Compares two local git refs |

### Fully Available (requires FalkorDB + local git)

| Feature | CLI Flag | Reason |
|---------|----------|--------|
| Persistent graph store | `--graph-db` | Local `.falkordb` file |
| Cross-repo edges | `--compare-repo` | Local inventories + local FalkorDB |
| Drift reports | `--drift-report` | Local inventories compared in-memory |

### Degraded or Unavailable

**None.** Every GE feature operates entirely on local data. There are no features that depend on a remote, a GitHub API, or internet access.

### Summary for Private Projects

Private Projects (BL-162 pattern: local git, no remote) can use **100% of GE's features** without degradation. The only prerequisites are:

1. **git binary installed** (for `--git-ref` and `--graph-diff`)
2. **FalkorDB optional dependency** (for `--graph-db` and cross-repo features)
3. **scikit-learn optional dependency** (for `--semantic` and fuzzy inventory matching)

All three are local-only requirements with no network dependency.

---

## Appendix: I/O Method Summary

| Category | Method | Files |
|----------|--------|-------|
| Git (subprocess) | `subprocess.run(["git", ...])` | git_resolver.py |
| Filesystem (read) | `Path.open()`, `Path.read_text()`, `Path.glob()` | cli.py, markdown_parser.py, cross_ref_extractor.py, config_loader.py, inventory_parser.py |
| Filesystem (write) | `Path.write_text()`, `Path.mkdir()` | inventory_parser.py, graph_export.py |
| Database (local) | FalkorDB embedded (file-based) | graph_store.py, cross_repo.py |
| Network | None | (no files) |
