# SMC Failure Modes

## Contents

- [6. Failure Mode Reference](#6-failure-mode-reference)

---

## 6. Failure Mode Reference

### Key Prometheus Alerts

| Alert                                  | Trigger                                                                                                    | First check                                    |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `HostOutOfDiskSpace`                   | < 10% free                                                                                                 | `/var/log`, overlayroot upper dir              |
|                                        |                                                                                                            |   fills (tmpfs)                                |
| `HostOutOfInodes`                      | < 10% inodes                                                                                               | Small file accumulation in `/tmp`, logs        |
| `HostDiskWillFillIn24Hours`            | `predict_linear` > 24h                                                                                     | Find write rate source                         |
| `HostSystemdServiceCrashed`            | unit state = failed                                                                                        | `journalctl -u <unit>`                         |
| `HostClockSkew`                        | offset > ±0.05s                                                                                            | `chronyc tracking`                             |
| `HostClockNotSynchronising`            | stratum = 0                                                                                                | `chronyc sources -v`; upstream NTP reachable?  |
| `HostConntrackLimit`                   | > 80% conntrack                                                                                            | `ss -s`; check for connection leak; see Tier 6 |
| `NodeNetworkDefaultRouteInstability`   | 4+ route changes / 60min                                                                                   | VRRP flap, overlay issue, uplink unstable      |
| `NodeStarlinkInterfacecheckPacketLoss` | 100% loss / 60min                                                                                          | Starlink interface down (specific flavor)      |
| `sbdm_device_health_status == 0`       | RPi Swissbit microSD card degraded (RPi/rct/wh/nbn_wh only — corrected 2026-07-13, was mislabeled "Samsung | microSD card replacement needed                |
|                                        |   SSD"; `sbdm-cli` only detects genuine Swissbit hardware, never fires on x86 SSD/CFast)                   |                                                |
| `smartmon_device_smart_healthy == 0`   | SMART failure — x86 rcp/nbn_accelerate only (Innodisk CFast or Transcend SSD; `smartctl` finds no          | Drive health critical                          |
|                                        |   ATA-SMART device on RPi microSD, this alert never fires there)                                           |                                                |

### Overlayroot Upper Dir Full

```
Symptom: HostOutOfDiskSpace fires on a box with 60GB storage
Cause: /dev/overlay (tmpfs at /media/root-rw) fills RAM-backed space
Check: df -h | grep overlay
       # "size=40%" → mount actually lands at 50% of RAM = ~3.9GB on an 8GB RPi 4B
Fix:   Identify what is filling /media/root-rw/overlay
       find /media/root-rw/overlay -type f -size +10M 2>/dev/null
```

### Root Filesystem Unexpectedly Read-Only (x86 `rcp` / `nbn_accelerate`)

| Field               | Value                                                                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Error text          | Write failures (`Read-only file system`) on `/`; package/install tasks and file edits fail                                                                                     |
| Typical context     | `rcp` or `nbn_accelerate` where overlayroot is not expected                                                                                                                    |
| Cause class         | Kernel protective remount after ext4 journal/storage I/O errors (not overlayroot behavior)                                                                                     |
| Immediate checks    | `findmnt -no SOURCE,OPTIONS /`;                                                                                                                                                |
|                     |   `mount \| egrep ' on / \|overlay\|root-ro'`; `dmesg -T \| egrep -i 'EXT4-fs error\|I/O error\|Remounting filesystem read-only\|nvme\|sda' \| tail -n 120`                    |
| Source-of-truth     | `/etc/fstab`; `inventories/nbn_accelerate/group_vars/smc_bases.yml`; `references/07_hardware-overlay.md` migration table                                                       |
|   files             |                                                                                                                                                                                |
| Fix pattern         | 1) `mount -o remount,rw /` 2) reboot once 3) if RO returns, run offline `fsck.ext4 -f -y <root-device>` from rescue/initramfs 4) run SMART check and replace disk if media     |
|                     |   errors persist                                                                                                                                                               |
| Validation commands | `findmnt -no OPTIONS /` shows `rw`; `touch /root/.rw_test && rm /root/.rw_test`; `journalctl -k -b \| egrep -i 'EXT4-fs error\|I/O error\|read-only'` shows no new             |
|                     |   remount errors                                                                                                                                                               |

### Domain-Specific Host DNS Resolution Delay (non-`smc_ltp` hosts)

