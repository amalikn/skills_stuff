#!/usr/bin/env python3
"""Rebuild a pack's sources.json: keep curated evidence entries, merge new curated lists, catalogue every other cited URL, attach local copies.

Usage: just ledger [--add <curated.json>...] [--apply] (or: <venv python> scripts/sources_ledger.py <root> --store <dir> [--add f.json...] [--apply])
Plan by default: prints counts and writes nothing. --apply rewrites only <root>/sources.json (atomic replace).
Curated entries carry an evidence label (VERIFIED_PRIMARY, VERIFIED_SECONDARY, UNVERIFIED); generated ones are labelled CITED (link resolved and
cited, the claim it supports is labelled in the reference itself) and marked "generated": true so the next run refreshes them.
Shared helper: canonical in skill-network-architect, symlinked into skill-systems-architect.
Exit 0: plan printed or ledger written, 2: invalid input.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

from check_links import URL

INLINE = re.compile(r"\[([^\]\n]+)\]\((https?://[^)\s]+(?:\([^)\s]*\))?[^)\s]*)\)")
DEFINITION = re.compile(r"^ {0,3}\[([^\]\n]+)\]:\s*(https?://\S+)", re.MULTILINE)
RFC_NUMBER = re.compile(r"rfc-editor\.org/(?:rfc|info)/rfc(\d+)|datatracker\.ietf\.org/doc/(?:html/)?rfc(\d+)")


def cited_titles(root):
  """Map every external URL cited in the pack's Markdown to a title and the files citing it.

  Args:
    root: Skill directory.
  Returns:
    Dictionary of URL to {"title", "files"}.
  """
  found = {}
  for path in sorted(root.rglob("*.md")):
    relative = path.relative_to(root)
    if any(part.startswith(".") for part in relative.parts) or relative.parts[0] in ("sources", "docs"):
      continue
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    titles = {url.rstrip(".,;:"): label for label, url in INLINE.findall(text) + DEFINITION.findall(text)}
    for url in URL.findall(text):
      url = url.rstrip(".,;:")
      entry = found.setdefault(url, {"title": "", "files": set()})
      entry["files"].add(relative.as_posix())
      if not entry["title"] and titles.get(url):
        entry["title"] = re.sub(r"[`*]", "", titles[url]).strip()
  return {url: {"title": value["title"] or url.split("/")[2], "files": sorted(value["files"])} for url, value in found.items()}


def local_copy(url, index):
  """Find the store file for a URL, matching RFCs by number.

  Args:
    url: Cited URL.
    index: Parsed sources/index.json.
  Returns:
    Store-relative path, or None.
  """
  if url in index:
    return index[url]["path"]
  match = RFC_NUMBER.search(url)
  if match:
    key = f"https://www.rfc-editor.org/rfc/rfc{int(match.group(1) or match.group(2))}.txt"
    if key in index:
      return index[key]["path"]
  return None


def build(root, store, extra_files):
  """Merge curated entries, generate the rest and attach local copies.

  Args:
    root: Skill directory.
    store: Source store directory.
    extra_files: Paths to JSON lists of curated entries to merge.
  Returns:
    Pair of (new ledger dictionary, counts dictionary).
  Raises:
    ValueError: When a curated entry lacks id, url or evidence.
  """
  path = root / "sources.json"
  ledger = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"schema_version": 1, "sources": []}
  curated = [entry for entry in ledger.get("sources", []) if not entry.get("generated")]
  for extra in extra_files:
    for entry in json.loads(Path(extra).read_text(encoding="utf-8")):
      if not {"id", "url", "evidence"} <= set(entry):
        raise ValueError(f"{extra}: curated entries need id, url and evidence")
      curated.append(entry)
  by_url, ids = {}, set()
  for entry in curated:
    if entry["url"] in by_url:
      continue
    while entry["id"] in ids:
      entry["id"] += "-2"
    ids.add(entry["id"])
    by_url[entry["url"]] = entry
  index_path = store / "index.json"
  index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else {}
  cited = cited_titles(root)
  generated = []
  for url, info in sorted(cited.items()):
    if url in by_url:
      continue
    generated.append(
      {
        "id": "C-" + hashlib.sha256(url.encode()).hexdigest()[:8],
        "title": info["title"],
        "url": url,
        "evidence": "CITED",
        "note": "cited in " + ", ".join(info["files"]),
        "generated": True,
      }
    )
  for entry in [*by_url.values(), *generated]:
    copy = local_copy(entry["url"], index)
    entry.pop("local", None)
    if copy:
      entry["local"] = f"sources/{copy}"
      stored = next((value for key, value in index.items() if value["path"] == copy), None)
      if stored and entry.get("generated"):
        entry["checked"] = stored["retrieved"][:10]
  ledger["sources"] = [*by_url.values(), *generated]
  counts = {
    "curated": len(by_url),
    "generated": len(generated),
    "with_local_copy": sum(1 for entry in ledger["sources"] if "local" in entry),
    "cited_urls": len(cited),
  }
  return ledger, counts


def main():
  """Plan or write the rebuilt ledger.

  Args:
    None.
  Returns:
    Integer process exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("root", type=Path)
  parser.add_argument("--store", type=Path, required=True)
  parser.add_argument("--add", type=Path, nargs="*", default=[])
  parser.add_argument("--apply", action="store_true")
  args = parser.parse_args()
  started = time.perf_counter()
  root = args.root.resolve()
  try:
    ledger, counts = build(root, args.store.resolve(), args.add)
  except (OSError, ValueError, KeyError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  if args.apply:
    temporary = root / "sources.json.tmp"
    temporary.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, root / "sources.json")
  print(json.dumps({"status": "written" if args.apply else "plan", **counts, "elapsed_seconds": round(time.perf_counter() - started, 3)}, indent=2))
  return 0


if __name__ == "__main__":
  sys.exit(main())
