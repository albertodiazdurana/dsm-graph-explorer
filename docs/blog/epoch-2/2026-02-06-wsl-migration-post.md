# From Windows to WSL: Migrating an AI-Assisted Documentation Ecosystem

**Date:** 2026-02-05
**Author:** Alberto Diaz Durana
**Status:** Draft v1

---

DEC-004: WSL Migration for Cross-Platform Development. Status: Approved.

That's how my move from Windows to WSL2 started, not with frustration but with a structured decision record. I evaluated three options, documented trade-offs, and created a migration guide before touching any files. This is what environment standardization looks like when you treat infrastructure decisions like architecture decisions.

## The Context

You work with what you have. My machine runs Windows, which is common in enterprise and data science environments. Windows works fine for many tasks, and I knew from the start that Linux would eventually be the better fit for Python tooling and CI/CD. The question was never *whether* to migrate, but *when*.

During Epoch 1, I focused on building the tool: parser, validator, CLI, 202 tests. Windows didn't block any of that. But as I planned Epoch 2, specifically GitHub Actions integration, the friction started to matter. CI runs on Linux. Path separators differ. Environment parity between local development and CI becomes a real concern.

I had three options: convert the machine to Ubuntu (losing Windows tools I use for other work), spin up a cloud VM (recurring costs for what should be a local workflow), or use WSL2. Microsoft built WSL2 precisely for this situation, a native Linux kernel inside Windows, with first-class VS Code integration. It's not a workaround; it's a supported development path that Docker Desktop itself runs on.

I maintain two interconnected repositories:

- **DSM Central** (~7,400 lines of markdown): A methodology framework for human-AI collaboration in data science projects
- **DSM Graph Explorer** (Python CLI): A tool that validates cross-references in DSM documentation

These repositories follow a hub-and-spoke model. Graph Explorer references DSM Central through a single `@` import in its configuration file. When I update DSM Central, Graph Explorer inherits those changes automatically, no copy-paste required.

## The Decision

I didn't just start copying files. I wrote a decision record (DEC-004) with three options:

| Option | Verdict |
|--------|---------|
| **Continue on Windows** | Works now, path edge cases may emerge |
| **Docker for development** | Overkill, volume mount complexity |
| **WSL2 migration** | Native Linux, seamless IDE support, easy containerization later |

WSL2 won. Native Linux development environment with VSCode Remote-WSL integration. Same OS as CI/CD. No path translation issues.

## The Migration

The actual file moves were straightforward:

```
D:\data-science\agentic-ai-data-science-methodology
    → ~/dsm-agentic-ai-data-science-methodology

D:\data-science\dsm-graph-explorer
    → ~/dsm-graph-explorer
```

I renamed the DSM folder to add a `dsm-` prefix. Now `ls ~/dsm-*` shows all methodology-related projects together. Small detail, surprisingly useful.

## The Gotcha

Here's where things got interesting. After copying Graph Explorer, I tried to run tests:

```bash
$ source .venv/bin/activate
$ pip list
/bin/bash: .venv/bin/pip: bad interpreter: No such file or directory
```

The virtual environment was copied from Windows, and Python venvs embed absolute paths in their shebang lines at creation time. The copied venv still pointed to:

```
/home/berto/data-science/dsm-graph-explorer/.venv/bin/python3
```

But that path no longer existed. The venv was dead on arrival.

**The fix:** Delete and recreate.

```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Lesson learned: **venvs don't travel**. Always recreate, never copy.

## The Verification

With a fresh venv, everything worked:

| Check | Result |
|-------|--------|
| pytest | 202 passed (94% coverage) |
| dsm-validate | 125 files scanned, 0.08s |
| git operations | Working |
| VSCode Remote-WSL | Connected |

The validator found 8 broken references, all pointing to Section 2.6 which doesn't exist in the documentation. Those are real issues in the DSM docs, not migration artifacts. The tool works.

## The Documentation Updates

Migration isn't just moving files. It's updating every reference to those files:

1. **CLAUDE.md** — Updated `@` import path and environment section
2. **Migration guide** — Added new path mappings table
3. **DSM Central checkpoint** — Updated hub-and-spoke diagram

The hub-and-spoke model helped here. Because Graph Explorer references DSM Central through a single import rather than copied content, I only needed to update one line:

```markdown
# Before
@D:/data-science/agentic-ai-data-science-methodology/DSM_Custom_Instructions_v1.1.md

# After
@~/dsm-agentic-ai-data-science-methodology/DSM_Custom_Instructions_v1.1.md
```

One line changed. The entire methodology inheritance still works.

## Key Takeaways

**1. Decision records work for infrastructure too.** DEC-004 took 20 minutes to write. It saved hours of second-guessing and provided a reference when updating documentation.

**2. Python venvs are environment-specific.** The shebang paths are hardcoded at creation. Don't copy them across machines or directories. Recreate.

**3. Hub-and-spoke reduces migration friction.** Reference once, inherit everything. When the hub moves, spokes just update their pointer.

**4. Document before you migrate.** The migration guide I wrote became my checklist. Nothing was forgotten.

**5. Dev/CI parity matters.** Same OS, same Python version, same paths. What passes locally will pass in CI.

## What's Next

With the environment standardized, I'm ready for Sprint 5: CI integration. GitHub Actions will run the same commands I run locally. No path translation, no Windows-specific edge cases.

WSL2 solves the immediate need. If the workflow outgrows it, the next step would be converting to Ubuntu or provisioning a cloud development environment, but both come with trade-offs (lost Windows tooling or recurring costs). For now, WSL2 gives native Linux where it matters without forcing a full platform switch.

The methodology that started on Windows now lives where it will eventually run in production.

---

*This project is part of the [DSM (Agentic AI Data Science Methodology)](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology) ecosystem. The decision record (DEC-004) and migration guide are in the [dsm-graph-explorer](https://github.com/albertodiazdurana/dsm-graph-explorer) repository.*

---

**Tags:** #Python #WSL #DevOps #DataScience #TechnicalWriting #DocsAsCode
