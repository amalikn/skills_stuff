#!/usr/bin/env python3
"""Check a project's adoption of the governed-file standard and add what is missing. Idempotent. Stdlib only.

Why (operator, 2026-10-10: "that skill is mostly used with bootstrap or refresh. So will calling slurp automatically engage the new features?"):
the standard's tools only act where they are installed. skill-slurp-chat runs this at every close, so a project reached by any slurp adopts it.

What it checks and, with --apply, adds:
1. justfile: the `ai_it` variable, `doc_freshness.py --check` in the `check` recipe, and the recipes stale, docs, history, history-show, rotate, budget, changelog-entry, move-sections; a `check` recipe when there is none
   (from skill-ai-it `templates/justfile`; a project without one gets a new justfile). Refuses when the governed files are symlinks.
2. AGENTS.md: one line on triage, staleness and history, outside any managed block.
3. CHANGELOG.md and SCRATCHPAD.md: front matter with Kind, Budget and, for SCRATCHPAD, Keep and an open-items tracker.
4. scripts/doc-freshness-baseline.json: written when absent, so existing findings are grandfathered and new ones fail.

Usage:
    python scripts/adopt_governed_files.py --project-root P            # report what is missing
    python scripts/adopt_governed_files.py --project-root P --apply    # add it
Exit: 0 when adopted (or applied), 1 when something is missing in report mode, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import subprocess
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
RECIPES = ("stale", "docs", "history", "history-show", "rotate", "budget", "changelog-entry", "move-sections")
AGENTS_MARK = "just docs <folder>"
AGENTS_LINE = ("- Governed files: triage with `just docs <folder>` (one header line per file); run `just stale`; old CHANGELOG and SCRATCHPAD entries\n"
               "  live in `docs/history/`, read only on need (`just history <term>`, `just history-show <stamp>`).\n")


def template_recipes() -> str:
    """The recipe block to add, taken from the skill's justfile template so it never drifts.

    Returns:
        The text of the stale, docs, history, history-show, rotate and move-sections recipes.
    """
    text = (SKILL / "templates" / "justfile").read_text(encoding="utf-8")
    start = text.index("# Session preflight: list stale docs")
    last = "move-sections *ARGS:" if "move-sections *ARGS:" in text else "rotate *ARGS:"
    end = text.index("\n\n", text.index(last)) if last in text else len(text)
    return text[start:end].rstrip("\n") + "\n"


#: recipes that take free text (titles, heading names): `{{ARGS}}` is substituted unquoted, so a title with a semicolon ran as shell commands
#: (2026-10-10). They take quoted positional arguments instead.
FREE_TEXT = {"changelog-entry": "add_changelog_entry.py", "move-sections": "move_sections.py"}


def make_free_text_safe(text: str) -> str:
    """Give the free-text recipes `[positional-arguments]` and `"$@"` in place of `{{ARGS}}`.

    Args:
        text: the justfile.

    Returns:
        The justfile with those recipes quoted.
    """
    for name, script in FREE_TEXT.items():
        text = re.sub(rf'(?m)^({re.escape(name)} \*ARGS:[^\n]*\n\s+@[^\n]*{re.escape(script)}" --project-root \. )\{{{{ARGS\}}}}',
                      r'\1"$@"', text)
        text = re.sub(rf"(?m)^(?<!\[positional-arguments\]\n)({re.escape(name)} \*ARGS:)", r"[positional-arguments]\n\1", text)
    return text


def justfile_gaps(text: str) -> list[str]:
    """What the justfile lacks.

    Args:
        text: the justfile.

    Returns:
        Short names of the missing pieces.
    """
    gaps = []
    if not re.search(r"^ai_it\s*:=", text, re.M):
        gaps.append("ai_it variable")
    if not re.search(r"^check\b", text, re.M):
        gaps.append("check recipe (nothing gates freshness)")  # smc-file-writing-analysis had none, so its adoption gated nothing (2026-10-10)
    elif "doc_freshness.py" not in text:
        gaps.append("freshness in check")
    gaps += [f"recipe {r}" for r in RECIPES if not re.search(rf"^{re.escape(r)}\b", text, re.M)]
    if make_free_text_safe(text) != text:
        gaps.append("free-text recipes take unquoted {{ARGS}}")
    return gaps


def fix_justfile(text: str) -> str:
    """Add the missing justfile pieces.

    Args:
        text: the justfile.

    Returns:
        The updated justfile.
    """
    if not re.search(r"^ai_it\s*:=", text, re.M):
        m = re.search(r"^py\s*:=.*$", text, re.M)
        line = f'ai_it := "{SKILL}"'
        text = text[:m.end()] + "\n" + line + text[m.end():] if m else line + "\n" + text
    if re.search(r"^check\b", text, re.M) and "doc_freshness.py" not in text:
        m = re.search(r"^check\b[^\n]*\n((?:[ \t]+[^\n]*\n)+)", text, re.M)
        if m:
            indent = re.match(r"[ \t]+", m.group(1)).group(0)
            py = "{{py}}" if "py :=" in text else "python3"
            text = text[:m.end()] + f'{indent}@{py} "{{{{ai_it}}}}/scripts/doc_freshness.py" --project-root . --check\n' + text[m.end():]
    if not re.search(r"^check\b", text, re.M):
        py = "{{py}}" if "py :=" in text else "python3"
        text = text.rstrip("\n") + ("\n\n# Governance gate: document freshness (fails only on a finding the baseline does not excuse). Read-only.\n"
                                     f'check:\n    @{py} "{{{{ai_it}}}}/scripts/doc_freshness.py" --project-root . --check\n')
    missing = [r for r in RECIPES if not re.search(rf"^{re.escape(r)}\b", text, re.M)]
    if missing:
        recipes = split_recipes(template_recipes())
        block = "\n".join(recipes[r] for r in missing if r in recipes)
        used = re.search(r'@(\S+) "\{\{ai_it\}\}/scripts/', text)  # the interpreter the project's skill recipes already call (of-si: {{ai_py}})
        interp = used.group(1) if used else "{{py}}" if re.search(r"^py\s*:=", text, re.M) else "python3"
        if interp != "{{py}}":
            block = block.replace("{{py}}", interp)
        if not re.search(r"^_require-venv\b", text, re.M):
            block = block.replace(": _require-venv", ":")  # of-si has `py :=` but no _require-venv recipe (2026-10-10)
        text = text.rstrip("\n") + "\n\n" + block
    return make_free_text_safe(text)


def split_recipes(block: str) -> dict[str, str]:
    """Split a block of just recipes into one entry per recipe, each with the comment lines above it.

    Args:
        block: recipes as they appear in the template.

    Returns:
        Recipe name to its text (comments, header and indented body).
    """
    out: dict[str, str] = {}
    pending: list[str] = []
    lines = block.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Za-z][\w-]*)\b[^\n]*:", line)
        if m and not line.startswith("#"):
            body = [line]
            i += 1
            while i < len(lines) and lines[i][:1] in (" ", "\t"):
                body.append(lines[i])
                i += 1
            out[m.group(1)] = "\n".join(pending + body) + "\n"
            pending = []
            continue
        pending = pending + [line] if line.startswith("#") else []
        i += 1
    return out


def records_gaps(path: pathlib.Path, kind: str) -> list[str]:
    """What a record's front matter lacks.

    Args:
        path: CHANGELOG.md or SCRATCHPAD.md.
        kind: `log` or `state`.

    Returns:
        Missing keys.
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    head = text.split("\n---", 1)[0] if text.startswith("---\n") else ""
    need = ["Kind:", "Budget:"] + (["Keep:", "Open items tracker:"] if kind == "state" and "Pinned sections:" not in head else [])
    return [k for k in need if k not in head]


