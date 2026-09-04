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

## 2026-07-31 — Sprint 18: the null model that ended a feature

Sprint 17 killed a format. Sprint 18 killed a feature, and it took two sessions and
three wrong recommendations to get there.

The plan was concept clusters. Run Leiden community detection over the repository's
cross-reference graph, emit the resulting clusters into the Intrinsic-ToC, and give a
consuming agent a topical map instead of a flat file list. It had been on the roadmap
since Session 49. It sounded obviously good.

The metric I used to justify it, for most of a session, was NMI against directory
labels: if the clusters disagreed with the folder tree, the algorithm was finding
structure the filesystem didn't encode. The number looked encouraging. Then I built a
degree-preserving null model, a graph rewired at random but keeping every node's exact
number of connections, and scored that the same way. The null scored **higher**:
0.1881 against 0.1812 for the real graph.

That is the whole session in one number. My quality metric had been measuring the
*absence* of agreement with the folder tree, not the *presence* of topical structure. A
randomised graph satisfies it just as well, which means it was never evidence for
anything. And once the null was in place, the headline result went with it: the real
Leiden partition beat the rewired graph by 2.8% modularity. Not zero, but nowhere near
enough to build a feature on.

The cause turned out to be sparsity. Only about 25% of files in this repository carry a
single cross-reference, and around 99% of sections are orphans. You cannot cluster a
graph that is mostly disconnected dust. Worse, when I went back to check *why* Leiden was
on the roadmap at all, I found the premise had already collapsed: Session 49 had taken
the clustering algorithm from GraphRAG while rejecting GraphRAG's LLM entity extraction
as incompatible with an earlier decision. But the extraction is what *produces* something
clusterable. GraphRAG doesn't cluster document cross-references at all. I had carried the
algorithm forward and left behind the thing that feeds it.

The move that finally ended it was not another comparison. I had spent two sessions
ranking four candidate designs against each other and going in circles. So I stopped
comparing and re-read the vision document that defines what this artifact is for.
Clustering appears nowhere in it. The four components it specifies for this layer,
project structure, hub documents, cross-reference hotspots, orphan files, all shipped
back in Sprint 16. Clustering would have been an unspecified fifth, and the whole option
space I'd been agonising over was optional scope against an aim nobody had re-read since
the premise that introduced it was refuted.

Two things I want to keep from this one.

The first is that pre-registration works precisely when it hurts. Before running the null
model I wrote down what would kill the design: a flat curve across the weight sweep. NMI
came back flat at 0.755 to 0.767 across every setting, and the design died on a condition
I could no longer renegotiate. The same thing happened again at the end, when I predicted
that PageRank would collapse to the existing degree-based ranking on a graph this sparse
and pre-registered the threshold before checking. It didn't collapse. Nine of ten
positions moved. My own claim, refuted by my own test, which is the only reason I trust
the answer.

The second is about honesty in the record. Three recommendations across these two
sessions, three key claims overturned by cheap measurement, twice *after* I had already
approved them. The pattern is consistent and worth naming precisely: the measurements
held up, the inferences layered on top of them did not. That distinction is now written
into the decision record beside every justification, so a future reader knows which parts
to trust.

Sprint 18 shipped no feature. Its deliverables are a research file, a validation gate,
and a decision to stop. I'd rather that than a clustering section nobody could defend.
