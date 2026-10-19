#!/usr/bin/env python3
"""Check a project's code file names and task-runner recipe names against skill-coder's naming mapping, as a shrink-only ratchet. Read-only
unless --write-baseline. Stdlib only.

Why (operator, 2026-10-19: "define a mapping for language against convention"; "is it better to have a json or yaml or toml file for the mapping"):
the mapping lives as data in the pack's `naming.toml` (TOML, so this runs with the project's own Python), and this checks what can be seen without
parsing code: file names by language, and `just` recipe names. Names inside code (functions, variables, classes) are the language linter's job; each
such row in the mapping names the tool.

A project overrides the mapping in its `code-map.toml`:
    [naming]
    recipe = "snake_case"                  # this project's recipes keep underscores
    [naming.files]
    "*.js" = "kebab-case"                  # this project's JavaScript files
keeps a name with a reason in `[naming.exceptions]` ("recipe nav_upgrade" = "owned by skill-ai-it's template"), and leaves files out with
`[scan.exclude]`. Python dunder files (`__init__.py`, `__main__.py`) and private recipes (a leading `_`) are judged without
their underscores. Existing names that break the rule go in the baseline and are renamed when next touched.

Usage:
    naming_check.py --project-root . [--roots src,scripts] [--baseline scripts/naming-baseline.json] [--list] [--write-baseline]
Exit: 0 when nothing new breaks the mapping and the baseline is current, 1 otherwise, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
import tomllib
from pathlib import Path

import code_map
import ratchet

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
#: The pack's mapping (the source of truth; references/naming-conventions.md's table is rendered from it).
MAPPING = Path(__file__).resolve().parent.parent / "naming.toml"
CHECKS = ("file", "recipe", "linter")
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", "vendor", "dist", "build"}
#: A recipe header: a name at the start of a line, optional parameters (which may hold `="default"`), then a colon that is not `:=`.
RECIPE = re.compile(r"^(@?)([A-Za-z_][\w-]*)\s*(?:[*+$A-Za-z_].*?)?:(?!=)", re.M)


def load_mapping(path: Path = MAPPING) -> dict:
    """Read and check the naming mapping.

    Args:
        path: the TOML file.

    Returns:
        {"conventions": {name: regex}, "rule": [rule, ...]}.

    Raises:
        ValueError: when a rule has an unknown check, or a file or recipe rule names a convention with no regex or has no globs.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    conventions, problems = data.get("conventions", {}), []
    for i, rule in enumerate(data.get("rule", [])):
        where = f"rule {i + 1} ({rule.get('language')}, {rule.get('element')})"
        if rule.get("check") not in CHECKS:
            problems.append(f"{where}: check must be one of {', '.join(CHECKS)}")
        elif rule["check"] in ("file", "recipe") and rule.get("convention") not in conventions:
            problems.append(f"{where}: a checked rule needs a convention with a regex in [conventions]")
        elif rule["check"] == "file" and not rule.get("globs"):
            problems.append(f"{where}: a file rule needs globs")
        elif rule["check"] == "linter" and not rule.get("tool"):
            problems.append(f"{where}: a linter rule names the tool that checks it")
    if problems:
        raise ValueError(f"{path.name}: " + "; ".join(problems))
    return data


def _stem(name: str) -> str:
    """A file or recipe name as judged: suffix removed, dunder and private underscores stripped.

    Args:
        name: the file name or recipe name.

    Returns:
        The part the convention applies to.
    """
    stem = name.split(".", 1)[0] if "." in name else name
    return stem.strip("_")


def file_findings(root: Path, roots: list[str], mapping: dict, overrides: dict, exclude: set[str]) -> dict[str, str]:
    """Code files whose names break their language's convention.

    Args:
        root: the project root.
        roots: folders to scan.
        mapping: load_mapping()'s result.
        overrides: {glob: convention} from the project's [naming.files].
        exclude: repo-relative files never checked ([scan.exclude]).

    Returns:
        {"file <path>": "<convention> (<language>)"} per breaking file.
    """
    regex = {k: re.compile(v) for k, v in mapping["conventions"].items()}
    rules = [(g, r["convention"], r["language"], tuple(r.get("exclude_globs", ()))) for r in mapping["rule"] if r["check"] == "file" for g in r["globs"]]
    rules = [(g, overrides.get(g, conv), lang, ex) for g, conv, lang, ex in rules] + [(g, c, "project", ()) for g, c in overrides.items()
                                                                                       if g not in {r[0] for r in rules}]
    out: dict[str, str] = {}
    for folder in roots:
        for path in sorted((root / folder).rglob("*")) if (root / folder).is_dir() else []:
            rel = path.relative_to(root).as_posix()
            if not path.is_file() or rel in exclude or SKIP_PARTS & set(path.parts):
                continue
            for glob, conv, lang, ex in rules:
                if fnmatch.fnmatch(path.name, glob) and not any(fnmatch.fnmatch(rel, e) for e in ex):
                    if conv not in regex:
                        raise ValueError(f"[naming.files] {glob}: unknown convention {conv}")
                    if not regex[conv].match(_stem(path.name)):
                        out[f"file {rel}"] = f"{conv} ({lang})"
                    break
    return out


