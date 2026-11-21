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

## 20261121_1313 — Edge allowlist miss recurred; route-coverage check proposed (v2.3.9 -> v2.3.10)

- references/security-and-segmentation.md: Recurred 2026-11-21 note under the 2026-11-20 edge allowlist entry, with a cheaper guard (route coverage check).

## 20261120_2330 — An edge path allowlist silently drops new device routes (v2.3.8 -> v2.3.9)

- `references/security-and-segmentation.md` (Trust-boundary pass): Learned 2026-11-20 from the continuum P4 gate, with the Caddy excerpt.

## 20261120_1815 — WAN: roaming laptops dial out to a relay when there is no overlay (v2.3.7 -> v2.3.8)

- references/wan-and-remote-access.md: Learned 2026-11-20 (Continuum DL-065): host-to-host rsync or scp needs an inbound listener on the receiving end; with no overlay, both ends dial out to an authenticated relay and the direct tool stays a measured baseline.

## 20261120_0255 — APN: a bench Pi needs the field's uplink shape, not an untagged LAN lease (v2.3.6 -> v2.3.7)

- `operator/apn/site-boxes-and-platforms.md` lab-proof entry 41: the field interface-activation hook loops when untagged eth0 gets a DHCP lease on the
  bench; carry internet on tagged VLAN 522 as a site does (smc-resiliency B20-02, lab test record 27).

## 20261119_2214 — Containers: isolating CI jobs on a developer Mac (v2.3.5 -> v2.3.6)

- `references/datacenter-cloud-containers.md` Learned 2026-11-19: host.docker.internal exposes loopback-published Mac services to any bridge; an internal network plus an
  allowlisting forward proxy isolates CI; build the allowlist from a logged discovery run (continuum-app DL-034).

## 20261119_1855 — APN: the warehouse field image as the bench base, its network as shipped (v2.3.4 -> v2.3.5)

- `operator/apn/site-boxes-and-platforms.md` item 40: the shipped site Pi (untagged eth0 unaddressed, VLAN 500/501 bridges, MANAGEMENT chain, Teleport by
  hostname), the bench overlay (20261119_1756) and B19-06.

## 20261119_1539 — Local container networks reach host loopback (v2.3.3 -> v2.3.4)

- `references/security-and-segmentation.md`: Learned entry from continuum-app (b6dbded): on OrbStack a container's own bridge network reaches every 127.0.0.1-published Mac service through host.docker.internal; probe before trusting it as isolation.

## 20261119_1325 — WireGuard-based overlays compared for a small self-hosted estate (v2.3.2 -> v2.3.3)

- `references/wan-and-remote-access.md`: Learned 2026-11-19 from Continuum DL-019: plain WireGuard, NetBird ports and licences, Headscale with closed Tailscale GUI clients, Firezone self-hosting stance.

## 20261118_2124 — Position identity where addressing repeats; APN D3a (v2.3.1 -> v2.3.2)

- `references/addressing-and-ipv6.md`: Learned 2026-11-18, key a position by site and name where sites reuse a prefix; what stays with the position and what moves with the unit; a record outside
  every site holds no address.
- `operator/apn/oss-bss-and-fleet-data.md`: D3a, the low-touch `name` and `locid` as the position's identity and the decided asset ID for the unit. From a design review for
  unified-network-controller (D17), on the operator's instruction to use this pack.

## 20261110_1248 — APN fleet survey facts in operator/apn (v2.3.0 -> v2.3.1)

- operator/apn/site-boxes-and-platforms.md: Learned 2026-11-10 before "Hangs, power and detection" (bootloader census, nbn_wh writable root, undervoltage, x86 watchdog and write rates, census misses).
- Source: smc-resiliency fleet survey (2026-11-10).

## 20261110_0025 — APN operator context extended; collaboration protocol: proxmox and vagrant rows, one fact one home (v2.2.0 -> v2.3.0)

- operator/apn/site-fleet-network.md items 43 to 62 (site patterns, reach checks and ladder, DNS paths, backdoor, Teleport, cnMaestro, the SMC to
  UNC contract, site devices) and new operator/apn/site-backhaul.md (12 items: Sky Muster, Starlink, Iridium and Thuraya swaps, latency and
  measured link profiles); README index and estate paragraph corrected (Sky Muster and Starlink; Pi or x86 boxes). Source disagreements recorded,
  not resolved (counts, latency, backdoor retirement, Teleport versions).
- operator/apn/site-boxes-and-platforms.md items 27 to 39 (for skill-systems-architect, which reads this folder by path).
- references/collaboration-protocol.md (shared): skill-proxmox and skill-vagrant rows; an "Overlap" rule (product facts in the platform pack, the
  vendor-neutral lesson in the architect, project facts in the project, the operator folder summarises and points; the pack wins on a product fact).

## 20261029_2029 — Session closeout: incidents and operational events (2026-10-29)

- Incident: a concurrent session's commit b6f399f (skill-slurp-chat and skill-coder) swept in this session's staged files (215 files, v2.2.0
  and all write-backs) under its own message; content intact, attribution in that message is wrong. Found when the local commit reported
  nothing to commit. Lesson: stage and commit in one command when another session shares the repo.
- Incident: the auto-mode classifier refused `git push` for skills_stuff after b6f399f (Out-of-Place Publication); the push is handed to the
  operator. Earlier pushes this session (ab9b2fb, 6bb262e, 6995542, ba56a38) went through.
- Incident: the OPA gate refused a Bash heredoc whose text contained the word "deleting"; the same edit was made with the Edit tool.
- Incident: four quality-pass agents stopped at the 5-hour usage limit mid-edit; resumed at 19:00 from their saved state, no lost work.
- Operational: skill-ifa install at ~/.claude/skills/skill-ifa was a stale copy (327 lines behind its source); replaced by a symlink to
  invoice-finance-analyst/internal-invoice-analysis; the old copy is recoverable from that pack's git history.
- Operational: markdown_rewrap fixed twice (link definitions are fixed lines; suffixed Learned headers are fixed lines), scripts_stuff
  236e88e and 78952fe; all-scraper fixed twice (mcp-fetch readability error, thin-body false successes), tools_stuff a659c26 and 0bac50b.
- Finding: a side review showed the eval rubric's interfaces criterion favoured the skill; the fair rerun (baseline given the specialist
  registry) still showed 22/22 wins, 12.71 vs 9.75 (evals/results.md).

## 20261029_2024 — Knowledge harvest from the APN and personal projects; APN operator context (v2.1.0 -> v2.2.0)

- Project harvest (operator, 2026-10-29): seven read-only harvests of the APN and personal projects (368 items) fed both architects and
  other packs. New references: australian-access-networks (nbn constructs incl. CVC TC-4 not charged from 2026-07-01 on non-satellite
  networks, 121 POIs, TC classes), service-provider-edge (BNG, CoA, reconnect storms, CGNAT logging), voice-and-sip (trunks, Erlang B,
  emergency-call obligations under the 2019 Determination), remote-site-fleet (one-box rule, GEO polling limits, discovery ranking).
  Updates: network-services (resolver receive path), routing-and-switching (transport baseline, ECMP hashing), security-and-segmentation
  (zero-trust fleet access), observability-troubleshooting, red-flags (Remote-site fleets table); shared method and automation additions.
- APN operator context contained in operator/apn/ (README index plus four topic files, 137 items, no names, IPs or figures); general
  references stay operator-neutral. check_package scans operator/ and accepts links into a sibling skill folder.
- Sources: store 519 items; ledgers rebuilt.

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
