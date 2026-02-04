# DSM Graph Explorer: Research Material Handoff

**Date:** February 1, 2026  
**Project:** https://github.com/albertodiazdurana/dsm-graph-explorer  
**Status:** Phase 0 complete, Phase 1 in progress

---

## 1. Project Summary

**What it does:** Validates cross-references in documentation repositories by parsing semantic textual references (e.g., "See Section 3.2.1", "per Appendix A.1") and building a dependency graph to check integrity.

**Original hypothesis:** This is a novel approach not covered by existing tools.

**Revised understanding:** The NLP is well-established (coreference resolution, discourse parsing). The value is in the **applied tooling layer** ; packaging known techniques for a specific use case.

---

## 2. Related NLP Research Fields

### 2.1 Coreference Resolution

**Definition:** Linking mentions that refer to the same entity (e.g., "it", "the system", "this approach" → their referents)

**Key surveys:**
- Liu et al. (2023) "A Brief Survey on Recent Advances in Coreference Resolution" - Springer
  - Covers 10 metrics, 18 datasets, 4 technical trends
  - https://link.springer.com/article/10.1007/s10462-023-10506-3

- Porada et al. (2024) "A Controlled Reevaluation of Coreference Resolution Models"
  - Compares encoder vs decoder models
  - Encoder-based still outperforms decoder-based for accuracy and speed
  - https://arxiv.org/abs/2404.00727

**Foundational papers:**
- Lee et al. (2017) "End-to-End Neural Coreference Resolution" - ACL 2017
- Lee et al. (2018) "Higher-order Coreference Resolution with Coarse-to-Fine Inference"
- Bohnet et al. (2023) - seq2seq transition-based system, SOTA on mT5-XXL

**Current state:**
- LLMs still struggle with coreference (Gan et al., 2024)
- Encoder-based models outperform decoder-based
- Multilingual shared task: CorefUD (17 languages)
- Benchmark: OntoNotes, GAP dataset

**Leaderboard:** http://nlpprogress.com/english/coreference_resolution.html

### 2.2 Discourse Parsing

**Definition:** Parsing document structure to understand how clauses, sentences, and text spans connect into coherent text.

**Two main frameworks:**

| Framework | Structure | Scope |
|-----------|-----------|-------|
| **RST (Rhetorical Structure Theory)** | Tree structure | Whole document |
| **PDTB (Penn Discourse Treebank)** | Local relations | Adjacent sentences |

**Key surveys:**
- Hou et al. (2020) "RST: A Comprehensive Review" - ScienceDirect
  - Theory, parsing methods, applications
  - https://www.sciencedirect.com/science/article/abs/pii/S0957417420302451

- Kong et al. (2022) "A Survey of Discourse Parsing" - Frontiers of Computer Science
  - RST-style, PDTB-style, dialogue parsing
  - https://link.springer.com/article/10.1007/s11704-021-0500-z

**Foundational papers:**
- Mann & Thompson (1988) "Rhetorical Structure Theory: Toward a functional theory of text organization" - Original RST paper
- Morey et al. (2018) "A Dependency Perspective on RST Discourse Parsing" - MIT Press
  - Links discourse parsing to dependency parsing

**Key datasets:**
- RST-DT: 385 WSJ documents
- PDTB 3.0: Penn Discourse Treebank
- STAC: Multiparty dialogue corpus

### 2.3 Named Entity Recognition (NER)

Identifies entities (people, places, sections, figures) in text. Relevant for extracting section references.

### 2.4 Relation Extraction

Finds relationships between entities. Relevant for building the reference dependency graph.

---

## 3. Existing Documentation Tools

### 3.1 Markdown Link Checkers

| Tool | What it does | Limitation |
|------|--------------|------------|
| **remark-validate-links** | Validates `[text](url)` hyperlinks in Git repos | Only hyperlinks, not prose references |
| **markdown-link-check** | Checks if URLs are alive (200 OK) | External links only |
| **linkcheckmd** | Fast async link checking (10K files/sec) | Only hyperlink format |
| **mdrefcheck** | CLI for markdown link validation | Same limitation |
| **webhintio/markdown-link-validator** | Validates internal + external links | Only hyperlink format |

**Key insight:** All these tools validate `[text](url)` syntax. None parse prose references like "See Section 3.2".

### 3.2 Documentation Build Tools

| Tool | Cross-reference handling |
|------|-------------------------|
| **Sphinx** | `{ref}` syntax; warns on broken refs during build |
| **MyST-parser** | Cross-reference targets with `{#id}` attributes |
| **MkDocs** | Limited; mostly hyperlink validation |

### 3.3 Knowledge Graph Tools

