from datetime import date

from bftoolkit.models import Claim, ClaimState, EvidenceQuality, HumanApproval, Source
from bftoolkit.store import LocalStore


def test_sqlite_store_persists_claim_approval_and_run(tmp_path) -> None:
    store = LocalStore(tmp_path / "records.sqlite")
    claim = Claim(
        id="market-demand",
        statement="Demand has been checked.",
        state=ClaimState.VERIFIED,
        evidence_quality=EvidenceQuality.VERIFIED_PRIMARY,
        sources=[Source(title="Authority", url="https://example.test", retrieved_on=date(2026, 8, 29), primary=True)],
    )
    approval = HumanApproval(approver="Owner", scope="pilot")

    store.save_claim(claim)
    store.save_approval(approval)

    assert store.get_claim("market-demand").is_actionable is True
    assert store.latest_approval("pilot").approver == "Owner"
