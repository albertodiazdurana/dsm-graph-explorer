# DEC-007: Python 3.12 Upgrade

**Date:** 2026-03-10
**Status:** ACCEPTED
**Epoch:** 3 (Sprint 9)
**Supersedes:** pyproject.toml `requires-python = ">=3.10"` (Epochs 1-2)

---

## Context

Epoch 3 introduces FalkorDBLite as the graph database backend (DEC-006). FalkorDBLite
requires **Python 3.12+** and has no 3.10/3.11 wheels. This creates a compatibility gap
with the project's current minimum target of Python 3.10.

Two strategies were considered: unconditional version upgrade or optional dependency gate.

---

## Decision

**Upgrade the project minimum Python version to 3.12.**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| New minimum | Python 3.12 | Minimum version required by FalkorDBLite |
| Version bump | 0.2.0 → 0.3.0 | New epoch, breaking change in platform requirement |
| falkordblite | Added to `[graph]` optional extra | Alongside networkx; both are part of the graph feature set |
| CI workflow | No change | Already targets Python 3.12 (`python-version: '3.12'`) |
| Classifiers | Drop 3.10/3.11, keep 3.12 | Reflects actual support |

---

## Options Evaluated

### Option A: Upgrade to Python 3.12 -- SELECTED

| Aspect | Assessment |
|--------|------------|
| FalkorDBLite support | Native, no workarounds |
| Existing stack compatibility | Click, Rich, Pydantic, PyYAML, scikit-learn, networkx, pytest all support 3.12 |
| Python 3.10 EOL | October 2026, upgrade is timely |
| Python 3.12 improvements | Faster interpreter, improved error messages, `tomllib` stdlib |
| Implementation scope | Four `pyproject.toml` lines, zero CI changes, zero source changes |
| Breaking change | Yes, for users on 3.10/3.11 |

**Verdict:** Selected. FalkorDBLite is the core feature of Epoch 3, not an optional
enhancement. Requiring 3.12 as the minimum is the correct technical response.

### Option B: Optional Dependency Gate

| Aspect | Assessment |
|--------|------------|
| FalkorDBLite support | Available under `pip install .[graph]` with Python 3.12+ |
| 3.10/3.11 users | Can still use non-graph CLI features |
| Implementation scope | import guard, version check at runtime, conditional CI matrix |
| Complexity | Import guards, version gates, conditional test skips, confusing UX |
| Architectural honesty | FalkorDB IS the graph backend; calling it optional is misleading |

**Verdict:** Rejected. This pattern is appropriate for enhancement features (scikit-learn
for semantic search, networkx for in-memory queries). FalkorDBLite is the foundational
infrastructure of Epoch 3, not a feature enhancement layered on top. Making the core
architecture optional contradicts Epoch 3's design intent.

The optional gate pattern should be reserved for features where the tool remains fully
useful without the optional component. Graph persistence is not such a feature.

---

## Implementation Notes

Changes required in `pyproject.toml`:

1. `requires-python = ">=3.12"` (was `>=3.10`)
2. Remove `"Programming Language :: Python :: 3.10"` and `":: Python :: 3.11"` classifiers
3. Add `"falkordblite>=0.9"` to `[project.optional-dependencies] graph` (alongside networkx)
4. Update `[tool.black] target-version = ['py312']`
5. Update `[tool.ruff] target-version = "py312"`
6. Version bump: `version = "0.3.0"`

No changes required in `.github/workflows/dsm-validate.yml` (already uses Python 3.12).

Post-upgrade validation: run `pytest tests/` and confirm all 331 tests pass with zero
regressions before proceeding to Sprint 9 FalkorDBLite integration work.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing tests break on 3.12 | Low | Medium | Run full suite immediately after upgrade |
| Dependency incompatibility | Low | Low | All current deps tested on 3.12 by their maintainers |
| Users on 3.10/3.11 excluded | Medium | Low | Project is a personal DSM tool, not a public library |
| FalkorDBLite 3.12 API changes in future | Low | Low | Pinned to `>=0.9`; Beta status acknowledged in DEC-006 |

---

## References

- FalkorDBLite deep-dive: `docs/research/epoch-3-falkordblite-deep-dive.md` (Section 1, Section 8)
- DEC-006: `docs/decisions/DEC-006-graph-database-selection.md`
- Epoch 3 plan: `docs/plans/epoch-3-plan.md`