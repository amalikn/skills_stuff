"""Root-cause grouping (research B3, `kc roots`): one finding per cause, so a person reads a shared cause once.

Imported, not run. A conflict's cause tokens are identifiers (paths, names with a hyphen, dot, underscore or digit) that both claims
name, or that the conflict's question or topic names and one claim does. Tokens on many live claims, and document names, say nothing about
a cause and are dropped. Each conflict joins the group of its most widely shared token (no chaining, so one bridging conflict cannot
merge two causes); a conflict with no token stands alone, with a `near` hint when it shares a claim with a group. Grouping never changes a status:
deciding a group means one explicit `kc decide` per member, which the group lists. Safety: read-only.
"""

import re
from collections import Counter

from . import ids
from .state import State

_WORD = re.compile(r"[A-Za-z0-9_./-]*[A-Za-z0-9]")
_MARK = re.compile(r"[-_./0-9]")
_NUMBER = re.compile(r"[\d.]+")
_STEM_HEAD = re.compile(r"^([a-z]+\d+)[-_]")


def tokens(text: str, min_len: int) -> set[str]:
  """Identifier-like tokens of a text: whole paths and their segments.

  Args:
    text: any text.
    min_len: shortest token kept.

  Returns:
    Lower-case tokens that hold a hyphen, dot, underscore, slash or digit and are not bare numbers.
  """
  out = set()
  for raw in _WORD.findall(text):
    word = raw.lower().strip("./")
    parts = [p for p in word.split("/") if p]
    for part in parts + ([word] if len(parts) > 1 else []):
      if len(part) >= min_len and _MARK.search(part) and not _NUMBER.fullmatch(part):
        out.add(part)
  return out


def _document_names(st: State) -> set[str]:
  """Tokens that only name a source document (file stem, its numbered head such as step12), never a cause.

  Args:
    st: current state.

  Returns:
    Lower-case names.
  """
  names = set()
  for path in st.source_by_path():
    stem = path.rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
    names |= {stem, path.lower(), path.rsplit("/", 1)[-1].lower()}
    head = _STEM_HEAD.match(stem)
    if head:
      names.add(head.group(1))
  return names


def _claim_tokens(st: State, min_len: int) -> dict[str, set[str]]:
  """Tokens per claim, from subject, object and text.

  Args:
    st: current state.
    min_len: shortest token kept.

  Returns:
    claim_id -> tokens.
  """
  return {cid: tokens(" ".join((c["subject"], c["object"], c["claim_text"])), min_len) for cid, c in st.claims.items()}


def cause_tokens(st: State, conflicts: list[dict]) -> dict[str, set[str]]:
  """Rare identifiers each conflict is about.

  Args:
    st: current state.
    conflicts: conflict records.

  Returns:
    conflict_id -> tokens.
  """
  cfg = st.cfg["roots"]
  per_claim = _claim_tokens(st, cfg["min_token_len"])
  live = [c for c in st.claims if st.disposition(c) in ("CURRENT", "REVIEW_REQUIRED")]
  df = Counter(t for c in live for t in per_claim[c])
  cap = max(cfg["token_floor"], cfg["max_token_share"] * len(live))
  docs = _document_names(st)
  out = {}
  for cf in conflicts:
    sides = [per_claim[c] for c in cf["claims"] if c in per_claim]
    both = set.intersection(*sides) if sides else set()
    named = tokens(cf.get("question", "") + " " + cf["topic_key"].replace(".", " "), cfg["min_token_len"]) & set().union(*sides)
    out[cf["conflict_id"]] = {t for t in both | named if df[t] <= cap and t not in docs}
  return out


