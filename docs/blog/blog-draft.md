# What 448 Broken References Taught Me About Documentation at Scale

**By Alberto Diaz Durana | February 2026**

---

This post is about what happens when documentation grows faster than your ability to maintain it.

I built a tool to validate cross-references in markdown files. When I ran it against my own documentation — 7,400 lines across 6 files — it found 448 broken references. My first reaction was alarm. Had things really drifted that badly?

Then I looked closer. Most of those "errors" weren't bugs. They were evidence that the documentation had evolved.

## The Problem

It started with growth. The [Agentic AI Data Science Methodology (DSM)](https://github.com/albertodiazdurana/agentic-ai-data-science-methodology) began as a single document — a workflow framework for data science projects: 3 documents and 300+ lines. Real-world use added feedback: templates, checklists, appendices, domain adaptations. After 5 months and multiple projects, it grew to 7,400+ lines with over 100 cross-references between sections.

Then I noticed something uncomfortable. When Section 2.4.8 mentions "See Appendix D.2.7," how do I know that appendix still exists? When I rename a section during a refactor, how do I find all the places that reference it?

I tried existing tools. **markdown-link-check** [1] and **mlc** [2] validate URLs and file paths — but DSM uses semantic references. "Section 2.4.8" isn't a URL. It's a pointer to a heading that might have been renamed or removed. These tools couldn't help.

I looked at **coreference resolution** in NLP [3] — the task of identifying when different expressions refer to the same entity. Closer, but designed for sentence-level analysis in prose, not structured documentation.

Then I found the analogy that changed everything.

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

The pipeline processes 122 files in under a second. The separation of concerns makes each stage testable in isolation — 150 tests, 98% coverage by the end.

## The Real-World Run

With the tool built, I ran it against the actual DSM repository.

```
Scanning 122 files...
Found 448 errors, 0 warnings
```

448 errors. That's a lot.

But when I examined the report, a pattern emerged:

![Broken reference examples from the integrity report](images/broken-refs-example.png)

*Sample broken references from the integrity report. Most appear in CHANGELOG.md and checkpoint files — historical documents that reference sections as they existed at the time of writing.*

Most errors came from CHANGELOG and checkpoint files — **historical references that were valid when written**. Section 2.4.11 existed in version 1.2.3. It was renamed in version 1.3.0. The CHANGELOG entry documenting that change now references a section that no longer exists.

That's not a bug. It's evidence that the documentation evolved.

This distinction matters. A broken reference in current documentation is actionable — it should be fixed. A broken reference in a historical changelog is informational — it documents the evolution. The tool reports both. The human interprets which category each error falls into.

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
| Files scanned          | 122                 |
| Cross-reference errors | 448 → 6 (after fix) |
| Tests written          | 150                 |
| Coverage               | 98%                 |
| Regex patterns         | 6                   |
| Implementation         | ~400 lines          |

## What's Next

The validator provides immediate value. But the "Explorer" in DSM Graph Explorer points to where this could go.

**Graph database layer.** Cross-references form a network. Representing them in Neo4j (I'd prototype first with NetworkX for speed) would enable queries like "what sections reference Section 2.4.8?" or "which appendices are orphaned?" The relationship types are clear: REFERENCES, CONTAINS, PARENT_OF. Visualizing this network would reveal structural patterns invisible in flat reports.

**Advanced reference extraction.** The current regex patterns handle explicit references ("Section 2.4.8"). But documentation also contains implicit references — mentions of concepts defined elsewhere. **spaCy NER** [5] could identify these mentions; **sentence transformer embeddings** could match them to their definitions through semantic similarity rather than string matching.

This embeddings approach builds on prior work. In [tfidf-to-transformers-with-disaster-tweets](https://github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets) [6], I demonstrated the progression from TF-IDF to embeddings to transformers for context-sensitive text classification. The same progression applies here: regex (current) → TF-IDF similarity → transformer embeddings for deep semantic alignment.

**Cypher query library.** Common navigation patterns could become reusable queries: find all paths between two sections, identify clusters of tightly-coupled content, surface sections that reference deprecated appendices. A library of these would make the graph immediately useful.

## What I Learned

**Documentation can be validated like code.** The same patterns compilers use — parse, build symbol table, resolve, report — apply to structured documentation. If your docs have semantic cross-references, you can build tooling to validate them.

**"Errors" require interpretation.** 448 broken references sounds like failure. Most are historical drift — evidence of evolution, not bugs. The tool reports; the human interprets.

**Real data validates design decisions.** The identifier list seemed complete until real-world testing showed 152 warnings. Design → Test → Real-world → Fix is a necessary loop.

**Analogies accelerate design.** The compiler analogy didn't just explain the architecture — it shaped it. Recognizing documentation validation as a solved problem in another domain saved weeks of exploration.

**Fixtures encode assumptions.** Test fixtures work great for TDD — until you discover real data looks different. The trailing period bug (448 false positives) would have been caught by opening one real file before creating the fixture. Before writing tests against synthetic fixtures, verify the fixture format matches actual production data.

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
