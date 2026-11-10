#!/usr/bin/env python3
"""Open repo files in VS Code from links in Pad: a localhost service that redirects /open/<absolute path>?f=L<n> to vscode://file/<path>:<n>.

Why (operator, 2026-11-11: "build vscode:// as an add-on to pad"): Pad's page view keeps only http(s), mailto, ftp and tel links
(web/src/lib/utils/markdown.ts:224 at v0.19.2) and strips vscode://, and a relative repo link means nothing on a Pad page. Pad allows an
http link, so items link here and this service sends the browser on to VS Code. Pad itself is not patched, so brew upgrades need nothing.
pad_tracker.py writes these links into Pad and turns them back into relative links in the repo file.

Usage:
    python3 pad_link_opener.py serve [--port 47800] [--root /Volumes/Data ...]   # launchd runs this (pad_link_opener.plist)
    python3 pad_link_opener.py url <path> [--line N] [--port 47800]               # print the Pad link for a file (read-only)
Environment: PAD_LINK_OPENER_PORT and PAD_LINK_OPENER_ROOTS (colon-separated) override the defaults below.
Safety: listens on 127.0.0.1 only; returns no file content; answers only for an existing path under an allowed root; writes nothing.
Exit: 0 stopped, 2 bad arguments or the port in use.
Budget: one stat per request, well under 5 ms.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

PORT = int(os.environ.get("PAD_LINK_OPENER_PORT", "47800"))
ROOTS = tuple(p for p in os.environ.get("PAD_LINK_OPENER_ROOTS", "/Volumes/Data").split(":") if p)
PREFIX = "/open"
LINE = re.compile(r"^L(\d+)")


def base_url(port: int = PORT) -> str:
  """The opener's base URL, as it appears in Pad.

  Args:
    port: the port the service listens on.

  Returns:
    `http://127.0.0.1:<port>/open`.
  """
  return f"http://127.0.0.1:{port}{PREFIX}"


def link_for(path: str, fragment: str = "", port: int = PORT) -> str:
  """The Pad link for an absolute path and an optional fragment (`L86`, `L86-L90`, a heading slug).

  Args:
    path: absolute file or folder path.
    fragment: the part after `#` in the repo link, without the `#`.
    port: the service port.

  Returns:
    The http link, path percent-encoded, fragment carried as `?f=` (a browser never sends `#...` to a server).
  """
  return base_url(port) + quote(path, safe="/") + (f"?f={quote(fragment, safe='')}" if fragment else "")


def target(request_path: str, roots: tuple[str, ...] = ROOTS) -> tuple[int, str]:
  """Decide the answer for one request: pure, so it is tested without a socket.

  Args:
    request_path: the request line's path and query, e.g. `/open/Volumes/Data/x/y.py?f=L86`.
    roots: folders a path must sit under (after resolving symlinks and `..`).

  Returns:
    (302, vscode URL) for an existing allowed path; (404, reason) otherwise.
  """
  parts = urlsplit(request_path)
  if not parts.path.startswith(PREFIX + "/"):
    return 404, "not an /open link"
  path = unquote(parts.path[len(PREFIX):])
  real = os.path.realpath(path)
  if not any(real == r or real.startswith(r.rstrip("/") + "/") for r in (os.path.realpath(x) for x in roots)):
    return 404, f"outside the allowed roots: {path}"
  if not os.path.exists(real):
    return 404, f"no such file: {path}"
  frag = (parse_qs(parts.query).get("f") or [""])[0]
  m = LINE.match(frag)
  return 302, "vscode://file" + quote(path, safe="/") + (f":{m.group(1)}" if m else "")


class Handler(BaseHTTPRequestHandler):
  """Answers GET /open/... with a redirect to VS Code, anything else with 404. `roots` is set by main() before serving."""

  roots: tuple[str, ...] = ROOTS

  def do_GET(self) -> None:
    """Send the redirect, or a short plain-text 404 (the method name is the one BaseHTTPRequestHandler dispatches to).

    Returns:
      None.
    """
    status, value = target(self.path, self.roots)
    if status == 302:
      self.send_response(302)
      self.send_header("Location", value)
      self.send_header("Content-Type", "text/html; charset=utf-8")
      self.end_headers()
      self.wfile.write(f'<a href="{value}">Open in VS Code</a>'.encode())
      return
    self.send_response(404)
    self.send_header("Content-Type", "text/plain; charset=utf-8")
    self.end_headers()
    self.wfile.write(value.encode())

  def log_message(self, fmt: str, *args) -> None:
    """One line per request on stderr (launchd sends it to the log file).

    Args:
      fmt: format string from the base class.
      args: its values.

    Returns:
      None.
    """
    sys.stderr.write(f"{self.log_date_time_string()} {fmt % args}\n")


def main(argv: list[str] | None = None) -> int:
  """Run the service or print a link.

  Args:
    argv: command-line arguments (None reads sys.argv).

  Returns:
    Exit code: 0 stopped, 2 bad arguments or the port in use.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  sub = ap.add_subparsers(dest="cmd", required=True)
  s = sub.add_parser("serve")
  s.add_argument("--port", type=int, default=PORT)
  s.add_argument("--root", action="append", help="allowed root (repeatable); default PAD_LINK_OPENER_ROOTS or /Volumes/Data")
  u = sub.add_parser("url")
  u.add_argument("path")
  u.add_argument("--line", type=int)
  u.add_argument("--port", type=int, default=PORT)
  a = ap.parse_args(argv)
  if a.cmd == "url":
    print(link_for(str(Path(a.path).absolute()), f"L{a.line}" if a.line else "", a.port))
    return 0
  roots = tuple(a.root) if a.root else ROOTS
  Handler.roots = roots
  try:
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
  except OSError as exc:
    print(f"pad_link_opener: cannot listen on 127.0.0.1:{a.port}: {exc}", file=sys.stderr)
    return 2
  print(f"pad_link_opener: {base_url(a.port)} for {', '.join(roots)}", file=sys.stderr)
  try:
    srv.serve_forever()
  except KeyboardInterrupt:
    pass
  return 0


if __name__ == "__main__":
  sys.exit(main())
