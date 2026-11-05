"""Refuting verifier (research B4, `kc verify`): try to show an open conflict is not one before a person reads it.

Imported, not run. Three ways in, one record: an agent answers exported tasks (`--export`, then `--file`), or a local model on an
OpenAI-compatible server answers them (`--model`, through llm.py). A verdict is conflict, not-conflict (with a kind) or uncertain, and a
not-conflict must quote a line of the pair's own evidence, or it is downgraded to uncertain (citation-constrained). Verdicts only propose:
the conflict stays open with a `verify` note until the operator confirms a run in bulk (`--confirm`), which clears not-conflict pairs as
dismissed or documented-evolution, never P0, never a same-identifier-opposite-status pair, and never a different-scope pair whose recorded
scopes overlap (the model's word alone is not a scope); `kc triage --undo` reverses it.
A model run first answers two control pairs and stops if either is wrong, because a model can read the verdict words backwards.
Safety: returns records for ledger.append; the model arm sends claim text to a loopback endpoint unless the config allows otherwise.
"""

import json
import time
from collections import Counter

from . import ids, llm, roots, settings, status_map, triage
from .candidates import overlaps, situation
from .errors import InputError
from .state import State

# Version 2 (2026-11-05): version 1 opened with "try to refute the conflict first" and answered not-conflict on 75 of 96 MCP pilot pairs,
# mostly different-scope for two claims naming the same path; version 2 drops the bias and makes a shared identifier the same scope.
PROMPT_VERSION = 2
INSTRUCTIONS = (
  "You check whether two statements from project documents conflict. A careful reader flagged each pair; do not explain a "
  "disagreement away. Answer verdict 'conflict' when both cannot be true now in the same scope. When both statements name the same "
  "path, server, file or setting and give it different states or values, that is the same scope: answer 'conflict' unless the words "
  "themselves give a date, a stated replacement or a superseded label. Answer 'not-conflict' only when the quoted words show why both "
  "can stand, and name the kind: time-evolution (the words date or state a replacement), superseded-history (the document is labelled "
  "superseded or historical), different-scope (the words name different environments, hosts, components or conditions), equivalent "
  "(same meaning in other words), proposal-vs-observation (one is worded as a plan or option, the other as a fact), extraction-error "
  "(a statement misreads its excerpt), other. A not-conflict must quote, word for word, the excerpt words that show it. Answer "
  "'uncertain' when the evidence does not settle it. Reply with one JSON object: "
  '{"verdict": "conflict|not-conflict|uncertain", "kind": "<kind or null>", "quote": "<exact words or null>", "reason": "<one sentence>"}'
)
CONTROLS = (
  {
    "expected": "conflict",
    "a": {"text": "The nightly backup runs at 02:00 on the primary database.", "doc_status": "unknown"},
    "b": {"text": "The primary database has no scheduled backup; backups are manual only.", "doc_status": "unknown"},
  },
  {
    "expected": "not-conflict",
    "a": {"text": "In 2025 the gateway was Caddy.", "doc_status": "historical"},
    "b": {"text": "Since March 2026 the gateway is Traefik; it replaced Caddy.", "doc_status": "unknown"},
  },
)


def _norm(text: str) -> str:
  """Whitespace-folded lower-case text for quote matching.

  Args:
    text: any text.

  Returns:
    Folded text.
  """
  return " ".join((text or "").split()).lower()


def _side(st: State, cid: str, status: dict) -> dict:
  """One claim as a verifier sees it.

  Args:
    st: current state.
    cid: claim ID.
    status: from status_map.files.

  Returns:
    {claim_id, text, kind, epistemic_status, scope, evidence: [{path, lines, excerpt, doc_status}]}.
  """
  c = st.claims[cid]
  ev = [
    {
      "path": e["path"],
      "lines": [e["line_start"], e["line_end"]],
      "excerpt": e.get("excerpt", ""),
      "doc_status": status.get(e["path"], {}).get("status", "unknown"),
    }
    for e in c["evidence"]
  ]
  return {"claim_id": cid, "text": c["claim_text"], "kind": c["kind"], "epistemic_status": c["epistemic_status"], "scope": c.get("scope", {}), "evidence": ev}


def tasks(st: State) -> list[dict]:
  """One verify task per open conflict, ordered by root group so a shared cause is read together.

  Args:
    st: current state.

  Returns:
    Task records.
  """
  status, where = status_map.files(st), roots.index(st)
  out = []
  for cf in st.open_conflicts():
    group = where.get(cf["conflict_id"], {})
    out.append(
      {
        "conflict_id": cf["conflict_id"],
        "severity": cf["severity"],
        "conflict_type": cf["conflict_type"],
        "question": cf.get("question"),
        "root": {"root_id": group.get("root_id"), "token": group.get("token"), "size": group.get("size")},
        "claims": [_side(st, c, status) for c in cf["claims"]],
      }
    )
  out.sort(key=lambda t: (t["root"]["root_id"] or "", t["severity"], t["conflict_id"]))
  return out


