#!/usr/bin/env python3
"""The scaffold helpers of new-skill: render the pack's templates from a seed, plan the files, classify them and write them. Stdlib only.

Why (operator, 2026-11-12): `new_skill.py` is the command line; this module holds the logic it calls so each stays small. `render` fills template placeholders; `build_mapping` turns a complete seed into the
values; `plan_files` renders every file (a `parts/<reference>.md` beside the seed becomes that reference's body); `find_leaks` refuses a forbidden term; `classify` and `write_plan` write only what is new
(a different existing file gets a `.proposed` beside it). Used through `new_skill.py`; it has no command line of its own.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("skill_seed", Path(__file__).resolve().with_name("skill_seed.py"))
ss = importlib.util.module_from_spec(_spec)
sys.modules["skill_seed"] = ss
_spec.loader.exec_module(ss)

AI_IT = Path(__file__).resolve().parents[2]
TEMPLATES = AI_IT / "templates"
PACK_TEMPLATES = TEMPLATES / "skill-pack"
PLACEHOLDER_RX = re.compile(r"\{\{([A-Z_]+)\}\}")
#: template file -> path in the pack, for files whose name differs; `when` names the parameter that must be yes.
RENAMES = {
  ".mise.toml.tmpl": (".mise.toml", "scripts"),
  "ruff.toml.tmpl": ("ruff.toml", "scripts"),
  "requirements.txt.tmpl": ("requirements.txt", "scripts"),
  "gitignore.tmpl": (".gitignore", None),
  "operator-readme.md.tmpl": ("operator/readme.md", "operator_context"),
}


def render(text: str, mapping: dict[str, str]) -> str:
  """Fill `{{NAME}}` placeholders in a template.

  Args:
    text: the template text.
    mapping: placeholder name to value.

  Returns:
    The text with every placeholder replaced.

  Raises:
    ValueError: when the template uses a placeholder the mapping lacks.
  """
  unknown = sorted(set(PLACEHOLDER_RX.findall(text)) - set(mapping))
  if unknown:
    raise ValueError(f"template uses unknown placeholder(s): {', '.join(unknown)}")
  return PLACEHOLDER_RX.sub(lambda m: mapping[m.group(1)], text)


def md_table(header: list[str], rows: list[list[str]]) -> str:
  """A markdown table as text.

  Args:
    header: the header cells.
    rows: the data rows.

  Returns:
    The table lines joined with newlines.
  """
  out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
  out += ["| " + " | ".join(r) + " |" for r in rows]
  return "\n".join(out)


def _routing(seed: ss.Seed) -> list[tuple[str, str, str]]:
  """The routing rows as (task, reference file, contents)."""
  rows = ss.table_rows(seed.sections["Task routing"])
  return [(r[0], r[1], r[2] if len(r) > 2 else r[0]) for r in rows]


def _tools(seed: ss.Seed) -> str:
  """The 'The pack's tools' block: planned scripts from the seed, or a statement that there are none."""
  rows = ss.table_rows(seed.sections.get("Scripts plan", ""))
  if not rows:
    return "This pack ships no scripts."
  body = [[f"`{r[0]}`", r[1], "planned"] for r in rows]
  return (
    "Catalogue with inputs, outputs and safety: scripts/README.md. A `planned` row is built by the seed's build order and the word removed.\n\n"
    + md_table(["Script", "What it does", "Status"], body)
  )


def _claims(seed: ss.Seed, short: str) -> str:
  """sources.yaml claim rows from the seed's Evidence plan."""
  rows = ss.table_rows(seed.sections["Evidence plan"])
  out = []
  for i, r in enumerate(rows, 1):
    src = r[1] if len(r) > 1 else "TODO(build)"
    fals = r[2] if len(r) > 2 else "TODO(build)"
    out.append(
      "\n".join(
        [
          f"  - id: C-{short}{i:02d}",
          f"    statement: {json.dumps(r[0])}",
          "    kind: generic_invariant",
          "    evidence_status: UNVERIFIED",
          "    lifecycle: current",
          f"    evidence: {json.dumps(src)}",
          f"    falsifier: {json.dumps(fals)}",
          "    reference: TODO(build)",
        ]
      )
    )
  return "\n".join(out)


