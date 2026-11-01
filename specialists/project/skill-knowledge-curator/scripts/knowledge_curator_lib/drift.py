"""Claim drift: claim text checked against its own excerpts, because a verified quote does not prove the paraphrase (evaluation.md P18).

Imported, not run. Deterministic and advisory: it flags, never refuses, since a paraphrase can be right. It compares numbers, negation
and names, the things a lossy rewrite changes, and it reads the cited lines. Safety: pure functions over claims.
"""

import fnmatch
import re

from .evidence import Reader, cited_text
from .state import State

_NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)*")
_NEG = re.compile(r"\b(not|no|never|without|cannot|must not|neither|nor)\b|n't\b", re.IGNORECASE)
_NAME = re.compile(r"(?<=[a-z0-9,;:)] )[A-Z][A-Za-z0-9+#-]{2,}")


def findings(claim: dict, cited: str) -> list[str]:
  """What a claim's text says that its source does not.

  Numbers and names are checked against the whole cited lines, since an excerpt is only a short quote from them; the subject is the
  claim's own label. A dropped negation is checked against the excerpt, because that is the sentence the claim restates.

  Args:
    claim: a claim with evidence records.
    cited: text of its cited lines.

  Returns:
    Findings, empty when the text is faithful or there is no evidence to compare (an operator claim).
  """
  if not claim["evidence"]:
    return []
  text, excerpts = claim["claim_text"], " ".join(e["excerpt"] for e in claim["evidence"])
  source = f"{cited} {excerpts}"
  known = f"{source} {claim['subject']}".lower()
  out = [f"number {n} is not in the cited lines" for n in sorted(set(_NUM.findall(text)) - set(_NUM.findall(source)))]
  if _NEG.search(excerpts) and not _NEG.search(text):
    out.append("negation in the excerpt is missing from the text")
  out.extend(f"name {n} is not in the cited lines" for n in sorted({n for n in _NAME.findall(text) if n.lower() not in known}))
  return out


def check_claim(reader: Reader, claim: dict) -> list[str]:
  """Findings for one stored or pending claim.

  Args:
    reader: file reader.
    claim: a claim with evidence records.

  Returns:
    Findings.
  """
  return findings(claim, " ".join(cited_text(reader, _span(e), None) for e in claim["evidence"]))


def _span(ev: dict) -> dict:
  """Evidence record as a span for cited_text.

  Args:
    ev: evidence record.

  Returns:
    {source_path, line_start, line_end}.
  """
  return {"source_path": ev["path"], "line_start": ev["line_start"], "line_end": ev["line_end"]}


def report(st: State, path: str | None = None) -> dict:
  """Live claims whose text drifts from their excerpts.

  Args:
    st: current state.
    path: glob limiting the claims to those citing a matching file.

  Returns:
    {"claims": [{claim_id, text, paths, findings}], "counts": {"checked", "flagged"}}.
  """
  rows, checked, reader = [], 0, Reader(st)
  for cid, c in sorted(st.claims.items()):
    paths = sorted({e["path"] for e in c["evidence"]})
    if st.disposition(cid) in ("DUPLICATE", "REJECTED") or (path and not any(fnmatch.fnmatchcase(p, path) for p in paths)):
      continue
    checked += 1
    found = check_claim(reader, c)
    if found:
      rows.append({"claim_id": cid, "text": c["claim_text"], "paths": paths, "findings": found})
  return {"claims": rows, "counts": {"checked": checked, "flagged": len(rows)}}