| Field                     | Value                                                                                                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Error text                | `ping <fqdn>` / `getaddrinfo(AF_UNSPEC)` from the SMC itself stalls ~15s before resolving; direct IP and single-record `dig` are fast; delay is domain-specific          |
|                           |   (reproduces on domains with an A record + AAAA NODATA, not on domains with no AAAA-eligible answer path)                                                               |
| Typical context           | Any non-`smc_ltp` host performing a combined A+AAAA lookup (`getaddrinfo(AF_UNSPEC)`) — this is glibc's default behavior for most name resolution, not something the     |
|                           |   caller opts into                                                                                                                                                       |
| Cause class               | Architecture exposure, not a code bug: `DNSStubListener=no` (unconditional, `roles/smc_network/templates/resolved.conf.j2`) means host glibc talks directly to           |
|                           |   `external_dns_servers` over raw UDP — bypassing systemd-resolved's stub *and* unbound/stubby entirely (see `02_service-map.md`). On some WAN paths, one leg (typically |
|                           |   AAAA) of the near-simultaneous A/AAAA query pair fails to return; isolated queries and TCP both succeed, ruling out general DNS reachability                           |
| First confirmed on        | garimba-smc01 (rct), 2026-07-03; not reproduced on yuelamu-10mile-smc01 (same fleet, different WAN path)                                                                 |
| Immediate checks          | `time ping <fqdn>` from the box; compare `dig +tcp` (expected to succeed) against default `getaddrinfo` (may stall); packet capture on the WAN interface during the      |
|                           |   stall to see which query type's response is missing                                                                                                                    |
| Mitigation (not           | Point host resolution at systemd-resolved's stub (`127.0.0.53`) instead of the raw uplink file — this changes resolver *implementation* and appears to route around the  |
|   yet fleet-validated)    |   WAN-path condition, but does **not** prove the underlying condition is fixed. Do not roll out fleet-wide without live validation — see `13_known-issues.md`            |
| Source-of-truth files     | `roles/smc_network/templates/resolved.conf.j2`, `roles/smc_network/tasks/ubuntu.yml:196-214`,                                                                            |
|                           |   `roles/smc_dns/templates/unbound.conf.j2`, `roles/smc_dns/files/stubby.yml`                                                                                            |
| Full RCA                  | `local-knowledge-ansible/ansible-wifi/issues/garimba-smc01/garimba-smc01-dns-resolution-rca-20260703_1158.md` (revision 3, with two rounds of validation-prompt          |
|                           |   corrections) + companion docs under `issues/garimba-smc01/docs/reports/`                                                                                               |

### Captive Portal Dead at Bootstrap — `Directory APPPATH/cache must be writable`

| Field              | Value                                                                                                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Error text         | Response body is exactly `Directory APPPATH/cache must be writable` (40 bytes), served with **HTTP 200**, and `/var/log/apache2/error.log` stays **empty** — Kohana catches and prints |
|                    |   the exception rather than raising it                                                                                                                                          |
| Typical context    | Any Ubuntu SMC after `application/cache` or `application/logs` ends up `0755 root:root`. Apache runs mod_php as `www-data` (see `10_captive-portal.md` §11.1), so the dirs are  |
|                    |   unwritable and `Kohana::init()` throws before routing                                                                                                                         |
| Cause class        | Ansible tag gap, not drift: a `--tags wifi_dev_repo` run wipes and re-clones `/var/www/html/wifi` (git recreates both dirs at umask 022) while the untagged block that chmods   |
|                    |   them 0777 is skipped. A full untagged run is correct, which masks the defect                                                                                                  |
| Source-of-truth    | `/var/www/kohana-base/system/classes/kohana/core.php:281` (cache check), `.../kohana/log/file.php:31` (logs check — **fix both dirs or the failure just moves one step**        |
|   files            |   **later**), `roles/smc_application/tasks/main.yml`                                                                                                                            |
| First confirmed on | 10 of 16 in-scope `rcp` sites, 2026-07-21 → 2026-07-28 (7-day outage). `rct` and `wh` swept and unaffected                                                                      |
| Immediate checks   | `stat -c '%a %U:%G' /var/www/html/wifi/application/{cache,logs}` (expect `777 root:root`); then curl the **real ServerName**, never `localhost` with a `Host:` header — localhost |
|                    |   is served by `000-default` and returns a healthy-looking 10671-byte `index.html` on a completely dead portal                                                                  |
| Resolution         | `ansible ... -m file -a "path=/var/www/html/wifi/application/cache state=directory recurse=yes owner=root group=root mode=0777"`, repeated for `logs`. Permanent fix: the perms |
|                    |   block **and** the `stat` task registering `wifi_stat` must both carry `tags: wifi_dev_repo`                                                                                   |
| Detection gap      | No alert can fire on this today. The Kohana usage/status crons run as **root**, for whom a 0755 root-owned dir is writable, so they keep succeeding and Eclipse keeps receiving |
|                    |   data. A status-code-only HTTP probe would also miss it — the failure returns 200                                                                                              |
| Full RCA           | `local-knowledge-ansible/ansible-wifi/issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md`                                                                  |

