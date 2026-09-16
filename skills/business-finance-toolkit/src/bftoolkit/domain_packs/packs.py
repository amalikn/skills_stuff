from pydantic import BaseModel


class DomainPack(BaseModel):
    id: str
    name: str
    required_claims: list[str]
    hidden_cost_categories: list[str]
    warnings: list[str]


GENERIC_IMPORT = DomainPack(
    id="generic-import",
    name="Generic import and procurement",
    required_claims=["market-demand", "supplier-terms", "import-eligibility", "landed-cost", "sales-price", "pilot-approval"],
    hidden_cost_categories=[
        "supplier-or-auction-fees",
        "origin-inland-transport",
        "inspection-and-preparation",
        "export-documents-and-storage",
        "freight-and-marine-insurance",
        "customs-and-border-processing",
        "port-and-terminal-charges",
        "brokerage-and-domestic-transport",
        "compliance-repairs-and-certification",
        "payment-fx-finance-and-inventory-holding",
        "sales-warranty-returns-and-contingency",
    ],
    warnings=["Confirm every duty, tax, border, product-safety, and licensing condition from an in-force primary authority before relying on it."],
)

AUSTRALIA_JDM = DomainPack(
    id="australia-jdm",
    name="Australia/JDM import pilot",
    required_claims=GENERIC_IMPORT.required_claims + ["australian-compliance-path", "biosecurity-path", "registration-path"],
    hidden_cost_categories=GENERIC_IMPORT.hidden_cost_categories + ["inspection-and-quarantine-treatment", "compliance-work-and-registration-readiness"],
    warnings=GENERIC_IMPORT.warnings
    + [
        "This pack identifies Australian/JDM research questions only; it does not determine vehicle eligibility, duty, GST, biosecurity treatment, certification, or registration requirements.",
        "Record the regulator, in-force date, operative wording, and retrieval date for each relied-on jurisdictional claim.",
    ],
)

PACKS = {GENERIC_IMPORT.id: GENERIC_IMPORT, AUSTRALIA_JDM.id: AUSTRALIA_JDM}


def get_domain_pack(pack_id: str) -> DomainPack:
    try:
        return PACKS[pack_id]
    except KeyError as error:
        raise ValueError(f"unknown domain pack: {pack_id}") from error
