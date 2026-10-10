"""References resolve: named paths, index links, skill-package references, superseded documents marked in their index."""

from __future__ import annotations

import re
from pathlib import Path

from ..core import counted, fail
from ..config import (
    CATALOGS,
    CONDITIONAL_PATHS,
    EXAMPLE_MARKER,
    IGNORE_EXACT,
    IGNORE_PREFIXES,
    PATHLIKE,
    REPO_SUFFIXES,
    ROOT,
    SURFACES,
)
from ..helpers import (
    read,
    without_code,
)

def check_referenced_paths() -> None:
    """Every repo-relative path named in a governance surface resolves on disk."""
    for surface in SURFACES:
        text = read(surface)
        if text is None:
            fail("surface", f"{surface} is listed as a governance surface but does not exist")
            counted()
            continue
        body = "\n".join(l for l in without_code(text).splitlines() if EXAMPLE_MARKER not in l)
        tokens = set(re.findall(r"`([^`\n]+)`", body))
        tokens |= {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", body)}
        for raw in sorted(tokens):
            tok = raw.split("#", 1)[0].strip().rstrip("/")
            if not tok or tok in IGNORE_EXACT or tok in CONDITIONAL_PATHS or tok.startswith(IGNORE_PREFIXES):
                continue
            if not PATHLIKE.match(tok):
                continue
            # A token with no letters is not a path. `2/3`, `16/19`, `60/60` are fractions and scores, and this project's prose is full of them; three false
            # failures in one session (`n/a`, `2/3`, and a near-miss on a ratio) is enough evidence that the exclusion is needed. It cannot hide a real path,
            # because every path in this repo contains at least one letter — asserted below so the exemption cannot silently widen.
            if not any(c.isalpha() for c in tok):
                continue
            suffix = Path(tok).suffix
            if "/" not in tok and suffix not in REPO_SUFFIXES:
                continue
            if suffix and suffix not in REPO_SUFFIXES:
                continue
            counted()
            # Resolve relative to the file that MAKES the reference first, then relative to ROOT. Resolving only against ROOT false-fails every correct relative
            # link written inside a subfolder README.
            near = (ROOT / surface).parent / tok
            if not near.exists() and not (ROOT / tok).exists():
                fail("path", f"{surface} references `{tok}` which does not exist")


def check_index_links() -> None:
    """Links inside an index file resolve, relative to the index's own folder."""
    for index in CATALOGS:
        text = read(index)
        if text is None:
            fail("index", f"catalog {index} does not exist")
            counted()
            continue
        base = (ROOT / index).parent
        for target in {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", without_code(text))}:
            tok = target.split("#", 1)[0].strip()
            if not tok or tok.startswith(IGNORE_PREFIXES):
                continue
            counted()
            if not (base / tok).exists():
                fail("index", f"{index} links `{tok}` which does not exist")


def check_skill_package_references() -> None:
    """Every in-package path a SKILL.md names — in prose OR in a command — resolves inside that package.

    THE HOLE THIS CLOSES. check_referenced_paths reads registered governance SURFACES, so until 20260903 no check had ever opened a `skills/*/SKILL.md` and asked
    whether its own references exist. A staleness audit that day found 11 across four packages: `skills/devops/SKILL.md` advertised a `### Scripts` section
    listing two automation scripts that were never imported, and `product-strategist` listed four reference files and four runnable scripts, none of which exist.
    An agent invoking one of those skills is told a capability is available and reaches for something that is not there — mid-task, with no error to read.

    COMMANDS INSIDE FENCES COUNT. `product-strategist`'s four were written as `python scripts/market_sizing.py ...` inside a ```bash block, which every
    prose-oriented scanner skips by construction. Five of the sixteen findings were only visible this way, which is the argument for checking the invocation form
    separately rather than trusting one pattern.

    An `<!-- claim-scan:examples -->` marker exempts a file whose paths are ILLUSTRATIVE — `skill-creator` teaches skill structure and names `references/finance.md`
    to show the shape, not to point at a file. The marker is the same one the audit tooling honours, so the two agree rather than each keeping a private list.
    """
    for md in sorted(ROOT.glob("skills/*/SKILL.md")):
        pkg = md.parent
        text = md.read_text(encoding="utf-8", errors="replace")
        counted()
        if EXAMPLE_MARKER in text:
            continue
        named: set[str] = set()
        prose = without_code(text)
        for m in re.finditer(r"`([^`\n]+)`", prose):
            named.add(m.group(1).strip())
        # The invocation form, read from the WHOLE file including fenced blocks — that is where it lives.
        for m in re.finditer(r"\b(?:python3?|bash|sh|node)\s+((?:scripts|assets|bin|templates|references|resources)/[\w./-]+)", text):
            named.add(m.group(1))
        for tok in sorted(named):
            if not tok.startswith(("scripts/", "assets/", "templates/", "references/", "resources/")):
                continue
            if not PATHLIKE.match(tok):
                continue
            counted()
            # Package-relative OR repo-relative. `skill-agent-stack` correctly names scripts/close_route.py at the repo root, and reading that as a
            # package path reported a defect that does not exist. Only a token resolving NOWHERE is a promise the agent cannot collect on.
            if not (pkg / tok).exists() and not (ROOT / tok).exists():
                fail("skill-refs", f"{md.relative_to(ROOT)} names {tok}, which exists neither in {pkg.name}/ nor at the repo root; "
                                  f"an agent invoking this skill is promised a capability that is absent")


def check_superseded_marked_in_index() -> None:
    """A document declaring `Status: superseded` says so in the index that routes readers to it.

    `.archcore/` is this project's HIGHEST authority — AI_NAVIGATION.md routes there first — so its index is the surface an agent reads before deciding which
    document is binding. On 20260903 that index listed four retired sync documents with no indication of their state: the banners were inside the files, and a
    reader scanning the index for the governing rule saw four live entries.

    This is the Phase 3 defect inverted. The usual failure is a supersession recorded in a routing table that never reaches the superseded file; here it reached
    the file and never reached the routing table. Both leave a reader acting on a retired rule, so both need the check.

    Derived from each document's own `Status:` line rather than a hand-kept list, because a hand-kept list of what is superseded drifts exactly as the thing it
    polices does.
    """
    index = ROOT / ".archcore" / "README.md"
    if not index.is_file():
        return
    body = index.read_text()
    for doc in sorted((ROOT / ".archcore").rglob("*.md")):
        if doc.name == "README.md":
            continue
        counted()
        if not re.search(r"^Status:\s*superseded\s*$", doc.read_text(encoding="utf-8", errors="replace"), re.M):
            continue
        rel = doc.relative_to(ROOT / ".archcore").as_posix()
        row = re.search(rf"^\|\s*\[([^\]]+)\]\({re.escape(rel)}\)", body, re.M)
        if row is None:
            fail("supersession", f".archcore/{rel} is superseded but the index does not link it at all")
        elif "SUPERSEDED" not in row.group(1).upper():
            fail("supersession", f".archcore/{rel} declares Status: superseded, but .archcore/README.md lists it as though it were live; "
                                 f"the index is where a reader decides which document binds")
