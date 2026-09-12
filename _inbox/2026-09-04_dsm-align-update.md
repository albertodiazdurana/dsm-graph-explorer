### [2026-09-04] /dsm-align: alignment updated (1.26.3)

**Type:** Notification
**Priority:** Low
**Source:** /dsm-align

Run mode: post-change
Full report: `.claude/last-align-report.md`

Second alignment run of session 59. The first (this morning, at 1.26.0) deliberately
WITHHELD the block regeneration because the template had lost a rule and gained a
headless paragraph. DSM Central fixed that in 1.26.1, so this run completes it.

Summary:
- Created: none
- Fixed: CLAUDE.md alignment block regenerated to 1.26.3 (198 -> 196 lines, 8 lines changed)
- Warnings: 1 , the regeneration removes `### Punctuation`, because DSM 1.26.1 retired
  the rule fleet-wide in favour of the `humanizer` skill on demand. Behavioural change,
  effective immediately.
- Collisions: 0

Spoke actions 1.26.0 -> 1.26.3: `/dsm-align` done by this run; `sync-commands.sh --deploy`
already satisfied (0 of 20 files differing); 1.26.3 needs nothing.

Open review items are NOT in this entry. They live in
`_inbox/2026-09-04_open-review-items.md`, deliberately under a name this notification
cannot overwrite. See BACKLOG-549.
