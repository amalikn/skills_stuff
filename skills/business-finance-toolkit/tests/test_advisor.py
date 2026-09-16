from datetime import date

from bftoolkit.advisor import build_assessment_plan
from bftoolkit.gates import evaluate_pilot_gate
from bftoolkit.models import Claim, ClaimState, EvidenceQuality, HumanApproval, Source


def test_generic_import_plan_includes_hidden_cost_and_evidence_work() -> None:
    plan = build_assessment_plan("Import used equipment from Japan to Australia", domain_pack="australia-jdm")

    assert "hidden-cost-discovery" in plan.required_skills
    assert "import-eligibility" in plan.required_claims


def test_gate_blocks_when_a_critical_claim_is_not_actionable() -> None:
    claim = Claim(
        id="import-eligibility",
        statement="Import eligibility is unknown.",
        state=ClaimState.MISSING,
        evidence_quality=EvidenceQuality.UNVERIFIED,
    )

    result = evaluate_pilot_gate([claim], required_claim_ids=["import-eligibility"], approval=None)

    assert result.status == "BLOCKED"
    assert "import-eligibility" in result.reasons


def test_gate_requires_human_approval() -> None:
    claim = Claim(
        id="market-demand",
        statement="Demand has been checked.",
        state=ClaimState.VERIFIED,
        evidence_quality=EvidenceQuality.VERIFIED_PRIMARY,
        sources=[Source(title="Authority", url="https://example.test", retrieved_on=date(2026, 8, 29))],
    )

    result = evaluate_pilot_gate([claim], required_claim_ids=["market-demand"], approval=None)

    assert result.status == "READY_FOR_REVIEW"


def test_gate_blocks_when_required_claim_is_absent_even_with_approval() -> None:
    approval = HumanApproval(approver="Owner", scope="pilot")

    result = evaluate_pilot_gate([], required_claim_ids=["market-demand"], approval=approval)

    assert result.status == "BLOCKED"
    assert "market-demand" in result.reasons


def test_gate_approves_only_with_named_human_approval_and_all_claims() -> None:
    claim = Claim(
        id="market-demand",
        statement="Demand has been checked.",
        state=ClaimState.VERIFIED,
        evidence_quality=EvidenceQuality.VERIFIED_PRIMARY,
        sources=[Source(title="Authority", url="https://example.test", retrieved_on=date(2026, 8, 29), primary=True)],
    )
    approval = HumanApproval(approver="Owner", scope="pilot")

    result = evaluate_pilot_gate([claim], required_claim_ids=["market-demand"], approval=approval)

    assert result.status == "APPROVED"
