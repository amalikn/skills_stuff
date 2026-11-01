"""Consolidation aliases: two wordings of one thing, joined for comparison only (evaluation.md P28).

Imported, not run. Agents working apart word subjects, predicates and topics differently, so a consolidation agent records which terms
mean the same. Claims and their IDs never change: aliases apply when comparing, are append-only, and a later record revokes one.
Safety: returns records for ledger.append.
"""

from dataclasses import dataclass, field

from . import ids, schema
from .state import State


@dataclass
class AliasResult:
  """Records produced from one aliases input file.

  Attributes:
    aliases: alias records.
    errors: messages; non-empty means nothing may be appended.
  """

  aliases: list = field(default_factory=list)
  errors: list = field(default_factory=list)


def _known_terms(st: State, name: str) -> set[str]:
  """Terms in use for one field.

  Args:
    st: current state.
    name: field name.

  Returns:
    Normalised terms.
  """
  return {ids.norm(c[name]) for c in st.claims.values()}


def ingest(st: State, records: list[dict]) -> AliasResult:
  """Validate one batch of aliases: no self alias, no unknown term, no chain, in the ledger or the batch.

  Args:
    st: current state.
    records: alias inputs.

  Returns:
    The result (check errors before appending anything).
  """
  res = AliasResult()
  live = {name: dict(terms) for name, terms in st.aliases.items()}
  for n, rec in enumerate(records, 1):
    problems = schema.record_errors(rec) if isinstance(rec, dict) and rec.get("record") == "alias" else ["record: expected 'alias'"]
    if problems:
      res.errors.extend(f"#{n}: {p}" for p in problems)
      continue
    name, term, canon = rec["field"], ids.norm(rec["term"]), ids.norm(rec["canonical"])
    terms = live.setdefault(name, {})
    if rec.get("revoked"):
      terms.pop(term, None)
    elif term == canon:
      res.errors.append(f"#{n}: {term!r} cannot alias itself")
    elif term not in _known_terms(st, name):
      res.errors.append(f"#{n}: {name} {term!r} is not in the ledger")
    elif canon in terms or term in terms.values():
      res.errors.append(f"#{n}: {term!r} -> {canon!r} would chain aliases; point every term at one canonical form")
    else:
      terms[term] = canon
    out = {**rec, "term": term, "canonical": canon, "revoked": bool(rec.get("revoked"))}
    res.aliases.append({**out, "alias_id": ids.make_id("al", name, term, canon, out["revoked"])})
  return res
