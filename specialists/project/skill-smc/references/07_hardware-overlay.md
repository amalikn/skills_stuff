# SMC Hardware and Overlayroot

## Contents

- [7. Hardware Differences: x86 vs Raspberry Pi](#7-hardware-differences-x86-vs-raspberry-pi)
- [8. Overlay Filesystem (Critical Concept)](#8-overlay-filesystem-critical-concept)
- [Orphaned persistent journal after the volatile conversion (~44 GB fleet-wide, reclaimed 2026-07-28)](#orphaned-persistent-journal-after-the-volatile-conversion-44-gb-fleet-wide-reclaimed-2026-07-28)
- [Fleet status-probe gotchas — three checks that read as fleet-wide failures but are wrong paths (verified 2026-08-25)](#fleet-status-probe-gotchas-three-checks-that-read-as-fleet-wide-failures-but-are-wrong-paths-verified-2026-08-25)
- [Write-rate sweeps are blind to burst writers (2026-08-26)](#write-rate-sweeps-are-blind-to-burst-writers-2026-08-26)
- [The 24 h write baseline, and what two attribution passes buy you (2026-08-27/28 capture)](#the-24-h-write-baseline-and-what-two-attribution-passes-buy-you-2026-08-2728-capture)
- Hardware differences: x86 vs Raspberry Pi
- NBN Accelerate / NBN WH hardware inventory (first live fleet sweep)
- Overlay filesystem structure and runtime behavior
- Overlayroot status checks
- Ansible and overlayroot persistence
- Disable sequence
- Read-only migration status
- Verifying 12-fix parity on-box (probe gotchas + healthy-node write profile)
- rcp disk write profile
- Legacy url_capture disk-write behavior

## 7. Hardware Differences: x86 vs Raspberry Pi

**Corrected 2026-08-03 — the DNS and VoIP rows below were wrong, conflating platform (x86 vs ARM) with flavor-specific gates that are actually orthogonal to platform.** This table predates both the
2026-07-03 DNS correction (which fixed the same "unbound=RCT/bind=non-RCT" mistake in `02_service-map.md` but was never applied here) and the 2026-08-03 NBN Accelerate gap-fill — it went unnoticed
because no coherence sweep had re-checked this specific file against those corrections until today.

| Aspect             | x86 PC (`rcp`, `nbn_accelerate`)          | Raspberry Pi (`rct`, `wh`, `nbn_wh`)                                                                                                |
| ------------------ | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| CPU arch           | x86_64                                    | ARM64 (aarch64)                                                                                                                     |
| RAM                | 4–16 GB typical                           | 8 GB (Model 4B; measured 7807 MB — corrected 2026-09-03, was 1.9 GB)                                                                |
| Storage            | SSD or CFast (Innodisk CFast 3ME3 /       | **Always SD card** (Swissbit industrial microSD, monitored via `sbdm.py`/`sbdm-cli`) — USB storage may be physically present but is     |
|                    |   Transcend TS128GSSD420K confirmed       |   reserved for future use, not the root/primary storage device                                                                      |
|                    |   brands, monitored via                   |                                                                                                                                     |
|                    |   `smartmon.py`/`smartctl`)               |                                                                                                                                     |
| Swap               | Traditional swap partition                | zram (`/dev/zram0`, ~1.2 GB, compressed)                                                                                            |
| DNS                | **Not platform-determined — corrected**       | Same — Unbound + Stubby, unless `smc_ltp` (never applies to RPi flavors; `smc_ltp` is `rcp`-only)                                   |
|                    |   **2026-08-03.** Every flavor (both x86 and  |                                                                                                                                     |
|                    |   RPi) runs Unbound + Stubby              |                                                                                                                                     |
|                    |   (DNS-over-TLS) by default; the *only*     |                                                                                                                                     |
|                    |   hosts that get BIND/named instead are   |                                                                                                                                     |
|                    |   members of the `smc_ltp` inventory      |                                                                                                                                     |
|                    |   group — a static, `rcp`-only, 7-site    |                                                                                                                                     |
|                    |   allowlist, unrelated to CPU             |                                                                                                                                     |
|                    |   architecture. See `02_service-map.md`   |                                                                                                                                     |
|                    |   and `08_ansible-authoring.md` "smc_ltp  |                                                                                                                                     |
|                    |   Sub-Group".                             |                                                                                                                                     |
| VoIP | **Not platform-determined either —** | last == | Not deployed |
|  |   **corrected 2026-08-03.** Asterisk is gated |   'rcp'`), not "x86" generally — confirmed live 2026-08-03 that `nbn_accelerate` (also x86) does **not** have Asterisk (`systemctl |  |
|  |   to `rcp` specifically |   is-active asterisk` → inactive/not found on `warakurna-smc01`/`indulkana-smc01`). See `08_ansible-authoring.md` "Flavor/Cluster |  |
|  |   (`inventory_dir.split('/') |   Conditional Branching". |  |
| Antivirus/security | **`nbn_accelerate`** **only** (ClamAV + Lynis) —  | Not deployed on any RPi flavor                                                                                                      |
|                    |   confirmed live 2026-08-03 on            |                                                                                                                                     |
|                    |   `warakurna-smc01`/`indulkana-smc01`,    |                                                                                                                                     |
|                    |   both installed. `rcp` does not get this |                                                                                                                                     |
|                    |   despite being the same x86 platform.    |                                                                                                                                     |
| HA                 | keepalived (VRRP, built from source)      | Not deployed                                                                                                                        |
| Web apps           | Depends on flavor                         | Kohana + Laravel Tstik                                                                                                              |
| QoS                | tc via role (gated `rct`-only per         | networkd-dispatcher                                                                                                                 |
|                    |   `08_ansible-authoring.md` — silently    |                                                                                                                                     |
|                    |   no-ops on `rcp`/`nbn_accelerate`        |                                                                                                                                     |
|                    |   despite this row's platform framing;    |                                                                                                                                     |
|                    |   see `13_known-issues.md`)               |                                                                                                                                     |
| Kernel modules     | Standard x86                              | RPi-specific                                                                                                                        |
| Ansible            | Same roles                                | OS-specific tasks in smc_network                                                                                                    |

**Both platforms** run the identical service stack (monitoring, DHCP, WiFi AP, Teleport tunnel, Prometheus) with flavor-specific differences handled by `when: ansible_architecture == 'aarch64'`
conditions in Ansible roles for genuinely platform-driven behavior — but as the DNS/VoIP/antivirus/QoS rows above show, **not every difference in this table is actually platform-driven**; several are
flavor-exclusive gates (`inventory_dir.split('/')|last == '<flavor>'`) or inventory-group gates (`smc_ltp`) that happen to correlate with platform for some rows and not others. Don't assume a row
applies to "all x86" or "all RPi" without checking whether it's gated by `ansible_architecture`, `hotspot_flavor`, or an exact flavor/group name — see `08_ansible-authoring.md` "Flavor/Cluster
Conditional Branching" for the full selector-mechanism reference.

### Storage health monitoring — two different tools, clarified 2026-07-13

The table above says x86 storage is "monitored by SBDM/SMART" — this undersells how split the two mechanisms actually are. Confirmed live 2026-07-13:

| Tool                 | Binary                        | Works on                               | Fails on                                                                                             |
| -------------------- | ----------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `smartmon.py` (wraps | n/a (uses system `smartctl`)  | x86 rcp: Innodisk CFast, Transcend SSD | RPi/mmcblk SD cards — `smartctl --scan-open` finds zero devices; SD/eMMC doesn't expose classic ATA  |
|   `smartctl`)        |                               |   (both report via ATA SMART)          |   SMART attributes the way SATA/USB-SAT drives do                                                    |
| `sbdm.py` (wraps     | `roles/smc_node_exporter/\`   | RPi/rct/wh: genuine Swissbit-branded   | x86 rcp: Innodisk/Transcend hardware isn't Swissbit-branded — `sbdm-cli` returns "No supported disks |
|   `sbdm-cli`,        |   `files/{x86-64,aarch64}/\`  |   industrial microSD cards (model "SD  |   found" (exit 3), and `sbdm.py` currently exits 0 with **zero stdout output**, producing a 0-byte       |
|   "Swissbit Device   |   `sbdm-cli` — deployed to    |   card SB AFNI0", series S-58)         |   `sbdm.prom`. This is the root cause of the standing "sbdm.prom = 0 bytes" bug tracked as a known   |
|   Manager")          |   **both** architectures          |                                        |   issue on tjuntjuntjara/burringurrah/warburton — expected behavior for non-Swissbit hardware, not a |
|                      |                               |                                        |   bug in those specific nodes.                                                                       |

So: x86 rcp nodes are monitored by `smartmon.py`/`smartctl` only (SBDM silently no-ops there). RPi rct/wh nodes are monitored by `sbdm.py`/`sbdm-cli` only (SMART silently no-ops there, confirmed
`smartmon.prom` has metric headers but zero data lines on every RPi node checked). Never assume both tools produce meaningful data on both platforms.

### Transcend SSD wear metric — firmware limitation, fixed fleet-wide (found 2026-06-02, root-caused 2026-07-13, Part 1 shipped + confirmed live 2026-07-17)

Transcend TS128GSSD420K (BOXER-6641 nodes: mornington, bidyadanga, horn-island, warburton) used to report `smartmon_attr_value` = **100 for every single SMART attribute**, not just
`remaining_lifetime_perc` — confirmed via full `smartmon.prom` comparison against a working Innodisk CFast node. This was a firmware limitation (Transcend doesn't implement SMART VALUE normalization
at all on this model), not something `smartmon.py` got wrong — the script mirrors whatever the drive reports, faithfully, for both hardware classes identically.

`RAW_VALUE` (`smartmon_attr_raw_value`) being correct on both vendors was the original workaround (ADR-002, RULE-005, both dated 2026-06-02), superseded 2026-07-13 by a collector-level fix — see
`docs/audits/smartmon-active-disk-value-fix-plan-20260713_1310.md` Part 1 — that makes `smartmon_attr_value` itself directly correct. **Status as of 2026-07-17: Part 1 is deployed fleet-wide and
confirmed live via direct Prometheus query**, not just the 2/12-node state recorded 2026-07-13 ~17:33 — all 4 BOXER-6641 nodes now return distinct, plausible per-disk values on the active Transcend
disk (mornington sdb=90%, bidyadanga sdb=91%, horn-island sda=100%, warburton sda=100%; idle standby disks correctly still read ~100%, near-zero writes). `smartmon_attr_raw_value` now returns **zero
series fleet-wide** — the raw-value workaround is fully retired, not just deprecated. The fix also covers `temperature_celsius`, which had the identical VALUE=100 bug and the identical fix
precondition. **Do not point new dashboards/alerts at `smartmon_attr_raw_value`** — it has no data to query. See `docs/disk-write-rates-20260716.md` for the live-query evidence and ADR-002 for the
supersession record. The earlier interim relabel fix mentioned in older revisions of this note was reverted before Part 1 implementation began — it is dead, do not deploy it anywhere.

### RPi/Swissbit microSD wear metrics — genuinely low fleet-wide usage, not a bug (investigated 2026-07-13)

`sbdm_device_attribute{name="remaining_erase_life_time"}` reads exactly `100.0` fleet-wide (298/298 reporting sites, zero exceptions) — investigated as a possible bug matching the Transcend pattern
above, concluded **genuine**: even the single busiest RPi node found fleet-wide (`rollah-smc01`, 282,613 total erases, 1,972 power cycles — both far above every other node sampled) has an average
erase count of only 312 against a 60,000-cycle rated budget (~0.5% used). Confirmed directly against Swissbit's own human-readable `sbdm-cli` output, not just CSV parsing — not a parsing bug.
`remaining_spare_blocks` (a different, discrete metric tracking physically failed/retired NAND blocks) *does* show real variance (5/298 sites below 100%, down to 93% on `rollah-smc01`) — proves the
pipeline can and does report differentiated data, it's specifically the erase-life percentage that's precision-starved (a coarse whole-number field) at this fleet's current usage level, not broken.

A plan to add real, currently-useful usage metrics (`docs/audits/smartmon-active-disk-value-fix-plan-20260713_1310.md` Part 2 — **not yet approved**) would extend `sbdm.py` to also publish
`average_erase_count`, `total_erase_count`, `power_on_cycles`, and a computed `estimated_remaining_lifetime_perc` (full float precision instead of Swissbit's coarse integer) — none of which `sbdm.py`
currently publishes despite the raw `sbdm-cli` CSV output already containing them.

**Also found**: 4 RPi nodes (`malupirti-smc01`, `orrtipa-thurra-bonya-smc01`, `rocket-bore-smc01`, `yuelamu-smc01`) genuinely lack overlayroot — root mounted directly from `/dev/mmcblk0p2 ext4`, a
real writable device, not the `overlayroot` pseudo-source seen on the rest of the RPi fleet. Operator-confirmed 2026-07-13: these are recently-replaced SMCs, expected to lack overlayroot at this
stage, not itself an urgent finding — but a real, live example of exactly the write-exposure this project exists to catch, worth revisiting once these units complete their overlayroot rollout.

### Mismatched Transcend SSD pairs on BOXER-6641 — now a recurring pattern (3 nodes confirmed 2026-07-17→2026-07-21)

Three rcp nodes discovered live in Teleport outside the original 12-node ansible-wifi inventory (beagle-bay-smc01, pandanus-park-smc01 2026-07-17; old-looma-smc01 2026-07-21) all run BOXER-6641
chassis with a **mismatched Transcend SSD pair** — `TS128GSSD472K` and `TS128GSSD460KI-VS1` on the same node, one active one standby, roles swapped between nodes (beagle-bay: active=472K,
standby=460KI-VS1; old-looma: active=460KI-VS1, standby=472K) — unlike the 4 fleet-standard BOXER-6641 nodes (mornington, bidyadanga, horn-island, warburton), which run a matched `TS128GSSD420K` pair.
Worth treating as an expected trait of nodes provisioned outside the main ansible-wifi rollout, not a per-node anomaly to re-investigate each time. `Wear_Leveling_Count` raw=0 on both old-looma disks
(near-new) at first audit.

### Same 3 nodes: `smartmon.py`'s `remaining_lifetime_perc` didn't publish — fixed 2026-07-21 (attribute-169 name-resolution gap, not a hardware limitation)

Found 2026-07-17, root-caused and fixed 2026-07-21: beagle-bay's/old-looma's Transcend pair (`TS128GSSD472K`/`TS128GSSD460KI-VS1`) and pandanus-park's Transcend CFast (`TS64GCFX600`) — the same 3
non-standard models from the section above — all report SMART attribute id **169** as smartctl's generic `Unknown_Attribute` placeholder rather than a resolved name, because these specific models
aren't in smartctl's drivedb. This is a *different* limitation from the original Transcend `VALUE`-column bug (Part 1, 2026-07-13 — that one affected `TS128GSSD420K` and was about the VALUE column
being uniformly wrong, not about name resolution) — don't conflate the two when triaging a "wear metric missing" report on this fleet; check which failure mode it actually is before assuming it's
already covered by Part 1.

Fixed at the collector (`roles/smc_node_exporter/files/smartmon.py`, `collect_ata_metrics`): before the whitelist-skip check, rewrite the id-169 `Unknown_Attribute` placeholder to
`remaining_lifetime_perc`, scoped narrowly (both the id **and** the placeholder name must match) so any drive smartctl already resolves correctly (e.g. Innodisk CFast 3ME3, unaffected) is untouched.
Deployed live via `smc_prometheus.yml --tags node_exporter` to all 3 affected nodes, confirmed end-to-end in central Prometheus (beagle-bay 100%/100%, pandanus-park 99% — matching the previously
manually-recovered figures exactly). `smartmon.py` remains **uncommitted** in ansible-wifi. See `docs/log-audit-results.md` `20260721_1830` in smc-file-writing-analysis for the full live-verification
narrative.

**Correction (live `tsh ssh` root-cause 2026-07-23, `disk-write-rates-20260723.md` Live Audit Addendum):** the "all 3 affected nodes" claim above held for **beagle-bay and pandanus-park only**. The
two looma nodes are both unpublished but for **entirely different reasons — don't treat them as one gap:**

- **old-looma-smc01** (same `TS128GSSD472K`/`TS128GSSD460KI-V` Transcend pair): its `/usr/local/lib/smartmon.py` is still the **pre-fix version** — no id-169 rewrite present (grep for
  `169`/`Unknown_Attribute` returns nothing). The 07-21 fix was **never actually applied here** (the confirmation only ever cited beagle-bay/pandanus-park values, never old-looma's). `smartctl -A
  /dev/sda` attr 169 = `Unknown_Attribute` RAW=100 → real wear **100%**, data present, just unnamed. **Secondary bug:** old-looma publishes `smartmon_active_disk_remaining_lifetime_perc 0.0` — a
  **false 0%** (the gauge defaults to 0.0 when the per-attribute value can't be resolved, instead of going absent — could trip a wear alert). **Fix:** redeploy the already-fixed `smartmon.py` via
  `smc_prometheus.yml --tags node_exporter`; no new code needed.
- **new-looma-smc01** (BOXER-6404, **standard Innodisk CFast 3ME3**): **no monitoring stack at all** — `node_exporter` inactive, no textfile_collector dir, `smartmon.py` absent, no Graylog sidecar, no
  tmpfs mounts, overlayroot disabled, plain LVM root. Ungoverned node. Its Innodisk disk resolves attr 169 natively (`Remaining_Lifetime_Perc VALUE=099` → **99%**), so it needs **no collector code
  fix** — just the standard ansible-wifi onboarding + full 12-fix stack. Its 446 MB/day is an idle-baseline, not a fixed-state figure.

### `fatrace` not installed on ungoverned nodes — audit-methodology gotcha (found 2026-07-21, old-looma-smc01) — standing fix: install it, don't just substitute

Every prior live audit in this project used `fatrace`'s 60s true-write count as the primary write-rate evidence (see `AGENTS.md` "Live Audit Procedure"). `fatrace` is installed as part of the
ansible-wifi rollout, not present on the base OS image — a node discovered live but never touched by any ansible-wifi playbook (old-looma-smc01, first case found) will not have it. Don't assume
fatrace availability when auditing a node without confirmed ansible-wifi history — check `which fatrace` first before spending time on a filter/capture command that silently returns nothing.

**Standing policy as of 2026-07-21: install it, don't just work around it.** `apt-get install -y fatrace` on any rcp node found missing it, then re-run the standard 60s true-write capture — do not
settle for the `iostat -xd <interval> <count> <device...>` per-device substitute as a final answer, it gives directional evidence only (no per-process attribution). On old-looma-smc01 the install was
a clean one-package `apt-get` (`fatrace_0.16.3-1`, pulled in `powertop` as a dependency, no service restarts triggered) — confirmed low-risk on a plain rw-ext4 rcp node. The real fatrace capture after
install surfaced a write surface the iostat-only pass had missed entirely: `python3` writing 24 times/60s to `/var/local/cnmaestro-provisioning/` (130M, 116 files) — a path this project's own
`AGENTS.md` inventory had listed at the wrong location (`/var/log/cnmaestro-provisioning/`, which doesn't exist on this node), now corrected. Same lesson as the `iostat`-only limitation above: a
substitute methodology doesn't just lose precision, it can miss entire write surfaces that only show up in a true per-process syscall trace.

### Verifying 12-fix parity on-box — two probe gotchas + what "healthy" looks like (2026-07-22)

When re-auditing whether the fleet's write-reduction fixes are actually applied on a node (as opposed to trusting a deployment recap), check each fix's **durable on-box artifact** — the mount,
symlink, masked unit, journald drop-in, or published metric — not the ansible run result. Two naive probes give false negatives; use the corrected form:

- **Fluent Bit is NOT a standalone systemd unit on this fleet.** `systemctl is-active fluent-bit` returns inactive even when it is running correctly. Fluent Bit is spawned as a **child process of
  `graylog-sidecar`** (`/opt/fluent-bit/bin/fluent-bit -c /var/lib/graylog-sidecar/generated/<id>/apn-gelf-http.conf`). Verify with `pgrep -a fluent-bit` (or confirm it appears under the sidecar
  cgroup in `systemctl status graylog-sidecar`), never with `systemctl is-active`.
- **`apt_info.py` lives at `/usr/local/lib/apt_info.py`** (confirmed on beagle-bay/pandanus-park/ old-looma), not `/var/lib/node_exporter/` or `/usr/local/bin/`. A locator that guesses the wrong
  directory will make a "no live `cache.update()`" check pass vacuously. Locate with `find / -name apt_info.py` first, then `grep -nE '^[^#]*cache\.update\(\)'` on the real path — the only legitimate
  occurrence is the explanatory comment, so any *uncommented* hit is a regression.

Other durable signatures (all `findmnt -rno FSTYPE <path> | grep tmpfs` or `systemctl is-enabled … | grep masked`): journald `Storage=volatile` drop-in under `/etc/systemd/journald.conf.d/`;
`url-capture.service` active + `/run/url_capture` tmpfs (**unit name is `url-capture`, hyphen, not `url_capture`**); `status.json` a symlink; `apt-daily`/`apt-daily-upgrade`/`apt-news`/`esm-cache`/
`unattended-upgrades` all `masked`; `/tmp`, `/var/lib/node_exporter/textfile_collector`, `/var/lib/prometheus` all tmpfs; `remaining_lifetime_perc` present in `textfile_collector/smartmon.prom`.

**What a healthy post-fix rcp node looks like in a 5-min fatrace capture (2026-07-22, all 3 new nodes):** none of the 12 fixes' target surfaces appear anywhere in the top writers — no apt/gpgv churn,
no url_capture `.pcap`, no prometheus WAL/TSDB, no `status.json`, no textfile `.prom` hitting disk. The residual top writers are the **fleet-wide known-open backlog**, not regressions:
`/var/log/syslog` (rsyslogd, dominant — rcp has no overlayroot so it writes straight to ext4; the rsyslog 3-group split + Fluent-Bit-systemd-input migration per ADR-006 is the next disk-reduction
target, not one of the 12 fixes), `squid/access.log` and `mosquitto.log` (drafted-not-deployed STOP/STREAM dispositions), `interfacecheck.log` (parser-bug writer, fix committed `ae838c2`, deploy
deferred), and `asterisk/astdb.sqlite3-journal` (SQLite WAL churn, low, LOCAL-KEEP-class). Totals landed 1070–1627 true-writes/300s, in-family with the governed fleet's 538–1624 range — so a node
sitting in that band with syslog/squid/mosquitto on top is behaving normally, not carrying an undeployed fix. Full evidence: `docs/log-audit-results.md` `20260722_2020`/`20260722_2028`.

---

### NBN Accelerate / NBN WH Hardware Inventory (first live fleet sweep, 2026-08-03)

No live hardware inventory existed for this cluster before this sweep — everything below is from direct `tsh ssh` capture against all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh` hosts (28
total, `aurukun-smc03` unreachable at capture time), via `scripts/collect-fleet-health.sh`. **`nbn_wh` is the operator-confirmed `wh`-flavor equivalent on this cluster** — compare it against the
`rct`/`wh` row in the platform table above, not against `nbn_accelerate`'s x86 baseline.

| Chassis                            | Count | CPU                       | RAM   | Storage                                                   | Flavor           | Kernel                               |
| ---------------------------------- | ----- | ------------------------- | ----- | --------------------------------------------------------- | ---------------- | ------------------------------------ |
| AAEON BOXER-6641                   | 11    | Intel Core i5-8500T @     | 15Gi  | Transcend TS128GSSD420K SSD                               | `nbn_accelerate` | `5.15.0-119-generic` (fleet-uniform) |
|                                    |       |   2.10GHz                 |       |                                                           |                  |                                      |
| AAEON BOXER-6404                   | 15    | Intel Celeron J1900 @     | 7.7Gi | Innodisk CFast 3ME3                                       | `nbn_accelerate` | `5.15.0-117-generic` (2 outliers —   |
|                                    |       |   1.99GHz                 |       |                                                           |                  |   see below)                         |
| Raspberry Pi, Cortex-A72 (`-raspi` | 2     | ARM64, 4-core Cortex-A72  | 7.6Gi | Swissbit SB AFNI0 microSD (`sbdm.prom` populated,         | `nbn_wh`         | `5.15.0-1064-raspi` /                |
|   kernel, no dmidecode)            |       |                           |       |   `smartmon.prom` header-only — same split as `rct`/`wh`) |                  |   `5.15.0-1078-raspi`                |

Same BOXER-6641/BOXER-6404 chassis family already documented for the `rcp` fleet (`amata-smc01` was independently confirmed BOXER-6641 during the earlier disk-fault incident) — this is not new
hardware, just the first time it's been inventoried for this specific cluster.

**Kernel/OS version drift, live-confirmed — corroborates the already-documented "no automated kernel-update pipeline for cw-cluster" structural finding** (`01_overview.md` "APN Cluster vs NBN
Accelerate Cluster"): most BOXER-6404 hosts run `5.15.0-117-generic`, but `koonibba-smc01` is on `5.15.0-79-generic` (significantly older) and `warakurna-smc01` is on `5.15.0-133-generic`
(significantly newer) — a wide, organic spread consistent with hosts being patched independently by hand rather than through a fleet-wide pipeline, exactly as predicted by the earlier structural
finding (apn-cluster has a Jenkins kernel-update pipeline; cw-cluster does not). OS point-release also varies: `22.04.1`/`22.04.3`/`22.04.4` seen across the fleet, no single dominant version.

**`nbn_wh` swap/zram discrepancy — not yet resolved.** Both `nbn_wh` hosts show `Swap: 0B` in `free -h` and no `zram0` device in `lsblk`, contradicting the "RPi flavor → zram swap" row in the platform
table above as a universal claim. Not established whether `nbn_wh` genuinely doesn't get zram (a real flavor-level difference from `rct`/`wh`), or whether the zram claim itself needs re-checking
against a live `rct`/`wh` host — this pack has not directly confirmed zram presence on `rct`/`wh` via `tsh ssh` either, only asserted it. Flag any zram-dependent troubleshooting step as unconfirmed
for `nbn_wh` until checked.

**`nbn_wh` overlayroot: not yet active, and that's expected — a planned-but-not-yet-executed rollout, confirmed by the operator 2026-08-03.** `smc_rise_deploy.yml` targets `nbn_wh` alongside
`rct`/`wh` (`inventory_dir.split('/')|last in ['rct', 'wh', 'nbn_wh']`), consistent with `nbn_wh` being the `wh`-equivalent flavor where overlayroot is the expected long-term state — but live `mount |
grep overlay` on both `nbn_wh` hosts returns nothing today. The operator confirmed this is simply pre-rollout current state (overlay is planned to be enabled on these 2 sites in the near future), not
a stalled or reverted deployment. Re-check after that rollout lands — see `13_known-issues.md` "Known Operational Bugs (NBN Accelerate cluster)" for the tracking row.

**Disk usage:** `koonibba-smc01` at 95% root disk usage is the fleet's clear outlier (next highest: `warakurna-smc01` at 65%; everyone else under 55%, most well under 35%) — combined with its
outlier-old kernel, this specific host looks overdue for a maintenance pass. Not investigated further this sweep (no directory-level `du` breakdown taken).

Full per-host data: `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` (relocated from `skill-smc/evidence/` per the evidence-retention policy in
`scripts/README.md`).

---

## 8. Overlay Filesystem (Critical Concept)

### Structure

```
/                          ← merged view (what you see at runtime)
├── upper dir: /media/root-rw/overlay   (tmpfs, volatile, ALWAYS 50% RAM - see below)
├── lower dir: /media/root-ro           (ext4, real filesystem, read-only at runtime)
└── workdir:   /media/root-rw/overlay-workdir/_

Real block device: /dev/sda1 or equivalent → mounted at /media/root-ro (60 GB on RPi)
tmpfs:             kernel default 50% of RAM (the configured size= is inert)
```

### Runtime Behavior

- All file writes go to tmpfs upper dir
- On reboot: upper dir is gone, lower dir reverts to original state
- `df -h` shows the tmpfs as `/dev/overlay` at `/`; real filesystem at `/media/root-ro`

### The copy_up cost model — size at first write, not write rate (established 2026-08-18)

**This is the single most important thing to understand about overlayroot on these boxes, and it is counter-intuitive.** overlayfs is copy-on-write at *file* granularity, not block granularity. The
first write to a file that lives in the lower (read-only) dir copies **the entire file** into the tmpfs upper layer before the write lands.

The overlay is therefore charged a file's **size at first write**, not its rate of growth:

- A 2.6 GiB log appended at 4 KB/min costs **2.6 GiB of RAM** the moment anything touches it.
- A 10 MB log appended at 4 MB/min costs **10 MB**.

The slow-growing giant is far more dangerous than the fast-growing small file, which inverts normal disk-space intuition.

**The budget is 50% of RAM, and `overlay.size_ratio` does not change it** (verified 2026-08-18 on overlayroot 0.47ubuntu1). Measured: **3.81 GiB on a 7.6 GiB Pi 4**, matching `df` exactly. See
"`overlay.size_ratio` is inert" below before doing any budget arithmetic — earlier notes in this pack used a 40% / ~3.05 GiB denominator and were wrong by about 22%.

Corollaries worth remembering:

- **Reading does not trigger copy_up.** Only writes do. A read-only filesystem scan is safe to run against live overlay-enabled production hosts — this is what makes fleet assessment practical.
- A file's presence in the lower dir is free. Its first modification is not. "It has been sitting there for months without a problem" says nothing about what happens when something appends to it.
- Deleting or truncating a file in the lower dir is *also* a write, and a delete costs a whiteout, not the file's size — so truncation is the cheap remedy, deletion cheaper still.

### `overlay.size_ratio` is inert — the budget is always 50% of RAM (verified at source 2026-08-18)

`inventories/{rct,wh,nbn_wh}/group_vars/smc_bases.yml` sets `overlay.size_ratio: 40`, and `roles/smc_rise_overlay/templates/overlayroot.conf.j2` renders it into
`overlayroot="tmpfs:swap=1,recurse=0,size=40%"`. **That `size=` does nothing.**

Why, from `/usr/share/initramfs-tools/scripts/init-bottom/overlayroot` on the box:

1. The `tmpfs|tmpfs:*` case strips the prefix, leaving `opts="swap=1,recurse=0,size=40%"`.
2. `parse_string "$opts" "," _RET_common_` turns every `key=value` into a shell variable, so `_RET_common_size=40%` *is* created. `parse_string` is a generic parser — it validates only that the key is
   alphanumeric (`safe_string`), and accepts any key without checking it against a known set. So there is **no error and no warning**.
3. Only five of those variables are ever read back (lines ~695-699): `swap`, `recurse`, `debug`, `dir`, `driver`. `_RET_common_size` is never referenced again.
4. The mount itself is unconditional and option-free (lines ~758-761):

   ```sh
   if [ "$mode" = "tmpfs" ]; then
           # mount a tmpfs using the device name tmpfs-root
           mount -t tmpfs tmpfs-root "${root_rw}" ||
                   fail "failed to create tmpfs"
   ```

5. With no `-o size=`, the kernel applies the tmpfs default: **50% of RAM**.

Confirmed on delye-smc01: `MemTotal` 7,995,328 kB (7.625 GiB), tmpfs at `/media/root-rw` = 3.812 GiB = exactly 50.0%, mount options `rw,relatime,inode64` with no `size=` present. The configured 40%
would have been 3.05 GiB.

Consequences:

- Do not tune `overlay.size_ratio` expecting an effect. Changing the real budget requires patching the initramfs script or remounting the tmpfs after boot.
- Any budget arithmetic must **measure** the tmpfs, not compute it. `rise_logcap.py` does this via `statvfs` on `/media/root-rw` (falling back to RAM/2), which is why
  `rise_logcaps_overlay_budget_bytes` matches `df` on every host tested.
- The failure mode is unchanged — only the denominator moves, and it moves in the *safe* direction (more headroom than assumed, not less).

### `recurse=0` — the escape hatch that is already unlocked (verified at source 2026-08-18)

Verified directly in overlayroot **0.47ubuntu1**, `/usr/share/initramfs-tools/scripts/init-bottom/overlayroot` line ~419:

```sh
if [ "$recurse" != "0" -o "$file" = "/" ]; then
        ...emit the overlay mount lines for this fstab entry...
else
        echo "$line"      # passed through VERBATIM
fi
```

`rct`/`wh`/`nbn_wh` already set `overlay.mount_options: "swap=1,recurse=0"`. With `recurse=0`, **only `/` becomes an overlay** — every other fstab entry is emitted unchanged and mounts as a real
read-write filesystem: unlimited size, persists across reboot, **zero overlay cost**.

This is the structural fix for overlay RAM exhaustion: put volatile paths (`/var/log`, the portal's `storage/logs`) on their own mount and file size stops mattering permanently, with no capping or
trimming required.

Two constraints on actually doing it:

- **A loop-mounted image file does not work.** The backing file would live in the read-only lower dir, so the loop mount would be read-only. A real partition is the only route to persistent writable
  space.
- Most fleet boxes have no spare partition (`delye-smc01`: `mmcblk0p1` 256M `/boot/firmware` + `mmcblk0p2` 57.7G `/`, root fills the disk). `roles/smc_persistent_partition` exists for exactly this —
  it shrinks root from initramfs and creates partition N+1 — but defaults to `ADDITIONAL_SIZE_GB: 2`, which would need raising, and refuses to run while overlayroot is enabled.

As of 2026-08-18 this remains **deferred, not rejected**. The interim mitigation is `roles/smc_rise_logcaps` (below).

### Bounding writes instead: `roles/smc_rise_logcaps` (added 2026-08-18)

Until volatile paths move off the overlay, the only defence is keeping files small enough that copy_up cannot exhaust the upper layer. Three pre-existing cleanup paths all miss the file class that
actually matters:

| Mechanism                                | Covers                                                                             | Blind spot              |
| ---------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------- |
| Overlay prep (`smc_rise_enable_overlay`) | journal to 100M, `*.gz` >7d, `auth.log` to 200 lines, apt cache, teleport logs >7d | active application logs |
| Watchdog `cleanup_always()`              | `/opt/rise/cache`, `/tmp`, `/var/tmp`, apt, journal                                | active application logs |
| Watchdog `cleanup_logs_gated()`          | **rotated** siblings, and only once Graylog confirms ingestion                         | anything un-rotated     |

None of them can shrink an un-rotated **active** log — which is precisely the file that fills the overlay. `smc_rise_logcaps` closes that gap by **discovery rather than enumeration**: `rise_logcap.py`
walks `/var /opt /srv /home` (`-xdev`, ~1.3 s on a Pi 4) and buckets everything over `watch_mb`:

| Bucket     | Gets a logrotate stanza? | Hard-capped? | Rationale                                                                                                                                     |
| ---------- | ------------------------ | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **managed**    | yes                      | yes          | live, log-shaped, unclaimed by any other config                                                                                               |
| **foreign**    | **no**                       | yes          | another `/etc/logrotate.d` config owns it; a duplicate entry aborts the entire daily logrotate run. Ownership is no guarantee of a *sane*       |
|            |                          |              |   policy — see the rsyslog note below                                                                                                         |
| **rotated**    | **no**                       | yes          | `.1`/`.2.gz`/`.old`/`.bak` — rotating a rotation is meaningless, but it costs the overlay the same                                            |
| **stale**      | no                       | no           | unwritten for `stale_days`; reported only, `prune_stale` defaults false because retention is an operator decision                             |
| **ineligible** | no                       | **never**        | oversized but not log-shaped, or binary (NUL byte in first 4 KB). Always reported; blocks the overlay-enable preflight                        |

The **ineligible** bucket is the design's whole point: an unknown oversized file becomes a Prometheus metric and a blocked preflight rather than a silent reboot loop. That is what makes this scale
without anyone maintaining a list of paths.

Mechanics that are easy to get wrong, all of them learned the hard way:

- **`copytruncate` is mandatory.** fluent-bit, Laravel and the RISE scripts hold their logs open. Rename-based rotation leaves them appending to the unlinked inode and the active file never shrinks.
- **`size`, never `daily`/`maxsize`.** Purely size-triggered rotation lets the hourly RISE run and the daily system run both act on the same files without double-rotating a small log.
- **rsyslog does not reopen on truncate.** It tracks its own write offset and resumes there, recreating a sparse file of the original size — the truncation frees nothing while appearing to succeed.
  Must call `/usr/lib/rsyslog/rsyslog-rotate` (the hook rsyslog's own `postrotate` uses) or `systemctl kill -s HUP rsyslog.service` afterwards.
- **Never truncate a compressed file.** Tailing a `.gz` produces a corrupt archive — worse than the oversized file. Compressed rotations are the gz-pruning path's job.
- **`su root adm`, not `su root root`.** `/var/log` is `0775 root:syslog`; `root root` trips logrotate's insecure-permissions check. `su root adm` is the platform global in `/etc/logrotate.conf`.
- Truncation keeps the **inode** (open `r+b`, write tail, `ftruncate`) so writers holding an fd keep working, and drops the partial first line a byte-offset tail always begins with — otherwise
  fluent-bit ships one malformed record.

The scan is `-xdev`, so it is forward-compatible with the structural fix: anything later moved onto its own filesystem drops out of scope automatically and correctly.

### Checking Overlayroot Status

```bash
mount | grep overlay     # confirms overlay is mounted
mount | grep root-ro     # confirm lower dir is ro vs rw
df -h                    # check tmpfs headroom
```

### Configuration

```
/etc/overlayroot.conf:
  overlayroot="tmpfs:swap=1,recurse=0"
```

### Ansible + Overlayroot

1. Ansible must remount lower dir rw before making changes that must persist
2. `smc_bases.yml` playbook handles this remount
3. If running a role directly (not via `smc_bases.yml`), verify lower dir is rw first
4. After Ansible completes, confirm change persisted: check file in `/media/root-ro/...`

### Disable Sequence (when needed)

```bash
# 1. Remount lower dir rw
mount -o remount,rw /media/root-ro

# 2. Remove overlayroot config
rm /media/root-ro/etc/overlayroot.conf

# 3. Reboot
reboot

# 4. After reboot: verify overlayroot is gone
mount | grep overlay   # should return nothing
```

**Kernel match required:** `uname -r` must match an entry in `/lib/modules/` on the lower dir. Kernel upgrades without rebooting can cause overlayroot to fail on next boot.

### Read-Only Migration Status (per flavor)

| Flavor               | Platform  | Root partition                       | Firmware/boot                | Track   | Status                      |
| -------------------- | --------- | ------------------------------------ | ---------------------------- | ------- | --------------------------- |
| rct / wh             | RPi ARM64 | **READ-ONLY** (overlayroot active)       | WRITABLE (/boot vfat)        | Track B | Root done; firmware pending |
| rcp / nbn_accelerate | x86       | **WRITABLE** (bare ext4, no overlayroot) | WRITABLE (/boot + /boot/efi) | Track A | Primary migration target    |

### `smc_disk_failover` role — EFI BootNext mechanism, not a guaranteed live-corruption failover

The role's failover mechanism sets a one-time EFI boot entry (`efibootmgr -n <id>`, "BootNext") to an alternate disk after a prolonged internet-failure count is observed — it is a **connectivity**
failover trigger, not a storage-health trigger, and it is not guaranteed to run cleanly while the active disk is under active I/O corruption (EFI tooling itself can fail with `Input/output error` in
that state — confirmed live on amata-smc01, see the storage incident in `06_failure-modes.md` "Disk Path Failure Forcing Root Read-Only"). If a disk is failing hard enough to force the root filesystem
read-only, do not assume `smc_disk_failover` will cut over automatically — verify EFI tooling is actually responsive (`efibootmgr -v`) before relying on it, and be ready to set the one-time boot entry
manually or fall back to a BIOS/UEFI console boot to the alternate disk.

### rcp Disk Write Profile (confirmed jigalong-smc01, 2026-04-20; re-confirmed 3 more nodes 2026-07-20)

**2026-07-20 re-confirmation:** live-checked `/etc/overlayroot.conf` (`overlayroot=""`), `mount | grep overlay`/`root-ro`/`root-rw` (no matches), and `findmnt -T /var/log/syslog` (resolves to the real
root device, `ext4 rw`) on tjuntjuntjara-smc01, mornington-smc01, and jigalong-smc01 — same result on all 3, no overlayroot anywhere on rcp. This re-confirmation was prompted by
`smc-file-writing-analysis/AGENTS.md`'s "Overlayroot Context" section having drifted to describe rcp as running overlayroot with a writable lower dir (implying partial RAM buffering) — that section
has now been corrected to match this file, which had the right model all along.

rcp has NO overlayroot — all writes go directly to SSD:
- journald: **3.9GB uncapped** (fix: RuntimeMaxUse=200M on real disk)
- /url_capture/: **~22MB/day** — intentional DNS pcap (dst port 53 on bridge_501)
- /var/lib/squidguard/db/: **665MB** — blocklist databases (LOCAL-KEEP)
- /var/lib/asterisk/: **344MB** — VoIP SQLite + logs
- /var/lib/dhcp/dhcpd.leases: continuous DHCP lease writes
- Prometheus WAL: 2.9MB (real disk, remote_write active)

### url_capture DNS Monitoring Service (rcp only)

> **Superseded by Python streaming service (Section 10).** v2 must be deployed per-node via Ansible. Nodes not yet migrated remain on v1 with active crons — do not assume crons are removed until
> confirmed for a specific node.

**Legacy system (active on un-migrated nodes):**
- Script: `/var/local/sslurlcapture/url_capturev1.sh`
- Midnight reset cron: `59 23 * * *` — kills screen session so next start creates new daily file
- Rsync cron: `10 0,8,16 * * *` — ships pcaps to remote (`rsync_urlcapture.sh`)
- Path: `/url_capture/YYYYMM/<hostname>-<iface>-YYYYMMDD-0000.pcap`
- Rate: ~22MB/day accumulated locally; shipped up to 8h late

**Known rsync behaviour (rsync_urlcapture.sh.j2):**
- Excludes the newest file in the sync dir — protects the active tcpdump capture from partial transfer
- This means the last file of each month is delayed by one rsync cycle after a new month starts
- Fix applied 2026-05-01: `yearmonth_today` was a literal string (missing `$()`); now fixed plus a conditional block syncs the current month dir on the 1st when today ≠ yesterday month

---

### fatrace write-rate audits: filter bug — RO/RC/RCO counted as writes (2026-07-09)

`fatrace` event codes: `R`=read, `O`=open, `C`=close, `W`=write. Only codes containing `W` (`W`, `WO`, `CW`, `CWO`, `RW`) are real writes. A filter of `grep -v ': R '` excludes only the bare `R` event
— it lets `RO`/`RC`/`RCO` (read-open/read-close/read-close-open — all still just reads, no write) through as if they were writes. Every shared-library load during process exec (`ld.so.cache`,
`libc.so.6`, `locale-archive`) fired by routine cron `sh`/`stat`/`grep`/`dash` spawns gets miscounted this way — confirmed on smc-file-writing-analysis fleet checks: on a 60s capture, one node showed
6,029 events passing the old filter but only 59 were true writes (~100x inflation). Correct filter: `grep -E ': (W|WO|CW|CWO|RW) '`.

**Fleet-wide `*/5`, `*/2`, `*/1` cron schedule (identical via Ansible) means any capture window of a few minutes will always catch a full interfacecheck/apt_info/Kohana/mqtt-client cycle** — a burst
of activity at that moment is normal steady-state, not an anomaly, and does not on its own indicate a regression.

**Phase 3 effectiveness re-confirmed with the corrected filter:** Phase 3 node (journald volatile
+ Fluent Bit pos tmpfs + sidecar redirect) showed 0 `systemd-journal` write events in a 60s true-write
capture; a non-Phase-3 node showed 32 direct writes to `/var/log/journal/.../system.journal` in the same window, and ~3.7x more total true writes overall. Full detail:
[log-audit-results.md](../../../../../../_project/project_stuff/apn/smc-file-writing-analysis/docs/log-audit-results.md) (2026-07-09 12:37 AEST entry). `scripts/wear_fatrace_remote.sh` in that project
was corrected to use the true-write filter.

---

### fatrace write counts measure syscalls, not physical disk I/O (2026-07-15)

Even with the true-write filter above, a `fatrace` event count is **not** a physical-disk-write count or an SSD-wear figure — it's a write-*syscall* count. `fatrace` logs every individual `write()`
call as its own event, and processes that stream data through in small buffered chunks (confirmed: `gpgv`, verifying apt package-list signatures) generate dozens of events for one logical operation —
one `/tmp/apt.data.*` temp file showed 29 separate `W` events plus 1 `CW` for a single download-verify pass, in just an 80-line raw sample slice.

The kernel buffers small `write()` calls in page cache and coalesces them before an actual physical flush (delayed writeback, ~30s default `dirty_expire_centisecs`). Short-lived temp files — created
and deleted within seconds, like apt's staging files — may never fully reach physical media before being overwritten or removed. So a fatrace count systematically **overstates** physical wear for
syscall-heavy buffered-write files, and is closer to accurate for writers that `fsync`/`O_DIRECT` on every write (databases, journals).

**How to apply:** treat fatrace counts as a relative/comparative signal (did this go up or down after a fix) and a lock-contention/CPU-churn proxy — never as a literal physical-write or SSD-wear
number. Comparing counts captured with different methodologies (e.g. a 60s×5-sampled full total vs a continuous-window top-N-sum) is also invalid — they're different metrics, not just different
samples of the same one. Full detail:
[smc-file-writing-analysis/.archcore/rules/RULE-011-fatrace-write-count-syscall-not-physical-io.md](../../../../../../_project/project_stuff/apn/smc-file-writing-analysis/.archcore/rules/RULE-011-fatrace-write-count-syscall-not-physical-io.md).

### fatrace excludes tmpfs entirely — every sweep in this project is real-disk-only (confirmed 2026-07-24)

`fatrace` on rcp SMC nodes **never reports writes to tmpfs-mounted paths** — `/tmp`, `/run`, `/var/lib/prometheus`, `/var/lib/fluent-bit/pos`, `/var/lib/node_exporter/textfile_collector`,
`/var/log/smc-groups` (and anything symlinked onto it, e.g. `squid`/`interfacecheck`) are all invisible to it, even though `fatrace`'s own man page/`--help` don't call this out explicitly and expose
no fstype-include/exclude flag. Confirmed live on tjuntjuntjara-smc01: a background `fatrace --timestamp --filter=W` capture caught a real-disk write to `/root/mytestfile.txt` (`CW
/root/mytestfile.txt`) but produced zero output for the identical `echo`/`echo >>` write pattern against `/tmp/mytestfile.txt` in the same window, with `findmnt` confirming the fstypes (`ext4` vs
`tmpfs`) as expected.

**How to apply:** every fatrace-derived top-writer list or `write_count` in this project — this sweep's or any historical one in `docs/fatrace-sweep-history.csv` — is a **real-disk-write list only**.
This is the correct scope for the project's read-only-migration goal (only real SSD/CFast writes matter), but it means fatrace **cannot** answer "is a tmpfs mount under write pressure" — use `du
-sh`/`df -h` on the mount, or the `node_filesystem_*` Prometheus metrics enabled fleet-wide 2026-07-23, for that question instead. Do not read a fatrace sweep's silence on
prometheus/tmp/squid/interfacecheck as those paths being idle — they aren't, fatrace simply can't see them. Full detail:
[smc-file-writing-analysis/.archcore/rules/RULE-014-fatrace-excludes-tmpfs-real-disk-only.md](../../../../../../_project/project_stuff/apn/smc-file-writing-analysis/.archcore/rules/RULE-014-fatrace-excludes-tmpfs-real-disk-only.md).

---

---

## Orphaned persistent journal after the volatile conversion (~44 GB fleet-wide, reclaimed 2026-07-28)

Once journald is `Storage=volatile` it writes to `/run/log/journal` and **never touches `/var/log/journal` again**. Any persistent journal left behind from before the conversion is therefore **inert
dead weight on the SSD/CFast that nothing will ever reclaim on its own** — it does not shrink, rotate, or get vacuumed.

Found across the rcp fleet 2026-07-28: **~43,952 MB total.** ~4.1–4.3 GB each on kalumburu, mowanjum, guda-guda, jigalong, umoona, horn-island, bidyadanga, warburton, beagle-bay and pandanus-park; 1.9
GB on old-looma; 153 MB on new-looma. On a 64 GB BOXER-6404 CFast that is ~6.6% of the device, permanently consumed.

**Where the gap came from.** Only four nodes were clean (1 MB) — tjuntjuntjara, burringurrah, wujal-wujal, mornington — which are **exactly the 2026-06-30 first Phase 3 cohort**. That deploy reclaimed
the pre-existing journal; every later Phase 3 rollout (07-10, 07-14, 07-21, 07-23) did not. The gap would have recurred on every future onboarding, so the cleanup is now a task in `smc_system` rather
than a manual step.

### `journalctl --vacuum-*` cannot do this job

This is the trap. journald does not manage `/var/log/journal` once volatile, so vacuum reports **`freed 0B` for that path while happily vacuuming the RAM journal instead**. Verified live on new-looma
2026-07-28: `journalctl --vacuum-time=1s` freed 192 MB from `/run/log/journal` and 0 B from the actual target — i.e. it destroyed recent journal history in RAM and achieved nothing against the disk
residue. Removing the directory is the only thing that works.

### Safe reclaim procedure

1. Confirm journald is *genuinely* volatile at runtime — `/run/log/journal` must exist. Do **not** rely on the config file saying `Storage=volatile`; a node that has not restarted journald yet is
   still writing persistently, and deleting its journal would destroy live logs.
2. Confirm no open handles: `lsof +D /var/log/journal` should be 0.
3. Remove the directory. Removing it (rather than emptying it) also hardens against a future `Storage=auto`, which only uses persistent storage if `/var/log/journal` exists.
4. Verify after: directory absent, `systemd-journald` active, `/run/log/journal` present and capped, and a `logger` round-trip visible in `journalctl` — proving logging still works end to end.

Canary result (kalumburu, 4.1 GB): 37 G → 41 G free, 32% → 24% used, all checks green. Fleet result: all 16 nodes clean, journald active, runtime journal at its 200 M cap, disk used 12–25%.

## Fleet status-probe gotchas — three checks that read as fleet-wide failures but are wrong paths (verified 2026-08-25)

A uniform status probe pushed over `tsh ssh` to every rcp node returned negative on three keys for **all 17 nodes**, including 15 verified working four weeks earlier. Unanimous failure across
known-good nodes is a probe bug, not a fleet event. All three were wrong-path assumptions:

| Wrong check                                | Correct check                         | Why                                                                                                             |
| ------------------------------------------ | ------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `test -L /var/log/interfacecheck`          | `test -L /var/log/interfacecheck.log` | `smc_rsyslog` symlinks the **log file**, not a directory:                                                           |
|                                            |                                       |   `/var/log/interfacecheck.log -> /var/log/smc-groups/interfacecheck.log`. squid and mosquitto *are* directory    |
|                                            |                                       |   symlinks, so the three are not symmetrical.                                                                   |
| `test -L /opt/apn-mqtt-client/status.json` | `find / -maxdepth 5 -name status.\`   | The app lives at `/run/apn-mqtt-client/` (a real file, already on tmpfs since `/run` is tmpfs) on most nodes,   |
|                                            |   `json -path '*mqtt*'`               |   or `/var/www/apn-mqtt-client/` (a symlink into `/run`) on others. Never `/opt/`. Both forms are the *fixed*     |
|                                            |                                       |   state — a real file under `/run` is not a gap.                                                                |
| `systemctl is-active fluent-bit`           | `pgrep -c fluent-bit`                 | fluent-bit has **no systemd unit**. `graylog-sidecar` spawns it directly as a child:                                |
|                                            |                                       |   `/opt/fluent-bit/bin/fluent-bit -c /var/lib/graylog-sidecar/generated/<id>/apn-gelf-http.conf`. `is-active`   |
|                                            |                                       |   returns `inactive` on a perfectly healthy node.                                                               |

**Rule:** before recording a negative status finding, check whether the *known-good* nodes also fail it. If they do, fix the probe, not the fleet. Recording these three unverified would have produced
three false fleet-wide regressions in the canonical tracker.

Two more probe notes from the same sweep: macOS has no `timeout(1)`, so a `timeout 90 tsh ssh …` wrapper fails with rc=127 on every host and looks like a Teleport auth problem; and `xargs -P`
interleaves worker stdout line-by-line, so per-node output must be redirected to its own file or attribution is lost.

### Teleport node name can differ from hostname and inventory name

`family-pending-smc01` is the Teleport node name for a box whose hostname and `inventories/rcp/prod` name are both `family-friendly-smc01`. Target it by the **inventory** name for Ansible and the
**Teleport** name for `tsh ssh`. `tsh ls` shows the Teleport name in the node column and the real hostname in the `hostname` cmd_label — compare both when reconciling a fleet list against inventory.

### Inventory group membership proves eligibility, not application

`smc_bases.yml`, `smc_graylog.yml` and `smc_prometheus.yml` all target `hosts: smc_bases`, so any node in that group is *eligible* for every fleet pass. It does not follow that the passes reached it —
Ansible skips UNREACHABLE hosts and the play still reports success for everyone else. Two nodes have now been found in the right group and fully unremediated: new-looma (down during the 2026-07-23
log-consolidation rollout) and family-friendly (never run against, 4w5d uptime). Verify on-box, never from group membership.

**Scope note:** `family-friendly-smc01` / Teleport `family-pending-smc01` is used above purely as an example of these two mechanisms. It is **excluded from the `smc-file-writing-analysis` project by
operator decision (2026-08-25)** and must not be added to that project's `docs/fleet-status.md` matrix or node count. The mechanisms themselves are fleet-wide SMC facts and stay in scope here.

---

## Write-rate sweeps are blind to burst writers (2026-08-26)

**Every write-rate measurement method this project has used before 2026-08-26 counts write EVENTS over a sampling window. Both properties are limitations, and the second one is severe.**

### Events are not bytes

`fatrace` emits one line per write syscall. A 4-byte write and a 4 MB write are indistinguishable in it. Grafana's daily-write panel measures **bytes**. The two rankings genuinely disagree: on
2026-07-28 umoona-smc01 logged the **lowest** event count of all 16 nodes (149 events/5 min) while sitting at 1.95 GB/day — fourth-highest on the byte chart. old-looma was the same shape (178 events,
2.03 GB/day).

For byte attribution use `/proc/<pid>/io`: `write_bytes` minus `cancelled_write_bytes` is the count of bytes the kernel charged that process to the block layer. Complement it with `/proc/diskstats`
field 10 (sectors written × 512) as whole-device ground truth. tmpfs stays excluded on all axes — tmpfs writes never reach the block layer, so `write_bytes` never counts them, consistent with RULE-014
for `fatrace`.

### Windows miss burst writers entirely — this is the bigger problem

Some of the largest writers on an SMC fire **once or twice a day for a few seconds** and move hundreds of MB. No sampling window of practical length catches them. Two independent windows (300 s and
600 s) run on 2026-08-26 agreed closely on continuous writers and **missed every one of the following**:

| Writer                         | Volume per event                                                        | Notes                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `snapd` snap refresh           | **image written twice** — `/var/lib/snapd/cache/` then                      | Refresh times scatter across the clock (observed 02:25/10:00/14:23/17:20/19:55) — snapd's |
|                                |   `/var/lib/snapd/snaps/`. `lxd_40575.snap` = 115.3 MB × 2 = **230.6 MB**   |   own randomised timer. Same node looks clean one day, heavy the next.                    |
| `squidguard` blacklist refresh | 24.3 MB `.tar.gz` + 24.3 MB `.bak`, then extraction into a 624–657 MB   | Observed at **15:29 on 7 of 9 nodes simultaneously** — one fleet-wide cron                    |
|                                |   tree                                                                  |                                                                                           |
| `apt` metadata churn           | `pkgcache.bin` ~67 MB + `srcpkgcache.bin` ~67 MB + ~117 MB lists ≈ 250  | Only on nodes where apt timers are unmasked                                               |
|                                |   MB/day                                                                |                                                                                           |
| `dhcpd` lease-DB rewrite       | full-file rewrite, up to 294 MB                                         | Episodic. `dhcpd` measured 1.30 MB in one 5-min window and 0.02 MB in the next 10-min     |
|                                |                                                                         |   window on the same node.                                                                |

**Method rule going forward: pair every sampling window with a 24 h large-file scan.** Neither alone is sufficient.

```bash
find / -xdev -type f -mmin -1440 -size +4M -printf '%s %TH:%TM %p\n' 2>/dev/null | sort -rn | head
```

`-xdev` keeps the scan on the real root filesystem, so it never crosses into a tmpfs mount.

### snapd is a read-only-root blocker, not just a wear problem

All 9 rcp nodes audited 2026-08-26 run `snapd` **active** with **8 seeded snaps** and **773–952 MB** in `/var/lib/snapd`, including `lxd` — which nothing in the SMC service inventory uses. Beyond the
230 MB-per-refresh write cost, **snapd cannot operate on a read-only root**, so it must be resolved before the rcp migration regardless of the wear argument.

### Lifetime counters are contaminated by pre-remediation history — do not use them

`write_bytes ÷ process age` looks like an attractive way to dodge the sampling problem. It is not usable here. On mornington-smc01 it ranks `systemd` at 8,374 MB/day — **higher than the node's entire
device throughput of 2.87 GB/day**, which is impossible for a current rate. `write_bytes` is cumulative since process start, and that PID 1 had been up 310 days, so the counter spans the era before
journald-volatile and the tmpfs stack landed. In live deltas the same `init` and `cron` processes wrote 0.01–0.02 MB. They are not current writers.

Read those figures as evidence the write-reduction program worked, never as a current-rate finding.

### What the continuous writers actually are (2026-08-26, 9 nodes)

- **`jbd2/<dev>`** — top byte writer on 6 of 9. Not a service and cannot be stopped: it is ext4 committing metadata on behalf of everyone else's small fsyncs, so it falls only when what feeds it
  falls. **No rcp node uses `noatime`** — all mount `/` with `relatime` and default `commit=5`; neither lever is in use.
- **`asterisk`** — largest continuous *service* writer, top-2 on six nodes. Target is `/var/lib/asterisk/astdb.sqlite3` **plus its `-journal` rollback file**. The DB is only 12–250 KB; the cost is
  transaction overhead, since SQLite's default rollback-journal mode does create-journal → write → fsync → write-page → fsync → delete-journal → fsync-dir for *every* transaction. Files never grow;
  the disk still pays. Separately `/var/log/asterisk/cdr-csv/Master.csv` grows unrotated (43.3 MB observed).
- **Roughly half of device bytes are unattributable** to any live process (45–62% attribution). The remainder is writeback charged to processes that exited mid-window plus kernel flushing — a known
  limit, not a data gap.
- **`teleport` appears as a writer in any Teleport-collected audit** at ~0.12–0.31 MB/window, largely the audit's own SSH session recording streaming to `/var/lib/teleport/log/upload/streaming/`.
  Discount it unless measuring from an unattended session.

### Tooling

`scripts/wear_deep_write_remote.sh` (byte + event + file-growth + device ground truth in one window) and `scripts/deep_write_sweep.sh` (batched driver) in `smc-file-writing-analysis`. The driver
writes into a per-run `RUN_TAG` subdirectory — added after a repeat sweep truncated an earlier run's captures by reusing the same output directory. Related: editing a bash script while it is executing
corrupts the running interpreter's byte offsets and throws a syntax error mid-run; patch after the run completes.

Full analysis: `smc-file-writing-analysis/docs/audits/deep-write-attribution-20260826_1600.md`.

---

## The 24 h write baseline, and what two attribution passes buy you (2026-08-27/28 capture)

A 24 h `write_collect_24h.py` capture across 8 rcp nodes, window 2026-08-27 00:29 UTC → 2026-08-28 00:33 UTC. Analysed twice: file-level in
`smc-file-writing-analysis/docs/audits/write24-baseline-analysis-20260831_1400.md`, then process-level and reconciliation in `write24-baseline-analysis-20260901_1400.md` (re-runnable via
`scripts/analyze_write24.py`).

### The collector runs two passes that share no mechanism — compare them per node

File size-deltas and `/proc/<pid>/io`. The first analysis used the file pass and quoted the process pass only fleet-summed; comparing them **per node** is what turns an indicative number into a
corroborated one. On squidguard they agree within 6% on every node where it ran, which is what promotes cron's bytes from "driver process, attribute downstream" to a node-by-node attribution.

### Rewrite-in-place bytes are an UPPER bound — the direction matters and has been got wrong

`write_collect_24h.py:12`: *"mtime moved, size not grown -> rewrite-in-place (UPPER BOUND: counts size)"*. The collector charges the **full file size** once per interval in which the file changed, so
a SQLite page-level rewrite of a 250 KB database is charged 250 KB — an **over**count. The 2026-08-31 analysis stated the opposite ("undercounted … at least what is shown"), contradicting both its own
"upper bound" phrasing and the source; corrected 2026-09-01.

Consequence when quoting astdb: its byte figures are a **ceiling**, not a floor. The rewrite *counts* (1082–1434/day, ~1/min, on 7 of 8 nodes) are exact and carry the WAL argument on their own. The
one leak in the other direction is a file rewritten more than once inside a single 60 s interval.

### Process-sum figures are a floor, not a total — 30–42% of device bytes are unattributed

Consistent across all 8 nodes, which is what identifies it as a property of the instrument rather than a hidden writer: `/proc/<pid>/io` is sampled every 60 s, so a process that starts and exits
between two samples contributes exactly nothing — the profile of short-lived cron children, logrotate and package tooling. **Never state "X is N% of this node's writes" against the process sum**; it
inflates by 1.4–1.7×. Use the device total. `jbd2` sits at 180–286 MB/day on every node regardless of workload — ext4 journal amplification, no application fix touches it.

### squidguard is the largest single writer at ~440 MB/node/day

Confirmed on 6 of 8 nodes by both passes. One refresh: 249.1 MB `newdb/univ-tlse1/adult/domains` extract, 50.8 MB download, **50.8 MB `.tar.gz.bak` copy**, ~45 MB db rebuild, ~44 MB other extracts.
Cron is `minute: "29"`, `hour: "3,15"` — twice daily, verified in `roles/smc_squid/tasks/main.yml:187-190`, not inferred, and confirmed by arithmetic: the observed 249.1 MB `adult/domains` is exactly
2× its 124.5 MB upstream size, so **both slots do a complete refresh**.

**For the mechanism, the rsync transport upstream offers, and the traps in changing any of it, see `08_ansible-authoring.md` → "`smc_squid`'s blocklist refresh".** Short version: nothing in the
pipeline is incremental, upstream publishes an rsync endpoint that reduces the same work to kilobytes/day *if* `--inplace` is used, and outbound rsync from an SMC is untested. The `.bak` is a `cp`
that should be an `mv`/`ln`: 50.8 MB/day/node of duplicated bytes with no freshness trade-off attached, and unlike the cron-frequency question it needs no operator decision.

### A single window never gives an event-driven writer's daily rate — snapd is the worked example

Two non-overlapping windows: **5 of 9 nodes refreshed** on 2026-08-25/26 (230.6 MB each), **0 of 8** on 2026-08-27/28. Roughly 0.3 refreshes/node/day ≈ 60–70 MB/node/day averaged — an estimate from
two windows, not a measured rate. The shape is what is established: lumpy and episodic, a node can sit at zero for a full day.

The fleet-wide removal (14/17 nodes, 2026-09-01) stands on grounds this does not touch — snapd cannot operate on a read-only root at all, plus 773–952 MB resident per node and no lxd use anywhere.
Only the wear estimate moves, from 230 toward ~65 MB/node/day.

Also worth carrying forward: the 08-31 analysis **declined to derive snapd from this capture**, reasoning the size-delta method could not see it. That was wrong — a snap refresh *downloads a new
file*, and the collector's accounting classifies a new path as **exact** (`write_collect_24h.py:9`). The rewrite-in-place blindness applies to constant-size files, not to newly-arriving images. Check
which accounting class a writer falls into before declaring the instrument blind to it.

### squidguard is silently dead on mornington and bidyadanga

Both report zero squidguard bytes on both passes while `.univ-tlse1.lockfile` **is** touched twice daily — the job fires and does nothing, which makes "the cron didn't fire" the less likely
explanation. bidyadanga's 25-day-stale blacklist corroborates. This is **content-filtering correctness**, and it points the opposite way from every other finding here: those nodes need writes
restored, not suppressed. Textbook RULE-008 — low write volume as the visible symptom of a silently-failing chain.

### rsyslogd spread is 6.7× and unexplained

mornington 672.8 MB/day against umoona's 100.9 — the largest single line item in the dataset, 2.1× the fleet median, not explained by site size. mornington also carries the known 64 MB `auth.log` and
the unremediated auth-filter.
