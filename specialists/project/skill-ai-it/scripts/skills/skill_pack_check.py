#!/usr/bin/env python3
"""Hold a skill pack to the shared contract: front matter, routing, references, evidence files, scripts, secrets. Stdlib only, read-only.

Why (operator, 2026-11-12): skill-nautobot, skill-vagrant, skill-coder and the two architect packs share one shape, and every new pack drifted from it until the operator caught it by hand.
This check states that shape once. A pack's `tests/test_package_contract.py` calls `check_pack`; run directly it prints one line per finding.

Levels: `error` fails the check; `warn` is reported and fails only with `--strict` (a pack not yet finished: an unfilled `TODO(build)`, a `planned` tool row, missing governance files).

Usage:
    python scripts/skills/skill_pack_check.py PACK_DIR [--strict]
Exit: 0 no error (and no warning with --strict), 1 findings, 2 bad arguments.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SKILL_LINES, SKILL_BYTES, DESC_MAX = 200, 25 * 1024, 300
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".toml", ".txt", ".py", ".json"}
SKIP_PARTS = {"__pycache__", ".git", ".venv", ".ruff_cache", ".archcore", "graphify-out", ".ai-context", "node_modules"}
SECRET_RXS = [re.compile(p) for p in (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"\bAKIA[0-9A-Z]{16}\b", r"\bghp_[A-Za-z0-9]{30,}\b", r"\bsk-[A-Za-z0-9]{32,}\b")]
ASSIGN_RX = re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*['\"]?([A-Za-z0-9/+_\-]{16,})")
PLACEHOLDER_RX = re.compile(r"\{\{[A-Z_]+\}\}")
LINK_RX = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
INLINE_CODE_RX = re.compile(r"`[^`\n]*`")
COMMENT_RX = re.compile(r"<!--.*?-->", re.S)
ANY_OF = (
  ("role", ("## role and non-goals", "## when to use", "## use when")),
  ("routing", ("## route the task", "## domain routing")),
  ("write-back", ("## standing write-back contract",)),
)
GOVERNANCE_FILES = ("AGENTS.md", "CLAUDE.md", "README.md", "CHANGELOG.md")


@dataclass(frozen=True)
class Finding:
  """One finding: its level, the file it concerns and the message."""

  level: str
  path: str
  message: str

  def __str__(self) -> str:
    """The one-line form printed by the command line."""
    return f"{self.level.upper():5} {self.path}: {self.message}"


def front_matter(text: str) -> dict[str, str]:
  """Read the top-level keys of a markdown file's front matter (folded and quoted values included).

  Args:
    text: the file text.

  Returns:
    Key to value; empty when there is no front matter.
  """
  if not text.startswith("---\n"):
    return {}
  end = text.find("\n---", 4)
  if end < 0:
    return {}
  out: dict[str, str] = {}
  key = None
  for line in text[4:end].splitlines():
    m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
    if m:
      key, val = m.group(1), m.group(2).strip()
      out[key] = "" if val in (">-", ">", "|", "|-") else val.strip("\"'")
    elif key and line.startswith((" ", "\t")):
      out[key] = (out[key] + " " + line.strip()).strip()
  return out


def _authored_text_files(pack: Path) -> list[Path]:
  """Text files the pack authors (verbatim captures are excluded from marker checks by the callers)."""
  files = []
  for path in sorted(pack.rglob("*")):
    if path.is_file() and path.suffix in TEXT_SUFFIXES and not (set(path.relative_to(pack).parts) & SKIP_PARTS):
      files.append(path)
  return files


def _visible(text: str) -> str:
  """Text without HTML comments and inline code spans, where markers and placeholders do not count."""
  return INLINE_CODE_RX.sub("", COMMENT_RX.sub("", text))


def check_skill_md(pack: Path) -> list[Finding]:
  """Checks of SKILL.md: front matter, headings, links, budget and `planned` rows.

  Args:
    pack: the pack folder.

  Returns:
    The findings.
  """
  path = pack / "SKILL.md"
  if not path.is_file():
    return [Finding("error", "SKILL.md", "missing")]
  text, out = path.read_text(encoding="utf-8"), []
  fm = front_matter(text)
  if fm.get("name") != pack.name:
    out.append(Finding("error", "SKILL.md", f"front matter name {fm.get('name')!r} must equal the folder name {pack.name!r}"))
  desc = fm.get("description", "")
  if not desc or len(desc) > DESC_MAX or "TODO" in desc:
    out.append(
      Finding(
        "error", "SKILL.md", f"description must be 1 to {DESC_MAX} characters and complete (now {len(desc)}); the full scope goes in '## Full description'"
      )
    )
  low = text.lower()
  for label, options in ANY_OF:
    if not any(opt in low for opt in options):
      out.append(Finding("error", "SKILL.md", f"missing section for {label}: one of {', '.join(options)}"))
  for target in sorted(set(LINK_RX.findall(text))):
    if not target.startswith(("http", "mailto:", "/")) and not (pack / target).exists():
      out.append(Finding("error", "SKILL.md", f"link target does not exist: {target}"))
  if text.count("\n") + 1 > SKILL_LINES or len(text.encode()) > SKILL_BYTES:
    out.append(Finding("warn", "SKILL.md", f"over its budget of {SKILL_LINES} lines / {SKILL_BYTES // 1024} KB; move detail into references/"))
  if re.search(r"^\|.*\|\s*planned\s*\|\s*$", text, re.M):
    out.append(Finding("warn", "SKILL.md", "a tool row is still marked planned"))
  return out


def check_references(pack: Path) -> list[Finding]:
  """Checks of references/: routed from SKILL.md, headed, and the write-back reference present.

  Args:
    pack: the pack folder.

  Returns:
    The findings.
  """
  refs, out = pack / "references", []
  skill = (pack / "SKILL.md").read_text(encoding="utf-8") if (pack / "SKILL.md").is_file() else ""
  if not (refs / "evolution-and-write-back.md").is_file():
    out.append(Finding("error", "references/evolution-and-write-back.md", "missing"))
  for path in sorted(refs.rglob("*.md")) if refs.is_dir() else []:
    rel = path.relative_to(pack).as_posix()
    if "screenshots" in path.parts or path.name == "readme.md":
      continue
    if rel not in skill:
      out.append(Finding("error", rel, "not linked from SKILL.md; route it in the table or delete it"))
    fm = front_matter(path.read_text(encoding="utf-8"))
    if not fm.get("Title") or not fm.get("Summary"):
      out.append(Finding("warn", rel, "front matter needs Title and Summary (governed file header)"))
  return out


def check_files_and_markers(pack: Path) -> list[Finding]:
  """Required files, unfilled markers, unreplaced placeholders and secrets.

  Args:
    pack: the pack folder.

  Returns:
    The findings.
  """
  out = []
  for rel in ("sources.yaml", "compatibility.yaml", "tests/scenarios.md"):
    if not (pack / rel).is_file():
      out.append(Finding("error", rel, "missing"))
  for rel in GOVERNANCE_FILES + ("tests/test_package_contract.py",):
    if not (pack / rel).is_file():
      out.append(Finding("warn", rel, "missing (skill-ai-it bootstrap creates the governance files)"))
  for path in _authored_text_files(pack):
    rel = path.relative_to(pack).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    seed_copy = "research-sources-" in rel
    visible = _visible(text)
    if not seed_copy and path.suffix != ".py" and ("TODO(build)" in visible or "TODO(seed)" in visible):
      out.append(Finding("warn", rel, "unfilled TODO(build) or TODO(seed) marker"))
    if not seed_copy and PLACEHOLDER_RX.search(visible):
      out.append(Finding("error", rel, "unreplaced template placeholder"))
    out += _secret_findings(rel, text)
  return out


def _secret_findings(rel: str, text: str) -> list[Finding]:
  """Secret-looking content in one file."""
  out = []
  if any(rx.search(text) for rx in SECRET_RXS):
    out.append(Finding("error", rel, "looks like a key or token"))
  for m in ASSIGN_RX.finditer(text):
    value = m.group(2)
    if not re.search(r"(?i)example|placeholder|xxxx|changeme|your|<|\{", value) and not value.isalpha():
      out.append(Finding("error", rel, f"looks like a credential assigned to {m.group(1)!r}"))
  return out


def check_scenarios(pack: Path) -> list[Finding]:
  """At least five scenarios in tests/scenarios.md.

  Args:
    pack: the pack folder.

  Returns:
    The findings.
  """
  path = pack / "tests" / "scenarios.md"
  if not path.is_file():
    return []
  rows = [ln for ln in path.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*S?\d+\s*\|", ln)]
  return (
    []
    if len(rows) >= 5
    else [
      Finding("warn", "tests/scenarios.md", f"{len(rows)} scenario(s); at least 5 needed (one that must not trigger the skill, one that must stop and ask)")
    ]
  )


def check_scripts(pack: Path) -> list[Finding]:
  """Each script has a header docstring, a catalogue row and a test.

  Args:
    pack: the pack folder.

  Returns:
    The findings.
  """
  scripts = pack / "scripts"
  if not scripts.is_dir():
    return []
  out, catalogue = [], (scripts / "README.md").read_text(encoding="utf-8") if (scripts / "README.md").is_file() else None
  tests = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in (pack / "tests").glob("test_*.py")) if (pack / "tests").is_dir() else ""
  for path in sorted(scripts.rglob("*.py")):
    if path.name == "check_governance.py" or set(path.parts) & SKIP_PARTS:
      continue
    rel = path.relative_to(pack).as_posix()
    try:
      doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8")))
    except SyntaxError:
      doc = None
    if not doc:
      out.append(Finding("error", rel, "no module docstring (purpose and run line)"))
    if catalogue is None or path.name not in catalogue:
      out.append(Finding("error", rel, "not catalogued in scripts/README.md"))
    if path.stem not in tests:
      out.append(Finding("error", rel, "no test mentions it in tests/test_*.py"))
  return out


def check_pack(pack: Path) -> list[Finding]:
  """All checks for one pack folder.

  Args:
    pack: the pack folder.

  Returns:
    Every finding, errors first.
  """
  findings = check_skill_md(pack) + check_references(pack) + check_files_and_markers(pack) + check_scenarios(pack) + check_scripts(pack)
  return sorted(findings, key=lambda f: (f.level != "error", f.path))


def main(argv: list[str]) -> int:
  """Print the findings for one pack and return the exit code.

  Args:
    argv: command-line arguments after the program name.

  Returns:
    Exit code: 0 clean, 1 findings that fail, 2 bad arguments.
  """
  parser = argparse.ArgumentParser(description="Check a skill pack against the shared contract.")
  parser.add_argument("pack")
  parser.add_argument("--strict", action="store_true", help="warnings fail too (a finished pack)")
  args = parser.parse_args(argv)
  pack = Path(args.pack).resolve()
  if not pack.is_dir():
    print(f"not a folder: {pack}", file=sys.stderr)
    return 2
  findings = check_pack(pack)
  for f in findings:
    print(f)
  errors = sum(1 for f in findings if f.level == "error")
  warns = len(findings) - errors
  print(f"{errors} error(s), {warns} warning(s) in {pack.name}")
  return 1 if errors or (args.strict and warns) else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
