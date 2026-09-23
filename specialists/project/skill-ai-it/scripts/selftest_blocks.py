#!/usr/bin/env python3
"""Self-test for the managed-block builders in upgrade_navigation_control_layer.py.

Why this exists. On 2026-09-23 the upgrader's inlined navigation block had fallen nine sections
behind `templates/AI_NAVIGATION.md`. A project bootstrapped from the template and then upgraded by
the script LOST task routing, drift handling, update rules and the answer contract — and the run
reported only `replaced-managed-block`, which reads like a successful migration. Two of the three
blocks happened to still agree with their templates, so the pattern looked maintained.

The structural fix was to delete the inlined copies and have each builder read its template, making
the template the single source of truth. This file asserts that the structure actually holds:

1. every builder emits canonical markers carrying the CURRENT version;
2. the navigation block carries every `##` heading its template's block region carries;
3. a builder FAILS LOUDLY when its template is unreadable, rather than falling back to a copy.

Assertion 3 is the one that matters most: a silent fallback would reintroduce the second source of
truth this file exists to prevent. Standard library only, no arguments:

    python3 scripts/selftest_blocks.py
"""

import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UPGRADER = os.path.join(HERE, "upgrade_navigation_control_layer.py")

# Sections the emitted navigation block must always carry, independent of what any template says.
REQUIRED_NAV_SECTIONS = [
    "## Mandatory read order",
    "## Source priority",
    "## Project context files",
    "## Task routing",
    "## Script and Task Navigation",
    "## Governance coherence checks",
    "## Companion consistency",
    "## Drift handling",
    "## Update rules",
    "## Generated context",
    "## Context compaction recovery",
    "## Audit procedure",
    "## Agent answer contract",
]

failures: list[str] = []
checks = 0


def check(condition: bool, detail: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(detail)


def load():
    spec = importlib.util.spec_from_file_location("upgrader_under_test", UPGRADER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def headings(text: str, level: str = "## ") -> list[str]:
    return [l.strip() for l in text.split("\n") if l.startswith(level) and not l.startswith(level + "#")]


def main() -> int:
    m = load()

    blocks = {
        "navigation": (m.build_navigation_block, m.BEGIN_MANAGED, m.END_MANAGED),
        "agents": (m.build_agents_block, m.BEGIN_MANAGED, m.END_MANAGED),
        "scripts": (m.build_scripts_block, m.BEGIN_SCRIPTS_MANAGED, m.END_SCRIPTS_MANAGED),
    }

    for name, (build, begin, end) in blocks.items():
        body = build()
        check(body.startswith(begin), f"{name}: does not open with {begin}")
        check(body.rstrip().endswith(end), f"{name}: does not close with {end}")
        check(
            f"<!-- skill-ai-it-version: {m.VERSION} -->" in body,
            f"{name}: emitted block does not carry the current version {m.VERSION}",
        )
        check(
            body.count(begin) == 1 and body.count(end) == 1,
            f"{name}: emitted block contains duplicate markers",
        )
        check(
            not re.search(r"[ \t]+$", body, flags=re.MULTILINE),
            f"{name}: emitted block has trailing whitespace",
        )
        check("\n\n\n" not in body, f"{name}: emitted block has a blank run")

    # The navigation block must not be thinner than this floor. Comparing the emitted block against
    # the template it is generated FROM would be tautological — both sides move together — so the
    # floor is stated here independently. Truncating the template now turns this red, which is the
    # regression that went unnoticed for six weeks. Add a section here when one becomes required;
    # removing one is a deliberate act that should be argued for in the changelog.
    emitted = headings(m.build_navigation_block())
    missing = [h for h in REQUIRED_NAV_SECTIONS if h not in emitted]
    check(not missing, f"navigation: required sections absent from emitted block: {missing}")

    # A missing template must stop the run, never degrade to an inlined copy.
    saved = m.NAVIGATION_TEMPLATE
    try:
        m.NAVIGATION_TEMPLATE = os.path.join(ROOT, "templates", "__no_such_template__.md")
        try:
            m.build_navigation_block()
            check(False, "navigation: a missing template did NOT stop the run — a fallback copy has crept back in")
        except SystemExit:
            check(True, "")
    finally:
        m.NAVIGATION_TEMPLATE = saved

    if failures:
        print(f"FAIL — {len(failures)} issue(s) across {checks} checks\n")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"OK — {checks} managed-block self-tests passed (version {m.VERSION})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
