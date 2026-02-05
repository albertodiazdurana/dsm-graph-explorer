# LinkedIn Post: DSM Graph Explorer

**Date:** 2026-02-05
**Author:** Alberto Diaz Durana
**Status:** Published
**Platform:** LinkedIn
**URL:** https://www.linkedin.com/posts/albertodiazdurana_technicalwriting-docsascode-documentation-activity-7425203346304835585-9fZJ

**Blog:** Validating 7,400 Lines of Documentation with Compiler Architecture

---

When documentation grows faster than you can maintain it, you need tooling. Compilers have solved reference validation for decades. I borrowed their architecture.

The [Agentic AI Data Science Methodology (DSM)](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology) grew from 300 lines to 7,400+ lines since August 2025. With that came hundreds of cross-references: "See Section 2.4.8", "Reference Appendix D.2.7". When sections get renamed, how do you find every reference that now points to nothing?

Existing link checkers validate URLs. But "Section 2.4.8" isn't a URL, it's a semantic reference to a heading. I needed something different.

The solution: compiler architecture. Parse source, build a symbol table, resolve references, report diagnostics. Same pattern that validates variable references in code, applied to section references in documentation.

I ran it against 125 files. It found 6 broken references, all pointing to Section 2.6 which doesn't exist. The tool works.

**The architecture:**
- **Parser** — Extracts section headings and cross-references from markdown
- **Symbol table** — Indexes all sections across files
- **Resolver** — Validates that each reference points to an existing section
- **Reporter** — Outputs diagnostics with file, line, and severity

Lessons along the way:
- Real data validates assumptions: identifier lists, regex patterns, and fixtures all needed refinement after running against actual files
- "Errors" require interpretation: some broken references are bugs to fix; others document how the documentation evolved
- Analogies accelerate design: recognizing this as a solved problem in compilers saved weeks of exploration

The tool works. 202 tests, 94% coverage. Scans 125 files in under a second.

Full write-up covers the compiler-inspired architecture and where this could go next (graph database for navigating the reference network, TF-IDF for semantic drift detection).

Link in comments.

#TechnicalWriting #DocsAsCode #Documentation #SoftwareEngineering #Python #StaticAnalysis

---

## Comment (with blog link)

Full write-up: https://github.com/albertodiazdurana/dsm-graph-explorer/blob/main/docs/blog/epoch-1/blog-draft.md

The architecture: parser → symbol table → resolver → reporter. If you've worked with compilers, you'll recognize the pattern. If not, the blog explains how it maps to documentation validation.

If you maintain technical docs with cross-references, I'd be curious what a validator would find in yours.

Repo: https://github.com/albertodiazdurana/dsm-graph-explorer
