# DSM Graph Explorer - Epoch 2 Plan

**Project Type:** Software Engineering (DSM 4.0 Track)
**Status:** PLANNING
**Prerequisite:** Epoch 1 Complete ([epoch-1-plan.md](epoch-1-plan.md))
**Project Lead:** Alberto Diaz Durana (with AI assistance)

---

## Epoch 2 Overview

### Context

Epoch 1 delivered a working CLI validator that found 448 broken cross-references in the DSM repository. Epoch 2 focuses on two tracks:

1. **Remediation support** — Features to help fix and prevent broken references
2. **Graph exploration** — Transform the reference network into a navigable graph

### Scope

**MUST (Epoch 2 Core):**
- File exclusion patterns (`--exclude` flag and config file)
- Severity levels by file pattern (ERROR for core docs, INFO for historical)
- CI workflow template for GitHub Actions
- Error remediation documentation

**SHOULD (Epoch 2 Enhancements):**
- Semantic cross-reference validation (TF-IDF keyword similarity)
- NetworkX graph prototype (before Neo4j)
- Section rename tracking (`section-renames.yml`)

**COULD (Future Epoch):**
- Neo4j graph database integration
- Cypher query library for navigation
- Web visualization (Neo4j Browser)
- spaCy NER for advanced reference extraction
- Sentence transformer embeddings for deep semantic alignment

---

## Sprint Structure

### Sprint 4: Exclusion & Severity

**Objective:** Implement file exclusion and severity classification to focus validation on actionable errors.

**Deliverables:**
- [ ] `--exclude` CLI flag for file/pattern exclusion
- [ ] `.dsm-graph-explorer.yml` config file support
- [ ] Severity levels by file pattern (ERROR/WARNING/INFO)
- [ ] `--strict` respects severity (only fails on ERROR)
- [ ] Tests for exclusion and severity logic

**Acceptance Criteria:**
- Running with exclusions reduces 448 → ~180 errors
- Config file can specify patterns and severity mappings
- CI can enforce core docs without blocking on historical drift

**Sprint boundary deliverables:**
- [ ] DSM feedback update
- [ ] Decision document (DEC-004: Exclusion and Severity Design)
- [ ] Checkpoint document

---

### Sprint 5: CI Integration & Remediation Docs

**Objective:** Provide ready-to-use CI workflow and documentation for fixing broken references.

**Deliverables:**
- [ ] `.github/workflows/dsm-validate.yml` — GitHub Actions workflow
- [ ] Pre-commit hook script (optional install)
- [ ] `docs/remediation-guide.md` — How to fix broken references
- [ ] `docs/config-reference.md` — Config file options

**Acceptance Criteria:**
- CI workflow runs on PR, fails if core docs have errors
- Remediation guide covers common scenarios
- Config reference documents all options

**Sprint boundary deliverables:**
- [ ] Blog entry (CI integration story)
- [ ] Checkpoint document

---

### Sprint 6: Semantic Validation (TF-IDF)

**Objective:** Detect meaning drift when sections are rewritten but keep their numbers.

**Deliverables:**
- [ ] TF-IDF similarity between reference context and target section title
- [ ] Configurable similarity threshold
- [ ] WARNING for low-similarity references
- [ ] Tests with synthetic drift examples

**Acceptance Criteria:**
- References to renamed sections flagged with low similarity
- False positive rate acceptable (<10%)
- Performance acceptable for 100+ file repositories

**Technical Approach:**
- Use scikit-learn TF-IDF vectorizer
- Compare reference sentence context with section title + first paragraph
- Threshold ~0.3 for warning (tunable)

**Sprint boundary deliverables:**
- [ ] Decision document (DEC-005: Semantic Validation Approach)
- [ ] Checkpoint document

---

### Sprint 7: Graph Prototype (NetworkX)

**Objective:** Build a graph representation of the reference network for analysis.

