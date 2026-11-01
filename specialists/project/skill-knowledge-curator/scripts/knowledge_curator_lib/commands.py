"""Command implementations for scripts/knowledge_curator.py: one function per kc subcommand, keyed in COMMANDS.

Imported by the front end, not run. Each function takes the project root and the parsed arguments and returns a JSON-ready dict, or
raises a KcError subclass whose exit_code the front end returns. Safety: writes only through ledger.py, and only when args.apply
is set (promote --apply and archive-plan --apply included); dry runs take no lock.
"""

import json
from pathlib import Path

from . import (
  archive_plan,
  candidates,
  claims,
  decision_points,
  decisions,
  drift,
  intake,
  inventory,
  ledger,
  promote,
  query,
  recall,
  relations,
  render,
  report,
  settings,
  state,
  validate,
  worksheet,
  yaml_io,
)
from .command_support import Noop, now, reject
from .commands_review import cmd_aliases, cmd_amend, cmd_decide, cmd_group_review
from .errors import ConflictBlocker, InputError, ReviewNeeded, SourceChanged, ValidationFailed


def emit(data: dict) -> None:
  """Print a JSON result.

  Args:
    data: the result.
  """
  print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))


def cmd_init(root: Path, args) -> dict:
  """Write .kc/config.yaml and .kc/.gitignore.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.
  """
  if settings.kc_path(root, settings.CONFIG_FILE).exists():
    return {"changed": False, "detail": ".kc/config.yaml exists; edit it by hand"}
  cfg = {**settings.DEFAULT_CONFIG, "project_id": root.resolve().name}
  with ledger.write_lock(root) if args.apply else Noop():
    a = ledger.write_text(root, f"{settings.KC_DIR}/{settings.CONFIG_FILE}", yaml_io.dump(cfg), args.apply)
    ledger.write_text(root, f"{settings.KC_DIR}/.gitignore", "cache/\nlocks/\n", args.apply)
  return {"changed": a, "applied": args.apply, "config": cfg}


def cmd_inventory(root: Path, args) -> dict:
  """Fingerprint sources and parse sections.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.
  """
  st = state.load(root)
  res = inventory.build(st)
  snapshot = {"exclusions": res.exclusions, "duplicate_groups": res.duplicate_groups}
  with ledger.write_lock(root) if args.apply else Noop():
    ledger.append(root, "sources", res.source_records, args.apply)
    ledger.append(root, "sections", res.section_records, args.apply)
    ledger.write_text(root, f"{settings.KC_DIR}/reports/inventory.json", json.dumps(snapshot, indent=2, sort_keys=True) + "\n", args.apply)
  warnings = inventory.excluded_markdown(root, st.cfg, res.exclusions)
  return {"applied": args.apply, "counts": res.counts, "new_sections": len(res.section_records), "warnings": warnings, **snapshot}


def _ingest(root: Path, args, kind: str) -> dict:
  """Shared body of the claims and relate commands.

  Args:
    root: project root.
    args: parsed arguments.
    kind: "claims" or "relations".

  Returns:
    Result.
  """
  st = state.load(root)
  records = claims.load_input(Path(args.file))
  if kind == "claims":
    res = claims.ingest(st, records)
    plan = {"claims": res.claims, "dispositions": res.dispositions, "sections": res.sections}
  else:
    res = relations.ingest(st, records)
    plan = {"relations": res.relations, "conflicts": res.conflicts, "dispositions": res.dispositions}
  if res.errors:
    reject(res.errors, res.source_changed)
  with ledger.write_lock(root) if args.apply else Noop():
    if kind == "claims":
      ledger.append(root, "claims", res.claims + res.dispositions + res.sections, args.apply)
    else:
      ledger.append(root, "relations", res.relations, args.apply)
      ledger.append(root, "conflicts", res.conflicts, args.apply)
      ledger.append(root, "claims", res.dispositions, args.apply)
  out = {
    "applied": args.apply,
    "skipped": res.skipped,
    **{k: len(v) for k, v in plan.items()},
    "ids": sorted({r.get("claim_id") or r.get("relation_id") or r.get("section_id") for v in plan.values() for r in v}),
  }
  if kind == "claims":
    effect = worksheet.batch_effect(st, res)
    out |= {"warnings": res.warnings, "sections_closed": effect["sections_closed"]}
    if args.coverage:
      out["coverage"] = effect["coverage"]
  return out


