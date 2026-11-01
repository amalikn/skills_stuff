"""Seeded samples of conflicts as blind cards, and precision with a Wilson interval (research B0).

Imported, not run. Small samples only support intervals, never a per-finding noise probability, so this reports intervals. Safety: reads state.
"""

import json
import math
import random
from pathlib import Path

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
