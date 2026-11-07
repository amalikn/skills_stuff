"""Keep each language override small: report language files over budget, and split one into a folder of topic files.

Run: python3 scripts/language_split.py [--check] [--lang <name> --apply]   (just language-split ...)
Read-only by default: prints each languages/*.md (and languages/<lang>/*.md) with its lines and bytes against the budget (200 lines, 25 KB:
an agent loads a language file whole). --check exits 1 when any is over. --lang <name> --apply splits languages/<name>.md: the entry file keeps
its front matter, Contents, Authoritative sources, Tools, Core rule mapping and Size tweaks, plus an index of topic files; every other H2
section moves to languages/<name>/<section-slug>.md, and each `> **Learned` block goes to the topic file named in languages/<name>/topics.toml
(`[topics] <file-stem> = ["keyword", ...]`, first match wins; unmatched blocks to learned-other.md). The split writes only when the words of
the result equal the words of the original (index lines aside); otherwise it changes nothing. Operator rule 2026-11-07.
Exit: 0 ok or split; 1 over budget (--check) or the word check failed; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

REQUIRES_PYTHON = (3, 11)

LANGS = Path(__file__).resolve().parents[1] / "languages"
BUDGET_LINES, BUDGET_BYTES = 200, 25 * 1024
KEEP = ("contents", "authoritative sources", "tools", "core rule mapping", "size and limit tweaks")


def slug(title: str) -> str:
  """A file stem from a heading.

  Args:
    title: the heading text.

  Returns:
    Lower-case words joined by hyphens.
  """
  return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def over(path: Path) -> str:
  """Why a file is over budget, or "".

  Args:
    path: the markdown file.

  Returns:
    The reason, or "" within budget.
  """
  text = path.read_text(encoding="utf-8")
  n, b = text.count("\n"), len(text.encode())
  return f"{n} lines, {b // 1024} KB (budget {BUDGET_LINES} lines, {BUDGET_BYTES // 1024} KB)" if n > BUDGET_LINES or b > BUDGET_BYTES else ""


def sections(text: str) -> tuple[str, list[tuple[str, str]]]:
  """Split a file into its head (front matter and title) and its H2 sections.

  Args:
    text: the file.

  Returns:
    (head, [(title, body including the heading line)]).
  """
  parts = re.split(r"(?m)^(?=## )", text)
  return parts[0], [(p.splitlines()[0][3:].strip(), p) for p in parts[1:]]


def blocks(body: str) -> list[str]:
  """Split a section body into paragraphs, a `>` quote run counting as one block.

  Args:
    body: the section text without its heading.

  Returns:
    The blocks, each ending in a newline.
  """
  out, cur, quote = [], [], None
  for line in body.splitlines(keepends=True):
    is_q = line.startswith(">")
    if line.strip() == "" or (cur and quote is not None and is_q != quote):
      if cur:
        out.append("".join(cur))
      cur, quote = ([], None) if line.strip() == "" else ([line], is_q)
      continue
    cur.append(line)
    quote = is_q if quote is None else quote
  if cur:
    out.append("".join(cur))
  return out


def front(lang: str, stem: str) -> str:
  """The front matter of a topic file.

  Args:
    lang: the language stem.
    stem: the topic file stem.

  Returns:
    The fenced front matter block.
  """
  return (f"---\nTitle: {lang} override - {stem.replace('-', ' ')}\nCategory: reference\nStatus: current\nAuthority: local-supplement\n"
          f"Scope: one topic of languages/{lang}.md (split by scripts/language_split.py)\nLast reviewed: 2026-11-07\n"
          f"Summary: The {stem.replace('-', ' ')} part of the {lang} override; the entry file holds the tools and the core rule mapping.\n---\n\n")


def words(text: str) -> Counter:
  """The multiset of words, for the before-and-after check.

  Args:
    text: any text.

  Returns:
    A Counter of word tokens.
  """
  return Counter(re.findall(r"[A-Za-z0-9_]+", text))


def split(lang: str, apply: bool) -> int:
  """Split one language file into an entry file and a folder of topic files.

  Args:
    lang: the file stem under languages/.
    apply: write the result (after the word check).

  Returns:
    0 split or planned; 1 the word check failed; 2 no such file.
  """
  src = LANGS / f"{lang}.md"
  if not src.is_file():
    print(f"no {src}")
    return 2
  topics_file = LANGS / lang / "topics.toml"
  topics = tomllib.loads(topics_file.read_text(encoding="utf-8")).get("topics", {}) if topics_file.is_file() else {}
  original = src.read_text(encoding="utf-8")
  head, secs = sections(original)
  entry, files = [head], {}
  for title, body in secs:
    if title.lower() in KEEP:
      entry.append(body)
      continue
    heading, rest = body.split("\n", 1) if "\n" in body else (body, "")
    for blk in blocks(rest):
      if blk.startswith("> **Learned"):
        low = blk.lower()
        stem = next((t for t, kws in topics.items() if any(k.lower() in low for k in kws)), "learned-other")
      else:
        stem = slug(title)
      files.setdefault(stem, []).append(blk)
  index = ["## Topic files\n\n", f"The rest of this override lives in [{lang}/]({lang}/) (split 2026-11-07 by scripts/language_split.py: one topic per file).\n\n",
           "| File | Blocks |\n| --- | --- |\n"] + [f"| [{s}.md]({lang}/{s}.md) | {len(b)} |\n" for s, b in sorted(files.items())]
  kept = [t for t, _ in secs if t.lower() in KEEP and t.lower() != "contents"] + ["Topic files"]
  toc = "## Contents\n\n" + "".join(f"- [{t}](#{slug(t)})\n" for t in kept) + "\n"
  entry = [toc if e.startswith("## Contents") else e for e in entry]
  new_entry = "".join(entry).rstrip("\n") + "\n\n" + "".join(index)
  outs = {LANGS / lang / f"{s}.md": front(lang, s) + f"# {lang}: {s.replace('-', ' ')}\n\nPart of [{lang}.md](../{lang}.md).\n\n" + "\n".join(b)
          for s, b in files.items()}
  dropped = "".join(f"## {t}\n" for t, _ in secs if t.lower() not in KEEP) + "".join(b for t, b in secs if t.lower() == "contents")
  lost = words(original) - words(new_entry + "".join(outs.values())) - words(dropped)
  if lost:
    print(f"word check failed: {sum(lost.values())} words would be lost, e.g. {list(lost)[:5]}; nothing written")
    return 1
  for path, text in outs.items():
    print(f"{'write' if apply else 'plan: write'} {path.relative_to(LANGS.parent)} ({text.count(chr(10))} lines)")
  print(f"{'rewrite' if apply else 'plan: rewrite'} {src.relative_to(LANGS.parent)} ({new_entry.count(chr(10))} lines, was {original.count(chr(10))})")
  if apply:
    (LANGS / lang).mkdir(exist_ok=True)
    for path, text in outs.items():
      path.write_text(text, encoding="utf-8")
    src.write_text(new_entry, encoding="utf-8")
  return 0


def main() -> int:
  """Report, check or split.

  Returns:
    The exit code.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--check", action="store_true", help="exit 1 when any language file is over budget")
  ap.add_argument("--lang", help="the language file to split")
  ap.add_argument("--apply", action="store_true", help="with --lang: write the split")
  args = ap.parse_args()
  if args.lang:
    return split(args.lang, args.apply)
  bad = 0
  for path in sorted(LANGS.glob("*.md")) + sorted(LANGS.glob("*/*.md")):
    why = over(path)
    bad += bool(why)
    if why or not args.check:
      print(f"{'OVER' if why else 'ok  '} {path.relative_to(LANGS.parent)}{': ' + why + ' (split it: --lang <name> --apply)' if why else ''}")
  return 1 if bad and args.check else 0


if __name__ == "__main__":
  sys.exit(main())