def fix_record(path: pathlib.Path, kind: str, stamp: str) -> None:
    """Add the missing front-matter keys to a record.

    Args:
        path: the record.
        kind: `log` or `state`.
        stamp: today's stamp, for the tracker's file name.
    """
    text = path.read_text(encoding="utf-8")
    keys = {"Kind": kind, "Budget": "200 lines, 25 KB"}
    if kind == "state":
        keys |= {"Keep": "Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3",
                 "Open items tracker": f"docs/trackers/open-items-{stamp}.md"}
    if text.startswith("---\n"):
        head, rest = text.split("\n---", 1)
        for k, v in keys.items():
            if f"\n{k}:" not in head and not head.startswith(f"---\n{k}:"):
                head += f"\n{k}: {v}"
        text = head + "\n---" + rest
    else:
        title = "Changelog" if kind == "log" else "Scratchpad"
        summary = ("Newest entries only; older ones rotate to docs/history." if kind == "log"
                   else "Current working state; older entries rotate to docs/history, older open items to docs/trackers.")
        body = "\n".join(f"{k}: {v}" for k, v in keys.items())
        text = f"---\nTitle: {title}\nCategory: {'change-log' if kind == 'log' else 'working-state'}\nStatus: current\nSummary: {summary}\n{body}\n---\n\n" + text
    path.write_text(text, encoding="utf-8")


def agents_gap(path: pathlib.Path) -> bool:
    """Whether AGENTS.md lacks the governed-files line.

    Args:
        path: the AGENTS.md file.

    Returns:
        True when the file exists and lacks it.
    """
    return path.is_file() and AGENTS_MARK not in path.read_text(encoding="utf-8")


