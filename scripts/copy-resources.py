#!/usr/bin/env python3
"""Copy shared resources to each language implementation.

This script copies the shared resources from resources/content/ to each
language implementation's expected location. Run this script after editing
any resource files.

Usage:
    python scripts/copy-resources.py
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "resources" / "content"

TARGETS = [
    ROOT / "py" / "src" / "resources" / "content",
    ROOT / "tsx" / "src" / "resources" / "content",
    ROOT / "rs" / "src" / "resources" / "content",
]


def copy_resources(verbose: bool = True) -> bool:
    """Copy resources from source to all target directories.

    Args:
        verbose: Print status messages if True.

    Returns:
        True if all copies succeeded, False otherwise.
    """
    if not SOURCE.exists():
        print(f"Error: Source directory not found: {SOURCE}", file=sys.stderr)
        return False

    success = True
    for target in TARGETS:
        try:
            # Create parent directory if needed
            target.parent.mkdir(parents=True, exist_ok=True)

            # Remove existing target if it exists
            if target.exists():
                shutil.rmtree(target)

            # Copy source to target
            shutil.copytree(SOURCE, target)

            if verbose:
                print(f"Copied resources to {target.relative_to(ROOT)}")
        except Exception as e:
            print(f"Error copying to {target}: {e}", file=sys.stderr)
            success = False

    return success


def main() -> int:
    """Main entry point."""
    print(f"Copying resources from {SOURCE.relative_to(ROOT)}...")
    if copy_resources():
        print("Done!")
        return 0
    else:
        print("Some copies failed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
