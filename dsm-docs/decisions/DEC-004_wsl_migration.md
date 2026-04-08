# DEC-004: WSL Migration for Cross-Platform Development

**Date:** 2026-02-04
**Status:** Approved
**Context:** Development environment standardization for DSM ecosystem projects

---

## Situation

Currently developing on Windows with paths like `D:\data-science\dsm-graph-explorer`. While the code handles cross-platform paths correctly (forward slash normalization), future scaling and deployment considerations require a consistent Linux-based environment.

### Current State
- Development on Windows 11
- Path handling works via normalization
- CI/CD will run on Linux (GitHub Actions)
- Potential deployment to Linux servers

### Concerns
- Windows-specific edge cases in path handling
- Different behavior between dev and CI environments
- Containerization complexity with Windows paths
- Team scalability (future collaborators may use Mac/Linux)

---

## Options Considered

### Option A: Continue on Windows
**Pros:**
- No migration effort
- Current setup works
- Familiar environment

**Cons:**
- Path edge cases may emerge
- CI/prod environment mismatch
- Docker volume mounts more complex

**Verdict:** Acceptable short-term, not ideal long-term.

---

### Option B: Docker for Development
**Pros:**
- Fully isolated Linux environment
- Reproducible across machines
- Matches CI exactly

**Cons:**
- Volume mount complexity on Windows
- Overhead for local development
- IDE integration requires dev containers

**Verdict:** Better for CI/distribution, overkill for active development.

---

### Option C: WSL2 Migration (Selected)
**Pros:**
- Native Linux environment
- Seamless file access
- Full IDE support (VSCode Remote-WSL)
- Claude Code works identically
- Git, Python, all tools native
- Easy path to containerization later

**Cons:**
- One-time migration effort
- Paths change (need to update configs)

**Verdict:** Best balance of development experience and environment consistency.

---

## Decision

**Selected:** Option C — Migrate to WSL2

### Rationale
1. **Development parity** — Same environment as CI and production
2. **Simpler paths** — No more `D:\` vs `/mnt/d/` confusion
3. **Future-proof** — Easy to containerize later if needed
4. **Claude Code compatible** — Works natively in WSL terminal

---

## Implementation Plan

### Phase 1: Backup & Verify
```bash
# Ensure all changes committed and pushed
git status  # Clean working tree
git push origin master
```

### Phase 2: Copy to WSL
```bash
# In WSL terminal
mkdir -p ~/data-science
cp -r /mnt/d/data-science/dsm-graph-explorer ~/data-science/
cp -r /mnt/d/data-science/agentic-ai-data-science-methodology ~/data-science/
```

### Phase 3: Setup Environment
```bash
cd ~/data-science/dsm-graph-explorer
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/  # Verify all tests pass
```

### Phase 4: Update Configuration
- Update `CLAUDE.md` with new paths
- Verify `.dsm-graph-explorer.yml` works (forward slashes already)

### Phase 5: Verify & Clean
- Run full test suite in WSL
- Validate against DSM repo from WSL paths
- Optionally remove Windows copies after confirmed working

---

## Affected Projects

| Project | Path (Windows) | Path (WSL) |
|---------|---------------|------------|
| DSM Graph Explorer | `D:\data-science\dsm-graph-explorer` | `~/data-science/dsm-graph-explorer` |
| DSM Methodology | `D:\data-science\agentic-ai-data-science-methodology` | `~/data-science/agentic-ai-data-science-methodology` |
| (Future projects) | `D:\data-science\*` | `~/data-science/*` |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss during copy | High | Git push before migration, keep Windows copy as backup |
| Permission issues | Medium | Standard user owns WSL home directory |
| Different Python version | Low | pyenv or system Python 3.12 in WSL |
| IDE integration issues | Low | VSCode Remote-WSL extension well-tested |

---

## Success Criteria

- [ ] All 202 tests pass in WSL
- [ ] `dsm-validate` works against DSM repo from WSL
- [ ] Claude Code sessions work in WSL terminal
- [ ] VSCode Remote-WSL connects properly
- [ ] Git operations work (push/pull)

---

## References

- [WSL Migration Guide](../handoffs/wsl_migration_guide.md) — Step-by-step guide for all repos
- Microsoft WSL Documentation
- VSCode Remote-WSL Extension

---

**Author:** Alberto Diaz Durana (with AI assistance)
**Last Updated:** 2026-02-04
