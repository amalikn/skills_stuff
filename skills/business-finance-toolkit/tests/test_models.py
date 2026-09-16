from datetime import date

import pytest

from bftoolkit.models import Claim, ClaimState, EvidenceQuality, Source


def test_claim_with_primary_source_is_verified() -> None:
    claim = Claim(
        id="gst-registration",
        statement="Registration threshold has been checked.",
        state=ClaimState.VERIFIED,
        evidence_quality=EvidenceQuality.VERIFIED_PRIMARY,
        sources=[Source(title="Authority", url="https://example.test", retrieved_on=date(2026, 8, 29))],
    )

    assert claim.is_actionable is True


def test_verified_claim_requires_a_source() -> None:
    with pytest.raises(ValueError, match="at least one source"):
        Claim(
            id="unsupported",
            statement="Unsupported fact",
            state=ClaimState.VERIFIED,
            evidence_quality=EvidenceQuality.VERIFIED_PRIMARY,
        )


def test_regulated_verified_claim_requires_a_primary_source() -> None:
    with pytest.raises(ValueError, match="primary source"):
        Claim(
            id="regulated",
            statement="Regulated fact",
            regulated=True,
            state=ClaimState.VERIFIED,
            evidence_quality=EvidenceQuality.VERIFIED_SECONDARY,
            sources=[Source(title="Secondary", url="https://example.test", retrieved_on=date(2026, 8, 29))],
        )


def test_source_url_must_be_http_url() -> None:
    with pytest.raises(ValueError):
        Source(title="Bad", url="not-a-url", retrieved_on=date(2026, 8, 29))
