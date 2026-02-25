# DSM Graph Explorer

**Version:** 0.2.0
**Status:** Epoch 2 In Progress (Sprint 6 complete, EXP-003b validated)

Repository integrity validator and graph database explorer for the [DSM (Agentic AI Data Science Methodology)](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology) framework.

---

## Overview

The [DSM framework](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology) is a structured methodology for human-AI collaboration in data science and software engineering projects. As the framework grows, its documentation accumulates hundreds of cross-references between sections, appendices, and versioned documents. Keeping these references consistent manually becomes error-prone.

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

**Next (Sprint 7 — Graph Prototype):**
- NetworkX graph builder mapping reference networks
- Graph queries: most-referenced sections, orphan sections, reference chains
- GraphML export for visualization in Gephi/yEd

**Future (Epoch 3+):**
- Neo4j graph database integration
- Cypher query library for navigation
- Web visualization using Neo4j Browser
- Convention linting mode (`--lint` flag) for DSM style checks
- spaCy NER for advanced reference extraction
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
│   └── semantic/         # TF-IDF similarity (Sprint 6)
├── tests/
│   ├── test_parser.py    # Parser module tests
│   ├── test_validator.py # Validator tests
│   ├── test_reporter.py  # Reporter + integration tests
│   ├── test_cli.py       # CLI tests
│   ├── test_cli_semantic.py # Semantic CLI integration tests
│   ├── test_config.py    # Config loader tests
│   ├── test_filter.py    # File filter tests
│   ├── test_semantic.py  # TF-IDF similarity tests
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

- Python 3.10+ (developed on 3.10, tested on 3.12)
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
```

**Note:** Development is done on Linux (WSL2). Python 3.10+ required.

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

This project is built using the [Agentic AI Data Science Methodology (DSM)](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology). The DSM provides structured guidance for human-AI collaborative projects, covering everything from sprint cadence to feedback tracking. This project follows:

- **DSM 4.0:** Software Engineering Adaptation — the track for building software with AI collaboration
- **Section 3:** Development Protocol — TDD approach with pre-generation briefs
- **Section 2:** Project Structure Patterns — in-repo `docs/` with checkpoints, decisions, and feedback
- **Section 2.5.6-2.5.8:** Blog as Standard Deliverable — capturing the development journey
- **Section 6.4-6.5:** Checkpoint, Feedback, and Gateway Reviews — systematic quality gates

The three-file feedback system (`docs/feedback/`) tracks methodology effectiveness as the project progresses, generating actionable improvements back into the DSM itself.

For more details, see [epoch-1-plan.md](docs/plans/epoch-1-plan.md) (completed) and [epoch-2-plan.md](docs/plans/epoch-2-plan.md) (in progress) in this repository.

---

## Project Status

### Epoch 1: Parser MVP & Validator (Complete)
- [x] **Phase 0:** Environment Setup — repository, venv, pyproject.toml, docs structure
- [x] **Phase 0.5:** Research & Grounding — validated approach against published best practices ([research](docs/research/e1_handoff_graph_explorer_research.md))
- [x] **Sprint 1:** Parser MVP — markdown parser, cross-reference extractor, 52 tests at 98% coverage ([DEC-001](docs/decisions/DEC-001_parser_library_choice.md))
- [x] **Sprint 2:** Validation Engine — cross-ref validator, version checker, report generator, 126 tests at 99% coverage
- [x] **Sprint 3:** CLI & Real-World Run — CLI interface, 150 tests at 98% coverage, first DSM integrity report (448 → 6 errors after trailing period fix)

### Epoch 2: Productionization & Graph (In Progress)
- [x] **Sprint 4:** Exclusion & Severity — `--exclude` flag, YAML config, Pydantic models, severity levels (218 tests, 95% coverage)
- [x] **Sprint 5:** CI Integration — GitHub Actions workflow, pre-commit hook, user guides (232 tests, 95% coverage)
- [x] **Sprint 6:** Semantic Validation — TF-IDF cosine similarity, `--semantic` flag, drift detection, EXP-003b real data validation (250 tests, 95% coverage)
  - Phase 6.0: EXP-003 threshold tuning → [DEC-005](docs/decisions/DEC-005-semantic-validation-approach.md) (threshold 0.10→0.08, min 3 tokens)
  - Phase 6.1: Parser context extraction (`Section.context_excerpt`, `CrossReference.context_before/after`)
  - Phase 6.2: TF-IDF implementation (`src/semantic/similarity.py`, corpus-scoped IDF)
  - Phase 6.3: CLI integration (`--semantic`, graceful fallback, Rich + markdown reports)
  - EXP-003b: 1,191 real cross-references validated, threshold amended to 0.08
- [ ] **Sprint 7:** Graph Prototype — NetworkX graph builder, queries, GraphML export
- [ ] **Sprint 8:** Convention Linting — `--lint` flag, 6 style checks

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

**Last Updated:** 2026-02-25
**Current Status:** Epoch 2 in progress (Sprint 6 complete, EXP-003b validated)
**Tests:** 250 passed, 95% coverage
**DSM Feedback:** 28 methodology entries, 23 improvement proposals
