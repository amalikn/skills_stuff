"""Fold a project's append-only ledgers into the current state the feature modules read.

Imported, not run. Later records win per ID, so history stays in the files and the state is always rebuildable (INV-004, INV-016).
A claim's disposition is the last disposition event for it; the effective disposition also honours open blocking conflicts
(INV-006). Safety: reads .kc/*.jsonl only.
"""

from dataclasses import dataclass, field
from pathlib import Path

from . import ledger, settings


@dataclass
class State:
  """Current view of one project's ledgers.

  Attributes:
    root: project root.
    cfg: project config.
    sources: source_id -> latest source_version record (removed sources carry ingestion_state "removed").
    versions: source_version_id -> source_version record.
    sections: section_id -> latest section record.
    section_status: section_id -> latest section_status record.
    claims: claim_id -> latest claim version.
    dispositions: claim_id -> latest disposition event.
    relations: relation_id -> relation record.
    conflicts: conflict_id -> latest conflict event.
    decisions: decision records in order.
    promotions: page path -> latest promotion record.
  """

  root: Path
  cfg: dict
  sources: dict = field(default_factory=dict)
  versions: dict = field(default_factory=dict)
  sections: dict = field(default_factory=dict)
  section_status: dict = field(default_factory=dict)
  claims: dict = field(default_factory=dict)
  dispositions: dict = field(default_factory=dict)
  relations: dict = field(default_factory=dict)
  conflicts: dict = field(default_factory=dict)
  decisions: list = field(default_factory=list)
  promotions: dict = field(default_factory=dict)

  def source_by_path(self) -> dict:
    """Live (not removed) sources keyed by project-relative path.

    Returns:
      path -> latest source_version record.
    """
    return {s["path"]: s for s in self.sources.values() if s.get("ingestion_state") != "removed"}

  def disposition(self, claim_id: str) -> str:
    """Recorded disposition of a claim.

    Args:
      claim_id: the claim.

    Returns:
      The last disposition event's value, or REVIEW_REQUIRED when none exists.
    """
    event = self.dispositions.get(claim_id)
    return event["disposition"] if event else "REVIEW_REQUIRED"

  def open_conflicts(self, claim_id: str | None = None) -> list[dict]:
    """Open conflicts, optionally only those involving one claim.

    Args:
      claim_id: restrict to conflicts naming this claim.

    Returns:
      Conflict records with status "open", sorted by severity then ID.
    """
    found = [c for c in self.conflicts.values() if c["status"] == "open" and (claim_id is None or claim_id in c["claims"])]
    return sorted(found, key=lambda c: (c["severity"], c["conflict_id"]))

  def effective(self, claim_id: str) -> str:
    """Disposition used for publishing: CURRENT drops to REVIEW_REQUIRED while a P0/P1 conflict on the claim is open.

    Args:
      claim_id: the claim.

    Returns:
      The effective disposition.
    """
    disp = self.disposition(claim_id)
    if disp == "CURRENT" and any(c["severity"] in settings.BLOCKING_SEVERITIES for c in self.open_conflicts(claim_id)):
      return "REVIEW_REQUIRED"
    return disp


def _fold_sources(st: State, records: list[dict]) -> None:
  """Apply sources.jsonl records.

  Args:
    st: state being built.
    records: ledger records in order.
  """
  for rec in records:
    if rec["record"] == "source_version":
      st.versions[rec["source_version_id"]] = rec
      st.sources[rec["source_id"]] = rec
    elif rec["record"] == "source_removed" and rec["source_id"] in st.sources:
      st.sources[rec["source_id"]] = {**st.sources[rec["source_id"]], "ingestion_state": "removed"}


def _fold_claims(st: State, records: list[dict]) -> None:
  """Apply claims.jsonl records (claim versions, disposition events, section statuses).

  Args:
    st: state being built.
    records: ledger records in order.
  """
  for rec in records:
    kind = rec["record"]
    if kind == "claim":
      st.claims[rec["claim_id"]] = rec
    elif kind == "disposition":
      st.dispositions[rec["claim_id"]] = rec
    elif kind == "section_status":
      st.section_status[rec["section_id"]] = rec


def load(root: Path, cfg: dict | None = None) -> State:
  """Read and fold every ledger of a project.

  Args:
    root: project root.
    cfg: config already loaded (loaded from .kc/config.yaml when None).

  Returns:
    The folded state.
  """
  st = State(root=root, cfg=cfg or settings.load_config(root))
  read = {name: ledger.read_jsonl(settings.ledger_path(root, name)) for name in settings.LEDGERS}
  _fold_sources(st, read["sources"])
  for rec in read["sections"]:
    st.sections[rec["section_id"]] = rec
  _fold_claims(st, read["claims"])
  for rec in read["relations"]:
    st.relations[rec["relation_id"]] = rec
  for rec in read["conflicts"]:
    st.conflicts[rec["conflict_id"]] = rec
  for rec in read["decisions"]:
    if rec["record"] == "promotion":
      st.promotions[rec["page"]] = rec
    else:
      st.decisions.append(rec)
  return st
