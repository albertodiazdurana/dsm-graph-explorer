@~/dsm-agentic-ai-data-science-methodology/DSM_0.2_Custom_Instructions_v1.1.md

<!-- BEGIN DSM_0.2 ALIGNMENT - do not edit manually, managed by /dsm-align -->
## DSM Alignment (managed by /dsm-align)

**Project type:** Application (DSM 4.0)
**Participation pattern:** Spoke

### Session Transcript Protocol (reinforces inherited protocol)
- Append thinking to `.claude/session-transcript.md` BEFORE acting
- Output summary AFTER completing work
- Conversation text = results only
- Use Session Transcript Delimiter Format for every block:
  <------------Start Thinking / HH:MM------------>
  <------------Start Output / HH:MM------------>
  <------------Start User / HH:MM------------>
- HH:MM is 24-hour local time when the block begins; no end delimiter needed
- Append technique: read last 3 lines, use last non-empty line as anchor.
  NEVER match earlier content for mid-file insertion.

### Pre-Generation Brief Protocol (reinforces inherited protocol)
- Three-gate model: concept (explain) → implementation (diff review) → run (when applicable)
- Each gate requires explicit user approval; gates are independent

### Inbox Lifecycle (reinforces inherited protocol)
- After processing an inbox entry, move it to `_inbox/done/`
- Do not mark entries as "Status: Processed" while keeping them in place

### Punctuation
Use "," instead of "—" for connecting phrases in any language.

### App Development Protocol (reinforces inherited protocol)
- Explain why before each action
- Create files via Write/Edit tools; user approves via permission window
- Wait for user confirmation before proceeding to next step
- Build incrementally: imports → constants → one function → test → next function
<!-- END DSM_0.2 ALIGNMENT -->

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
├── .claude/                 # AI agent configuration
├── _inbox/                  # Hub-spoke communication transit
│   └── done/
├── src/                     # Application source code
├── tests/                   # Test suite
├── data/experiments/        # Capability experiment outputs
├── docs/
│   ├── plans/               # Epoch roadmaps, backlog items
│   ├── decisions/           # Architecture Decision Records
│   ├── checkpoints/         # Milestone snapshots
│   ├── handoffs/            # Session continuity notes
│   ├── feedback/            # Per-session DSM feedback files
│   ├── research/            # Phase 0.5 research files
│   ├── guides/              # User-facing documentation
│   └── blog/                # Blog materials and drafts (per epoch)
├── scripts/                 # Utility scripts
└── pyproject.toml
```

## Environment

- **Platform**: Linux (WSL2)
- **Project path**: `~/dsm-graph-explorer/`
- **DSM repository**: `~/dsm-agentic-ai-data-science-methodology/`
- **Portfolio**: `~/dsm-data-science-portfolio-working-folder/`

---

## Working Style

I always want to understand what we are doing. Before generating any file I want to read a brief explanation of what it is and why we need it. This should be the way in which we work: I need to have context to approve.

## Development Protocol

- Do NOT use `AskUserQuestion` for approvals (modal blocks IDE reading). Plain text approvals only.
- Build modules incrementally, one module at a time, tests alongside
- Run `pytest tests/` after each module to verify before proceeding
- Keep changes focused: one logical unit per step

## Development Approach

- **TDD (Test-Driven Development)**: Write tests before implementation
- **Incremental development**: Build one function at a time, test, then next
- **Blog as deliverable**: Document journey throughout (Section 2.5.6-2.5.8)

## DSM Alignment

- Check `_inbox/` at session start for hub-spoke communication
- At sprint boundaries, follow the Sprint Boundary Checklist:
  - [ ] Checkpoint document created (`docs/checkpoints/`)
  - [ ] Per-session feedback files written (`docs/feedback/YYYY-MM-DD_sN_*.md`)
  - [ ] Decision log updated with sprint decisions (`docs/decisions/`)
  - [ ] Blog journal entry written (`docs/blog/<epoch>/journal.md`)
  - [ ] Repository README updated (status, results, structure)
  - [ ] Epoch plan updated (completed tasks checked off, sprint status updated)
  - [ ] Hub/portfolio notified of sprint completion (`_inbox/` in DSM Central and portfolio)
- At phase boundaries (intra-sprint): update blog materials if insights worth sharing

## Blog Integration

Following Section 2.5.6 (Blog/Communication Deliverable Process):
- **Materials**: `docs/blog/<epoch>/materials.md`
- **Journal**: `docs/blog/<epoch>/journal.md` (daily observations)
- **File naming**: `YYYY-MM-DD-title.md` for blog posts
- **Steps**: Preparation → Scoping → Capture → Drafting → Review → Publication
