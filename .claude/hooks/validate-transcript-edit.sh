#!/bin/bash
# Hook: Enforce session transcript append-only rule (DSM_0.2 §7)
# Fires on PreToolUse for Edit calls to *session-transcript.md
# Validations (check 0 runs first; 1-3 block; 4 blocks on (a), warns on (b)):
# 0. replace_all is categorically forbidden
# 1. old_string must be anchored to the last non-empty line of the file
# 2. new_string must start with old_string (append-only, no replacement)
# 3. Appended content must contain a <------------Start {timestamp}------------>
#    delimiter (ensures every entry is timestamped)
# 4. The delimiter's HH:MM must not run backwards (blocks, day rollover excepted),
#    and a gap over 4h should carry a marker (warns only)

set -e

# Read JSON from stdin and extract fields
INPUT=$(cat)
eval "$(echo "$INPUT" | python3 -c "
import sys, json, shlex
data = json.load(sys.stdin)
ti = data.get('tool_input', {})
print(f'FILE_PATH={shlex.quote(ti.get(\"file_path\", \"\"))}')
print(f'OLD_STRING={shlex.quote(ti.get(\"old_string\", \"\"))}')
print(f'NEW_STRING={shlex.quote(ti.get(\"new_string\", \"\"))}')
print(f'REPLACE_ALL={shlex.quote(\"true\" if ti.get(\"replace_all\", False) else \"\")}')
")"

# Only validate session-transcript.md edits
if [[ ! "$FILE_PATH" =~ \.claude/session-transcript\.md$ ]]; then
  exit 0
fi

# If file doesn't exist yet, allow (initial creation via Write)
if [[ ! -f "$FILE_PATH" ]]; then
  exit 0
fi

# --- Check 0: replace_all is categorically forbidden on the transcript ---
# (DSM_0.2 §7; BL-449). The append-anchor rule assumes a unique last-line
# anchor; replace_all duplicates new content at EVERY match, exploding the file
# (IronCalc S17: 95 MB / 1.5M lines; blog-poster S22: Output block duplicated).
# This check runs before the anchor/append/delimiter checks because replace_all
# is wrong regardless of their state.
if [[ "$REPLACE_ALL" == "true" ]]; then
  cat >&2 <<EOF
BLOCKED: Session transcript violation — replace_all forbidden (DSM_0.2 §7, check 0/3).

Edit with replace_all: true is never allowed on .claude/session-transcript.md.
The append-anchor rule assumes a unique last-line anchor; replace_all duplicates
your new content at every match and explodes the file (IronCalc S17: 95 MB).

FIX: Use a normal append Edit (replace_all absent/false): read the last 3 lines,
anchor old_string on the last non-empty line, set new_string = old_string + new
content. To recover from a botched transcript Edit, append a [RETROACTIVE] note
via a Bash heredoc — never a replace_all cleanup.
EOF
  exit 2
fi

# Get last non-empty line from the file
LAST_LINE=$(grep -v '^[[:space:]]*$' "$FILE_PATH" | tail -1)
if [[ -z "$LAST_LINE" ]]; then
  exit 0
fi

