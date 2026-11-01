"""Decision points: claims on one key across sources, the review unit that replaces raw pairs (evaluation.md P13, P25).

Imported, not run. Also serves the per-claim unreviewed counts for query, validate and render, and records a group reviewed whole.
Counts unclassified pairs, not disagreements: a review prompt, never a dispute count. Safety: reads state only.
"""

import re
from collections import Counter
from itertools import combinations

from . import ids
from .candidates import classified, compared, multi_valued, norm_cached, overlaps, situation, source_ids
from .errors import InputError
from .state import State

_WORD = re.compile(r"[a-z0-9]{4,}")


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
    c = compared(st, st.claims[cid])
    if st.disposition(cid) in ("CURRENT", "REVIEW_REQUIRED") and norm_cached(c["predicate"]) not in multi:
      where = tuple(sorted((k.lower(), str(v).lower()) for k, v in situation(c["scope"]).items()))
      groups.setdefault((norm_cached(c["subject"]), norm_cached(c["predicate"]), where), []).append(cid)
  return groups


def _word_groups(st: State) -> dict[str, list[str]]:
  """Live claims grouped by a rare subject word: the blocking that survives agents who share no topic or predicate wording (P28).

  Args:
    st: current state.

  Returns:
    word -> claim IDs, for words within the rarity limit. Claims on multi-valued predicates stay out.
  """
  cfg, multi = st.cfg["candidates"], multi_valued(st)
  live = {c: compared(st, x) for c, x in st.claims.items() if st.disposition(c) in ("CURRENT", "REVIEW_REQUIRED")}
  project = set(_WORD.findall(norm_cached(st.cfg["project_id"])))
  groups: dict[str, list[str]] = {}
  for cid in sorted(live):
    if norm_cached(live[cid]["predicate"]) not in multi:
      for word in sorted(set(_WORD.findall(norm_cached(live[cid]["subject"]))) - project):
        groups.setdefault(word, []).append(cid)
  limit = max(cfg["subject_word_floor"], len(live) * cfg["subject_word_share"])
  return {w: members for w, members in groups.items() if len(members) <= limit}


def _word_pairs(st: State, members: list[str], done: set) -> list[tuple[str, str]]:
  """Open pairs in a word group: overlapping situations, and not already on one key (those are in a key group).

  Args:
    st: current state.
    members: claim IDs.
    done: classified pairs.

  Returns:
    The pairs.
  """
  out = []
  for a, b in _open_pairs(st, members, done):
    ca, cb = compared(st, st.claims[a]), compared(st, st.claims[b])
    same_key = norm_cached(ca["subject"]) == norm_cached(cb["subject"]) and norm_cached(ca["predicate"]) == norm_cached(cb["predicate"])
    if not same_key and overlaps(situation(ca["scope"]), situation(cb["scope"])):
      out.append((a, b))
  return out