### Disk Path Failure Forcing Root Read-Only (x86 `nbn_accelerate`, active disk path)

| Field                               | Value                                                                                                                                                          |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Error text                          | `/dev/sdb2 on / type ext4 (ro,relatime)`; `mount -o remount,rw /` fails with `cannot remount /dev/sdb2 read-write, is write-protected` (rc=32); most binaries  |
|                                     |   (`efibootmgr`, `lsblk`, `blkid`, `findmnt`, `dmesg`) fail with `Input/output error`, not a PATH issue                                                        |
| Typical context                     | amata-smc01 (nbn_accelerate, x86, BOXER-6641 class)                                                                                                            |
| Cause class                         | Physical storage-path failure on the active root disk (`sdb`) — SSD fault and/or SATA link/cable/backplane/power instability. **Not** overlayroot behavior, not a |
|                                     |   PATH issue, not an Ansible playbook logic error                                                                                                              |
| Error signature (from device log,   | `ata4.00: failed command: WRITE FPDMA QUEUED`, repeated `COMRESET failed`, `ata4.00: disabled`, `blk_update_request: I/O error, dev sdb`,                      |
|   ~2026-04-25 10:37:08)             |   `EXT4-fs ... I/O error while writing superblock`, `EXT4-fs (sdb2): Remounting filesystem read-only`, `hostbyte=DID_BAD_TARGET`                               |
| What was evaluated                  | `smc_disk_failover` role: uses `efibootmgr -n` (BootNext, one-time) after a prolonged internet-failure count — **not a guaranteed safe immediate failover under** |
|                                     |   **active I/O corruption**, and EFI tooling itself was unreliable on this host because of the ongoing I/O errors                                              |
| Operational decision guidance       | 1) Reboot is a reasonable first attempt, outage risk acknowledged. 2) If a short RW window appears post-reboot: `efibootmgr -v` → set one-time boot to the     |
|                                     |   alternate Ubuntu entry (`efibootmgr -n <id>`) → reboot quickly. 3) If tooling fails or host stays RO: BIOS/UEFI console boot to the alternate SSD manually.  |
|                                     |   4) After a successful alternate boot: set permanent `BootOrder` with the alternate first (`efibootmgr -o ...`), verify Teleport/autossh, then replace/repair |
|                                     |   the failed disk path before reintroducing it to the boot order                                                                                               |
| Status                              | **Open as of 2026-04-30 — not yet recovered.** ROADMAP backlog for this host still lists: recover via reboot/failover, re-establish the PIN/session enforcement |
|                                     |   chain (`ECLIPSE_*` mark population + `netfilter-persistent`) once writable, validate month-rollover PIN behavior post-recovery, and capture final incident   |
|                                     |   closeout. Baseline content filtering was confirmed still active during the degradation window — do not assume a fully down box means filtering is also down  |
| Full incident capture               | `local-knowledge-ansible/ansible-wifi/issues/amata-smc01/2026-04-30-amata-smc01-storage-incident.md` + `amata-error.log`                                       |

### Ansible Failure: `iptables-restore` references missing `restricted` set

| Field           | Value                                                                   |
| --------------- | ----------------------------------------------------------------------- |
| Error text      | `iptables-restore ... Set restricted doesn't exist`                     |
| Typical task    | `smc_iptables : Generate and copy iptables configuration for smp`       |
| Cause class     | Template/runtime drift after fqdn2ip/ipset decommissioning              |
| Immediate check | `rg -n "match-set | restricted | ipset" roles/smc_iptables roles/smc_fqdn2ip` |
| Resolution      | Remove active ipset dependency from SMP template and stale toggle logic |

