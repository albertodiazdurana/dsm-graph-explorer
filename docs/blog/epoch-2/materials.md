# Epoch 2 Blog Materials

**Date range:** 2026-02-04 to 2026-03-03
**Project:** DSM Graph Explorer
**Epoch theme:** Productionization, from prototype to validation platform
**Status:** Draft materials (consolidated from journal entries)
**Target Platform:** LinkedIn posts, technical blog, or combined retrospective
**Target Audience:** Developers working with AI coding assistants, documentation engineers, data scientists

---

## Epoch 2 Narrative Arc

The overarching story is **productionization**: taking a working prototype (448 errors found, 6 real) and turning it into a deployable validation platform. Each sprint added a layer:

1. **Sprint 4:** Made errors actionable (exclusion, severity, config)
2. **Sprint 5:** Made validation automatic (CI, pre-commit, docs)
3. **Sprint 6:** Made validation semantic (TF-IDF, drift detection)
4. **Sprint 7:** Made structure queryable (graph builder, queries, export)
5. **Sprint 8:** Made conventions enforceable (linting, 6 style checks)

The compiler architecture from Epoch 1 (parser -> symbol table -> resolver -> reporter) was extended without being replaced. Each new capability plugged into the existing pipeline or ran alongside it. New features compose rather than conflict.

**Cumulative metrics:**
- Tests: 150 -> 331 (+181)
- Source modules: 4 -> 10
- Experiments: 4 (EXP-001 through EXP-004, plus EXP-003b)
- Decisions: 2 new (DEC-004, DEC-005)
- DSM feedback: 31 methodology entries, 26 backlog proposals

---

## Working Title Options (Epoch-Level)

1. "From Prototype to Platform: Productionizing a Documentation Validator in 5 Sprints"
2. "The 448->6->0 Journey: Making Error Reports Actionable"
3. "Dog-Fooding Your Methodology: What Happens When Tools Validate Their Creators"
4. "From Tool to Pipeline: How Each Sprint Added a Validation Layer"

---

## Sprint-Level Blog Threads

### Sprint 4: Exclusion & Severity

**Narrative threads:**
- From 448 errors to 10: the journey of making error reports actionable
- Config files as documentation: `.dsm-graph-explorer.yml` tells you what to exclude and why
- Severity levels let teams triage: ERROR for core docs, INFO for drafts, WARNING as default
- Post-validation override: a clean pattern for separating "what's wrong" from "how bad is it"

**Title options:**
1. "Making Error Reports Actionable: Exclusion Patterns and Severity Levels"
2. "Post-Validation Override: Separating Detection from Triage"

**Key insight:** Research-first planning pays off. The research phase grounded the fnmatch and Pydantic choices. Sprint 4 implementation had no surprises; every design decision was pre-validated.

---

### Sprint 5: CI & Documentation (including WSL Migration)

**Narrative threads:**
- From tool to pipeline: adding CI, pre-commit, and docs turns a CLI tool into a deployable validation system
- The spoke-repo problem: what happens when your tool validates references to documents it can't see
- Documentation as product: user guides vs project-management docs, and why they need different homes
- Collaboration protocol convergence: three iterations of the same problem, each making the mechanics more explicit

**Title options:**
1. "From Tool to Pipeline: Adding CI to a Documentation Validator"
2. "The Spoke-Repo Problem: Validating References You Can't See"

**Key insight:** The spoke-repo config pattern. When a project references DSM sections defined in another repository, those references always appear broken. The solution: set `docs/**/*.md` to INFO severity. Findings stay visible but don't block CI. First reusable configuration pattern to emerge.

#### WSL Migration Post Draft

**Title options:**
1. "From Windows to WSL: Migrating an AI-Assisted Documentation Ecosystem"
2. "Environment Standardization for AI Coding Projects: A Practical Migration Story"
3. "The Venv Portability Trap and Other Migration Lessons"

