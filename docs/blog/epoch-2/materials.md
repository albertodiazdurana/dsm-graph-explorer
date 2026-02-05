# Epoch 2 Blog Materials — WSL Migration

**Project:** DSM Graph Explorer + DSM Central
**Topic:** Environment Migration (Windows → WSL2)
**Status:** Draft materials
**Target Platform:** LinkedIn post or technical blog
**Target Audience:** Developers working with AI coding assistants, documentation engineers, data scientists

---

## Working Title Options

1. "From Windows to WSL: Migrating an AI-Assisted Documentation Ecosystem"
2. "Environment Standardization for AI Coding Projects: A Practical Migration Story"
3. "The Venv Portability Trap and Other Migration Lessons"
4. "Why We Moved Our Data Science Methodology to Linux"
5. "Hub-and-Spoke in Practice: Coordinating Multi-Repo Migrations"

**Recommended:** Option 1 or 2 (captures both the technical move and the AI context)

---

## Hook (Opening Paragraph)

**Version A (Problem-first):**
"Our data science methodology framework lived on Windows. Our CI/CD runs on Linux. Our future production deployments will be Linux containers. The path handling code worked, but we were constantly context-switching between environments. When we started planning CI integration for our documentation validator, we realized: it's time to standardize on Linux. Here's how we migrated two interconnected repositories while keeping everything running."

**Version B (Decision-first):**
"DEC-004: WSL Migration for Cross-Platform Development. Status: Approved. That's how our move from Windows to WSL2 started, not with frustration but with a structured decision record. We evaluated three options, documented trade-offs, and created a migration guide before touching any files. This is what environment standardization looks like when you treat infrastructure decisions like architecture decisions."

**Recommended:** Version B (emphasizes the methodical approach)

---

## Story Arc

### 1. Context: The Ecosystem

Two interconnected repositories:
- **DSM Central** (~7,400 lines of markdown): The methodology framework, documentation-only
- **DSM Graph Explorer** (Python CLI): Tool that validates DSM documentation integrity

Hub-and-spoke model: Graph Explorer references DSM Central via `@` import in CLAUDE.md.

### 2. The Trigger

Planning Sprint 5 of Epoch 2: CI integration with GitHub Actions. Realization:
- GitHub Actions runs on Linux
- Our development was on Windows
- Path handling worked but felt fragile
- Docker integration would be easier from Linux

### 3. The Decision Process (DEC-004)

Three options evaluated:
1. **Continue on Windows** — Works now, path edge cases may emerge
2. **Docker for development** — Overkill, volume mount complexity
3. **WSL2 migration** — Native Linux, seamless IDE support, easy containerization later

Decision: Option 3. Rationale documented, success criteria defined.

### 4. The Migration

**What moved:**
```
D:\data-science\agentic-ai-data-science-methodology
    → ~/dsm-agentic-ai-data-science-methodology

D:\data-science\dsm-graph-explorer
    → ~/dsm-graph-explorer
```

**What changed:**
- CLAUDE.md environment section
- @ reference paths
- Migration guide updated
- DSM Central checkpoint updated

### 5. The Gotchas

**Venv portability trap:**
```bash
$ source .venv/bin/activate
$ pip list
/bin/bash: .venv/bin/pip: bad interpreter: No such file or directory
```

The venv was copied from Windows. Python venvs embed absolute paths in their shebangs at creation time. They're not portable.

**Resolution:**
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 6. Verification

| Check | Result |
|-------|--------|
| pytest | 202 passed (94% coverage) |
| dsm-validate | 125 files, 0.08s |
| git operations | Working |
| VSCode Remote-WSL | Connected |

### 7. Lessons Learned

1. **Venvs don't travel** — Always recreate, never copy
2. **Document before migrate** — Migration guide saves time
3. **Decision records work** — DEC-004 made the choice clear
4. **Naming helps** — `dsm-` prefix groups related projects

---

## Key Insights (Numbered Takeaways)

1. **Environment decisions deserve architecture rigor** — A decision record (DEC-004) with options, trade-offs, and success criteria made the migration traceable and reversible.

