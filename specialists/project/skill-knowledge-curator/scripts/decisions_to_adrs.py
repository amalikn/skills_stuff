#!/usr/bin/env python3
"""Render Archcore ADRs from operator decisions in a curator ledger: the Decision section is the ledger's own words, never a paraphrase.

Input is a groups file naming each ADR and the decision ids it rests on; each id is followed through `previous_decision_id` links to its latest
refinement, consecutive amendments with the same reason are folded into one row, and the conflict ids are listed for context. Output is one
`<slug>.adr.md` per group with YAML front matter (quoted values, `status: proposed`, `Last reviewed`) that `archcore status` accepts.

Safety: plan by default (prints create, update, unchanged or skipped per file); writes only with `--apply`. An existing ADR whose status is no
longer `proposed` (the operator accepted or changed it) is skipped, never overwritten. A second `--apply` reports no change. Fails closed on an
unknown decision id or a missing page. Found in Continuum (2026-11-05): a hand-written first pass missed the later refinements (Temporal and
OpenFGA + OPA into the first slice, fence first); following the chains caught them.

Run: python scripts/decisions_to_adrs.py --project <p> --groups groups.json [--out-dir .archcore/adr] [--stamp YYYYMMDD_hhmm] [--apply]
(or `just decisions-to-adrs ...`). groups.json: [{"slug": "...", "title": "...", "decisions": ["dr-..."], "page": "docs/..."}]. Standard library only.
Exit 0 ok, 1 refused input, 2 missing ledger.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
  """Read one ledger file.

  Args:
    path: a JSONL file.

  Returns:
    Its records, in file order.
  """
  with path.open(encoding="utf-8") as handle:
    return [json.loads(line) for line in handle if line.strip()]


def chain(start: str, nxt: dict[str, str]) -> list[str]:
  """Follow refinement links from a decision to its latest refinement.

  Args:
    start: first decision id.
    nxt: decision id to the decision that names it as previous.

  Returns:
    The ids in order, start first.
  """
  out = [start]
  while out[-1] in nxt and nxt[out[-1]] not in out:
    out.append(nxt[out[-1]])
  return out


def decision_rows(ids: list[str], dec: dict[str, dict]) -> list[str]:
  """Table rows for the decisions, folding consecutive amendments that share a reason.

  Args:
    ids: decision ids in order.
    dec: decision records by id.

  Returns:
    Markdown table rows.
  """
  groups: list[list] = []
  for i in ids:
    r = dec[i]
    key = (r["action"], (r.get("answer_text") or "").strip(), (r.get("reason") or "").strip())
    if groups and r["action"] == "AMEND" and groups[-1][0] == key:
      groups[-1][1].append(i)
    else:
      groups.append([key, [i], str(r.get("decided_at", ""))[:10]])
  rows = []
  for (action, text, reason), gids, day in groups:
    shown = text or ("amendment" if action == "AMEND" else action)
    label = ", ".join(f"`{g}`" for g in gids)
    rows.append(f"| {label} | {day} | {action} | {shown.replace('|', '/')} | {reason.replace('|', '/')} |")
  return rows


def render(group: dict, dec: dict[str, dict], nxt: dict[str, str], stamp: str, depth: str, tag: str) -> str:
  """Render one ADR.

  Args:
    group: {slug, title, decisions, page}.
    dec: decision records by id.
    nxt: refinement links.
    stamp: YYYYMMDD_hhmm for Last reviewed.
    depth: relative prefix from the ADR folder to the project root.
    tag: front-matter tag.

  Returns:
    The Markdown document.
  """
  ids = [i for s in group["decisions"] for i in chain(s, nxt)]
  conflicts = sorted({dec[i]["conflict_id"] for i in ids if dec[i].get("conflict_id")})
  dates = sorted(str(dec[i].get("decided_at", ""))[:10].replace("-", "") for i in ids)
  title = group["title"]
  return "\n".join(
    [
      "---",
      f"title: {json.dumps(title)}",
      "type: adr",
      "status: proposed",
      f"Last reviewed: {stamp}",
      f"date: {dates[0] if dates else stamp[:8]}",
      "source: " + json.dumps(f".kc/decisions.jsonl ({', '.join(ids)}); {group['page']}"),
      f"tags: [{tag}]",
      "promoted_by: decisions_to_adrs.py (skill-knowledge-curator)",
      "---",
      "",
      f"# {title}",
      "",
      "## Context",
      "",
      f"The sources disagreed; both positions and the curator's question are on [the page]({depth}{group['page']}) and in the conflict register"
      f" ({', '.join(conflicts) or 'no conflict record'}). Only the operator resolves a conflict.",
      "",
      "## Decision",
      "",
      "Recorded operator decisions, verbatim from the curator ledger, oldest first; a later row refines the one before it.",
      "",
      "| Decision | Date | Action | Answer | Reason |",
      "| --- | --- | --- | --- | --- |",
      *decision_rows(ids, dec),
      "",
      "## Consequences",
      "",
      "- Claims superseded by these decisions stay in the ledger as SUPERSEDED with their successor; pages cite them as history.",
      "- `status: proposed` until the operator accepts this document; acceptance does not settle open conflicts named on the page.",
      "",
    ]
  )


def plan(project: Path, groups: list[dict], out_dir: Path, stamp: str, tag: str = "decision") -> tuple[list[tuple[str, Path, str]], list[str]]:
  """Work out what each ADR file would become.

  Args:
    project: project root.
    groups: ADR groups.
    out_dir: folder for the ADRs.
    stamp: YYYYMMDD_hhmm.
    tag: front-matter tag.

  Returns:
    (actions, errors): (verb, path, text) per group, and refusals.
  """
  kc = project / ".kc"
  dec = {r["decision_id"]: r for r in read_jsonl(kc / "decisions.jsonl")}
  nxt = {r["previous_decision_id"]: k for k, r in dec.items() if r.get("previous_decision_id")}
  depth = os.path.relpath(project.resolve(), out_dir.resolve()).replace(os.sep, "/") + "/"
  actions, errors = [], []
  for g in groups:
    missing = [i for i in g["decisions"] if i not in dec]
    if missing or not (project / g["page"]).is_file():
      errors.append(f"{g['slug']}: unknown decisions {missing}" if missing else f"{g['slug']}: missing page {g['page']}")
      continue
    path = out_dir / f"{g['slug']}.adr.md"
    text = render(g, dec, nxt, stamp, depth, tag)
    if not path.exists():
      actions.append(("create", path, text))
      continue
    old = path.read_text(encoding="utf-8")
    status = re.search(r"^status:\s*(\S+)", old, re.M)
    if not status or status[1] != "proposed":
      actions.append(("skipped (not proposed)", path, old))
    elif re.sub(r"^Last reviewed: .*$", "", old, flags=re.M) == re.sub(r"^Last reviewed: .*$", "", text, flags=re.M):
      actions.append(("unchanged", path, old))
    else:
      actions.append(("update", path, text))
  return actions, errors


def main(argv: list[str] | None = None) -> int:
  """Plan or apply the ADRs.

  Args:
    argv: arguments, default sys.argv[1:].

  Returns:
    0 ok, 1 refused input, 2 missing ledger.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--project", required=True, type=Path)
  ap.add_argument("--groups", required=True, type=Path)
  ap.add_argument("--out-dir", type=Path, help="default <project>/.archcore/adr")
  ap.add_argument("--stamp", default="00000000_0000", help="YYYYMMDD_hhmm from `date`")
  ap.add_argument("--tag", default="decision", help="front-matter tag, e.g. the project name")
  ap.add_argument("--apply", action="store_true", help="write; default prints the plan")
  a = ap.parse_args(argv)
  if not (a.project / ".kc" / "decisions.jsonl").is_file():
    print(f"no decisions ledger under {a.project / '.kc'}", file=sys.stderr)
    return 2
  out_dir = a.out_dir or a.project / ".archcore" / "adr"
  actions, errors = plan(a.project, json.loads(a.groups.read_text(encoding="utf-8")), out_dir, a.stamp, a.tag)
  for e in errors:
    print(f"refused: {e}", file=sys.stderr)
  if errors:
    return 1
  for verb, path, text in actions:
    print(f"{verb}: {path}")
    if a.apply and verb in ("create", "update"):
      out_dir.mkdir(parents=True, exist_ok=True)
      path.write_text(text, encoding="utf-8")
  if not a.apply:
    print("plan only; rerun with --apply to write")
  return 0


if __name__ == "__main__":
  sys.exit(main())
