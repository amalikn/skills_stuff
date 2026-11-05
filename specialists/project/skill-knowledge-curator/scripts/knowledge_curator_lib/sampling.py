"""Seeded samples of conflicts as blind cards, precision with a Wilson interval (research B0), and kc verify notes scored against labels (B4).

Imported, not run. Small samples only support intervals, never a per-finding noise probability, so this reports intervals. Safety: reads state.
"""

import json
import math
import random
from collections import Counter
from pathlib import Path

from . import verify
from .errors import InputError
from .state import State

Z_95 = 1.959964


def wilson(hits: int, total: int) -> list[float]:
  """Wilson 95% interval for a proportion.

  Args:
    hits: successes.
    total: trials.

  Returns:
    [low, high], rounded to three places.
  """
  if not total:
    return [0.0, 0.0]
  p, z2 = hits / total, Z_95**2
  centre = (p + z2 / (2 * total)) / (1 + z2 / total)
  half = Z_95 * math.sqrt(p * (1 - p) / total + z2 / (4 * total**2)) / (1 + z2 / total)
  return [round(centre - half, 3), round(centre + half, 3)]


def cards(st: State, size: int, seed: int, status: str, exclude: Path | None) -> dict:
  """A seeded sample of conflicts, with no verdict or severity shown, so a judge stays blind.

  Args:
    st: current state.
    size: cards wanted.
    seed: random seed.
    status: conflict status to draw from.
    exclude: JSON file of records with conflict_id to leave out.

  Returns:
    {"cards": [...], "population": n, "seed": seed}.
  """
  used = {r["conflict_id"] for r in json.loads(exclude.read_text(encoding="utf-8"))} if exclude else set()
  pool = sorted(c for c, r in st.conflicts.items() if r["status"] == status and c not in used)
  chosen = random.Random(seed).sample(pool, min(size, len(pool)))
  rows = []
  for cid in chosen:
    cf = st.conflicts[cid]
    claims = [
      {"text": st.claims[c]["claim_text"], "lines": sorted({f"{e['path']}:{e['line_start']}-{e['line_end']}" for e in st.claims[c]["evidence"]})}
      for c in cf["claims"]
    ]
    rows.append({"conflict_id": cid, "question": cf["question"], "claims": claims})
  return {"cards": rows, "population": len(pool), "seed": seed}


def score(path: Path) -> dict:
  """Precision from verdicts; unclear ones are counted apart.

  Args:
    path: JSON array of {conflict_id, verdict}.

  Returns:
    Counts, precision and its Wilson interval.
  """
  rows = json.loads(path.read_text(encoding="utf-8"))
  real = sum(r["verdict"] == "real" for r in rows)
  noise = sum(r["verdict"] == "noise" for r in rows)
  total = real + noise
  return {"real": real, "noise": noise, "unclear": len(rows) - total, "precision": round(real / total, 3) if total else 0.0, "interval": wilson(real, total)}


def verify_score(st: State, labels: Path) -> dict:
  """Compare the latest verify notes with labelled verdicts (judge files: [{conflict_id, verdict: real | noise}]).

  Args:
    st: current state.
    labels: labels file.

  Returns:
    {"labelled", "matrix", "real_lost", "noise_cleared", "kept_precision", "by_kind"}.

  Raises:
    InputError: the labels file is not a JSON array.
  """
  rows = json.loads(labels.read_text(encoding="utf-8"))
  if not isinstance(rows, list):
    raise InputError(f"{labels}: expected a JSON array")
  matrix, by_kind, lost = Counter(), Counter(), []
  for r in rows:
    note = st.conflicts.get(r["conflict_id"], {}).get("verify")
    if not note:
      continue
    matrix[f"{r['verdict']}->{note['verdict']}"] += 1
    if note["verdict"] == "not-conflict":
      by_kind[f"{note['kind']}:{r['verdict']}"] += 1
      if r["verdict"] == "real":
        lost.append(r["conflict_id"])
  real = sum(v for k, v in matrix.items() if k.startswith("real->"))
  noise = sum(v for k, v in matrix.items() if k.startswith("noise->"))
  kept_real = real - len(lost)
  kept = kept_real + noise - matrix["noise->not-conflict"]
  return {
    "labelled": real + noise,
    "matrix": dict(sorted(matrix.items())),
    "real_lost": sorted(lost),
    "real_recall_kept": round(kept_real / real, 3) if real else None,
    "noise_cleared": round(matrix["noise->not-conflict"] / noise, 3) if noise else None,
    "kept_precision": round(kept_real / kept, 3) if kept else None,
    "by_kind": dict(sorted(by_kind.items())),
    "confirm": _confirm_outcomes(st, {r["conflict_id"]: r["verdict"] for r in rows}),
  }


def _confirm_outcomes(st: State, labels: dict[str, str]) -> dict:
  """What `kc verify --confirm` would clear for each verify run, by label, with all guards applied (nothing is written).

  Args:
    st: current state.
    labels: conflict_id -> real | noise.

  Returns:
    run_id -> {"would_clear": {label: n}, "real_cleared": [ids], "clears_right": share of labelled clears that were noise}.
  """
  out = {}
  for run in sorted({c["verify"]["run_id"] for c in st.open_conflicts() if c.get("verify")}):
    cleared = [e["conflict_id"] for e in verify.confirm(st, run, "score")["events"]]
    seen = Counter(labels.get(c, "unlabelled") for c in cleared)
    judged = seen["real"] + seen["noise"]
    out[run] = {
      "would_clear": dict(sorted(seen.items())),
      "real_cleared": sorted(c for c in cleared if labels.get(c) == "real"),
      "clears_right": round(seen["noise"] / judged, 3) if judged else None,
    }
  return out
