#!/usr/bin/env python3
"""Start a new skill pack: write a seed from the template, check a seed, and scaffold the pack from a finished seed. Stdlib only.

Why (operator, 2026-11-12): every new skill was built by hand from a sibling and drifted (shebang recipes, no contract test, no evidence file, lessons lost). A seed holds the design and what the
engagement learned; the scaffold turns a complete seed into the pack skeleton every skill-* pack shares (SKILL.md, references, sources.yaml, compatibility.yaml, tests, governance stubs), and
`skill_pack_check.py` then holds the result to one contract. Plan by default; `--apply` writes. A file that already exists is never overwritten: an identical one is skipped, a different one
gets a `.proposed` file beside it.

Usage:
    python scripts/skills/new_skill.py intake skill-topic [--family specialists/project] [--apply]   # the interview form and the seed folder
    python scripts/skills/new_skill.py research-briefs INTAKE.md [--apply]                          # one research brief per topic
    python scripts/skills/new_skill.py seed skill-topic [--family specialists/project] [--from-intake INTAKE.md] [--apply]   # write the seed template
    python scripts/skills/new_skill.py check-seed SEED.md                                           # list what is still missing
    python scripts/skills/new_skill.py scaffold SEED.md [--apply]                                   # plan, then write the pack skeleton
Options: --skills-root DIR (default: the skills_stuff folder this pack sits in), --out FILE (seed only).
Exit: 0 planned or written, 1 refusal (incomplete seed, existing seed), 2 bad arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import re
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("skill_seed", Path(__file__).resolve().with_name("skill_seed.py"))
ss = importlib.util.module_from_spec(_spec)
sys.modules["skill_seed"] = ss
_spec.loader.exec_module(ss)

_spec_i = importlib.util.spec_from_file_location("skill_intake", Path(__file__).resolve().with_name("skill_intake.py"))
si = importlib.util.module_from_spec(_spec_i)
sys.modules["skill_intake"] = si
_spec_i.loader.exec_module(si)

_spec_s = importlib.util.spec_from_file_location("skill_scaffold", Path(__file__).resolve().with_name("skill_scaffold.py"))
sc = importlib.util.module_from_spec(_spec_s)
sys.modules["skill_scaffold"] = sc
_spec_s.loader.exec_module(sc)

render = sc.render
AI_IT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = AI_IT.parents[2]
TEMPLATES = AI_IT / "templates"


def cmd_seed(args: argparse.Namespace) -> int:
  """The `seed` subcommand: write the seed template for a new skill.

  Args:
    args: parsed arguments (name, family, skills_root, out, apply).

  Returns:
    Exit code.
  """
  if not ss.NAME_RX.match(args.name):
    print(f"name must look like skill-topic: {args.name!r}", file=sys.stderr)
    return 2
  now = dt.datetime.now()
  out = Path(args.out) if args.out else Path(args.skills_root) / "pending_skills" / args.name / f"seed-{args.name}-{now.strftime('%Y%m%d_%H%M')}.md"
  text = (TEMPLATES / "skill-seed.md").read_text(encoding="utf-8").replace("<skill-name>", args.name).replace("<YYYYMMDD_hhmm>", now.strftime("%Y%m%d_%H%M"))
  text = re.sub(r"^name: TODO\(seed\)$", f"name: {args.name}", text, flags=re.M)
  text = re.sub(r"^family: .*$", f"family: {args.family}", text, count=1, flags=re.M)
  if args.from_intake:
    text = si.apply_intake(text, si.parse_intake(Path(args.from_intake)))
  if out.exists():
    print(f"refused: {out} already exists", file=sys.stderr)
    return 1
  print(f"{'write' if args.apply else 'plan: would write'} {out}")
  if args.apply:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    si.ensure_seed_folder(out.parent, args.name, now)
    print("next: fill every TODO(seed), then `new_skill.py check-seed` and `scaffold`")
  return 0


def cmd_scaffold(args: argparse.Namespace) -> int:
  """The `scaffold` subcommand: plan or write the pack skeleton from a complete seed.

  Args:
    args: parsed arguments (seed, skills_root, apply).

  Returns:
    Exit code.
  """
  seed = ss.parse_seed(Path(args.seed))
  problems = ss.seed_problems(seed)
  if problems:
    print("\n".join(f"PROBLEM {p}" for p in problems))
    print(f"refused: the seed has {len(problems)} problem(s); fix them first", file=sys.stderr)
    return 1
  root = Path(args.skills_root).resolve()
  pack = root / seed.params["family"] / seed.params["name"]
  files = sc.plan_files(seed, pack, sc.build_mapping(seed, pack, root, dt.datetime.now()))
  for name in sc.orphan_parts(seed):
    print(f"NOTE part not routed (not used): parts/{name}")
  terms = [t.strip() for t in seed.params.get("forbidden_terms", "").split(",") if t.strip()]
  leaks = sc.find_leaks(files, terms)
  if leaks:
    print("\n".join(f"LEAK {x}" for x in leaks))
    print(f"refused: {len(leaks)} forbidden term(s) would enter the shared pack; write that lesson generically in the seed", file=sys.stderr)
    return 1
  actions = sc.classify(pack, files)
  for action, rel in actions:
    print(f"{action:8} {pack / rel}")
  used = [r for _, r, _ in sc._routing(seed) if (seed.path.parent / "parts" / r).is_file()]
  print(f"{len(used)} reference(s) drafted from seed parts: {', '.join(used) or 'none'}")
  counts = {a: sum(1 for x, _ in actions if x == a) for a in ("create", "skip", "propose")}
  print(
    f"{'written' if args.apply else 'plan only'}: {counts['create']} create, {counts['skip']} skip, {counts['propose']} propose (.proposed beside the original)"
  )
  if args.apply:
    sc.write_plan(pack, files, actions)
    print(
      f"next: run skill-ai-it bootstrap on {pack}, then `just bootstrap`, `just check`, and fill the TODO(build) markers from the seed (see references/new-skill.md)"
    )
  else:
    print("add --apply to write")
  return 0


def build_parser() -> argparse.ArgumentParser:
  """The command-line parser.

  Returns:
    The configured parser with the three subcommands.
  """
  parser = argparse.ArgumentParser(description="Seed and scaffold a new skill pack.")
  parser.add_argument("--skills-root", default=str(DEFAULT_ROOT), help="the skills_stuff folder (default: the one this pack sits in)")
  sub = parser.add_subparsers(dest="cmd", required=True)
  seed = sub.add_parser("seed", help="write the seed template for a new skill")
  seed.add_argument("name")
  seed.add_argument("--family", default="specialists/project", choices=ss.FAMILIES)
  seed.add_argument("--out")
  seed.add_argument("--from-intake", help="an intake file whose answered parameters pre-fill the seed")
  seed.add_argument("--apply", action="store_true")
  intake = sub.add_parser("intake", help="write the intake form (the interview record) and the seed folder")
  intake.add_argument("name")
  intake.add_argument("--family", default="specialists/project", choices=ss.FAMILIES)
  intake.add_argument("--out")
  intake.add_argument("--apply", action="store_true")
  briefs = sub.add_parser("research-briefs", help="one generic research brief per intake research topic")
  briefs.add_argument("intake")
  briefs.add_argument("--apply", action="store_true")
  check = sub.add_parser("check-seed", help="list what a seed still lacks")
  check.add_argument("seed")
  scaffold = sub.add_parser("scaffold", help="plan or write the pack skeleton from a complete seed")
  scaffold.add_argument("seed")
  scaffold.add_argument("--apply", action="store_true")
  return parser


def main(argv: list[str]) -> int:
  """Run the chosen subcommand.

  Args:
    argv: command-line arguments after the program name.

  Returns:
    Exit code: 0 ok, 1 refusal, 2 bad arguments.
  """
  args = build_parser().parse_args(argv)
  try:
    if args.cmd == "seed":
      return cmd_seed(args)
    if args.cmd == "check-seed":
      return ss.main([args.seed])
    if args.cmd == "intake":
      return si.cmd_intake(args, dt.datetime.now())
    if args.cmd == "research-briefs":
      return si.cmd_research_briefs(args, dt.datetime.now())
    return cmd_scaffold(args)
  except (OSError, ValueError, KeyError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    return 2


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
