# Research: Experiment Documentation Standards

**Date:** 2026-03-10
**Project:** DSM Graph Explorer
**Session:** 24
**Purpose:** Validate the proposed four-element experiment documentation structure
against established standards from software engineering, data science, reproducibility,
and hypothesis-driven development. Extract strengths, gaps, and a revised proposal.
**Feeds:** `docs/feedback/methodology.md` Entry 34, `docs/feedback/backlogs.md` Proposal #29

---

## The Structure Under Validation

The four elements proposed for DSM capability experiments:

1. **Justification / Why** — why this experiment is needed
2. **Expected Results / Hypothesis** — what we predict we will observe
3. **Validation** — did we obtain what we were expecting (actual vs expected)
4. **References** — where the idea came from, traceability to decisions

---

## Frameworks Surveyed

Six independent frameworks were reviewed. Sources listed at the end.

---

### 1. Scientific Method

The canonical elements (Science Buddies, Wikipedia):

- **Observation / Background**: What phenomenon motivates the inquiry; prior knowledge
- **Question**: A precise, answerable question
- **Hypothesis**: A falsifiable, testable prediction. Standard form: "If [condition], then [outcome], because [mechanism]"
- **Prediction**: The specific measurable outcome if the hypothesis is true
- **Experimental design**: Variables (independent, dependent, controlled), measurement method
- **Execution / Data collection**: Systematic recording
- **Analysis**: Comparing actual results to predicted results
- **Conclusion**: Confirming, refuting, or refining the hypothesis

**Notable:** The scientific method distinguishes the *hypothesis* (the mechanism claim) from the *prediction* (what we will observe). It also explicitly separates *experimental design* (how we measure) from both of these. The four-element structure collapses these into "Expected Results."

---

### 2. ML/Data Science Experiment Tracking Tools

**MLflow**, **Neptune.ai**, **Weights & Biases**, **DVC** were reviewed.

All four tools share the same structural blind spot: they are **execution-centric, not hypothesis-centric**. They capture what was run and what the numbers were, but not why the experiment was designed that way or what outcome was expected. None enforce or prompt for a justification or hypothesis field.

| Tool | Justification | Hypothesis | Environment | Results | Decision |
|------|:---:|:---:|:---:|:---:|:---:|
| MLflow | — | — | params/tags | metrics | — |
| Neptune.ai | — | — | params | metrics | — |
| W&B | — | — | config | metrics | — |
| DVC | — | — | params (Git) | metrics | — |

**Key insight:** The four-element DSM structure's main contribution relative to mainstream tooling is precisely that it captures justification and expected results, the two elements these tools entirely omit.

---

### 3. Software Engineering Experiment Frameworks

**Wohlin et al., "Experimentation in Software Engineering" (Springer, 2012/2024):**

Five phases: Scoping → Planning → Execution → Analysis → Result Presentation.

Planning requires: explicit null hypothesis (H0) and alternative hypothesis (H1), independent and dependent variables, confounding variables, measurement plan.

The null/alternative distinction matters: H0 is the "no effect" claim; H1 is the expected effect. Making H0 explicit makes an experiment falsifiable in a rigorous sense. "Expected Results" is a softer equivalent.

**GQM (Goal-Question-Metric), Basili et al.:**

Three levels:

- **Goal (Conceptual)**: Object, purpose, quality focus, viewpoint, context
- **Question (Operational)**: What must we know to assess the goal?
- **Metric (Quantitative)**: What can be measured to answer each question?

The GQM Abstraction Sheet additionally documents: variation factors, baseline hypotheses, and impact on quality focus. GQM makes the measurement plan a first-class element, distinct from both the goal and the hypothesis.

**How the four elements map to Wohlin/GQM:**

| Wohlin / GQM element | Maps to | Gap? |
|---|---|---|
| Goal / Scope / Motivation | Justification / Why | No gap |
| H0 + H1 / GQM Questions | Expected Results | Partial: "expected results" is softer than H0/H1 |
| Variables + Measurement plan | (missing) | **GAP: no measurement element** |
| Execution + Analysis | Validation | Partial: analysis is there, design is not |
| Related work + External validity | References | No gap |
| GQM Context / Environment | (missing) | **GAP: no environment element** |

---

### 4. Reproducibility Standards

**FAIR Principles (Nature Scientific Data, 2016; GO FAIR):**

The 15 FAIR principles group into Findable, Accessible, Interoperable, Reusable. Most relevant:

