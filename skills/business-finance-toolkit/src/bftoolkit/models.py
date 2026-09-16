"""Core data contracts. These models deliberately separate facts from recommendations."""

from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, model_validator


class EvidenceQuality(StrEnum):
    USER_STATED = "USER_STATED"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED_PRIMARY = "VERIFIED_PRIMARY"
    VERIFIED_SECONDARY = "VERIFIED_SECONDARY"


class ClaimState(StrEnum):
    MISSING = "MISSING"
    PROPOSED = "PROPOSED"
    VERIFIED = "VERIFIED"
    SUPERSEDED = "SUPERSEDED"


class SkillLifecycle(StrEnum):
    PROPOSED = "PROPOSED"
    RESEARCHED = "RESEARCHED"
    PROTOTYPE = "PROTOTYPE"
    VALIDATED = "VALIDATED"
    GOVERNED = "GOVERNED"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"


class DecisionStatus(StrEnum):
    DRAFT = "DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    BLOCKED = "BLOCKED"


class Source(BaseModel):
    title: str = Field(min_length=1)
    url: HttpUrl
    publisher: str | None = None
    primary: bool = False
    retrieved_on: date
    published_or_in_force_on: date | None = None
    excerpt: str | None = None


class Claim(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    statement: str = Field(min_length=1)
    critical: bool = True
    regulated: bool = False
    state: ClaimState
    evidence_quality: EvidenceQuality
    sources: list[Source] = Field(default_factory=list)
    notes: str | None = None

    @model_validator(mode="after")
    def verified_claims_need_evidence(self) -> "Claim":
        if self.state == ClaimState.VERIFIED and not self.sources:
            raise ValueError("verified claims require at least one source")
        if self.state == ClaimState.VERIFIED and self.evidence_quality in {
            EvidenceQuality.UNVERIFIED,
            EvidenceQuality.USER_STATED,
        }:
            raise ValueError("verified claims require verified evidence quality")
        if self.regulated and self.state == ClaimState.VERIFIED:
            if self.evidence_quality != EvidenceQuality.VERIFIED_PRIMARY or not any(source.primary for source in self.sources):
                raise ValueError("regulated verified claims require a primary source")
        return self

    @property
    def is_actionable(self) -> bool:
        return self.state == ClaimState.VERIFIED and bool(self.sources)


class HumanApproval(BaseModel):
    approver: str = Field(min_length=1)
    approved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scope: str = Field(min_length=1)
    decision: DecisionStatus = DecisionStatus.APPROVED
    notes: str | None = None


class RunManifest(BaseModel):
    run_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    calculator_version: str
    input_sha256: str
    claim_ids: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    provider: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
