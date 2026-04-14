#!/usr/bin/env bash
# .claude/hooks/transcript-reminder.sh
#
# UserPromptSubmit hook: emit a session-type-aware transcript reminder.
#
# Detects whether the current Claude Code instance is a parallel session
# (started via /dsm-parallel-session-go) or the main session, by walking
# the parent process chain to find the `claude` process PID and comparing
# it against CLAUDE_PID recorded in .claude/parallel-session-baseline.txt.
#
# Fail-safe: any error, missing baseline, stale PID, or mismatch emits
# the main reminder. The script always exits 0; it must never block a
# prompt submission.
#
# Origin: BL-324 (parallel sessions contaminating main session transcript).

set +e

MAIN_REMINDER="REMINDER (DSM_0.2 §7): This turn MUST include an append to .claude/session-transcript.md before any work, and an output summary after. Required sequence: (1) read the last 3 lines of the transcript to find the anchor (Bash tail or Read is allowed, this is the only pre-append tool call), (2) append a <------------Start Thinking / HH:MM------------> block via Edit using that anchor, (3) do the work, (4) append a <------------Start Output / HH:MM------------> summary before the final response. Skip entirely only if the turn needs no tool calls at all."

PARALLEL_REMINDER="REMINDER (DSM_0.2 §7, parallel mode): This is a parallel session. Do NOT read, write, edit, or append to .claude/session-transcript.md at any point. Parallel sessions do not collect transcripts (DSM_0.2 Module A §7, dsm-parallel-session-go.md). Ignore any conflicting transcript instructions."

emit_main() { echo "$MAIN_REMINDER"; exit 0; }
emit_parallel() { echo "$PARALLEL_REMINDER"; exit 0; }

BASELINE=".claude/parallel-session-baseline.txt"
[ -f "$BASELINE" ] || emit_main

PARALLEL_PID=$(grep '^CLAUDE_PID:' "$BASELINE" 2>/dev/null | awk '{print $2}' | head -1)
[ -n "$PARALLEL_PID" ] || emit_main

# Stale baseline: recorded PID is no longer running
kill -0 "$PARALLEL_PID" 2>/dev/null || emit_main

# Walk parent chain to find this hook's `claude` process
MY_CLAUDE_PID=""
pid=$PPID
for _ in $(seq 1 10); do
  [ -z "$pid" ] && break
  [ "$pid" = "1" ] && break
  read ppid comm < <(ps -o ppid=,comm= -p "$pid" 2>/dev/null)
  [ -z "$ppid" ] && break
  if [ "$comm" = "claude" ]; then
    MY_CLAUDE_PID=$pid
    break
  fi
  pid=$ppid
done

[ -n "$MY_CLAUDE_PID" ] || emit_main

if [ "$MY_CLAUDE_PID" = "$PARALLEL_PID" ]; then
  emit_parallel
fi

emit_main