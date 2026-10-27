"""The MVP contract record: criteria, exclusions, necessary blockers and approval, parsed from .gg/mvp.yaml.

Imported, not run. Field names follow references/mvp-contract-and-change-control.md (Contract fields). Consumers: project, decide,
rank, trace, excel.
"""

from dataclasses import dataclass

from .errors import RecordError
from .records import text_field

MVP_STATUSES = ("draft", "approved", "delivered", "superseded")
# Words the contract rejects as subjective acceptance criteria (references/mvp-contract-and-change-control.md, Contract fields).
SUBJECTIVE = ("enterprise ready", "enterprise-ready", "scalable", "bulletproof", "world-class", "best-in-class", "future-proof")
WHERE = "mvp.yaml"


@dataclass(frozen=True)
class Criterion:
  """One acceptance criterion.

  Args:
    id: stable criterion ID, e.g. AC-01.
    test: observable pass/fail condition.
    evidence_required: what proves it.
  """

  id: str
  test: str
  evidence_required: str


@dataclass(frozen=True)
class Exclusion:
  """A feature consciously deferred; matching work is BLOCK (decision rule 4).

  Args:
    id: exclusion ID, or its text when the contract gives a bare string.
    text: what is excluded.
    keywords: lower-case phrases that identify it in a proposal.
  """

  id: str
  text: str
  keywords: tuple[str, ...]


@dataclass(frozen=True)
class Blocker:
  """A dependency already judged necessary in the approved baseline.

  Args:
    id: blocker ID.
    unblocks: the criterion ID it unblocks.
    description: what it is.
  """

  id: str
  unblocks: str
  description: str


@dataclass(frozen=True)
class Mvp:
  """The MVP contract of one project.

  Args:
    mvp_id: contract ID, e.g. UNC-MVP-001.
    baseline_version: revision number, from 1.
    status: draft, approved, delivered or superseded.
    owner: the human owner.
    outcome: the one observable outcome.
    criteria: acceptance criteria.
    exclusions: deferred features.
    blockers: necessary blockers.
    approval: actor, evidence_ref and approved_at, or an empty dict.
    issues: validation problems found while parsing (subjective criteria, approval missing for an approved status).
  """

  mvp_id: str
  baseline_version: int
  status: str
  owner: str
  outcome: str
  criteria: tuple[Criterion, ...]
  exclusions: tuple[Exclusion, ...]
  blockers: tuple[Blocker, ...]
  approval: dict
  issues: tuple[str, ...] = ()

  @property
  def revision(self) -> str:
    """Return the contract revision label used in verdicts, e.g. UNC-MVP-001@1.

    Returns:
      mvp_id and baseline_version joined by @.
    """
    return f"{self.mvp_id}@{self.baseline_version}"

  def criterion_ids(self) -> set[str]:
    """Return the IDs of the accepted criteria.

    Returns:
      The set of criterion IDs.
    """
    return {c.id for c in self.criteria}


def _criteria(data: dict, issues: list[str]) -> tuple[Criterion, ...]:
  """Parse acceptance_criteria, flagging subjective or duplicate ones.

  Args:
    data: the parsed contract.
    issues: list to append non-fatal problems to.

  Returns:
    The criteria in contract order.

  Raises:
    RecordError: an entry is not a mapping or lacks id or test.
  """
  criteria = []
  for i, raw in enumerate(data.get("acceptance_criteria") or []):
    if not isinstance(raw, dict):
      raise RecordError(f"{WHERE}: acceptance_criteria[{i}] must be a mapping")
    where = f"{WHERE} criterion {i}"
    crit = Criterion(text_field(raw, "id", where), text_field(raw, "test", where), text_field(raw, "evidence_required", where, False))
    if any(word in crit.test.lower() for word in SUBJECTIVE):
      issues.append(f"criterion {crit.id}: subjective wording, rewrite as an observable pass/fail test")
    criteria.append(crit)
  if not criteria:
    issues.append("no acceptance criteria")
  if len({c.id for c in criteria}) != len(criteria):
    issues.append("duplicate criterion IDs")
  return tuple(criteria)


