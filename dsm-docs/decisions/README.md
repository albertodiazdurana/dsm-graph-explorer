# dsm-docs/decisions/

Architecture Decision Records (ADRs) — documents significant technical choices with rationale.

## Files

| File | Decision | Status |
|------|----------|--------|
| `DEC-001_parser_library_choice.md` | Chose pure regex over markdown libraries | Implemented |
| `DEC-002_cli_design_choices.md` | CLI arguments, exit codes, output options | Implemented |
| `DEC-003_error_remediation_strategy.md` | DSM repo error triage approach | In Progress |
| `DEC-004_wsl_migration.md` | WSL2 for cross-platform development | Approved |
| `DEC-005-semantic-validation-approach.md` | Semantic validation: title + context-excerpt mode | Accepted |
| `DEC-006-graph-database-selection.md` | FalkorDBLite as the graph backend (Epoch 3) | Accepted |
| `DEC-007-python-312-upgrade.md` | Upgrade minimum Python to 3.12 | Accepted |
| `DEC-008-heading-based-section-ids.md` | Heading-based section node IDs (`{file}:h:{slug}`) | Accepted |
| `DEC-009-no-local-llm-dependencies.md` | No local LLM deps; the consuming agent is the LLM | Accepted |
| `DEC-010-toon-migration-format.md` | Migrate knowledge-summary output to TOON | Accepted |
| `DEC-011-semantic-concept-layer-adoption.md` | Adopt Semantic Concept Layer (Layer 4.5) for Epoch 6 | Accepted |

## Naming Convention

`DEC-NNN_short-description.md`

## Content Structure

- **Context:** What problem we faced
- **Decision:** What we chose
- **Rationale:** Why this option
- **Alternatives considered:** What else we evaluated
- **Trade-offs:** Consequences accepted