### Ansible Failure: loop receives scalar package name

| Field         | Value                                                                                                                                                                                |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Error text    | `Invalid data passed to 'loop' ... got this instead: php8.1-cli`                                                                                                                     |
| Typical task  | `smc_application : Collect archive size for each pkg (bytes)`                                                                                                                        |
| Cause class   | Jinja type-check bug in helper normalization                                                                                                                                         |
| Immediate     | `roles/_helpers/custom_apt_install.yml` package normalization logic                                                                                                                  |
|   check       |                                                                                                                                                                                      |
| Resolution    | First-attempt fix (`is sequence` normalization, see `05_troubleshooting.md` Tier 10) hit a second incompatibility under `--check` mode (`Package unavailable`). **Actual applied fix** |
|               |   **(old-looma/umoona, 2026-07-29): wholesale-replaced** `roles/_helpers/custom_apt_install.yml` and `custom_apt_update_cache.yml` with their `rise-multi` versions (simpler         |
|               |   `apt-cache policy` check, no size-collection step) rather than patching in place                                                                                                   |

---

### Silent Total Hang — healthy box vanishes mid-scrape, needs physical power cycle (windjana-gorge + kupungarri on `wh`; pandanus-park on `rcp`)

The most damaging failure mode found to date, and the one most likely to be misdiagnosed as SD-card corruption. Sites go completely unreachable — no `tsh`, no reverse tunnel — and are restored by an
on-site **reboot alone**. No card/disk replacement required. Earlier `wh` sites with the same symptom had cards swapped, which is what created the false "corrupt card" narrative. First identified on
`wh` (RPi, investigated 2026-08-28); confirmed on `rcp` (x86) at pandanus-park-smc01, 2026-09-07 — see the dedicated subsection below. Treat this as a cross-flavor signature, not a RPi-specific one.

| Field             | Value                                                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Symptom           | Box unreachable via Teleport and via the autossh reverse tunnel; recovered only by physical power cycle                                |
| Flavors affected  | `wh` (and by construction `nbn_wh`) — RPi flavors with **no** tstik board; also confirmed on `rcp` (x86, no tstik, no RISE at all)     |
| Cause class       | Abrupt kernel/SoC-level lockup. **Not** resource exhaustion — see the ruled-out table below                                            |
| Detection latency | ~6 months per incident on `wh`; ~2 days on `rcp` (pandanus-park caught same-week via Prometheus + Graylog cross-check)                 |
| Immediate check   | `up{instance=~"<site>.*"}` on `apn-prometheus01` (3-year retention) — find the last sample, then read memory/disk/load at that instant |
| Resolution        | Physical power cycle restores the box. No card/disk replacement required                                                               |

#### Evidence (both sites)

|                          | kupungarri-smc01                                            | windjana-gorge-smc01  |
| ------------------------ | ----------------------------------------------------------- | --------------------- |
| Last metric sample       | 2026-02-17 14:20 AEST                                       | 2026-02-20 14:50 AEST |
| Rebooted on site         | 2026-08-24 ~08:35 AEST                                      | 2026-08-24 20:31 AEST |
| Dark for                 | ~6 months                                                   | ~6 months             |
| Root free at death       | 1.5 GB                                                      | 2.4 GB                |
| `MemAvailable` at death  | 2,962 MB of 7,807                                           | 4,669 MB of 7,807     |
| `node_load1` at death    | 0.26                                                        | 0.47                  |
| SD health after recovery | `sbdm_device_health_status 1`, `remaining_spare_blocks 100` | identical             |

`node_exporter` (:9100), the box's own Prometheus (:9090) and `speedtest_exporter` (:9798) all stopped in the **same scrape**. No degradation, no trend, no partial failure — the whole box vanished at
once.

#### What this rules out — check these off before reaching for the card