def cmd_render(root: Path, args) -> dict:
  """Render knowledge pages.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.

  Raises:
    ValidationFailed: --check and the pages differ from a fresh rendering.
  """
  st = state.load(root)
  out = render.render(st)
  with ledger.write_lock(root) if args.apply else Noop():
    changed = sorted(p for p, t in {**out.files, **out.proposals}.items() if ledger.write_text(root, p, t, args.apply))
  if args.check and changed:
    raise ValidationFailed("knowledge pages differ from a fresh rendering: " + ", ".join(changed))
  return {"applied": args.apply, "changed": changed, "proposals": sorted(out.proposals), "pages": out.pages}


def cmd_promote(root: Path, args) -> dict:
  """Evaluate, apply or revoke a page promotion.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.

  Raises:
    ConflictBlocker: --apply while an open P0/P1 conflict blocks the page.
    ValidationFailed: --apply while another gate fails.
  """
  st = state.load(root)
  result = promote.evaluate(st, args.page, args.approve_digest)
  if not args.apply:
    return result
  if not args.reason:
    raise InputError("--reason is required with --apply")
  if args.revoke:
    rec = promote.promotion_record(st, result, args.actor or settings.actor(), args.reason, now(), status="revoked")
  else:
    if not result["ready"]:
      gate = result["gates"].get("no_open_p0_p1", {"pass": True})
      raise (ConflictBlocker if not gate["pass"] else ValidationFailed)(f"promotion refused: {json.dumps(result['gates'])}")
    rec = promote.promotion_record(st, result, args.actor or settings.actor(), args.reason, now())
  with ledger.write_lock(root):
    ledger.append(root, "decisions", [rec], True)
    fresh = render.render(state.load(root))
    page_text = fresh.proposals.pop(f"{settings.KC_DIR}/proposals/{args.page}", None) or fresh.files[args.page]
    for path, text in {**fresh.files, args.page: page_text}.items():
      ledger.write_text(root, path, text, True)
  return {**result, "applied": True, "promotion": rec}


def cmd_archive_plan(root: Path, args) -> dict:
  """Plan an archive batch (never moves files).

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.
  """
  res = archive_plan.plan(state.load(root))
  if args.apply and res["entries"]:
    with ledger.write_lock(root):
      ledger.write_text(root, f"{settings.KC_DIR}/archive-plans/{res['batch_id']}.json", json.dumps(res, indent=2, sort_keys=True) + "\n", True)
  return {**res, "applied": args.apply}


def cmd_review(root: Path, args) -> dict:
  """Write or print the review queue.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.

  Raises:
    ReviewNeeded: open conflicts exist (after printing the queue).
  """
  st = state.load(root)
  text = decisions.review_markdown(st)
  with ledger.write_lock(root) if args.apply else Noop():
    ledger.write_text(root, f"{settings.KC_DIR}/reports/review-queue.md", text, args.apply)
  print(text)
  if st.open_conflicts():
    raise ReviewNeeded(f"{len(st.open_conflicts())} open conflict(s) await a decision")
  return {"open": 0}


def cmd_validate(root: Path, args) -> dict:
  """Run the deterministic gates.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.

  Raises:
    SourceChanged: a source changed (exit 5).
    ValidationFailed: any other error (exit 3).
  """
  res = validate.run(state.load(root), args.strict)
  if not res["ok"]:
    emit(res)
    raise (SourceChanged if res["source_changed"] else ValidationFailed)(f"{len(res['errors'])} validation error(s)")
  return res


COMMANDS = {
  "init": cmd_init,
  "inventory": cmd_inventory,
  "worksheet": lambda root, a: worksheet.batch(state.load(root), a.batch, a.path),
  "sections": lambda root, a: worksheet.sections(state.load(root), a.path),
  "vocabulary": lambda root, a: worksheet.vocabulary(state.load(root)),
  "coverage": lambda root, a: claims.coverage(state.load(root)),
  "claims": lambda root, a: _ingest(root, a, "claims"),
  "candidates": lambda root, a: candidates.pairs(state.load(root), a.limit),
  "decision-points": lambda root, a: decision_points.decision_points(state.load(root)),
  "aliases": cmd_aliases,
  "recall": lambda root, a: recall.score(state.load(root), Path(a.labels)),
  "group-review": cmd_group_review,
  "drift": lambda root, a: drift.report(state.load(root), a.path),
  "relate": lambda root, a: _ingest(root, a, "relations"),
  "review": cmd_review,
  "decide": cmd_decide,
  "amend": cmd_amend,
  "render": cmd_render,
  "promote": cmd_promote,
  "archive-plan": cmd_archive_plan,
  "query": lambda root, a: {"results": query.search(state.load(root), a.text, a.limit, a.history)},
  "intake": lambda root, a: intake.respond(state.load(root), json.loads(Path(a.payload).read_text(encoding="utf-8"))),
  "validate": cmd_validate,
  "report": lambda root, a: report.build(state.load(root)),
}