def export(st: State, batch_size: int) -> dict:
  """Batches of tasks for an agent to answer.

  Args:
    st: current state.
    batch_size: tasks per batch.

  Returns:
    {"prompt_version", "instructions", "batches": [[task, ...], ...], "counts"}.
  """
  ts = tasks(st)
  batches = [ts[i : i + batch_size] for i in range(0, len(ts), batch_size)]
  return {"prompt_version": PROMPT_VERSION, "instructions": INSTRUCTIONS, "batches": batches, "counts": {"tasks": len(ts), "batches": len(batches)}}


def _quoted(st: State, cf: dict, quote: str | None) -> bool:
  """Whether a quote is words of the pair's own claims or excerpts.

  Args:
    st: current state.
    cf: the conflict.
    quote: quoted words.

  Returns:
    True when found.
  """
  q = _norm(quote)
  if len(q) < 8:
    return False
  texts = [st.claims[c]["claim_text"] for c in cf["claims"]] + [e.get("excerpt", "") for c in cf["claims"] for e in st.claims[c]["evidence"]]
  return any(q in _norm(t) for t in texts)


def ingest(st: State, verdicts: list[dict], verifier: dict, now: str) -> dict:
  """Check verdicts and turn them into conflict events carrying a verify note; statuses stay open.

  Args:
    st: current state.
    verdicts: [{conflict_id, verdict, kind, quote, reason}].
    verifier: {"mode": "agent" | "model", "model": ..., "endpoint": ...}.
    now: run time.

  Returns:
    {"run_id", "events", "errors", "downgraded", "counts"}.
  """
  run_id = ids.make_id("vr", now, sorted(str(v.get("conflict_id")) for v in verdicts))
  events, errors, downgraded = [], [], []
  for n, v in enumerate(verdicts):
    cf = st.conflicts.get(v.get("conflict_id"))
    if not cf or cf["status"] != "open":
      errors.append(f"[{n}] {v.get('conflict_id')}: not an open conflict")
      continue
    verdict, kind = v.get("verdict"), v.get("kind")
    if verdict not in settings.VERIFY_VERDICTS:
      errors.append(f"[{n}] {cf['conflict_id']}: verdict {verdict!r} not in {settings.VERIFY_VERDICTS}")
      continue
    note = {"verdict": verdict, "kind": None, "quote": v.get("quote"), "reason": v.get("reason") or "", "verifier": verifier}
    if verdict == "not-conflict":
      if kind not in settings.VERIFY_KINDS:
        note |= {"verdict": "uncertain", "downgraded": f"kind {kind!r} not in the vocabulary"}
      elif not _quoted(st, cf, v.get("quote")):
        note |= {"verdict": "uncertain", "kind": kind, "downgraded": "quote not found in the pair's claims or excerpts"}
      else:
        note["kind"] = kind
      if note.get("downgraded"):
        downgraded.append(cf["conflict_id"])
    note |= {"run_id": run_id, "prompt_version": PROMPT_VERSION, "at": now}
    events.append({**cf, "verify": note})
  counts = Counter(e["verify"]["verdict"] for e in events)
  return {"run_id": run_id, "events": events, "errors": errors, "downgraded": downgraded, "counts": dict(sorted(counts.items()))}


def _prompt(task: dict) -> str:
  """User prompt for one task.

  Args:
    task: a task record (or a control).

  Returns:
    Prompt text.
  """
  return json.dumps({k: task[k] for k in ("question", "claims") if k in task} | {"root": task.get("root")}, ensure_ascii=False, indent=1)


def _control_task(control: dict) -> dict:
  """A control pair shaped like a task.

  Args:
    control: one of CONTROLS.

  Returns:
    Task record.
  """
  sides = [{"text": s["text"], "evidence": [{"excerpt": s["text"], "doc_status": s["doc_status"]}]} for s in (control["a"], control["b"])]
  return {"question": "Do these two statements conflict?", "claims": sides}


