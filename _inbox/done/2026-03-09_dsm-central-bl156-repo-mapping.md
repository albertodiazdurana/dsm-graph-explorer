### [2026-03-09] Design input: DSM private-to-public repository mapping

**Type:** Action Item
**Priority:** High
**Source:** DSM Central

## Context

BL-156 (DSM rebranding) creates two DSM repository instances:

1. **DSM Private** (`dsm-agentic-ai-data-science-methodology`): the full methodology repository containing all content, including internal protocols, session management, custom instructions (DSM_0.2), implementation guides, backlog governance, and operational artifacts. This is the working repository where methodology development happens.

2. **DSM Public** (`dsm-take-ai-bite` or future public-facing repo): a curated subset of the methodology, packaged for external consumption. Contains the core methodology (DSM_1.0), appendices, PM guidelines (DSM_2.0), software engineering adaptation (DSM_4.0), AI collaboration principles (DSM_6.0), and supporting materials (README, case studies, templates). Excludes internal operational content: custom instructions (DSM_0.2), implementation guide (DSM_3), session management protocols, backlog system, and hub-spoke infrastructure.

## The Mapping Problem

The two repositories share content but are not mirrors. The relationship is:

- **Shared sections:** Core methodology sections exist in both repos, potentially with different formatting or packaging
- **Private-only sections:** Operational protocols, internal governance, session artifacts, backlog items, feedback infrastructure
- **Public-only sections:** Getting started guides, onboarding materials, simplified navigation tailored for external users
- **Transformed sections:** Some content may be adapted for the public audience (simplified language, removed internal references, consolidated structure)

This creates a synchronization challenge: when the private repo evolves (new methodology sections, updated guidelines, refined appendices), the public repo must reflect those changes in its curated subset. Currently, there is no mechanism to detect which changes in the private repo affect the public repo, or whether the public repo has drifted from its source.

## Graph Explorer's Role

Graph Explorer is uniquely positioned to solve this problem. Its core capability, modeling document structure as a graph and detecting changes, extends naturally to cross-repo comparison:

### 1. Multi-repo graph modeling
Model both repositories as separate document graphs. Each graph captures the hierarchical structure (documents, sections, subsections) and content of its repository. The graphs share a common schema but represent different instances.

### 2. Cross-repo node matching
Establish mappings between nodes in the private graph and nodes in the public graph. A section in DSM_1.0 in the private repo corresponds to the same section in the public repo. These mappings can be:
- **Exact match:** section exists identically in both repos
- **Transformed match:** section exists in both but with known transformations (e.g., internal references stripped)
- **Private-only:** section exists only in the private repo (no public counterpart)
- **Public-only:** section exists only in the public repo (e.g., onboarding content)

### 3. Diff detection and drift tracking
When the private repo changes (new commit, updated section, added content):
- Compare the private graph's changed nodes against their mapped counterparts in the public graph
- Identify which changes affect shared content (requires public repo update) vs. private-only content (no action needed)
- Surface a list of sync actions: "Section 2.2 updated in private; public copy is stale"

### 4. Sync action reporting
Produce actionable output:
- List of public-repo sections that need updating, with links to the source changes in the private repo
- List of unmapped new sections in the private repo (decision needed: public or private-only?)
- List of public-repo sections with no private counterpart (review: is this intentional public-only content?)

## Design Implications for Epoch 3

This capability requires architectural support that should be considered in Epoch 3 planning:

1. **Multi-repo graph support:** The graph database must support multiple repository graphs simultaneously, with clear boundaries between them. Currently, Graph Explorer models a single repo.

2. **Cross-repo node matching:** A mapping layer that connects nodes across graphs. This could be:
   - Explicit mapping file (maintained manually or semi-automatically)
   - Content-based matching (hash or similarity comparison of section content)
   - Path-based matching (sections with the same hierarchical path are assumed to correspond)

3. **Diff visualization:** The UI or reporting layer needs to show cross-repo differences, not just within-repo changes. This extends the existing diff capability to a new dimension.

4. **Mapping persistence:** The cross-repo mappings must persist between sessions. When a new section is added to the private repo, the system should prompt for classification (shared vs. private-only) and store the decision.

5. **Sync workflow integration:** The output of cross-repo diff should integrate with the existing inbox/feedback infrastructure. When drift is detected, Graph Explorer could generate inbox entries or sync action items automatically.

## Why This Matters Now

Epoch 3 planning is the right moment to incorporate this design input because:
- The architecture decisions made in Epoch 3 will determine whether multi-repo support is a natural extension or a retrofit
- BL-156 Phase 3 (public repo content population) will create the first real instance of the two-repo pattern
- Early design consideration avoids building single-repo assumptions into the Epoch 3 architecture that would be costly to change later

## Requested Action

Consider this mapping capability as a design requirement for Epoch 3 architecture planning. Specifically:
- Include multi-repo graph support in the data model design
- Plan the node matching strategy as part of the graph schema
- Consider whether this warrants a dedicated sprint or can be woven into existing sprint scope
