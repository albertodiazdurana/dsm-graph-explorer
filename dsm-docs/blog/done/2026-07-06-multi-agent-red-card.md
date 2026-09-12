# How a Fleet of Agents Red-Carded My Own Decision

*Multi-agent orchestration as a decision instrument, and the format that got a red card.*

## Kickoff: a format gets sent off

It's football season, so let's borrow some terminology to tell the following story.
Last week a team of AI agents red-carded a decision I'd spent a sprint building toward.

I'd committed to migrating my project's "table of contents for LLMs" from Markdown to
TOON, a compact format I picked for exactly one reason: it promised to shave roughly
10% off the tokens every agent pays to read it. The plan was real, a decision record, a
backlog, phased tasks. Then I pointed a fleet of agents at my own reasoning and gave
them one objective: decide, with evidence, whether migrating to TOON was actually worth
it. They didn't just find a bug in the format. They found I'd been optimizing the wrong
thing.

This post isn't really about TOON. It's about using multi-agent orchestration as a
decision *instrument*, a way to make an engineering call and then unmake it with more
rigor than I could have mustered alone. The sharpest thing the fleet caught wasn't a
wrong answer. It was a wrong question: the metric I'd chosen to judge the whole
decision by. Two experiments, thirty-plus agents, one red card.

## The bet: buying tokens with a format

Some context on the pitch. This project generates what I call an Intrinsic Table of
Contents: a machine-readable map of a repository, its files, its sections, its
cross-references, and structural landmarks like hub files and orphaned documents. Think
of it as a README written for an LLM instead of a human, a briefing an agent reads
before it starts work so it knows where everything lives.

That briefing costs tokens. Every agent that reads it pays for it, on every task,
forever. So when a compact tabular format called TOON showed up promising the same
information in fewer tokens, the move looked obvious. I wrote a decision record,
DEC-010, to migrate the table of contents from Markdown to TOON, and I did the responsible thing: I
gave it a falsifiable test. If TOON didn't cut token cost by at least 10% on a
real corpus, the migration was off. A decision with a built-in way to lose is good
discipline.

Here's the part I didn't examine. The test measured tokens. The whole decision
was framed around one number, context consumption, because tokens are easy to count and
easy to argue about. But cheaper is not the same as better. The table of contents exists so an agent
can navigate a repository, and I had chosen to judge formats by their size, not by
whether they actually helped an agent find anything. I'd picked a proxy and mistaken it
for the goal. The test was checking the wrong number.

## Scouting report: an adversarial fleet (EXP-010)

The first fleet was a scouting report. Before the season starts, you send analysts to
study the opposition and write up everything that could go wrong. I did the same thing
to my own plan.

The setup was one capable model, Fable 5, acting as the lead analyst, coordinating nine
cheaper Haiku agents that did the legwork: reading the code, the decision record, the
plan, and the format spec, running the tests, and generating both formats to count
their tokens. The economics were the point. Roughly two-thirds of the nearly three
hundred thousand tokens went to the cheap model doing bulk reading, while the expensive
model spent its budget on judgment. Going wide on the read was only affordable because
most of the reading was cheap.

Then every claim the lead analyst made was checked, one by one, by a third model, Opus,
against the actual code and test output. Not "the agent said so", but "the agent said
so, and here is the file and line that confirms it". Fourteen findings came back, and
all fourteen survived that check. The load-bearing one, the token measurement, I re-ran
myself, and it matched to the token.

Two of those findings mattered. The first: the format I was migrating to did not save
tokens at all. On every real corpus, TOON produced *more* tokens than the Markdown it
replaced, because its long comma-separated paths break into more pieces, not fewer. The
test I had set up would fail. The second finding was worse, and quieter. Nowhere in the
whole plan had anyone checked whether the table of contents helps an agent navigate a
repository in the first place, in any format. I had spent a sprint tuning the price of a
briefing without ever confirming the briefing worked. The scouting report had found not
just a weak player, but a question I'd never thought to ask.

## On the pitch: the A/B (EXP-011)

The scouting report told me what to test. The next fleet went and played the match.

The question was simple to state: does the table of contents actually help an agent
find its way around a repository, and does the format matter? To answer it I wrote eight
navigation tasks, real questions about a real codebase, things like "which file is
referenced most often?", "how many orphaned documents are there?", and "where is this
decision recorded?". Then I gave each question to a fresh, isolated agent in one of three
versions: with no table of contents, with the Markdown one, or with the TOON one.
Twenty-four agents in all, each seeing only its own task, none told which version it had,
none allowed to run the project's own tooling and shortcut the answer.

