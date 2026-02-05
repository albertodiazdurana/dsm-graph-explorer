# Validating 7,400 Lines of Documentation with Compiler Architecture

**Date:** 2026-02-05
**Author:** Alberto Diaz Durana
**Status:** Published
**Platform:** LinkedIn Article / GitHub
**URL:** https://www.linkedin.com/posts/albertodiazdurana_technicalwriting-docsascode-documentation-activity-7425203346304835585-9fZJ

---

When documentation grows faster than your ability to maintain it, you need tooling. Compilers have solved reference validation for decades. I borrowed their architecture to build a documentation validator.

The [Agentic AI Data Science Methodology (DSM)](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology) grew from 300 lines to 7,400+ lines over five months. With that growth came hundreds of cross-references: "See Section 2.4.8", "Reference Appendix D.2.7", "Per DSM 4.0 guidelines". When I renamed a section, how would I find every reference that now pointed to nothing?

Existing tools like **markdown-link-check** validate URLs. But "Section 2.4.8" isn't a URL, it's a semantic reference to a heading. I needed something different.

The insight: compilers solve exactly this problem. They parse source, build symbol tables, resolve references, and report diagnostics. Documentation is just another domain for the same pattern.

## Why Not Existing Tools?

I tried **markdown-link-check** [1] and **mlc** [2], they validate URLs and file paths but can't handle semantic references. I looked at **coreference resolution** in NLP [3], closer, but designed for sentence-level analysis in prose, not structured documentation.

The gap: no tool validates that "Section 2.4.8" actually exists as a heading in your documentation. That's what I built.

## The Compiler Connection

Code static analysis does exactly what I needed: parsing source files, building symbol tables, and validating that references resolve to real definitions. Compilers have solved this problem for decades [4].

The analogy mapped directly:

| Compiler Stage            | Documentation Equivalent          |
| ------------------------- | --------------------------------- |
| Lexer/Parser builds AST   | Extract headings as nodes         |
| Symbol table construction | Build index of all sections       |
| Name resolution           | Find references in body text      |
| Type checking             | Validate references against index |
| Diagnostic output         | Report errors with locations      |

This wasn't a new problem. It was an old problem in a new domain. That realization saved me from reinventing something that already had established patterns.

## Building the Validator

DSM Graph Explorer follows the compiler pattern through four stages.

**Stage 1: Parsing.** Read each markdown file and extract section headings — numbered sections like "2.4.8", appendix headings like "Appendix D.2.7", DSM document references. Each heading becomes a node with its number, title, and line number. This mirrors how a compiler builds an abstract syntax tree from source code.

**Stage 2: Index building.** Aggregate all parsed sections into a single lookup table mapping section numbers to file paths. This is the documentation equivalent of a compiler's symbol table. The separation matters: parsing handles individual files, indexing combines them into a searchable structure.

**Stage 3: Reference extraction.** A second pass through each file finds cross-references in body text — patterns like "Section 2.4.8" or "See Appendix D.2.7". Each reference captures its source location for error reporting. This is symbol resolution: finding all the places that *use* definitions.

**Stage 4: Validation and reporting.** Check each extracted reference against the section index. If the target exists, valid. If not, broken. The validator distinguishes severity levels — errors for broken section references, warnings for unknown document identifiers.

The pipeline processes 125 files in under a second. The separation of concerns makes each stage testable in isolation, 202 tests, 94% coverage by the end.

## The Real-World Run

With the tool built, I ran it against the DSM repository: 125 markdown files, 7,400+ lines.

```
Scanning 125 files...
Found 6 errors, 0 warnings
```

Six genuine broken references, all pointing to **Section 2.6**, which doesn't exist in the documentation. The tool found real issues.

![Broken reference examples from the integrity report](images/broken-refs-example.png)

*The integrity report shows exactly where broken references occur: file, line number, and the target that couldn't be resolved.*

Beyond the errors, running the validator revealed something interesting about how documentation evolves. Historical files (changelogs, checkpoints) contain references that were valid when written but now point to renamed or removed sections. That's not a bug, it's evidence of evolution. The tool reports both; the human interprets which need fixing.

## A Few Wrong Turns

The path wasn't straight.

**The identifier list assumption.** I started with a hardcoded list of known DSM document identifiers — "DSM 1.0", "DSM 4.0", and a few others. Running against real files generated 152 warnings for "unknown" identifiers. Turns out real documents used short forms ("DSM 1" instead of "DSM 1.0") and referenced documents I'd forgotten about ("DSM 0.1", "DSM 2.1"). The list grew from 5 entries to 11. Design decisions need validation against real data.

