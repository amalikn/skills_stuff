#!/usr/bin/env python3
"""Check a project's adoption of the governed-file standard and add what is missing. Idempotent. Stdlib only.

Why (operator, 2026-10-10: "that skill is mostly used with bootstrap or refresh. So will calling slurp automatically engage the new features?"):
the standard's tools only act where they are installed. skill-slurp-chat runs this at every close, so a project reached by any slurp adopts it.

What it checks and, with --apply, adds:
1. justfile: the `ai_it` variable, `doc_freshness.py --check` in the `check` recipe, and the recipes stale, docs, history, history-show, rotate, budget, changelog-entry, move-sections, outline, section; a `check` recipe when there is none
   (from skill-ai-it `templates/justfile`; a project without one gets a new justfile). Refuses when the governed files are symlinks.
2. AGENTS.md: one line on triage, staleness and history, outside any managed block.
3. CHANGELOG.md and SCRATCHPAD.md: front matter with Kind, Budget and, for SCRATCHPAD, Keep and an open-items tracker; ROADMAP.md, when the project has
   one, with Kind, Budget and Archive, and `roadmap_trim.py` in the `rotate` recipe (2026-10-14: ROADMAP had no budget and no trim outside UNC).
4. scripts/doc-freshness-baseline.json: written when absent, so existing findings are grandfathered and new ones fail.
5. File roles (operator, 2026-10-14: the roles in references/governed-file-roles.md must reach every project, and files loaded whole stay small):
   `---` front matter on every root governance file that lacks it (README, AGENTS, AI_NAVIGATION, ARCHITECTURE, CONVENTIONS, SETUP; a legacy
   unfenced `Title:` block is fenced and moved above an `@` import), Authority/Scope/Last reviewed on the records, a `Budget` key on README,
   `role_check.py --check` in `check`, and scripts/role-check-baseline.json written when absent. A header it adds says `Review by` 30 days on,
   so the file is reviewed rather than stamped; an over-budget README is grandfathered in the freshness baseline (shrink-only from then on).

Usage:
    python scripts/adopt_governed_files.py --project-root P            # report what is missing
    python scripts/adopt_governed_files.py --project-root P --apply    # add it
Exit: 0 when adopted (or applied), 1 when something is missing in report mode, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
RECIPES = ("stale", "roles", "govern", "docs", "history", "history-show", "rotate", "budget", "changelog-entry", "move-sections", "outline", "section")
AGENTS_MARK = "just docs <folder>"
AGENTS_LINE = ("- Governed files: triage with `just docs <folder>` (one header line per file); run `just stale`; old CHANGELOG and SCRATCHPAD entries\n"
               "  live in `docs/history/`, read only on need (`just history <term>`, `just history-show <stamp>`). Large Markdown: `just outline <file>`,\n"
               "  then `just section <file> \"<title>\"` or a ranged Read.\n")


def template_recipes() -> str:
    """The recipe block to add, taken from the skill's justfile template so it never drifts.

    Returns:
        The text of the stale, docs, history, history-show, rotate, budget, changelog-entry, move-sections, outline and section recipes.
    """
    text = (SKILL / "templates" / "justfile").read_text(encoding="utf-8")
    start = text.index("# Session preflight: list stale docs")
    last = next((m for m in ("section *ARGS:", "move-sections *ARGS:") if m in text), "rotate *ARGS:")
    end = text.index("\n\n", text.index(last)) if last in text else len(text)
    return text[start:end].rstrip("\n") + "\n"


#: recipes that take free text (titles, heading names): `{{ARGS}}` is substituted unquoted, so a title with a semicolon ran as shell commands
#: (2026-10-10). They take quoted positional arguments instead.
FREE_TEXT = {"changelog-entry": "add_changelog_entry.py", "move-sections": "move_sections.py"}  # outline and section ship quoted


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


def rotate_lacks_roadmap(text: str) -> bool:
    """Whether the justfile's rotate recipe does not trim ROADMAP.md.

    Args:
        text: the justfile.

    Returns:
        True when a rotate recipe exists and none of its lines runs a roadmap trim.
    """
    m = re.search(r"^rotate\b[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", text, re.M)
    return bool(m) and "roadmap_trim" not in m.group(1)


def add_roadmap_to_rotate(text: str) -> str:
    """Append the ROADMAP trim to the rotate recipe, with the interpreter its other lines use.

    Args:
        text: the justfile.

    Returns:
        The updated justfile.
    """
    m = re.search(r"^rotate\b[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", text, re.M)
    if not m or "roadmap_trim" in m.group(1):
        return text
    first = m.group(1).splitlines()[0]
    indent = re.match(r"[ \t]+", first).group(0)
    interp = re.search(r"@?(\S+) \"\{\{ ?ai_it ?\}\}/scripts/", first)
    py = interp.group(1) if interp else "{{py}}"
    body = m.group(1) if m.group(1).endswith("\n") else m.group(1) + "\n"
    line = f'{indent}@{py.lstrip("@")} "{{{{ai_it}}}}/scripts/roadmap_trim.py" --project-root . {{{{ARGS}}}}\n'
    return text[:m.start(1)] + body + line + text[m.end(1):]


#: skill-owned recipes refreshed when a project's copy differs from the template; adoption otherwise only adds missing recipes, which left
#: cambium-swap on a `govern` that printed a blank reason (2026-10-14). Only the project form (`govern:`) is touched.
REFRESHED = ("govern",)
#: a recipe line that starts with the interpreter calling a skill script; a call inside `$(...)` (govern's navigation dry run) is not one
INTERP = re.compile(r'(?m)^[ \t]+@?(\{\{ ?\w+ ?\}\}|\S*python[\w.]*) "\{\{ ?ai_it ?\}\}/scripts/')


def adapt(block: str, text: str) -> str:
    """Fit template recipe text to a project's justfile: its interpreter, and no `_require-venv` dependency when it has no such recipe.

    Args:
        block: recipe text from the template.
        text: the project's justfile.

    Returns:
        The adapted recipe text.
    """
    used = INTERP.search(text)  # the interpreter the project's skill recipes already call (of-si: {{ai_py}})
    interp = used.group(1) if used else "{{py}}" if re.search(r"^py\s*:=", text, re.M) else "python3"
    if interp != "{{py}}":
        block = block.replace("{{py}}", interp)
    if not re.search(r"^_require-venv\b", text, re.M):
        block = block.replace(": _require-venv", ":")
    return block


def recipe_span(text: str, name: str) -> re.Match | None:
    """The project-form recipe `name:` with its comment and attribute lines and indented body.

    Args:
        text: the justfile.
        name: the recipe name.

    Returns:
        The match, or None when the recipe is absent or takes parameters (the skill's own `govern project="."`).
    """
    return re.search(rf"(?m)^(?:#[^\n]*\n|\[[\w-]+\]\n)*{re.escape(name)}:[^\n=]*\n(?:[ \t][^\n]*\n?)*", text)


def outdated_recipes(text: str) -> list[str]:
    """Skill-owned recipes whose project copy differs from the template.

    Args:
        text: the justfile.

    Returns:
        Recipe names to refresh.
    """
    recipes = split_recipes(template_recipes())
    out = []
    for name in REFRESHED:
        m = recipe_span(text, name)
        if m and name in recipes and m.group(0).rstrip("\n") != adapt(recipes[name], text).rstrip("\n"):
            out.append(name)
    return out


def justfile_gaps(text: str, roadmap: bool = False) -> list[str]:
    """What the justfile lacks.

    Args:
        text: the justfile.
        roadmap: the project has a ROADMAP.md, so `rotate` must trim it.

    Returns:
        Short names of the missing pieces.
    """
    gaps = []
    if roadmap and rotate_lacks_roadmap(text):
        gaps.append("rotate does not trim ROADMAP")
    if not re.search(r"^ai_it\s*:=", text, re.M):
        gaps.append("ai_it variable")
    if not re.search(r"^check\b", text, re.M):
        gaps.append("check recipe (nothing gates freshness)")  # smc-file-writing-analysis had none, so its adoption gated nothing (2026-10-10)
    elif "doc_freshness.py" not in text:
        gaps.append("freshness in check")
    elif not roles_in_check(text):
        gaps.append("roles in check")
    gaps += [f"recipe {r}" for r in RECIPES if not re.search(rf"^{re.escape(r)}\b", text, re.M)]
    if make_free_text_safe(text) != text:
        gaps.append("free-text recipes take unquoted {{ARGS}}")
    gaps += [f"recipe {r} outdated" for r in outdated_recipes(text)]
    return gaps


def fix_justfile(text: str, roadmap: bool = False) -> str:
    """Add the missing justfile pieces.

    Args:
        text: the justfile.
        roadmap: the project has a ROADMAP.md, so `rotate` must trim it.

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
        used = INTERP.search(text)  # the interpreter the project's skill recipes already call (of-si: {{ai_py}})
        interp = used.group(1) if used else "{{py}}" if re.search(r"^py\s*:=", text, re.M) else "python3"
        if interp != "{{py}}":
            block = block.replace("{{py}}", interp)
        if not re.search(r"^_require-venv\b", text, re.M):
            block = block.replace(": _require-venv", ":")  # of-si has `py :=` but no _require-venv recipe (2026-10-10)
        text = text.rstrip("\n") + "\n\n" + block
    if roadmap:
        text = add_roadmap_to_rotate(text)
    text = add_roles_to_check(text)
    recipes = split_recipes(template_recipes())
    for name in outdated_recipes(text):
        m = recipe_span(text, name)
        text = text[:m.start()] + adapt(recipes[name], text).rstrip("\n") + "\n" + text[m.end():]
    return make_free_text_safe(text)


def split_recipes(block: str) -> dict[str, str]:
    """Split a block of just recipes into one entry per recipe, each with the comment lines above it.

    Args:
        block: recipes as they appear in the template.

    Returns:
        Recipe name to its text (comments, attribute lines, header and indented body).
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
        # attribute lines (`[positional-arguments]`) belong to the recipe below; dropping them sent `"$@"` empty (outline, 2026-10-11)
        pending = pending + [line] if line.startswith("#") or re.match(r"^\[[\w-]+(\(.*\))?\]\s*$", line) else []
        i += 1
    return out


def records_gaps(path: pathlib.Path, kind: str) -> list[str]:
    """What a record's front matter lacks.

    Args:
        path: CHANGELOG.md, SCRATCHPAD.md or ROADMAP.md.
        kind: `log`, `state` or `roadmap`.

    Returns:
        Missing keys.
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    head = text.split("\n---", 1)[0] if text.startswith("---\n") else ""
    need = ["Kind:", "Budget:", "Authority:", "Scope:", "Last reviewed:"] + (["Archive:"] if kind == "roadmap" else [])
    need += (["Keep:", "Open items tracker:"] if kind == "state" and "Pinned sections:" not in head else [])
    return [k for k in need if k not in head]


def fix_record(path: pathlib.Path, kind: str, stamp: str) -> None:
    """Add the missing front-matter keys to a record.

    Args:
        path: the record.
        kind: `log` or `state`.
        stamp: today's stamp, for the tracker's file name.
    """
    text = path.read_text(encoding="utf-8")
    keys = {"Authority": "record" if kind == "log" else "working-state" if kind == "state" else "canonical", "Scope": RECORD_SCOPE[kind],
            "Kind": kind, "Budget": "200 lines"} | ({"Archive": "docs/history/ (roadmap-*.md, `just rotate`)"} if kind == "roadmap" else {})
    if "\nLast reviewed:" not in text.split("\n---", 1)[0]:
        # ROADMAP is a living document and needs a review date; take the newest date a record names (dated from its content), else today.
        # Dates after today are deadlines, not reviews (enterprise-strategy SCRATCHPAD, 2026-10-14, got a 25 Oct deadline as Last reviewed).
        today = dt.date.today().isoformat()
        dates = [d for d in re.findall(r"\b(20\d\d-[01]\d-[0-3]\d)\b", text) if d <= today]
        keys["Last reviewed"] = max(dates) if dates else dt.date.today().isoformat()
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
        title = {"log": "Changelog", "state": "Scratchpad", "roadmap": "Roadmap"}[kind]
        summary = {"log": "Newest entries only; older ones rotate to docs/history.",
                   "state": "Current working state; older entries rotate to docs/history, older open items to docs/trackers.",
                   "roadmap": "Current phase and open milestones; done items move to docs/history (just rotate)."}[kind]
        body = "\n".join(f"{k}: {v}" for k, v in keys.items())
        text = f"---\nTitle: {title}\nCategory: { {'log': 'change-log', 'state': 'working-state', 'roadmap': 'roadmap'}[kind] }\nStatus: current\nSummary: {summary}\n{body}\n---\n\n" + text
    path.write_text(text, encoding="utf-8")


#: root file -> (Category, Authority, Summary used when the file has no first paragraph to take one from)
HEADED = {
    "README.md": ("readme", "canonical", "Front door for people: what the project is, quick start, folder index and where the detail lives."),
    "AGENTS.md": ("agent-governance-guide", "local-supplement", "Rules every agent follows in this project."),
    "AI_NAVIGATION.md": ("navigation", "local-supplement", "Where project truth lives, what to read first and what is authoritative; a router, not the store."),
    "ARCHITECTURE.md": ("architecture", "canonical", "How the project works: components, data flow, boundaries and key decisions with reasons."),
    "CONVENTIONS.md": ("conventions", "canonical", "Naming, style and anti-patterns for this project."),
    "SETUP.md": ("setup", "canonical", "Prerequisites, pinned versions, bootstrap, environment variable names and first run."),
}
RECORD_SCOPE = {"log": "Dated changes to this project", "state": "Working state between sessions", "roadmap": "Current phase and open milestones"}


def fm_value(value: str) -> str:
    """A front-matter value as valid YAML: double-quoted when plain style would break (smc-resiliency README, 2026-10-14: `Scope: ... apn: what`).

    Args:
        value: the value as written, or a folded block (`>-` plus indented lines), which is returned unchanged.

    Returns:
        The value, quoted when it holds `: ` or ` #`, or starts with a YAML indicator character.
    """
    if value.startswith((">", "|")) or not value:
        return value
    if ": " in value or " #" in value or value.endswith(":") or value[0] in "!&*[]{}#|>'\"%@`,?-":
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def has_header(text: str) -> bool:
    """Whether the text opens with `---` front matter naming a Title and a Summary (role_check.py rule 1).

    Args:
        text: the file.

    Returns:
        True when it does.
    """
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return bool(m) and bool(re.search(r"(?m)^Title:", m.group(1))) and bool(re.search(r"(?m)^Summary:", m.group(1)))


def first_paragraph(body: str) -> str:
    """The first prose paragraph after the first heading, on one line and cut to fit a front-matter value.

    Args:
        body: the file without front matter.

    Returns:
        The paragraph, or "" when there is none.
    """
    h1 = re.search(r"(?m)^# .*$", body)
    after = body[h1.end():] if h1 else body
    for para in re.split(r"\n\s*\n", after):
        s = para.strip()
        if s and not s.startswith(("#", "-", "*", "|", "<!--", "```", "@", ">")) and not re.match(r"[A-Z][\w-]*(?: [\w-]+){0,2}: \S", s):  # a `Key: value` line, not a sentence
            s = re.sub(r"\s+", " ", re.sub(r"[`*]", "", s))
            return s if len(s) <= 190 else s[:187].rsplit(" ", 1)[0] + "..."
    return ""


def last_commit_day(root: pathlib.Path, rel: str) -> str:
    """The date the file was last committed, else today.

    Args:
        root: the project root.
        rel: the file, relative to it.

    Returns:
        YYYY-MM-DD.
    """
    r = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%as", "--", rel], capture_output=True, text=True)
    return r.stdout.strip() or dt.date.today().isoformat()


def header_gaps(root: pathlib.Path) -> list[str]:
    """Root governance files without front matter, and a README without a Budget key.

    Args:
        root: the project root.

    Returns:
        Short descriptions of the gaps.
    """
    gaps = []
    for name in HEADED:
        p = root / name
        if p.is_file() and not p.is_symlink():
            text = p.read_text(encoding="utf-8")
            if not has_header(text):
                gaps.append(f"{name}: front matter")
            elif name == "README.md" and not re.search(r"(?m)^Budget:", text.split("\n---", 1)[0]):
                gaps.append("README.md: Budget key")
    return gaps


def fix_header(root: pathlib.Path, name: str) -> None:
    """Give a root file `---` front matter: fence a legacy block (moving it above an `@` import), complete a partial one, or write a new one.

    The new header's Title is the first heading, its Summary the first paragraph; `Last reviewed` is the last commit and `Review by` 30 days on,
    so the file is read before it counts as reviewed. README also gets `Budget: 200 lines` (it is read whole).

    Args:
        root: the project root.
        name: the file name, a key of HEADED.
    """
    p = root / name
    text = p.read_text(encoding="utf-8")
    category, authority, fallback = HEADED[name]
    keys: dict[str, str] = {}
    imports: list[str] = []
    if text.startswith("---\n") and "\n---" in text[4:]:
        head, body = text[4:].split("\n---", 1)
        body = body.lstrip("\n")
        for ln in head.splitlines():
            if m := re.match(r"([A-Z][\w ]*):\s?(.*)$", ln):
                keys[m.group(1)] = m.group(2)
            elif keys:
                keys[list(keys)[-1]] += "\n" + ln  # a folded value's continuation
    else:
        lines = text.splitlines()
        i = 0
        while i < len(lines) and (not lines[i].strip() or lines[i].startswith("@")):
            imports += [lines[i]] if lines[i].startswith("@") else []
            i += 1
        j = i
        while j < len(lines) and (re.match(r"[A-Z][\w ]*: ", lines[j]) or (keys and re.match(r"[ \t]+\S", lines[j]))):
            if lines[j][0] in " \t":
                keys[list(keys)[-1]] += "\n" + lines[j]  # a folded value's continuation; it stayed outside the fence (UNC AGENTS.md, 2026-10-14)
            else:
                k, v = lines[j].split(": ", 1)
                keys[k] = v
            j += 1
        if "Title" not in keys:  # prose such as `Status: active` under the heading is not a legacy header
            keys, j = {}, i
        body = "\n".join(lines[j:]).lstrip("\n") + ("\n" if text.endswith("\n") else "")
    h1 = re.search(r"(?m)^# (.+)$", body)
    reviewed = keys.get("Last reviewed") or last_commit_day(root, name)
    fill = {"Title": h1.group(1).strip() if h1 else name[:-3].replace("_", " ").title(), "Category": category, "Status": "current",
            "Authority": authority, "Scope": f"Root {name} of {root.name}", "Last reviewed": reviewed, "Summary": first_paragraph(body) or fallback}
    new = {k: keys.get(k) or v for k, v in fill.items()}
    new |= {k: v for k, v in keys.items() if k not in new}
    if "Last reviewed" not in keys and "Review by" not in keys:
        new["Review by"] = (dt.date.today() + dt.timedelta(days=30)).isoformat()
    if name == "README.md" and "Budget" not in new:
        new["Budget"] = "200 lines"
    head = "\n".join(f"{k}: {fm_value(v)}" for k, v in new.items())
    p.write_text("---\n" + head + "\n---\n\n" + ("\n".join(imports) + "\n\n" if imports else "") + body, encoding="utf-8")


def grandfather_sizes(root: pathlib.Path, names: list[str]) -> None:
    """Record in the freshness baseline the size of each file adoption headed that is over budget, so the header's few lines (or README's new
    Budget key) do not fail a ratchet the operator's content did not break; cambium-swap's AGENTS.md went from 218 to 220 lines (2026-10-14).

    Args:
        root: the project root.
        names: the files adoption changed.
    """
    base = root / "scripts" / "doc-freshness-baseline.json"
    spec = importlib.util.spec_from_file_location("doc_freshness", SKILL / "scripts" / "doc_freshness.py")
    df = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("doc_freshness", df)
    spec.loader.exec_module(df)
    keys = {f"over-budget:{n}" for n in names}
    found = {k: v for k, v in df.findings(root, dt.date.today(), df.DEFAULT_WINDOW_DAYS).items() if k in keys}
    if found and base.is_file():
        data = json.loads(base.read_text(encoding="utf-8"))
        if any(data.get(k) != v for k, v in found.items()):
            data |= found
            base.write_text(json.dumps(dict(sorted(data.items())), indent=1) + "\n", encoding="utf-8")


def roles_in_check(text: str) -> bool:
    """Whether the justfile's check recipe runs role_check.py.

    Args:
        text: the justfile.

    Returns:
        True when it does.
    """
    m = re.search(r"^check\b[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", text, re.M)
    return bool(m) and "role_check.py" in m.group(1)


def add_roles_to_check(text: str) -> str:
    """Append role_check.py --check to the check recipe, with the interpreter its freshness line uses.

    Args:
        text: the justfile.

    Returns:
        The updated justfile.
    """
    m = re.search(r"^check\b[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", text, re.M)
    if not m or "role_check.py" in m.group(1):
        return text
    fresh = next((ln for ln in m.group(1).splitlines() if "doc_freshness.py" in ln), None)
    if fresh is None:
        return text
    line = fresh.replace("doc_freshness.py", "role_check.py")
    body = m.group(1) if m.group(1).endswith("\n") else m.group(1) + "\n"
    return text[:m.start(1)] + body + line + "\n" + text[m.end(1):]


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
    "check": "`just check`: the project's governance checks, then document freshness and file roles. Read-only; `safe`.",
    "govern": "`just govern`: governance up to the current skill-ai-it standard (adoption, record budgets with `just check`, role findings); content fixes are `/skill-ai-it refresh`. `modifies-files`.",
    "roles": "`just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.",
    "stale": "`just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.",
    "docs": "`just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.",
    "history": "`just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.",
    "history-show": "`just history-show <stamp>`: print one rotated entry. Read-only; `safe`.",
    "rotate": "`just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries and done ROADMAP items to docs/history, verified. Plan by default; `modifies-files`.",
    "budget": "`just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.",
    "changelog-entry": "`just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.",
    "move-sections": "`just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.",
    "outline": "`just outline <file.md>`: each heading with its line range, to read one section instead of the file. Read-only; `safe`.",
    "section": "`just section <file.md> \"<title>\"`: print one section (exact title, `Parent > Child`, `#anchor`, `~text`). Read-only; `safe`.",
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
    roadmap = (root / "ROADMAP.md").is_file()
    gaps += [f"justfile: {g}" for g in (justfile_gaps(justfile.read_text(encoding="utf-8"), roadmap) if justfile.is_file() else ["no justfile"])]
    gaps += ["AGENTS.md: governed-files line"] if agents_gap(root / "AGENTS.md") else []
    gaps += [f"CHANGELOG.md: {k}" for k in records_gaps(root / "CHANGELOG.md", "log")]
    gaps += [f"SCRATCHPAD.md: {k}" for k in records_gaps(root / "SCRATCHPAD.md", "state")]
    gaps += [f"ROADMAP.md: {k}" for k in records_gaps(root / "ROADMAP.md", "roadmap")]
    if not (root / "scripts" / "doc-freshness-baseline.json").is_file():
        gaps.append("baseline: scripts/doc-freshness-baseline.json")
    gaps += header_gaps(root)
    if not (root / "scripts" / "role-check-baseline.json").is_file():
        gaps.append("baseline: scripts/role-check-baseline.json")
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
    justfile.write_text(fix_justfile(justfile.read_text(encoding="utf-8"), roadmap), encoding="utf-8")
    document_recipes(root / "scripts" / "README.md", justfile.read_text(encoding="utf-8"))
    if agents_gap(root / "AGENTS.md"):
        fix_agents(root / "AGENTS.md")
    for name, kind in (("CHANGELOG.md", "log"), ("SCRATCHPAD.md", "state"), ("ROADMAP.md", "roadmap")):
        if records_gaps(root / name, kind):
            fix_record(root / name, kind, stamp)
    headed = [n for n in HEADED if (root / n).is_file() and not (root / n).is_symlink() and any(g.startswith(n) for g in header_gaps(root))]
    for name in headed:
        fix_header(root, name)
    if not (root / "scripts" / "doc-freshness-baseline.json").is_file():
        (root / "scripts").mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(SKILL / "scripts" / "doc_freshness.py"), "--project-root", str(root), "--write-baseline"], check=True)
    else:
        grandfather_sizes(root, headed + ["CHANGELOG.md", "SCRATCHPAD.md", "ROADMAP.md"])
    if not (root / "scripts" / "role-check-baseline.json").is_file():
        subprocess.run([sys.executable, str(SKILL / "scripts" / "role_check.py"), "--project-root", str(root), "--write-baseline"], check=True)
    print(f"{root.name}: applied; run the project's check, then `just rotate --apply` if a record is over budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
