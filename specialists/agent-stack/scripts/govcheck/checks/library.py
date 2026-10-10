"""The manifest and the persona/skill library agree: paths exist, coverage both ways, SKILL.md present, counts."""

from __future__ import annotations

import re

from ..core import counted, fail
from ..config import (
    ASAT_MARKER,
    CATALOG_EXEMPT,
    ROOT,
    SURFACES,
)
from ..helpers import (
    manifest_capabilities,
    read,
    without_code,
)

def check_manifest_paths_exist() -> None:
    """Every capability path in manifest.yaml resolves on disk.

    Rule: manifest.yaml is the install contract — README.md calls it "source paths, install convention, and the classification inventory", and
    scripts/install_global.py symlinks from it. A capability naming a path that does not exist becomes a broken global symlink on the next install.
    """
    for cap in manifest_capabilities():
        counted()
        if not (ROOT / cap["path"].strip()).exists():
            fail("manifest", f"capability `{cap['id'].strip()}` names path `{cap['path'].strip()}` which does not exist")


def check_manifest_covers_library() -> None:
    """Nothing in personas/ or skills/ is missing from manifest.yaml.

    The orphan direction, and the one that grows silently: an unregistered skill is invisible to the installer, the routing catalogue and the validator at once,
    so it ships as a file nobody links. Rule: README.md states the manifest IS the classification inventory, which is only true if it is complete.
    """
    registered = {cap["path"].strip() for cap in manifest_capabilities()}
    if not registered:
        return
    for folder, pattern in (("personas", "*.md"), ("skills", "*")):
        base = ROOT / folder
        if not base.is_dir():
            continue
        for entry in sorted(base.glob(pattern)):
            # A folder's own index is navigation, not a capability. CATALOG_EXEMPT already names the same file for the coverage check, so both checks
            # agree on what README.md is rather than each keeping a private opinion.
            if entry.name.startswith(".") or entry.name in CATALOG_EXEMPT:
                continue
            counted()
            if f"{folder}/{entry.name}" not in registered:
                fail("manifest", f"{folder}/{entry.name} exists but no manifest.yaml capability registers it")


def check_package_skills_have_skill_md() -> None:
    """Every capability of kind `package` contains a SKILL.md.

    Rule: SKILL_STANDARD.md, "Required metadata" — "Every package skill has `SKILL.md` with valid YAML frontmatter". Frontmatter VALIDITY is checked by
    skills/skill-creator/scripts/quick_validate.py under `just test`; this asserts only the structural precondition, which is what a missing file breaks first.
    """
    for cap in manifest_capabilities():
        if cap["kind"].strip() != "package":
            continue
        counted()
        if not (ROOT / cap["path"].strip() / "SKILL.md").is_file():
            fail("skill-contract", f"package `{cap['id'].strip()}` has no SKILL.md")


def check_library_counts() -> None:
    """Prose counts of skills/capabilities match the manifest.

    Skill packages are directories, so the generic COUNT_CLAIMS check (which globs files) cannot see them. Rule: README.md and REVISION_NOTES.md both state
    library sizes; a stale number here is how a reader learns the wrong inventory. Historical lines marked `count:asat` are evidence, not live claims, and are
    exempt.

    "Capability" carries two meanings in this repo since the 2026-09-01 routing taxonomy: a manifest capability is an installable entry (persona or skill), while
    a ROUTING capability is a taxonomy term that skills, personas and gates reference. Only the first is what this check counts, so a claim explicitly qualified
    as "routing capabilities" is skipped. The qualifier is required precisely because the bare noun is ambiguous — an unqualified count is still checked.
    """
    caps = manifest_capabilities()
    if not caps:
        return
    actual = {
        "skills": sum(1 for c in caps if c["kind"].strip() != "persona"),
        "capabilities": len(caps),
    }
    for noun, expected in actual.items():
        pattern = re.compile(rf"(\d+)\s+(?!routing\b)(?:current\s+|package\s+)?{noun}\b", re.IGNORECASE)
        for surface in SURFACES:
            text = read(surface)
            if text is None:
                continue
            for line in without_code(text).splitlines():
                if ASAT_MARKER in line:
                    continue
                for claim in pattern.finditer(line):
                    counted()
                    if int(claim.group(1)) != expected:
                        fail("count", f"{surface} claims {claim.group(1)} {noun}; manifest.yaml holds {expected}")