| Hypothesis                     | Ruled out by                                                                                                                                                        |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SD-card corruption / wear      | SBDM health 1 and 100% spare blocks on both cards post-recovery; zero `EXT4-fs error` / `I/O error` in dmesg                                                        |
| Overlay tmpfs (RAM) exhaustion | Root free space **sawtoothed** between 1.3–2.5 GB for months — logrotate reclaims on cycle. Nothing was filling. This was the initial hypothesis and the data       |
|                                |   refutes it                                                                                                                                                        |
| Memory leak / OOM              | 3.0–4.7 GB `MemAvailable` at the instant of death; zero OOM-killer entries                                                                                          |
| Load or thermal runaway        | `load1` under 0.5 on a 4-core box                                                                                                                                   |
| Shared upstream/WAN event      | The `wh` fleet dropped 22 → 21 → 20 → 19 one host at a time over five days, not together                                                                            |

#### Why `wh` and not `rct`

`rct` carries the external **tstik** board, which hard-power-cycles the appliance when internet connectivity is lost. It masks this failure mode entirely — an `rct` box in the same state self-recovers
within minutes and nobody opens a ticket. `wh` has no equivalent, and nothing in software substitutes for it:

- `watchdog.auto_reboot: 0` in `inventories/{wh,nbn_wh,rct}/group_vars/smc_bases.yml` — the RISE watchdog never reboots.
- The RISE watchdog is a userspace `systemd` timer. A kernel-level lockup stops it dead along with everything else.
- Its only reboot trigger is disk pressure, and its log cleanup is **gated on Graylog reachability** — so it disables itself precisely when the site is offline.
- **The repo contains no hardware-watchdog configuration at all** — no `/dev/watchdog`, no `RuntimeWatchdogSec`, no `bcm2835_wdt`. Verified by `rg` across the whole tree, 2026-08-28.

#### Why `rcp` is exposed too — for a simpler reason than `wh`

`rcp` has no tstik (x86, not `rct`) and, per `inventories/rcp/group_vars/smc_bases.yml`, does **not run RISE at all** — the comment there is explicit: "rcp nodes do not run RISE". So `rcp` isn't
missing a working recovery layer the way `wh` is (inert `watchdog.auto_reboot: 0`, wedged `rise-healthcheck.service`); it never had one to begin with. No watchdog config of any kind exists for this
flavor either. Same blast radius as `wh` (silent hang, no self-recovery), simpler root cause (nothing was ever built to catch it).

#### Why nothing alerted

Alert rules do exist — `/etc/prometheus/rules.d/{windjana-gorge,kupungarri}-smc01.yml` carry `absent_over_time(up{...}[60m])`. They were true for six months. **Verify where those alerts route before
assuming this is now covered.**

#### Forensic reality: the evidence destroys itself

On an overlayroot box, journald and `/var/log` live on the tmpfs upper dir. The reboot that fixes the box erases every local trace of why it hung. `/media/root-ro` is frozen at the date overlayroot
was sealed — windjana 2025-09-23, kupungarri 2025-12-08 — so **the SD card has recorded nothing since**. This is why swapping the card neither proves nor disproves corruption.

Off-box telemetry is therefore the only usable evidence, and on these two it was largely absent:

- windjana has **never** shipped a log line. `Failed to start Graylog Sidecar` appears in its own September 2025 syslog; the unit is still `failed`.
- kupungarri shipped to Graylog only on 2025-12-08, then nothing until the 2026-08-24 reboot. **Graylog silence is not evidence the box was down** — Prometheus proves it ran healthily until
  2026-02-17.
- `apn-prometheus01` keeps **3 years**. It is the authoritative source for "when did this site actually die". Do not conclude a host was never monitored from a query window that starts after it died.

Incidental finding: kupungarri-smc01 is not the original unit. Its `syslog.2.gz` in `/media/root-ro` runs under hostname `generic-wh01` → `generic-wh01-20240408`, renamed 2025-12-06. The December 2025
"card replacement" at that site was a **whole-appliance swap**.

**`rcp` should NOT destroy evidence the same way.** `rcp` (x86) is not overlayroot — see "Root Filesystem Unexpectedly Read-Only (x86 `rcp` / `nbn_accelerate`)" above, which treats overlayroot as
explicitly *not* the `rcp` model. `/var/log` there is on real, persistent disk. This means a `rcp` instance of this failure mode (pandanus-park, below) is the first real chance to get on-disk
`dmesg`/kernel evidence of the hang itself after the next recovery reboot — check `journalctl -k -b -1` (previous boot) before assuming nothing survived.

#### `rcp`/x86 instance — pandanus-park-smc01 (found 2026-09-07, still dark at time of writing)

First confirmed instance of this signature outside `wh`/RPi. Investigated starting from an operator report ("pandanus park is offline") rather than a fleet sweep.

