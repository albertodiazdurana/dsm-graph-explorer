# /dsm-align persistent report

**Timestamp:** 2026-04-20T09:53:00+02:00
**DSM version:** v1.6.0 (was v1.4.17)
**Run mode:** post-change
**Project:** dsm-graph-explorer
**Project type:** Application (DSM 4.0 Track)

---

## Report

/dsm-align post-change report:
- Project type: Application (unchanged)
- Created: none
- Already correct: 9 dsm-docs folders + done/, _inbox/, .gitattributes, session-transcript, dsm-ecosystem, reasoning-lessons, CLAUDE.md @ reference, alignment delimiters, settings.json hooks wiring
- Fixed: transcript-reminder.sh updated from Central source (byte-differed); chmod +x applied to both hooks (were mode 644, the S180 failure mode)
- Collisions: none
- Warnings: 2 (see below)
- CLAUDE.md alignment: OK (delimiters present, in sync)
- CLAUDE.md content: OK
- CLAUDE.md redundancy: OK
- CLAUDE.md paths: OK
- .gitattributes: OK
- Command sync: N/A (not DSM Central)
- Feedback pushed: none pending (S47 feedback already pushed, in done/)
- EC governance scaffold: N/A (not EC)

## Spoke actions surfaced (v1.4.17 → v1.6.0)

Major version jump. Key actions:

1. **BL-385 (DSM_0.2 §8.2.1):** Review counter-evidence surfacing requirement for Gate 2 briefs. Loaded immediately via @ reference.
2. **BL-386 (Default-branch verification):** `sync-commands.sh --deploy` in DSM Central to pick up `/dsm-go` Step 2a.6. This project uses `master`, declare `**Main branch:** master` in CLAUDE.md after deploy.
3. **BL-387 (PR-merge parity):** Review DSM_0.2.C §2 + §2.2 for equivalence rule and opt-in permission pattern.
4. **BL-380 (`/dsm-backlog` sprint-plan scaffold):** Applies when creating sprint-titled BLs. Pick up via `sync-commands.sh --deploy`.
5. **BL-377 (parallel-session turn-1 hook fix):** `sync-commands.sh --deploy`.
6. **BL-379 (broadened Application detection):** Applied by this run; no reclassification needed (was already Application).
7. **BL-370 (`validate-rename-staging.sh`):** Not installed by this alignment (current /dsm-align only installs 2 hooks). Manual copy if desired.
8. **BL-372 (Cloned-Mirror Kick-off):** N/A (spoke, not mirror clone).

## Warnings (full text)

1. Hooks were not executable (mode 644). `transcript-reminder.sh` also byte-differed from Central source. Both fixed: updated + chmod +x. This is the S180 failure mode where hooks are present but OS silently refuses to run them.
2. Project uses `master` as main branch (per git default-branch, visible in status). BL-386 Check A compares GitHub default against local main line (defaults to `main`). Consider adding `**Main branch:** master` to CLAUDE.md project-specific section to prevent false-positive halts after sync-commands deploy.

## Collisions (full text)

None.

## Already correct

- 9 canonical `dsm-docs/` folders + `done/` subfolders where required
- All template README files present (blog, checkpoints, feedback, handoffs, plans, research)
- `_inbox/` at project root with `done/` and `README.md`
- `.gitattributes` with `* text=auto eol=lf`
- `.claude/session-transcript.md`, `.claude/dsm-ecosystem.md`, `.claude/reasoning-lessons.md` all present
- CLAUDE.md `@` reference valid; alignment delimiters present and in sync with template
- Feedback lifecycle clean (S47 per-session files already in `done/`)
- settings.json: UserPromptSubmit + PreToolUse hook entries wired

## Steps skipped

- Step 11 skipped: not DSM Central
- Step 3a sprint-plan audit: epoch plans don't match `^# Sprint N` regex (intentional, these are epoch-level plans)
