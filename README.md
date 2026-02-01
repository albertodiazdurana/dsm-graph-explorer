# DSM Graph Explorer

**Version:** 0.1.0 (Alpha)
**Status:** In Development - Sprint 1 Complete

Repository integrity validator and graph database explorer for the DSM (Agentic AI Data Science Methodology) framework.

---

## Overview

DSM Graph Explorer is a tool designed to maintain integrity across large documentation repositories with complex cross-reference patterns. Built using the DSM 4.0 Software Engineering Adaptation, this project demonstrates dog-fooding a data science methodology to build software tooling.

### Features

**Implemented (Sprint 1):**
- Markdown parser — extracts section headings with hierarchical numbering (1.2.3), appendix sections (A.1.2), and unnumbered headings
- Cross-reference extractor — finds `Section X.Y.Z`, `Appendix X.Y`, and `DSM_X.Y` patterns in prose text
- Code block awareness — skips references inside fenced code blocks to avoid false positives
- Line number tracking — precise location for every section and cross-reference

**In Progress (Sprint 2–3):**
- Cross-reference validator — checks that referenced sections actually exist
- Version consistency checker — validates version numbers match across DSM_0, README, CHANGELOG
- Integrity report generator — markdown format
- CLI interface for running validation

**Future (COULD scope):**
- Neo4j graph database mapping DSM structure (prototype with NetworkX first)
- Cypher query library for navigation
- Web visualization using Neo4j Browser
- spaCy NER for advanced reference extraction

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

**NOTE: CLI implementation is planned for Phase 3.**

Planned usage:
```bash
# Validate DSM repository integrity
dsm-validate /path/to/dsm-repo

# Generate integrity report
dsm-validate /path/to/dsm-repo --output report.md

# Run with verbose output
dsm-validate /path/to/dsm-repo --verbose
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

### Up Next
- [ ] **Sprint 2:** Validation Engine — cross-ref validator, version checker, report generator
- [ ] **Sprint 3:** CLI & Real-World Run — CLI interface, integration tests, first DSM integrity report
- [ ] **Sprint 4:** Documentation & Publication — README finalization, CI/CD, blog draft

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

**Last Updated:** 2026-02-01
**Current Sprint:** Sprint 1 Complete — Parser MVP