Two disciplines made the result trustworthy. First, I filed the team sheet before
kickoff: the success criteria and the correct answer to every task were written down
before a single agent ran, so the verdict could not drift to fit the outcome. Second,
the VAR. Rather than trust each agent's own account of how much work it did, I counted
its tool calls straight from its transcript, the actual reads and searches it ran. In a
pilot, the transcript counts matched what the agents reported exactly, so I could rely
on the number for the full match.

The score was not close. The agents with no table of contents got four of eight tasks
right and averaged almost four tool calls per task, often spending those calls only to
arrive at a confident wrong answer. The agents with a table of contents used about six
times fewer tool calls and were far more accurate: the Markdown group answered all eight
correctly, the TOON group seven. The advantage was sharpest exactly where I hoped, on
the questions whose answers come from the repository's graph structure, hub files,
hotspots, orphan counts, which an agent cannot cheaply reconstruct on its own.

And then the red card. One task asked how many orphaned documents the repository has. The
Markdown agent answered 112, correctly. The TOON agent answered 15, because the TOON
format silently drops the "and 97 more" total that Markdown keeps. Same repository, same
question, same zero navigation, and the format alone turned a correct answer into a
confident undercount of nearly a hundred files. I had written that exact prediction down
before the run. It happened precisely as described. TOON did not just cost more, it
misinformed the agent reading it.

## The verdict: what the fleet taught me

The call was clean. The table of contents earns its place, so it stays, and it stays
in Markdown. TOON came off with a red card: it cost more to read and, at least once, it
made the reading agent measurably wrong. The decision record that had committed me to the
migration now carries an amendment reversing it. A sprint's worth of plan, unmade, and I
was glad to unmake it.

What I keep coming back to is that the agents did not just answer my question. They made
a decision and then took it back, with more rigor than I would have managed on my own.
Three habits did the heavy lifting, and I would keep all three.

**Write down the answers before you play.** I fixed the success criteria and the correct
answer to every task before a single agent ran. When the results came in, the verdict
fell out on its own, there was no room to argue the goalposts over to where the ball
happened to land.

**Trust the tape, not the testimony.** An agent's own account of its work is not
evidence; its transcript is. Counting tool calls from the record, after checking in a
pilot that the record and the self-report agreed, is what let me believe the numbers.

**Test the thing you actually care about.** This is the one that stings. My original
error was never TOON, it was the metric. I had judged formats by how many tokens they
cost, when what mattered was whether an agent could find its way. A single wrong turn by
a lost agent costs more than the whole migration would ever have saved. Measure the goal,
not the proxy, and stay ready to change the goal itself the moment you find it was the wrong one.

## On the bench: why not just use RAG?

The obvious signing I left on the bench was retrieval-augmented generation: embed the
repository, fetch the chunks relevant to each question, feed them to the model. So why
not?

Because RAG answers "what does the corpus say about X", and my problem was "how is this
repository laid out". Different jobs. The agent already retrieves, it has search and file
reads; what it lacks on arrival is a map. And the questions the map won on, hub files,
orphan counts, the shape of the whole, are computed facts, not passages you fetch by
similarity. You cannot retrieve an orphan count, you compute it, once, exactly. So the
rule here is simple: the agent is the query engine, and the map's only job is to be
faithful.

Two honest caveats. I never ran RAG head to head against the map, so this is reasoning,
not a measured result. And at large scale, thousands of files, a static map that
truncates its own lists loses exactly what RAG's hierarchical indexing keeps, the orphan
undercount that red-carded TOON is a preview of that limit. For a single repository an
agent can already search, the map wins, and needs no index.

And none of this was reflexive. When three research agents went looking at where the
project should head next, they came back with a clean split: take the structural ideas from the
graph-retrieval world, leave the retrieval machinery behind. Leiden community clustering,
the structural half, with no model-authored summaries, is already on the Sprint 18
roadmap. The map gets richer; the agent stays the query engine. More on that when Sprint
18 kicks off.

## Injury time: the honest caveats

A result is only as good as what you are willing to admit about it, so here is the fine
print.

Eight tasks is a directional signal, not a statistical one. Each version of each task ran
once, so there are no error bars, only a clear lean. One task was flawed: I forgot to
scope it to the documents the map actually covers, so every version answered the whole
repository and it told me nothing. I kept it in the record rather than quietly drop it.
And tokens-to-answer would not meter cleanly per agent, so I lean on the two numbers I
trust, tool calls and success rate, plus a careful count of the maps' own size.

None of that moves the verdict. The table of contents helped, Markdown carried it
faithfully, and TOON earned its card. But a decision instrument you cannot second-guess
is not an instrument, it is a mirror.
