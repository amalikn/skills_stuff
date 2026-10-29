#!/usr/bin/env python3
"""Keep a local copy of every source the packs cite: RFC text, PDFs, and Markdown snapshots of web pages.

Usage: just fetch-sources [--apply] (or: <venv python> scripts/fetch_sources.py <root>... --store <dir> --scraper <all-scraper justfile> [--apply])
Plan by default: lists what it would fetch and writes nothing. --apply downloads into the store and updates <store>/index.json.
Resumable: a URL already in the index with its file present is skipped (--refresh fetches again).
RFCs come from rfc-editor.org as .txt; .pdf URLs are fetched directly; web pages go through all-scraper (--markdown), which climbs past bot walls.
Network: bounded workers, a timeout per request, each all-scraper run in its own process group and killed whole on timeout.
Exit 0: plan printed or every fetch succeeded, 1: some fetches failed, 2: invalid arguments.
"""

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from check_links import AGENT, collect

RFC_URL = re.compile(r"^https?://(?:www\.)?(?:rfc-editor\.org/(?:rfc|info)/rfc|datatracker\.ietf\.org/doc/(?:html/)?rfc)(\d+)(?:\.(?:html|txt|pdf))?/?$")
RFC_TEXT = re.compile(r"\bRFC[ -]?(\d{3,5})\b")
SKIP_HOSTS = ("github.com/", "img.shields.io")  # repositories and badges: cite, do not snapshot
MIN_BYTES = 800  # a smaller snapshot is a wall or an error page, not the document
MAX_BYTES = 60 * 1024 * 1024


def slug(url):
  """Turn a URL into a short, stable, filesystem-safe name.

  Args:
    url: Absolute URL.
  Returns:
    "<host>/<path-slug>-<8 hex>" without extension.
  """
  host = re.sub(r"^www\.", "", url.split("/")[2])
  path = re.sub(r"[^A-Za-z0-9._-]+", "-", "/".join(url.split("/")[3:])).strip("-.")[:80] or "index"
  return f"{host}/{path}-{hashlib.sha256(url.encode()).hexdigest()[:8]}"


def plan(roots):
  """List every fetchable item from the cited URLs and the RFC numbers named in the text.

  Args:
    roots: Skill directories to scan.
  Returns:
    Dictionary of key (URL) to item {kind, source, path, cited_in}.
  """
  items = {}
  for root in roots:
    for url, files in collect(root).items():
      cited = [f"{root.name}/{name}" for name in files]
      match = RFC_URL.match(url)
      if match:
        number = int(match.group(1))
        key = f"https://www.rfc-editor.org/rfc/rfc{number}.txt"
        items.setdefault(key, {"kind": "rfc", "source": key, "path": f"rfc/rfc{number}.txt", "cited_in": []})["cited_in"] += cited
      elif any(skip in url for skip in SKIP_HOSTS):
        continue
      elif url.lower().split("?")[0].endswith(".pdf"):
        items.setdefault(url, {"kind": "pdf", "source": url, "path": f"pdf/{slug(url)}.pdf", "cited_in": []})["cited_in"] += cited
      else:
        items.setdefault(url, {"kind": "web", "source": url, "path": f"web/{slug(url)}.md.txt", "cited_in": []})["cited_in"] += cited
    for path in sorted(root.rglob("*.md")):
      if any(part.startswith(".") for part in path.relative_to(root).parts):
        continue
      for number in set(RFC_TEXT.findall(path.read_text(encoding="utf-8"))):
        key = f"https://www.rfc-editor.org/rfc/rfc{int(number)}.txt"
        item = items.setdefault(key, {"kind": "rfc", "source": key, "path": f"rfc/rfc{int(number)}.txt", "cited_in": []})
        item["cited_in"].append(f"{root.name}/{path.relative_to(root).as_posix()}")
  for item in items.values():
    item["cited_in"] = sorted(set(item["cited_in"]))
  return items


def download(url, target, timeout):
  """Fetch a URL directly into a file.

  Args:
    url: Absolute URL.
    target: Destination file.
    timeout: Seconds for the request.
  Returns:
    Pair of (ok flag, detail text).
  """
  request = urllib.request.Request(url, headers={"User-Agent": AGENT})
  try:
    with urllib.request.urlopen(request, timeout=timeout) as response:
      body = response.read(MAX_BYTES + 1)
  except (urllib.error.URLError, TimeoutError, OSError) as error:
    return False, f"direct fetch failed: {error}"
  if len(body) > MAX_BYTES:
    return False, "larger than 60 MiB"
  target.write_bytes(body)
  return True, "direct"


