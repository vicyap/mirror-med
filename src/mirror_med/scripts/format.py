#!/usr/bin/env python3
"""Format and lint code using ruff."""

import subprocess
import sys


def main():
    """Run ruff format and check commands."""
    # Get source paths from command line args, default to "src" if none provided
    src_paths = sys.argv[1:] if len(sys.argv) > 1 else ["src"]

    try:
        subprocess.run(["ruff", "format"] + src_paths, check=True)
    except subprocess.CalledProcessError:
        print("❌ Formatting failed")
        sys.exit(1)

    try:
        subprocess.run(["ruff", "check", "--fix"] + src_paths, check=True)
    except subprocess.CalledProcessError:
        print("❌ Linting failed")
        sys.exit(1)

    print("✅ Code formatting and linting complete!")


if __name__ == "__main__":
    main()
