### [2026-02-11] Session Transcript Protocol: /dsm-go updated

**Type:** Notification
**Priority:** Medium
**Source:** DSM Central

The `/dsm-go` skill (step 6) has been updated to be more explicit about creating
the session transcript file:

- File must be `.claude/session-transcript.md` (`.md`, not `.txt`)
- It is a separate file from `.claude/session-baseline.txt`
- Step now includes an explicit `cat > .claude/session-transcript.md` bash command
- Purpose: persistent reasoning log the user monitors in VS Code in real time

The Session Transcript Protocol is documented in DSM_0.2 (v1.3.11). Per-turn
flow: append thinking BEFORE acting, append output summary AFTER completing work.
Two appends per turn.
