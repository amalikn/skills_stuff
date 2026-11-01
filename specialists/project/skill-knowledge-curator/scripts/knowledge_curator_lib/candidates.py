"""Candidate pairs for duplicate and conflict review.

Method: SQLite FTS5 blocking, then RapidFuzz scores, deterministic signals and an
optional NLI score.

Imported, not run. Blocking keeps the work near-linear: each claim is compared only with its FTS neighbours and claims sharing its
subject or topic, never with every other claim. Signals rank pairs; they never decide (design doc 7.1). Pairs already classified in
relations.jsonl are left out, so reruns ask nothing new (INV-011). Safety: in-memory database; reads state only.
"""

import re
import sqlite3
from collections import Counter
from functools import lru_cache
from itertools import combinations

from . import fuzzy, ids, nli, settings
from .state import State

_NEG = re.compile(r"\b(not|no|never|without|removed|retired|absent|disabled|rejected|failed|cannot)\b", re.IGNORECASE)
_NUM = re.compile(r"\d+(?:\.\d+)*")
_TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]{2,}")


norm_cached = lru_cache(maxsize=None)(ids.norm)
_subject_similarity = lru_cache(maxsize=None)(fuzzy.similarity)


def situation(scope: dict) -> dict:
  """Scope without provenance keys: where a claim came from never separates it from another source (P12).

  Args:
    scope: claim scope.

  Returns:
    The situational keys only.
  """
  return {k: v for k, v in scope.items() if k.lower() not in settings.PROVENANCE_SCOPE_KEYS}


def _overlaps(a: dict, b: dict) -> bool:
  """Whether two situations can be the same: every key both name has the same value (a missing key matches any).

  Args:
    a: first situation, from situation.
    b: second situation.

  Returns:
    True when they overlap.
  """
  return all(str(a[k]).lower() == str(b[k]).lower() for k in a.keys() & b.keys())


def source_ids(claim: dict) -> set[str]:
  """Independent sources of a claim (byte copies count once).

  Args:
    claim: the claim.

  Returns:
    Source hashes.
  """
  return {e["source_sha256"] for e in claim["evidence"]}


def _prepared(claim: dict, project: str, multi: set[str]) -> dict:
  """Claim with its per-claim comparison facts computed once, not per pair (pairs() compares about 190,000 pairs at 3,500 claims).

  Args:
    claim: the claim.
    project: project ID, not counted as a subject word.
    multi: normalised multi-valued predicates.

  Returns:
    A copy carrying sources, situation, numbers, negated, subject_words and multi.
  """
  text = claim["claim_text"]
  return {
    **claim,
    "sources": source_ids(claim),
    "situation": situation(claim["scope"]),
    "numbers": set(_NUM.findall(text)),
    "negated": bool(_NEG.search(text)),
    "subject_words": set(norm_cached(claim["subject"]).split()) - set(norm_cached(project).split()),
    "multi": norm_cached(claim["predicate"]) in multi,
  }


def _search_tokens(claims: dict, cfg: dict) -> dict[str, list[str]]:
  """Rarest tokens of every claim: common words cost most FTS time and separate least, and rare ones carry the match.

  Args:
    claims: claim_id -> claim.
    cfg: candidates config (fts_tokens, fts_common_share).

  Returns:
    claim_id -> tokens to search.
  """
  own = {cid: list(dict.fromkeys(_TOKEN.findall(ids.norm(f"{c['subject']} {c['claim_text']}")))) for cid, c in claims.items()}
  freq = Counter(t for tokens in own.values() for t in tokens)
  common = max(5, len(claims) * cfg["fts_common_share"])
  return {cid: sorted((t for t in tokens if freq[t] <= common), key=lambda t: (freq[t], t))[: cfg["fts_tokens"]] for cid, tokens in own.items()}


def _fts_neighbours(claims: dict, cfg: dict) -> dict[str, set[str]]:
  """FTS5 neighbours of every claim.

  Args:
    claims: claim_id -> claim.
    cfg: candidates config (fts_neighbours and the token limits).

  Returns:
    claim_id -> neighbouring claim IDs (itself excluded).
  """
  limit = cfg["fts_neighbours"]
  db = sqlite3.connect(":memory:")
  db.execute("CREATE VIRTUAL TABLE f USING fts5(cid UNINDEXED, body)")
  db.executemany("INSERT INTO f VALUES (?, ?)", [(cid, f"{c['subject']} {c['claim_text']}") for cid, c in claims.items()])
  out = {}
  for cid, tokens in _search_tokens(claims, cfg).items():
    if not tokens:
      out[cid] = set()
      continue
    query = " OR ".join('"' + t.replace('"', "") + '"' for t in tokens)
    rows = db.execute("SELECT cid FROM f WHERE f MATCH ? ORDER BY rank LIMIT ?", (query, limit + 1)).fetchall()
    out[cid] = {r[0] for r in rows} - {cid}
  db.close()
  return out


def _shared_subject(a: dict, b: dict, subject_ratio: float) -> bool:
  """Whether two subjects name the same thing within one topic: near-identical, or sharing a word that is not the project's own name.

  Args:
    a: first claim, from _prepared.
    b: second claim, from _prepared.
    subject_ratio: similarity that counts as near-identical.

  Returns:
    True when they match.
  """
  return bool(a["subject_words"] & b["subject_words"]) or _subject_similarity(norm_cached(a["subject"]), norm_cached(b["subject"])) >= subject_ratio