# Extract first line of old_string for matching
FIRST_OLD_LINE=$(echo "$OLD_STRING" | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
if [[ -z "$FIRST_OLD_LINE" ]]; then
  exit 0
fi

# --- Check 1: old_string anchored to last non-empty line ---
if ! echo "$LAST_LINE" | grep -qF -- "$FIRST_OLD_LINE"; then
  cat >&2 <<EOF
BLOCKED: Session transcript violation — wrong anchor (DSM_0.2 §7, check 1/3).

old_string is not anchored to the last non-empty line of the file.

Last non-empty line:
  $LAST_LINE

Your old_string started with:
  $FIRST_OLD_LINE

FIX: Read the last 3 lines of .claude/session-transcript.md, use the last
non-empty line as old_string, and append new content after it.
EOF
  exit 2
fi

# --- Check 2: new_string starts with old_string (append-only) ---
if [[ "$NEW_STRING" != "$OLD_STRING"* ]]; then
  cat >&2 <<EOF
BLOCKED: Session transcript violation — content replaced (DSM_0.2 §7, check 2/3).

new_string must START WITH old_string verbatim. You are replacing content
instead of appending after it.

FIX: new_string = old_string + new content. Preserve old_string at the start.
EOF
  exit 2
fi

# --- Check 3: appended content contains a timestamped delimiter ---
# Extract the appended part (new_string minus old_string prefix)
APPENDED="${NEW_STRING#"$OLD_STRING"}"

# Check for <------------Start {anything}------------>
if ! echo "$APPENDED" | grep -q '<------------Start '; then
  cat >&2 <<EOF
BLOCKED: Session transcript violation — missing delimiter (DSM_0.2 §7, check 3/3).

Every appended entry must contain a timestamped delimiter:
  <------------Start {timestamp}------------>

Your appended content does not contain this delimiter.

FIX: Start your appended block with:
  <------------Start Thinking / HH:MM------------>
or for output blocks:
  <------------Start Output / HH:MM------------>
EOF
  exit 2
fi

# --- Check 4: block timestamp sanity (monotonicity + unmarked gaps) ---
# Added S58 per the S57 STAA. Transcript timestamp hygiene has now failed in S49,
# S54 and S57; S49 entry 50 classified it as the mechanism-not-another-lesson
# case and S54 entry 109 asked for this hook. Two shapes are detectable:
#
#   (a) Non-monotonic: S57 had an Output block stamped 01:52 answering a User
#       block stamped 02:16. A backwards stamp is never correct outside a day
#       rollover, and the fix (write the right HH:MM) is trivial, so this BLOCKS.
#   (b) Unmarked long gap: S57 had 15.5 hours between User 08:04 and Thinking
#       23:32 with no marker. Long pauses are legitimate, so this only WARNS.
#
# Note on (b)'s reach: a PreToolUse hook's stderr is delivered to the agent only
# on exit 2. Warning at exit 0 surfaces in transcript mode but is not guaranteed
# to reach the model, so (b) is advisory by construction. Escalating it to a
# block was rejected: it would fire on every legitimate overnight or multi-day
# session pause and make the protocol unusable, which is the failure mode the
# warn-only choice exists to avoid.

GAP_WARN_MINUTES=240   # 4 hours
ROLLOVER_EVENING_HOUR=20
ROLLOVER_MORNING_HOUR=4

# Prints "HH MM" for a delimiter timestamp, or nothing. $1 = text, $2 = first|last
_extract_hhmm() {
  local _match
  if [[ "$2" == "first" ]]; then
    _match=$(echo "$1" | grep -oE 'Start [A-Za-z]+ */ *[0-9]{1,2}:[0-9]{2}' | head -1 || true)
  else
    _match=$(echo "$1" | grep -oE 'Start [A-Za-z]+ */ *[0-9]{1,2}:[0-9]{2}' | tail -1 || true)
  fi
  [[ -z "$_match" ]] && return 0
  echo "$_match" | sed -E 's/.*\/ *([0-9]{1,2}):([0-9]{2}).*/\1 \2/'
}

PREV_TS=$(_extract_hhmm "$(cat "$FILE_PATH")" last)
NEW_TS=$(_extract_hhmm "$APPENDED" first)

# Only evaluate when both sides carry a parseable timestamp. Legacy blocks
# without one, and appends that add no new delimiter, are silently skipped.
if [[ -n "$PREV_TS" && -n "$NEW_TS" ]]; then
  PREV_H=$(echo "$PREV_TS" | cut -d' ' -f1); PREV_M=$(echo "$PREV_TS" | cut -d' ' -f2)
  NEW_H=$(echo "$NEW_TS" | cut -d' ' -f1);   NEW_M=$(echo "$NEW_TS" | cut -d' ' -f2)

  # 10# forces base-10 so 08 and 09 do not parse as invalid octal
  PREV_MIN=$(( 10#$PREV_H * 60 + 10#$PREV_M ))
  NEW_MIN=$(( 10#$NEW_H * 60 + 10#$NEW_M ))
  DELTA=$(( NEW_MIN - PREV_MIN ))

  if (( DELTA < 0 )); then
    # Day rollover is legitimate: late-evening block followed by an early-morning one.
    if (( 10#$PREV_H >= ROLLOVER_EVENING_HOUR && 10#$NEW_H <= ROLLOVER_MORNING_HOUR )); then
      : # rollover, allowed
    else
      cat >&2 <<EOF
BLOCKED: Session transcript violation — timestamp runs backwards (DSM_0.2 §7, check 4/4).

Previous block: ${PREV_H}:${PREV_M}
This block:     ${NEW_H}:${NEW_M}

A block cannot be stamped earlier than the block before it. Observed in S57, where
an Output block stamped 01:52 answered a User block stamped 02:16.

FIX: use the current 24-hour local time for this block. It must be >= ${PREV_H}:${PREV_M}.
Never backdate. If this is a genuine day rollover, the previous block must be at or
after ${ROLLOVER_EVENING_HOUR}:00 and this one at or before 0${ROLLOVER_MORNING_HOUR}:59.
EOF
      exit 2
    fi
  elif (( DELTA > GAP_WARN_MINUTES )); then
    if ! echo "$APPENDED" | grep -qiE '\[RETROACTIVE\]|gap marker|session (pause|resumed)|resumed after'; then
      cat >&2 <<EOF
WARNING: Session transcript — unmarked $(( DELTA / 60 ))h$(( DELTA % 60 ))m gap (DSM_0.2 §7, check 4/4).

Previous block: ${PREV_H}:${PREV_M}
This block:     ${NEW_H}:${NEW_M}

Long pauses are legitimate and this is not blocked. But an unmarked gap makes the
transcript unreadable as a sequence later (S57 carried a 15.5h gap and a 3-day one,
both unmarked, both found only at STAA time three sessions on).

SUGGESTED: note the pause in this block, or prefix it [RETROACTIVE] if you are
recording work done earlier. Never backdate the delimiter.
EOF
    fi
  fi
fi

# All checks passed
exit 0