def _check_controls(base: str, model: str, max_tokens: int, usage: Counter) -> list[dict]:
  """Ask the control pairs; any wrong answer stops the run before a verdict is recorded.

  Args:
    base: endpoint base URL.
    model: model ID.
    max_tokens: completion cap.
    usage: token counter, updated in place.

  Returns:
    [{expected, got}] per control.

  Raises:
    InputError: a control failed to run or was answered wrong.
  """
  controls = []
  for control in CONTROLS:
    try:
      got, used = llm.chat_json(base, model, INSTRUCTIONS, _prompt(_control_task(control)), max_tokens)
    except llm.ModelError as err:
      raise InputError(f"control pair failed to run: {err}") from err
    usage.update({k: v or 0 for k, v in used.items()})
    controls.append({"expected": control["expected"], "got": got.get("verdict")})
    if got.get("verdict") != control["expected"]:
      raise InputError(f"control pair answered {got.get('verdict')!r}, expected {control['expected']!r}: verdicts from {model} are not trusted")
  return controls


def run_model(st: State, model: str, limit: int | None = None) -> dict:
  """Answer every open conflict with a local model, after the control pairs pass.

  Args:
    st: current state.
    model: allowlisted model ID.
    limit: answer only the first N tasks.

  Returns:
    {"verdicts", "verifier", "controls", "timing", "usage"}.

  Raises:
    InputError: the model or endpoint is not allowed, or a control pair is answered wrong.
  """
  cfg = st.cfg["verify"]
  base = llm.check_target(cfg, model)
  timing, usage = {}, Counter()
  start = time.perf_counter()
  controls = _check_controls(base, model, cfg["max_tokens"], usage)
  timing["controls_s"] = round(time.perf_counter() - start, 2)
  verdicts, ts = [], tasks(st)[:limit] if limit else tasks(st)
  start = time.perf_counter()
  for task in ts:
    try:
      got, used = llm.chat_json(base, model, INSTRUCTIONS, _prompt(task), cfg["max_tokens"])
      usage.update({k: v or 0 for k, v in used.items()})
      row = {"conflict_id": task["conflict_id"], **{k: got.get(k) for k in ("verdict", "kind", "quote", "reason")}}
      if row["verdict"] not in settings.VERIFY_VERDICTS:
        row = row | {"verdict": "uncertain", "reason": f"model answered {row['verdict']!r}, outside the vocabulary: {row.get('reason')}"}
      verdicts.append(row)
    except llm.ModelError as err:
      verdicts.append({"conflict_id": task["conflict_id"], "verdict": "uncertain", "kind": None, "quote": None, "reason": f"model error: {err}"})
  timing["tasks_s"] = round(time.perf_counter() - start, 2)
  timing["per_task_s"] = round(timing["tasks_s"] / len(ts), 2) if ts else 0.0
  verifier = {"mode": "model", "model": model, "endpoint": base}
  return {"verdicts": verdicts, "verifier": verifier, "controls": controls, "timing": timing, "usage": dict(usage)}


def confirm(st: State, run_id: str, now: str) -> dict:
  """The operator's bulk confirmation of one verify run: clear its not-conflict pairs, with guards.

  Args:
    st: current state.
    run_id: the verify run.
    now: confirmation time.

  Returns:
    {"run_id" (the confirmation's, for kc triage --undo), "events", "kept": [{conflict_id, why}]}.
  """
  hit = [c for c in st.open_conflicts() if c.get("verify", {}).get("run_id") == run_id]
  confirm_id = ids.make_id("tr", "verify-confirm", run_id, now)
  events, kept = [], []
  for cf in hit:
    note = cf["verify"]
    a, b = (st.claims[c] for c in cf["claims"][:2])
    if note["verdict"] != "not-conflict":
      kept.append({"conflict_id": cf["conflict_id"], "why": note["verdict"]})
    elif cf["severity"] == "P0":
      kept.append({"conflict_id": cf["conflict_id"], "why": "p0"})
    elif triage.opposite_status(a, b):
      kept.append({"conflict_id": cf["conflict_id"], "why": "same-identifier-opposite-status"})
    elif note["kind"] == "different-scope" and overlaps(situation(a["scope"]), situation(b["scope"])):
      # The model's scope claim has no record behind it: on the MCP pilot most real conflicts it lost were different-scope (evaluation.md, kc verify).
      kept.append({"conflict_id": cf["conflict_id"], "why": "scope-not-recorded"})
    else:
      status = "documented-evolution" if note["kind"] in settings.VERIFY_EVOLUTION_KINDS else "dismissed"
      signals = [s for s in (note.get("quote"), note.get("reason")) if s]
      rule = {"rule": f"verify:{note['kind']}", "version": PROMPT_VERSION, "signals": signals, "run_id": confirm_id, "at": now, "verify_run": run_id}
      events.append({**cf, "status": status, "triage": rule})
  return {"run_id": confirm_id, "events": events, "kept": kept}
