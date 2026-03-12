# Session 27 Transcript
**Started:** 2026-03-12T02:20:56-03:00
**Project:** DSM Graph Explorer

---

## Session Start

**Context loaded:** MEMORY.md (Session 26, Sprint 9 complete), DSM_0.2 v1.3.58, project CLAUDE.md.

**Project type:** Application (DSM 4.0), Standard Spoke pattern.
**Ecosystem paths:** No registry found; using fallback resolution.
**Inbox:** Empty (only README.md).
**Version check:** DSM_0.2 v1.3.58, last breaking change 2026-02-13. No change since last session.
**Handoffs:** None unconsumed.
**Checkpoints:** Read sprint-9-completion.md (Sprint 9 summary, 355 tests, 96% coverage). Moved all 9 checkpoints (epoch 1-3) to done/.
**Transcript archived:** 2026-03-11T16:41-ST.md
**Bandwidth:** Normal usage, 150 MiB spike at 02:00 today (likely system updates).
**Git:** Clean working tree, up to date with origin/master.
**Baseline:** Saved to .claude/session-baseline.txt.

**Pending work from checkpoint:**
1. Sprint 10: Git-Ref Temporal Compilation (--git-ref, git_resolver.py, graph_diff.py, EXP-006)
2. Epoch 4 roadmap: LLM second-pass (tiered: TF-IDF filters, LLM confirms)
3. Deferred SHOULD: section rename tracking (section-renames.yml)

## Sprint 10 Kickoff

User wants to start Sprint 10: Git-Ref Temporal Compilation.

**First step:** Read the epoch-3 plan to understand Sprint 10 scope and phases. Then propose a plan for the sprint before writing any code.

## Sprint 10 Planning

Read epoch-3-plan.md. Sprint 10 has 3 phases:
- **Phase 10.0:** EXP-006 (Temporal Accuracy Experiment) — pre-implementation gate
- **Phase 10.1:** Git-Ref Compilation (git_resolver.py + CLI --git-ref)
- **Phase 10.2:** Temporal Diff (graph_diff.py + CLI --graph-diff)

Key design decisions from plan:
- Git is the event store; compilation pipeline is the projection function
- Use subprocess (git show, git ls-tree) — no gitpython dependency
- git_ref property already exists on Document nodes (added in Sprint 9)
- New files: src/git_ref/__init__.py, src/git_ref/git_resolver.py, src/graph/graph_diff.py
- New tests: tests/test_git_resolver.py, tests/test_graph_diff.py

Need to understand current pipeline before proposing detailed plan. Reading cli.py and parser to see how files are currently fed to the system.

### Current Pipeline Analysis

Read cli.py. The current flow for graph operations:
1. `collect_markdown_files(paths)` → reads from disk via `Path.glob()`
2. `parse_markdown_file(f)` → parses each file (expects a Path, reads from disk)
3. `extract_cross_references(f)` → extracts refs (also reads from disk)
4. `build_reference_graph(documents, references, section_lookup)` → builds NetworkX graph
5. `GraphStore.write_graph(G, graph_name)` → persists to FalkorDB

For `--git-ref`, I need to intercept step 1-3: instead of reading from disk, read from git at the specified ref. The key question is how `parse_markdown_file` works, does it take a Path or can it take content?

Also noticed: cli.py still shows `version="0.2.0"` in @click.version_option but pyproject.toml should be 0.3.0. This is a minor inconsistency to flag later.

Need to read parse_markdown_file to understand its interface.

### Key Finding: Parser Interface

Both `parse_markdown_file` and `extract_cross_references`:
- Accept `Path | str`
- Read from disk via `path.open()`
- Cannot accept string content directly

For `--git-ref`, I need to either:
1. **Option A:** Create content-based variants (`parse_markdown_content`, `extract_cross_references_from_content`)
2. **Option B:** Use `git worktree` or temp directory approach (checkout files to disk, then use existing parsers)
3. **Option C:** Use `git show REF:path` for each file, write to temp files, pass to existing parsers

The plan says "Uses `subprocess` (git show, git ls-tree) rather than gitpython dependency". Option C (temp files) would be simplest but wasteful. Option A (content-based parsers) is cleanest but requires changes to existing modules. Option B (worktree) adds git complexity.

**Best approach:** Option A, create `parse_markdown_content(content, file_path)` and `extract_cross_references_from_content(content, file_path)` that accept string content + a virtual file path. These are thin wrappers that share the same core logic. This keeps the git_resolver clean and avoids temp file overhead.

