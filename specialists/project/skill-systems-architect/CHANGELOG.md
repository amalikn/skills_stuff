---
Title: Changelog
Category: change-log
Status: current
Authority: authored-guidance
Scope: skill-systems-architect
Last reviewed: 2026-10-29
Summary: Dated changes to the pack, newest first. The version lives in SKILL.md metadata.
Kind: log
---

# Changelog

## Unreleased

- 2026-11-11: front-matter description shortened to cut startup tokens; the full original text is kept verbatim in the new `## Full description` section of SKILL.md.

## 20261111_2007 — Read-only root versus RAM overlay: the trial boot catches missed writers, scheduled writers need their own run (v2.3.6 -> v2.3.7)

- references/edge-appliances.md, Image layout and updates: Learned 2026-11-11 entry from the APN R28 review (enterprise-strategy hub, smc-resiliency SM report):
  commit-on-health turns a missed writer on a read-only root into a fallback, only when the health check exercises every write path; scheduled writers need a
  run in the trial or a canary; a RAM overlay is a bench write detector, not a field safety net.

## 20261110_1355 — Edge retention, silent provisioning skips, transient units; SSH changed host key kills reverse tunnels (v2.3.5 -> v2.3.6)

- references/edge-appliances.md: three Learned 2026-11-10 entries before "Flash wear and RAM placement" (delete each period only after its own upload
  succeeds, never an exact period; survey provisioning outcomes, online `lvextend -r`; `systemd-run --unit --collect` for long jobs over flaky sessions).
- references/security-and-service-identity.md: Learned 2026-11-10 before "Worked example" (`StrictHostKeyChecking=no` does not cover a changed key:
  forwarding is disabled; monitor the server-side listener; install keys read on the server).
- Source: smc-resiliency, koonibba-smc01 disk, backdoor and url_capture work (2026-11-10).

## 20261110_1248 — Fleet survey: watchdog audit, write measurement, overlay wear, undervoltage; systemd credentials rotation (v2.3.4 -> v2.3.5)

- references/edge-appliances.md: Learned 2026-11-10 before "Patterns and anti-patterns" (a shipped driver is not a watchdog; writes per disk and per process; overlay root wear; Pi undervoltage; census bootloaders).
- references/linux-unix.md: Learned 2026-11-10 (LoadCredential copies at start: stage, switch a symlink, restart users).
- Source: smc-resiliency fleet survey and N15 design note (2026-11-10).

## 20261110_1205 — Restore proof by exact row counts; compose `up --wait` false failures (v2.3.3 -> v2.3.4)

- references/backup-disaster-recovery.md: Learned 2026-11-10 before "Patterns and anti-patterns" (restore into a scratch DB, per-table exact counts, live-growth vs loss verdict).
- references/containers-and-platforms.md: Learned 2026-11-10 before "Kubernetes essentials" (start_period from the worst post-rebuild start; read the process before a rollback).
- Source: unified-network-controller Nautobot 3.2.9 upgrade on the Mac and apn-unc01 (2026-11-10).

## 20261110_0525 — Measured Qwen3.8-27B on oMLX; prefill-peak rule; prefix-cache blocks on hybrid models (v2.3.2 -> v2.3.3)

- references/ai-inference-platforms.md: three Learned entries before "Fair comparisons" (measured weights, prefill, MTP accept and an agentic
  benchmark ranking on M2 Max 64 GB; prefill peak set by per-step attention memory and the engine's prefill policy, headroom check and one model
  resident at a time; 4096-token prefix-cache blocks on hybrid Gated DeltaNet models). Source: tools_stuff cline session record, commit d88d77b.

## 20261110_0202 — Converting deployed single-root boxes in place; slot sizing; field wear metrics (v2.3.1 -> v2.3.2)

- references/edge-appliances.md: Learned 2026-11-10 beside "Convert existing boxes at a planned visit" (bench pilot, carve before copy, shrink exposure measured read-only, slots sized at twice a measured release, wear measured in the field).

## 20261110_0030 — Flash-step guards for removable media (v2.3.0 -> v2.3.1)

- references/provisioning-and-lifecycle.md: Learned 2026-11-10 before "Rollout waves": build apart from flash, layout as data, and a flash
  step that refuses by disk content and a size range because a USB SSD reports removable like an SD card (smc-resiliency lab/logic/flash.py).