def _claim_rows(st: State, members: list[str]) -> list[dict]:
  """Group members as output rows.

  Args:
    st: current state.
    members: claim IDs.

  Returns:
    Rows with subject, object and paths.
  """
  return [
    {"claim_id": c, "subject": st.claims[c]["subject"], "object": st.claims[c]["object"], "paths": sorted({e["path"] for e in st.claims[c]["evidence"]})}
    for c in members
  ]


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
    {"groups": [...], "word_groups": [...], "claims": n}; most sources first. Word groups span topics and are a prompt to read, weaker than key
    groups: they share a word, not a question.
  """
  done = classified(st)
  groups = []
  for (subject, predicate, where), members in _key_groups(st).items():
    remaining = _open_pairs(st, members, done)
    if remaining:
      rows = _claim_rows(st, members)
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
  words = []
  for word, members in _word_groups(st).items():
    remaining = _word_pairs(st, members, done)
    if remaining:
      sources = len({s for c in members for s in source_ids(st.claims[c])})
      gid = ids.make_id("dp", "word", word)
      words.append({"group_id": gid, "word": word, "sources": sources, "unclassified_pairs": len(remaining), "claims": _claim_rows(st, members)})
  words.sort(key=lambda g: (-g["sources"], -g["unclassified_pairs"], g["word"]))
  return {"groups": groups, "word_groups": words, "claims": len({c["claim_id"] for g in groups for c in g["claims"]})}


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
  found = [m for key, m in _key_groups(st).items() if _group_id(key) == group_id and _open_pairs(st, m, done)]
  found += [m for w, m in _word_groups(st).items() if ids.make_id("dp", "word", w) == group_id and _word_pairs(st, m, done)]
  if found:
    rel = ids.make_id("grp", group_id, found[0])
    return {"record": "group_review", "relation_id": rel, "relation": "group-reviewed", "group_id": group_id, "claims": found[0], "reason": reason}
  raise InputError(f"unknown or already reviewed group {group_id}")


def _byte_copies(st: State, claim: dict) -> list[str]:
  """Cited paths that repeat another cited file's bytes: the shortest path is kept, so a view cites one file per byte group (P32).

  Args:
    st: current state.
    claim: the claim.

  Returns:
    The repeating paths, sorted.
  """
  groups: dict[str, set[str]] = {}
  for ev in claim["evidence"]:
    groups.setdefault(ev["source_sha256"], set()).add(ev["path"])
  return sorted(p for paths in groups.values() for p in paths if p != min(paths, key=lambda x: (len(x), x)))


def topics(st: State) -> dict:
  """Claims by consolidated topic, for the relate agent: same-source and historical claims included, since conflicts live there too.

  Args:
    st: current state.

  Returns:
    {"topics": {topic: [rows]}, "claims": n}.
  """
  out: dict[str, list[dict]] = {}
  for cid, c in sorted(st.claims.items()):
    disp = st.disposition(cid)
    if disp not in ("DUPLICATE", "REJECTED"):
      view = compared(st, c)
      copies = _byte_copies(st, c)
      lines = sorted({f"{e['path']}:{e['line_start']}-{e['line_end']}" for e in c["evidence"] if e["path"] not in copies})
      row = {"claim_id": cid, "subject": view["subject"], "predicate": view["predicate"], "text": c["claim_text"]}
      out.setdefault(view["topic_key"], []).append(row | {"disposition": disp, "kind": c["kind"], "lines": lines, "byte_copies": copies})
  return {"topics": dict(sorted(out.items())), "claims": sum(len(v) for v in out.values())}


def by_file(st: State) -> dict:
  """Claims under each file they cite, in line order, for reading one document against itself (P29).

  Args:
    st: current state.

  Returns:
    {"files": {path: [rows]}}.
  """
  first: dict[str, dict[str, tuple[int, dict]]] = {}
  for rows in topics(st)["topics"].values():
    for row in rows:
      for ev in st.claims[row["claim_id"]]["evidence"]:
        seen = first.setdefault(ev["path"], {})
        if row["claim_id"] not in seen or ev["line_start"] < seen[row["claim_id"]][0]:
          seen[row["claim_id"]] = (ev["line_start"], row)
  return {"files": {path: [r for _, r in sorted(rows.values(), key=lambda x: (x[0], x[1]["claim_id"]))] for path, rows in sorted(first.items())}}


def review_pairs(st: State) -> set[frozenset]:
  """Every pair a decision point puts in front of a reviewer, key and word groups alike.

  Args:
    st: current state.

  Returns:
    Pairs as frozensets of two claim IDs.
  """
  done = classified(st)
  found = {frozenset(p) for members in _key_groups(st).values() for p in _open_pairs(st, members, done)}
  return found | {frozenset(p) for members in _word_groups(st).values() for p in _word_pairs(st, members, done)}


def unreviewed_counts(st: State) -> dict[str, int]:
  """Per-claim count of unclassified cross-source disagreements on the same key; cheap enough for query and validate (P3).

  Args:
    st: current state.

  Returns:
    claim_id -> count (claims with none are absent).
  """
  done = classified(st)
  return dict(Counter(c for members in _key_groups(st).values() for pair in _open_pairs(st, members, done) for c in pair))
