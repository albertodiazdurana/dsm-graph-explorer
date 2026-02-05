@~/dsm-agentic-ai-data-science-methodology/DSM_Custom_Instructions_v1.1.md

# Project: DSM Graph Explorer

**Type:** Software Engineering (DSM 4.0 Track)
**Author:** Alberto Diaz Durana
**Domain:** Repository Integrity Validation / Graph Database Exploration

---

## Project Context

- **Purpose**: Python application for repository integrity validation and graph database exploration
- **DSM Track**: DSM 4.0 (Software Engineering Adaptation)
- **Key DSM Sections**: Section 3 (Development Protocol), Section 4 (Tests vs Capability Experiments)

## Technical Stack

- **Language**: Python 3.12+
- **Testing**: pytest (80%+ coverage target)
- **Dependencies**: See `pyproject.toml`

## Project Structure

```
dsm-graph-explorer/
├── .claude/              # AI agent configuration
├── src/                  # Application source code
├── tests/                # Test suite
├── docs/
│   ├── plan/
│   │   ├── epoch-1-plan.md  # Epoch 1 roadmap (complete)
│   │   └── epoch-2-plan.md  # Epoch 2 roadmap (next)
│   ├── decisions/           # Architecture Decision Records
│   ├── checkpoints/         # Milestone checkpoints
│   ├── handoffs/            # Session continuity notes
│   ├── backlog/             # DSM-to-project alignment reports
│   ├── feedback/            # Project-to-DSM feedback
│   └── blog/                # Blog materials and drafts
└── pyproject.toml
```

## Environment

- **Platform**: Linux (WSL2)
- **Project path**: `~/dsm-graph-explorer/`
- **DSM repository**: `~/dsm-agentic-ai-data-science-methodology/`

## Key References

- **DSM 4.0**: `DSM_4.0_Software_Engineering_Adaptation_v1.0.md` (primary)
- **DSM 1.0**: `DSM_1.0_Data_Science_Collaboration_Methodology_v1.1.md`
- **PM Guidelines**: `DSM_2.0_ProjectManagement_Guidelines_v2_v1.1.md`
- **Getting Started**: `DSM_0_START_HERE_Complete_Guide.md`

---

## Working Style

I always want to understand what we are doing. Before generating any file I want to read a brief explanation of what it is and why we need it. This should be the way in which we work: I need to have context to approve.

## Development Protocol

This project uses Claude Code to write files directly. User reviews in IDE.

**Collaboration workflow:** (1) Agent explains what and why, (2) Human reviews and approves, (3) Agent executes.

- Explain **what** and **why** before creating or modifying each file — describe the purpose, the specific changes, and how they fit the current task. Wait for approval before executing.
- For approval prompts, use `AskUserQuestion` tool with Yes/No options instead of plain text "Should I proceed?" questions.
- Write files directly using Claude Code tools
- Build modules incrementally — one module at a time, tests alongside
- Run `pytest tests/` after each module to verify before proceeding
- Keep changes focused: one logical unit per step

## Development Approach

- **TDD (Test-Driven Development)**: Write tests before implementation
- **Incremental development**: Build one function at a time, test, then next
- **Blog as deliverable**: Document journey throughout (Section 2.5.6-2.5.8)
- **Three-file feedback system**: Track DSM methodology effectiveness

## DSM Alignment

- Check `docs/backlog/` at session start for any DSM alignment reports
- Update `docs/feedback/` files (backlogs.md, methodology.md, blog.md) at sprint boundaries
- Follow the sprint boundary checklist: checkpoint, feedback files, decision log, blog entry

## Blog Integration

Following Section 2.5.6 (Blog/Communication Deliverable Process):
- **Materials**: `docs/blog/materials.md`
- **Journal**: `docs/blog/journal.md` (daily observations)
- **Steps**: Preparation → Scoping → Capture → Drafting → Review → Publication

## Punctuation
Use "," instead of "—" for connecting phrases in any language.
The comma (,) is a punctuation mark used to separate elements in a list, set off introductory phrases, clarify meaning, or indicate a pause in a sentence.
Semicolons (;) are used to connect closely related independent clauses—complete sentences that could stand alone—without using a coordinating conjunction like and or but.  They create a stronger pause than a comma but a softer break than a period. 
Colon (:) is a punctuation mark used to introduce a list, explanation, quotation, or elaboration.  It appears after a complete independent clause to signal that what follows will clarify, expand on, or list related information.