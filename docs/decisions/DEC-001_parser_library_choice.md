# DEC-001: Parser Library Choice

**Date:** 2026-02-01
**Status:** Accepted
**Sprint:** Sprint 1 (Parser MVP)
**Decision maker:** Alberto Diaz Durana

---

## Context

The DSM Graph Explorer needs to extract section headings and cross-references from markdown files. The first design decision is what parsing approach to use.

## Options Considered

### Option 1: Pure regex (CHOSEN)

- Line-by-line iteration with regex patterns for headings and cross-references
- No additional dependencies
- Full control over pattern matching
- Patterns: `Section X.Y.Z`, `Appendix X.Y`, `DSM_X.Y`

### Option 2: mistune

- Fast Python markdown parser
- Produces AST from markdown
- Would handle heading extraction natively
- Overkill for our use case: we only need headings and regex on body text

### Option 3: markdown-it-py

- Feature-rich Python port of markdown-it
- Plugin ecosystem
- Most capable but heaviest dependency
- Would require learning the plugin API for custom cross-reference extraction

## Decision

**Pure regex.** The DSM cross-reference patterns are structured and predictable (`Section X.Y.Z`, `Appendix X.Y`, `DSM_X.Y`). These don't require a full markdown AST — line-by-line processing with regex is sufficient, simpler, and has zero additional dependencies.

## Rationale

1. **Patterns are structured, not ambiguous.** DSM follows strict formatting conventions. Regex handles this directly without the overhead of a full parser.
2. **Aligns with code static analysis pipeline.** The research review (see `docs/research/`) confirmed our approach follows the well-established parsing → symbol resolution → validation pipeline. Regex is the standard tool for tokenization in this pattern.
3. **No dependency risk.** Zero additional packages means no version conflicts or supply chain concerns.
4. **Upgrade path is clear.** If edge cases emerge (e.g., prose references like "the section described above"), spaCy NER is a validated upgrade path (see research document, Extension A).

## Trade-offs

- **Pro:** Simple, no dependencies, fast, full control
- **Con:** Won't handle ambiguous/prose references. Won't parse markdown structure (bold, links, etc.)
- **Mitigation:** Track missed patterns when running against real DSM files in Sprint 3. Evaluate if spaCy is needed post-MVP.

## Implementation

- Heading extraction: 3 regex patterns for numbered (`1.2.3`), appendix heading (`Appendix A:`), and appendix subsection (`A.1.2`)
- Cross-reference extraction: 3 regex patterns for Section, Appendix, and DSM references
- Code block skipping: state toggle on fenced ``` delimiters

---

**References:**
- Research review: `docs/research/handoff_graph_explorer_research.md`
- Sprint plan: `docs/plan/SPRINT_PLAN.md` (Resolved Questions table)
