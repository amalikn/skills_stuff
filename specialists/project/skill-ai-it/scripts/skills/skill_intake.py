#!/usr/bin/env python3
"""The intake and research stage of new-skill: write the intake form, check it, turn its research topics into briefs, and pre-fill a seed from it. Stdlib only.

Why (operator, 2026-11-12): a seed written by hand misses the point; skill-ai-it should run the seeding itself. The agent interviews the operator in rounds using the intake form (searching the conversation and files
first, asking only what is left), then `research-briefs` writes one generic brief per research topic for research agents, and `new_skill.py seed --from-intake` pre-fills the seed's parameters. Briefs are
refused if they contain a forbidden term (a project, customer or people name), so outside searches never carry them. Plan by default; `--apply` writes; existing files are never overwritten.

Usage (through new_skill.py):
    python scripts/skills/new_skill.py intake skill-topic [--family F] [--apply]       # write the intake form and the seed folder
    python scripts/skills/new_skill.py research-briefs INTAKE.md [--apply]             # one research brief per topic, into research/briefs/
    python scripts/skills/new_skill.py seed skill-topic --from-intake INTAKE.md        # seed with the parameters filled from the intake
Exit: 0 planned or written, 1 refusal (incomplete intake, forbidden term), 2 bad arguments.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import re
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("skill_seed", Path(__file__).resolve().with_name("skill_seed.py"))
ss = importlib.util.module_from_spec(_spec)
sys.modules["skill_seed"] = ss
_spec.loader.exec_module(ss)

AI_IT = Path(__file__).resolve().parents[2]
TEMPLATES = AI_IT / "templates"
FENCE = "intake-parameters"
ROUNDS = ("Round 1: purpose and callers", "Round 2: boundaries and safety", "Round 3: knowledge to keep", "Round 4: quality and install")
SEED_PARAMS = ("name", "family", "short_description", "scripts", "operator_context", "memory_channel", "related", "forbidden_terms")
PLACEHOLDER_RX = re.compile(r"\{\{([A-Z_]+)\}\}")


def parse_intake(path: Path) -> ss.Seed:
  """Parse an intake file the way a seed is parsed, with the intake parameter fence.

  Args:
    path: the intake markdown file.

  Returns:
    The parsed Seed object (parameters and sections).

  Raises:
    OSError: when the file cannot be read.
  """
  return ss.parse_seed(path, fence=FENCE)


def bullet_blocks(section: str) -> list[str]:
  """List items of a section with their wrapped continuation lines joined.

  Args:
    section: the section body.

  Returns:
    One string per `- ` item.
  """
  items: list[str] = []
  for line in section.splitlines():
    if re.match(r"^\s*[-*]\s+", line):
      items.append(re.sub(r"^\s*[-*]\s+", "", line).strip())
    elif items and line.strip() and line.startswith(" ") and not line.strip().startswith("|"):
      items[-1] += " " + line.strip()
  return items


def answer(seed: ss.Seed, qid: str) -> str:
  """The answer text of one question (`- Q1.1 ... Answer: text`).

  Args:
    seed: the parsed intake.
    qid: the question id, for example Q1.1.

  Returns:
    The answer text, empty when the question or its answer is missing.
  """
  for title in ROUNDS:
    for item in bullet_blocks(seed.sections.get(title, "")):
      if item.startswith(qid + " ") and "Answer:" in item:
        return item.split("Answer:", 1)[1].strip()
  return ""


def research_topics(seed: ss.Seed) -> list[tuple[str, str, str]]:
  """The research topic rows as (area, questions, scope).

  Args:
    seed: the parsed intake.

  Returns:
    The rows of the Research topics table.
  """
  rows = ss.table_rows(seed.sections.get("Research topics", ""))
  return [(r[0], r[1] if len(r) > 1 else "", r[2] if len(r) > 2 else "") for r in rows]


def intake_problems(seed: ss.Seed) -> list[str]:
  """Everything still missing from an intake.

  Args:
    seed: the parsed intake.

  Returns:
    Problem lines; empty when the interview is complete.
  """
  out = []
  for title in ROUNDS + ("Material to harvest", "Neighbour skills to study", "Research topics"):
    body = ss.INLINE_CODE_RX.sub("", seed.sections.get(title, ""))
    if title not in seed.sections:
      out.append(f"missing section '{title}'")
    elif "TODO(intake)" in body:
      out.append(f"section '{title}': {body.count('TODO(intake)')} unanswered TODO(intake)")
  for key, value in seed.params.items():
    if "TODO(intake)" in value:
      out.append(f"parameter '{key}' is unfilled")
  if not ss.NAME_RX.match(seed.params.get("name", "")):
    out.append("parameter 'name' must look like skill-topic")
  if seed.params.get("family") not in ss.FAMILIES:
    out.append(f"parameter 'family' must be one of {', '.join(ss.FAMILIES)}")
  if not research_topics(seed):
    out.append("section 'Research topics': at least one topic is needed")
  return out


def forbidden_hits(text: str, terms: list[str]) -> list[str]:
  """Forbidden terms found in a text as whole words, case-insensitively ("Rob" does not match "robust").

  Args:
    text: the text to scan.
    terms: the forbidden words.

  Returns:
    The terms found.
  """
  return [t for t in terms if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", text, re.I)]


def slug(text: str) -> str:
  """A file-name slug of a topic name.

  Args:
    text: the topic name.

  Returns:
    Lowercase words joined by hyphens.
  """
  return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "topic"


def render_briefs(seed: ss.Seed, now: dt.datetime) -> dict[str, str]:
  """One research brief per research topic.

  Args:
    seed: the parsed intake.
    now: the clock reading for the brief's date.

  Returns:
    File name to brief text.

  Raises:
    ValueError: when the brief template uses a placeholder this module does not fill.
  """
  template = (TEMPLATES / "research-brief.md").read_text(encoding="utf-8")
  terms = [t.strip() for t in seed.params.get("forbidden_terms", "").split(",") if t.strip()]
  purpose = answer(seed, "Q1.1") or seed.params.get("short_description", "")
  briefs = {}
  for area, questions, scope in research_topics(seed):
    mapping = {
      "FORBIDDEN": ", ".join(terms) or "none listed",
      "PURPOSE": purpose,
      "AREA": area,
      "SCOPE": scope or "not limited",
      "QUESTIONS": "\n".join(f"- {q.strip()}" for q in re.split(r";|\n", questions) if q.strip()) or "- TODO",
      "DATE": now.strftime("%Y-%m-%d"),
    }
    unknown = sorted(set(PLACEHOLDER_RX.findall(template)) - set(mapping))
    if unknown:
      raise ValueError(f"research-brief template uses unknown placeholder(s): {', '.join(unknown)}")
    briefs[f"brief-{slug(area)}.md"] = PLACEHOLDER_RX.sub(lambda m, mp=mapping: mp[m.group(1)], template)
  return briefs


def ensure_seed_folder(folder: Path, name: str, now: dt.datetime) -> None:
  """Create a seed folder's research and parts folders with an index each (existing files are kept).

  Args:
    folder: the seed folder.
    name: the skill name.
    now: the clock reading for the index headers.

  Raises:
    OSError: when a write fails.
  """
  for sub, template in (("research", "research-readme.md"), ("parts", "parts-readme.md")):
    note = folder / sub / "readme.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    if not note.exists():
      body = (TEMPLATES / "seed-folder" / template).read_text(encoding="utf-8")
      note.write_text(body.replace("<skill-name>", name).replace("<YYYYMMDD_hhmm>", now.strftime("%Y%m%d_%H%M")), encoding="utf-8")


def apply_intake(seed_text: str, intake: ss.Seed) -> str:
  """Fill the seed's parameter block from the intake's answered parameters.

  Args:
    seed_text: the seed template text.
    intake: the parsed intake.

  Returns:
    The seed text with each answered parameter written into its `key: value` line.
  """
  for key in SEED_PARAMS:
    value = intake.params.get(key, "").strip()
    if value and "TODO(intake)" not in value:
      seed_text = re.sub(rf"^{key}:.*$", lambda _m, k=key, v=value: f"{k}: {v}", seed_text, count=1, flags=re.M)
  return seed_text


def cmd_intake(args, stamp: dt.datetime) -> int:
  """The `intake` subcommand: write the intake form and the seed folder's indexes.

  Args:
    args: parsed arguments (name, family, out, apply, skills_root).
    stamp: the clock reading.

  Returns:
    Exit code.
  """
  if not ss.NAME_RX.match(args.name):
    print(f"name must look like skill-topic: {args.name!r}", file=sys.stderr)
    return 2
  folder = Path(args.skills_root) / "pending_skills" / args.name
  out = Path(args.out) if args.out else folder / f"intake-{args.name}-{stamp.strftime('%Y%m%d_%H%M')}.md"
  if out.exists():
    print(f"refused: {out} already exists", file=sys.stderr)
    return 1
  text = (
    (TEMPLATES / "skill-intake.md").read_text(encoding="utf-8").replace("<skill-name>", args.name).replace("<YYYYMMDD_hhmm>", stamp.strftime("%Y%m%d_%H%M"))
  )
  text = re.sub(r"^name: TODO\(intake\)$", f"name: {args.name}", text, flags=re.M)
  text = re.sub(r"^family: .*$", f"family: {args.family}", text, count=1, flags=re.M)
  print(f"{'write' if args.apply else 'plan: would write'} {out}")
  if args.apply:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    ensure_seed_folder(out.parent, args.name, stamp)
    print("next: interview the operator round by round (references/new-skill.md, Stage 1), then `new_skill.py research-briefs`")
  return 0


def cmd_research_briefs(args, stamp: dt.datetime) -> int:
  """The `research-briefs` subcommand: plan or write one research brief per intake research topic.

  Args:
    args: parsed arguments (intake, apply).
    stamp: the clock reading.

  Returns:
    Exit code.
  """
  intake_path = Path(args.intake)
  seed = parse_intake(intake_path)
  problems = intake_problems(seed)
  if problems:
    print("\n".join(f"PROBLEM {p}" for p in problems))
    print(f"refused: the intake has {len(problems)} problem(s); finish the interview first", file=sys.stderr)
    return 1
  terms = [t.strip() for t in seed.params.get("forbidden_terms", "").split(",") if t.strip()]
  briefs = render_briefs(seed, stamp)
  listed = ", ".join(terms)  # the brief names the forbidden words once, to tell the research agent what to avoid; that line is not a leak
  leaks = [f"{name}: {t}" for name, text in briefs.items() for t in forbidden_hits(text.replace(listed, "") if listed else text, terms)]
  if leaks:
    print("\n".join(f"LEAK {x}" for x in leaks))
    print("refused: a forbidden term is in a research brief; make the topic generic", file=sys.stderr)
    return 1
  folder = intake_path.parent / "research" / "briefs"
  for name, text in briefs.items():
    target = folder / name
    state = "skip (exists)" if target.exists() else ("write" if args.apply else "plan: would write")
    print(f"{state} {target}")
    if args.apply and not target.exists():
      folder.mkdir(parents=True, exist_ok=True)
      target.write_text(text, encoding="utf-8")
  print("next: dispatch each brief to a research agent, save every report under research/ (research-<stamp>.md), then `new_skill.py seed --from-intake`")
  return 0
