# DSM Graph Explorer

**Version:** 0.4.0
**Status:** Epoch 4 in progress (Sprint 13 complete)

Repository integrity validator and graph database explorer for the [DSM (Agentic AI Data Science Methodology)](https://github.com/albertodiazdurana/take-ai-bite) framework.

---

## Overview

The [DSM framework](https://github.com/albertodiazdurana/take-ai-bite) is a structured methodology for human-AI collaboration in data science and software engineering projects. As the framework grows, its documentation accumulates hundreds of cross-references between sections, appendices, and versioned documents. Keeping these references consistent manually becomes error-prone.

DSM Graph Explorer automates this integrity checking: it parses DSM markdown files, extracts cross-references, validates them against actual section headings, and reports broken links and version mismatches. The project itself is built using DSM 4.0 (Software Engineering Adaptation), making it a dog-fooding exercise — using the methodology to build tooling that validates the methodology.

### Features

**Implemented (Sprint 1 — Parser MVP):**
- Markdown parser — extracts section headings with hierarchical numbering (1.2.3), appendix sections (A.1.2), and unnumbered headings
- Cross-reference extractor — finds `Section X.Y.Z`, `Appendix X.Y`, and `DSM_X.Y` patterns in prose text
- Code block awareness — skips references inside fenced code blocks to avoid false positives
- Line number tracking — precise location for every section and cross-reference

**Implemented (Sprint 2 — Validation Engine):**
- Cross-reference validator — checks that referenced sections exist across multiple files, with severity levels (ERROR for broken refs, WARNING for unknown DSM docs)
- Version consistency checker — extracts version patterns from files and flags mismatches
- Integrity report generator — both markdown file reports and Rich console output

**Implemented (Sprint 3 — CLI):**
- CLI interface (`dsm-validate`) — accepts files or directories, recursive scanning, `--strict` for CI, `--output` for saved reports

**Implemented (Sprint 4 — Exclusion & Severity):**
- YAML configuration file (`.dsm-graph-explorer.yml`) with Pydantic validation
- File exclusion patterns (`--exclude` flag, repeatable, supports fnmatch globs)
- Severity levels (ERROR/WARNING/INFO) with config-based overrides by file pattern
- `--strict` respects severity (only fails on ERROR)
- Config file discovery (walks up directory tree)

**Implemented (Sprint 5 — CI & Documentation):**
- GitHub Actions workflow (`.github/workflows/dsm-validate.yml`) for automated validation on push/PR
- Pre-commit hook (`scripts/pre-commit-hook.sh`) for local validation of staged markdown files
- User guides: [remediation guide](docs/guides/remediation-guide.md) and [config reference](docs/guides/config-reference.md)
- Cross-repo reference handling: spoke repositories that reference DSM sections defined elsewhere can set those files to INFO severity, keeping findings visible without blocking CI (see [config reference](docs/guides/config-reference.md))

**Implemented (Sprint 6 — Semantic Validation):**
- TF-IDF cosine similarity for detecting semantic drift in cross-references (`--semantic` flag)
- Context extraction: section excerpts (~50 words) and cross-reference context windows (3 lines before/after)
- Corpus-scoped IDF weighting across all sections for proper vocabulary downweighting
- Minimum token gate (3 tokens after stopword removal) to flag insufficient context rather than producing unreliable scores
- Section number stripping before vectorization to avoid artificial similarity inflation
- Configurable threshold (default 0.08, per [DEC-005](docs/decisions/DEC-005-semantic-validation-approach.md)) and min tokens via `.dsm-graph-explorer.yml`
- Graceful fallback: `--semantic` without scikit-learn prints a clear error and exits with code 2
- Rich console output with drift warning (yellow) and insufficient context (dim) tables
- EXP-003b real data validation: 1,191 cross-references analyzed, 128 labeled, threshold amended to 0.08 (Precision=1.000, Recall=0.496→recovered at 0.08)

**Implemented (Sprint 7 — Graph Prototype):**
- NetworkX graph builder mapping reference networks (FILE and SECTION nodes, CONTAINS and REFERENCES edges)
- Graph queries: most-referenced sections, orphan sections, reference chains
- GraphML export (`--graph-export PATH`) for visualization in Gephi/yEd
- Graph statistics summary (`--graph-stats`) showing node/edge counts and top-referenced sections
- Graceful fallback: `--graph-export`/`--graph-stats` without networkx prints a clear error and exits with code 2
- EXP-004 performance validation: 104ms build, 12.7MB memory on DSM repository (all 5 targets PASS)

**Implemented (Sprint 8 — Convention Linting):**
- Convention linting mode (`--lint` flag), independent from validation pipeline
- 6 checks: emoji usage (E001), TOC headings (E002), mojibake encoding (E003), em-dash punctuation (W001), CRLF line endings (W002), backlog metadata (W003)
- Configurable severity overrides per rule via `lint:` section in `.dsm-graph-explorer.yml`
- Rich console output and markdown report (`--lint -o report.md`)
- `--strict` support: exit code 1 if any ERROR-level lint findings

**Implemented (Sprint 9 — FalkorDBLite Integration):**
- FalkorDBLite persistence layer (`--graph-db PATH`) for storing reference graphs to disk
- Cache-aware rebuilds: skip persistence if graph already exists, force with `--rebuild`
- GraphStore API: write_graph, graph_exists, ro_query, Cypher query wrappers
- Schema: Document and Section nodes with CONTAINS and REFERENCES edges, git_ref on all nodes
- Python 3.12+ upgrade (DEC-007) to support FalkorDBLite dependency
- EXP-005: 16/16 FalkorDB API validation checks passed
- Graceful fallback: `--graph-db` without falkordblite prints a clear error and exits with code 2

**Implemented (Sprint 10 — Git-Ref Temporal Compilation):**
- Git-ref resolver (`--git-ref REF`) for validating and building graphs at any historical commit
- Content-based parser variants for parsing git-ref content without temporary files
- Subdirectory-safe repo root resolution (`find_repo_root()`)
- Graph diff engine (`--graph-diff REF_A REF_B`) comparing reference graphs across two commits
- Rich console output for structural diff (added/removed/modified nodes and edges)
- EXP-006: 19/19 git-ref temporal accuracy checks passed

**Implemented (Sprint 11 — Entity Inventory):**
- Entity inventory spec (`dsm-entity-inventory.yml`) with Pydantic models (Entity, RepoInfo, EntityInventory)
- Inventory parser: `load_inventory()`, `discover_inventory()` for automatic detection
- Cross-repo reference resolution via `--inventory PATH` (external repo inventories)
- EXTERNAL classification for references resolved via inventory (distinct from UNKNOWN)
- Inventory export (`--export-inventory PATH`) with type heuristics for sections, protocols, and backlog items

**Implemented (Sprint 12 — Cross-Repo Edges + BL-156):**
- Cross-repo bridge graph (`CrossRepoBridge`) with typed edges: INBOX_NOTIFICATION, AT_IMPORT, ECOSYSTEM_LINK, MAPS_TO
- Three-pass entity matching algorithm: exact ID → heading → TF-IDF fuzzy (reuses Sprint 6 threshold)
- Repo comparison (`--compare-repo INV_A INV_B`) showing match types: IDENTICAL, RENAMED, MODIFIED, ADDED, REMOVED
- Drift detection (`--drift-report`) filtering to diverged sections between private and public repos
- BL-156 fulfilled: private-to-public DSM repository mapping with drift tracking

**Implemented (Sprint 13 — BL-090 Resilience + Heading-Based Sections):**
- EXP-007: Multi-file document resilience validated against real DSM_0.2 modular split (BL-090)
- Heading-based section detection: graph builder creates SECTION nodes for all markdown headings, not just numbered sections
- Architecture audit (BL-170): confirmed 100% Private Project compatibility (all I/O local)
- DEC-008: heading-based section node IDs (`h:slug` format)

**Future (Epoch 4 remaining):**
- Cross-reference resolution by heading title matching (NLP/TF-IDF)
- Incremental graph updates (skip unchanged files)
- FalkorDB index creation and export
- Protocol usage frequency analysis
- LLM second-pass: tiered approach where TF-IDF filters, LLM confirms borderline cases

---

## Project Structure

```
dsm-graph-explorer/
├── .claude/               # Claude configuration
├── .github/workflows/     # CI workflow (dsm-validate.yml)
├── scripts/               # Pre-commit hook
├── src/
│   ├── parser/           # Markdown parser and cross-ref extractor
│   ├── validator/        # Cross-reference and version validators
│   ├── reporter/         # Report generator (Rich + markdown)
│   ├── config/           # YAML config loader
│   ├── filter/           # File exclusion logic
│   ├── semantic/         # TF-IDF similarity (Sprint 6)
│   ├── graph/            # Graph builder, queries, export, diff (Sprint 7, 10)
│   ├── git_ref/          # Git-ref resolver for temporal compilation (Sprint 10)
│   ├── inventory/        # Entity inventory parser and export (Sprint 11)
│   └── linter/           # Convention linting checks (Sprint 8)
├── tests/
│   ├── test_parser.py    # Parser module tests
│   ├── test_validator.py # Validator tests
│   ├── test_reporter.py  # Reporter + integration tests
│   ├── test_cli.py       # CLI tests
│   ├── test_cli_semantic.py # Semantic CLI integration tests
│   ├── test_cli_graph.py    # Graph CLI integration tests
│   ├── test_cli_graph_db.py # Graph DB CLI integration tests
│   ├── test_config.py       # Config loader tests
│   ├── test_filter.py    # File filter tests
│   ├── test_semantic.py  # TF-IDF similarity tests
│   ├── test_graph.py        # Graph builder and query tests
│   ├── test_graph_store.py  # FalkorDBLite persistence tests
│   ├── test_graph_diff.py   # Graph diff tests
│   ├── test_git_resolver.py # Git-ref resolver tests
│   ├── test_cli_git_ref.py  # Git-ref CLI integration tests
│   ├── test_inventory.py      # Entity inventory tests
│   ├── test_cross_repo.py     # Cross-repo bridge graph tests
│   ├── test_repo_diff.py      # Repo comparison tests
│   ├── test_cli_compare.py    # Cross-repo CLI integration tests
│   ├── test_linter.py       # Convention linting tests
│   ├── test_heading_sections.py # Heading-based section tests
│   └── fixtures/         # Test data (sample DSM markdown)
├── data/experiments/      # Capability experiments (EXP-xxx)
├── _inbox/               # Hub-spoke communication
├── docs/
│   ├── plans/            # Sprint and epoch plans
│   ├── research/         # State-of-the-art review
│   ├── decisions/        # Decision logs (DEC-001, ...)
│   ├── checkpoints/      # Sprint checkpoints
│   ├── blog/             # Blog materials and journal
│   ├── feedback/         # Three-file DSM feedback system
│   └── guides/           # User-facing docs (remediation, config reference)
├── outputs/reports/       # Generated integrity reports
├── .dsm-graph-explorer.yml # Validation config
├── pyproject.toml         # Project configuration
└── README.md
```

---

## Requirements

- Python 3.12+ (required for FalkorDBLite support)
- Git (for repository operations)
- Linux/WSL2 (recommended) or macOS/Windows

---

## Installation

```bash
# Clone the repository
git clone https://github.com/albertodiazdurana/dsm-graph-explorer.git
cd dsm-graph-explorer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Optional: install semantic validation support
pip install -e ".[dev,semantic]"

# Optional: install graph database support (networkx + falkordblite)
pip install -e ".[dev,graph]"

# Install everything
pip install -e ".[dev,all]"
```

**Note:** Development is done on Linux (WSL2). Python 3.12+ required.

---

## Usage

```bash
# Validate all markdown files in a directory
dsm-validate /path/to/dsm-repo

# Validate specific files
dsm-validate docs/DSM_1.0.md docs/DSM_4.0.md

# Save a markdown report
dsm-validate /path/to/dsm-repo --output report.md

# Strict mode for CI (exit code 1 if errors found)
dsm-validate /path/to/dsm-repo --strict

# Exclude files by pattern (repeatable)
dsm-validate /path/to/dsm-repo --exclude 'plan/*' --exclude 'CHANGELOG.md'

# Use a config file
dsm-validate /path/to/dsm-repo --config .dsm-graph-explorer.yml

# Check version consistency across files
dsm-validate docs/ --version-files DSM_0.md --version-files README.md

# Custom glob pattern
dsm-validate /path/to/repo --glob "docs/**/*.md"

# Semantic drift detection (requires scikit-learn)
dsm-validate /path/to/dsm-repo --semantic

# Graph statistics (requires networkx)
dsm-validate /path/to/dsm-repo --graph-stats

# Export reference graph to GraphML (for Gephi/yEd visualization)
dsm-validate /path/to/dsm-repo --graph-export graph.graphml

# Convention linting (emoji, TOC, mojibake, em-dash, CRLF, backlog metadata)
dsm-validate /path/to/dsm-repo --lint

# Lint with strict mode and markdown output
dsm-validate /path/to/dsm-repo --lint --strict --output lint-report.md

# Persist reference graph to FalkorDBLite (requires falkordblite)
dsm-validate /path/to/dsm-repo --graph-db /path/to/db.falkordb

# Force rebuild of cached graph
dsm-validate /path/to/dsm-repo --graph-db /path/to/db.falkordb --rebuild

# Validate at a historical git ref (commit, tag, branch)
dsm-validate /path/to/dsm-repo --git-ref v1.0

# Compare reference graphs between two git refs
dsm-validate /path/to/dsm-repo --graph-diff main feature-branch

# Compare two repo inventories (cross-repo entity matching)
dsm-validate --compare-repo inventory-a.yml inventory-b.yml

# Drift report (show diverged sections between repos)
dsm-validate --compare-repo inventory-a.yml inventory-b.yml --drift-report

# Combine semantic with other options
dsm-validate /path/to/dsm-repo --semantic --strict --output report.md
```

---

## Development

This project follows the DSM 4.0 Software Engineering Adaptation methodology.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

---

## Methodology

This project is built using the [Agentic AI Data Science Methodology (DSM)](https://github.com/albertodiazdurana/take-ai-bite). The DSM provides structured guidance for human-AI collaborative projects, covering everything from sprint cadence to feedback tracking. This project follows:

- **DSM 4.0:** Software Engineering Adaptation — the track for building software with AI collaboration
- **Section 3:** Development Protocol — TDD approach with pre-generation briefs
- **Section 2:** Project Structure Patterns — in-repo `docs/` with checkpoints, decisions, and feedback
- **Section 2.5.6-2.5.8:** Blog as Standard Deliverable — capturing the development journey
- **Section 6.4-6.5:** Checkpoint, Feedback, and Gateway Reviews — systematic quality gates

The three-file feedback system (`docs/feedback/`) tracks methodology effectiveness as the project progresses, generating actionable improvements back into the DSM itself.

For more details, see [epoch-1-plan.md](docs/plans/epoch-1-plan.md) (complete), [epoch-2-plan.md](docs/plans/epoch-2-plan.md) (complete), [epoch-3-plan.md](docs/plans/epoch-3-plan.md) (complete), and [epoch-4-plan.md](docs/plans/epoch-4-plan.md) (in progress) in this repository.

---

## Project Status

### Epoch 1: Parser MVP & Validator (Complete)
- [x] **Phase 0:** Environment Setup — repository, venv, pyproject.toml, docs structure
- [x] **Phase 0.5:** Research & Grounding — validated approach against published best practices ([research](docs/research/e1_handoff_graph_explorer_research.md))
- [x] **Sprint 1:** Parser MVP — markdown parser, cross-reference extractor, 52 tests at 98% coverage ([DEC-001](docs/decisions/DEC-001_parser_library_choice.md))
- [x] **Sprint 2:** Validation Engine — cross-ref validator, version checker, report generator, 126 tests at 99% coverage
- [x] **Sprint 3:** CLI & Real-World Run — CLI interface, 150 tests at 98% coverage, first DSM integrity report (448 → 6 errors after trailing period fix)

### Epoch 2: Productionization & Graph (Complete)
- [x] **Sprint 4:** Exclusion & Severity — `--exclude` flag, YAML config, Pydantic models, severity levels (218 tests, 95% coverage)
- [x] **Sprint 5:** CI Integration — GitHub Actions workflow, pre-commit hook, user guides (232 tests, 95% coverage)
- [x] **Sprint 6:** Semantic Validation — TF-IDF cosine similarity, `--semantic` flag, drift detection, EXP-003b real data validation (250 tests, 95% coverage)
  - Phase 6.0: EXP-003 threshold tuning → [DEC-005](docs/decisions/DEC-005-semantic-validation-approach.md) (threshold 0.10→0.08, min 3 tokens)
  - Phase 6.1: Parser context extraction (`Section.context_excerpt`, `CrossReference.context_before/after`)
  - Phase 6.2: TF-IDF implementation (`src/semantic/similarity.py`, corpus-scoped IDF)
  - Phase 6.3: CLI integration (`--semantic`, graceful fallback, Rich + markdown reports)
  - EXP-003b: 1,191 real cross-references validated, threshold amended to 0.08
- [x] **Sprint 7:** Graph Prototype — NetworkX graph builder, queries, GraphML export (284 tests, 95% coverage)
  - Phase 7.0: EXP-004 graph performance (all 5 targets PASS: 104ms build, 12.7MB memory)
  - Phase 7.1: Graph construction (`src/graph/graph_builder.py`, FILE/SECTION nodes, CONTAINS/REFERENCES edges)
  - Phase 7.2: Graph queries (`src/graph/graph_queries.py`, most-referenced, orphans, reference chains)
  - Phase 7.3: Export & CLI (`--graph-export`, `--graph-stats`, GraphML format, graceful fallback)
- [x] **Sprint 8:** Convention Linting — `--lint` flag, 6 style checks (331 tests, 96% coverage)
  - `src/linter/checks.py`: 6 checks (E001-E003, W001-W003) + `run_all_checks` orchestrator
  - `src/linter/lint_reporter.py`: Rich console + markdown report output
  - CLI `--lint` flag, config `lint:` section with per-rule severity overrides

### Epoch 3: Graph Database Integration (Complete)
- [x] **Sprint 9:** FalkorDBLite Integration — Python 3.12 upgrade, GraphStore persistence layer, `--graph-db`/`--rebuild` CLI flags, EXP-005 validation (355 tests, 96% coverage)
  - Phase 9.0: Python 3.12 upgrade (DEC-007)
  - Phase 9.1: EXP-005 FalkorDBLite API validation (16/16 checks)
  - Phase 9.2: `src/graph/graph_store.py` persistence layer (18 tests)
  - Phase 9.3: CLI `--graph-db` integration (6 tests)
- [x] **Sprint 10:** Git-Ref Temporal Compilation — `git_resolver.py`, content-based parsers, `--git-ref`, `graph_diff.py`, `--graph-diff`, EXP-006 (402 tests, 95% coverage)
  - Phase 10.0: EXP-006 git-ref temporal accuracy (19/19 checks)
  - Phase 10.1: `src/git_ref/git_resolver.py` + content-based parser variants (35 tests)
  - Phase 10.2: `src/graph/graph_diff.py` + CLI `--graph-diff` (12 tests)
- [x] **Sprint 11:** Entity Inventory — Pydantic models, `--inventory` for cross-repo resolution, `--export-inventory` for manifest generation, EXTERNAL classification (471 tests, 95% coverage)
  - Phase 11.1: Inventory spec and parser (`src/inventory/inventory_parser.py`, Pydantic models, 33 tests)
  - Phase 11.2: Cross-repo reference resolution (`--inventory PATH`, EXTERNAL classification, 17 tests)
  - Phase 11.3: Inventory export (`--export-inventory PATH`, type heuristics, 19 tests)
- [x] **Sprint 12:** Cross-Repo Edges + BL-156 — `CrossRepoBridge`, three-pass entity matching, `--compare-repo`, `--drift-report`, BL-156 complete (513 tests, 95% coverage)
  - Phase 12.1: `src/graph/cross_repo.py` (CrossRepoBridge, EdgeType, 19 tests)
  - Phase 12.2: `src/graph/repo_diff.py` (compare_inventories, three-pass matching, 13 tests)
  - Phase 12.3: CLI `--compare-repo INV_A INV_B`, `--drift-report` (10 tests)

### Epoch 4: Resilience & Ecosystem Analysis (In Progress)
- [x] **Sprint 13:** BL-090 Resilience + Heading-Based Sections — EXP-007 multi-file validation, heading-based section detection, BL-170 architecture audit, DEC-008 (531 tests, 95% coverage)
  - Phase 13.0: EXP-007 multi-file document resilience (real DSM_0.2 split data)
  - Phase 13.1: BL-042 heading-based section detection in graph builder (18 new tests)
  - BL-170 Part B: architecture audit (100% Private Project compatibility)
- [ ] **Sprint 14:** Performance & Completeness (carry-forward SHOULDs)
- [ ] **Sprint 15:** Protocol Usage Analysis
- [ ] **Sprint 16:** Reserved

---

## Contributing

This project is currently in active development. Contribution guidelines will be added after Phase 1 MVP completion.

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Author

**Alberto Diaz Durana**
[GitHub](https://github.com/albertodiazdurana) | [LinkedIn](https://www.linkedin.com/in/albertodiazdurana/)

---

## Acknowledgments

Built as a dog-fooding project to validate and improve the DSM methodology framework. This project demonstrates applying data science methodology principles to software engineering tasks.

---

## Blog

- [Validating 7,400 Lines of Documentation with Compiler Architecture](https://www.linkedin.com/posts/albertodiazdurana_technicalwriting-docsascode-documentation-activity-7425203346304835585-9fZJ) — How compiler architecture (parser → symbol table → resolver → reporter) applies to documentation validation.

---

**Last Updated:** 2026-03-16
**Current Status:** Epoch 4 in progress (Sprint 13 complete: BL-090 resilience + heading-based sections)
**Tests:** 531 passed, 95% coverage
**DSM Feedback:** 47 methodology entries, 42 improvement proposals