| Tool | What it does |
|------|--------------|
| **Neo4j** | Graph database for storing relationships |
| **neo4j-graphrag-python** | KG construction from unstructured data |
| **LangChain + Neo4j** | RAG with knowledge graphs |

---

## 4. Gap Analysis

### What exists:
- Hyperlink validation (markdown-link-check, remark-validate-links)
- RST/PDTB discourse parsing (academic NLP)
- Coreference resolution (academic NLP)
- Knowledge graph construction (Neo4j ecosystem)

### What's missing (DSM Graph Explorer opportunity):
1. **Prose reference parsing** ; "See Section 3.2" not `[link](url)`
2. **Methodology-specific validation** ; DSM framework conventions
3. **Graph visualization** of document structure dependencies
4. **CI/CD integration** for documentation repositories
5. **Actionable tooling** ; not academic research, practical tool

---

## 5. Technical Approach Comparison

### Code Static Analysis (inspiration)

| Technique | Code world | Documentation world |
|-----------|------------|---------------------|
| **Parsing** | Source → AST | Markdown → structured nodes |
| **Symbol resolution** | Variable use → declaration | "Section 3.2" → actual section |
| **Dependency analysis** | Module imports | Section references |
| **Dead code detection** | Unreachable code | Orphaned sections |
| **Reference validation** | Function exists? | Section exists? |

### Relevant libraries for implementation:

| Library | Purpose |
|---------|---------|
| **pulldown-cmark** (Rust) | Markdown parsing with offset tracking |
| **mistune** (Python) | Fast markdown parser |
| **spaCy** | NER, dependency parsing |
| **Neo4j** | Graph storage and querying |
| **NetworkX** | Python graph analysis |

---

## 6. Revised Project Positioning

### Not novel:
- NLP for reference extraction (coreference, NER)
- Discourse structure analysis (RST)
- Graph-based document modeling

### Novel/valuable:
- **Applied tooling** ; packaging NLP for documentation validation
- **Domain-specific** ; DSM framework conventions
- **Developer-focused** ; CI/CD integration, actionable output
- **Graph visualization** ; dependency exploration

### Honest framing:
"The NLP for parsing references is well-established. What I'm building is the applied tooling layer ; taking those techniques, combining them with graph databases, and creating actionable validation for documentation repositories. It's engineering, not research."

---

## 7. Key References (Quick Access)

### Surveys (start here)
1. Liu et al. (2023) - Coreference survey: https://link.springer.com/article/10.1007/s10462-023-10506-3
2. Hou et al. (2020) - RST comprehensive review: https://www.sciencedirect.com/science/article/abs/pii/S0957417420302451
3. Kong et al. (2022) - Discourse parsing survey: https://link.springer.com/article/10.1007/s11704-021-0500-z

### Benchmarks
4. NLP-Progress Coreference: http://nlpprogress.com/english/coreference_resolution.html
5. CorefUD Shared Task (multilingual): https://arxiv.org/html/2509.17796v1

### Foundational
6. Lee et al. (2017) - End-to-end neural coreference - ACL 2017
7. Mann & Thompson (1988) - RST original paper
8. Morey et al. (2018) - Dependency perspective on RST: https://direct.mit.edu/coli/article/44/2/197/1602/

### Recent developments
9. Porada et al. (2024) - Coreference model reevaluation: https://arxiv.org/abs/2404.00727
10. Gan et al. (2024) - LLMs as coreference resolvers (they struggle)

---

## 8. Potential Extensions

Based on research, potential directions for DSM Graph Explorer:

### Extension A: Use spaCy for NER
Extract section references using Named Entity Recognition rather than regex patterns.

### Extension B: RST-style structure
Parse document into RST tree to understand nucleus-satellite relationships between sections.

### Extension C: Embedding-based similarity
Use sentence embeddings to find semantically similar sections (potential duplicates or related content).

### Extension D: LLM-assisted extraction
Use LLM to identify references that regex/NER miss (e.g., "the algorithm described above").

---

## 9. Interview Application

### For JetBrains interview:
"I'm building a tool that validates cross-references in documentation repositories. The NLP is well-established ; coreference resolution, discourse parsing. My contribution is the applied tooling: parsing semantic references from prose, building dependency graphs, and creating CI/CD-integrated validation. It's the same approach used in code static analysis ; parsing structured content, resolving symbols, validating references ; applied to documentation."

### Key parallel:
Code static analysis : DSM Graph Explorer :: IDE features : Documentation tooling

---

## 10. Next Steps for Project

1. [ ] Read Liu et al. (2023) coreference survey
2. [ ] Explore spaCy NER for section reference extraction
3. [ ] Prototype with NetworkX before Neo4j
4. [ ] Define DSM-specific reference patterns
5. [ ] Build validation rules based on framework conventions
