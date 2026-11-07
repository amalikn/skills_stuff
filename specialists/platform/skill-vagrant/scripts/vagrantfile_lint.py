#!/usr/bin/env python3
"""Lint Vagrantfiles as text: exact box pins, a provider block and VM names, customize events, and no secrets. Read-only.

Why: a lab must rebuild the same VM next month and must never carry a credential into a repo; both are visible in the Vagrantfile before
`vagrant up`. Written for skill-vagrant (operator 2026-11-07) from the smc-resiliency lab Vagrantfile.

Usage:
  vagrantfile_lint.py <Vagrantfile> [<Vagrantfile> ...] [--provider parallels] [--json]

Rules (each finding is error or warn):
  box-unpinned     error  a `vm.box` with no `vm.box_version` near it
  box-range        warn   a `box_version` that is a range (>=, >, <, ~>, a comma list), not one exact version
  box-computed     warn   a box or version that is not a string literal (cannot be checked as text)
  provider-missing error  no `vm.provider "<provider>"` block
  vm-name-missing  warn   a multi-machine file whose provider blocks set no `name` (the VM gets <folder>_<timestamp>)
  customize-device warn   a `customize` that adds a device without the "post-import" event (runs on every boot)
  secret           error  a password, token, API key, private key block or AWS key written in the file

Safety: reads the named files only; evaluates no Ruby and runs no Vagrant. Exit: 0 no errors; 1 an error finding; 2 bad arguments or unreadable file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

#: Patterns that mark a secret written into a Vagrantfile. Values pulled from ENV or a file are not secrets in the file.
SECRET_PATTERNS: tuple[tuple[str, str], ...] = (
  (r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "private key block"),
  (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
  (r"(?i)\b(?:password|passwd|secret|token|api[_-]?key|access[_-]?key)\w*\s*[:=]>?\s*[\"'][^\"'\s]{4,}[\"']", "credential literal"),
  (r"(?i)--password\s+[\"']?[^\s\"'$]{4,}", "password on a command line"),
)
EXACT_VERSION = re.compile(r"=?\s*[0-9][0-9A-Za-z.+-]*")


@dataclass
class Finding:
  """One lint result."""

  path: str
  line: int
  rule: str
  severity: str
  message: str


def _code(line: str) -> str:
  """The line without a trailing Ruby comment (a `#` outside quotes).

  Args:
    line: one source line.

  Returns:
    The code part.
  """
  quote = ""
  for i, ch in enumerate(line):
    if quote:
      if ch == quote:
        quote = ""
    elif ch in "\"'":
      quote = ch
    elif ch == "#":
      return line[:i]
  return line


def _literal(expr: str) -> str | None:
  """The string inside a plain Ruby string literal, or None when the expression is not one.

  Args:
    expr: the right-hand side of an assignment.

  Returns:
    The literal's text, or None.
  """
  found = re.fullmatch(r"\s*([\"'])([^\"'#{}]*)\1\s*", expr)
  return found.group(2) if found else None


def lint_text(text: str, path: str = "Vagrantfile", provider: str = "parallels") -> list[Finding]:
  """Apply every rule to one Vagrantfile's text.

  Args:
    text: the file content.
    path: the name to report.
    provider: the provider block the lab requires.

  Returns:
    The findings, in line order.
  """
  out: list[Finding] = []
  raw = text.splitlines()
  code = [_code(line) for line in raw]

  for n, line in enumerate(raw, 1):
    for pattern, what in SECRET_PATTERNS:
      if re.search(pattern, line):
        out.append(Finding(path, n, "secret", "error", f"{what} written in the file; read it from ENV or a file outside the repo"))
        break

  for i, line in enumerate(code):
    box = re.search(r"\.vm\.box\s*=\s*(.+)$", line)
    if not box:
      continue
    name = _literal(box.group(1))
    if name is None:
      out.append(Finding(path, i + 1, "box-computed", "warn", "box name is not a string literal; check its pin by hand"))
    version_line = next((j for j in range(max(0, i - 5), min(len(code), i + 6)) if re.search(r"\.vm\.box_version\s*=", code[j])), None)
    if version_line is None:
      out.append(Finding(path, i + 1, "box-unpinned", "error", f"box {name or '?'} has no box_version: it follows the latest release"))
      continue
    value = _literal(re.search(r"\.vm\.box_version\s*=\s*(.+)$", code[version_line]).group(1))
    if value is None:
      out.append(Finding(path, version_line + 1, "box-computed", "warn", "box_version is not a string literal; check it by hand"))
    elif "," in value or not EXACT_VERSION.fullmatch(value.strip()):
      out.append(Finding(path, version_line + 1, "box-range", "warn", f"box_version {value!r} is a constraint, not one exact version"))

  blocks = [i for i, line in enumerate(code) if re.search(rf"\.provider\s*\(?\s*[\"':]{re.escape(provider)}[\"']?", line)]
  if not blocks:
    out.append(Finding(path, 1, "provider-missing", "error", f"no vm.provider {provider!r} block"))
  defines = [line for line in code if re.search(r"\.vm\.define\b", line)]
  if len(defines) > 1 and blocks and not any(re.search(r"\.name\s*=", line) for line in code):
    out.append(Finding(path, blocks[0] + 1, "vm-name-missing", "warn", "multi-machine file without provider `name`: VMs get <folder>_<timestamp> names"))

  for i, line in enumerate(code):
    if ".customize" in line and re.search(r"--device-add\b", line) and "post-import" not in line:
      out.append(Finding(path, i + 1, "customize-device", "warn", 'customize adds a device on every boot; use the "post-import" event'))

  return sorted(out, key=lambda f: (f.line, f.rule))


def main(argv: list[str] | None = None) -> int:
  """Command line.

  Args:
    argv: arguments (default sys.argv[1:]).

  Returns:
    0 no errors, 1 an error finding, 2 an unreadable file (argparse exits 2 on bad arguments).
  """
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("paths", nargs="+", help="Vagrantfiles to lint")
  ap.add_argument("--provider", default="parallels", help="provider block the lab requires (default parallels)")
  ap.add_argument("--json", action="store_true", help="print JSON")
  args = ap.parse_args(argv)
  findings: list[Finding] = []
  for p in args.paths:
    try:
      text = Path(p).read_text(encoding="utf-8")
    except OSError as exc:
      print(f"cannot read {p}: {exc}", file=sys.stderr)
      return 2
    findings += lint_text(text, p, args.provider)
  if args.json:
    print(json.dumps([asdict(f) for f in findings], indent=2))
  else:
    for f in findings:
      print(f"{f.path}:{f.line}: {f.severity} {f.rule}: {f.message}")
    print(f"{len(findings)} finding(s), {sum(f.severity == 'error' for f in findings)} error(s)")
  return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
  sys.exit(main())