def _decide_lines(cf: dict, token: str | None) -> list[str]:
  """The explicit per-member commands a group decision expands to.

  Args:
    cf: member conflict.
    token: the group's cause token.

  Returns:
    Command lines, one per action a person may choose.
  """
  cid, why = cf["conflict_id"], f"root {token}: ..." if token else "..."
  first = f"kc decide --project <dir> {cid} ACCEPT_RECOMMENDATION --reason '{why}'" if cf.get("recommended_current") else None
  rest = [f"kc decide --project <dir> {cid} USE_OTHER --current <claim> --reason '{why}'", f"kc decide --project <dir> {cid} DEFER --reason '{why}'"]
  return ([first] if first else []) + rest


def group(st: State, conflicts: list[dict] | None = None) -> dict:
  """Group conflicts by cause.

  Args:
    st: current state.
    conflicts: conflicts to group (open ones when None).

  Returns:
    {"groups": [...], "counts": {...}}; groups sorted by worst severity, then size.
  """
  conflicts = st.open_conflicts() if conflicts is None else conflicts
  keys = cause_tokens(st, conflicts)
  spread = Counter(t for ts in keys.values() for t in ts)
  home: dict[str, str] = {}
  for cid, ts in keys.items():
    if ts:
      home[cid] = max(ts, key=lambda t: (spread[t], -len(t), t))
  claim_home: dict[str, str] = {}
  for cf in conflicts:
    if cf["conflict_id"] in home:
      for claim in cf["claims"]:
        claim_home.setdefault(claim, home[cf["conflict_id"]])
  members: dict[tuple, list[dict]] = {}
  near: dict[str, str] = {}
  for cf in conflicts:
    cid = cf["conflict_id"]
    if cid in home:
      members.setdefault(("identifier", home[cid]), []).append(cf)
      continue
    # A shared claim is only a hint: on the MCP pilot 6 of 8 conflicts joined that way had another cause (evaluation.md, kc roots).
    via = next((claim_home[c] for c in cf["claims"] if c in claim_home), None)
    if via:
      near[cid] = via
    members.setdefault(("none", cid), []).append(cf)
  groups = [_group_row(key, rows, keys) | ({"near": near[key[1]]} if key[1] in near else {}) for key, rows in members.items()]
  groups.sort(key=lambda g: (g["severity"], -g["size"], g["root_id"]))
  sizes = [g["size"] for g in groups]
  counts = {"conflicts": len(conflicts), "groups": len(groups), "singletons": sizes.count(1), "largest": max(sizes, default=0)}
  return {"groups": groups, "counts": counts}


def _group_row(key: tuple, rows: list[dict], keys: dict[str, set[str]]) -> dict:
  """One group's record.

  Args:
    key: (basis, token or conflict ID).
    rows: member conflicts.
    keys: cause tokens per conflict.

  Returns:
    {root_id, basis, token, shared_tokens, size, severity, representative, members, member_tokens, decide}.
  """
  rows = sorted(rows, key=lambda c: (c["severity"], c["conflict_id"]))
  token = key[1] if key[0] == "identifier" else None
  shared = Counter(t for c in rows for t in keys.get(c["conflict_id"], ()))
  rep = rows[0]
  basis = key[0]
  return {
    "root_id": ids.make_id("rt", token or rep["conflict_id"], sorted(c["conflict_id"] for c in rows)),
    "basis": basis,
    "token": token,
    "shared_tokens": [t for t, _ in shared.most_common(4)],
    "size": len(rows),
    "severity": rep["severity"],
    "representative": {"conflict_id": rep["conflict_id"], "question": rep.get("question"), "claims": rep["claims"]},
    "members": [c["conflict_id"] for c in rows],
    "member_tokens": {c["conflict_id"]: sorted(keys.get(c["conflict_id"], ())) for c in rows},
    "decide": {c["conflict_id"]: _decide_lines(c, token) for c in rows},
  }


def index(st: State) -> dict[str, dict]:
  """Group of each open conflict, for the review queue and verify batches.

  Args:
    st: current state.

  Returns:
    conflict_id -> {"root_id", "token", "size"}.
  """
  out = {}
  for g in group(st)["groups"]:
    for cid in g["members"]:
      out[cid] = {"root_id": g["root_id"], "token": g["token"], "size": g["size"]}
  return out
