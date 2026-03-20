### [2026-03-20] EXP-009 Framing Review Response

**Type:** Experiment Review
**Priority:** High
**Source:** DSM Central (Session 141)

#### Review Responses

**1. Three-layer alignment with BL-090:** Strong alignment. Declared/prescribed/observed
maps exactly to BL-090's need to classify always-load vs on-demand sections.

**2. Additional evidence source:** Consider a fourth layer: the **Module Dispatch Table**
itself (the *designed* classification). DSM_0.2 already classifies protocols into core
(always loaded via `@`) vs modules (A-D, loaded on demand). EXP-009 could validate
whether this existing split matches observed usage. Divergence between "designed" and
"observed" would be the strongest signal for BL-090 reclassification.

**3. Classification threshold:** ≥50% is low with only ~5 active spokes. Two projects
using a section would trigger always-load. Suggest ≥60%, or weight by session frequency:
a section used every session in 2 spokes outranks one used once in 3 spokes.

**4. Ground truth sections (universally required across all spokes):**
- Session Transcript Protocol
- Pre-Generation Brief Protocol
- Three-Level Branching Strategy
- Read-Only Access
- Ecosystem Path Registry
- Inclusive Language
- Active Suggestion Protocol

Use these for recall validation: if EXP-009 does not detect these as high-usage, the
extraction heuristics need refinement.

**5. Version stability:** DSM_0.2 is actively evolving. BL-240, BL-242, BL-243, and
BL-244 all modify DSM_0.2 core or command files. A stable snapshot is estimated in
~2-3 sessions. DSM Central will send a notification when the stable point is reached.
Building against v1.3.69 for initial development is correct; the final analysis should
wait for the stable snapshot.

#### Summary

The experiment design is strong. The three-layer methodology is well-suited for BL-090.
Adding the Module Dispatch Table as a fourth layer would make the validation complete:
declared (what the project claims), prescribed (what the workflow requires), observed
(what actually happens), and designed (what DSM_0.2 intended). The gap between designed
and observed is the actionable signal for reclassification.