#!/usr/bin/env bash
# pre-commit-hook.sh — Validate DSM cross-references in staged markdown files
#
# Installation (manual):
#   cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Installation (pre-commit framework):
#   See docs/guides/remediation-guide.md for .pre-commit-config.yaml example
#
# Requires: dsm-graph-explorer installed (pip install dsm-graph-explorer)

set -euo pipefail

# Check if dsm-validate is available
if ! command -v dsm-validate &> /dev/null; then
    echo "dsm-validate not found, skipping documentation validation."
    echo "Install with: pip install dsm-graph-explorer"
    exit 0
fi

# Get staged markdown files (Added, Copied, Modified)
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM -- '*.md')

if [ -z "$STAGED_FILES" ]; then
    # No markdown files staged, nothing to validate
    exit 0
fi

echo "Validating cross-references in staged markdown files..."

# Run dsm-validate on staged files with strict mode
# shellcheck disable=SC2086
dsm-validate $STAGED_FILES --strict
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "Cross-reference validation failed. Fix errors before committing."
    echo "Run 'dsm-validate <file>' to see details."
    echo "See docs/guides/remediation-guide.md for common fixes."
fi

exit $exit_code