**Hook (recommended, decision-first):**
"DEC-004: WSL Migration for Cross-Platform Development. Status: Approved. That's how our move from Windows to WSL2 started, not with frustration but with a structured decision record. We evaluated three options, documented trade-offs, and created a migration guide before touching any files."

**Story arc:**
1. Context: Two interconnected repos (DSM Central ~7,400 lines markdown, Graph Explorer Python CLI), hub-and-spoke model
2. Trigger: Sprint 5 CI integration planning, GitHub Actions runs Linux, dev was Windows
3. Decision process: DEC-004 with three options evaluated
4. Migration: path mapping, config updates, migration guide
5. Gotcha: venv portability trap (shebangs embed absolute paths)
6. Verification: pytest 202 passed, dsm-validate 125 files
7. Lessons: venvs don't travel, document before migrate, decision records work, naming helps

**Key takeaways:**
1. Environment decisions deserve architecture rigor (DEC-004 with options, trade-offs, success criteria)
2. Python venvs are environment-specific (shebangs contain absolute paths, always recreate)
3. Hub-and-spoke simplifies coordination (only @ reference in CLAUDE.md needed updating)
4. Dev/CI parity reduces surprises (same OS, same Python, same paths)

**Call to action (recommended):**
"We treat infrastructure decisions the same way we treat code decisions: with a decision record, options analysis, and defined success criteria. DEC-004 is in the project repo if you want to see the template."

---

### Sprint 6: Semantic Validation

**Narrative threads:**
- When synthetic tests lie: how 25 hand-crafted cases produced F1=0.889 but real data revealed F1=0.663
- The precision-recall trade-off in documentation tools: why conservative is correct
- Agent-assisted labeling: a human-AI collaboration pattern for ground truth creation
- Empty excerpts as a content quality signal: when your tool's weakness reveals your documentation's weakness
- From experiment to amendment: how EXP-003b changed a decision that EXP-003 established

**Title options:**
1. "When Your Synthetic Tests Are Too Optimistic: Validating NLP Thresholds Against Real Data"
2. "Perfect Precision, Imperfect Recall: The Right Failure Mode for Documentation Tools"
3. "1,191 Cross-References Later: What Real-World Data Teaches You About TF-IDF Thresholds"

**Key insight:** The synthetic vs real data gap. EXP-003 (synthetic) achieved F1=0.889 with recall=0.800. EXP-003b (real) dropped to F1=0.663 with recall=0.496. Synthetic cases were too clean: rich excerpts, distinct vocabulary. Real content has empty excerpts, short titles, vocabulary overlap. The experiment's limitations section explicitly called out this risk, and real data confirmed it.

**Data points:**
- 1,191 cross-reference rows from actual DSM repository
- 128 near-threshold rows labeled via agent-assisted process (~15 minutes)
- Precision=1.000, Recall=0.496, F1=0.663 at threshold 0.10
- All 63 disagreements were false negatives (conservative failure mode)
- Threshold amended from 0.10 to 0.08 based on evidence

---

### Sprint 7: Graph Prototype

**Narrative threads:**
- The CQRS framing made concrete: markdown as write model, graph as read model, builder as projection
- Performance experiment as confidence builder: when your targets pass by 50x, you know the approach scales
- Graph queries that reveal documentation structure: which sections are most referenced? Which are orphaned?
- The recurring protocol pattern: why approval gates need explicit multiplicity

**Title options:**
1. "Turning Documentation Into a Queryable Graph: From Markdown to NetworkX"
2. "The CQRS Architecture You Didn't Know Your Documentation Needed"
3. "50x Performance Headroom: When Your Experiment Results Surprise You"

**Key insight:** The graph IS the read model. Markdown files are the write model (human-authored); the NetworkX DiGraph is the read model (agent-queryable). The graph builder is the projection function. This is not a metaphor; it is the actual architecture.

