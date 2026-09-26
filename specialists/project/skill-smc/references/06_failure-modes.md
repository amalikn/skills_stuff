# SMC Failure Modes

## Contents

- [6. Failure Mode Reference](#6-failure-mode-reference)
- [A full `netplan apply` leaves isc-dhcp-server in systemd's start limit (2026-09-27)](#a-full-netplan-apply-leaves-isc-dhcp-server-in-systemds-start-limit-2026-09-27)

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

**Known coverage gap:** there is no per-device `role="internet"` equivalent of `NodeStarlinkInterfacecheckPacketLoss` — see `13_known-issues.md` "No per-device `role: internet` Prometheus alert
exists" and the "interfacecheckv2.sh's Unconditional dhclient Restart" entry below for why this let an outage go undetected.

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

### interfacecheckv2.sh's Unconditional dhclient Restart Can Worsen a Marginal Link (No Backoff)

**Do not read the aurukun entry above as "the self-heal cron is always harmless."** That incident concluded the cron was blameless because the circuit was already fully dead (zero DHCPOFFERs even
after a clean bounce) — cycling `dhclient` on a dead circuit changes nothing. This is the opposite case: the same script's same behavior actively made a **still-recoverable, briefly-degraded** link
worse, observed at `galiwinku-smc01` (`nbn_accelerate`), 2026-09-08.

| Field           | Value                                                                                                                                                                              |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mechanism       | `interfacecheckv2.sh` (`roles/smc_network/templates/interfacecheckv2.sh.j2`) runs via a 5-minute cron, `ping -I <iface> -c4 -W3 8.8.8.8` on every                                  |
|                 |   `role: internet`/`role: starlink` interface, and on **any** failure unconditionally runs `systemctl restart dhclient@<iface>.service` — no consecutive-failure counter, no backoff, |
|                 |   no escalation tier. One failed 4-packet ping is enough to trigger a full DHCP client restart on that interface, every 5 minutes, indefinitely                                    |
| Observed        | `vlan523` on galiwinku went from "briefly degraded during an upstream flap" to a full DHCP lease loss (`No DHCPOFFERS received`,                                                   |
|   failure       |   `No working leases in persistent database - sleeping`) immediately after the script's `dhclient` restart landed inside the same 5-minute window (~11:48 AEST). A link that might |
|                 |   have recovered on its own, or recovered its existing lease via renewal, instead lost the lease entirely and had to renegotiate from scratch                                      |
| Why it can hurt | Restarting `dhclient` on a marginal/flapping link discards the current, possibly-still-valid lease and forces a fresh `DISCOVER`/`OFFER`/`REQUEST`/`ACK` cycle. If the             |
|                 | far end is mid-flap rather than fully dead, the restart can lose a lease that a simple renewal (`dhclient -1`/lease renewal, no restart) would have kept, or can land the          |
|                 | new negotiation in a worse moment of the same flap                                                                                                                                 |
| Not yet         | A consecutive-failure counter/backoff so the script stops restarting `dhclient` after 2-3 consecutive failed cycles and instead just reports via the existing                      |
| implemented     | `my_node_interfacecheck_success` Prometheus metric — restarting a client can't fix a problem that isn't a stale-lease problem (e.g. an upstream ARP failure), and                  |
|                 | continuing to kick a link that's mid-flap risks compounding a transient issue into a harder one                                                                                    |
| Relationship to | The `HostInterfacecheckTextfileCollectorNotUpdated` alert (`SKILL.md` / `06_failure-modes.md` Key Prometheus Alerts) only detects the script itself going stale — it says          |
| monitoring gap  | nothing about a single interface repeatedly failing and being repeatedly restarted while the script keeps running fine. See `13_known-issues.md` "Fleet-Wide Architecture          |
|                 | Risks" for the related per-device `role: internet` alerting gap that let this class of failure go undetected until manual SSH diagnosis                                            |

### ECMP Multipath Hashing Pins Fixed-Destination Traffic to a Single (Possibly Dead) Nexthop — the single most generalizable multi-WAN finding in this pack

Confirmed at `galiwinku-smc01` (`nbn_accelerate`), 2026-09-08. **Presume fleet-wide unless proven otherwise on other hosts** — nothing in Ansible sets `net.ipv4.fib_multipath_hash_policy` anywhere in
the repo, so every multi-WAN site inherits the kernel default. Read `03_communication-flows.md` "Nothing in ansible-wifi builds the ECMP multipath default" first — this entry is the practical
consequence of that unmanaged, emergent ECMP group described there.

| Field                                  | Value                                                                                                                                                       |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Root cause                             | `net.ipv4.fib_multipath_hash_policy` defaults to `0` (L3-only: hashes source+destination IP only, ignoring port/protocol). Every flow to a **fixed**        |
|                                        |   **destination IP** (DNS queries to `8.8.8.8`/`8.8.4.4`, or any monitoring/health-check target pinged by IP) is deterministically pinned to exactly **one** ECMP |
|                                        |   nexthop, permanently, regardless of that nexthop's actual health — and because ECMP membership itself drifts (unmanaged, no health eviction — see         |
|                                        |   `03_communication-flows.md`), which specific link a given destination pins to also silently drifts over time with zero visibility                         |
| Symptom signature (memorize this)      | **Recognize this pattern at any multi-WAN SMC:** pinging an FQDN fails or times out inconsistently, seemingly regardless of which interface (`-I`) is       |
|                                        |   specified, but pinging the same destination by raw IP works fine, and/or hardcoding the resolved IP into `/etc/hosts` "fixes" it                          |
| Why FQDN tests mislead                 | DNS resolution does not respect `ping -I`'s device binding — glibc's resolver uses the box's normal route selection, not the bound test interface. So the   |
|   per-iface testing                    |   DNS lookup step transits whichever single link the destination IP's L3 hash currently pins to. If that link happens to be currently broken, **every**     |
|                                        |   FQDN-based test fails together regardless of which interface is actually under test, while direct-IP tests (no DNS step) correctly show the true          |
|                                        |   per-interface health. This can make a single bad link look like a fleet-wide DNS outage when only one nexthop is actually down                            |
| Fix                                    | `net.ipv4.fib_multipath_hash_policy=1` (adds source/destination port + protocol to the hash — standard "L4" multipath hashing). Lets different              |
|                                        |   flows/retries to the same destination land on different nexthops instead of being permanently glued to one                                                |
| Reboot required                        | **No.** `sysctl -w net.ipv4.fib_multipath_hash_policy=1` takes effect immediately. Persist via a file in `/etc/sysctl.d/`, then `sysctl --system` re-applies |
|                                        |   cleanly, matching what happens at next boot anyway                                                                                                        |
| Live-test procedure (~30s, zero risk)  | Run `ip route get <known-fixed-destination-ip> sport <N1> dport <P> ipproto <proto>` for several arbitrary source port numbers `N`. Under `policy=0` all    |
|                                        |   return the identical nexthop; after switching to `policy=1`, the same commands should return varying nexthops. Provable on any live box in under a minute |
|                                        |   with no traffic impact                                                                                                                                    |
| Applied at galiwinku                   | Live + persisted on 2026-09-08 via a new file `/etc/sysctl.d/60-smc-multiwan-fib-hash.conf` — **on-box only, NOT committed to the ansible-wifi git repo, NOT** |
|                                        |   **rolled into** **`roles/smc_network`** **via Ansible**. A fleet-wide rollout via a `sysctl` module task (`sysctl_set: yes`, `reload: yes`) was proposed but |
|                                        |   **deliberately deferred** pending an observation period on galiwinku alone. **Do not assume this fix is live fleet-wide from this entry alone — check the** |
|                                        |   **actual role/live hosts before relying on it anywhere else.**                                                                                            |

**Important caveat — the fix does NOT give seamless mid-connection failover.** Switching to L4 hashing does not monitor or reroute an already-established flow just because the hash policy changed or
the path went bad — an open TCP connection keeps using its originally-hashed nexthop for its entire lifetime. Only **new** connection attempts (including reconnects of a dropped connection) benefit,
since each gets a fresh ephemeral source port and therefore an independent hash roll. Practical implication: if the link carrying an active session goes bad, that session must first be detected as
dead by whatever keepalive the specific service uses before a reconnect is even attempted — the fix only improves the odds that *that* reconnect attempt succeeds quickly, rather than repeatedly
hashing onto the same dead nexthop forever (the old L3-only failure mode).

**Real production evidence this already hit live infrastructure** — the `autossh-teleport-openssh` systemd service's own log, galiwinku, 2026-09-08 incident window:

```
Sep 08 11:25:32 galiwinku-smc01 autossh[1980298]: ssh: connect to host 3.104.50.51 port 22: No route to host
ssh exited with error status 255; restarting ssh
```

A genuine reconnect attempt failed outright because, under the pre-fix L3-only policy, it hashed onto a nexthop that was ARP-dead at that moment (the service self-recovered on a later retry, now
established via `eno1`). This is concrete proof the pinning issue doesn't just affect DNS lookups — it affects **any** fixed-destination-IP traffic, including the Teleport reverse tunnel itself, since
Teleport's own bastion IP (`3.104.50.51`) is just as subject to the same per-destination hash pinning as `8.8.8.8` is. See `05_troubleshooting.md` Tier 1 for the autossh tunnel check this relates to,
and `03_communication-flows.md` §Backdoor SSH Access for the fallback path when this tunnel itself is the thing affected.

### Port-80 Source-IP Allowlist on the APN VIP (`202.171.100.138` / `wifi-02.activ8me.net.au`) — a site's public IP drifting out of the NAT pool breaks it silently

Confirmed 2026-09-08. **This is an APN-internal policy failure, not a vendor problem** — read `03_communication-flows.md` "`wifi-02.activ8me.net.au` / `202.171.100.138` is APN's OWN keepalived/LVS
VIP" first for the ownership correction that makes this an internal escalation.

| Field                                    | Value                                                                                                                                                     |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mechanism                                | The **port-80** virtual service on `202.171.100.138` enforces a source-IP ACL. Sources inside `119.12.209.0/24` (the fleet's normal NAT pool) are permitted; |
|                                          |   sources outside it are **rejected at the director** with ICMP type 3 code 13 (admin prohibited). **Port 443 carries no such restriction** — HTTP 200 from every |
|                                          |   source tested                                                                                                                                           |
| Symptom signature (memorize this)        | `curl`/`telnet` to **port 80** fails with **"No route to host" in ~1 RTT**, while **ping to the same host succeeds** and **port 443 works**. That combination is an |
|                                          |   ICMP admin-prohibited *reject*, not a routing failure — a genuine routing failure would not let ping through, and a drop/blackhole would time out over  |
|                                          |   seconds rather than answering immediately                                                                                                               |
| Do not confuse with the expected         | `curl` **exit 56** / "Connection reset by peer" means the TCP connection reached **ESTABLISHED** and the application then reset it — this is the **normal** behaviour |
|   behaviour other sites see              |   of this endpoint and is what a healthy in-pool site looks like. `curl` **exit 7** / "No route to host" means the connection **never established at all** — that |
|                                          |   is the allowlist reject. Always capture `rc=$?` separately; the two are trivially distinguishable by exit code and completely different diagnoses       |
| Confirmed out-of-range sources           | `galiwinku-smc01` public IP `119.12.211.80`, and `cw-teleport01` `3.104.50.51` — two independent sources, both rejected on port 80, both fine on 443      |
| Root cause (galiwinku case)              | The site's **carrier NAT placed it in `119.12.211.0/24` instead of the fleet's `119.12.209.0/24`**, silently putting it outside the allowlist. **No config** |
|                                          |   **change was made on either side and nothing alerted.** Any site whose public IP drifts out of the pool breaks identically and just as silently         |
| Fix path                                 | Either add the range to the director's allowlist, or — **preferred** — restore the site to the fleet's NAT pool so the allowlist stays a tight,           |
|                                          |   meaningful control                                                                                                                                      |
| Investigation limit hit                  | **SSH to the director (`202.171.100.132:22`) is FILTERED from `cw-teleport01`**, so the allowlist rule itself could not be read in-session. The behaviour |
|                                          |   above is inferred from the ICMP responses, not from the rule text                                                                                       |

**Prevention**: nothing today audits site public egress IPs against the expected pool. See `03_communication-flows.md` "Per-Site Public Egress IP" for the `curl -sS https://api.ipify.org` check, the
known per-site values, and the recommended fleet-wide audit. For the method used to prove the rejection was generated at the far end rather than by a nearby middlebox, see `05_troubleshooting.md`
"Cross-Tier: Reject vs Drop, Where a Rejection Was Generated, and On-Box Tooling Gotchas".

### Expired `tsh` Certificate Masquerades as a Fleet-Wide Device Failure (2026-09-25/26); a Refusing Box Masquerades as a Site Failure (aurukun, 2026-09-22/23)

Found by unified-network-controller while building its alarm engine (its CHANGELOG 20260926_1810). Any automation that reaches devices through `tsh` (SSH to the SMC, `-L` tunnels) fails every call the
moment the cluster's certificate lapses, and each failure looks like the device's own fault: 94 of 156 monitored devices went `critical` on 2026-09-25 with 17,309 `cert has expired` lines in the
collector log and nothing naming the certificate. The same week, "Aurukun polls failing since 2026-09-22" was `aurukun-smc01` refusing SSH on the 22nd and 23rd, then the certificate; the site's other
two boxes were fine.

- **Check first, before any device diagnosis:** `tsh status` for each cluster you will cross (`teleport.apn.au`, `teleport.communitywifi.net.au`: separate logins, separate expiries); the controller
  now refuses to poll a cluster whose certificate has lapsed and raises one alarm for it instead of one per device (`unified-network-controller/wc-local/scripts/run_collector.py`).
- **At a multi-SMC site, fall back to the other boxes** before calling the site down: `01_overview.md`'s "any box is a valid jump host" is now implemented for the controller's pushes
  (`unified-network-controller/wc-local/scripts/batch_push_devices.py`, 2026-09-26) and holds for hand diagnosis too.
- Related earlier trap, same shape (the tool's error reads as the fleet's): `--cluster=` instead of `--proxy=` on `teleport.communitywifi.net.au`, `01_overview.md` "Remote Access".

## A full `netplan apply` leaves isc-dhcp-server in systemd's start limit (2026-09-27)

Seen on the virtual SMC `malik-rcp01` (Ubuntu 22.04, ansible-wifi `smc_bases.yml` shape) during unified-network-controller's Step 7 rehearsal, on an unchanged config. Mechanism: the `smc_dhcpd` role
installs `/etc/networkd-dispatcher/routable.d/00-isc-dhcp-server-restart.sh`, which restarts `isc-dhcp-server` whenever a link becomes routable; `netplan apply` bounces every managed link at once
(twelve on that box: three bridges, nine VLAN sub-interfaces), dhcpd restarts on each of them within seconds, and systemd stops it with `start-limit-hit`. The unit then shows `failed` and the site
serves no DHCP until someone runs `systemctl reset-failed isc-dhcp-server; systemctl restart isc-dhcp-server`. A health check taken a few seconds after the apply can pass one second before it happens
(02:07:39 ok, 02:07:40 failed).

What avoids it: the apply surface ansible-wifi's own handler uses, `netplan generate` then `networkctl reload`, which reconfigures only the links whose config changed; and, after any apply or
rollback, `systemctl reset-failed` plus `restart` of the services that bind to the bridges (`isc-dhcp-server`, `named`) before judging health. A rollback that restores the network and leaves DHCP dead
is not a rollback (unified-network-controller `wc-local/scripts/smc_intent.py`, report `docs/reports/controller-option3/step7-smc-intent-rehearsal-20260927_0226.md`).

Same hook, same risk anywhere many links become routable together: a reboot with many VLANs, an `ansible-playbook` run whose `networkctl reload` touches many links at once, a cable event on the trunk
port. Worth checking on a production box after any of those: `systemctl is-active isc-dhcp-server`. The hook's own guard (`systemctl status` before `restart`) does not stop the storm; a
`StartLimitIntervalSec`/`StartLimitBurst` override on the unit, or a debounce in the hook, would. **Proved on the virtual SMC 2026-09-27 02:48 to 02:51:** a drop-in with `StartLimitIntervalSec=60` and
`StartLimitBurst=20` kept the unit active through a full `netplan apply` (6 restarts) and a simultaneous bounce of the three bridges (3 restarts); a debounced hook (`systemd-run --on-active=5 --unit
unc-dhcpd-debounce --collect systemctl restart isc-dhcp-server`, re-armed per event) kept it active with 1 restart in each case. The drop-in survives the storm, the debounce removes it; both together
cover a handler restart landing inside a burst. Recorded, with the box restored, in local-knowledge-ansible issues/rcp-fleet/rcp-dhcpd-start-limit-on-link-flap-20260927_0238.md. `UNVERIFIED` on a
physical SMC: the count of links that flap under a real reload there.
