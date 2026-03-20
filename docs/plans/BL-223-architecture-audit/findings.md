# Graph Explorer Architecture Audit

**Date:** 2026-03-20
**Requested by:** DSM Central BACKLOG-199
**Performed in:** Graph Explorer parallel session (`parallel/architecture-audit`)
**Method:** Direct source code examination

---

## 1. Artifact Inventory

All artifact types Graph Explorer indexes to build graph nodes, confirmed by reading source code.

### 1.1 Document Nodes (FILE)

| Property | Value |
|----------|-------|
| Source | `src/graph/graph_builder.py:82-84` |
| Input | Markdown files (`.md`) |
| Node ID | File path (e.g., `docs/plans/epoch-1-plan.md`) |
| Attributes | File basename |

### 1.2 Numbered Section Nodes (SECTION)

| Property | Value |
|----------|-------|
| Source | `src/parser/markdown_parser.py:51`, `src/graph/graph_builder.py:36-44` |
| Pattern | `\d+(?:\.\d+)*` (e.g., `1.2.3`, `2.5`) |
| Node ID | `file_path:number` (e.g., `docs/DSM.md:2.3.7`) |
| Attributes | Number, title, line number, heading level (1-6), context excerpt |

### 1.3 Appendix Section Nodes (SECTION)

| Property | Value |
|----------|-------|
| Source | `src/parser/markdown_parser.py:52-53` |
| Patterns | `Appendix [A-E]: Title`, `A.1.2 Title` |
| Node ID | `file_path:A` or `file_path:A.1.2` |
| Attributes | Number, title, line number, heading level, context excerpt |

### 1.4 Unnumbered Heading Nodes (SECTION)

| Property | Value |
|----------|-------|
| Source | `src/parser/markdown_parser.py:146-179`, `src/graph/graph_builder.py:133-148` |
| Input | Markdown headings (H1-H6) without numeric prefix |
| Node ID | `file_path:h:slugified-title` (e.g., `docs/guides/overview.md:h:session-transcript-protocol`) |
| Attributes | Title, heading level, line number, context excerpt |

### 1.5 Cross-Reference Edges (REFERENCES)

| Ref Type | Pattern | Source |
|----------|---------|--------|
| Section ref | `Section \d+(\.\d+)*` | `src/parser/cross_ref_extractor.py:32` |
| Appendix ref | `Appendix [A-E](\.\d+)*` | `src/parser/cross_ref_extractor.py:33` |
| DSM doc ref | `DSM[_ ]\d+(\.\d+)*` | `src/parser/cross_ref_extractor.py:34` |
| Heading ref | Exact case-insensitive match to known heading titles | `src/parser/cross_ref_extractor.py:178-261` |

Edge attributes: line number, reference type, context (surrounding lines).

### 1.6 Entity Inventory Entries (External)

| Property | Value |
|----------|-------|
| Source | `src/inventory/inventory_parser.py:32-62` |
| Input | YAML (`dsm-entity-inventory.yml`) |
| Entity types | `section`, `protocol`, `backlog-item` |
| Attributes | id, type, path, heading, level, stable flag |
| Repo types | `dsm-hub`, `dsm-spoke`, `external` |
| Classification | Heuristic (BL-pattern → backlog-item, keyword match → protocol, default → section) |

### 1.7 Skeleton Entries (Lightweight)

| Property | Value |
|----------|-------|
| Source | `src/parser/markdown_parser.py:27-38` |
| Content | Heading, level, line number, end_line, number |
| Purpose | Quick structural overview without excerpt extraction |
| Note | Not persisted to graph; used for scanning and pre-filtering |

### 1.8 DSM_0.2 Module Entries (Specialized)

| Property | Value |
|----------|-------|
| Source | `src/analysis/section_index.py:17-43` |
| Types | `SectionEntry` (module, classification, section_id), `DispatchEntry` (protocol, trigger) |
| Module classification | "core" or "A"-"D" (on-demand modules) |

### Summary Table

| Artifact Type | Graph Element | ID Format | Persisted |
|---------------|--------------|-----------|-----------|
| Document (FILE) | Node | `file_path` | Yes |
| Numbered Section | Node | `file_path:number` | Yes |
| Appendix Section | Node | `file_path:A[.digits]` | Yes |
| Unnumbered Heading | Node | `file_path:h:slug` | Yes |
| Section/Appendix/DSM/Heading Ref | Edge (REFERENCES) | source → target | Yes |
| Entity (external inventory) | Node (RepoEntity) | Custom id | Yes (FalkorDB) |
| Skeleton | Internal only | — | No |
| DSM_0.2 Module Entry | Internal only | — | No |

---

## 2. Git Access Method

**Finding: Graph Explorer uses local git commands exclusively. No remote API calls.**

### 2.1 Implementation

| Property | Value |
|----------|-------|
| Source | `src/git_ref/git_resolver.py:17-36` |
| Method | `subprocess.run(["git", "-C", repo_path, ...])` |
| Timeout | 30 seconds per command |
| Libraries | Python `subprocess` (stdlib); no gitpython, no GitHub API |

### 2.2 Git Operations

| Operation | Command | Source |
|-----------|---------|--------|
| Repo root discovery | `git rev-parse --show-toplevel` | `git_resolver.py:39-55` |
| Ref resolution (SHA) | `git rev-parse --verify <ref>` | `git_resolver.py:58-76` |
| File listing at commit | `git ls-tree -r --name-only <sha>` | `git_resolver.py:79-106` |
| File content at commit | `git show <sha>:<filepath>` | `git_resolver.py:109-130` |

### 2.3 Implication for Private Projects

Since Graph Explorer accesses git via local subprocess commands (`git -C <path> ...`), it works identically for:
- Repositories with remote origins (Standard Spoke, External Contribution)
- Repositories with no remote (Private Project, local-only)

