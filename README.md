# DSM Graph Explorer

**Version:** 0.2.0
**Status:** Epoch 2 In Progress (Sprint 4 complete)

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

**Future (SHOULD scope):**
- Pre-commit hook integration
- CI/CD workflow (GitHub Actions)
- Semantic cross-reference validation — TF-IDF keyword similarity to detect meaning drift when sections are rewritten

**Future (COULD scope):**
- Neo4j graph database mapping DSM structure (prototype with NetworkX first)
- Cypher query library for navigation
- Web visualization using Neo4j Browser
- spaCy NER for advanced reference extraction
- Sentence transformer embeddings for deep semantic cross-reference alignment

---

## Project Structure

```
dsm-graph-explorer/
├── .claude/               # Claude configuration
├── src/
│   ├── parser/           # Markdown parser and cross-ref extractor
│   ├── validator/        # Cross-reference and version validators
│   ├── reporter/         # Report generator
│   ├── config/           # YAML config loader (Epoch 2)
│   └── filter/           # File exclusion logic (Epoch 2)
├── tests/
│   ├── test_parser.py    # Parser module tests
│   ├── test_validator.py # Validator tests
│   ├── test_reporter.py  # Reporter + integration tests
│   ├── test_cli.py       # CLI tests
│   ├── test_config.py    # Config loader tests (Epoch 2)
│   ├── test_filter.py    # File filter tests (Epoch 2)
│   └── fixtures/         # Test data (sample DSM markdown)
├── docs/
│   ├── plan/             # Sprint plan
│   ├── research/         # State-of-the-art review
│   ├── handoffs/         # Session handoffs
│   ├── decisions/        # Decision logs (DEC-001, ...)
│   ├── checkpoints/      # Sprint checkpoints
│   ├── blog/             # Blog materials and journal
│   └── feedback/          # Three-file DSM feedback system
├── outputs/reports/       # Generated integrity reports
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

For more details, see [epoch-1-plan.md](docs/plan/epoch-1-plan.md) (completed) and [epoch-2-plan.md](docs/plan/epoch-2-plan.md) (upcoming) in this repository.

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
- [ ] **Sprint 5:** CI Integration — GitHub Actions workflow, pre-commit hook, remediation docs *(next)*
- [ ] **Sprint 6:** Semantic Validation — TF-IDF similarity, drift detection ([research](docs/research/e2_handoff_graph_explorer_research.md))
- [ ] **Sprint 7:** Graph Prototype — NetworkX graph builder, queries, GraphML export

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

**Last Updated:** 2026-02-06
**Current Status:** Epoch 2 in progress (Sprint 4 complete, Sprint 5 next)
**Tests:** 218 passed, 95% coverage
**DSM Validation:** 10 errors (all reference non-existent Section 2.6), 0 warnings, 0 info
