---
Title: Changelog
Category: change-log
Status: current
Authority: authored-guidance
Scope: skill-network-architect
Last reviewed: 2026-10-29
Summary: Dated changes to the pack, newest first. The version lives in SKILL.md metadata.
Kind: log
---

# Changelog

## 20261029_1951 — Gap closure: helpers, verified facts, templates, filled examples (v2.0.0 -> v2.1.0)

- Helpers: fibre_budget.py (TIA-568 maximum defaults, verified via the FOA loss-budget page) and power_budget.py (PoE per class, UPS load
  and linear runtime); mtu_budget.py gains AES-GCM ESP layers (57, NAT-T 65, IPv6 77). 20 tests.
- Resolved: LIPD Class Licence 2025 includes 6425-6585 MHz (items 13-14: 250 mW indoor, 25 mW otherwise; VERIFIED_PRIMARY); DFS timings per ETSI
  EN 301 893 (60 s CAC, 10 min weather band, 30 min non-occupancy); copper and optical reach sourced. Usable-throughput rules for Wi-Fi and TDD radios.
- Templates: bgp-peer-policy, evpn-fabric-build, wifi-survey-acceptance, ptp-link-record. Collaboration protocol: placement ownership row and
  the intent-versus-observation rule. Routing row for platform-pack or monitoring symptoms.
- Domain Routing gains a topical-sections column (direct links to a module's sections), so a narrow question loads one section, not the file.
- Filled worked examples in examples/filled/ (every number from a helper run, inputs beside each); each template links its example.
- Link definitions merged by the old wrap-hook bug split back to one per line (14 blocks); check_package now fails on merged definitions.
- Source store 410 items; ledgers rebuilt.

## 20261029_1911 — Research-backed deepening, local sources, enforced quality bar (v1.1.0 -> v2.0.0)

- Helpers added: mtu_budget.py (payload MTU and TCP MSS per encapsulation stack), link_budget.py (FSPL, fade margin, Fresnel clearance with
  k-factor bulge), availability.py (series/parallel, shared); ip_plan_check.py flags IPv6 segments other than /64, /127, /128. 14 tests.
- New network templates: ip-addressing-plan, site-network-design, routing-policy. 27 network red flags.
- References rewritten to one backbone (Scope, Decision rules with evidence labels and sources, Patterns and anti-patterns, Failure modes and tests,
  Worked example run through the helpers, Review checklist, Further reading); every load-bearing claim checked online 2026-10-29 and labelled.
  architecture-method.md is the framework: modes, the discover -> operate flow mapped to templates and helpers, per-mode checklists.
- ASCII diagrams redrawn or added in every reference and template (ASCII only, at most 110 columns, title, legend, ruler-checked).
- Shared templates: 5 rewritten in depth (MADR 4.0 decision record, Method of Procedure change form) and 7 added (requirements, discovery, FMEA,
  risk register, test and acceptance with failure injection, post-incident review, capacity model).
- Local source store `sources/` (RFC text, PDFs, all-scraper Markdown snapshots, index.json; 355 items, 15 MB) via `just fetch-sources`;
  `sources.json` rebuilt by `just ledger` (curated labels kept, every cited URL catalogued, local paths); `just links` probes every URL.
- check_package now enforces: references routed in SKILL.md, templates catalogued in RUNBOOK.md, scripts catalogued, recipes named in docs exist,
  docstrings with Args/Returns, ASCII diagrams within 110 columns, lines within 200, RFC links to the .html text, no contractions, every cited URL
  in sources.json. Negative tests for each.
- SKILL.md: third-person descriptions with user vocabulary and a not-for list; Domain Routing table with a Load-when column (one hop);
  red-flags.md triage table. evals/trigger-cases.json (10 trigger, 10 near-miss); offline proxy run 38/39.
- Similar-skills survey: docs/research/similar-skills-survey-20261029_1758.md in skill-network-architect; adoptions paraphrased, nothing copied.
- Feedback written back: all-scraper (mcp-fetch readability error now escalates; two thin hosts in its ROADMAP) and markdown_rewrap (link
  reference definitions no longer merged).

## 20261029_1750 — Adopted into skills_stuff conventions and deepened (v1.0.0 -> v1.1.0)

- Removed the portable-ZIP packaging: LICENSE, THIRD_PARTY_NOTICES.md, Makefile, the SHA-256 manifest.json and its verify/refresh scripts and tests (operator, 2026-10-29).
  Upstream attribution stays in sources.json.
- Runtime: justfile, .mise.toml (Python 3.14), requirements.txt (ruff 0.17.3), venv in skills-working-cache/skill-network-architect; `just check` is the closing check.
- Structure aligned with the other operator packs: RUNBOOK.md routing, CHANGELOG.md, SCRATCHPAD.md, SKILL.md Use When, Standing Write-Back Contract, Related Skills.
- Shared material made single-source: six references, the templates and scripts/check_package.py, scripts/availability.py are canonical in skill-network-architect;
  skill-systems-architect symlinks to them.
