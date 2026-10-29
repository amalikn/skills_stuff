#!/usr/bin/env python3
"""Check local links, entrypoint identity, Markdown headers, JSON and Python syntax.

Usage: just check (or: <venv python> scripts/check_package.py .)
Offline/read-only. Skips dot folders. Accepts a symlink only when it resolves to a file one folder deep in a sibling skill
(the shared references). This is not a full YAML validator or an agent behavior test.
Exit 0: structural checks pass, 1: findings, 2: unreadable root.
"""

import argparse
import ast
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote

HEADER_FIELDS = {"Title", "Category", "Status", "Authority", "Scope", "Last reviewed", "Summary"}
DIAGRAM_WIDTH = 110
MERGED_DEFINITION = re.compile(r"\[[^\]\n]+\]:\s*https?://")
LEDGER_URL = re.compile(r"https?://(?:[^\s()<>\]\"'`]|\([^\s()<>]*\))+")
LINE_WIDTH = 200
BARE_RFC = re.compile(r"rfc-editor\.org/rfc/rfc\d+(?![\d.])")
CONTRACTION = re.compile(r"\b(?:\w+n't|it's|I'm|we're|you're|they're|that's|there's|let's|I'll|we'll|I'd|we'd)\b", re.IGNORECASE)
REQUIRED_FILES = (
  "SKILL.md",
  "AGENTS.md",
  "CLAUDE.md",
  "RUNBOOK.md",
  "CHANGELOG.md",
  "SCRATCHPAD.md",
  "README.md",
  "justfile",
  ".mise.toml",
  "scripts/README.md",
)


def check(root):
  """Inspect a skill tree without executing its scripts.

  Args:
    root: Skill directory to inspect.
  Returns:
    Findings and counts dictionary.
  Raises:
    OSError: When the root cannot be read.
  """
  root = root.resolve()
  findings = []
  # Dot folders hold local tool state (memory logs, note indexes), not pack content.
  paths = sorted(path for path in root.rglob("*") if path.is_file() and not any(part.startswith(".") for part in path.relative_to(root).parts))
  if not paths:
    raise OSError("empty or missing skill root")
  markdown, links, python_files = 0, 0, 0
  for path in paths:
    relative = path.relative_to(root).as_posix()
    # A shared reference is a symlink into the peer pack; it must land in a sibling skill folder.
    if path.is_symlink() and path.resolve().parent.parent.parent != root.parent:
      findings.append(f"symlink outside the sibling skills: {relative}")
      continue
    if path.suffix == ".md":
      markdown += 1
      body = path.read_text(encoding="utf-8")
      parts = body.split("---", 2)
      if len(parts) < 3 or not body.startswith("---\n"):
        findings.append(f"missing frontmatter: {relative}")
      else:
        header = parts[1]
        keys = set(re.findall(r"^([A-Za-z][A-Za-z -]*):", header, re.MULTILINE))
        if relative == "SKILL.md":
          name = re.search(r"^name: (.+)$", header, re.MULTILINE)
          if not name or name.group(1).strip() != root.name:
            findings.append("entrypoint name does not match directory")
          if not {"name", "description"} <= keys:
            findings.append("entrypoint missing discovery fields")
        elif not HEADER_FIELDS <= keys:
          findings.append(f"incomplete Markdown header: {relative}")
      for target in re.findall(r"\[[^\]\n]*\]\(([^)\s]+)\)", body):
        target = unquote(target.split("#", 1)[0])
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
          continue
        links += 1
        # Normalise without following symlinks: a link in a shared module is judged from the pack it is read in.
        destination = Path(os.path.normpath(path.parent / target))
        # A link may land in this pack or in a sibling skill folder (the peer architect pack); nowhere else.
        if not (destination.is_relative_to(root) or destination.is_relative_to(root.parent)) or not destination.exists():
          findings.append(f"broken or external local link: {relative}: {target}")
    elif path.suffix == ".json":
      try:
        json.loads(path.read_text(encoding="utf-8"))
      except (ValueError, UnicodeError) as error:
        findings.append(f"invalid JSON: {relative}: {error}")
    elif path.suffix == ".py":
      python_files += 1
      try:
        ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 10))
      except (SyntaxError, UnicodeError) as error:
        findings.append(f"invalid Python 3.10 syntax: {relative}: {error}")
  findings.extend(check_governance(root))
  findings.extend(check_prose(root))
  findings.extend(check_ledger(root))
  return {"findings": findings, "files": len(paths), "markdown": markdown, "local_links": links, "python_files": python_files}


def check_ledger(root):
  """Every external URL cited in SKILL.md, references and templates must have an entry in sources.json.

  Args:
    root: Resolved skill directory.
  Returns:
    A list of findings, one per uncatalogued URL.
  """
  ledger_path = root / "sources.json"
  if not ledger_path.is_file():
    return ["missing sources.json"]
  known = {entry.get("url") for entry in json.loads(ledger_path.read_text(encoding="utf-8")).get("sources", [])}
  findings = []
  for path in sorted([root / "SKILL.md", *(root / "references").glob("*.md"), *(root / "templates").glob("*.md"), *(root / "operator").rglob("*.md")]):
    if not path.is_file():
      continue
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    for url in sorted(set(LEDGER_URL.findall(text))):
      if url.rstrip(".,;:") not in known:
        findings.append(f"source not in sources.json (run just ledger --apply): {path.relative_to(root).as_posix()}: {url}")
  return findings