def build_mapping(seed: ss.Seed, pack: Path, root: Path, now: dt.datetime) -> dict[str, str]:
  """All placeholder values for the pack's templates, from the seed.

  Args:
    seed: the complete seed.
    pack: the pack folder to be created.
    root: the skills root.
    now: the clock reading used for dates and stamps.

  Returns:
    Placeholder name to text.
  """
  p, s = seed.params, seed.sections
  name = p["name"]
  routing = _routing(seed)
  related = [x.strip() for x in p.get("related", "").split(",") if x.strip()]
  non_goals = ss.table_rows(s["Non-goals and neighbours"])
  initials = "".join(w[0] for w in name.split("-")[1:])[:3].upper() or "X"
  return {
    "NAME": name,
    "TITLE": " ".join(w.capitalize() for w in name.split("-")[1:]),
    "DATE": now.strftime("%Y-%m-%d"),
    "STAMP": now.strftime("%Y%m%d_%H%M"),
    "SHORT_DESCRIPTION": p["short_description"],
    "PURPOSE": ss.prose(s["Purpose and users"]),
    "MEMORY_CHANNEL": p["memory_channel"],
    "NON_GOALS": "Not this skill's job, and who owns it (this pack links to the owner and does not copy its facts):\n\n"
    + md_table(["Not this skill's job", "Owner"], non_goals),
    "SAFETY": "\n".join(f"- {b}" for b in ss.bullets(s["Safety boundaries"])),
    "ROUTING_TABLE": md_table(["Task", "Read first"], [[t, f"[references/{f}](references/{f})"] for t, f, _ in routing]),
    "TOOLS": _tools(seed),
    "RULES": md_table(["Rule", "Reason", "Decided by"], ss.table_rows(s["Standing rules"])),
    "RELATED": "\n".join(f"- **{r}**: neighbour skill; TODO(build): one line on what it owns and when to hand over." for r in related) or "- None.",
    "REPO_AGENTS_REL": os.path.relpath(root / "AGENTS.md", pack),
    "AI_IT_REL": os.path.relpath(AI_IT, pack),
    "REFERENCE_INDEX": "\n".join(f"- [{f}]({f}) {t}" for t, f, _ in routing),
    "CLAIMS": _claims(seed, initials),
    "SCENARIO_ROWS": "\n".join(f"| S{i} | {r[0]} | {r[1] if len(r) > 1 else ''} | |" for i, r in enumerate(ss.table_rows(s["Acceptance scenarios"]), 1)),
  }


def plan_files(seed: ss.Seed, pack: Path, mapping: dict[str, str]) -> dict[str, str]:
  """The pack's files as relative path to rendered text.

  Args:
    seed: the complete seed.
    pack: the pack folder to be created.
    mapping: the placeholder values.

  Returns:
    Relative path to content, in a stable order.

  Raises:
    ValueError: when a template uses an unknown placeholder.
  """
  files: dict[str, str] = {}
  for tmpl in sorted(PACK_TEMPLATES.rglob("*.tmpl")):
    rel = tmpl.relative_to(PACK_TEMPLATES).as_posix()
    if rel in ("references/topic.md.tmpl", "references/part-frame.md.tmpl"):
      continue
    dest, when = RENAMES.get(rel, (rel[: -len(".tmpl")], None))
    if when and seed.params.get(when) != "yes":
      continue
    files[dest] = render(tmpl.read_text(encoding="utf-8"), mapping)
  topic = (PACK_TEMPLATES / "references" / "topic.md.tmpl").read_text(encoding="utf-8")
  for task, ref, outline in _routing(seed):
    local = dict(mapping, TOPIC=ref[:-3].replace("-", " ").capitalize(), TASK=task, OUTLINE=outline)
    part = seed.path.parent / "parts" / ref
    if part.is_file():
      frame = (PACK_TEMPLATES / "references" / "part-frame.md.tmpl").read_text(encoding="utf-8")
      files[f"references/{ref}"] = render(frame, local) + part.read_text(encoding="utf-8")
    else:
      files[f"references/{ref}"] = render(topic, local)
  return files


def orphan_parts(seed: ss.Seed) -> list[str]:
  """Part files beside the seed that no routing row names.

  Args:
    seed: the complete seed.

  Returns:
    The file names under `parts/` that are not a routed reference.
  """
  folder = seed.path.parent / "parts"
  routed = {ref for _, ref, _ in _routing(seed)}
  return sorted(p.name for p in folder.glob("*.md") if p.name not in routed and p.name != "readme.md") if folder.is_dir() else []


def find_leaks(files: dict[str, str], terms: list[str]) -> list[str]:
  """Forbidden terms (project, customer or people names) found in the generated files, as whole words ("Rob" does not match "robust").

  Args:
    files: relative path to rendered content.
    terms: words that must not appear in a shared pack, compared case-insensitively.

  Returns:
    One `path: term` line per file and term found.
  """
  out = []
  for rel, text in files.items():
    out += [f"{rel}: {t}" for t in terms if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", text, re.I)]
  return out


def classify(pack: Path, files: dict[str, str]) -> list[tuple[str, str]]:
  """What each planned file would do: create, skip (identical) or propose (a different file exists).

  Args:
    pack: the pack folder.
    files: relative path to content.

  Returns:
    (action, relative path) pairs.
  """
  out = []
  for rel, text in files.items():
    target = pack / rel
    if not target.exists():
      out.append(("create", rel))
    elif target.read_text(encoding="utf-8") == text:
      out.append(("skip", rel))
    else:
      out.append(("propose", rel))
  return out


def write_plan(pack: Path, files: dict[str, str], actions: list[tuple[str, str]]) -> None:
  """Write the planned files: new ones as they are, differing ones beside the original as `.proposed`.

  Args:
    pack: the pack folder.
    files: relative path to content.
    actions: the classified plan.

  Raises:
    OSError: when a write fails.
  """
  for action, rel in actions:
    if action == "skip":
      continue
    target = pack / (rel + ".proposed" if action == "propose" else rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(files[rel], encoding="utf-8")
