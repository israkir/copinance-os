#!/usr/bin/env python3
"""
Pre-commit hook to ensure CHANGELOG.md is updated when there are staged changes.

This hook checks if there are any staged changes (excluding CHANGELOG.md itself).
If there are changes, it verifies that CHANGELOG.md is also in the staged changes.
"""

import subprocess
import sys
from pathlib import Path


def get_staged_files() -> list[str]:
    """Get list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def main() -> int:
    """Main hook logic."""
    staged_files = get_staged_files()

    # If no files are staged, allow the commit (might be an amend or other case)
    if not staged_files:
        return 0

    # Check if CHANGELOG.md is in the staged files
    changelog_path = Path("CHANGELOG.md")
    changelog_staged = any(Path(f).resolve() == changelog_path.resolve() for f in staged_files)

    # If CHANGELOG.md is staged, allow the commit
    if changelog_staged:
        return 0

    # If there are staged changes but CHANGELOG.md is not updated, fail
    print(
        "❌ CHANGELOG.md has not been updated!\n"
        "Please update CHANGELOG.md to document your changes before committing.\n"
        "If this change doesn't require a changelog entry, you can skip this check with:\n"
        "  git commit --no-verify"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
