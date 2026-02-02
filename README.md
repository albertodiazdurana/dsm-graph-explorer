# DSM Graph Explorer

**Version:** 0.1.0 (Alpha)
**Status:** In Development — Sprint 3 In Progress

Repository integrity validator and graph database explorer for the DSM (Agentic AI Data Science Methodology) framework.

---

## Overview

DSM Graph Explorer is a tool designed to maintain integrity across large documentation repositories with complex cross-reference patterns. Built using the DSM 4.0 Software Engineering Adaptation, this project demonstrates dog-fooding a data science methodology to build software tooling.

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
│   ├── validator/        # Cross-reference and version validators (Sprint 2)
│   └── reporter/         # Report generator (Sprint 2)
├── tests/
│   ├── test_parser.py    # 52 unit tests for parser modules
│   ├── test_validator.py # 51 tests for validators
│   ├── test_reporter.py  # 23 tests for reporter + integration
│   ├── test_cli.py       # 19 tests for CLI
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

- Python 3.12+
- Git (for repository operations)
- Virtual environment (recommended)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/albertodiazdurana/dsm-graph-explorer.git
cd dsm-graph-explorer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

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

This project is built using the [Agentic AI Data Science Methodology](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology), specifically:

- **DSM 4.0:** Software Engineering Adaptation
- **Section 3:** Development Protocol (TDD approach)
- **Section 2:** Project Structure Patterns (in-repo docs/)
- **Section 2.5.6-2.5.8:** Blog as Standard Deliverable

For more details, see [SPRINT_PLAN.md](docs/plan/SPRINT_PLAN.md) in this repository.

---

## Project Status

### Completed
- [x] **Phase 0:** Environment Setup — repository, venv, pyproject.toml, docs structure
- [x] **Phase 0.5:** Research & Grounding — validated approach against published best practices ([research](docs/research/handoff_graph_explorer_research.md))
- [x] **Sprint 1:** Parser MVP — markdown parser, cross-reference extractor, 52 tests at 98% coverage ([DEC-001](docs/decisions/DEC-001_parser_library_choice.md))
- [x] **Sprint 2:** Validation Engine — cross-ref validator, version checker, report generator, 126 tests at 99% coverage

### In Progress
- [ ] **Sprint 3:** CLI & Real-World Run — CLI interface (implemented), real-world run pending, first DSM integrity report

### Up Next
- [ ] **Sprint 4:** Documentation & Publication — CI/CD, blog draft

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

**Last Updated:** 2026-02-02
**Current Sprint:** Sprint 3 In Progress — CLI & Real-World Run
**Tests:** 145 passed, 98% coverage
