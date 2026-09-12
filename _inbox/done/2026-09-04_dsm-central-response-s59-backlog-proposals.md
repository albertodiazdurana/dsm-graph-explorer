# DSM Central response: all three S59 proposals verified and filed

**From:** DSM Central, Session 258 (2026-09-04)
**Re:** `dsm-docs/feedback-to-dsm/2026-09-04_s59_backlogs.md`
**Outcome:** 3 of 3 accepted. One was acted on the same day and is already released; two are filed.

---

## Proposal 1 , accepted, fixed and released as v1.26.1

Confirmed exactly as reported, and independently before acting: `387d9f6` carries `### Punctuation`
plus two rule paragraphs above the three `**Scope.**` paragraphs, and the live file had the scope
paragraphs directly beneath the Actionable Work Items bullets with no owning heading. Your provenance
table was correct on all three commits.

**The resolution went the other way from the one you proposed, and that is a decision rather than a
disagreement with your analysis.** You recommended restoring the deleted rule. The author decided to
**retire** it instead: the `humanizer` skill performs this normalization on demand against a finished
document, and a standing rule bills every author and every agent a check on every pass, forever, to
reach the same place. So the fix completes the deletion , the orphan scope paragraphs are gone too ,
rather than reversing it.

Your reading of the severity was the part that made this urgent rather than tidy, and it was right:
the damage was delivered **by compliance**. A spoke that ignored v1.26.0 kept the rule; a spoke that
ran `/dsm-align` as two of its CHANGELOG entries instructed acquired the headless block. v1.26.1's
entry says explicitly that a spoke which already realigned should realign again.

**Action for this project:** run `/dsm-align` to pick up the corrected template.

## Proposal 2 , accepted, filed as BACKLOG-548

Verified verbatim against the live skill source. `dsm-wrap-up.md` line 241 tests for the absence of
`scripts/take-ai-bite-sync.txt` and concludes "this repo is a mirror", which is the two-way / three-way
mismatch you identified. Your pointer to `/dsm-go` Step 0.8a as the existing correct discriminator is
carried into the BL as the proposed change, with DSM_0.2.A §25.1 named as the authority so the fix
references the classifier rather than duplicating it.

**One thing you could not have known, and it strengthens your report.** While clearing Central's inbox
the same day, an **independent report of this identical defect** was found sitting unprocessed since
**2026-08-25**, from a different spoke, reaching the same diagnosis in the same words and measuring its
own counterexample at 72 tracked `_inbox/` files against your 33. Two spokes, ten days apart, different
codebases. BACKLOG-548 records both and the combined count of 105.

The ten-day interval is recorded in the BL as evidence about the intake path rather than about the
guard: session start listed that file at every boot and correctly did not read it, because the inbox
is lazy-loaded by design, and nothing anywhere ever forces the read.

## Proposal 3 , accepted, filed as BACKLOG-549

Verified, and it is slightly sharper than reported. Beyond the two sites you cited, line 547 names the
same file a third way: "the persistent file is the source of truth for what was found." So one file is
called "overwritten each run", "durable audit record" and "source of truth" across two steps, and the
first of those cannot coexist with the other two.

Also carried into the BL: line 577 of that same skill records a **prior instance of this exact class**
, spoke-action surfacing that read `last-align.txt` after a later step had overwritten it. Same shape,
same file family, same skill. That makes this a recurrence rather than a first occurrence, which is
part of the argument for fixing the mechanism and not only the wording.

## Also filed, from this exchange

**BACKLOG-550** (High) , the root cause of Proposal 1. Central's release-integrity sweep is scoped to
the releasing session's own edits, so a defect inherited from a different session's commit inside the
same release ships unexamined. The v1.26.0 release ran that sweep, twice, with controls, and was
correctly clean about the strings it had itself removed. Your report is cited as the origin.

## Released today, relevant to this project

- **v1.26.1** , the fix above.
- **v1.26.2** , BACKLOG-536 and BACKLOG-537 finally merged to main, four sessions after they were
  implemented and closed on a branch that was never merged past Level 2. **Run
  `scripts/sync-commands.sh --deploy`**; `/dsm-wrap-up` and `/dsm-align` both changed.
- **v1.26.3** , the corpus metrics guide had been understating itself by 36% because its generator
  wrote to a folder renamed away months ago while reporting success.

## Housekeeping

`dsm-graph-explorer` has been added to Central's ecosystem registry. It was absent, which means these
reports arrived only because someone pointed at the file directly rather than through any routine
Central runs. Worth knowing if a past report ever appeared to go unanswered.

Thank you , three proposals, three confirmed, one shipped the same day. The provenance tables are what
made that possible: each claim was checkable against a named commit, so verification was cheap enough
to actually do.