def scrape(url, target, scraper, timeout, js=False):
  """Snapshot a web page as Markdown through all-scraper, killing the whole process group on timeout.

  Args:
    url: Absolute URL.
    target: Destination file.
    scraper: Path to all-scraper's justfile.
    timeout: Seconds for the whole escalation ladder.
    js: Require a strategy that renders JavaScript.
  Returns:
    Pair of (ok flag, detail text).
  """
  command = ["just", "-f", str(scraper), "fetch", url, "--markdown", "--out", str(target)] + (["--js"] if js else [])
  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
  try:
    _, error = process.communicate(timeout=timeout)
  except subprocess.TimeoutExpired:
    os.killpg(process.pid, signal.SIGKILL)
    process.communicate()
    return False, f"all-scraper timed out after {timeout:.0f} s"
  if process.returncode != 0:
    return False, f"all-scraper exit {process.returncode}: {error.strip()[-200:]}"
  return True, "all-scraper"


def fetch(item, store, scraper, timeout):
  """Fetch one planned item into the store and describe the result.

  Args:
    item: One value from plan().
    store: Store directory.
    scraper: Path to all-scraper's justfile.
    timeout: Seconds per fetch.
  Returns:
    Index entry dictionary (with ok flag and detail).
  """
  target = store / item["path"]
  target.parent.mkdir(parents=True, exist_ok=True)
  if item["kind"] == "web":
    ok, detail = scrape(item["source"], target, scraper, timeout * 4)
    # A short body is usually a page that renders client-side: retry once with a JS-capable strategy.
    if ok and (not target.is_file() or target.stat().st_size < MIN_BYTES):
      ok, detail = scrape(item["source"], target, scraper, timeout * 6, js=True)
      detail = f"{detail} --js"
  else:
    ok, detail = download(item["source"], target, timeout)
    if not ok and item["kind"] == "pdf":
      ok, detail = scrape(item["source"], target.with_suffix(".md.txt"), scraper, timeout * 4)
      target = target.with_suffix(".md.txt")
  if ok and (not target.is_file() or target.stat().st_size < MIN_BYTES):
    ok, detail = False, f"{detail}: body under {MIN_BYTES} bytes (wall or error page)"
  if not ok and target.is_file():
    target.unlink()
  entry = {"path": target.relative_to(store).as_posix(), "kind": item["kind"], "method": detail, "cited_in": item["cited_in"], "ok": ok}
  if ok:
    data = target.read_bytes()
    entry.update({"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "retrieved": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")})
  return entry


def main():
  """Plan, then fetch with --apply, and maintain the index.

  Args:
    None.
  Returns:
    Integer process exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("roots", type=Path, nargs="+")
  parser.add_argument("--store", type=Path, required=True)
  parser.add_argument("--scraper", type=Path, required=True)
  parser.add_argument("--apply", action="store_true")
  parser.add_argument("--refresh", action="store_true")
  parser.add_argument("--workers", type=int, default=4)
  parser.add_argument("--timeout", type=float, default=30)
  parser.add_argument("--limit", type=int, default=0, help="fetch at most N items per kind (canary); 0 = all")
  args = parser.parse_args()
  started = time.perf_counter()
  roots = [root.resolve() for root in args.roots]
  if not all(root.is_dir() for root in roots) or not args.scraper.is_file():
    print(json.dumps({"status": "invalid", "error": "every root must be a directory and --scraper an existing justfile"}))
    return 2
  store = args.store.resolve()
  index_path = store / "index.json"
  index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else {}
  items = plan(roots)
  todo = {url: item for url, item in items.items() if args.refresh or not (url in index and (store / index[url]["path"]).is_file())}
  if args.limit > 0:
    kept, seen = {}, {}
    for url, item in todo.items():
      seen[item["kind"]] = seen.get(item["kind"], 0) + 1
      if seen[item["kind"]] <= args.limit:
        kept[url] = item
    todo = kept
  counts = {kind: sum(1 for item in todo.values() if item["kind"] == kind) for kind in ("rfc", "pdf", "web")}
  if not args.apply:
    print(
      json.dumps(
        {"status": "plan", "cited": len(items), "already_stored": len(items) - len(todo), "to_fetch": counts, "note": "add --apply to download"}, indent=2
      )
    )
    return 0
  with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as pool:
    results = dict(zip(todo, pool.map(lambda item: fetch(item, store, args.scraper, args.timeout), todo.values()), strict=True))
  failed = {url: entry["method"] for url, entry in results.items() if not entry["ok"]}
  for url, entry in results.items():
    if entry.pop("ok"):
      index[url] = entry
  for url in index:
    if url in items:
      index[url]["cited_in"] = items[url]["cited_in"]
  store.mkdir(parents=True, exist_ok=True)
  temporary = index_path.with_suffix(".json.tmp")
  temporary.write_text(json.dumps(dict(sorted(index.items())), indent=1) + "\n", encoding="utf-8")
  os.replace(temporary, index_path)
  print(
    json.dumps(
      {
        "status": "fail" if failed else "pass",
        "fetched": len(results) - len(failed),
        "failed": failed,
        "stored": len(index),
        "elapsed_seconds": round(time.perf_counter() - started, 1),
      },
      indent=2,
    )
  )
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
