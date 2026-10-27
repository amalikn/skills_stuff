"""Candidate pairs for duplicate and conflict review.

Method: SQLite FTS5 blocking, then RapidFuzz scores, deterministic signals and an
optional NLI score.

Imported, not run. Blocking keeps the work near-linear: each claim is compared only with its FTS neighbours and claims sharing its
subject, never with every other claim. Signals rank pairs; they never decide (design doc 7.1). Pairs already classified in
relations.jsonl are left out, so reruns ask nothing new (INV-011). Safety: in-memory database; reads state only.
"""

import re
import sqlite3

from . import fuzzy, ids, nli
from .state import State

_NEG = re.compile(r"\b(not|no|never|without|removed|retired|absent|disabled|rejected|failed|cannot)\b", re.IGNORECASE)
_NUM = re.compile(r"\d+(?:\.\d+)*")
_TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]{2,}")


def scope_overlaps(a: dict, b: dict) -> bool:
  """Whether two scopes can describe the same situation: every key both name has the same value (a missing key matches any).

  Args:
    a: first scope.
    b: second scope.

  Returns:
    True when they overlap.
  """
  return all(str(a[k]).lower() == str(b[k]).lower() for k in a.keys() & b.keys())


def _fts_neighbours(claims: dict, limit: int) -> dict[str, set[str]]:
  """FTS5 neighbours of every claim.

  Args:
    claims: claim_id -> claim.
    limit: neighbours per claim.

  Returns:
    claim_id -> neighbouring claim IDs (itself excluded).
  """
  db = sqlite3.connect(":memory:")
  db.execute("CREATE VIRTUAL TABLE f USING fts5(cid UNINDEXED, body)")
  db.executemany("INSERT INTO f VALUES (?, ?)", [(cid, f"{c['subject']} {c['claim_text']}") for cid, c in claims.items()])
  out = {}
  for cid, c in claims.items():
    tokens = list(dict.fromkeys(_TOKEN.findall(ids.norm(f"{c['subject']} {c['claim_text']}"))))[:12]
    if not tokens:
      out[cid] = set()
      continue
    query = " OR ".join('"' + t.replace('"', "") + '"' for t in tokens)
    rows = db.execute("SELECT cid FROM f WHERE f MATCH ? ORDER BY rank LIMIT ?", (query, limit + 1)).fetchall()
    out[cid] = {r[0] for r in rows} - {cid}
  db.close()
  return out


def signals(a: dict, b: dict, ratio: float) -> list[str]:
  """Deterministic disagreement signals for one pair.

  Args:
    a: first claim.
    b: second claim.
    ratio: their text similarity.

  Returns:
    Signal names, sorted.
  """
  out = []
  same_key = ids.norm(a["subject"]) == ids.norm(b["subject"]) and ids.norm(a["predicate"]) == ids.norm(b["predicate"])
  overlap = scope_overlaps(a["scope"], b["scope"])
  if same_key and overlap and ids.norm(a["object"]) != ids.norm(b["object"]):
    out.append("same-key-different-object")
  if same_key and not overlap:
    out.append("same-key-different-scope")
  nums_a, nums_b = set(_NUM.findall(a["claim_text"])), set(_NUM.findall(b["claim_text"]))
  if (same_key or ratio >= 70) and nums_a and nums_b and nums_a != nums_b:
    out.append("numeric-mismatch")
  if (same_key or ratio >= 70) and bool(_NEG.search(a["claim_text"])) != bool(_NEG.search(b["claim_text"])):
    out.append("negation-asymmetry")
  if a["kind"] != b["kind"] and {a["kind"], b["kind"]} & {"proposal", "observed", "decision"} and (same_key or ratio >= 70):
    out.append("kind-differs")
  return sorted(out)


def _pair_row(st: State, a: str, b: str, ratio: float, sig: list[str]) -> dict:
  """Output row for one candidate pair.

  Args:
    st: current state.
    a: first claim ID.
    b: second claim ID.
    ratio: similarity.
    sig: signals.

  Returns:
    The row.
  """
  ca, cb = st.claims[a], st.claims[b]
  shared = {e["source_sha256"] for e in ca["evidence"]} & {e["source_sha256"] for e in cb["evidence"]}
  return {
    "claims": [a, b],
    "texts": [ca["claim_text"], cb["claim_text"]],
    "kinds": [ca["kind"], cb["kind"]],
    "scopes": [ca["scope"], cb["scope"]],
    "dispositions": [st.disposition(a), st.disposition(b)],
    "sources": [sorted({e["path"] for e in ca["evidence"]}), sorted({e["path"] for e in cb["evidence"]})],
    "same_source_bytes": bool(shared),
    "similarity": ratio,
    "signals": sig,
  }


def pairs(st: State) -> dict:
  """Candidate pairs not yet classified.

  Args:
    st: current state.

  Returns:
    {"pairs": [...], "nli": bool, "compared": n}; deterministic-signal pairs first, then by similarity.
  """
  cfg = st.cfg["candidates"]
  active = {cid: c for cid, c in st.claims.items() if st.disposition(cid) not in ("DUPLICATE", "REJECTED")}
  done = {frozenset(r["claims"]) for r in st.relations.values()}
  by_subject: dict[str, set[str]] = {}
  for cid, c in active.items():
    by_subject.setdefault(ids.norm(c["subject"]), set()).add(cid)
  neighbours = _fts_neighbours(active, cfg["fts_neighbours"])
  seen, rows = set(), []
  for a in sorted(active):
    for b in sorted(neighbours[a] | by_subject[ids.norm(active[a]["subject"])]):
      key = frozenset((a, b))
      if a == b or key in seen or key in done:
        continue
      seen.add(key)
      x, y = sorted((a, b))
      ratio = fuzzy.similarity(active[x]["claim_text"], active[y]["claim_text"])
      sig = signals(active[x], active[y], ratio)
      if sig or ratio >= cfg["min_ratio"]:
        rows.append(_pair_row(st, x, y, ratio, sig))
  scores = nli.contradiction_scores([(r["texts"][0], r["texts"][1]) for r in rows])
  for row, score in zip(rows, scores or [], strict=False):
    row["nli_contradiction"] = score
  rows.sort(key=lambda r: (0 if r["signals"] else 1, -r["similarity"], r["claims"]))
  return {"pairs": rows, "nli": scores is not None, "compared": len(seen)}