**No remote URL is required.** Graph Explorer reads the local `.git` directory. A Private Project's git history is fully accessible as long as Graph Explorer runs on the same filesystem.

---

## 3. Cross-Pattern Availability Matrix

Three DSM participation patterns (per DSM_3 Section 6):
- **Standard Spoke:** Remote GitHub tracking, full ecosystem participation
- **External Contribution:** Fork of upstream, governance artifacts in separate folder
- **Private Project:** Local-only git, data isolation, receive-only inbox

### 3.1 Artifact Availability by Pattern

| Artifact Type | Standard Spoke | External Contribution | Private Project |
|---------------|:-:|:-:|:-:|
| Markdown files (.md) | Yes (disk + git) | Yes (disk + git) | Yes (disk + git) |
| Numbered sections | Yes | Yes | Yes |
| Appendix sections | Yes | Yes | Yes |
| Unnumbered headings | Yes | Yes | Yes |
| Cross-references (Section/Appendix/DSM/Heading) | Yes | Yes | Yes |
| Entity inventory (YAML) | Yes | Yes | Yes (manual export) |
| Git-ref temporal (--git-ref) | Yes | Yes | Yes |
| Graph diff (--graph-diff) | Yes | Yes | Yes |
| FalkorDB persistence (--graph-db) | Yes | Yes | Yes |
| GraphML export (--graph-export) | Yes | Yes | Yes |
| Cross-repo comparison (--compare-repo) | Yes | Yes | Partial* |
| Cross-repo bridge (FalkorDB) | Yes | Yes | Partial* |
| Config (.dsm-graph-explorer.yml) | Yes | Yes | Yes |

*\*Partial:* Cross-repo features require entity inventories from other repos. A Private Project can consume inventories from other repos (read-only), but sharing its own inventory externally would require manual sanitization per the Private Project isolation rules.

### 3.2 Access Path by Pattern

| Access Path | Standard Spoke | External Contribution | Private Project |
|-------------|:-:|:-:|:-:|
| Filesystem (pathlib.Path) | Yes | Yes | Yes |
| Git subprocess (local .git) | Yes | Yes | Yes |
| GitHub API | Not used | Not used | Not used |
| Remote URL required | No | No | No |

### 3.3 Key Finding

Graph Explorer's architecture is **pattern-agnostic at the data access layer.** All three patterns use the same code paths (local filesystem + local git). The differences between patterns manifest only at the ecosystem integration level (inbox direction, feedback push), which is outside Graph Explorer's scope.

---

## 4. Protocol Elevation Check

For each graph-relevant artifact, checking whether the governing protocol is explicit in each pattern section of DSM_3.

### 4.1 Artifacts and Governing Protocols

| Graph-Relevant Artifact | Governing Protocol | Standard Spoke | External Contribution | Private Project |
|------------------------|-------------------|:-:|:-:|:-:|
| Markdown files (.md) | File naming conventions (DSM 2.0) | Explicit | Explicit | Explicit |
| Section numbering | Heading conventions (DSM 1.0 Section 2) | Explicit | Implicit | Implicit |
| Entity inventory YAML | Inventory protocol (DSM 4.0 Section 3) | Explicit | Not defined | Not defined |
| Cross-repo comparison | Drift detection protocol (DSM 4.0 Section 3) | Explicit | Not defined | Not defined |
| Config file (.dsm-graph-explorer.yml) | Tool-specific config (Graph Explorer docs) | Explicit | Implicit | Implicit |
| Graph database (FalkorDB) | Persistence protocol (DEC-006) | Project-specific | N/A | N/A |

### 4.2 Protocol Gaps Identified

1. **Entity inventory for External Contribution and Private Project:** The `dsm-entity-inventory.yml` protocol is defined for Standard Spoke projects. No explicit guidance exists for how External Contribution or Private Projects should produce or consume inventories.

2. **Section numbering in External Contribution:** When contributing to an upstream project, the upstream's heading conventions may not follow DSM numbering. No explicit protocol addresses how Graph Explorer should handle non-DSM-numbered headings in external repos. (Note: unnumbered heading indexing partially covers this, but the protocol is implicit.)

3. **Cross-repo comparison for Private Projects:** The comparison protocol assumes both repos can share inventories. For Private Projects, sharing an inventory may expose sensitive structural information. No sanitization protocol exists.

---

## 5. Summary of Findings

### What Graph Explorer Indexes (8 artifact types)
1. Document nodes (FILE)
2. Numbered section nodes (SECTION)
3. Appendix section nodes (SECTION)
4. Unnumbered heading nodes (SECTION)
5. Cross-reference edges (REFERENCES, 4 subtypes)
6. External entity inventory entries (RepoEntity)
7. Skeleton entries (internal, not persisted)
8. DSM_0.2 module entries (internal, not persisted)

### Git Access: Local Only
- All git access via `subprocess.run(["git", ...])`, no remote APIs
- Works identically for all three patterns, including local-only Private Projects
- No remote URL required

### Cross-Pattern Availability
- Core indexing features (parse, graph, export) available to all three patterns
- Cross-repo features available but with caveats for Private Projects (isolation rules)
- Architecture is pattern-agnostic at the data access layer

### Protocol Gaps (3 identified)
1. Entity inventory protocol undefined for External Contribution and Private Project patterns
2. Non-DSM heading conventions in external repos handled implicitly, not explicitly
3. No sanitization protocol for Private Project inventory sharing

---

## Success Criteria Checklist

- [x] All artifact types enumerated with source references
- [x] Cross-pattern availability matrix completed
- [x] Local-only git access method documented
- [x] Protocol gaps identified for elevation
- [ ] Findings sent to DSM Central (pending inbox notification)
