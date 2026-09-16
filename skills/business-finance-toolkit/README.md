# Business & Finance Toolkit

An evidence-governed, production-oriented starting point for assessing a business idea, an import/procurement opportunity, or a pilot before committing money. It is a commercial advisor and skill portfolio, not an accounting ledger and not a substitute for legal, tax, customs, financial-planning, or compliance advice.

## What it does

- Plans an investigation across opportunity, market, competitors, imports, hidden costs, economics, cash, capital, operations, sales, pilot design, and a decision memo.
- Keeps claims separate from assumptions; claims carry a source, evidence-quality label, and state.
- Calculates landed cost, contribution margin, closing cash, scenarios, and capital requirements with `Decimal`.
- Blocks a pilot gate when critical evidence is missing and requires explicit human approval before approval.
- Includes portable Markdown skill workflows and declarative generic-import and Australia/JDM domain packs.

## Quick start

```bash
uv sync --extra dev
uv run bftoolkit assess --idea "Import used equipment from Japan to Australia" --domain-pack australia-jdm
uv run bftoolkit gate --claims claims.json --required-claim market-demand --approver "Business owner" --store records.sqlite
uv run pytest
python tools/validate_repository.py
```

The `assess` command is read-only and prints a JSON assessment plan plus an input-hashed run manifest. `gate` evaluates supplied claims, requires a named human approval to approve, and can store claims, approval, and manifest locally in SQLite. The Australia/JDM pack intentionally identifies questions without asserting current regulatory answers.

`examples/verified-market-demand-claim.json` is a format demonstration only. `example.test` is deliberately non-authoritative and must be replaced with a real primary source before use in a material decision.

## Design choices

The core remains a modular local Python package. SQLite is appropriate for local durable records, while pandas and DuckDB are optional analysis adapters. There is no required vector database, agent graph framework, microservice layer, or provider SDK. An LLM may draft text through a narrow provider-neutral contract, but it cannot certify claims, alter deterministic results, or approve a decision.

`invoice-finance-analyst` is intentionally excluded. It may become a later portfolio skill after independent remediation and compatibility review; this repository neither imports its code nor treats it as the platform foundation.

## Repository map

- `src/bftoolkit/` — code contracts, calculations, advisor planner, gates, provenance, CLI, and domain packs.
- `skills/` — portable workflow instructions plus machine-readable manifests.
- `schemas/` and `config/` — interchange boundaries and defaults.
- `docs/` — architecture, governance, source policy, and roadmap.
- `examples/` — an inspectable import-pilot input and expected assessment output.
- `third_party/` — conceptual provenance and licence review notes; no external code is copied.

## Operating rule

Before relying on a legal, tax, customs, duty, GST, biosecurity, certification, registration, or product-compliance claim, attach an in-force primary source and record the retrieval date. Until then, label it `UNVERIFIED` and keep the decision gate blocked where it is critical.

## Development

Run `uv run pytest` and `python tools/validate_repository.py` before packaging or release. See [architecture](docs/architecture/overview.md), [governance](docs/governance/claim-and-decision-policy.md), and the [roadmap](docs/roadmap.md).

## Governance pointers

- Agent guidance: [AGENTS.md](AGENTS.md)
- AI context router: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Current working state: [SCRATCHPAD.md](SCRATCHPAD.md)
- Project history: [CHANGELOG.md](CHANGELOG.md)
