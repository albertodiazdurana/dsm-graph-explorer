# LinkedIn Post: DSM Graph Explorer

**Published:** February 2026
**Blog:** What 448 Broken References Taught Me About Documentation at Scale

---

I ran a cross-reference validator against 7,400 lines of my own documentation.

It found 448 broken references. My first reaction was alarm. Had things really drifted that badly?

Then I looked closer.

Most errors were in CHANGELOG and checkpoint files — historical references that were valid when written. Section 2.4.11 existed in v1.2.3. Renamed in v1.3.0. The changelog entry now points to nothing.

That's not a bug. It's evidence the documentation evolved.

The insight that shaped the solution came from compilers. They've solved reference validation for decades: parse source, build symbol table, resolve references, report diagnostics. Documentation is just another domain for the same pattern.

A few wrong turns along the way:
- Hardcoded identifier list missed short forms (DSM 1 vs DSM 1.0) — real data caught it
- Organizing project documentation took iteration — adopting patterns from another project helped
- Regex edge cases everywhere — real files are messier than test fixtures

The tool works. 145 tests, 98% coverage. But the real value is clarity: knowing which references need fixing vs. which ones document evolution.

Full write-up covers the compiler analogy, architecture, and where this could go next (graph database for navigating the reference network, transformer embeddings for semantic matching).

Link in comments.

#TechnicalWriting #DocsAsCode #Documentation #SoftwareEngineering #Python

---

## Comment (with blog link)

Blog: https://github.com/albertodiazdurana/dsm-graph-explorer/blob/main/docs/blog/blog-draft.md

If you maintain documentation with cross-references, try running a validator against it. The "errors" might tell you something interesting about how your docs evolved.

Repo: https://github.com/albertodiazdurana/dsm-graph-explorer
