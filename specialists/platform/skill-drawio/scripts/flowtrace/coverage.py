"""The other direction of the trace: code no flow mentions, steps that cite no code, and step words the code no longer holds. Stdlib only.

A stamp can only watch code a step already cites, so a new helper would pass unseen; traceability is checked both ways for that reason (jamb).
The map's optional `trace:` block sets it up:

    trace:
      cover: [tasks/**/*.yml, files/*.py]          # every file these match must be cited by a step or component, or exempt
      exempt: {files/tests/*: tests, not behaviour} # glob: why no flow needs to cite it
      uncited_steps: 42                            # shrink-only: most steps allowed without a code reference
      known_words: [some_term]                     # step words checked and found fine though the covered code does not hold them

Imported, not run: `from flowtrace import coverage` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

#: Words in a step that name something in the code: a path, a file, or an identifier with an underscore.
NAMED = re.compile(r"(?<![\w/.-])(?:/[\w.-]+(?:/[\w.-]+)+|[\w-]+\.(?:py|sh|yml|yaml|json|csv|j2|service|timer)|[a-z][a-z0-9]*(?:_[a-z0-9]+)+)(?![\w/-])")


def covered_files(root: Path, trace: dict) -> list[str]:
    """Every file `trace.cover` matches.

    Args:
        root: the project root.
        trace: the map's `trace:` block.

    Returns:
        Root-relative paths, sorted.
    """
    return sorted({p.relative_to(root).as_posix() for g in trace.get("cover", []) for p in root.glob(g) if p.is_file()})


def cited_files(data: dict) -> set[str]:
    """Every file a step or component cites.

    Args:
        data: the loaded map.

    Returns:
        The paths.
    """
    refs = [r for c in data["components"] for r in c.get("code", [])] + [r for f in data["flows"] for s in f["steps"] for r in s.get("code", [])]
    return {r.partition(":")[0] for r in refs}


def is_exempt(path: str, exempt: dict) -> bool:
    """Whether a file is exempt.

    Args:
        path: the root-relative path.
        exempt: {glob: reason}.

    Returns:
        True when a glob matches it.
    """
    return any(PurePosixPath(path).match(g) or path == g for g in exempt)


def coverage_problems(root: Path, data: dict) -> list[str]:
    """Covered files no flow cites, exempt globs that match nothing, and steps over the `uncited_steps` allowance.

    Args:
        root: the project root.
        data: the loaded map.

    Returns:
        One message each; empty with no `trace:` block.
    """
    trace = data.get("trace") or {}
    if not trace:
        return []
    files, cited, exempt = covered_files(root, trace), cited_files(data), trace.get("exempt") or {}
    out = [f"uncovered: {p} is cited by no step or component (cite it, or add it to trace.exempt with a reason)"
           for p in files if p not in cited and not is_exempt(p, exempt)]
    out += [f"stale exempt: `{g}` matches no covered file" for g in exempt if not any(is_exempt(p, {g: ""}) for p in files)]
    limit = trace.get("uncited_steps")
    if limit is not None:
        count = sum(1 for f in data["flows"] for s in f["steps"] if not s.get("code"))
        if count > limit:
            out.append(f"uncited steps: {count} steps cite no code, trace.uncited_steps allows {limit}")
        elif count < limit:
            out.append(f"ratchet: {count} steps cite no code; lower trace.uncited_steps from {limit} to {count}")
    return out


def stale_words(root: Path, data: dict) -> list[str]:
    """Step words that name something the covered code does not hold: a removed path, a renamed helper, a script that went away. A warning, for a
    person to read; a name can sit outside the code on purpose (`trace.known_words`).

    Args:
        root: the project root.
        data: the loaded map.

    Returns:
        "<flow>/<step>: `<word>`" per word, in map order.
    """
    trace = data.get("trace") or {}
    if not trace.get("cover"):
        return []
    known = set(trace.get("known_words") or [])
    paths = set(covered_files(root, trace)) | cited_files(data)
    code = "\n".join((root / p).read_text(encoding="utf-8", errors="replace") for p in sorted(paths) if (root / p).is_file())
    out = []
    for f in data["flows"]:
        for s in f["steps"]:
            for word in dict.fromkeys(w.rstrip(".") for w in NAMED.findall(s["action"])):
                if word not in known and word not in code and word.rsplit("/", 1)[-1] not in code:
                    out.append(f"{f['id']}/{s['id']}: `{word}`")
    return out
