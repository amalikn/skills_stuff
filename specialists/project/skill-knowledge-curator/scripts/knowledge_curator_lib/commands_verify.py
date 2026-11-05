"""Root-cause and verifier commands for scripts/knowledge_curator.py: `kc roots` and `kc verify` (research B3, B4).

Imported by commands.py, not run. Each function takes the project root and the parsed arguments and returns a JSON-ready dict, or raises a
KcError subclass. Safety: writes only through ledger.py, and only with args.apply; `verify --model` sends claim text to the configured
loopback endpoint (llm.py) and records nothing without --apply.
"""

import json
from pathlib import Path

from . import claims, ledger, roots, sampling, schema, settings, state, verify
from .command_support import Noop, now
from .errors import InputError


def cmd_roots(root: Path, args) -> dict:
  """Group open conflicts by cause (read-only).

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Groups and counts; --limit keeps the first N groups, counts cover all.
  """
  res = roots.group(state.load(root))
  if args.limit:
    res["groups"] = res["groups"][: args.limit]
  return res


def _record(root: Path, events: list[dict], apply: bool) -> None:
  """Append conflict events under the write lock.

  Args:
    root: project root.
    events: conflict events.
    apply: write (False plans only).
  """
  with ledger.write_lock(root) if apply else Noop():
    ledger.append(root, "conflicts", events, apply)


def _load_verdicts(path: Path) -> list[dict]:
  """Verdicts from a file, each checked against schemas/verify-verdict.schema.json.

  Args:
    path: JSON or JSONL file.

  Returns:
    Verdict records.

  Raises:
    InputError: any record breaks the schema (the whole file is refused).
  """
  rows = claims.load_input(path)
  bad = [f"[{n}] {e}" for n, r in enumerate(rows) for e in schema.errors("verify-verdict", r)]
  if bad:
    raise InputError("verdicts rejected:\n  " + "\n  ".join(bad))
  return rows


def _export(root: Path, st, args) -> dict:
  """Print verify tasks, or write them as batch files with --apply.

  Args:
    root: project root.
    st: current state.
    args: parsed arguments.

  Returns:
    Counts, plus the batches on a dry run.
  """
  res = verify.export(st, args.batch_size or st.cfg["verify"]["batch_size"])
  if args.apply:
    with ledger.write_lock(root):
      for n, batch in enumerate(res["batches"], 1):
        body = {"prompt_version": res["prompt_version"], "instructions": res["instructions"], "tasks": batch}
        ledger.write_text(root, f"{settings.KC_DIR}/verify/batch-{n:02d}.json", json.dumps(body, indent=1, ensure_ascii=False) + "\n", True)
  return {"applied": args.apply, "counts": res["counts"], **({} if args.apply else {"batches": res["batches"], "instructions": res["instructions"]})}


def cmd_verify(root: Path, args) -> dict:
  """Export tasks, take verdicts from a file or a local model, confirm a run, or score one.

  Args:
    root: project root.
    args: parsed arguments.

  Returns:
    Result.

  Raises:
    InputError: no mode chosen, or verdicts refused.
  """
  st, at = state.load(root), now().isoformat(timespec="seconds")
  if args.score:
    return sampling.verify_score(st, Path(args.score))
  if args.export:
    return _export(root, st, args)
  if args.confirm:
    res = verify.confirm(st, args.confirm, at)
    _record(root, res["events"], args.apply)
    cleared = {s: sum(e["status"] == s for e in res["events"]) for s in settings.CLEARED_STATUSES}
    return {"applied": args.apply, "run_id": res["run_id"], "cleared": cleared, "kept": res["kept"], "undo": f"kc triage --undo {res['run_id']} --apply"}
  if args.model:
    ran = verify.run_model(st, args.model, args.limit)
    verdicts, verifier = ran.pop("verdicts"), ran.pop("verifier")
  elif args.file:
    verdicts, verifier, ran = _load_verdicts(Path(args.file)), {"mode": "agent", "model": args.verifier}, {}
  else:
    raise InputError("choose --export, --file, --model, --confirm or --score")
  res = verify.ingest(st, verdicts, verifier, at)
  if res["errors"]:
    raise InputError("verdicts refused:\n  " + "\n  ".join(res["errors"]))
  _record(root, res["events"], args.apply)
  return {"applied": args.apply, "run_id": res["run_id"], "counts": res["counts"], "downgraded": res["downgraded"], **ran}