2. **Python venvs are environment-specific** — Shebangs contain absolute paths. Copying a venv across machines or even directories breaks it. Always `rm -rf` and recreate.

3. **Hub-and-spoke simplifies coordination** — When DSM Central moved, only the `@` reference in CLAUDE.md needed updating. Content wasn't duplicated, so nothing drifted.

4. **Migration guides are worth writing** — The guide created for DEC-004 served as both documentation and checklist during execution.

5. **Dev/CI parity reduces surprises** — Same OS, same Python, same paths. What passes locally will pass in CI.

6. **Naming conventions reveal structure** — `ls ~/dsm-*` now shows all methodology projects. Small detail, big clarity.

---

## Technical Details

### Path Mapping Table

| Project | Windows | WSL |
|---------|---------|-----|
| DSM Central | `D:\data-science\agentic-ai-data-science-methodology` | `~/dsm-agentic-ai-data-science-methodology` |
| Graph Explorer | `D:\data-science\dsm-graph-explorer` | `~/dsm-graph-explorer` |

### Files Updated

```
# Graph Explorer
.claude/CLAUDE.md              # @ reference, environment section
docs/handoffs/wsl_migration_guide.md  # v1.1

# DSM Central
docs/checkpoints/2026-02-04_wsl-migration-context_checkpoint.md
```

### Verification Commands

```bash
# Check structure
ls ~/dsm-*

# Verify DSM Central
cd ~/dsm-agentic-ai-data-science-methodology
git status
ls DSM_*.md

# Verify Graph Explorer
cd ~/dsm-graph-explorer
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/  # 202 passed

# Validate DSM
dsm-validate ~/dsm-agentic-ai-data-science-methodology
# 125 files, 8 errors (all Section 2.6, expected)
```

---

## Visuals to Capture

1. **Before/after path diagram** — Windows paths vs WSL paths
2. **Hub-and-spoke diagram** — DSM Central with Graph Explorer spoke
3. **Terminal screenshot** — pytest 202 passed
4. **Terminal screenshot** — dsm-validate output
5. **DEC-004 summary** — Options table from decision record

---

## Connection to Larger Narrative

This migration fits into the Epoch 2 "productionization" story:

- **Sprint 4:** Exclusion patterns, config files
- **Sprint 5:** CI integration (requires Linux parity) ← **WSL enables this**
- **Sprint 6:** Semantic validation
- **Sprint 7:** Graph prototype

The WSL migration is infrastructure work that enables the CI sprint. It's not glamorous but it's essential.

---

## Call to Action Ideas

**Version A (Practical):**
"If you're developing Python tools on Windows but deploying to Linux, consider migrating to WSL2 now. The transition cost is low; the parity benefits are real."

**Version B (Methodology):**
"We treat infrastructure decisions the same way we treat code decisions: with a decision record, options analysis, and defined success criteria. DEC-004 is in the project repo if you want to see the template."

**Version C (Discussion):**
"What's your dev/prod environment story? Do you develop on the same OS you deploy to? What gotchas have you hit with cross-platform Python projects?"

**Recommended:** B + C (methodology reference + discussion)

---

## Publication Options

### Option 1: Standalone Short Post

~500 words, focused on the venv gotcha and environment parity lesson. Quick read, practical value.

### Option 2: Part of Epoch 2 Retrospective

Include as one section in a larger post about productionizing the validator. Fits the Sprint 5 CI integration narrative.

### Option 3: Decision Record Showcase

Focus on DEC-004 as an example of structured decision-making. The migration becomes the case study.

**Recommended:** Option 2 or 3 depending on how Sprint 5 unfolds.

---

## Notes for Drafting

- Keep it practical: readers want actionable advice
- The venv gotcha is the hook; universal Python experience
- DEC-004 as template is shareable value
- Hub-and-spoke model is differentiating but needs explanation
- Screenshots of terminal output add credibility
- Don't oversell: this is infrastructure work, not breakthrough innovation

---

**Last Updated:** 2026-02-05
