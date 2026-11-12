#!/usr/bin/env python3
"""Read a skill seed (templates/skill-seed.md filled in) and report what is missing. Stdlib only, read-only.

Why (operator, 2026-11-12): a new skill is built from a written seed that holds what the engagement learned, so the build keeps the lessons instead of rediscovering them. This module
parses that seed into parameters, sections and tables, and lists every problem that stops a build: an unfilled `TODO(seed)`, a missing section, a thin table, an open blocking question.
`new_skill.py` imports it; run directly it is the `check-seed` step.

Usage:
    python scripts/skills/skill_seed.py SEED.md
Exit: 0 when the seed is complete, 1 when it has problems, 2 on bad arguments or an unreadable file.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

FAMILIES = ("specialists/project", "specialists/platform", "skills", "personal")
NAME_RX = re.compile(r"^skill-[a-z0-9]+(-[a-z0-9]+)*$")
CHANNEL_RX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COMMENT_RX = re.compile(r"<!--.*?-->", re.S)
INLINE_CODE_RX = re.compile(r"`[^`\n]*`")
RESERVED_REFERENCES = {"readme.md", "evolution-and-write-back.md"}
VAGUE_REFERENCES = {"misc.md", "notes.md", "other.md", "general.md", "stuff.md"}
REQUIRED_SECTIONS = (
  "Parameters",
  "Purpose and users",
  "Trigger phrases",
  "Non-goals and neighbours",
  "Source material",
  "What was learned",
  "Vocabulary",
  "Outputs and artifacts",
  "Task routing",
  "Scripts plan",
  "Templates and assets",
  "Standing rules",
  "Safety boundaries",
  "Evidence plan",
  "Acceptance scenarios",
  "Write-back",
  "Install and registry",
  "Open questions",
  "Build order and done",
)
MINIMUM_ROWS = {"What was learned": 1, "Task routing": 1, "Standing rules": 1, "Evidence plan": 1, "Acceptance scenarios": 5, "Non-goals and neighbours": 1}


@dataclass
class Seed:
  """A parsed seed: where it came from, its parameters and its sections (comments removed)."""

  path: Path
  params: dict[str, str] = field(default_factory=dict)
  sections: dict[str, str] = field(default_factory=dict)


def parse_seed(path: Path, fence: str = "seed-parameters") -> Seed:
  """Parse a seed file into parameters and sections.

  Args:
    path: the seed markdown file.
    fence: the info string of the parameter block (`seed-parameters`; an intake uses `intake-parameters`).

  Returns:
    The parsed Seed; HTML comments are removed so guidance text never counts as content.

  Raises:
    OSError: when the file cannot be read.
  """
  raw = path.read_text(encoding="utf-8")
  seed = Seed(path=path)
  match = re.search(rf"^```text {re.escape(fence)}\s*\n(.*?)^```", raw, re.S | re.M)
  if match:
    for line in match.group(1).splitlines():
      line = line.split("#", 1)[0].strip()
      if ":" in line:
        key, value = line.split(":", 1)
        seed.params[key.strip()] = value.strip()
  text = COMMENT_RX.sub("", raw)
  current = None
  for line in text.splitlines():
    if line.startswith("## "):
      current = line[3:].strip()
      seed.sections[current] = ""
    elif current is not None:
      seed.sections[current] += line + "\n"
  return seed


def table_rows(section: str) -> list[list[str]]:
  """The data rows of the first markdown table in a section.

  Args:
    section: the section body.

  Returns:
    One list of cell texts per row, header and separator excluded. A wrapped row, as the repo's table formatter writes it (a cell
    indented by three or more spaces, usually with an empty first cell), is merged cell by cell into the row above.
  """
  rows: list[list[str]] = []
  lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
  for line in lines[2:]:
    raw = re.split(r"(?<!\\)\|", line.strip("|"))
    cells = [c.strip() for c in raw]
    if not any(cells):
      continue
    if rows and any(c.startswith("   ") for c in raw):
      for i, cell in enumerate(cells):
        if cell and i < len(rows[-1]):
          rows[-1][i] = f"{rows[-1][i]} {cell}".strip()
      continue
    rows.append(cells)
  return rows


def table_header(section: str) -> list[str]:
  """The header cells of the first markdown table in a section.

  Args:
    section: the section body.

  Returns:
    The header cell texts, or an empty list when there is no table.
  """
  for line in section.splitlines():
    if line.strip().startswith("|"):
      return [c.strip() for c in line.strip().strip("|").split("|")]
  return []


def bullets(section: str) -> list[str]:
  """The list items of a section (`- ` or `1. `), without the marker.

  Args:
    section: the section body.

  Returns:
    The item texts in order.
  """
  return [m.group(1).strip() for m in re.finditer(r"^\s*(?:[-*]|\d+\.)\s+(.*\S)\s*$", section, re.M)]


def prose(section: str) -> str:
  """The paragraphs of a section outside its tables and lists, joined with blank lines.

  Args:
    section: the section body.

  Returns:
    The prose text.
  """
  kept = [ln for ln in section.splitlines() if not ln.strip().startswith(("|", "- ", "* ", "```"))]
  return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()


def _markers(seed: Seed) -> list[str]:
  """Problems for each `TODO(seed)` left in the content (inline code spans are ignored)."""
  found = []
  for title, body in seed.sections.items():
    cleaned = INLINE_CODE_RX.sub("", body)
    if "TODO(seed)" in cleaned:
      count = cleaned.count("TODO(seed)")
      found.append(f"section '{title}': {count} unfilled TODO(seed); fill it or delete the row")
  for key, value in seed.params.items():
    if "TODO(seed)" in value:
      found.append(f"parameter '{key}' is unfilled")
  return found


def _params_problems(params: dict[str, str]) -> list[str]:
  """Problems with the Parameters block."""
  out = []
  name = params.get("name", "")
  if not NAME_RX.match(name):
    out.append(f"parameter 'name' must look like skill-topic (lowercase, hyphens): {name!r}")
  if params.get("family") not in FAMILIES:
    out.append(f"parameter 'family' must be one of {', '.join(FAMILIES)}")
  desc = params.get("short_description", "")
  if not desc or len(desc) > 250:
    out.append(f"parameter 'short_description' must be 1 to 250 characters (now {len(desc)})")
  if not CHANNEL_RX.match(params.get("memory_channel", "")):
    out.append("parameter 'memory_channel' must be lowercase words joined by hyphens")
  for key in ("scripts", "operator_context"):
    if params.get(key) not in ("yes", "no"):
      out.append(f"parameter '{key}' must be yes or no")
  return out


def _routing_problems(rows: list[list[str]]) -> list[str]:
  """Problems with the Task routing rows: reference names, duplicates and vague names."""
  out, seen = [], set()
  for row in rows:
    ref = row[1] if len(row) > 1 else ""
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$", ref):
      out.append(f"Task routing: reference file {ref!r} must be topic-name.md")
    elif ref in RESERVED_REFERENCES or ref in VAGUE_REFERENCES:
      out.append(f"Task routing: reference file {ref!r} is reserved or too vague; name the topic")
    elif ref in seen:
      out.append(f"Task routing: reference file {ref!r} appears twice")
    seen.add(ref)
  return out


def seed_problems(seed: Seed) -> list[str]:
  """Every problem that stops a build from this seed.

  Args:
    seed: the parsed seed.

  Returns:
    Human-readable problem lines; empty when the seed is complete.
  """
  out = _params_problems(seed.params)
  for title in REQUIRED_SECTIONS:
    if title not in seed.sections:
      out.append(f"missing section '{title}'")
  out += _markers(seed)
  for title, minimum in MINIMUM_ROWS.items():
    have = len(table_rows(seed.sections.get(title, "")))
    if title in seed.sections and have < minimum:
      out.append(f"section '{title}': {have} row(s), at least {minimum} needed")
  if len(bullets(seed.sections.get("Trigger phrases", ""))) < 3:
    out.append("section 'Trigger phrases': at least 3 phrases needed")
  if len(prose(seed.sections.get("Purpose and users", ""))) < 80:
    out.append("section 'Purpose and users': a paragraph of at least 80 characters is needed")
  out += _routing_problems(table_rows(seed.sections.get("Task routing", "")))
  scripts = seed.sections.get("Scripts plan", "")
  if seed.params.get("scripts") == "yes" and not table_rows(scripts) and "none" not in scripts.lower():
    out.append("section 'Scripts plan': list the scripts or write 'none' (and set parameter scripts: no)")
  for row in table_rows(seed.sections.get("Open questions", "")):
    if len(row) > 1 and row[1].lower() == "blocking":
      out.append(f"blocking open question: {row[0]}")
  return out


def main(argv: list[str]) -> int:
  """Print the problems of one seed file.

  Args:
    argv: command-line arguments after the program name: the seed path.

  Returns:
    Exit code: 0 complete, 1 problems, 2 bad arguments.
  """
  if len(argv) != 1:
    print(__doc__, file=sys.stderr)
    return 2
  try:
    seed = parse_seed(Path(argv[0]))
  except OSError as exc:
    print(f"cannot read seed: {exc}", file=sys.stderr)
    return 2
  problems = seed_problems(seed)
  for line in problems:
    print(f"PROBLEM {line}")
  print(f"{len(problems)} problem(s) in {seed.path}" if problems else f"seed complete: {seed.path}")
  return 1 if problems else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