def _exclusions(data: dict) -> tuple[Exclusion, ...]:
  """Parse exclusions given as bare text or as {id, text, keywords}.

  Args:
    data: the parsed contract.

  Returns:
    The exclusions; a bare string is its own ID and keyword.

  Raises:
    RecordError: an entry is neither text nor a mapping, or a mapping lacks text.
  """
  out = []
  for raw in data.get("exclusions") or []:
    if isinstance(raw, str):
      out.append(Exclusion(raw, raw, (raw.lower(),)))
    elif isinstance(raw, dict):
      text = text_field(raw, "text", f"{WHERE} exclusion")
      words = tuple(str(k).lower() for k in raw.get("keywords") or [text])
      out.append(Exclusion(text_field(raw, "id", WHERE, False) or text, text, words))
    else:
      raise RecordError(f"{WHERE}: an exclusion must be text or a mapping")
  return tuple(out)


def _blockers(data: dict, criteria: tuple[Criterion, ...], issues: list[str]) -> tuple[Blocker, ...]:
  """Parse necessary_blockers, flagging any that unblock an unknown criterion.

  Args:
    data: the parsed contract.
    criteria: the parsed criteria.
    issues: list to append non-fatal problems to.

  Returns:
    The blockers.

  Raises:
    RecordError: an entry is not a mapping or lacks id or unblocks.
  """
  out = []
  for raw in data.get("necessary_blockers") or []:
    if not isinstance(raw, dict):
      raise RecordError(f"{WHERE}: a necessary blocker must be a mapping with id and unblocks")
    where = f"{WHERE} blocker"
    out.append(Blocker(text_field(raw, "id", where), text_field(raw, "unblocks", where), text_field(raw, "description", where, False)))
  known = {c.id for c in criteria}
  issues.extend(f"blocker {b.id} unblocks unknown criterion {b.unblocks}" for b in out if b.unblocks not in known)
  return tuple(out)


def _status_and_version(data: dict) -> tuple[str, int]:
  """Read and check status and baseline_version.

  Args:
    data: the parsed contract.

  Returns:
    (status, baseline_version).

  Raises:
    RecordError: status unknown, or baseline_version not an integer of 1 or more.
  """
  status = text_field(data, "status", WHERE)
  if status not in MVP_STATUSES:
    raise RecordError(f"{WHERE}: status {status!r} is not one of {MVP_STATUSES}")
  try:
    version = int(data.get("baseline_version", 0))
  except (TypeError, ValueError) as err:
    raise RecordError(f"{WHERE}: baseline_version must be an integer") from err
  if version < 1:
    raise RecordError(f"{WHERE}: baseline_version must be 1 or more")
  return status, version


def parse_mvp(data: object) -> Mvp:
  """Build an Mvp from a parsed mvp.yaml.

  Args:
    data: the parsed YAML mapping.

  Returns:
    The Mvp; problems that do not stop parsing are listed in issues.

  Raises:
    RecordError: the record is not a mapping, or a required field is missing or malformed.
  """
  if not isinstance(data, dict):
    raise RecordError(f"{WHERE}: expected a mapping")
  status, version = _status_and_version(data)
  issues: list[str] = []
  criteria = _criteria(data, issues)
  approval = data.get("approval") or {}
  if not isinstance(approval, dict):
    raise RecordError(f"{WHERE}: approval must be a mapping")
  if status == "approved" and not (approval.get("actor") and approval.get("evidence_ref") and approval.get("approved_at")):
    issues.append("status approved but approval actor, evidence_ref or approved_at is missing")
  return Mvp(
    mvp_id=text_field(data, "mvp_id", WHERE),
    baseline_version=version,
    status=status,
    owner=text_field(data, "owner", WHERE),
    outcome=text_field(data, "outcome", WHERE),
    criteria=criteria,
    exclusions=_exclusions(data),
    blockers=_blockers(data, criteria, issues),
    approval=dict(approval),
    issues=tuple(issues),
  )
