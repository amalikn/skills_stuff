#!/usr/bin/env python3
"""Resolve every external URL in a skill pack's Markdown and report the ones that fail, cannot be judged, or redirect elsewhere.

Usage: just links (or: <venv python> scripts/check_links.py <skill-root> [--workers 8] [--timeout 15])
Read-only, but it does use the network: one HEAD (GET on refusal) per unique URL, bounded parallelism, per-request timeout.
Shared helper: canonical in skill-network-architect, symlinked into skill-systems-architect. Not part of `just check`, which stays offline.
Exit 0: no URL failed (unknowns allowed), 1: a URL failed, 2: unreadable root.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

URL = re.compile(r"https?://(?:[^\s()<>\]\"'`]|\([^\s()<>]*\))+")  # allows balanced parentheses, e.g. Wikipedia titles
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
MAX_URLS = 2000
UNKNOWN_CODES = (401, 403, 429)  # auth, bot wall, rate limit: the page may well exist


def collect(root):
  """Map each external URL to the Markdown files that cite it, skipping dot folders and fenced code.

  Args:
    root: Skill directory.
  Returns:
    Dictionary of URL to sorted list of relative file paths.
  """
  found = {}
  for path in sorted(root.rglob("*.md")):
    relative = path.relative_to(root)
    if any(part.startswith(".") for part in relative.parts):
      continue
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    for url in URL.findall(text):
      found.setdefault(url.rstrip(".,;:"), set()).add(relative.as_posix())
  return {url: sorted(files) for url, files in found.items()}


def probe(url, timeout):
  """Fetch one URL with HEAD, falling back to GET when HEAD is refused.

  Args:
    url: Absolute http(s) URL.
    timeout: Seconds per request.
  Returns:
    Dictionary with url, status (int or error text) and final URL.
  """
  last = None
  for method in ("HEAD", "GET"):
    request = urllib.request.Request(url, method=method, headers={"User-Agent": AGENT})
    try:
      with urllib.request.urlopen(request, timeout=timeout) as response:
        return {"url": url, "status": response.status, "final": response.geturl()}
    except urllib.error.HTTPError as error:
      last = {"url": url, "status": error.code, "final": url}
      # Some servers answer HEAD with 404 or 405 yet serve GET (seen: csrc.nist.gov, 2026-10-29), so only a GET error is final.
      if method == "GET":
        return last
    except (urllib.error.URLError, TimeoutError, OSError) as error:
      last = {"url": url, "status": f"error: {error}", "final": url}
  return last


def classify(result):
  """Sort one probe result into ok, unknown or failed.

  Args:
    result: Output of probe().
  Returns:
    One of "ok", "unknown" or "failed".
  """
  status = result["status"]
  if isinstance(status, int) and 200 <= status < 300:
    return "ok"
  if status in UNKNOWN_CODES or "CERTIFICATE_VERIFY_FAILED" in str(status):
    return "unknown"
  return "failed"


def main():
  """Collect, probe and report.

  Args:
    None.
  Returns:
    Integer process exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("root", type=Path)
  parser.add_argument("--workers", type=int, default=8)
  parser.add_argument("--timeout", type=float, default=15)
  args = parser.parse_args()
  started = time.perf_counter()
  root = args.root.resolve()
  if not root.is_dir():
    print(json.dumps({"status": "invalid", "error": f"not a directory: {root}"}))
    return 2
  cited = collect(root)
  if len(cited) > MAX_URLS:
    print(json.dumps({"status": "invalid", "error": f"{len(cited)} URLs exceeds {MAX_URLS}"}))
    return 2
  with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 16))) as pool:
    results = list(pool.map(lambda url: probe(url, args.timeout), sorted(cited)))
  groups = {"ok": [], "unknown": [], "failed": []}
  for result in results:
    groups[classify(result)].append(dict(result, cited_in=cited[result["url"]]))
  moved = [result for result in groups["ok"] if result["final"].rstrip("/") != result["url"].rstrip("/")]
  report = {
    "status": "fail" if groups["failed"] else "pass",
    "urls": len(results),
    "failed": groups["failed"],
    "unknown": groups["unknown"],
    "redirected": moved,
    "elapsed_seconds": round(time.perf_counter() - started, 2),
    "limits": "A 2xx answer proves the page exists, not that it still says what the reference claims. Unknowns (401/403/429, TLS chain) need all-scraper or a manual read.",
  }
  print(json.dumps(report, indent=2))
  return 1 if groups["failed"] else 0


if __name__ == "__main__":
  sys.exit(main())
