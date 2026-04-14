### [2026-04-07] heating-systems-conversational-ai: contribution playbook request

**Type:** Question / Knowledge Transfer
**Priority:** Medium
**Source:** heating-systems-conversational-ai (DSM spoke)
**Requestor:** Sprint 1 / Sprint 2 boundary work
**Response needed by:** Sprint 2 entry (no hard date; ideally before Sprint 2 starts)

## Context

The heating-systems-conversational-ai project just made an architectural
decision to use a hybrid LangGraph + Haystack design. Decision record:
`~/_projects/heating-systems-conversational-ai/dsm-dsm-docs/decisions/2026-04-07_orchestration-framework.md`

Companion deepened research:
`~/_projects/heating-systems-conversational-ai/dsm-dsm-docs/research/2026-04-07_haystack-vs-langgraph-deepened.md`

A central finding from the research: Haystack's `OllamaChatGenerator`
tool-calling support is **undocumented**. The Agent component docs (v2.27)
show only OpenAI examples, the Ollama integration page does not mention a
`tools` parameter, and the `haystack-core-integrations` README does not
surface tool-calling. The underlying Ollama API has supported tool calls
since July 2024.

The decision treats this gap as a **contribution opportunity**: in Sprint 2,
run an empirical spike to determine whether Haystack `OllamaChatGenerator`
supports `tools=[...]` in practice, and produce an upstream artifact based
on the result (working example PR, caveats PR, or issue report).

## Why I am asking graph-explorer

You have prior experience contributing PRs to tools that were not properly
documented when you needed to use them. Your implementation worked despite
the absence of prior knowledge, and you produced upstream contributions
afterward.

This project will be in a similar position in Sprint 2.

## What I am asking

If you are willing to share, I would like to understand:

1. **Which tool** did you contribute to, and what was the documentation gap?
2. **Your playbook** for "discover undocumented behavior → upstream
   contribution":
   - How did you decide what was worth contributing vs keeping local?
   - How did you separate "the tool is broken" from "the tool works,
     the docs do not"?
   - What did you write before opening the PR? (notes, repro case,
     tests, draft docs?)
3. **Maintainer interaction:**
   - How responsive were the maintainers?
   - Did you open an issue first, or go straight to a PR?
   - Any patterns that worked (or did not work) for getting merged?
4. **Reusable artifacts:**
   - Do you have a checklist, template, or process doc I could adapt?
   - Anything you wish you had known before starting?
5. **Take-ai-bite alignment:**
   - If this kind of contribution work is a take-ai-bite-recognized
     pattern, where is it documented? Should I align my contribution with
     a specific format?

A short response is fine (bullet points, links to your prior PR, or a
pointer to a doc in your repo). I do not need a polished writeup. Anything
you have already written that I can read is more valuable than something
you have to compose now.

## Output

I will use the answers to:

1. Plan the Sprint 2 spike on Haystack `OllamaChatGenerator` tool-calling
2. Decide issue-vs-PR strategy based on spike outcome
3. Document the contribution workflow in this project's
   `dsm-dsm-docs/decisions/` so it can be reused by future spokes

If the response reveals a reusable playbook, I will write it back to
DSM Central as feedback for inclusion in DSM_0.2 or a relevant module.

## How to respond

Move this entry to `_inbox/done/` after responding. Response can be:

- A new file in this repo's `_inbox/` directed back at
  heating-systems-conversational-ai
- A reply added to this file before moving to done
- A pointer to existing files in graph-explorer (path is sufficient)

No action required if you do not have time; this is medium priority and
the spike can proceed without prior playbook input (though it would be
slower and less rigorous).