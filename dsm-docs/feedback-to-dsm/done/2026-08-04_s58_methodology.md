# DSM Feedback: Methodology Observations (Session 58, 2026-08-04)

**Project:** dsm-graph-explorer
**DSM version at time of session:** 1.19.0

---

## Entry 48: an escape clause turns a checklist item into a permanent waiver

Sprint Boundary Checklist item 5 reads "`dsm-docs/guides/smoke-tests.md` current (or N/A if
no smoke tests recorded this sprint)". The clause in parentheses is sensible in isolation:
not every sprint runs smoke tests. But combined with the fact that no scaffold creates the
file, it means the item can be ticked as N/A in perpetuity and the underlying check never
runs once. The escape clause is not an escape from the *work*, it is an escape from the
*item*.

The distinction worth generalising: an escape clause is safe when the escaped condition is
observable ("no smoke tests were run this sprint" is checkable against a record) and unsafe
when the escape is also the default state. Where a checklist item's N/A branch is
indistinguishable from "nobody ever set this up", the item is decorative.

Detail on the two-instance pattern is in this session's backlog Proposal 1.

## Entry 49: the reproducibility preference paid out on its first use, by disagreeing

The recorded project preference that experiments be reproducible scripts existed as a
principle with no test case. S58 applied it to a check that Session 57 had run inline via a
heredoc, whose numbers a decision record (DEC-012) cites as counter-evidence.

Rebuilding the check produced three results, and the middle one is the interesting one:

1. It found a defect in the original: degree counts were looked up in a top-10-only
   dictionary, so entrants from outside the top 10 printed "0 refs".
2. It found a defect in *my own* first rebuild: PageRank run on the reversed raw graph
   scores files by how many sections they contain, not by how often they are referenced,
   because `REFERENCES` edges are section-to-section and `FILE` nodes have no in-edges at
   all. It returned Pearson r = **−0.34** and a top-10 of long documents with zero incoming
   references. What exposed it was not a test but the absurdity of the output.
3. Once corrected, it **partially disagreed with the record**. The verdict and two of the
   three cited figures reproduce; the positions-changed counts do not (7/10 and 8/10 here
   against 9/10 and 5/10 recorded).

The methodological point: a reproducibility requirement is usually justified as
housekeeping. Its real value showed up as disagreement, on the first artifact it was
applied to. A cited number that nobody can regenerate is not merely inconvenient, it is
unfalsifiable, and this one turned out to be partly wrong.

Corollary on how to report that: the divergence was annotated onto DEC-012 rather than
edited into it, preserving the S57 record and marking the correction separately, per the
records-versus-plans asymmetry. The decision's conclusion is unaffected because it rests on
a pre-registered threshold being cleared rather than on the counts, and the re-run clears it
by a wider margin. Stating that explicitly matters, otherwise "the numbers do not reproduce"
reads as "the decision is unsound".

## Entry 50: validating a new measure against the shipped one is what makes the new measure trustworthy

Related to Entry 49 but separable. After fixing the PageRank projection, the temptation was
to report the corrected numbers. Instead the script's *degree* ranking was diffed against
the `## Hub Documents` table that `dsm-validate . --knowledge-summary` actually emits: all
ten positions identical, over the same 199-file scan.

That check does not validate the PageRank half directly. What it does is rule out the
possibility that the baseline half is *also* subtly wrong, which is the failure mode that
would have made a corrected comparison meaningless. When a script reimplements something
the product already computes, diffing against the product is cheap and is the difference
between "my numbers changed" and "my numbers are right".

## Entry 51: a partial answer is a better report than a clean one, when the parts differ

Three separate findings this session resolved to "partly, and here is the split" rather
than yes or no:

- The failing test carried across three sessions does not reproduce (722 passed, no code
  changed since S55), **but** the test pins a commit and would fail on a shallow clone, and
  separately there is no CI job running pytest at all. I formed the hypothesis that CI's
  shallow checkout explained the S55 failure, checked the workflow, and found it runs
  `dsm-validate` rather than pytest, refuting my own explanation. The fragility is real but
  latent.
- The S57 methodology feedback file is missing locally, **but** its content did reach
  Central: the rolling notification archive was written 2026-07-31 01:32, inside S57's
  window, and carries the findings. Nothing was lost; the local record is incomplete. That
  is a materially different report from "S57 skipped its methodology feedback", and the
  difference only appeared by checking the destination rather than the source.
- The PageRank check reproduces the verdict and two figures, and diverges on a third.

In each case the tidy summary would have been wrong in a way that mattered to what someone
does next. Worth stating as a norm: when a finding splits, report the split rather than the
majority side of it.
