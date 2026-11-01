"""Decision points: claims on one key across sources, the review unit that replaces raw pairs (evaluation.md P13, P25).

Imported, not run. Also serves the per-claim unreviewed counts for query, validate and render, and records a group reviewed whole.
Counts unclassified pairs, not disagreements: a review prompt, never a dispute count. Safety: reads state only.
"""

from collections import Counter
from itertools import combinations

from . import ids
from .candidates import classified, multi_valued, norm_cached, situation, source_ids
from .errors import InputError
from .state import State


def _group_id(key: tuple) -> str:
  """Stable ID of a decision point.

  Args:
    key: (subject, predicate, where).

  Returns:
    "dp-" plus 12 hex digits.
  """
  return ids.make_id("dp", key[0], key[1], list(key[2]))


def _key_groups(st: State) -> dict[tuple, list[str]]:
  """Live claims grouped by subject, predicate and where.

  Args:
    st: current state.

  Returns:
    (subject, predicate, where) -> claim IDs.
  """
  groups: dict[tuple, list[str]] = {}
  multi = multi_valued(st)
  for cid in sorted(st.claims):
    c = st.claims[cid]
    if st.disposition(cid) in ("CURRENT", "REVIEW_REQUIRED") and norm_cached(c["predicate"]) not in multi:
      where = tuple(sorted((k.lower(), str(v).lower()) for k, v in situation(c["scope"]).items()))
      groups.setdefault((norm_cached(c["subject"]), norm_cached(c["predicate"]), where), []).append(cid)
  return groups


def _open_pairs(st: State, members: list[str], done: set) -> list[tuple[str, str]]:
  """Unclassified pairs in a group that disagree across sources.

  Args:
    st: current state.
    members: claim IDs.
    done: classified pairs.

  Returns:
    The pairs.
  """
  out = []
  for a, b in combinations(members, 2):
    ca, cb = st.claims[a], st.claims[b]
    if frozenset((a, b)) not in done and norm_cached(ca["object"]) != norm_cached(cb["object"]) and not source_ids(ca) & source_ids(cb):
      out.append((a, b))
  return out


def decision_points(st: State) -> dict:
  """Reviewable groups: one subject and predicate across two or more sources with differing objects and unclassified pairs (P13).

  Args:
    st: current state.

  Returns:
    {"groups": [...], "claims": n}; the groups with the most sources first.
  """
  done = classified(st)
  groups = []
  for (subject, predicate, where), members in _key_groups(st).items():
    remaining = _open_pairs(st, members, done)
    if remaining:
      rows = [{"claim_id": c, "object": st.claims[c]["object"], "paths": sorted({e["path"] for e in st.claims[c]["evidence"]})} for c in members]
      sources = len({s for c in members for s in source_ids(st.claims[c])})
      gid = _group_id((subject, predicate, where))
      groups.append(
        {
          "group_id": gid,
          "subject": subject,
          "predicate": predicate,
          "scope": dict(where),
          "sources": sources,
          "unclassified_pairs": len(remaining),
          "claims": rows,
        }
      )
  groups.sort(key=lambda g: (-g["sources"], -g["unclassified_pairs"], g["subject"], g["predicate"]))
  return {"groups": groups, "claims": len({c["claim_id"] for g in groups for c in g["claims"]})}


def group_review(st: State, group_id: str, reason: str) -> dict:
  """Record a decision point as reviewed whole, for a coordinator who reads by topic: a later claim reopens only its own pairs (P25).

  Args:
    st: current state.
    group_id: from decision_points.
    reason: what the review found.

  Returns:
    A record for relations.jsonl.

  Raises:
    InputError: unknown group or empty reason.
  """
  if not reason or not reason.strip():
    raise InputError("--reason is required")
  done = classified(st)
  for key, members in _key_groups(st).items():
    if _group_id(key) == group_id and _open_pairs(st, members, done):
      rel = ids.make_id("grp", group_id, members)
      return {"record": "group_review", "relation_id": rel, "relation": "group-reviewed", "group_id": group_id, "claims": members, "reason": reason}
  raise InputError(f"unknown or already reviewed group {group_id}")


def unreviewed_counts(st: State) -> dict[str, int]:
  """Per-claim count of unclassified cross-source disagreements on the same key; cheap enough for query and validate (P3).

  Args:
    st: current state.

  Returns:
    claim_id -> count (claims with none are absent).
  """
  done = classified(st)
  return dict(Counter(c for members in _key_groups(st).values() for pair in _open_pairs(st, members, done) for c in pair))
