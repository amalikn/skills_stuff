"""Review-side commands for scripts/knowledge_curator.py: decisions, amendments, group reviews and consolidation aliases.

Imported by commands.py, not run. Each function takes the project root and the parsed arguments and returns a JSON-ready dict, or raises a
KcError subclass. Safety: writes only through ledger.py, and only when args.apply is set.
"""

from pathlib import Path

from . import aliases, amendments, claims, decision_points, decisions, ledger, settings, state
from .command_support import Noop, now, reject
from .errors import InputError


def _record_decision(root: Path, res: decisions.DecideResult, apply: bool) -> None:
  """Append one decision's records under the write lock.

  Args:
    root: project root.
    res: the decision result.
    apply: write (False plans only).
  """
  with ledger.write_lock(root) if apply else Noop():
    ledger.append(root, "decisions", [res.decision], apply)
    ledger.append(root, "conflicts", res.conflicts, apply)
    ledger.append(root, "claims", res.claims + res.dispositions, apply)


def cmd_decide(root: Path, args) -> dict:
  """Record an operator decision on a conflict.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.
  """
  st = state.load(root)
  res = decisions.decide(
    st,
    args.conflict,
    args.action,
    args.reason,
    args.actor or settings.actor(),
    now(),
    current=args.current,
    scope_note=args.scope_note,
    corrected_text=args.corrected_text,
    answer_text=args.answer_text,
    override_supersession=args.override_supersession,
  )
  _record_decision(root, res, args.apply)
  return {"applied": args.apply, "decision": res.decision, "new_claims": [c["claim_id"] for c in res.claims]}


def cmd_amend(root: Path, args) -> dict:
  """Add a claim to a conflict, superseding or keeping it.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.
  """
  st, who = state.load(root), args.actor or settings.actor()
  if args.set_successor:
    if not args.successor:
      raise InputError("--set-successor needs --successor")
    res = amendments.set_successor(st, args.conflict, args.set_successor, args.successor, args.reason, who, now())
  else:
    if not (args.supersede or args.keep):
      raise InputError("--add-claim needs --supersede or --keep")
    res = amendments.amend(st, args.conflict, args.add_claim, args.supersede, args.reason, who, now())
  _record_decision(root, res, args.apply)
  return {"applied": args.apply, "decision": res.decision}


def cmd_aliases(root: Path, args) -> dict:
  """Record consolidation aliases.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.
  """
  res = aliases.ingest(state.load(root), claims.load_input(Path(args.file)))
  if res.errors:
    reject(res.errors, False)
  with ledger.write_lock(root) if args.apply else Noop():
    ledger.append(root, "aliases", res.aliases, args.apply)
  return {"applied": args.apply, "aliases": len(res.aliases)}


def cmd_group_review(root: Path, args) -> dict:
  """Record a decision point as reviewed whole.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.
  """
  rec = decision_points.group_review(state.load(root), args.group, args.reason)
  with ledger.write_lock(root) if args.apply else Noop():
    ledger.append(root, "relations", [rec], args.apply)
  return {"applied": args.apply, "group_review": rec}