- **R1.2**: Detailed provenance — the chain of decisions and transformations leading to the result
- **I3**: Qualified references to other (meta)data — linkage to related experiments and datasets
- **F1/F2**: Persistent identifiers and rich metadata

**ACM Artifact Review and Badging:**

For "Artifacts Evaluated" badge: Documented, Consistent, Complete, Exercisable. The emphasis is on re-runnability, not hypothesis documentation.

**NeurIPS Reproducibility Checklist (2021, current):**

Requires: Steps for reproducibility, code and data, all training details (splits, hyperparameters, selection method), error bars and statistical significance, compute resources (hardware, memory, execution time).

**2024 Reproducibility Survey (arXiv 2406.14325):**

Seven elements required for code reproducibility: hypothesis, prediction method, source code, hardware specifications, software dependencies, experiment setup, experiment source code.

Five pillars of ML reproducibility tools: code versioning, data access, data versioning, experiment logging, pipeline creation.

**The most commonly missing elements in practice (from the 2024 survey):**

1. Environment specification (Python version, library versions, hardware, OS)
2. Random seeds
3. Explicit hypothesis
4. Statistical significance / error bars

**Key insight:** The reproducibility literature consistently identifies **environment documentation** as the most frequently absent element. Neither the four-element structure nor any of the ML tools above makes this explicit.

---

### 5. Hypothesis-Driven Development (HDD)

HDD is an established practice documented by MIT Lincoln Laboratory (2020), Alexander Cowan's guide (alexandercowan.com), IBM Garage Method, and the IEEE paper "Hypotheses Engineering" (IEEE Xplore, 2019).

Standard hypothesis format: "If we [do X] for [context/persona], then [observable outcome], because [mechanism or assumption]."