Actually, even simpler: refactor both functions so the existing function reads from disk and calls a new `_from_lines` internal, and the git-ref path calls `_from_lines` directly. Minimal API change.

### Sprint 10 Proposed Plan

**Phase 10.0: EXP-006 (Pre-Implementation Gate)**
- Manual experiment: pick 2 historical refs in the current repo or DSM repo
- Verify `git ls-tree` and `git show` produce correct file lists and content
- Document results

**Phase 10.1: Git-Ref Compilation**
- 10.1a: Add content-based parser variants (parse_markdown_content, extract_cross_references_from_content)
- 10.1b: Create src/git_ref/__init__.py + src/git_ref/git_resolver.py
  - resolve_ref(repo_path, ref) → validated SHA
  - list_files_at_ref(repo_path, sha) → list of markdown file paths
  - read_file_at_ref(repo_path, sha, filepath) → content string
- 10.1c: CLI --git-ref integration (replaces collect_markdown_files with git-based collection)
- 10.1d: Tests for all of the above

**Phase 10.2: Temporal Diff**
- graph_diff.py with diff_graphs function
- CLI --graph-diff REF_A REF_B
- Rich table reporter for diffs
- Tests

Let me present this plan to the user.

## Phase 10.0: EXP-006 (Temporal Accuracy Experiment)

User approved the plan. Starting with EXP-006.

**Goal:** Verify that `git ls-tree` and `git show` produce correct file lists and content at historical refs, confirming the subprocess approach is feasible before building the feature.

**Approach:** Pick 2 historical refs in this repo. Run the git commands manually in a script. Compare results against expectations.

First, find suitable refs: need an early commit (fewer files) and a recent one.

### Ref Selection
- **Ref A (old):** `87d869d` — Sprint 1 complete, 12 markdown files
- **Ref B (current):** `HEAD` (c67994f) — 86 markdown files

Good contrast: 74 files added between the two. This will clearly test added/removed detection.

### EXP-006 Test Matrix (from epoch-3-plan.md)
1. `--git-ref HEAD` matches current graph
2. `--git-ref <SHA>` (old commit) produces correct historical snapshot
3. Deterministic: same SHA, same result
4. Added file since ref: not present in historical graph
5. Deleted file since ref: present in historical graph (need to check if any files were deleted)
6. Diff (HEAD vs old): correct added/removed/changed nodes

### Experiment Script Design
- Python script in `data/experiments/`
- Tests the subprocess commands directly
- Validates output against expectations
- Reports pass/fail for each check

Let me write the experiment script.

### EXP-006 Results: 19/19 PASSED

All checks passed:
- **Ref resolution:** HEAD → 40-char SHA, short SHA → full SHA, invalid ref → error
- **File listing:** 12 md files at old ref, 86 at HEAD, correct presence/absence
- **Content reading:** README.md differs between refs, nonexistent files error correctly
- **Determinism:** Both ls-tree and git show are deterministic
- **Performance:** ls-tree 3.7ms avg, git show 2.9ms avg (both well under 100ms)

**Key findings:**
- 82 files added, 4 common, 8 removed between Sprint 1 and HEAD
- subprocess approach is fast and reliable
- No gitpython needed

**Gate passed.** Proceeding to Phase 10.1.

## Phase 10.1a: Content-Based Parser Variants

User approved. Implementing content-based variants in both parser modules.

**Plan:**
1. markdown_parser.py: extract `_parse_lines(lines, file_path, excerpt_words)` → `ParsedDocument`, then `parse_markdown_file` reads disk and calls it, new `parse_markdown_content` splits string and calls it.
2. cross_ref_extractor.py: extract `_extract_from_lines(lines, file_path, context_window)` → `list[CrossReference]`, same pattern.
3. Tests for both new functions.

## Phase 10.1b: git_resolver.py

User approved. Creating src/git_ref/__init__.py and src/git_ref/git_resolver.py.

## Phase 10.1 Tests: test_git_resolver.py

User approved. Writing tests for git_resolver + content-based parser variants.

### Phase 10.1a+b Complete
- Parser variants: `parse_markdown_content`, `extract_cross_references_from_content` working
- git_resolver.py: `resolve_ref`, `list_files_at_ref`, `read_file_at_ref` working
- Tests: 28 new tests, all passing. Full suite: 383 passed.
- git_resolver.py line 84 has 1 uncovered line (the empty-result guard in list_files_at_ref)

