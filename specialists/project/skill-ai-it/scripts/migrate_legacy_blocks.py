#!/usr/bin/env python3
"""Move a project's managed blocks from the pre-2026-09-23 layout to the template-sourced one without losing project content.

Before 2026-09-23 the managed blocks were where projects wrote their own material: the scripts block held the whole scripts
README (task catalogue, runtimes table, notes), and projects added rules and routing rows inside the navigation and agents
blocks. `nav_upgrade` replaces a block wholesale, so on those projects it deletes that material; the upgrader now refuses
them (`refused-legacy-layout`). This script is the `refresh` step that makes them upgradeable.

For each legacy block it splits the body into sections by heading and compares each one with every block the skill could
have emitted: the builders and templates of the three commits that shipped the `2026-08-11` stamp, plus the current ones.

- A section matching one of those, after whitespace, table padding and recipe-name normalisation, is skill text and is
  dropped; the current template block replaces it.
- A section whose heading the skill never emitted is project-authored and moves outside the block, unchanged.
- In `scripts/README.md`, every section the current block does not contain (Runtimes, Task Inventory, Raw Script Inventory,
  Safety Labels, Notes) moves outside, since the template-sourced layout keeps them there.
- A skill-headed section the project edited cannot be split mechanically. It is copied verbatim under a
  `## Moved from the managed block` heading below the block and reported, so the operator trims it to the project's own lines.
- Text before the first heading that is not skill text (project rules typed above the template's heading) moves above
  the block.

Blocks with the `skill-ai-it:manual` opt-out, or stamped on or after LAYOUT_SINCE, are left alone. `--dry-run` reports the
classification and writes nothing. The Contents block is not rebuilt here; run the markdown rewrap tool with
`--no-wrap --update` afterwards.

Exit status: 0 nothing to do, 2 files changed (or would change), 3 at least one edited skill section needs trimming by hand.
"""
import argparse
import difflib
import importlib.util
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)

# The commits whose builders or templates emitted blocks stamped 2026-08-11-governance-checks-layer-v1 (the stamp was
# introduced in 3ab6c94 and retired by 293c42b, so 293c42b^ is its last state).
LEGACY_COMMITS = ["3ab6c94", "1567158", "adcbea4", "293c42b^"]

FILES = {"AI_NAVIGATION.md": "navigation", "AGENTS.md": "navigation", "scripts/README.md": "scripts"}
MOVED_HEADING = "## Moved from the managed block"