def fix_agents(path: pathlib.Path) -> None:
    """Add the governed-files line before the managed navigation block, or at the end.

    Args:
        path: the AGENTS.md file.
    """
    text = path.read_text(encoding="utf-8")
    marker = "<!-- BEGIN MANAGED"
    text = text.replace(marker, AGENTS_LINE + "\n" + marker, 1) if marker in text else text.rstrip("\n") + "\n\n" + AGENTS_LINE
    path.write_text(text, encoding="utf-8")


RECIPE_DOCS = {
    "check": "`just check`: the project's governance checks, then document freshness. Read-only; `safe`.",
    "stale": "`just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.",
    "docs": "`just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.",
    "history": "`just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.",
    "history-show": "`just history-show <stamp>`: print one rotated entry. Read-only; `safe`.",
    "rotate": "`just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries to docs/history, verified. Plan by default; `modifies-files`.",
    "budget": "`just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.",
    "changelog-entry": "`just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.",
    "move-sections": "`just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.",
}


def document_recipes(readme: pathlib.Path, justfile_text: str) -> list[str]:
    """Add a line to scripts/README.md for each skill recipe the justfile has and the README does not mention as `just <name>`.

    A project whose checker requires every recipe to be documented failed after adoption added recipes (jdm, 2026-10-10).

    Args:
        readme: the project's scripts/README.md (left alone when it does not exist).
        justfile_text: the justfile after adoption.

    Returns:
        The recipe names documented now.
    """
    if not readme.is_file():
        return []
    text = readme.read_text(encoding="utf-8")
    missing = [r for r in RECIPE_DOCS if re.search(rf"^{re.escape(r)}\b", justfile_text, re.M) and f"just {r}" not in text]
    if missing:
        head = "" if "## Governance recipes (skill-ai-it)" in text else "\n## Governance recipes (skill-ai-it)\n\n"
        readme.write_text(text.rstrip("\n") + "\n" + head + "".join(f"- {RECIPE_DOCS[r]}\n" for r in missing), encoding="utf-8")
    return missing


def main(argv: list[str] | None = None) -> int:
    """Report or apply adoption for one project.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        0 adopted or applied, 1 missing pieces in report mode, 2 bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    links = [n for n in ("AGENTS.md", "CHANGELOG.md", "SCRATCHPAD.md") if (root / n).is_symlink()]
    if links:
        # ansible-wifi's governed files are links into local-knowledge-ansible; edits made here land in the other repo (2026-10-10)
        print(f"{root.name}: refused: {', '.join(links)} are symlinks; run with --project-root {(root / links[0]).resolve().parent}")
        return 1
    justfile = root / "justfile"
    gaps: list[str] = []
    gaps += [f"justfile: {g}" for g in (justfile_gaps(justfile.read_text(encoding="utf-8")) if justfile.is_file() else ["no justfile"])]
    gaps += ["AGENTS.md: governed-files line"] if agents_gap(root / "AGENTS.md") else []
    gaps += [f"CHANGELOG.md: {k}" for k in records_gaps(root / "CHANGELOG.md", "log")]
    gaps += [f"SCRATCHPAD.md: {k}" for k in records_gaps(root / "SCRATCHPAD.md", "state")]
    if not (root / "scripts" / "doc-freshness-baseline.json").is_file():
        gaps.append("baseline: scripts/doc-freshness-baseline.json")
    if not gaps:
        print(f"{root.name}: governed-file standard adopted")
        return 0
    print(f"{root.name}: missing " + "; ".join(gaps))
    if not args.apply:
        return 1
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    if not justfile.is_file():
        # a governed project without a justfile gets one, so the recipes AGENTS.md names exist (ansible-wifi governance, 2026-10-10)
        justfile.write_text(f"# Governance recipes from skill-ai-it templates/justfile (adopt_governed_files.py, {stamp}).\n"
                            f'py := "{sys.executable}"\n', encoding="utf-8")
    justfile.write_text(fix_justfile(justfile.read_text(encoding="utf-8")), encoding="utf-8")
    document_recipes(root / "scripts" / "README.md", justfile.read_text(encoding="utf-8"))
    if agents_gap(root / "AGENTS.md"):
        fix_agents(root / "AGENTS.md")
    for name, kind in (("CHANGELOG.md", "log"), ("SCRATCHPAD.md", "state")):
        if records_gaps(root / name, kind):
            fix_record(root / name, kind, stamp)
    if not (root / "scripts" / "doc-freshness-baseline.json").is_file():
        (root / "scripts").mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(SKILL / "scripts" / "doc_freshness.py"), "--project-root", str(root), "--write-baseline"], check=True)
    print(f"{root.name}: applied; run the project's check, then `just rotate --apply` if a record is over budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
