---
Title: Operator context - site boxes and platforms
Category: operator-context
Status: current
Authority: internal
Scope: One operator's site-box fleet, colocation, platform and AI work plus the operator's personal AI platform projects; not general guidance
Last reviewed: 2026-11-10
Summary: >-
  Operator-specific lessons behind the systems-architect references: site-box images, flash wear, hangs and power, telemetry spool, colocation power, Ceph and
  platform choice, resolver tuning and local AI measurements; items 27 to 39 (2026-11-10) add the site-box platforms, image design decisions, identity, controller
  role and lab results. Each item gives the fact, why it matters, an evidence path and the general section it applies to.
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
- [Site-box platforms in detail](#site-box-platforms-in-detail)
- [Site-box image design state](#site-box-image-design-state)
- [Site-box identity and management](#site-box-identity-and-management)
- [Site-box lab proof](#site-box-lab-proof)
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

> **Learned 2026-11-10** · APN site boxes, fleet survey (read-only, 79 boxes probed, 306 of 312 Pis censused) · VERIFIED_PRIMARY · Source:
> smc-resiliency `docs/overview/smc-fleet-survey-20261110_1145.md` @ 6f45ec65 · Falsifier: a later census or survey reading otherwise.
> - Pi bootloaders: 2023-01-11 x260, 2022-04-26 x36 (rct), 2022-01-25 x10 (rct, all Rev 1.4 boards); A/B on GPT is proved on 2023-01-11 and
>   2026-01-09 only. Every surveyed Pi: 7.8 GB RAM, Ubuntu 22.04.1, AFNI0 62 GB card, MBR.
> - nbn_wh runs a writable root (`overlayroot` disabled in its config): 5 to 6 GB a day to the card, against 10 to 20 MB on rct and wh.
> - Undervoltage since boot on 5 of 20 wh and 3 rct; canteen-creek and kundat-djaru logged it every few seconds (2026-11-10 12:04).
> - x86 (BOXER-6404 BIOS B404BM14, BOXER-6641 B641HM20; Ubuntu 22.04.1, .3, .4): no box loads a watchdog; nbn_accelerate writes 5.6 to 44.5 GB
>   a day (cron jobs, the journal); koonibba-smc01's root was 98% full (`/url_capture` 13 GB).
> - Six census misses: the backdoor tunnel was up on four (the box runs, the Teleport agent does not answer), down on two.

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

## Site-box platforms in detail

Added 2026-11-10 from the smc-resiliency records (state at apn 8295a792). `SMC` means `APN/smc-resiliency`; `UNC` means `APN/unified-network-controller`.

27. Pi flavours (`rct`, `wh`, `nbn_wh`) run a Raspberry Pi 4 Model B from an SD card with no real-time clock; the fleet bootloader is 2023-01-11 on six canaries read; cards read live on five Pis
    were 62 GB with card name `AFNI0` and `manfid` 0x000000. Two sources disagree and are both kept: skill-smc 07 says 8 GB RAM and "Swissbit industrial microSD"; the lab profile `pi4` says 4 GB
    ("RAM per board UNVERIFIED") and the Pi design calls the card unbranded.
    - Why: no RTC means a time floor from the release build stamp; the bootloader the fleet runs, not the newest, is the one a boot change must be proved on.
    - Evidence: `SMC/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` (sections 4, 7, 9.1); `SMC/lab/targets.toml` (profile `pi4`); `SMC/docs/trackers/plan-tracker.md` (S0 row);
      `SMC-SKILL/references/07_hardware-overlay.md` (section 7)
    - Applies: [Decision rules](../../../skill-systems-architect/references/edge-appliances.md#decision-rules)
28. x86 flavours (`rcp`, `nbn_accelerate`) run AAEON BOXER-6404 (4 cores, 7 GB, one 60 GB CFast, LVM root with no free space) or BOXER-6641 (6 cores, 15 GB, two 119 GB SSDs fitted); UEFI; no
    watchdog loaded on either; Ubuntu 22.04, systemd 249, kernels drifting from 5.15.0-79 to -133. Every x86 watchdog driver on disk is on Ubuntu's deny-list, so `modules-load.d` will not load
    it; an explicit `modprobe iTCO_wdt` bound on a lab VM and a crash reset itself in 91.1 s (BOXER runs still to do). Counts disagree: 47 x86 boxes by model including non-site boxes (skill-smc
    07, 2026-10-22), 34 x86 Devices in Nautobot (UNC `ARCHITECTURE.md`), "36 remote boxes" (UNC D12.2).
    - Why: an image that names no model must still load a named watchdog driver; size every layout against the smallest disk in service (the CFast capacity gate, decided 20261021_1155).
    - Evidence: `SMC/docs/x86/x86-smc-resiliency-plan-20261014_1436.md` (sections 3, 6.2, 6.7); `SMC/docs/overview/smc-lab-test-record-20261107_1931.md` (section 14);
      `SMC-SKILL/references/07_hardware-overlay.md` (Whole x86 fleet by model)
    - Applies: [Hangs, watchdogs and power](../../../skill-systems-architect/references/edge-appliances.md#hangs-watchdogs-and-power)

## Site-box image design state

The design as a whole is still a proposal proved stage by stage (S0 to S6 and SM on the Pi, X0 to X7 and XQ on x86); items below marked decided carry the operator's stamp from `SMC/SCRATCHPAD.md`
Recent decisions or `SMC/docs/history/`.

29. Rescue layout decided (operator, 20261105_2052): Layout 2, production A/B, recovery A/B and a factory R0, plus identity A/B/R, on one medium: 15 partitions on the Pi (boot p2 to p6, roots p7 to
    p11, identity p12 to p14, writable p15); the x86 plan proposes the same layers on its one disk (10 partitions, about 21 GB of the 60 GB CFast), not decided. The Pi firmware's `PARTITION_WALK`
    checks partitions 1 to 8, which covers the boot partitions; the 15-partition boot path is still to be proved on the bench (R1, R30).
    - Why: the only layout meeting the plan's rescue tests while a recovery slot is rewritten; its risk sits in firmware, so it is proved before it is built in number.
    - Evidence: `SMC/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` (4.1); `SMC/docs/x86/x86-smc-resiliency-plan-20261014_1436.md` (6.2); `SMC/CHANGELOG.md` (20261109_2134)
    - Applies: [Image layout and updates](../../../skill-systems-architect/references/edge-appliances.md#image-layout-and-updates)
30. Decided since 2026-10-29: root filesystem erofs only, every writer given a home, a RAM dm-snapshot rejected after measuring (R28, 20261107_1617); x86 boot selection by RAUC's `efi` backend
    (`BootNext` trial, `BootOrder` commit) with `grub` the fallback (C8, 20261107_1617); x86 kernels in a folder per slot on one shared ESP, written before the trial is armed (20261107_2105);
    the health check judges units before against after, so a unit already failed never reverts a change (20261107_2338). Still open: the Pi's RAUC custom backend or U-Boot (S1), whether a
    release trial waits for reach during an outage (S6), the reach ladder for losing the controller (proposed).
    - Why: each was settled by a lab finding (three good sets reverted over a unit that needs the internet; root-write measurement), which is the pattern to copy.
    - Evidence: `SMC/SCRATCHPAD.md` (Recent decisions 20261107_1617, 20261107_2105, 20261107_2338); `SMC/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` (9.1, 9.2, 9.4)
    - Applies: [Image layout and updates](../../../skill-systems-architect/references/edge-appliances.md#image-layout-and-updates)
31. A disposable writable area recovers in a decided order (operator, 20261105_2052, 20261105_2053, 20261105_2059): a bad area fails a release trial; on a committed release the box repairs in place
    at once and alarms; a second repair within 7 days waits 24 hours for the controller; if the controller stays away the box switches to the other production set; both sets failing boots
    recovery, then R0. The repair counter lives on the boot control partition, because the area cannot count itself.
    - Why: repair first keeps the box's way home (Teleport's data directory lives on the area); the controller decides before the box switches on its own.
    - Evidence: `SMC/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` (4.2, 4.3)
    - Applies: [Lifecycle and recovery](../../../skill-systems-architect/references/fleet-management.md#lifecycle-and-recovery)
32. Time: the Pi has no RTC, so the image build stamps `/usr/lib/clock-epoch` with the release build time (systemd advances the clock to it at boot), chrony takes the controller or gateway by
    address as first source, and the health check's clock line passes on a synchronised source or, offline, at or after the floor (R25, decided 20261105_2052).
    - Why: a box never runs earlier than its release, and time arrives before DNS.
    - Evidence: `SMC/docs/pi/pi-immutable-smc-image-design-20261014_0850.md` (9.1)
    - Applies: [Telemetry spool and time](../../../skill-systems-architect/references/edge-appliances.md#telemetry-spool-and-time)

## Site-box identity and management

33. Identity is read-only A/B plus a factory copy R. The device key pair is made by the factory station at issuance and remade at every reset (20261022_1407, 20261022_1426); secrets travel sealed
    to the box with `age` to a separate X25519 key, are decrypted at boot into a tmpfs credentials directory and read by services with `LoadCredential=` (R32 mechanism, decided 20261107_2047);
    the storage ID (SD CID or disk serial) is the controller's lookup key, never authentication, with the lowest burned-in MAC as fallback (CD10, decided in UNC 2026-10-22); a box joins a
    bootstrap Teleport identity, then a production one. The Teleport join method is open.
    - Why: a box rebuilt while the controller is away still serves its site; a cloned card cannot release secrets.
    - Evidence: `SMC/docs/recovery/identity-partition-and-data-recovery-20261014_1455.md` (sections 2, 6, 7); `SMC/SCRATCHPAD.md` (20261107_2047)
    - Applies: [Identity trust chain](../../../skill-systems-architect/references/security-and-service-identity.md#identity-trust-chain)
34. The controller's role is recorded in UNC's options register D12, decided for P0 only (ansible-wifi roles on Ubuntu 22.04, no remote A/B conversion of deployed boxes); the read-only images are
    D12.5 (proposed) and D12.6 (direction chosen 2026-10-14, mechanism not adopted); smc-resiliency's items are candidates CD1 to CD21, of which only CD10 is decided. The SMC to UNC contract
    (U1 to U14, JWS-signed) has ten interfaces proved on the box against a lab-only stand-in, U9, U12 and U13 proposed; v0.2 went to UNC 20261107 and a 0.3.0 issue binding was proposed
    20261109. The register's D12.6 text still predates C8 and R28.
    - Why: the box design runs ahead of the controller; read the register for what UNC has accepted, and the box project for what it proposes.
    - Evidence: `UNC/docs/architecture/decisions/tech-stack-options-register-20260920_1241.md` (D12); `SMC/docs/overview/smc-unc-interface-control-20261107_2025.md`; `SMC/SCRATCHPAD.md` (outbox)
    - Applies: [Source of truth and field ownership](../../../skill-systems-architect/references/fleet-management.md#source-of-truth-and-field-ownership)
35. Imaging is built for the controller to reuse on any device and medium (decided 20261109_2134): the builder makes an image file only, the layout is data per platform, and a separate flash step
    checks its target, writes only when applied, reads the medium back against the image hash and records the medium ID with that hash.
    - Why: the read-back record is the identity binding the controller needs at issuance.
    - Evidence: `SMC/.archcore/rules/imaging-reusable-for-unc.rule.md`
    - Applies: [Supply and configuration chain](../../../skill-systems-architect/references/provisioning-and-lifecycle.md#supply-and-configuration-chain)

## Site-box lab proof

36. Lab rigs: arm64 Parallels VMs through Vagrant for the Pi's OS, agent and config; x86 VMs with OVMF on a Proxmox node built from scratch by OpenTofu with a least-privilege token; a bench Pi 4 on
    a serial console; a BOXER-6641 at the bench from 2026-11-10. One lab package of logic over transport and power adapters runs the same cases on every rig, and every test is recorded verbatim
    with raw logs and images archived off the repository.
    - Why: a VM proves logic only: OVMF rewrites `BootOrder` itself, and the arm64 VM stands in for Pi tryboot with UEFI `BootNext`, so firmware claims wait for hardware.
    - Evidence: `SMC/lab/README.md`; `SMC/.archcore/rules/lab-is-one-package.rule.md`; `SMC/docs/overview/smc-lab-test-record-20261107_1931.md` (section 1)
    - Applies: [Failure modes and tests](../../../skill-systems-architect/references/edge-appliances.md#failure-modes-and-tests)
37. Results to 2026-11-09: site-config cases E1 to E7 8 of 8 on both VMs; claim cases C1 to C9 9 of 9 against the stand-in; x86 A/B (X2) good trial, broken kernel, panic and power cut pass, a hang
    recovered only by the lab's reset; arm64 A/B logic (S1V) 8 of 8 after the commit fix; bench Pi (S1, bootloader 2026-01-09) reads the selection file on GPT, trials B and returns, commits a good
    trial and rejects after the retry bound. Still to run: bootloader 2023-01-11, Layout 2, a hang through the Pi watchdog, broken kernel, power cut, and both on a BOXER.
    - Why: a hang test passed by a lab reset proves nothing about the watchdog; record which recovery actually acted.
    - Evidence: `SMC/docs/overview/smc-lab-test-record-20261107_1931.md` (sections 2, 11, 13, 15 to 19); `SMC/SCRATCHPAD.md` (Next actions 20261109_2316)
    - Applies: [What each probe does not prove](../../../skill-systems-architect/references/observability-and-incident.md#what-each-probe-does-not-prove)
38. Two lab traps: a power cut during write, sync and rename on the vfat boot partition left a 0-byte selection file (the rename reached the disk, the data did not), answered by a fixed-length
    in-place write and a boot-time repair from the running slot (20261108_0128); Ubuntu 24.04.5's packaged Pi firmware could not boot a non-first GPT boot partition and flash-kernel copies it
    back on kernel updates, so the image ships and pins newer firmware. Open for the R1.2 review: nothing resets a Pi that freezes before Linux starts.
    - Why: rename is not atomic on FAT; firmware outside the OS is part of the image.
    - Evidence: `SMC/docs/overview/smc-lab-test-record-20261107_1931.md` (sections 15, 19); `SMC/SCRATCHPAD.md` (open item 20261109_2316)
    - Applies: [Image layout and updates](../../../skill-systems-architect/references/edge-appliances.md#image-layout-and-updates)
39. Sources that disagree, recorded 2026-11-10 and not resolved here: the Pi design still marks S1 parked while the trackers show it running; the target map shows X0 not started while the x86 plan
    records it done in part; skill-smc 01 still says the A/B mechanism is undecided with no x86 plan; this note's sister systems reference (edge-appliances, Learned 2026-11-10) reports both Pi
    bootloaders tested while the committed record shows only 2026-01-09.
    - Why: read the owning project's tracker and SCRATCHPAD before quoting a design's stage text.
    - Evidence: `SMC/target-map.yaml`; `SMC/docs/trackers/plan-tracker.md`; `SMC-SKILL/references/01_overview.md` (section 2)
    - Applies: [Evidence labels and layers](../../../skill-systems-architect/references/architecture-method.md#evidence-labels-and-layers)

## Withheld evidence paths

- The flash-wear executive summary under `APN/smc-file-writing-analysis/docs/audits/` carries a site or node code in its file name; it is cited by folder only (item 5).
- The resolver review and tuning plans under `APN/docs/customer-resolvers/` carry resolver host names in their file names; cited by folder only (item 21).
