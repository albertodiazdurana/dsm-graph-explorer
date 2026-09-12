### [2026-09-04] /dsm-align: alignment updated, warnings present

**Type:** Notification
**Priority:** Medium
**Source:** /dsm-align

Run mode: post-change
Full report: `.claude/last-align-report.md`

DSM version moved 1.19.0 -> 1.26.0 since the last alignment (2026-07-30).

Summary:
- Created: none (scaffold was already complete: 8/8 dsm-docs folders, all done/ subfolders, all template files)
- Fixed: 3 hook scripts updated from Central (transcript-reminder.sh, validate-cross-repo-write.sh, validate-transcript-edit.sh); 1 hook entry merged into .claude/settings.json (PreToolUse matcher=Bash -> validate-cross-repo-write.sh, the BL-484 coverage that had never landed here)
- Warnings: 4 (see persistent report for full text)
  1. CLAUDE.md alignment block drift, 5 differences, regeneration WITHHELD because it would delete the project's `### Punctuation` rule
  2. Defect in DSM Central's own template: headless `**Scope.**` block at DSM_0.2.T_Alignment_Templates.md:48
  3. validate-transcript-edit.sh check 4 demoted from blocking to warning by the template sync
  4. Seven DSM_0.2 review items from the 1.19.0->1.26.0 span; the sync-commands deploy action is already satisfied (20/20 identical)
- Collisions: 0

---

## Consolidated review items (carried from two archived entries, S59)

The 2026-07-21 and 2026-07-30 `dsm-align-update` entries were processed and
archived in S59. Both pointed at `.claude/last-align-report.md`, which every
`/dsm-align` run overwrites, so their payload was no longer in the working tree.
It was recovered from git (`a311190`) because that file is tracked, and is
consolidated here so the items stay in front of a reader instead of being
archived unread. This is the only surviving copy outside git history.

**From v1.17.0 -> v1.18.0 (entry dated 2026-07-21), 5 items, none yet reviewed:**

- [ ] DSM_6.0 §1.13 "Forward the Why" (new collaboration principle; mirrored)
- [ ] DSM_0.2 §8.10 Gate 4, now self-sources the "Present Once, Then Deepen" writing discipline
- [ ] DSM_0.2.C §2 mirror-sync carve-out to the write-only rule (BL-471)
- [ ] DSM_0.1 §10 + DSM_1.0.D §6.4.5 feedback-file model reconciliation (BL-472)
- [ ] Inbox-lifecycle / context-budget / handoff guidance reconciliation (BL-470)

**From v1.18.0 -> v1.19.0 (entry dated 2026-07-30), 1 item:**

- [ ] DSM_0.2 §8.9.2 High-Token-Cost Action Gate (BL-476). Carried three times
      now: it was open at v1.19.0, unreviewed through S57 and S58, and appears
      again in the v1.26.0 spoke actions above.

**From v1.19.0 -> v1.26.0 (this entry), 7 items:** §21.4, §19.3, §8.9.2 (same as
above), §20.4, §19.2, §10.1 (applies here, the project keeps `dsm-docs/research/`),
§19.1.

Net open review surface: **12 distinct sections** (§8.9.2 counted once).
