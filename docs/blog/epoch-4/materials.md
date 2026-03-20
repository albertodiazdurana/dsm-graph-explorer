# Epoch 4 Blog Materials

## Article: "Three Layers of Protocol Usage: Measuring What Your AI Agent Actually Uses"

### Conceptual Anchor: Attention Residuals (MoonshotAI)

**Paper:** "Attention Residuals" (arXiv:2603.15031, March 2026)
**Repo:** https://github.com/MoonshotAI/Attention-Residuals

Standard Transformer residual connections accumulate all layer outputs uniformly.
Attention Residuals replaces this with learned, input-dependent selective aggregation:
each layer attends over preceding outputs, keeping what matters and ignoring what
doesn't. Result: equivalent performance to 1.25x more compute.

**The parallel to protocol loading:**

| Attention Residuals | DSM Protocol Usage |
|---|---|
| Standard residuals load all layers uniformly | DSM_0.2 loaded as a whole file into context |
| Each layer's contribution gets diluted | Each protocol section competes for agent attention |
| AttnRes selectively aggregates what matters | BL-090 splits into always-load vs on-demand |
| Content-dependent weighting across depth | Usage-dependent classification across sections |
| Result: same quality, less compute | Result: same coverage, less context consumption |

**Core insight for the article:** Just as Attention Residuals demonstrated that
uniform accumulation of layer outputs dilutes signal and selective aggregation is
more efficient, our four-layer analysis shows that uniformly loading all protocol
sections into an agent's context is wasteful. Some sections are core (always needed),
others are situational (load on demand). Measuring which is which requires data,
not intuition, and that's what EXP-009 provides.

### Four-Layer Methodology (EXP-009)

The methodology distinguishes four evidence layers for measuring protocol usage:

1. **Declared:** What the project's CLAUDE.md explicitly references (section numbers,
   protocol names, template references, @-imports)
2. **Prescribed:** What the session lifecycle skills (/dsm-go, /dsm-light-go, etc.)
   instruct the agent to follow
3. **Observed:** What the agent actually consulted and executed during real sessions
   (evidence from session transcripts)
4. **Designed:** What DSM_0.2's own Module Dispatch Table classifies as core vs
   on-demand modules (contributed by DSM Central review)

Each layer answers a different question:
- Declared = "what does the project claim to need?"
- Prescribed = "what does the methodology prescribe?"
- Observed = "what does the agent actually use?"
- Designed = "what did DSM_0.2 intend?"

Convergence across layers = high-confidence core section.
Divergence = signal for investigation. The designed-vs-observed gap is the strongest
signal: if DSM_0.2 classifies a section as on-demand but spokes use it every session,
it should be reclassified as always-load (and vice versa).

### Standardization Angle

If the methodology works for one spoke (graph-explorer), it becomes a reusable
protocol for any spoke project. Aggregate results across spokes produce an
ecosystem-wide usage map, directly informing BL-090's splitting decisions with data
rather than intuition.

### Narrative Arc

1. **Problem:** DSM_0.2 is 2,458 lines, consumes ~16-20% of context. Loading it all
   is the "uniform residual" approach.
2. **Insight:** Not all sections are equal. Some are core, others situational. But which?
3. **Method:** Three layers of evidence (declared, prescribed, observed) converge on
   a usage profile.
4. **Result:** Data-driven classification of always-load vs on-demand sections.
5. **Broader lesson:** The Attention Residuals analogy, selective aggregation outperforms
   uniform loading, applies beyond neural network architecture to knowledge management
   for AI agents.

### Key Quotes to Use

From the Attention Residuals paper:
> "each layer to selectively aggregate earlier representations via learned,
> input-dependent attention over depth"

Reframed for our context:
> "each session to selectively load protocol sections via usage-dependent
> classification over the ecosystem"
