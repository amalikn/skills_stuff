#!/usr/bin/env python3
"""Keep a Markdown tracker (bug-tracker.md, features-to-add.md) as a file generated from a Pad collection: import it once, export it on every commit.

Why (operator, 2026-11-10): bugs, features and tech debt live in Pad from now on ("Pad, repo file exported"); the repo files stay readable and keep
their paths, headings and links. Each section's item list sits between generated markers; the header and section intros stay hand-written.

  import  parse the file's checkbox items (top level and nested, with their indented lines), create one Pad item each (children under their parent),
          then render the file from Pad and write it only if it matches the original apart from the markers.
  export  render each marked block from Pad; a block edited by hand since the last export (its text no longer matches the hash in its marker) is
          refused and shown, so the edit goes into Pad first.
  links   rewrite the relative repo links already in the collection's Pad bodies into opener links (guarded by each item's seq).

Links (operator, 2026-11-11): a relative link means nothing on a Pad page and Pad strips vscode://, so a link to an existing repo path goes into
Pad as a pad_link_opener.py link (http://127.0.0.1:<port>/open/<absolute path>?f=<fragment>, which opens VS Code), and the export turns it back
into the link relative to the tracker file. --no-opener writes bodies unchanged; the export always turns opener links back.

Usage (from the project folder, whose .pad.toml names the workspace):
    python3 pad_tracker.py import docs/trackers/bug-tracker.md --collection bugs --kind bugs            # plan
    python3 pad_tracker.py import docs/trackers/bug-tracker.md --collection bugs --kind bugs --apply    # create items, write markers
    python3 pad_tracker.py export docs/trackers/bug-tracker.md --collection bugs --kind bugs [--apply]
    python3 pad_tracker.py links docs/trackers/bug-tracker.md --collection bugs --kind bugs [--apply]
Kinds: bugs (open/fixed), features (submitted/shipped), techdebt (identified/resolved): the status a checkbox maps to on import.
Exit: 0 done or plan clean, 1 refused (hand edit in a generated block, or import round-trip mismatch), 2 bad arguments, 3 Pad unreachable.
Budget: one list call plus one create per item; about 0.3 s per item on import, under 2 s for an export.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

# The shared pad call (timeout, rate-limit retry) lives in pad_rewrite.py beside this file; loaded by path so the scripts need no package.
_spec = importlib.util.spec_from_file_location("pad_rewrite", Path(__file__).resolve().parent / "pad_rewrite.py")
_rewrite = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rewrite)
pad = _rewrite.pad
_ospec = importlib.util.spec_from_file_location("pad_link_opener", Path(__file__).resolve().parent / "pad_link_opener.py")
opener = importlib.util.module_from_spec(_ospec)
_ospec.loader.exec_module(opener)

KINDS = {"bugs": ("open", "fixed"), "features": ("submitted", "shipped"), "techdebt": ("identified", "resolved")}
CLOSED = {"fixed", "wont-fix", "shipped", "declined", "resolved"}
BOX = re.compile(r"^(?P<ind> *)- \[(?P<x>[ xX])\] (?P<text>.*)$")
HEAD = re.compile(r"^(#{1,6}) (.*)$")
MARK = re.compile(r'^<!-- pad:generated collection=(?P<c>\S+) section="(?P<s>[^"]*)" sha=(?P<h>[0-9a-f]{12}); edit in Pad, not here -->$')
END = "<!-- /pad:generated -->"
LINK = re.compile(r"(\[[^\]]*\]\()([^)\s]+)(\))")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def to_pad_links(text: str, base: Path, port: int) -> str:
  """Rewrite relative links to existing repo paths into opener links, for a Pad body.

  Args:
    text: Markdown (an item body).
    base: the folder the tracker file sits in, which relative links are relative to.
    port: the opener's port.

  Returns:
    The text with each `[x](rel/path#frag)` whose path exists turned into `[x](http://127.0.0.1:<port>/open/<abs>?f=frag)`; links with a scheme,
    anchors within the page and paths that do not exist are left as they are.
  """
  def one(m: re.Match) -> str:
    href = m.group(2)
    if SCHEME.match(href) or href.startswith("#"):
      return m.group(0)
    path, _, frag = href.partition("#")
    full = os.path.normpath(os.path.join(base, path))
    return m.group(1) + opener.link_for(full, frag, port) + m.group(3) if os.path.exists(full) else m.group(0)

  return LINK.sub(one, text)


def from_pad_links(text: str, base: Path) -> str:
  """Turn opener links (any port) back into links relative to the tracker file, for the repo export.

  Args:
    text: Markdown from Pad.
    base: the tracker file's folder.

  Returns:
    The text with each opener link replaced by `relative/path#frag`.
  """
  def one(m: re.Match) -> str:
    parts = urlsplit(m.group(2))
    if parts.scheme != "http" or parts.hostname != "127.0.0.1" or not parts.path.startswith(opener.PREFIX + "/"):
      return m.group(0)
    rel = os.path.relpath(unquote(parts.path[len(opener.PREFIX):]), base)
    frag = (parse_qs(parts.query).get("f") or [""])[0]
    return m.group(1) + rel + (f"#{frag}" if frag else "") + m.group(3)

  return LINK.sub(one, text)


@dataclass
class Item:
  """One checkbox item: its text lines (first line without the checkbox), whether ticked, its children, and where it sits."""
  first: str
  done: bool
  indent: int
  lines: list[str] = field(default_factory=list)
  children: list["Item"] = field(default_factory=list)
  section: str = ""
  order: int = 0


def parse_items(lines: list[str]) -> list[Item]:
  """Parse a run of item lines into a tree of items.

  Args:
    lines: consecutive lines of one item run (checkbox lines, indented lines, blank lines inside the run).

  Returns:
    The top-level items; a checkbox line indented under an item is its child, any other line belongs to the deepest open item above it.
  """
  roots: list[Item] = []
  stack: list[Item] = []
  for ln in lines:
    m = BOX.match(ln)
    if m:
      it = Item(first=m.group("text"), done=m.group("x") != " ", indent=len(m.group("ind")))
      while stack and stack[-1].indent >= it.indent:
        stack.pop()
      (stack[-1].children if stack else roots).append(it)
      stack.append(it)
    elif stack:
      stack[-1].lines.append(ln)
  return roots


def runs(text: str) -> list[tuple[str, int, int]]:
  """Find each section's item run in a tracker file.

  Args:
    text: the whole file.

  Returns:
    (section heading text, first line index, end line index exclusive) per run, in file order.
  """
  L = text.split("\n")
  out, section, i = [], "", 0
  while i < len(L):
    h = HEAD.match(L[i])
    if h:
      section = h.group(2).strip()
    if BOX.match(L[i]) and not L[i].startswith(" "):
      j = i + 1
      while j < len(L):
        if BOX.match(L[j]) or L[j].startswith(" "):
          j += 1
          continue
        if not L[j].strip():
          k = j
          while k < len(L) and not L[k].strip():
            k += 1
          if k < len(L) and (BOX.match(L[k]) or L[k].startswith(" ")) and not HEAD.match(L[k]):
            j = k
            continue
        break
      out.append((section, i, j))
      i = j
      continue
    i += 1
  return out


def render(items: list[Item]) -> str:
  """Render items back to Markdown, children after their parent's lines.

  Args:
    items: top-level items in order.

  Returns:
    The block text, no trailing newline.
  """
  out = []

  def walk(it: Item) -> None:
    out.append(" " * it.indent + f"- [{'x' if it.done else ' '}] " + it.first)
    out.extend(it.lines)
    for ch in it.children:
      walk(ch)

  for it in items:
    walk(it)
  return "\n".join(out)


def sha(text: str) -> str:
  """Short content hash stored in a marker.

  Args:
    text: block text.

  Returns:
    The first 12 hex digits of its sha256.
  """
  return hashlib.sha256(text.encode()).hexdigest()[:12]


def title_of(first: str) -> str:
  """A plain Pad title from an item's first line: markup removed, at most 100 characters.

  Args:
    first: the item's first line without the checkbox.

  Returns:
    The title.
  """
  t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", first).replace("**", "").replace("`", "")
  t = re.sub(r"\s+", " ", t).strip()
  return t if len(t) <= 100 else t[:97].rsplit(" ", 1)[0] + "..."


def to_body(it: Item) -> str:
  """The Pad body for an item: its first line and own lines verbatim, so the export can rebuild them exactly.

  Args:
    it: the item.

  Returns:
    Body text.
  """
  return "\n".join([it.first, *it.lines])


def from_pad(rows: list[dict]) -> dict[str, list[Item]]:
  """Rebuild item trees per section from a Pad collection listing.

  Args:
    rows: `pad item list <collection> --all --format json --full` rows.

  Returns:
    section -> top-level items in order (children attached, indents recomputed from depth).
  """
  by_ref, kids = {}, {}
  for r in rows:
    f = r.get("fields") or {}
    f = json.loads(f) if isinstance(f, str) else f
    body = (r.get("content") or r.get("title") or "").split("\n")
    it = Item(first=body[0], done=f.get("status") in CLOSED, indent=0, lines=body[1:], section=f.get("section") or "Added in Pad",
              order=int(f.get("order") or 10**6))
    by_ref[r["ref"]] = it
    kids.setdefault(r.get("parent_ref"), []).append((it.order, r["ref"]))
  for parent, lst in kids.items():
    if parent in by_ref:
      by_ref[parent].children = [by_ref[ref] for _, ref in sorted(lst)]
  top: dict[str, list[Item]] = {}
  for _, ref in sorted(kids.get(None, []) + [x for p, lst in kids.items() if p not in by_ref and p is not None for x in lst]):
    top.setdefault(by_ref[ref].section, []).append(by_ref[ref])

  def depth(it: Item, d: int) -> None:
    it.indent = d
    for ch in it.children:
      depth(ch, d + 2)

  for lst in top.values():
    for it in lst:
      depth(it, 0)
  return top


def export_text(text: str, collection: str, top: dict[str, list[Item]], force: bool = False) -> tuple[str, list[str]]:
  """Fill every marked block of the collection from Pad.

  Args:
    text: the current file.
    collection: the Pad collection slug in the markers.
    top: from from_pad().
    force: replace blocks even when edited by hand.

  Returns:
    (new file text, list of sections refused because their block was edited by hand).
  """
  L, out, refused, seen, i = text.split("\n"), [], [], set(), 0
  while i < len(L):
    m = MARK.match(L[i])
    if m and m.group("c") == collection:
      j = L.index(END, i + 1)
      current = "\n".join(L[i + 1:j])
      section = m.group("s")
      seen.add(section)
      if sha(current) != m.group("h") and not force:
        refused.append(section)
        out.extend(L[i:j + 1])
      else:
        block = render(top.get(section, []))
        out.append(f'<!-- pad:generated collection={collection} section="{section}" sha={sha(block)}; edit in Pad, not here -->')
        out.extend(block.split("\n") if block else [])
        out.append(END)
      i = j + 1
      continue
    out.append(L[i])
    i += 1
  for section, items in top.items():
    if section not in seen:
      block = render(items)
      out += ["", f"### {section}", "", f'<!-- pad:generated collection={collection} section="{section}" sha={sha(block)}; edit in Pad, not here -->',
              *block.split("\n"), END]
  return "\n".join(out), refused


def strip_markers(text: str) -> str:
  """The file without generated markers, for the import round-trip comparison.

  Args:
    text: file text.

  Returns:
    Text with marker lines removed.
  """
  return "\n".join(ln for ln in text.split("\n") if not MARK.match(ln) and ln != END)


def list_rows(collection: str, a) -> list[dict]:
  """Read a collection's items with bodies.

  Args:
    collection: slug.
    a: parsed arguments (pad binary and timeout).

  Returns:
    The rows.
  """
  raw = json.loads(pad(["item", "list", collection, "--all", "--format", "json", "--full"], a.timeout, a.pad) or "[]")
  return raw if isinstance(raw, list) else raw.get("items", [])


def cmd_import(a) -> int:
  """Create Pad items from the file, then write the marked file if the round trip matches.

  Args:
    a: parsed arguments.

  Returns:
    Exit code.
  """
  text = Path(a.file).read_text(encoding="utf-8")
  found = runs(text)
  todo = []
  for section, s, e in found:
    for n, it in enumerate(parse_items(text.split("\n")[s:e]), 1):
      it.section, it.order = section, n * 10
      todo.append(it)
  count = sum(1 for _ in _walk(todo))
  print(f"{a.file}: {len(found)} section run(s), {len(todo)} top-level item(s), {count} item(s) with children")
  if not a.apply:
    print("plan only; --apply creates the items and writes the markers")
    return 0
  open_s, closed_s = KINDS[a.kind]
  created = 0

  def create(it: Item, parent: str | None, order: int) -> None:
    nonlocal created
    key = "tracker-" + hashlib.sha256(f"{a.collection}|{it.section}|{parent}|{order}|{it.first}".encode()).hexdigest()[:20]
    fields = {"section": it.section, "order": order}
    if a.kind == "bugs":
      m = re.match(r"^\*\*(\S+)", it.first)
      if m:
        fields["tracker_id"] = m.group(1)
    argv = ["item", "create", a.collection, title_of(it.first), "--stdin", "--status", closed_s if it.done else open_s,
            "--fields-json", json.dumps(fields), "--op-key", key, "--format", "json"] + (["--parent", parent] if parent else [])
    body = to_body(it) if a.no_opener else to_pad_links(to_body(it), base_of(a.file), a.opener_port)
    ref = json.loads(pad(argv, a.timeout, a.pad, body))["ref"]
    created += 1
    for n, ch in enumerate(it.children, 1):
      ch.section = it.section
      create(ch, ref, n * 10)

  for it in todo:
    create(it, None, it.order)
  print(f"created or found {created} item(s)")
  return cmd_export(a, initial=found)


def base_of(file: str) -> Path:
  """The folder relative links in a tracker file are relative to.

  Args:
    file: the tracker file path as given.

  Returns:
    Its absolute folder (symlinks kept, so links stay as written).
  """
  return Path(os.path.dirname(os.path.abspath(file)))


def cmd_links(a) -> int:
  """Rewrite relative repo links in the collection's Pad bodies into opener links: plan by default, --apply writes.

  Args:
    a: parsed arguments.

  Returns:
    Exit code: 0 done or planned, 1 a write failed (later ones are not attempted).
  """
  base = base_of(a.file)
  todo = []
  for r in list_rows(a.collection, a):
    old = r.get("content") or ""
    new = to_pad_links(old, base, a.opener_port)
    if new != old:
      changed = sum(1 for x, y in zip(LINK.findall(old), LINK.findall(new)) if x != y)
      todo.append((r["ref"], r["seq"], new, changed))
  for ref, seq, _, n in todo:
    print(f"{ref}: {n} link(s) to rewrite (seq {seq})")
  print(f"{len(todo)} item(s) to update")
  if not a.apply or not todo:
    if todo:
      print("plan only; --apply writes")
    return 0
  for ref, seq, body, _ in todo:
    try:
      pad(["item", "update", ref, "--stdin", "--expected-seq", str(seq)], a.timeout, a.pad, body)
    except RuntimeError as exc:
      print(f"{ref}: write failed, stopping: {exc}", file=sys.stderr)
      return 1
    print(f"{ref}: updated")
  return 0


def _walk(items: list[Item]):
  """Yield every item in a forest, parents first.

  Args:
    items: top-level items.

  Returns:
    A generator of items.
  """
  for it in items:
    yield it
    yield from _walk(it.children)


def cmd_export(a, initial: list | None = None) -> int:
  """Render the marked blocks from Pad (on import, first wrap each run in markers and check the round trip).

  Args:
    a: parsed arguments.
    initial: the import's section runs, to insert markers before the first export.

  Returns:
    Exit code.
  """
  path = Path(a.file)
  original = path.read_text(encoding="utf-8")
  text = original
  if initial is not None:
    L = text.split("\n")
    for section, s, e in reversed(initial):
      body = "\n".join(L[s:e])
      L[s:e] = [f'<!-- pad:generated collection={a.collection} section="{section}" sha={sha(body)}; edit in Pad, not here -->', *L[s:e], END]
    text = "\n".join(L)
  base = base_of(a.file)
  top = from_pad([dict(r, content=from_pad_links(r.get("content") or "", base)) for r in list_rows(a.collection, a)])
  new, refused = export_text(text, a.collection, top, a.force)
  if refused:
    print(f"refused: block(s) edited by hand since the last export: {', '.join(refused)}. Put the change into Pad, or rerun with --force", file=sys.stderr)
    return 1
  if initial is not None and strip_markers(new) != original:
    import difflib
    sys.stderr.writelines(difflib.unified_diff(original.splitlines(True), strip_markers(new).splitlines(True), "original", "from Pad", n=1))
    print("refused: the round trip from Pad does not match the original; the file was not changed", file=sys.stderr)
    return 1
  if new == original:
    print(f"{a.file}: up to date")
    return 0
  if not a.apply:
    print(f"{a.file}: would change (--apply writes)")
    return 0
  path.write_text(new, encoding="utf-8")
  print(f"{a.file}: written" + (" (round trip identical apart from the markers)" if initial is not None else ""))
  return 0


def main(argv: list[str] | None = None) -> int:
  """Parse arguments and run import or export.

  Args:
    argv: command-line arguments (None reads sys.argv).

  Returns:
    Exit code: 0 done, 1 refused, 2 bad arguments, 3 Pad unreachable.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("cmd", choices=["import", "export", "links"])
  ap.add_argument("file")
  ap.add_argument("--collection", required=True)
  ap.add_argument("--kind", choices=sorted(KINDS), required=True)
  ap.add_argument("--apply", action="store_true")
  ap.add_argument("--force", action="store_true", help="export: replace blocks edited by hand (their edit is lost unless already in Pad)")
  ap.add_argument("--pad", default="pad")
  ap.add_argument("--timeout", type=int, default=60)
  ap.add_argument("--opener-port", type=int, default=opener.PORT, help="pad_link_opener.py port for links written into Pad")
  ap.add_argument("--no-opener", action="store_true", help="import: write bodies with their relative links unchanged")
  a = ap.parse_args(argv)
  started = time.monotonic()
  try:
    rc = {"import": cmd_import, "export": cmd_export, "links": cmd_links}[a.cmd](a)
  except RuntimeError as exc:
    print(f"pad_tracker: {exc}", file=sys.stderr)
    return 3
  except (OSError, ValueError, KeyError) as exc:
    print(f"pad_tracker: {exc}", file=sys.stderr)
    return 2
  print(f"done in {time.monotonic() - started:.1f} s")
  return rc


if __name__ == "__main__":
  sys.exit(main())
