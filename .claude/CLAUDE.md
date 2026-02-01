# DSM Graph Explorer - Claude Configuration

This project follows the **Data Science Methodology (DSM)** framework.

## Central DSM Location

The full DSM documentation is maintained in the central repository:
`D:\data-science\agentic-ai-data-science-methodology\`

## Key DSM Documents

- **DSM 4.0**: `DSM_4.0_Software_Engineering_Adaptation_v1.0.md` (primary guidance for this project)
- **DSM 1.0**: `DSM_1.0_Data_Science_Collaboration_Methodology_v1.1.md`
- **DSM Appendices**: `DSM_1.0_Methodology_Appendices.md`
- **PM Guidelines**: `DSM_2.0_ProjectManagement_Guidelines_v2_v1.1.md`
- **Getting Started**: `DSM_0_START_HERE_Complete_Guide.md`

## Project Type

**Software Engineering** (DSM 4.0 Track)

This is a Python application for repository integrity validation and graph database exploration. Follow DSM 4.0 Section 3 (Development Protocol) and Section 4 (Tests vs Capability Experiments).

## Project Structure Pattern

This project uses the **DSM 4.0 Pattern** (in-repo `docs/` folder):
- Handoffs: `docs/handoffs/`
- Decisions: `docs/decisions/`
- Checkpoints: `docs/checkpoints/`
- Blog materials: `docs/blog/`
- Feedback: `docs/feedback/`

Reference: DSM 4.0 Section 2 (Project Structure Patterns)

## Collaboration Protocol

**Pre-generation brief (MANDATORY):** Before creating or modifying any file, provide a brief explanation of: (1) what the file is, (2) why it's needed, (3) what it will contain at a high level. Wait for user acknowledgment before proceeding. The user needs context to approve — never generate artifacts without explanation first.

## Development Approach

- **TDD (Test-Driven Development)**: Write tests before implementation
- **Incremental development**: Build one function at a time, test, then next
- **Blog as deliverable**: Document journey throughout (Section 2.5.6-2.5.8)
- **Three-file feedback system**: Track DSM methodology effectiveness

## Quick Reference

### Testing
- Framework: pytest
- Coverage target: 80%+ for MVP
- Location: `tests/`

### Dependencies
- Python: 3.12+
- See `pyproject.toml` for full dependency list

### Key Sections
- Section 3: Development Protocol (DSM 4.0)
- Section 4.4: Tests vs Capability Experiments (DSM 4.0)
- Section 2.5.6-2.5.8: Blog/Communication Process
- Section 6.4: Checkpoint and Feedback Protocol

## Blog Integration

Following Section 2.5.6 (Blog/Communication Deliverable Process):
- **Materials**: `docs/blog/materials.md` (prepared)
- **Journal**: `docs/blog/journal.md` (daily observations)
- **Steps**: Preparation → Scoping → Capture → Drafting → Review → Publication

## Project Plan

Sprint plan: `docs/plan/SPRINT_PLAN.md`

## Author

**Alberto Diaz Durana**
[GitHub](https://github.com/albertodiazdurana) | [LinkedIn](https://www.linkedin.com/in/albertodiazdurana/)
