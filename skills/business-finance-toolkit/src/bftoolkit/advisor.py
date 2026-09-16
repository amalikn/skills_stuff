"""Planning logic for commercial investigations, intentionally separate from LLM drafting."""

from pydantic import BaseModel

from .domain_packs import get_domain_pack


class AssessmentPlan(BaseModel):
    idea: str
    domain_pack: str
    required_skills: list[str]
    required_claims: list[str]
    hidden_cost_categories: list[str]
    warnings: list[str]


BASE_SKILLS = [
    "opportunity-assessment",
    "market-competitor-research",
    "import-procurement-analysis",
    "hidden-cost-discovery",
    "unit-economics",
    "cash-flow-scenario-analysis",
    "capital-requirements",
    "pilot-planning",
    "decision-memo",
]


def build_assessment_plan(idea: str, *, domain_pack: str = "generic-import") -> AssessmentPlan:
    pack = get_domain_pack(domain_pack)
    return AssessmentPlan(
        idea=idea,
        domain_pack=pack.id,
        required_skills=BASE_SKILLS,
        required_claims=pack.required_claims,
        hidden_cost_categories=pack.hidden_cost_categories,
        warnings=pack.warnings,
    )
