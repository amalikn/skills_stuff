#!/usr/bin/env python3
"""Check that only expected files changed after a navigation control upgrade.

Runs git diff --name-only in the project root and compares against
an expected set of governance file changes.

Usage:
    python scripts/check_expected_diff.py --project-root /path/to/project
    python scripts/check_expected_diff.py --project-root /path/to/project --allow docs/reports/source-inventory-current.md
    python scripts/check_expected_diff.py --project-root /path/to/project --report-json /path/to/report.json
"""

import argparse
import json
import os
import subprocess
import sys

DEFAULT_EXPECTED = {
    "AGENTS.md",
    "AI_NAVIGATION.md",
    "CHANGELOG.md",
    "context-map.yaml",
    "scripts/README.md",
    # Present so a project that gains or tunes a governance coherence checker during an upgrade does not read as an UNEXPECTED change.
    "scripts/check_governance.py",
}

ALLOWED_OPTIONAL = {
    "docs/reports/source-inventory-current.md",
}


def parse_args():
    p = argparse.ArgumentParser(description="Check expected git diff after upgrade")
    p.add_argument("--project-root", required=True, help="Path to project root (must be a git repo)")
    p.add_argument("--allow", action="append", default=[], help="Additional allowed unexpected files")
    p.add_argument("--report-json", help="Write report JSON to file")
    return p.parse_args()


def main():
    args = parse_args()
    root = os.path.abspath(args.project_root)

    if not os.path.isdir(root):
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        sys.exit(2)

    # The project root is NOT necessarily the git root: workspaces commonly nest many
    # projects under one repository (project_stuff/me/<project>). Ask git for the toplevel
    # instead of looking for a .git directory, which rejects every nested project.
    try:
        top = subprocess.run(
            ["git", "-C", root, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: git rev-parse timed out", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("ERROR: git not found", file=sys.stderr)
        sys.exit(2)
    if top.returncode != 0:
        print(f"ERROR: {root} is not inside a git repository", file=sys.stderr)
        sys.exit(2)
    git_root = os.path.abspath(top.stdout.strip())

    # git reports paths relative to the GIT ROOT, while DEFAULT_EXPECTED holds names relative
    # to the PROJECT. Without stripping this prefix every file classifies as "unexpected".
    prefix = os.path.relpath(root, git_root)
    prefix = "" if prefix == "." else prefix + os.sep

    # Run git diff --name-only, scoped to this project
    try:
        result = subprocess.run(
            ["git", "-C", root, "diff", "--name-only", "--", root],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: git diff timed out", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("ERROR: git not found", file=sys.stderr)
        sys.exit(2)

    changed_files = {
        ln[len(prefix):] if prefix and ln.startswith(prefix) else ln
        for ln in result.stdout.strip().split("\n")
    } if result.stdout.strip() else set()
    if result.returncode != 0:
        print(f"ERROR: git diff failed: {result.stderr}", file=sys.stderr)
        sys.exit(2)

    # Build allowed set
    expected = DEFAULT_EXPECTED.copy()
    allowed = ALLOWED_OPTIONAL.copy()
    for extra in args.allow:
        allowed.add(extra)

    # Classify
    expected_changed = changed_files & expected
    allowed_changed = changed_files & allowed
    unexpected_changed = changed_files - expected - allowed

    report = {
        "project_root": root,
        "expected": sorted(expected_changed),
        "allowed": sorted(allowed_changed),
        "unexpected": sorted(unexpected_changed),
        "status": "unexpected_changes" if unexpected_changed else "clean",
    }

    # Print
    if expected_changed:
        print("Expected changes:")
        for f in sorted(expected_changed):
            print(f"  {f}")
    if allowed_changed:
        print("\nAllowed optional changes:")
        for f in sorted(allowed_changed):
            print(f"  {f}")
    if unexpected_changed:
        print("\nUNEXPECTED changes:")
        for f in sorted(unexpected_changed):
            print(f"  {f}")
    else:
        print("\nNo unexpected changes.")

    print(f"\nStatus: {report['status']}")

    if args.report_json:
        with open(args.report_json, "w") as f:
            json.dump(report, f, indent=2)
            f.write("\n")

    if unexpected_changed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
