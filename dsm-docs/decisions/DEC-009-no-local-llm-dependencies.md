# DEC-009: Remove Local LLM/NLP Dependencies

**Date:** 2026-04-13
**Session:** 47
**Status:** Accepted
**Author:** Alberto Diaz Durana (with AI assistance)

---

## Context

Since Epoch 3, three COULD items have been carried forward in the epoch plan:

1. LLM second-pass validation (TF-IDF filters, LLM confirms cross-references)
2. spaCy NER for entity extraction
3. Sentence transformer embeddings for semantic similarity

These would require significant new dependencies (`spacy`, `sentence-transformers`,
`torch`, `ollama` or similar) and add installation complexity (model downloads,
GPU detection, platform-specific builds).

## Decision

**Drop all three items.** GE will not add local LLM or NLP model dependencies.

## Rationale

1. **The consuming agent IS the LLM.** GE produces structured output (markdown,
   GraphML, Rich tables) that an AI agent reads. The agent can perform NER,
   semantic validation, and similarity analysis on GE's output directly. Running
   a smaller local model to pre-process what a larger model will consume anyway
   is redundant.

2. **GE's value is structural analysis.** Graph topology, reference counting,
   hub scoring, orphan detection, these are deterministic computations that
   don't require probabilistic models. The `--knowledge-summary` design
   (Sprint 16) validates this: compute structure, output markdown, let the
   agent reason over it.

3. **Installation burden.** spaCy models (~500MB), sentence-transformers
   (~400MB), torch (~2GB) would increase the project's footprint by an order
   of magnitude for speculative features with no concrete use case.

4. **No ecosystem demand.** No DSM Central request or portfolio requirement
   has asked for local NLP processing. The knowledge summary request (BL-302)
   specifically asks for graph-topology-derived output.

## Consequences

- LLM second-pass validation, spaCy NER, and sentence embeddings removed
  from the epoch plan COULD list
- No `[llm]` optional dependency group will be created
- If a future use case genuinely requires local NLP (e.g., offline operation
  without an AI agent), this decision can be revisited with a concrete problem
  statement

## Alternatives Considered

- **Keep as COULDs:** Rejected. Carrying speculative items across epochs
  creates false optionality and planning noise.
- **Implement one as an experiment:** Rejected. No concrete hypothesis to test.
  Experiments need a question, not "what if we added NLP?"