def recipe_findings(root: Path, mapping: dict, convention: str | None) -> dict[str, str]:
    """`just` recipes whose names break the recipe convention.

    Args:
        root: the project root (its justfile is read).
        mapping: load_mapping()'s result.
        convention: the project's [naming] recipe override, or None for the mapping's.

    Returns:
        {"recipe <name>": "<convention>"} per breaking recipe.

    Raises:
        ValueError: when the convention has no regex.
    """
    runner = next((root / n for n in ("justfile", "Justfile", ".justfile") if (root / n).is_file()), None)
    if runner is None:
        return {}
    conv = convention or next(r["convention"] for r in mapping["rule"] if r["check"] == "recipe")
    if conv not in mapping["conventions"]:
        raise ValueError(f"[naming] recipe: unknown convention {conv}")
    pattern = re.compile(mapping["conventions"][conv])
    names = {m.group(2) for m in RECIPE.finditer(runner.read_text(encoding="utf-8")) if m.group(2) not in ("set", "export", "import", "mod", "alias")}
    return {f"recipe {n}": conv for n in sorted(names) if not pattern.match(_stem(n))}


def exceptions(naming: dict) -> dict[str, str]:
    """Names a project keeps although they break the mapping, each with its reason (for example recipes owned by another skill's template).

    Args:
        naming: the code map's [naming] section.

    Returns:
        {"file <path>" or "recipe <name>": reason}.

    Raises:
        ValueError: when an entry has no reason.
    """
    out = dict(naming.get("exceptions", {}))
    if blank := [k for k, v in out.items() if not str(v).strip()]:
        raise ValueError(f"[naming.exceptions] entries need a reason: {', '.join(blank)}")
    return out


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when within the baseline and current, 1 otherwise, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--roots", help="comma-separated folders (default: the code map's [scan] roots, else src,scripts)")
    ap.add_argument("--baseline", default="scripts/naming-baseline.json")
    ap.add_argument("--list", action="store_true", help="print every name that breaks the mapping")
    ap.add_argument("--write-baseline", action="store_true", help="record today's names (adoption or after renames)")
    ap.add_argument("--code-map", type=Path, help="the project's code-map.toml (default: code-map.toml at the root when present)")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    try:
        cmap, mapping = code_map.for_root(root, args.code_map), load_mapping()
        naming = code_map.section(cmap, "naming")
        roots = [r for r in (args.roots or code_map.scan_roots(cmap)).split(",") if r]
        kept = exceptions(naming)
        found = {**file_findings(root, roots, mapping, dict(naming.get("files", {})), set(code_map.excluded(cmap))),
                 **recipe_findings(root, mapping, naming.get("recipe"))}
        stale = sorted(k for k in kept if k not in found)
        found = {k: v for k, v in found.items() if k not in kept}
    except (OSError, ValueError) as exc:
        print(f"naming_check: {exc}", file=sys.stderr)
        return 2
    if args.list:
        print("\n".join(f"{key}: expected {conv}" for key, conv in found.items()))
    base_path = root / args.baseline
    counts = {key: 1 for key in found}
    if args.write_baseline:
        ratchet.save(base_path, counts)
        print(f"naming_check: baseline written, {len(counts)} name(s)")
        return 0
    verdict = ratchet.compare(counts, ratchet.load(base_path))
    lines = ratchet.report(verdict, "naming", base_path) + [f"STALE naming: exception {k} no longer breaks the mapping (or is gone): remove it" for k in stale]
    print("\n".join(lines) or f"naming_check: OK, {len(counts)} name(s) off the mapping in the baseline, {len(kept)} kept by exception")
    return 0 if verdict.ok and not stale else 1


if __name__ == "__main__":
    sys.exit(main())
