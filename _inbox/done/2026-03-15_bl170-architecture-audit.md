**Consumed at:** Session 35 (2026-03-16)

### [2026-03-15] Architecture audit requested (BL-170 Part B)

**Type:** Action Item
**Priority:** High
**Source:** DSM Central

Graph Explorer needs an architecture audit to answer three questions:

1. **Artifact inventory:** Which artifact types does GE index to build graph nodes? Enumerate all node types, entity types, or artifact categories from source code.

2. **Git access method:** Does GE use remote API (GitHub), local git commands, a git library, or filesystem reads? Can it work with local-only repos (no remote)?

3. **Cross-pattern availability:** Which artifact types would be unavailable or degraded for Private Projects (local git, no remote)? Which work fine via filesystem?

**Output:** Findings document in `docs/research/2026-03-15_architecture-audit.md` with file:line references. Send results back to DSM Central inbox.

**Context:** BL-170 in DSM Central. Part A (git auto-init) is implemented. Part B is this audit, deferred to a GE session because the audit requires reading GE source code.