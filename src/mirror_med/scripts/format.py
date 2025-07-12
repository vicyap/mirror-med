#!/usr/bin/env python3
"""Format and lint code using ruff."""

import subprocess
import sys


def main():
    """Run ruff format and check commands."""
    try:
        subprocess.run(["ruff", "format", "src"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Formatting failed")
        sys.exit(1)

    try:
        subprocess.run(["ruff", "check", "--fix", "src"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Linting failed")
        sys.exit(1)

    print("✅ Code formatting and linting complete!")


if __name__ == "__main__":
    main()
