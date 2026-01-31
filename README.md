# DSM Graph Explorer

**Version:** 0.1.0 (Alpha)
**Status:** In Development - Phase 0 Complete

Repository integrity validator and graph database explorer for the DSM (Agentic AI Data Science Methodology) framework.

---

## Overview

DSM Graph Explorer is a tool designed to maintain integrity across large documentation repositories with complex cross-reference patterns. Built using the DSM 4.0 Software Engineering Adaptation, this project demonstrates dog-fooding a data science methodology to build software tooling.

### Features (Planned)

**Phase 1: Integrity Validator** (In Progress)
- Cross-reference validation (Section X.Y.Z, Appendix X.Y, DSM_X patterns)
- Version consistency checking across multiple files
- DSM_0 alignment verification
- Integrity report generation (markdown format)
- CLI interface for running validation
- Pre-commit hook integration

**Phase 2: Graph Explorer** (Future)
- Neo4j graph database mapping DSM structure
- Cypher query library for navigation
- Web visualization using Neo4j Browser
- Relationship mapping (REFERENCES, CONTAINS, PARENT_OF)

---

## Project Structure

```
dsm-graph-explorer/
├── .claude/               # Claude configuration
├── src/                   # Source code
│   ├── parser/           # Markdown parser and cross-ref extractor
│   ├── validator/        # Cross-reference and version validators
│   └── reporter/         # Report generator
├── tests/                # Test suite (pytest)
│   └── fixtures/         # Test data
├── docs/                 # Project documentation (DSM 4.0 pattern)
│   ├── handoffs/         # Session handoffs
│   ├── decisions/        # Decision logs
│   ├── checkpoints/      # Project checkpoints
│   ├── blog/            # Blog materials and journal
│   ├── dsm-feedback-backlogs.md
│   ├── dsm-feedback-methodology.md
│   └── dsm-feedback-blog.md
├── outputs/              # Generated reports
│   └── reports/
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

---

## Requirements

- Python 3.12+
- Git (for repository operations)
- Virtual environment (recommended)

---

## Installation

**NOTE: Project is in Phase 0 (Environment Setup). Installation instructions will be finalized in Phase 4.**

```bash
# Clone the repository
git clone <repository-url>
cd dsm-graph-explorer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
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

For more details, see the [project plan](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology/blob/main/plan/DSM_Graph_Explorer_Sprint1_Plan.md).

---

## Project Status

### Completed
- [x] Phase 0: Environment Setup
  - [x] Repository structure
  - [x] Virtual environment
  - [x] Project configuration (pyproject.toml)
  - [x] Git initialization
  - [x] Blog materials and journal templates
  - [x] Three-file feedback system
  - [x] Handoff document created

**Handoff available:** [docs/handoffs/2026-01-31_phase0-complete_handoff.md](docs/handoffs/2026-01-31_phase0-complete_handoff.md)

### In Progress
- [ ] Phase 1: Data Pipeline (Parser Development)

### Planned
- [ ] Phase 2: Core Modules (Validation & Reporting)
- [ ] Phase 3: Integration & Evaluation
- [ ] Phase 4: Documentation & Blog

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

**Last Updated:** 2026-01-31
**Current Phase:** Phase 0 - Environment Setup Complete