Pre-experiment documentation (Cowan's guide):

- Clear premise / underlying assumption
- Testable hypothesis (if/then/because)
- Success / failure thresholds (kill metrics, minimum success criteria)
- Independent variable (what is being tested)
- Test protocol

Post-experiment documentation:

- Observed results
- **Pivot or persevere decision** (relative to predetermined thresholds)
- Learning outcomes (what was validated or disproven)
- Follow-on experiments

The IBM/IEEE "hypotheses engineering" work treats hypotheses as first-class engineering artifacts requiring version control, tracing, and formal invalidation, analogous to requirements.

**How the four elements map to HDD:**

| HDD element | Maps to | Gap? |
|---|---|---|
| Premise / assumption | Justification / Why | No gap |
| If/then/because hypothesis | Expected Results | Partial: "because" (mechanism) often absent |
| Kill metrics / success thresholds | (missing) | **GAP: decision threshold not explicit** |
| Observed results | Validation | No gap |
| **Pivot/persevere decision** | (missing) | **GAP: decision is separate from comparison** |
| **Learning / insight** | (missing) | **GAP: what was discovered is not explicit** |
| Follow-on experiments | References | Partial (backward but not forward references) |

HDD is the framework most closely aligned with DSM capability experiments. The main gap it identifies: the **decision and the learning** are distinct from the comparison. Validation answers "what did I measure?"; Decision answers "what do I do next?"; Learning answers "what did I now know that I didn't before?"

---

### 6. Data Science Methodologies

**CRISP-DM (1999):** Six phases, documentation implicit in each. No "experiment" primitive; closest is the Evaluation phase (does the model meet business criteria?). Requires documenting rationale for modeling decisions.

**TDSP (Microsoft, 2016):** Agile-influenced CRISP-DM evolution. Provides project charter template, model report template. Includes business problem, technical approach, model hypothesis, evaluation criteria. Closer to hypothesis documentation than CRISP-DM but still not a self-contained experiment card structure.

**Key insight:** Both CRISP-DM and TDSP treat experiments as part of a larger lifecycle, not as atomic self-contained artifacts. The DSM structure (one experiment = one document with required elements) is more disciplined at the experiment level than either.

---

## Synthesis: Element Coverage Across All Frameworks

| Element | Sci. Method | Wohlin | GQM | FAIR/NeurIPS | HDD | CRISP-DM/TDSP | DSM (current) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Motivation / Justification | Yes | Yes | Yes | Yes (R1.2) | Yes | Yes | **Yes** |
| Hypothesis / Expected results | Yes | Yes | Yes | Yes | Yes | Yes | **Yes** |
| **Measurement / Success criteria** | Yes | Yes | Yes | Yes | Yes | Yes | **Missing** |
| **Environment / Setup** | Yes | Yes | Yes | Yes | Yes | Yes | **Missing** |
| Execution / Raw results | Yes | Yes | Yes | Yes | Yes | Yes | **Yes (Validation)** |
| Comparison / Analysis | Yes | Yes | Yes | Yes | Yes | Yes | **Yes (Validation)** |
| **Decision / Conclusion** | Yes | Yes | — | — | Yes | Yes | **Missing** |
| **Learning / Insight** | Yes | — | — | — | Yes | — | **Missing** |
| Traceability / References | Partial | Yes | Yes | Yes (I3) | Yes | — | **Yes** |

---

## Assessment of the Four-Element Structure

### What is on track

**Justification / Why:** Strong. Maps directly to motivation, goal, business objective, and FAIR R1.2 (provenance). This is the element ML tools most frequently omit entirely. DSM has this right.

**Expected Results / Hypothesis:** Well-supported. Aligns with the hypothesis element in all six frameworks. The label "Expected Results" is softer than a formal H0/H1 pair, which is a deliberate and appropriate simplification for capability experiments (not academic studies).

**Validation / Actual vs Expected:** Well-supported. Aligns with analysis and comparison across all frameworks. The current weakness is not in the element's existence but in practice: the comparison is often computed but not explicitly narrated as "we expected X, observed Y, conclusion is Z."

**References / Traceability:** Well-supported. Aligns with FAIR I3 (qualified references), external validity in Wohlin, and HDD follow-on experiments. EXP-005 implements this well (backward references to decisions; forward references could be added post-decision).

### Critical gaps

**Gap 1: No explicit Success Criteria / Measurement element** (all frameworks, high severity)

Every framework treats "what will I measure and what threshold constitutes pass/fail" as a separate element from the hypothesis. In the current structure, this is either absent or collapsed into "Expected Results." The distinction matters: a hypothesis says "FalkorDBLite will handle our data"; a success criterion says "startup <2s, node count exact, persistence verified." Without explicit pass/fail thresholds documented *before* running, the experiment is vulnerable to post-hoc rationalization of results.

EXP-005's test matrix is a strong implementation of this, but it is embedded in the script, not named as a structural section.

**Gap 2: No Environment / Setup documentation** (reproducibility literature, high severity)

The 2024 reproducibility survey, NeurIPS checklist, and FAIR R1.2 all identify environment as the most commonly missing element. For DSM capability experiments (Python scripts that can be re-run), this means: Python version, key library versions, OS, hardware, execution time. EXP-005 prints Python and falkordblite versions, but this is in the output, not in the documented structure.

**Gap 3: Decision / Conclusion is not a named element** (HDD, Wohlin, medium severity)

HDD separates "pivot or persevere decision" from the measurement comparison. The current structure conflates them inside "Validation." Making Decision a named element allows experiments to be auditable: you can scan a list and see which ones passed their gate and what was decided.

**Gap 4: No explicit Learning / Insight capture** (scientific method, HDD, low-medium severity)

HDD distinguishes "what was discovered" from "did we pass the threshold." Learning can include unexpected findings, new hypotheses generated, or scope changes. This is the most valuable element for building institutional knowledge, and the least captured.

---

## Revised Structure Proposal

A seven-element structure that addresses all gaps while remaining practical for capability experiments:

| # | Element | When written | Description |
|---|---------|-------------|-------------|
| 1 | **Justification** | Pre-run | Why this experiment is needed; which decision or gate it unlocks (name the ADR or sprint phase) |
| 2 | **Hypothesis** | Pre-run | The testable claim: "If [X], then [Y], because [Z]." Include the expected failure mode (what would falsify this) |
| 3 | **Success Criteria** | Pre-run | What is measured, how, and what threshold constitutes pass/fail for each criterion |
| 4 | **Environment** | Pre-run | Python version, key library versions, OS/hardware, random seeds, configuration flags |
| 5 | **Results** | Post-run | Raw outcomes per criterion (actual values, not yet interpreted) |
| 6 | **Decision** | Post-run | Pass / Fail / Inconclusive + explicit "expected X, observed Y, conclusion Z" per criterion; gate outcome (GO / NO-GO) |
| 7 | **References** | Both | Backward: ADRs, plan sections, inbox entries, prior experiments. Forward: which decision this fed (added post-decision) |

**Minimal variant (four elements, strengthened):**

For projects where the seven-element structure is too heavy, the original four elements can be kept with mandatory sub-elements:

1. **Justification**: includes the gate it unlocks (required sub-element)
2. **Hypothesis + Success Criteria**: merged, but pass/fail thresholds required as a sub-element
3. **Environment + Results + Decision**: merged, but gate outcome (GO/NO-GO) required as a sub-element
4. **References**: forward references added post-decision (required sub-element)

---

## Where EXP-005 Stands Against the Revised Structure

| Element | EXP-005 status | Notes |
|---------|---------------|-------|
| Justification | Strong | "Purpose" + "Background" sections; names Phase 9.2 gate |
| Hypothesis | Partial | Test matrix functions as hypothesis; "because" mechanism not stated per check |
| Success Criteria | Strong | Test matrix with explicit targets per check |
| Environment | Partial | Python version + falkordblite version printed in output; not in a named section |
| Results | Strong | 16/16 pass/fail with actual values |
| Decision | Partial | Gate outcome stated; no explicit "expected X, observed Y, Z" narrative |
| References | Strong | Full references section; forward reference to Phase 9.2 present |

EXP-005 is the strongest of the five experiments and covers 5 of 7 elements well. The two weakest points are the "because" mechanism in hypothesis framing and the absence of a named Environment section.

---

## Implications for Existing Experiments

| Experiment | Justification | Hypothesis | Success Criteria | Environment | Results | Decision | References |
|------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| EXP-003 | Partial | Partial | Partial (implicit) | Missing | Yes | Partial | Missing |
| EXP-003b | Partial | Missing | Missing | Missing | Yes (CSV) | Partial | Missing |
| EXP-004 | Partial | Partial | Strong (target table) | Missing | Yes | Partial | Minimal |
| EXP-005 | Strong | Partial | Strong | Partial | Strong | Partial | Strong |

**Recommendation on backfill:** EXP-003 and EXP-003b are complete and their decisions (DEC-005 threshold) are already made and documented. Backfilling them provides retroactive documentation value but does not change outcomes. EXP-004 is in the same position. The higher-value action is to apply the revised structure to all future experiments (EXP-006 onwards) and leave existing ones as evidence of the gap this research identified.

---

## Sources

- [Scientific method, Wikipedia](https://en.wikipedia.org/wiki/Scientific_method)
- [Steps of the Scientific Method, Science Buddies](https://www.sciencebuddies.org/science-fair-projects/science-fair/steps-of-the-scientific-method)
- [MLflow Tracking documentation](https://mlflow.org/docs/latest/tracking/)
- [MLflow entities schema](https://mlflow.org/docs/latest/python_api/mlflow.entities.html)
- [Neptune.ai best practices (legacy)](https://docs-legacy.neptune.ai/usage/best_practices/)
- [Experimentation in Software Engineering, Wohlin et al., Springer 2024](https://link.springer.com/book/10.1007/978-3-662-69306-3)
- [Wohlin, Empirical Research Methods (PDF)](https://www.wohlin.eu/esernet03-1.pdf)
- [GQM approach, University of Maryland (PDF)](https://www.cs.umd.edu/users/mvz/handouts/gqm.pdf)
- [FAIR Principles, GO FAIR](https://www.go-fair.org/fair-principles/)
- [The FAIR Guiding Principles, Nature Scientific Data 2016](https://www.nature.com/articles/sdata201618)
- [The Turing Way: FAIR data principles](https://book.the-turing-way.org/reproducible-research/rdm/rdm-fair/)
- [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-badging)
- [NeurIPS Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist)
- [Hypothesis-Driven Development practitioner's guide, Alexander Cowan](https://www.alexandercowan.com/hypothesis-driven-development-practitioners-guide/)
- [Hypothesis-Driven Development, IBM Garage Method](https://www.ibm.com/garage/method/practices/learn/practice_hypothesis_driven_development/)
- [Hypotheses Engineering: First Essential Steps of Experiment-Driven Software Development, IEEE 2019, DOI: 10.1109/RCoSE/DDrEE.2019.00011](https://ieeexplore.ieee.org/document/8818178/)
- [CRISP-DM overview, Data Science PM](https://www.datascience-pm.com/crisp-dm-2/)
- [TDSP overview, Data Science PM](https://www.datascience-pm.com/tdsp/)
- [Reproducibility in ML-based research: overview, barriers, drivers, arXiv 2406.14325 (2024)](https://arxiv.org/html/2406.14325v1)
- [Best Practices for ML Experimentation in Scientific Applications, arXiv 2511.21354](https://arxiv.org/html/2511.21354v2)
- [How to Solve Reproducibility in ML, Neptune.ai blog](https://neptune.ai/blog/how-to-solve-reproducibility-in-ml)