**Deliverables:**
- [ ] NetworkX graph builder from validation output
- [ ] Node types: FILE, SECTION, REFERENCE
- [ ] Edge types: CONTAINS, REFERENCES
- [ ] Basic graph queries (most referenced sections, orphan sections)
- [ ] Export to GraphML for visualization

**Acceptance Criteria:**
- Graph accurately represents DSM reference structure
- Can identify most-referenced sections
- Can identify unreferenced sections
- Export works with tools like Gephi

**Sprint boundary deliverables:**
- [ ] Blog entry (graph visualization story)
- [ ] Checkpoint document

---

## Future Epochs (Deferred)

### Neo4j Integration (Epoch 3)

- Import NetworkX graph into Neo4j
- Cypher query library for navigation
- Web visualization using Neo4j Browser
- Relationship mapping (REFERENCES, CONTAINS, PARENT_OF)

### Advanced NLP (Epoch 4)

- spaCy NER for entity extraction (tool names, section titles in prose)
- Sentence transformer embeddings for deep semantic alignment
- Reference: [tfidf-to-transformers-with-disaster-tweets](https://github.com/albertodiazdurana/tfidf-to-transformers-with-disaster-tweets)

---

## Dependencies

### New Dependencies (Epoch 2)

```toml
[project.optional-dependencies]
semantic = [
    "scikit-learn>=1.3.0",  # TF-IDF vectorization
]
graph = [
    "networkx>=3.2.0",      # Graph representation
]
```

### Future Dependencies (Epoch 3+)

- neo4j-driver (Neo4j Python client)
- spacy (NER)
- sentence-transformers (embeddings)

---

## Document Health Recommendations

### For DSM Repository Maintainers

Based on Epoch 1 findings, recommendations for maintaining healthy documentation:

1. **Establish validation baseline**
   - Run validator with exclusions to get actionable error count
   - Set target: zero errors in core documentation

2. **Integrate into workflow**
   - Add pre-commit hook for authors
   - Add CI check for PRs touching documentation
   - Review validation report at each release

3. **Handle section renumbering**
   - Search for references to old numbers before renaming
   - Update or deprecate old references
   - Consider maintaining rename history for tooling

4. **Archive strategy**
   - Move deprecated documents to `archive/` folder
   - Exclude archive from strict validation
   - Document that archive references are frozen

5. **Reference style guide**
   - Prefer stable identifiers (section titles) over numbers where possible
   - Use consistent patterns (`Section X.Y.Z` not `see X.Y.Z`)
   - Add context to references ("Section 2.4 (Human Baseline)")

### For Tool Development

1. **Incremental adoption**
   - Start with exclusion-based validation (ignore historical)
   - Add severity levels (ERROR for core, INFO for historical)
   - Then add semantic validation

2. **Feedback loop**
   - Track which errors get fixed vs ignored
   - Adjust severity rules based on usage patterns
   - Add suggested fixes based on common patterns

3. **Performance considerations**
   - Cache parsed documents for repeated runs
   - Incremental validation (only changed files)
   - Parallel file processing for large repos

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **TF-IDF false positives** | Medium | Medium | Tunable threshold, optional feature |
| **Config complexity** | Medium | Low | Good defaults, clear documentation |
| **NetworkX learning curve** | Low | Low | Prototype first, document patterns |
| **Scope creep to Neo4j** | Medium | Medium | Strict epoch boundaries |

---

## Success Criteria (Epoch 2)

**Technical:**
- [ ] Exclusion patterns reduce errors to actionable set
- [ ] CI workflow passes on clean core docs
- [ ] Semantic validation detects renamed sections
- [ ] Graph prototype enables navigation queries

**Process:**
- [ ] Each sprint produces working increment
- [ ] Feedback files updated at sprint boundaries
- [ ] Blog material captured for final writeup

**Deliverable:**
- [ ] Production-ready CLI with exclusion and CI support
- [ ] Remediation guide for DSM maintainers
- [ ] Graph prototype demonstrating future potential

---

**Plan Status:** Draft
**Last Updated:** 2026-02-04
**Previous:** [epoch-1-plan.md](epoch-1-plan.md)