| Field                         | Value                                                                                                                                                                |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Last metric sample            | 2026-09-05 08:29:34 UTC (`up{instance="pandanus-park-smc01:9090\|:9100\|:9798"}` on `mcp-grafana-apn` — `prometheus`, `node_exporter` and `speedtest_exporter` all   |
|                               |   stop in the same scrape, same fingerprint as kupungarri/windjana)                                                                                                  |
| Last Graylog message          | 2026-09-05 08:40:03 UTC (routine `dhcpd`/`dhclient`/cron/mail/squid traffic — nothing anomalous). **Zero** messages of any kind, any log path, from 08:40:04 UTC through |
|                               |   2026-09-07 05:00 UTC when checked (`source:pandanus-park*` via the Teleport-App Graylog path in `03_communication-flows.md`)                                       |
| Boot time                     | Unchanged for the full 30-day lookback (`node_boot_time_seconds` constant at 2026-06-19 22:27 UTC) — ~78 days uptime at time of death, did **not** reboot            |
| `node_load1`/`MemAvailable`   | 0.02–0.7 load, ~6.65–6.7 GB `MemAvailable` flat for hours before — no trend, no pressure, matches the "clean stop" pattern from the ruled-out table                  |
|   at death                    |                                                                                                                                                                      |
| Pre-death log scan            | Searched the hour before death for `panic`, `Under-voltage`, `I/O error`, `EXT4-fs error`, `Out of memory`, `hung_task`, `Call Trace` — zero hits. Only Teleport     |
|                               |   session-audit lines (two brief automated-looking sessions at 07:44 and 08:27 UTC, last one ~12 min before the final log line)                                      |
| Site profile                  | `rcp` flavor, single-SMC site (no `smc02`) — a hang here is a full site outage with no local failover, on top of having no watchdog of any kind                      |
| Status at writing             | Still dark. No on-site power cycle performed yet                                                                                                                     |

This is also the **first time this signature has been corroborated by a full Graylog message search** rather than Prometheus alone — both `wh` cases had non-functional Graylog sidecars (see above), so
"off-box telemetry" there meant Prometheus only. Here, two independent telemetry sources agree to within ~10 minutes on the same death instant, and neither shows any warning trend beforehand.

#### Related live defect — `rise-healthcheck.service` restart storm