Next: Phase 10.1c, CLI --git-ref integration.

## Phase 10.1c: CLI --git-ref Integration

User approved. Modifying cli.py to add --git-ref option.

**Design:** When --git-ref is set:
1. resolve_ref to get full SHA
2. list_files_at_ref to get markdown file paths
3. For each file, read_file_at_ref + parse_markdown_content + extract_cross_references_from_content
4. Rest of pipeline (validation, graph, report) runs unchanged on the parsed data
5. Pass git_ref to GraphStore.write_graph

Need to re-read cli.py for current state, then make targeted edits.

### Phase 10.1c Complete: CLI --git-ref Integration
- Added --git-ref option to CLI
- find_repo_root() ensures correct repo root resolution from any subdirectory
- Git-ref mode: resolve → list → read → content-based parsers → validation
- --lint + --git-ref rejected with clear error
- git_ref_sha passed to GraphStore.write_graph
- Fixed version string 0.2.0 → 0.3.0 (+ updated test)
- 7 new CLI integration tests, all passing
- Full suite: 390 passed (355 original + 28 resolver + 7 CLI)

Phase 10.1 complete. Moving to Phase 10.2: Temporal Diff.

## Phase 10.2: Temporal Diff

User approved. Creating graph_diff.py + CLI --graph-diff + tests.

**Design refinement:** The diff operates at NetworkX level (no FalkorDB needed). The module:
1. Builds two NetworkX graphs from two git refs using the git-ref pipeline
2. Compares node sets (FILE and SECTION nodes) by ID
3. For common SECTION nodes, compares title property for changes

Need to read graph_builder.py to understand how graphs are built and what node IDs look like.

### Graph Builder Analysis
- FILE node ID = file path (e.g., "README.md")
- SECTION node ID = "file_path:section_number" (e.g., "README.md:1.2.3")
- FILE nodes have: type="FILE", title=basename
- SECTION nodes have: type="SECTION", title, number, file, line, level, context_excerpt

**Diff strategy:**
- Compare FILE nodes by file path (the node ID)
- Compare SECTION nodes by section number (strip file path prefix, use number)
  - Actually, since file paths differ between refs (git-relative vs disk), I should compare by the node ID directly since both refs produce git-relative paths
- For common sections, compare title to detect renames/changes

**Implementation:**
- `_build_graph_at_ref(repo_path, sha)` — internal helper that does: list_files → read_file → parse_markdown_content → extract_refs → build_reference_graph → return graph
- `diff_graphs(repo_path, ref_a, ref_b)` — calls helper twice, then compares
- `DiffResult` with: ref_a, ref_b, added_files, removed_files, added_sections, removed_sections, changed_sections
- `ChangedNode` with: node_id, field, old_value, new_value

### Phase 10.2 Complete: Temporal Diff
- Created `src/graph/graph_diff.py`: DiffResult, ChangedNode, diff_graphs, _build_graph_at_ref, _compare_graphs
- Added `--graph-diff REF_A REF_B` CLI option with Rich table output
- `_print_diff_report` shows added/removed files, added/removed sections, changed nodes, and summary
- 12 new tests (6 unit for _compare_graphs, 3 integration with real repo, 3 CLI)
- Full suite: 402 passed (355 + 47 new this session)
- Performance: 0.38s for full diff between Sprint 1 and HEAD

## Sprint 10 Summary

All three phases complete:
- **Phase 10.0:** EXP-006 (19/19 passed, subprocess approach validated)
- **Phase 10.1:** Git-Ref Compilation (git_resolver.py, content-based parsers, CLI --git-ref)
- **Phase 10.2:** Temporal Diff (graph_diff.py, CLI --graph-diff, Rich output)

**New files:**
- `data/experiments/exp006_git_ref_temporal.py`
- `src/git_ref/__init__.py`
- `src/git_ref/git_resolver.py`
- `src/graph/graph_diff.py`
- `tests/test_git_resolver.py`
- `tests/test_cli_git_ref.py`
- `tests/test_graph_diff.py`

**Modified files:**
- `src/parser/markdown_parser.py` (added parse_markdown_content, _parse_lines)
- `src/parser/cross_ref_extractor.py` (added extract_cross_references_from_content, _extract_from_lines)
- `src/cli.py` (--git-ref, --graph-diff, version 0.3.0, _print_diff_report)
- `tests/test_cli.py` (version assertion updated)

**Metrics:** 355 → 402 tests (+47), all passing
