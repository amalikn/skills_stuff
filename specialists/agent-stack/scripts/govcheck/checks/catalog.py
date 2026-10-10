"""Catalogs and counts: prose counts match reality, every file is cataloged, every just recipe is documented."""

from __future__ import annotations

import re

from ..core import counted, fail
from ..config import (
    ASAT_MARKER,
    CATALOGS,
    CATALOG_EXEMPT,
    COUNT_CLAIMS,
    ROOT,
    RUNNER_REFERENCES,
    SURFACES,
    TASK_RUNNER,
)
from ..helpers import (
    members,
    read,
    without_code,
)

def check_count_claims() -> None:
    """Prose stating a quantity matches the real count. Lines marked as historical facts are exempt."""
    for noun, (folder, glob) in COUNT_CLAIMS.items():
        actual = len(members(folder, glob))
        pattern = re.compile(rf"(\d+)\s+{re.escape(noun)}\b", re.IGNORECASE)
        for surface in SURFACES:
            text = read(surface)
            if text is None:
                continue
            for line in without_code(text).splitlines():
                if ASAT_MARKER in line:
                    continue
                for claim in pattern.finditer(line):
                    counted()
                    if int(claim.group(1)) != actual:
                        fail("count", f"{surface} claims {claim.group(1)} {noun}; {folder}/{glob} holds {actual}")


def check_catalog_coverage() -> None:
    """Both directions: the catalog names nothing missing, and nothing present is uncataloged.

    The second direction is the one that grows silently, and it is what makes this checker self-extending — a new file turns the build red until it is
    registered somewhere.
    """
    for index, (folder, glob) in CATALOGS.items():
        text = read(index)
        if text is None:
            continue
        body = without_code(text)
        for item in members(folder, glob):
            if item.name in CATALOG_EXEMPT or (ROOT / index).resolve() == item.resolve():
                continue
            # Rotated CHANGELOG/SCRATCHPAD archives are dated records indexed by docs/history/readme.md, which rotate_records.py maintains.
            if item.relative_to(ROOT).as_posix().startswith("docs/history/") and item.name != "readme.md":
                continue
            counted()
            if item.name not in body:
                fail("coverage", f"{folder}/{item.name} exists but is not cataloged in {index}")


def check_task_recipes() -> None:
    """Recipes named in prose exist in the task runner, and every cataloged script has a way to be run."""
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        fail("runner", f"{TASK_RUNNER} is configured but does not exist")
        counted()
        return
    recipes = {m.group(1) for m in re.finditer(r"^([a-zA-Z][\w-]*)\s*(?:[*+a-zA-Z_].*)?:(?!=)", runner, re.MULTILINE)}
    for surface in RUNNER_REFERENCES:
        text = read(surface)
        if text is None:
            continue
        for named in {m.group(1) for m in re.finditer(r"`just ([a-zA-Z][\w-]*)", without_code(text))}:
            counted()
            if named not in recipes:
                fail("runner", f"{surface} names recipe `{named}` which {TASK_RUNNER} does not define")

    # And the reverse: a recipe pointing at a script that no longer exists. Nothing reads a recipe until someone runs it, so a script deleted in a cleanup leaves
    # a recipe that looks live in `just --list` and fails only for whoever tries it. Found exactly that on 20260903 — `record-current` still invoked
    # scripts/sync_auto_company.py, deleted when upstream sync was retired, and the prose-to-recipe direction had no way to see it.
    # A path under another package (`"{{ai_it}}/scripts/x.py"`, a skill this project calls by absolute path) is not this project's script.
    for m in re.finditer(r"(?<![\w/}])(scripts/[\w./-]+\.py)", runner):
        counted()
        if not (ROOT / m.group(1)).is_file():
            fail("runner", f"{TASK_RUNNER} invokes {m.group(1)}, which does not exist; the recipe is dead but still listed")
