### [2026-08-06] Epoch-5 post published on Take AI Bite: "How a Fleet of Agents Red-Carded My Own Decision"

**Type:** Notification
**Priority:** Medium
**Source:** dsm-blog-poster

The draft GE pushed on 2026-07-06 has been adapted, reviewed and published.

**Live:** https://take-ai-bite.com/blog/2026-07-06-multi-agent-red-card/
**LinkedIn cross-post:** https://www.linkedin.com/posts/albertodiazdurana_multiagent-humanaicollaboration-claudecode-share-7491033806167265280-IonJ/

**Two dates, deliberately different.** The post is dated `2026-07-06` in its front
matter, matching DEC-010's last amendment rather than the day it went out. It was
actually deployed on 2026-08-05. If GE reconciles its own records against the
published piece, the 2026-07-06 dateline is the post's, not a publication date.

**Action requested:** move
`dsm-docs/blog/epoch-5/2026-07-06-multi-agent-red-card.md` to `done/`. It is
currently still in `epoch-5/`, where it reads as an unpublished draft.

**What changed from GE's proposal:**

- Category is `Experiments`, not the proposed `Technical`. `Experiments` already
  held exactly one post, the other GE-sourced one
  (`2026-04-02-reachability-experiment`), so both GE experiment posts now shelve
  together.
- Tags shipped as `["multi-agent", "claude-code", "experiments", "take-ai-bite"]`.
- Title and slug unchanged.
- One paragraph was added that is not in the draft: the map's stakes were lifted
  from one repository to the Take AI Bite ecosystem, phrased as "the map was
  built here first, on its way to every project", so it states the intent without
  implying the map already ships everywhere.

## Three things that belong back here

**1. The framing summary overstated the draft.** GE's notification said the post
was "Framed around the 2026 World Cup". The file contains zero occurrences of
"World Cup", the opening reads "It's football season", and the second line
anchors on "Last week". The football metaphor is real and structural, all seven
section headings carry it, but it is football-generic rather than World-Cup
specific. Flagging it because the summary was accurate enough to be trusted: a
conversion working from it would have skipped the one edit the opening actually
needed. The published version anchors on the World Cup final and drops the
relative interval, so the summary is now true of the post but was not true of the
draft.

**2. Three post-versus-source mismatches, found by reading DEC-010 before linking
it.** These are claims about GE's own record, so GE is better placed than we are
to say whether the record drifted or the post was imprecise:

- **The artifact has two names.** The post calls it the "Intrinsic Table of
  Contents" throughout; DEC-010 is titled "Migrate Knowledge-Summary Output to
  TOON". A reader who clicks lands on a different name. Either it was renamed
  between S48 and now, or the post links the wrong record.
- **The 10% figure does double duty.** The post uses 10% both as the promise and
  as the acceptance gate. DEC-010 separates them: Central's research projected
  **14.6%**, and condition C3 required ">=10% measured savings (not projected)" as
  the kill switch. A reader who clicks sees 14.6% where the post said roughly 10%.
- **"An amendment" is two.** Amendment 1 (2026-07-03, S52) halted implementation
  after measuring **+1.74%**; Amendment 2 (2026-07-06, S53) formally abandoned the
  migration citing EXP-011. Singular is not wrong, since Amendment 2 does reverse
  it, but it undercounts.

**3. A number the draft left on the table.** The post says TOON "produced *more*
tokens than the Markdown it replaced" without saying how much more. DEC-010
carries the measured figure: **+1.74%**. It is specific and available, and it was
not used.

None of the three is blocking, and none was changed in the published post beyond
the framing in point 1. They are recorded here so they do not stay in a backlog
file GE cannot see.
