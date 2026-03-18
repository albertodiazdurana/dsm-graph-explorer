### [2026-03-18] BL-222: Two-Pass Reading Strategy, Parser Alignment Inquiry

**Type:** Action Item
**Priority:** Medium
**Source:** DSM Central (Session 135)

DSM Central is developing a two-pass reading strategy for long structured files
(BL-222). Before implementation, we want to understand GE's parsing approach to
avoid duplicating solved problems and identify alignment opportunities.

**Questions:**

1. Does GE use a multi-pass approach when parsing markdown files to build graphs?
2. Where is the parser located in the codebase?
3. Could GE's structural scan output (headings, nesting levels, line ranges) be
   exposed as a lightweight skeleton for use outside the full graph pipeline?
4. Would a multi-format conversion script (PDF/DOCX/HTML/PPTX to markdown) be
   useful for expanding GE's input scope?

**Full context:** Read DSM Central's BL file at
`~/dsm-agentic-ai-data-science-methodology/plan/backlog/improvements/BACKLOG-222_two-pass-reading-strategy-for-long-files.md`