def load_upgrader(scripts_dir, name):
    """Import an upgrade_navigation_control_layer.py from scripts_dir as a module, with that directory as the working directory.

    The upgrader resolves its templates relative to its own location, so the import happens from inside the directory and
    the previous working directory is restored whatever happens.
    """
    spec = importlib.util.spec_from_file_location(name, os.path.join(scripts_dir, "upgrade_navigation_control_layer.py"))
    module = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(scripts_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        os.chdir(cwd)
    return module


def emitted_blocks(module, tmpl_dir):
    """Every block body one revision could emit, keyed by block section: its builder output plus its raw templates."""
    out = {"navigation": [], "scripts": []}
    for fn, sec in [("build_navigation_block", "navigation"), ("build_agents_block", "navigation"), ("build_scripts_block", "scripts")]:
        if hasattr(module, fn):
            try:
                out[sec].append(getattr(module, fn)())
            except SystemExit:
                pass
    for f, sec in [("AI_NAVIGATION.md", "navigation"), ("AGENTS-navigation-block.md", "navigation"), ("scripts-README.md", "scripts")]:
        p = os.path.join(tmpl_dir, f)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                out[sec].append(fh.read())
    return out


def reference_sections(current):
    """Map section -> heading -> set of normalised bodies, across the legacy commits and the current package.

    A legacy revision that cannot be extracted (shallow clone, rewritten history) is skipped with a warning: the current
    package alone still classifies most sections, and anything it cannot match is reported as edited, never dropped.
    """
    blocks = {"navigation": [], "scripts": []}
    for sec, texts in emitted_blocks(current, os.path.join(SKILL_DIR, "templates")).items():
        blocks[sec] += texts
    with tempfile.TemporaryDirectory() as tmp:
        for c in LEGACY_COMMITS:
            d = os.path.join(tmp, c.replace("^", "p"))
            os.makedirs(d)
            arc = subprocess.run(["git", "-C", SKILL_DIR, "archive", c, "scripts", "templates"], capture_output=True)
            if arc.returncode != 0:
                print(f"WARNING: cannot read skill-ai-it at {c}; classifying without it", file=sys.stderr)
                continue
            subprocess.run(["tar", "-x", "-C", d], input=arc.stdout, check=True)
            mod = load_upgrader(os.path.join(d, "scripts"), "legacy_" + c.replace("^", "p"))
            for sec, texts in emitted_blocks(mod, os.path.join(d, "templates")).items():
                blocks[sec] += texts
    table = {"navigation": {}, "scripts": {}}
    for sec, texts in blocks.items():
        for t in texts:
            for head, body in split_sections(t):
                table[sec].setdefault(head, set()).add(normalise(body, current))
    return table


def rename_recipes(text, current):
    """Apply the template recipe renames, so text written before the snake_case rename compares equal."""
    for old in sorted(current.TEMPLATE_RECIPE_RENAMES, key=len, reverse=True):
        text = re.sub(rf"(?<![\w-]){re.escape(old)}(?![\w-])", current.TEMPLATE_RECIPE_RENAMES[old], text)
    return text


def normalise(text, current):
    """Reduce a section body to its words: comments, line wrapping, table padding and recipe spelling removed."""
    text = rename_recipes(text, current)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"\|\s*:?-{3,}:?\s*", "|---", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*\|\s*", "|", text)
    return text.strip()


def split_sections(body):
    """Split markdown into (heading, text) pairs at `##`-`####` headings; text before the first heading has heading ''."""
    out, head, buf = [], "", []
    for line in body.split("\n"):
        if re.match(r"^#{2,4} ", line):
            out.append((head, "\n".join(buf)))
            head, buf = line.rstrip(), []
        else:
            buf.append(line)
    out.append((head, "\n".join(buf)))
    return out


def find_block(text, section):
    """Return (start, end, body) of the section's managed block, or None when the markers are absent."""
    begin = f"<!-- BEGIN MANAGED: skill-ai-it:{section} -->"
    end = f"<!-- END MANAGED: skill-ai-it:{section} -->"
    m = re.search(re.escape(begin) + r"(.*?)" + re.escape(end), text, re.S)
    return (m.start(), m.end(), m.group(1)) if m else None


def classify(body, section, refs, current, new_headings):
    """Label each section of a legacy block body: toc, skill, project, outside (scripts sections the new block omits) or edited."""
    rows = []
    for head, text in split_sections(body):
        norm = normalise(text, current)
        if head.strip() == "## Contents":
            kind = "toc"
        elif head == "":
            kind = "skill" if (not norm or norm in refs[section].get("", set())) else "preamble"
        elif section == "scripts" and head.strip() not in new_headings:
            kind = "outside"
        elif head.strip() not in {h.strip() for h in refs[section]}:
            kind = "project"
        elif norm in refs[section][head]:
            kind = "skill"
        else:
            kind = "edited"
        rows.append((head, text, kind))
    return rows


def migrate_text(text, section, block, refs, current):
    """Rebuild one file: current block in place of the legacy one, project material moved around it. Returns (text, rows) or None."""
    found = find_block(text, section)
    if not found:
        return None
    start, end, body = found
    if current.MANUAL_TOKEN in body:
        return None
    stamp = re.search(re.escape(current.VERSION_MARKER) + r"\s*(\S+)", body)
    if not stamp or stamp.group(1) >= current.LAYOUT_SINCE:
        return None
    new_headings = {h.strip() for h, _ in split_sections(block) if h}
    rows = classify(body, section, refs, current, new_headings)
    before, after, edited = [], [], []
    # Project material that preceded every skill section stays above the block, so reading order survives (a runtimes
    # table that opened the file still opens it); the rest goes below.
    first_skill = next((i for i, (h, _, k) in enumerate(rows) if h and k in ("skill", "edited")), len(rows))
    for i, (head, sec_text, kind) in enumerate(rows):
        chunk = (head + "\n" + sec_text).strip("\n") if head else sec_text.strip("\n")
        if kind == "preamble" or (kind in ("project", "outside") and i < first_skill):
            before.append(rename_recipes(chunk, current))
        elif kind in ("project", "outside"):
            after.append(rename_recipes(chunk, current))
        elif kind == "edited":
            edited.append("#" + rename_recipes(chunk, current))
    parts = [text[:start].rstrip("\n")]
    if before:
        parts.append("\n\n".join(before))
    parts.append(block.rstrip("\n"))
    if after:
        parts.append("\n\n".join(after))
    if edited:
        parts.append(MOVED_HEADING + "\n\n<!-- Edited copies of skill sections, kept verbatim by migrate_legacy_blocks.py. Keep only the lines that are "
                     "specific to this project, then remove this comment. -->\n\n" + "\n\n".join(edited))
    tail = text[end:].lstrip("\n")
    new = "\n\n".join(p for p in parts if p) + ("\n\n" + tail if tail else "\n")
    return new, rows


def main():
    """Migrate the legacy managed blocks of one project; see the module docstring for the rules and exit codes."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.project_root)
    current = load_upgrader(HERE, "current_upgrader")
    refs = reference_sections(current)
    builders = {"AI_NAVIGATION.md": current.build_navigation_block, "AGENTS.md": current.build_agents_block,
                "scripts/README.md": current.build_scripts_block}
    changed, needs_trim = [], False
    for rel, section in FILES.items():
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        result = migrate_text(text, section, builders[rel](), refs, current)
        if not result:
            continue
        new, rows = result
        print(f"== {rel}")
        for head, _, kind in rows:
            print(f"  {kind:8} {head.strip() or '(text before first heading)'}")
        if any(k == "edited" for _, _, k in rows):
            needs_trim = True
            print(f"  -> edited skill sections copied under '{MOVED_HEADING}'; trim them by hand")
        changed.append(rel)
        if not args.dry_run:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
    print(("Would change: " if args.dry_run else "Changed: ") + (", ".join(changed) or "nothing"))
    sys.exit(3 if needs_trim else 2 if changed else 0)


if __name__ == "__main__":
    main()