## 20261110_0025 — Linux and resiliency write-back from smc-resiliency S1; APN read from the shared folder (v2.2.0 -> v2.3.0)

- references/edge-appliances.md: Learned 2026-11-10 entries beside "Image layout and updates" (boot firmware is part of the image: a distribution's
  packaged Pi firmware could not boot GPT partition 2; prove the chain on every fleet bootloader; a fixed-length selection file overwritten in place)
  and "Hangs, watchdogs and power" (force the test hang by crashing PID 1, not SIGSTOP; the systemd watchdog does not cover firmware or initramfs
  failures). Evidence: smc-resiliency lab test record 19, bench transcript.
- APN: new items 27 to 39 in the shared ../skill-network-architect/operator/apn/site-boxes-and-platforms.md (resiliency design state, decisions,
  S1, S1V, X1, X2 results, lab rigs, UNC lifecycle role, source disagreements); no copy in this pack (operator, 2026-11-10: architects learn APN
  specifics; one home per fact).

## 20261029_2024 — Knowledge harvest from the APN and personal projects; APN operator context (v2.1.0 -> v2.2.0)

- Project harvest (operator, 2026-10-29): new references service-provider-systems (OSS/BSS, AVC keys, three-source reconciliation, money
  as numeric), fleet-management (per-field ownership, identity, spools, vendor exit by lifecycle event), edge-appliances (A/B images,
  pull updates, capped tmpfs and tmpfiles.d, Pi watchdog, honest write measurement). Updates: compute-and-facilities (kVA-billed colocation),
  storage-and-data (stretch vs replicate), migration-and-hybrid (measure before platform), ai-inference-platforms (measured local numbers,
  bandwidth bound), linux-unix (receive path), observability-and-incident (alert routing), red-flags. APN context read from
  ../skill-network-architect/operator/apn/.
- Sources: store 519 items; ledgers rebuilt.

## 20261029_1951 — Gap closure: helpers, verified facts, templates, filled examples (v2.0.0 -> v2.1.0)

- Helpers: restore_time.py (per-phase restore against the RTO, no capacity model needed) and eol_check.py (end-of-support register);
  quorum_check.py gains combined scenarios (`domain:rack-a+qdevice`). 14 tests.
- References: databases-and-ha (PostgreSQL replication, Patroni, PITR tools, Galera, SQLite at the edge) and ai-inference-platforms (weights,
  KV cache, concurrency, tokens/s); FOSS MDM (NanoMDM, MicroMDM status, Fleet licence split, osquery) and Apple Business (replaced ABM 2026-04-14);
  Windows Server 2016-2025 lifecycle dates now VERIFIED_PRIMARY. Template: dr-runbook. Red flag for stale monitoring; expand/contract pattern.
- Eval cases S01 and S02 replaced with fresh numbers (they reused worked-example values).
- Domain Routing gains a topical-sections column (direct links to a module's sections), so a narrow question loads one section, not the file.
- Filled worked examples in examples/filled/ (every number from a helper run, inputs beside each); each template links its example.
- Link definitions merged by the old wrap-hook bug split back to one per line (14 blocks); check_package now fails on merged definitions.
- Source store 410 items; ledgers rebuilt.

## 20261029_1911 — Research-backed deepening, local sources, enforced quality bar (v1.1.0 -> v2.0.0)

- Helpers added: quorum_check.py (node, domain and QDevice loss against quorum; odd-count QDevice warning) and ceph_capacity.py (plan TB after
  losing the largest domains, self-healing, min_size); worked-example inputs in examples/. 10 tests.
- New systems templates: host-and-cluster-build, backup-and-restore-test, lifecycle-and-patching. 30 systems red flags; DR strategy ladder.
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
- Runtime: justfile, .mise.toml (Python 3.14), requirements.txt (ruff 0.17.3), venv in skills-working-cache/skill-systems-architect; `just check` is the closing check.
- Structure aligned with the other operator packs: RUNBOOK.md routing, CHANGELOG.md, SCRATCHPAD.md, SKILL.md Use When, Standing Write-Back Contract, Related Skills.
- Shared material made single-source: six references, the templates and scripts/check_package.py, scripts/availability.py are canonical in skill-network-architect;
  skill-systems-architect symlinks to them.
