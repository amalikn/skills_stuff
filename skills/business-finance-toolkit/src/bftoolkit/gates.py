from collections.abc import Iterable

from pydantic import BaseModel

from .models import Claim, DecisionStatus, HumanApproval


class GateResult(BaseModel):
    status: DecisionStatus
    reasons: list[str]


def evaluate_pilot_gate(
    claims: Iterable[Claim], *, required_claim_ids: Iterable[str], approval: HumanApproval | None
) -> GateResult:
    claim_list = list(claims)
    claims_by_id = {claim.id: claim for claim in claim_list}
    required = list(required_claim_ids)
    blockers = [claim_id for claim_id in required if claim_id not in claims_by_id]
    blockers += [claim.id for claim in claim_list if claim.critical and not claim.is_actionable and claim.id not in blockers]
    if blockers:
        return GateResult(status=DecisionStatus.BLOCKED, reasons=blockers)
    if approval is None or approval.decision != DecisionStatus.APPROVED or approval.scope != "pilot":
        return GateResult(status=DecisionStatus.READY_FOR_REVIEW, reasons=["human-approval-required"])
    return GateResult(status=DecisionStatus.APPROVED, reasons=[])
