# Epoch 5 Blog Journal

## 2026-07-06 — Sprint 17: The agents red-carded my format

Sprint 17 was supposed to be a clean, boring migration. The Intrinsic-ToC, the
machine-readable "README for LLMs" that this project generates about a repository,
was going to move from Markdown to TOON, a compact tabular format, to save roughly
10% of the tokens every consuming agent pays to read it. There was a decision record
(DEC-010) with a falsifiable kill-switch: if the format didn't save at least 10%
tokens, halt. There was a phased backlog. It felt like paperwork.

Two multi-agent experiments turned it into the most interesting decision of the epoch.

The first (EXP-010, run in Session 52) was an adversarial assessment: a Fable-5 agent
orchestrating nine cheaper Haiku gatherers, its findings then adjudicated one by one by
Opus. The point of going multi-agent was economic, delegate the token-cheap reading to
a cheap model, reserve the expensive model for judgment, and make the wide read-set
affordable. It came back with 14 confirmed findings. Two mattered. TOON was *increasing*
tokens, not cutting them (the kill-switch had already failed and I hadn't run it). And
deeper: nothing anywhere had ever tested whether the ToC helps an agent navigate at all.
I had spent a sprint optimizing a proxy I was pessimizing, for a benefit I had never
measured.

The second (EXP-011, this session's predecessor S53) went and measured it. Twenty-four
fresh, isolated agents, blind to which arm they were in, each given one navigation
question and one of three contexts: no ToC, the Markdown ToC, or the TOON ToC. I
pre-registered the success criteria and the answer key before a single agent ran, and
I counted tool calls from each agent's transcript rather than trusting what it claimed
(the pilot proved those matched). The ToC arms used about six times fewer tool calls and
were more accurate. And on one task, the orphan-file count, TOON confidently answered 15
where the truth was 112, because its schema silently drops the overflow total. That was
the red card. TOON was not adopted; the ToC stays in Markdown.

The lesson I keep returning to: a fleet of agents was not just faster here, it was a
better *instrument* for the decision than I was alone, because it let me pre-register,
verify against transcripts, and test the real claim instead of the convenient proxy.