`roles/smc_rise_healthcheck/templates/rise-healthcheck.service.j2` is `Type=simple` + `Restart=always` + `RestartSec=10` on a run-once script that `rise-healthcheck.timer` already drives every 60 s.
Measured live on both boxes: **686 restarts/hour** (~16,500/day against the timer's 1,440), ~11,000 journal lines/hour, 257k Graylog messages/day, 65 PIDs/sec spawn churn. It is the **only** RISE unit
not `Type=oneshot`. Noise and needless wear, not the cause of the hang — fix it, but do not mistake it for the root cause.

#### Fleet status at time of writing

`wh` (2026-08-28): same signature, still open: **kintore** dark since ~June 2026, **orrtipa-thurra-bonya** and **yuelamu** dark since ~August 2026. **glen-hill** and **violet-valley** returned
recently after months dark.

`rcp` (2026-09-07): **pandanus-park-smc01** dark since 2026-09-05 08:29 UTC (see above) — first `rcp` instance found. Not yet checked whether other `rcp` sites (single-SMC, no RISE) carry the same
undetected exposure; a fleet-wide `up{flavor="rcp"}` absence sweep has not been run.

#### Recommended fix

Enable a hardware watchdog on every flavor that lacks one:

- `wh`/`nbn_wh` (RPi): `bcm2835_wdt` + `RuntimeWatchdogSec` in `systemd-system.conf`. It is the software-free equivalent of tstik, it survives a userspace lockup, and it costs nothing. Everything else
  in the RISE stack sits above the layer that fails.
- `rcp` (x86): needs the same treatment via the x86-equivalent driver (e.g. `iTCO_wdt`/`sp5100_tco` depending on chassis) plus `RuntimeWatchdogSec` — confirm hardware support per chassis model before
  assuming parity with the RPi fix. `rcp` currently has zero recovery layer of any kind (see "Why `rcp` is exposed too" above), so this is a bigger gap than `wh`'s inert-but-present one.

---

#### Doc drift found during this investigation

`07_hardware-overlay.md` used to state RPi flavors have **1.9 GB RAM**. Both boxes report **7,807 MB** (`free -m`) with a 4.6 GB zram device and a 3.9 GB overlay tmpfs. **Corrected fleet-wide
2026-09-03**: the operator confirms all RPi are Model 4B/8GB, and 20-mile-smc01 (`rct`) independently measured 7807 MB with `/proc/device-tree/model` = "Raspberry Pi 4 Model B Rev 1.5". The 1.9 GB,
2–4 GB and 4–8 GB figures are all superseded; 07_hardware-overlay.md, 01_overview.md and 02_service-map.md were updated in the same pass. Note also that `overlayroot.conf` requests `size=40%` but the
mount lands at 50% of RAM — consistent with the existing "`overlay.size_ratio` is inert" finding in `07_hardware-overlay.md` §8.

---

### WAN Uplink Stuck With No DHCP Lease, Self-Heal Cron Masquerades as "Flapping" (aurukun-smc03, `nbn_accelerate`, 2026-09-04)

| Field                           | Value                                                                                                                                                              |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Error text                      | Operator report: "ping to the internet from `<uplink>` consistently fails" / "it is flapping like every five minutes"                                              |
| Typical context                 | Any `internet0X` uplink (`enp1s0`, `enp2s0`, or a `vlanNNN` sub-interface) that has lost its DHCP lease and cannot renew — confirmed on `aurukun-smc03` (`enp2s0`, |
|                                 |   direct physical uplink into NTD2)                                                                                                                                |
| Cause class                     | Two independent things layered together, easy to conflate: (1) the far-end DHCP server stops answering on this circuit — carrier/NTD-side, not fixable from        |
|                                 |   ansible/smc; (2) every SMC box runs `/interfacecheckv2.sh` via cron (`*/5 * * * * cd / && /bin/bash interfacecheckv2.sh`), which pings 8.8.8.8 out each          |
|                                 |   interface in its `INTERFACES_LIST` and does `systemctl restart dhclient@<iface>.service` on failure. A dead uplink fails every single 5-minute check forever, so |
|                                 |   the box bounces its own `dhclient` on a strict 5-minute cadence — that restart churn is what reads as "flapping" in logs/monitoring, not the physical link       |
| How to tell the two apart       | Kernel `igb` driver log (`journalctl -k \| grep '<iface>.*Link is'`) shows the TRUE physical transition count — on this incident, 2 real link drops in 24h, not    |
|                                 |   hundreds. Compare against `journalctl -u dhclient@<iface>.service \| grep -c 'Started dhclient'` — 288/24h = exactly every 5 min confirms the cron, not the      |
|                                 |   cable, is cycling the client                                                                                                                                     |
| Confirming it's upstream,       | Manually `ip link set <iface> down` then `up`, then `systemctl restart dhclient@<iface>.service` fresh, wait ~20s. If `DHCPDISCOVER` still gets **zero DHCPOFFERs** |
|   not local                     |   immediately after a clean bounce, the local NIC/driver/config is not the cause — the interface resets and re-broadcasts correctly every time, so nothing is      |
|                                 |   answering on the wire                                                                                                                                            |
| Local evidence worth pulling    | `/var/lib/dhcp/dhclient.<iface>.leases` — the last valid lease's `expire` timestamp tells you how long the circuit has actually been dead (here: 11+ days, well    |
|                                 |   before the NTD's own uptime suggested)                                                                                                                           |
| Not a lead                      | NTD/NTD2 device uptime. A recent NTD reboot (short uptime) does not mean the DHCP problem started then — check the lease expiry, not the NTD's uptime, to date the |
|                                 |   actual outage start                                                                                                                                              |
| Resolution                      | None available locally. Escalate to carrier/NBN for the NTD/DHCP pool serving this circuit. `aurukun-smc03`'s config and self-heal cron are both working as        |
|                                 |   designed; there is nothing to fix in ansible                                                                                                                     |
| `tsh` gotcha hit during triage  | `tsh ssh root@<host> -- "<cmd>"` fails with "invalid option" — the `--` separator is forwarded literally to the remote bash. Use `tsh ssh root@<host> "<cmd>"`     |
|                                 |   (no `--`)                                                                                                                                                        |
| Full write-up                   | `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/aurukun/enp2s0-flap.md`                                                                                |
