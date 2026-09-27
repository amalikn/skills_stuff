# Patterns — skill-staleness-audit

The depth behind each phase of [SKILL.md](../SKILL.md). Load the one a phase names when you reach it; do not read them all up front. Where a pattern file and SKILL.md disagree, the pattern file wins.

| Pattern | Phase | What it holds |
|---|---|---|
| [domain-adapters.md](domain-adapters.md) | before 1 | The six claim types mapped onto code, research, finance, network, ops and ML repos, with each domain's silent-failure mode |
| [coverage-manifest.md](coverage-manifest.md) | 1 | Every file classified as examined, exempt or out of scope; binary and tabular files; systems of record |
| [materiality-ranking.md](materiality-ranking.md) | 1 | The M / H / G bands, and why ranking before fixing changes the outcome |
| [defect-taxonomy.md](defect-taxonomy.md) | 1–2 | The recurring defect patterns: signature, detection, a real instance, the fix |
| [supersession-banners.md](supersession-banners.md) | 3 | The in-place banner contract, and supersession chains that run against the ordering heuristic |
| [per-artifact-reasoning.md](per-artifact-reasoning.md) | 4 | The three prompts, including live-inventory reach — what a grep cannot find |
| [check-hardening.md](check-hardening.md) | 5 | Writing a check that can fail, and negative-testing it through `audit_state.py negtest` |
| [evidence-integrity.md](evidence-integrity.md) | 5–7 | Provenance labels, population matching and record counts |
| [completeness-verification.md](completeness-verification.md) | 7 | The exit gate: claim inventory, residual classes, report before cleanup, exit criteria |
