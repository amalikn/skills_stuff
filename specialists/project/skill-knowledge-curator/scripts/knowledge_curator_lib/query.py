"""Agent and human retrieval: full-text search over claims, answering with disposition, open conflicts and source lines (INV-013).

Imported, not run. Historical and superseded claims are returned marked as such, never as current guidance; an open conflict is
named so an answer can say the matter is not settled (design doc 7.9). Safety: in-memory database; reads state only.
"""

import re
import sqlite3

from .state import State

_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]+")


def search(st: State, text: str, limit: int = 10, include_history: bool = False) -> list[dict]:
  """Claims matching a query, best first.

  Args:
    st: current state.
    text: free text.
    limit: maximum results.
    include_history: also return SUPERSEDED, HISTORICAL, DUPLICATE and REJECTED claims.

  Returns:
    Result rows with claim, effective disposition, conflicts, page and evidence.
  """
  tokens = _TOKEN.findall(text)
  if not tokens or not st.claims:
    return []
  db = sqlite3.connect(":memory:")
  db.execute("CREATE VIRTUAL TABLE f USING fts5(cid UNINDEXED, body)")
  db.executemany(
    "INSERT INTO f VALUES (?, ?)",
    [(cid, " ".join([c["subject"], c["claim_text"], c["topic_key"], *c["labels"], *c["subcategories"]])) for cid, c in st.claims.items()],
  )
  query = " OR ".join('"' + t + '"' for t in tokens)
  rows = db.execute("SELECT cid FROM f WHERE f MATCH ? ORDER BY rank", (query,)).fetchall()
  db.close()
  out = []
  for (cid,) in rows:
    disp = st.effective(cid)
    if not include_history and disp in ("SUPERSEDED", "HISTORICAL", "DUPLICATE", "REJECTED"):
      continue
    c = st.claims[cid]
    out.append(
      {
        "claim_id": cid,
        "text": c["claim_text"],
        "disposition": disp,
        "settled": disp == "CURRENT",
        "conflicts": [{"conflict_id": cf["conflict_id"], "severity": cf["severity"], "question": cf["question"]} for cf in st.open_conflicts(cid)],
        "page": f"{st.cfg['knowledge_dir']}/{c['primary_category']}.md",
        "evidence": [f"{e['path']}:{e['line_start']}-{e['line_end']}" for e in c["evidence"]],
        "successor": (st.dispositions.get(cid) or {}).get("successor"),
      }
    )
    if len(out) >= limit:
      break
  return out