**The documentation structure puzzle.** Organizing the project's own documentation took iteration. Where do feedback files go? What about blog drafts? The methodology listed folder names but didn't explain the purpose of each or the relationships between them. Adopting patterns from a concurrent project ([sql-query-agent](https://github.com/albertodiazdurana/sql-query-agent-ollama)) provided the reference implementation I needed. Folder names aren't self-documenting; purpose and contents need explicit specification.

**The regex edge cases.** DSM identifiers use both underscore (`DSM_4.0`) and space (`DSM 4.0`). Appendix headings follow two formats: `# Appendix A: Title` at the top level vs `## A.1 Subsection` for nested sections. Code blocks contain example references that shouldn't be validated. Each discovery refined the patterns. Real files are always messier than test fixtures.

**The trailing period surprise.** The parser worked perfectly on test fixtures — until I ran it against real DSM files. 448 errors seemed alarming until I noticed something odd: references to sections that clearly existed weren't resolving. The culprit? DSM uses trailing periods in section numbers (`### 2.3.7. Title`) but my fixture used no trailing period (`### 2.3.7 Title`). I'd written the fixture from assumption, not observation. A two-character regex fix (`\.?` to allow an optional period) reduced 448 errors to 6. **Lesson:** Before writing tests against synthetic fixtures, verify the fixture format matches actual production data.

## Now What?

Finding errors is only useful if you can act on them. Here's how I'm thinking about the 448:

**Triage by file type.** Errors in active documentation (README, core methodology files) are high priority — those need fixing. Errors in historical files (CHANGELOG, checkpoints) are informational — they document evolution, not bugs.

**Fix actionable references.** For broken references in current docs, options include: updating the reference to the new section number, removing the reference if the concept was deprecated, or adding a note if the section was intentionally removed.

**Accept historical drift.** Changelog entries document what happened at a point in time. "Renamed Section 2.4.11 to Section 2.5.1" becomes more meaningful, not less, when the validator confirms 2.4.11 no longer exists. The drift is the point.

**Use strict mode for CI.** Running with `--strict` in continuous integration catches new broken references before they're committed. Historical drift remains visible but doesn't block the build.

## The Numbers

| Metric                 | Result              |
| ---------------------- | ------------------- |
| Files scanned          | 125                 |
| Broken references found| 6                   |
| Tests written          | 202                 |
| Coverage               | 94%                 |
| Regex patterns         | 6                   |
| Implementation         | ~500 lines          |
| Scan time              | <1 second           |

## What's Next

The validator provides immediate value. But the "Explorer" in DSM Graph Explorer points to where this could go.

**Graph database layer.** Cross-references form a network. Representing them in Neo4j (I'd prototype first with NetworkX for speed) would enable queries like "what sections reference Section 2.4.8?" or "which appendices are orphaned?" The relationship types are clear: REFERENCES, CONTAINS, PARENT_OF. Visualizing this network would reveal structural patterns invisible in flat reports.

**Advanced reference extraction.** The current regex patterns handle explicit references ("Section 2.4.8"). But documentation also contains implicit references — mentions of concepts defined elsewhere. **spaCy NER** [5] could identify these mentions; **sentence transformer embeddings** could match them to their definitions through semantic similarity rather than string matching.

This embeddings approach builds on prior work. In [tfidf-to-transformers-with-disaster-tweets](https://github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets) [6], I demonstrated the progression from TF-IDF to embeddings to transformers for context-sensitive text classification. The same progression applies here: regex (current) → TF-IDF similarity → transformer embeddings for deep semantic alignment.

**Cypher query library.** Common navigation patterns could become reusable queries: find all paths between two sections, identify clusters of tightly-coupled content, surface sections that reference deprecated appendices. A library of these would make the graph immediately useful.

## What I Learned

**Analogies accelerate design.** The compiler analogy didn't just explain the architecture, it shaped it. Recognizing documentation validation as a solved problem in another domain (compilers have done this for decades) saved weeks of exploration. Parse → symbol table → resolve → report. The pattern transferred directly.

**Documentation can be validated like code.** If your docs have semantic cross-references, you can build tooling to validate them. The same patterns that catch undefined variables in code catch broken section references in documentation.

**"Errors" require interpretation.** The 6 broken references are all to Section 2.6, which doesn't exist. Are they bugs to fix, or historical references to a section that was removed? The tool reports; the human interprets.

**Real data validates assumptions.** The identifier list seemed complete until real-world testing showed 152 warnings for "unknown" identifiers (short forms like "DSM 1" vs "DSM 1.0"). Similarly, test fixtures encode assumptions about data format. Running against real files early catches gaps that unit tests miss.

---

If you maintain technical documentation with complex cross-references, try running a validator against it. The errors might surprise you — not because your docs are broken, but because they evolved. Seeing that evolution documented is clarifying.

What would your documentation validation surface?

---

*DSM Graph Explorer is open source: [github.com/albertodiazdurana/dsm-graph-explorer](https://github.com/albertodiazdurana/dsm-graph-explorer)*

*The Agentic AI Data Science Methodology (DSM) is also open source: [github.com/albertodiazdurana/agentic-ai-data-science-methodology](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology)*

---

## References

[1] markdown-link-check. "Check links in markdown files." [github.com/tcort/markdown-link-check](https://github.com/tcort/markdown-link-check)

[2] mlc (Markdown Link Checker). "Fast link checker for markdown." [github.com/becheran/mlc](https://github.com/becheran/mlc)

[3] Stanford NLP Group. "Coreference Resolution." [nlp.stanford.edu](https://nlp.stanford.edu/projects/coref.shtml)

[4] Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. "Compilers: Principles, Techniques, and Tools" (Dragon Book). Chapter 2: A Simple Syntax-Directed Translator.

[5] spaCy. "Industrial-Strength Natural Language Processing." [spacy.io](https://spacy.io/)

[6] Diaz Durana, A. "TF-IDF to Transformers with Disaster Tweets." [github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets](https://github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets)