def signals(a: dict, b: dict, ratio: float, subject_ratio: float = 85) -> list[str]:
  """Deterministic disagreement signals for one pair.

  Args:
    a: first claim, from _prepared.
    b: second claim, from _prepared.
    ratio: their text similarity.
    subject_ratio: subject similarity that counts as the same subject within one topic.

  Returns:
    Signal names, sorted.
  """
  out = []
  same_subject = norm_cached(a["subject"]) == norm_cached(b["subject"])
  same_key = same_subject and norm_cached(a["predicate"]) == norm_cached(b["predicate"])
  overlap = _overlaps(a["situation"], b["situation"])
  differ = norm_cached(a["object"]) != norm_cached(b["object"])
  many = a["multi"] and b["multi"]
  if same_key and overlap and differ and not many:
    out.append("same-key-different-object")
  if same_key and not overlap and not many:
    out.append("same-key-different-scope")
  if not same_key and not many and overlap and differ and a["topic_key"] == b["topic_key"] and not a["sources"] & b["sources"]:
    if same_subject or _shared_subject(a, b, subject_ratio):
      out.append("same-topic-cross-source")
  if not (same_key or ratio >= 70):
    return sorted(out)
  if a["numbers"] and b["numbers"] and a["numbers"] != b["numbers"]:
    out.append("numeric-mismatch")
  if a["negated"] != b["negated"]:
    out.append("negation-asymmetry")
  if a["kind"] != b["kind"] and {a["kind"], b["kind"]} & {"proposal", "observed", "decision"}:
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
  shared = source_ids(ca) & source_ids(cb)
  return {
    "claims": [a, b],
    "texts": [ca["claim_text"], cb["claim_text"]],
    "kinds": [ca["kind"], cb["kind"]],
    "scopes": [ca["scope"], cb["scope"]],
    "dispositions": [st.disposition(a), st.disposition(b)],
    "sources": [sorted({e["path"] for e in ca["evidence"]}), sorted({e["path"] for e in cb["evidence"]})],
    "same_source_bytes": bool(shared),
    "cross_source": not shared,
    "similarity": ratio,
    "signals": sig,
  }


def _suppressed(a: dict, b: dict, sig: list[str]) -> bool:
  """Whether a same-source pair is a parallel enumeration, not a disagreement (P2).

  Args:
    a: first claim, from _prepared.
    b: second claim, from _prepared.
    sig: its signals.

  Returns:
    True when the pair shares a source, the subjects differ and no negation signal fired.
  """
  return bool(a["sources"] & b["sources"]) and norm_cached(a["subject"]) != norm_cached(b["subject"]) and "negation-asymmetry" not in sig


def pairs(st: State, limit: int | None = None) -> dict:
  """Candidate pairs not yet classified.

  Args:
    st: current state.
    limit: return only the top pairs; counts still cover them all.

  Returns:
    {"pairs": [...], "nli": bool, "compared": n, "counts": {...}}; cross-source pairs with a signal first, then by similarity.
  """
  cfg = st.cfg["candidates"]
  multi = multi_valued(st)
  active = {cid: _prepared(c, st.cfg["project_id"], multi) for cid, c in st.claims.items() if st.disposition(cid) not in ("DUPLICATE", "REJECTED")}
  done = classified(st)
  by_subject: dict[str, set[str]] = {}
  by_topic: dict[str, set[str]] = {}
  for cid, c in active.items():
    by_subject.setdefault(ids.norm(c["subject"]), set()).add(cid)
    by_topic.setdefault(c["topic_key"], set()).add(cid)
  neighbours = _fts_neighbours(active, cfg)
  seen, rows, suppressed = set(), [], 0
  for a in sorted(active):
    for b in sorted(neighbours[a] | by_subject[ids.norm(active[a]["subject"])] | by_topic[active[a]["topic_key"]]):
      key = frozenset((a, b))
      if a == b or key in seen or key in done:
        continue
      seen.add(key)
      x, y = sorted((a, b))
      ratio = fuzzy.similarity(active[x]["claim_text"], active[y]["claim_text"])
      sig = signals(active[x], active[y], ratio, cfg["subject_ratio"])
      if sig and _suppressed(active[x], active[y], sig):
        suppressed += 1
      elif sig or ratio >= cfg["min_ratio"]:
        rows.append(_pair_row(st, x, y, ratio, sig))
  scores = nli.contradiction_scores([(r["texts"][0], r["texts"][1]) for r in rows])
  for row, score in zip(rows, scores or [], strict=False):
    row["nli_contradiction"] = score
  rows.sort(key=lambda r: (0 if r["signals"] else 1, 0 if r["cross_source"] else 1, -r["similarity"], r["claims"]))
  cross = sum(r["cross_source"] for r in rows)
  counts = {"cross_source": cross, "same_source": len(rows) - cross, "suppressed_same_source": suppressed}
  return {"pairs": rows[:limit], "nli": scores is not None, "compared": len(seen), "counts": counts}


def multi_valued(st: State) -> set[str]:
  """Normalised multi-valued predicates for a project.

  Args:
    st: current state.

  Returns:
    The predicates.
  """
  return {norm_cached(p) for p in st.cfg["candidates"]["multi_valued_predicates"]}


def classified(st: State) -> set[frozenset]:
  """Pairs already reviewed, by a relation or by a group review.

  Args:
    st: current state.

  Returns:
    Each pair as a frozenset of two claim IDs.
  """
  done = set()
  for rec in st.relations.values():
    done.update(frozenset(pair) for pair in combinations(rec["claims"], 2))
  return done
