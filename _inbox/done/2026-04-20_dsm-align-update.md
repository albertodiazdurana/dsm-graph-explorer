### [2026-04-20] /dsm-align: warnings present, hooks repaired

**Type:** Notification
**Priority:** Medium
**Source:** /dsm-align

Run mode: post-change
Full report: `.claude/last-align-report.md`

Summary:
- Created: none
- Fixed: transcript-reminder.sh updated (byte-differed from Central); chmod +x on both hooks (were mode 644, S180 failure mode)
- Warnings: 2 (hook executability issue, master vs main-branch declaration for BL-386)
- Collisions: 0
- DSM version: v1.4.17 → v1.6.0 (major jump, spoke actions surfaced in persistent report)
