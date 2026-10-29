---
Title: Operator context - site boxes and platforms
Category: operator-context
Status: current
Authority: internal
Scope: One operator's site-box fleet, colocation, platform and AI work plus the operator's personal AI platform projects; not general guidance
Last reviewed: 2026-10-29
Summary: >-
  Operator-specific lessons behind the systems-architect references: site-box images, flash wear, hangs and power, telemetry spool, colocation power, Ceph and
  platform choice, resolver tuning and local AI measurements. Each item gives the fact, why it matters, an evidence path and the general section it applies to.
  No site, community, customer or people names, addresses, credentials or prices.
---

# Operator context: site boxes and platforms

## Contents

- [How to read this file](#how-to-read-this-file)
- [Site-box images and updates](#site-box-images-and-updates)
- [Flash wear and measurement](#flash-wear-and-measurement)
- [Hangs, power and detection](#hangs-power-and-detection)
- [Telemetry and jobs](#telemetry-and-jobs)
- [Colocation power](#colocation-power)
- [Storage and platform choice](#storage-and-platform-choice)
- [Resolver receive path](#resolver-receive-path)
- [Local AI platforms](#local-ai-platforms)
- [Withheld evidence paths](#withheld-evidence-paths)

## How to read this file

- These are facts about one operator's estate and personal lab, harvested read-only on 2026-10-29. The general rule lives in the linked skill-systems-architect reference; this file holds the local
  evidence and numbers that taught it.
- `APN` means `/Volumes/Data/_ai/_project/project_stuff/apn`. `ME` means `/Volumes/Data/_ai/_project/project_stuff/me`. `SMC-SKILL` means
  `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc`.
- The site box (SMC) is the operator's single gateway appliance per site: Raspberry Pi boxes on SD cards and x86 boxes on CFast or dual SSD.
- Evidence labels: VERIFIED_SECONDARY (read from a project document, not re-observed on the system) unless stated.

## Site-box images and updates

1. The site-box resiliency programme is defined as the A/B update model: replace the hard-to-maintain read-only overlay root with two system copies, update the idle copy, switch, fall back on failure.
   Hang recovery is secondary to it.
   - Why: the overlay root made updates fragile and lost state at reboot; A/B gives a known-good copy and a knowable version.
   - Evidence: `APN/enterprise-strategy/.archcore/adr/smc-resiliency-is-the-ab-update-model.adr.md`
   - Applies: [Image layout and updates](../../../skill-systems-architect/references/edge-appliances.md#image-layout-and-updates)
2. Pi design: one signed release ID (erofs OS root, application extensions, config templates) installed into the idle slot, booted by firmware tryboot, one health check, automatic revert; no package
   manager or remount on the box; the box reports release ID and variable-set number.
   - Why: drift disappears by construction; the controller can compare intent with what runs.
   - Evidence: `APN/smc-resiliency/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` (lines 84-126)
   - Applies: [Image layout and updates](../../../skill-systems-architect/references/edge-appliances.md#image-layout-and-updates)
3. Boot-time render spike (VM only): render plus checks 0.3 s, site services up 6.6 s after kernel start against a 10 s budget; a bad variable set reverted on its own in about 100 s; a resolver-only
   swap lost no pings, a VLAN-rebuilding swap lost 1-2 of 250 management pings.
   - Why: shows boot-time rendering is fast enough; the numbers are VM results and must be re-run on hardware.
   - Evidence: `APN/smc-resiliency/docs/pi/pi-spike-s2-config-swap-20261020_1856.md`
   - Applies: [Decision rules](../../../skill-systems-architect/references/edge-appliances.md#decision-rules)
4. x86: the dual-SSD class falls back to a standby install on the second disk; newer single-disk models cannot. Decided: read-only A/B for every new or reimaged x86 box, hardened in place for the
   deployed fleet. Kernels had drifted across a wide patch range within one release.
   - Why: when hardware loses redundancy, rollback has to move into the image layout.
   - Evidence: `APN/smc-resiliency/docs/x86/x86-smc-resiliency-plan-20261014_1436.md` (lines 126-145)
   - Applies: [Image layout and updates](../../../skill-systems-architect/references/edge-appliances.md#image-layout-and-updates)

## Flash wear and measurement

5. x86 CFast boxes (one card, no fallback) were at 23-43% life left while writing 5.9-10.4 GB/day; SSD boxes sat at 91-100%. One card fell from 43% to 31% in three months after its write rate had
   already dropped 77%.
   - Why: wear can lag a write cut; track percent life per month, not only GB/day.
   - Evidence: `APN/smc-file-writing-analysis/docs/audits/disk-write-rates-20260723_1244.md` (lines 40-65); see also the withheld executive summary below
   - Applies: [Flash wear and RAM placement](../../../skill-systems-architect/references/edge-appliances.md#flash-wear-and-ram-placement)
6. A twelve-fix stack (journal, `/tmp`, metrics textfile, agent TSDB to capped tmpfs) cut block-level writes 48-80% (11.4 to 3.4 and 11.4 to 2.3 GB/day on two boxes), leaving a 2-4 GB/day floor from
   local logging. Caps total about 0.9 GB on 7.7-15 GB boxes.
   - Why: the source of the cited 48-80% range in the general reference.
   - Evidence: `APN/smc-file-writing-analysis/docs/recommendations.md` (lines 56-78)
   - Applies: [Flash wear and RAM placement](../../../skill-systems-architect/references/edge-appliances.md#flash-wear-and-ram-placement)
7. Log directories moved to tmpfs by a one-time configuration task: the proxy daemon does not create its log directory, two boxes lost the proxy at their first reboot, and 13 of 15 were latently
   broken; re-running the playbook fixed nothing because of its idempotency guard.
   - Why: tmpfiles.d (or the unit's directory settings) plus a forced canary reboot after every tmpfs change.
   - Evidence: `APN/smc-file-writing-analysis/.archcore/rules/RULE-016-tmpfs-relocation-needs-tmpfiles-for-daemon-dirs.md`
   - Applies: [Flash wear and RAM placement](../../../skill-systems-architect/references/edge-appliances.md#flash-wear-and-ram-placement)
8. Sampling `/proc/<pid>/io` every 60 s left 30-42% of device bytes unattributed on every one of eight nodes, inflating any share 1.4-1.7x if quoted against the process sum.
   - Why: device bytes are the denominator; process sums are a floor.
   - Evidence: `APN/smc-file-writing-analysis/.archcore/rules/RULE-022-process-sums-are-a-floor-not-a-total.md`
   - Applies: [Measuring writes honestly](../../../skill-systems-architect/references/edge-appliances.md#measuring-writes-honestly)
9. The fleet's node_exporter configuration excluded tmpfs, so capped mounts had no metrics and a filling log buffer would not alert. The upstream default does not exclude tmpfs (checked 2026-10-29),
   so this was a local setting. One SSD firmware reports VALUE=100 for every SMART attribute, and a relabel rule had dropped the raw series.
   - Why: prove each new mount and series reaches the central store.
   - Evidence: `APN/smc-file-writing-analysis/docs/audits/tmpfs-exhaustion-behaviour-and-monitoring-20260723_1414.md` (lines 110-125)
   - Applies: [Alert routing and honest measurement](../../../skill-systems-architect/references/observability-and-incident.md#alert-routing-and-honest-measurement)

## Hangs, power and detection

10. Pi hub boxes went fully silent (no tunnel, all exporters stopped in one scrape) and needed an on-site power cycle; memory, card, overlay, load and WAN causes were ruled out; root cause unknown
    (kernel or SoC lockup class). The fleet had no hardware watchdog. Kernel logs lived in the RAM overlay and were lost with the power cycle.
    - Why: hardware watchdog plus off-box kernel logs or ramoops.
    - Evidence: `APN/smc-resiliency/docs/recovery/smc-hang-recovery-options-20261006_1214.md`; `SMC-SKILL/references/06_failure-modes.md` (lines 150-330)
    - Applies: [Hangs, watchdogs and power](../../../skill-systems-architect/references/edge-appliances.md#hangs-watchdogs-and-power)
11. Alert rules for silent hosts existed and fired; nobody had verified where they routed, and each hang went unnoticed for about six months. One box flavour self-recovers through an external
    power-cycle board, which also hides how often it hangs.
    - Why: test-fire alerts to a human; every automatic recovery emits an event.
    - Evidence: `APN/smc-resiliency/docs/recovery/smc-hang-recovery-options-20261006_1214.md` (What actually happened; Open question 4)
    - Applies: [Alert routing and honest measurement](../../../skill-systems-architect/references/observability-and-incident.md#alert-routing-and-honest-measurement)
12. Kernel logged undervoltage 1,859-7,352 times a day, flat across 24 hours (undersized supply, converter or cable), while the volt-alarm metric read 0 because it is not latched between scrapes.
    - Why: read latched bits and kernel counts; size the supply.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines 366-376)
    - Applies: [Hangs, watchdogs and power](../../../skill-systems-architect/references/edge-appliances.md#hangs-watchdogs-and-power)
13. Solar hub sites went dark from before dawn to mid-morning in winter and booted at nearly the same clock time daily: 17-44 boots per site in 90 days, two winters running; no RTC, so a cold clock.
    - Why: classify outages by boot pattern before blaming the link; size winter autonomy.
    - Evidence: `SMC-SKILL/references/06_failure-modes.md` (lines 349-364)
    - Applies: [Hangs, watchdogs and power](../../../skill-systems-architect/references/edge-appliances.md#hangs-watchdogs-and-power)
14. A blocklist job wrote "success" and a timestamp at the end of download while the filter read a later build stage; two boxes filtered on four-week-old lists with nothing alerting.
    - Why: emit freshness from the stage the consumer reads.
    - Evidence: `APN/smc-squid-redesign/plans/smc-squid-blocklist-redesign-plan-20260903_1547.md` (lines 28-100)
    - Applies: [Alert routing and honest measurement](../../../skill-systems-architect/references/observability-and-incident.md#alert-routing-and-honest-measurement)

## Telemetry and jobs

15. Push collector design (proposed): one gzip batch per cycle (temp file, fsync, rename, rising sequence), spool capped at 48 h or 200 MB with oldest dropped and counted, no readings before time
    sync, ingest refuses data skewed more than 2 minutes or dated in the future, newest batch first, ack only after the stored-metrics check. Pi boxes booted up to 13 months behind until NTP stepped
    the clock.
    - Why: the source of the store-and-forward rules.
    - Evidence: `APN/unified-network-controller/docs/engineering/smc-push-collector-design-20261021_1757.md` (lines 248-285)
    - Applies: [Telemetry spool and time](../../../skill-systems-architect/references/edge-appliances.md#telemetry-spool-and-time)
16. Central configuration management over SSH lost visibility on link drops. Proposed: signed manifest with immutable job ID and durable RECEIVED to COMMITTED or REVERTED states, local execution,
    timed rollback for network changes, report after the WAN returns.
    - Why: the source of the pull-based job model.
    - Evidence: `APN/smc-resiliency/docs/overview/smc-on-box-execution-and-site-services-addendum-20261026_1602.md` (lines 222-266)
    - Applies: [Pull-based jobs over poor links](../../../skill-systems-architect/references/edge-appliances.md#pull-based-jobs-over-poor-links)

## Colocation power

17. A first analysis priced savings per kWh; the invoice lines showed billing on contracted kVA capacity (space and power lines proportional to the contract), so every kWh saving was invalid and the
    report was superseded.
    - Why: read the billing model off invoice lines first.
    - Evidence: `APN/equinix-cost-cutting/docs/power-analysis-comprehensive-20260610_1530.md` (lines 6-8)
    - Applies: [Power, UPS and thermal arithmetic](../../../skill-systems-architect/references/compute-and-facilities.md#power-ups-and-thermal-arithmetic)
18. A per-rack analysis labelled A:B draw ratios of 0.9-1.2 "wasteful N+1" and proposed single-path circuits; this is a doubtful claim, because dual-PSU equipment load-shares and one feed must carry A
    + B on failure. The target contract was set as the sum of per-cabinet 3-month peaks x 1.25; one cabinet near 83% of usable capacity sets the headroom constraint.
    - Why: near-equal A/B draw is normal; capacity is checked against one feed.
    - Evidence: `APN/equinix-cost-cutting/docs/per-rack-analysis-20260610_1600.md` (lines 53-54, 104-167)
    - Applies: [Power, UPS and thermal arithmetic](../../../skill-systems-architect/references/compute-and-facilities.md#power-ups-and-thermal-arithmetic)

## Storage and platform choice

19. Repatriation estate: 72 vCPU, 224 GB RAM, about 5.5 TB; containers 13-14% of compute and 9% of memory. A platform ADR naming about twenty products was withdrawn because it preceded the inventory;
    a non-Kubernetes candidate (hypervisor cluster plus existing services) joined the bake-off.
    - Why: the source of the measure-before-platform worked example.
    - Evidence: `APN/aws-to-local/.archcore/adr/withdraw-platform-baseline.adr.md`; `APN/aws-to-local/docs/platform-approach-revision-plan-rev06-20260728_1723.md`
    - Applies: [Measure before choosing a platform](../../../skill-systems-architect/references/migration-and-hybrid.md#measure-before-choosing-a-platform)
20. Ceph: the proposed three nodes per site was raised to four; an HDD pool implied size 2; databases exceeded the planned NVMe tier before monitoring and logs were counted. Two cities about 12-14 ms
    RTT apart: two independent clusters with asynchronous replication, RPO > 0, not a stretched cluster.
    - Why: outside the ~10 ms stretch guideline; three nodes leave no re-replication target.
    - Evidence: `APN/aws-to-local/docs/platform-approach-revision-plan-rev06-20260728_1723.md` (sections 6.2.1-6.2.6)
    - Applies: [Two sites: stretch or replicate](../../../skill-systems-architect/references/storage-and-data.md#two-sites-stretch-or-replicate)

## Resolver receive path

21. A busy recursive resolver VM looked CPU-bound while mostly idle: socket buffers at distro defaults, about 67k UDP receive buffer errors, a single virtio queue, and the NIC interrupt landing almost
    entirely on one of 8 vCPUs. The plan raised buffers in two passes by sysctl drop-in and moved multiqueue into the domain definition (cold start of the VM).
    - Why: the receive-path ladder comes before more CPU.
    - Evidence: `APN/docs/customer-resolvers/` (review, UDP tuning plan and multiqueue plan, 2026-04-02; file names withheld)
    - Applies: [Packet receive path before more CPU](../../../skill-systems-architect/references/linux-unix.md#packet-receive-path-before-more-cpu)

## Local AI platforms

22. llama.cpp on an M2 Max 64 GB (2026-05-31): dense 7B Q4_K_M 521 prefill / 36.9 decode tokens/s; 30B-A3B MoE Q4_K_M 455 / 47.3; about 15 GB swap in use with the 30B loaded. VERIFIED_PRIMARY for that
    machine (measured).
    - Why: the calibration set in the general reference.
    - Evidence: `ME/llm-m2max/docs/reports/llamacpp-m2max-benchmarks.md`; `ME/llm-m2max/docs/reports/baseline-diagnostics-20260530.md`
    - Applies: [Measured local results and benchmark method](../../../skill-systems-architect/references/ai-inference-platforms.md#measured-local-results-and-benchmark-method)
23. A second engine's report concluded llama.cpp was 2.7-3.4x faster, but its runs used short UI generations on another day; a 7B slower than a 14B and a 32B coder at 1.6 tokens/s point to a broken
    method.
    - Why: compare engines on one harness only.
    - Evidence: `ME/llm-m2max/docs/reports/llamacpp-vs-omlx-comparison.md`
    - Applies: [Measured local results and benchmark method](../../../skill-systems-architect/references/ai-inference-platforms.md#measured-local-results-and-benchmark-method)
24. Hybrid routing: hosted model by default, local models for frequent short tasks, a local MoE fallback, a 30K-token gate below a 32,768 server window; a routing audit found one of six routes broken
    by a missing base URL and key, and a reasoning model returning reasoning tokens with no visible text.
    - Why: gateway seam, context gate and end-to-end route tests.
    - Evidence: `ME/llm-m2max/docs/reports/hermes-model-routing.md`
    - Applies: [Gateways, routing and rented GPUs](../../../skill-systems-architect/references/ai-inference-platforms.md#gateways-routing-and-rented-gpus)
25. Rented GPU node design (not deployed): provider-specific provisioning only, then the same automation and container stack; code and durable state in separate trees; ports bound to localhost and
    reached over an overlay network.
    - Why: thin provider seam; never publish an unauthenticated inference API.
    - Evidence: `ME/gpu-rental-orchestrator/ARCHITECTURE.md`
    - Applies: [Gateways, routing and rented GPUs](../../../skill-systems-architect/references/ai-inference-platforms.md#gateways-routing-and-rented-gpus)
26. An AI strategy ADR claimed a 273 GB/s desktop box runs 70B+ models "at production inference speed"; the bandwidth bound gives single-digit tokens/s per stream for a 4-bit 70B model, so the claim
    needs measurement.
    - Why: check vendor speed claims with bandwidth / bytes per token.
    - Evidence: `APN/ai-strategy/07-decisions/adr/` (ADR-005)
    - Applies: [Serving engines and hardware](../../../skill-systems-architect/references/ai-inference-platforms.md#serving-engines-and-hardware)

## Withheld evidence paths

- The flash-wear executive summary under `APN/smc-file-writing-analysis/docs/audits/` carries a site or node code in its file name; it is cited by folder only (item 5).
- The resolver review and tuning plans under `APN/docs/customer-resolvers/` carry resolver host names in their file names; cited by folder only (item 21).
