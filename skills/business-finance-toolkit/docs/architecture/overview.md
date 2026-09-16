# Architecture overview

## System shape

```text
Idea / data
    -> assessment plan
    -> claim register + source records
    -> deterministic calculations
    -> scenario and gate evaluation
    -> decision memo + run manifest
    -> human approval
```

The toolkit is a modular monolith. It can be installed as a CLI, embedded as a Python package, or used as portable skill instructions. The first release has no service boundary because the dominant risks are evidence quality, calculation correctness, and approval discipline—not distributed-system scale.

## Package boundaries

- `models.py`: stable contracts for claims, sources, lifecycle, decisions, approvals, and manifests.
- `calculators/`: pure functions with Decimal inputs and exact money rounding.
- `advisor.py`: assembles an investigation plan from an idea plus a domain pack.
- `gates.py`: determines whether evidence/approval gates block, require review, or permit approval.
- `provenance.py`: creates canonical input hashes and run manifests.
- `domain_packs/`: question and cost-discovery templates, not embedded regulatory decisions.
- `llm/contracts.py`: narrow provider protocols; providers may draft, never certify.

## Persistence and analysis adapters

JSON/YAML are the interchange format. SQLite is the recommended local system of record for claims, runs, and approvals once persistence is added. Pandas and DuckDB belong in optional adapters for larger CSV, listing, sales, or market datasets. Neither is necessary to run the current deterministic core.

## Extension rules

Add a domain pack when a business area needs different questions, sources, cost categories, or gates. Add a calculator only when its formula is deterministic, documented, and testable. Add an LLM provider outside the core package, with a data-classification policy and human review of drafts.