def check_prose(root):
  """Hold references and templates to the pack's writing rules: ASCII diagrams within 110 columns, lines within 200, RFC links to the text, no contractions.

  Args:
    root: Resolved skill directory.
  Returns:
    A list of findings, one per offending line or diagram.
  """
  findings = []
  for folder in ("references", "templates", "operator"):
    for path in sorted((root / folder).rglob("*.md")):
      relative = path.relative_to(root).as_posix()
      in_text, block, start = False, [], 0
      for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if line.startswith("```"):
          if not in_text and line.strip() == "```text":
            in_text, block, start = True, [], number
          elif in_text:
            in_text = False
            if any(ord(char) > 127 for row in block for char in row):
              findings.append(f"diagram not ASCII: {relative}:{start}")
            if max((len(row) for row in block), default=0) > DIAGRAM_WIDTH:
              findings.append(f"diagram wider than {DIAGRAM_WIDTH} columns: {relative}:{start}")
          continue
        if in_text:
          block.append(line)
          continue
        if len(line) > LINE_WIDTH:
          findings.append(f"line over {LINE_WIDTH} characters: {relative}:{number}")
        if len(MERGED_DEFINITION.findall(line)) > 1:
          findings.append(f"link definitions merged on one line (one per line): {relative}:{number}")
        if BARE_RFC.search(line):
          findings.append(f"bare RFC link (use the .html text): {relative}:{number}")
        if not line.startswith(">") and CONTRACTION.search(re.sub(r"`[^`]*`", "", line)):
          findings.append(f"contraction: {relative}:{number}")
  return findings


def check_governance(root):
  """Turn the pack's governance claims into findings: required files, routing and catalogue coverage, recipes named in prose, docstrings.

  Args:
    root: Resolved skill directory.
  Returns:
    A list of findings; empty when every claim holds.
  """
  findings = [f"missing required file: {name}" for name in REQUIRED_FILES if not (root / name).is_file()]
  runbook = (root / "RUNBOOK.md").read_text(encoding="utf-8") if (root / "RUNBOOK.md").is_file() else ""
  skill = (root / "SKILL.md").read_text(encoding="utf-8") if (root / "SKILL.md").is_file() else ""
  for reference in sorted((root / "references").glob("*.md")):
    if f"references/{reference.name}" not in skill:
      findings.append(f"reference not routed in SKILL.md: references/{reference.name}")
  for template in sorted((root / "templates").glob("*.md")):
    if f"templates/{template.name}" not in runbook:
      findings.append(f"template not catalogued in RUNBOOK.md: templates/{template.name}")
  catalogue = (root / "scripts" / "README.md").read_text(encoding="utf-8") if (root / "scripts" / "README.md").is_file() else ""
  for script in sorted((root / "scripts").glob("*.py")):
    if f"({script.name})" not in catalogue:
      findings.append(f"script not catalogued in scripts/README.md: {script.name}")
  justfile = (root / "justfile").read_text(encoding="utf-8") if (root / "justfile").is_file() else ""
  recipes = set(re.findall(r"^([a-z][a-z0-9_-]*)\b[^:\n]*:(?!=)", justfile, re.MULTILINE))
  for doc in ("SKILL.md", "RUNBOOK.md", "README.md", "AGENTS.md", "scripts/README.md"):
    text = (root / doc).read_text(encoding="utf-8") if (root / doc).is_file() else ""
    for recipe in sorted(set(re.findall(r"`just ([a-z][a-z0-9_-]*)", text)) - recipes):
      findings.append(f"{doc} names `just {recipe}`, which the justfile does not define")
  for script in sorted([*(root / "scripts").glob("*.py"), *(root / "tests").glob("*.py")]):
    tree = ast.parse(script.read_text(encoding="utf-8"))
    if not ast.get_docstring(tree):
      findings.append(f"module docstring missing: {script.relative_to(root).as_posix()}")
    for node in ast.walk(tree):
      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        doc = ast.get_docstring(node) or ""
        if "Args:" not in doc or "Returns:" not in doc:
          findings.append(f"docstring lacks Args/Returns: {script.relative_to(root).as_posix()}:{node.lineno} {node.name}")
  return findings


def main():
  """Run local structural inspection and emit JSON.

  Args:
    None.
  Returns:
    Integer exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("root", type=Path)
  args = parser.parse_args()
  started = time.perf_counter()
  try:
    result = check(args.root)
  except (OSError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  result["status"] = "fail" if result["findings"] else "pass"
  result["elapsed_seconds"] = round(time.perf_counter() - started, 6)
  print(json.dumps(result, indent=2))
  return 1 if result["findings"] else 0


if __name__ == "__main__":
  sys.exit(main())
