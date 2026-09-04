# Smoke Tests

Manual end-to-end checks for the `dsm-validate` CLI. These are **not** a substitute for
`pytest tests/`; the unit suite proves the code is correct against its own fixtures, while
these prove the installed console script still works against a real repository.

Referenced by Sprint Boundary Checklist item 5 ("`dsm-docs/guides/smoke-tests.md` current,
or N/A if no smoke tests recorded this sprint").

> **Why this file exists (S58, 2026-08-04).** Checklist item 5 named this path from the
> day the checklist was adopted, and no DSM scaffold creates it, so it never existed here.
> The S57 checkpoint recorded the item as "never actionable". That was slightly
> overstated: the item carries an "or N/A" clause, so it was always tickable as N/A, which
> is precisely the problem, it would have been waived every sprint forever and the check
> would never run. The file now exists with real, executed commands, so the item is live.

**Last run:** 2026-08-04 (S58), against this repository at commit `eda5da0`.
**Result:** 7 of 7 passed.

## Environment

```bash
cd ~/dsm-graph-explorer
pip install -e '.[graph]'      # graph extras needed for T4, T5
```

All commands below use the installed console script `dsm-validate`.

> **Do not use `python -m cli`.** `src/cli.py` has no `if __name__ == "__main__"` guard, so
> `python -m cli` exits 0 and does nothing at all: no output, no file written, no error.
> It looks like a passing run. This cost time in S58 and is recorded here so it does not
> cost it again.

---

## T1, version reports

```bash
dsm-validate --version
```

**Expected:** `dsm-validate, version 0.3.0`

Must agree with `version` in `pyproject.toml`, the `@click.version_option` literal in
`src/cli.py`, and `pip show dsm-graph-explorer`. All four are maintained by hand and drift
silently. S58 found `README.md` claiming 0.4.0 while the other three said 0.3.0.

## T2, help renders

```bash
dsm-validate --help
```

**Expected:** usage line `Usage: dsm-validate [OPTIONS] [PATHS]...` followed by the option
list. Catches Click decorator errors that import cleanly but fail at parse time.

## T3, validation on this repository

```bash
dsm-validate .
```

**Expected (2026-08-04):**

```
Scanned 199 file(s) (47 excluded) in 0.11s. Found 0 error(s), 134 warning(s), 134 info(s), 0 version mismatch(es).
```

**Error count must be 0.** File and warning counts move as the repository grows; treat a
change in those as informational, not a failure. The `47 excluded` figure is
`DEFAULT_EXCLUDES` working (BL-302 P1); if it drops to 0, the exclusions have regressed
and dependency directories are being indexed.

## T4, graph statistics

```bash
dsm-validate . --graph-stats
```

**Expected (2026-08-04):**

```
Graph Statistics:
  Nodes: 2778 (199 files, 2579 sections)
  Edges: 2698 (2579 contains, 119 references)
  Orphan sections: 2556 of 2579
```

The orphan ratio (2556/2579, about 99%) is not a defect. It is the measured sparsity that
[DEC-012](../decisions/DEC-012-close-phase-2-clustering-vision-scope.md) rests on and that
[BL-GE-002](../plans/BL-GE-002_graph-source-expansion.md) exists to address. Record it each
sprint: a material drop is the signal that source expansion is working.

## T5, knowledge summary generation

```bash
dsm-validate . --knowledge-summary /tmp/ks.md
```

**Expected:** `Knowledge summary (markdown) written to /tmp/ks.md (194 lines)`

Then confirm the four Layer 1 components are present, since these are the components the
Intrinsic-ToC vision specifies and all four must ship:

```bash
grep -E '^## ' /tmp/ks.md
```

**Expected sections**, verified 2026-08-04:

```
## Document Hierarchy
## Hub Documents
## Cross-Reference Hotspots
## Orphan Files
```

These are the four Layer 1 components, though the emitted heading is `Document Hierarchy`
while the vision calls the component "Project Map". The names differ; the component is the
same one. Do not "fix" either side to match the other without deciding which is canonical.

Note `--knowledge-summary` takes a PATH argument. Passing it as a bare flag consumes the
next token as its path.

## T6, strict mode exits 0 on a clean repository

```bash
dsm-validate . --strict; echo "exit=$?"
```

**Expected:** `exit=0`, because T3 reports 0 errors. Under `--strict` a non-zero exit means
real errors exist, which is what CI (`.github/workflows/dsm-validate.yml`) gates on.

## T7, unit suite

```bash
python -m pytest tests/ -q
```

**Expected (2026-08-04):** `722 passed, 1 skipped`, 91% coverage.

Note that CI does **not** run pytest. The only workflow runs `dsm-validate . --strict` on
markdown changes, so this check is manual-only and worth actually running.

---

## Recording a run

Update **Last run** and **Result** at the top, and refresh any expected output that has
legitimately moved. When a sprint records no smoke-test run, tick checklist item 5 as N/A
and say why, rather than leaving it ambiguous.