**Data points:**
- Build time: 104ms (target <5s), 50x margin
- Query times: <1ms (target <100ms), 100x margin
- Memory: 12.7MB (target <100MB), 8x margin
- Two node types (FILE, SECTION), two edge types (CONTAINS, REFERENCES)

---

### Sprint 8: Convention Linting

**Narrative threads:**
- Convention linting as executable style guides: turning prose rules into automated checks
- Independent pipelines: why `--lint` and `--strict` are separate entry points with shared infrastructure
- The transcript protocol bug: when a process artifact becomes load-bearing infrastructure
- Per-rule severity overrides: giving users control over what matters in their context

**Title options:**
1. "Making Style Guides Executable: Convention Linting for Documentation Repositories"
2. "Six Checks, One Flag: Adding Convention Linting to a Documentation Validator"
3. "When Your Session Log Becomes Load-Bearing: Process Artifacts in AI-Assisted Development"

**Key insight:** Convention checks as documentation standards. Each lint rule encodes a DSM convention that was previously only in prose. E001 says "use text labels, not emoji." W001 says "use commas, not em-dashes." Making conventions executable turns style guidelines into enforceable rules.

**Six checks:**
- E001: emoji usage (WARNING:/OK:/ERROR: instead)
- E002: TOC headings (DSM uses hierarchical numbering)
- E003: mojibake encoding (double-encoded UTF-8)
- W001: em-dash punctuation (use commas/semicolons)
- W002: CRLF line endings (use LF)
- W003: backlog metadata (required fields validation)

---

## Cross-Cutting Themes

### 1. Experiments as First-Class Artifacts
Four experiments produced evidence for every non-trivial design decision. The pattern: experiment -> results -> decision document -> implementation. EXP-003b was the standout, revealing the synthetic-vs-real gap.

### 2. Feedback as Product
31 methodology entries and 26 backlog proposals are not just process overhead; they are a deliverable that improves DSM itself. The spoke project's findings (user guides gap, inbox location, convention linting need) became methodology changes.

### 3. Protocol Evolution Through Practice
The collaboration protocol was refined 5 times, each iteration more explicit. The three-gate model (concept -> implementation -> run) emerged from Sprint 7's protocol violation. Protocols improve through failure, not through specification alone.

### 4. Independent Pipelines, Shared Infrastructure
Each major feature (`--semantic`, `--graph-stats`, `--lint`) runs as an independent pipeline sharing file collection, config loading, and reporting. This kept the CLI architecture clean despite growing scope.

### 5. Graceful Degradation
Optional dependencies (scikit-learn, networkx) degrade with clear error messages and exit code 2. Users see what they need to install, not a stack trace.

---

## Publication Options

### Option A: Single Epoch Retrospective
One long-form post covering the full productionization journey. ~2,000-3,000 words. Best for: technical blog, portfolio showcase.

### Option B: Sprint Series
5 shorter posts (one per sprint) plus a wrap-up. ~500-800 words each. Best for: LinkedIn, drip-feed content.

### Option C: Theme-Based Posts
Pick 2-3 cross-cutting themes (experiments as artifacts, synthetic vs real data, protocol evolution) and write standalone posts. Best for: broader audience, not tied to project specifics.

### Option D: Hybrid
One anchor post (Option A) + 1-2 standalone deep-dives on Sprint 6 (synthetic vs real data) and Sprint 7 (CQRS graph architecture). Best for: maximum reach with depth.

**Recommended:** Option D. The anchor post provides context; the deep-dives provide shareable, standalone value.

---

## Visuals to Capture

1. Before/after path diagram (Windows vs WSL paths)
2. Hub-and-spoke diagram (DSM Central with Graph Explorer spoke)
3. Sprint progression diagram (layers of validation capability)
4. EXP-003 vs EXP-003b comparison (synthetic vs real F1 scores)
5. Graph architecture diagram (FILE/SECTION nodes, CONTAINS/REFERENCES edges)
6. Terminal screenshots: pytest 331 passed, dsm-validate output, --lint output

---

**Last Updated:** 2026-03-09