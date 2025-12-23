#!/usr/bin/env python3
"""
Pre-push hook to ensure tests pass before pushing.

This hook runs the full test suite. Quality checks (lint, type-check,
format-check) are already run in pre-commit hooks, so we only need to
verify tests pass before sharing code with others.

Push will be blocked if tests fail.
"""

import os
import subprocess
import sys
from pathlib import Path

# Force unbuffered output so test progress is visible
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    # Write directly to stderr so pre-commit doesn't suppress it
    print(f"\n{'='*50}", file=sys.stderr, flush=True)
    print(f"Running: {description}", file=sys.stderr, flush=True)
    print(f"{'='*50}", file=sys.stderr, flush=True)
    print(f"Command: {' '.join(cmd)}\n", file=sys.stderr, flush=True)

    try:
        # Run with output visible so user sees test progress in real-time
        # Write directly to stderr to bypass pre-commit output capture
        # Use line buffering to see output immediately
        process = subprocess.Popen(
            cmd,
            stdout=sys.stderr,
            stderr=sys.stderr,
            text=True,
            bufsize=1,  # Line buffered
        )
        exit_code = process.wait()

        if exit_code != 0:
            print(f"\n✗ {description} failed!", file=sys.stderr, flush=True)
            print("\nPlease fix the issues above before pushing.", file=sys.stderr, flush=True)
            print(
                f"You can run '{' '.join(cmd)}' manually to see the errors.",
                file=sys.stderr,
                flush=True,
            )
            return False

        print(f"\n✓ {description} passed\n", file=sys.stderr, flush=True)
        return True
    except FileNotFoundError:
        print(
            "\n✗ Error: Command not found. Make sure 'make' is installed.",
            file=sys.stderr,
            flush=True,
        )
        return False


def main() -> int:
    """Main hook logic."""
    project_root = Path(__file__).parent.parent.resolve()
    makefile_path = project_root / "Makefile"

    if not makefile_path.exists():
        print("✗ Error: Makefile not found", file=sys.stderr, flush=True)
        return 1

    # Change to project root
    os.chdir(project_root)

    # Run all tests (quality checks already run in pre-commit)
    # Tests will show progress output so user can see what's happening
    if not run_command(["make", "test"], "Test suite"):
        return 1

    # All checks passed
    print(f"\n{'='*50}", file=sys.stderr, flush=True)
    print("✓ All pre-push checks passed!", file=sys.stderr, flush=True)
    print(f"{'='*50}\n", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
