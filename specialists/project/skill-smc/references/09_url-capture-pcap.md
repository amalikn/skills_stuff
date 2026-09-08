# SMC URL Capture and PCAP Workflows

## Contents
- Why url_capture was rewritten
- Replacement architecture
- Design decisions
- Remote storage layout
- Ansible role changes
- systemd service
- Node and Ansible verification
- Fetching PCAPs
- Rollout policy
- Fleet deployment lessons
- PIN/session enforcement degradation

## 10. url_capture v2 — Python Streaming Service

### Why the Rewrite

The legacy `screen` + cron architecture had three problems:
1. **SSD wear** — tcpdump wrote one large continuous `.pcap` to `/url_capture/` (SSD); rsync
   shipped data up to 8 hours late accumulating ~22MB/day on disk with no rotation.
2. **Fragile supervision** — a `*/2` cron checked whether a `screen` session existed; race
   condition possible if cron fired while tcpdump was dying. Restart latency up to 2 min.
3. **No observability** — state was visible only via `screen -ls`; no structured logs, no stats.

### What Replaced It

A single Python daemon (`url_capture_manager.py`) installed as a **systemd service** replaces
all three cron jobs.

| Removed cron | Replaced by |
|---|---|
| `*/2` screen watchdog | `systemd Restart=always` (15 s → 60 s restart delay) |
| `23:59` midnight kill | Boundary-aware chunk duration — the last chunk before midnight is shortened so the next day starts in a new file |
| `0,8,16` rsync | Continuous `drain_queue()` loop inside daemon |
| `screen` package | Removed from role package list |

During migration, `v1_teardown.yml` removes the v1 crons, stops the legacy `screen`
capture, waits for tcpdump to close the active file, then performs a full rsync flush of
`/url_capture/` to the legacy remote hostname directory. That final flush is a hard gate:
SSH or rsync failure must fail the play rather than being ignored.

`v2_setup.yml` also performs an idempotent legacy-data safety flush before starting or
restarting v2. If any old `/url_capture/YYYYMM/*.pcap` files still exist locally, it rsyncs
only missing or changed legacy PCAPs to the legacy remote hostname directory, marks changed
only when files transfer, and fails the play on SSH or rsync errors. After that flush
completes successfully, `v2_setup.yml` clears the contents of the local legacy
`/url_capture/` directory so already-flushed v1 files do not remain on the SMC disk.

### Architecture

```
tcpdump subprocess (5-min chunk)
    ↓ capture chunk → /run/url_capture/work/<host>-bridge_501-YYYYMMDD_HHMMSS.pcap
    ↓ compress (pigz → gzip fallback) → .pcap.gz
    ↓ move to /run/url_capture/ (tmpfs — RAM, no SSD write)
    ↓ upload via SCP (atomic: .part → rename) to remote
    ↓ delete from tmpfs on success
    ↓ repeat
```

**Three selectable modes** (set via `url_capture_mode` Ansible var):

| Mode | Queue | On upload failure |
|---|---|---|
| `tmpfs-buffer` (default) | `/run/url_capture/` (RAM, 256 MB cap) | Queue in RAM; evict oldest when cap hit |
| `stream-only` | None | Drop chunk; increment `dropped` counter |
| `disk-spool` | `/url_capture/spool/` (disk, 1 GB cap) | Accumulate on disk; drain when link recovers |

**Why tmpfs-buffer is default:** satellite links drop frequently but briefly. 256 MB holds
~50–250 chunks — enough to survive hours of outage without SSD writes.

**Explicit tmpfs mount:** v2 mounts `/run/url_capture` with `run-url_capture.mount`.
This makes the RAM-backed buffer visible as its own mount in `findmnt` output instead of
only inheriting the parent `/run` tmpfs mount.

**tmpfs vs zram:** tmpfs is a RAM-backed virtual filesystem. zram is compressed RAM used as
swap. URL capture uses tmpfs for low-latency staging — not zram. pcap data compresses
poorly (high entropy) so zram's compression advantage is minimal here.

### Key Design Decisions

- **tcpdump primary** (not dumpcap): already in use, operationally familiar, supports `-w -`
  for direct pipeline. dumpcap has stronger ring/rotation but adds new operational path.
- **5-minute chunks**: 288 files/day. Chosen for upload atomicity and RAM efficiency. The
  chunk that reaches midnight in Melbourne local time is shortened so pcap contents do not
  span calendar days.
- **YYYYMMDD/ subfolders on remote**: keeps per-day dir to 288 files (manageable for `ls`).
  Flat YYYYMM/ would be ~8,640 files/month per SMC. The folder date is derived from the
  timestamp embedded in the `.pcap.gz` filename, not upload wall-clock time, so a chunk that
  starts just before midnight stays under the capture-start day.
- **Filename keeps full hostname**: `amata-smc01-bridge_501-20260421_083000.pcap.gz`.
  Canonical source identifies the SMC by full hostname for unambiguous attribution.
- **SIGTERM handler**: sets a stop flag and terminates the tcpdump subprocess cleanly on
  `systemctl stop`. Without this, tcpdump stays as an orphan writing to work dir.
- **Work dir stays on tmpfs**: default work dir is `/run/url_capture/work`, not `/tmp`, so
  current chunks and queued chunks stay on the same RAM-backed filesystem. The manager also
  falls back to copy+unlink when a non-default mode crosses filesystems.
- **Mount is explicit**: `url-capture.service` requires `run-url_capture.mount`, whose
  `Where=/run/url_capture` and `Type=tmpfs` make the RAM buffer obvious during operations.
- **Orphan work recovery**: on startup the manager scans `/run/url_capture/work` for closed
  orphan `.pcap` or `.pcap.gz` files from interrupted captures, compresses/queues/uploads them
  through the normal path, and removes empty pcap headers.
- **`--healthcheck` flag**: prints stats JSON and exits 0 for cron/nagios health checks
  without stopping the service.

### Remote Storage Layout

```
/home/sslurlcapture/urlcapture_storage/
  amata-smc01/
    20260421/                               ← YYYYMMDD subfolder (288 files/day)
      amata-smc01-bridge_501-20260421_000000.pcap.gz
      amata-smc01-bridge_501-20260421_000500.pcap.gz
      ...
    20260422/
      ...
```

SSH key: `/var/local/sslurlcapture/sslurlcapture.id_rsa` (unchanged from legacy).
Remote user: `sslurlcapture` (unchanged).

### Ansible Role Changes (smc_url_capture)

**New files:**
- `roles/smc_url_capture/files/url_capture_manager.py` — Python daemon
- `roles/smc_url_capture/templates/url-capture.service.j2` — systemd unit
- `roles/smc_url_capture/templates/run-url_capture.mount.j2` — explicit tmpfs mount for
  `/run/url_capture`

**Modified files:**
- `roles/smc_url_capture/vars/urlcapture_vars.yml` — 6 new vars added:
  ```yaml
  url_capture_manager_script: /usr/local/sbin/url_capture_manager.py
  url_capture_mode: tmpfs-buffer
  url_capture_iface: bridge_501
  url_capture_chunk_seconds: 300
  url_capture_tmpfs_dir: /run/url_capture
  url_capture_tmpfs_mount_unit: run-url_capture.mount
  url_capture_tmpfs_cap_mb: 256
  ```
- `roles/smc_url_capture/tasks/main.yml` — `screen` → `python3`; crons → service

**Unchanged files (do not modify):**
- `roles/smc_url_capture/files/url_capturev1.sh` — legacy, kept for rollback reference
- `roles/smc_url_capture/templates/rsync_urlcapture.sh.j2` — legacy rsync script; still
  deployed to `/var/local/sslurlcapture/rsync_urlcapture.sh` for manual rollback use (no cron)

**Canonical Python source** (update here, then copy to role):
```
/Volumes/Data/_ai/_project/project_stuff/apn/smc-file-writing-analysis/plans/dns-query-capture-manager.py
```

### systemd Service

```ini
[Mount]
What=tmpfs
Where=/run/url_capture
Type=tmpfs
Options=mode=0755,size=256M,nosuid,nodev,noexec
```

```ini
[Unit]
Requires=run-url_capture.mount
Wants=network-online.target time-sync.target
After=network-online.target time-sync.target run-url_capture.mount

[Service]
Type=simple
Environment=TZ=Australia/Melbourne
ExecStartPre=/usr/sbin/ntp-wait -n 60 -s 5 -v
ExecStart=/usr/bin/python3 /usr/local/sbin/url_capture_manager.py \
  --mode tmpfs-buffer --iface bridge_501 --chunk-seconds 300 \
  --remote-host {{ teleport_fqdn }} ...
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal
```

### Verification (on SMC node after deploy)

```bash
# Service status
systemctl status url-capture
journalctl -u url-capture -f

# After first chunk (~5 min) — tmpfs queue draining
ls /run/url_capture/

# Confirm explicit RAM mount
findmnt -T /run/url_capture/work -o TARGET,SOURCE,FSTYPE,OPTIONS
df -T /run/url_capture/work

# Health check (non-disruptive)
python3 /usr/local/sbin/url_capture_manager.py --healthcheck

# Confirm old crons gone
crontab -l | grep -E 'url_capturev1|tcpdump|rsync_urlcapture'   # should return nothing

# On remote — new YYYYMMDD subfolder
ls /home/sslurlcapture/urlcapture_storage/<hostname>/$(date +%Y%m%d)/
```

### Ansible verification

```bash
ansible-lint roles/smc_url_capture/
ansible-playbook smc_bases.yml -i inventories/<flavor>/prod \
  --tags smc_url_capture --check --limit <canary_host>
```

### Fetching pcaps (smc_get_pcapv7.yml)

Use `ansible-malik/smc_get_pcapv7.yml` (v7) for mixed legacy/v2 URL-capture pulls.
During migration a site may still have legacy monthly `YYYYMM/` directories, v2 daily
`YYYYMMDD/` directories, or both. v7 handles both layouts for the requested month.

**v7 fetch flow:**
1. Prompts for `YYYYMM` (e.g. `202604`)
2. Finds matching `YYYYMM` and `YYYYMMDD` dirs for that month under each host dir
3. Groups matching dirs by site into `site_capture_dir_map`
4. Tars all matched dirs per site into one monthly archive:
   `amata-smc01-bridge_501-202604-monthly.tar.gz`
5. Rsyncs archives to local `fetched/nbn_accelerate/` or `fetched/rcp/`
6. Extracts archives and flattens any `YYYYMM` / `YYYYMMDD` folders into `extracted/<flavor>/<site>/`
7. Decompresses `.pcap.gz` → `.pcap` via `pigz -df`, or `gzip -df` when pigz is unavailable
8. Deletes zero-byte and `generic-*.pcap` files
9. Runs `pcapfix` on remaining `.pcap` files and removes originals when a fixed copy is produced
10. Writes `checked_pcaps.txt` in the extracted root after all checks complete

**Local output layout:**
```
fetched/
  nbn_accelerate/
    amata-smc01-bridge_501-202604-monthly.tar.gz
extracted/
  nbn_accelerate/
    amata/                                    ← short name (regex strips -smc01)
      state                                   ← "sa"
      amata-smc01-bridge_501-20260401_000000.pcap
      amata-smc01-bridge_501-20260401_000500.pcap
      ...                                     ← daily and/or 5-minute pcaps after checks
checked_pcaps.txt                             ← relative list of final checked pcaps
```

Note: the extracted folder uses the **short site name** (`amata`) from the regex
`'^(.*?)-smc0.*'` applied to the archive filename. The pcap filenames themselves
retain the full hostname (`amata-smc01-...`) as captured at source.
Do not expect `YYYYMM` or `YYYYMMDD` subdirectories under the extracted site folder after
`--tags process_files`; the processing step intentionally flattens them.

Validation anchor: APN `202605` was validated with mixed inputs from `kalumburu-smc01`
(legacy `202605/` plus v2 `20260501/`...) and `jigalong-smc01` (legacy `202605/` only).
The process run completed with `checked_pcap_count=1696`, no retained `.pcap.gz` files,
and final pcaps directly under `extracted/rcp/kalumburu/` and `extracted/rcp/jigalong/`.

**Usage:**
```bash
# fetch all
ansible-playbook -i inventories/rcp/prod ../ansible-malik/smc_get_pcapv7.yml --tags fetch_files

# fetch specific flavor
ansible-playbook -i inventories/cw/prod ../ansible-malik/smc_get_pcapv7.yml \
  -l cw-teleport01,localhost, --tags fetch_files

# process only (after manual fetch or re-run)
ansible-playbook -i inventories/apn/prod ../ansible-malik/smc_get_pcapv7.yml \
  -l apn-teleport01,localhost, --tags process_files
```

### Rollout Policy

- Canary on 1–3 SMC nodes first
- Verify the expected remote storage appears for the site: legacy `YYYYMM/`, v2 `YYYYMMDD/`, or both during migration
- Verify `journalctl -u url-capture` shows clean chunk/upload cycles
- Staged fleet rollout after canary passes
- `rsync_urlcapture.sh` stays deployed (no cron) as manual drain option during canary

### Fleet Deployment Lessons (2026-05-18)

#### Ansible + Teleport: host key verification fails for new hosts
**Symptom:** `ansible-playbook` fails with `Host key verification failed` on a host that `tsh ssh` reaches fine.

**Cause:** The `*.teleport.apn.au` block in `~/.ssh/config` has `ProxyCommand` (tsh) but no `UserKnownHostsFile`. Ansible falls back to `~/.ssh/known_hosts`, which has no entry for new Teleport-managed hosts. tsh uses `~/.tsh/known_hosts` (Teleport CA-signed) which trusts all cluster hosts automatically.

**Fix:** Add `UserKnownHostsFile /Users/malik.ahmad/.tsh/known_hosts` to the `Host *.teleport.apn.au !teleport.apn.au` block in `~/.ssh/config`. This is a one-time fix — all future Teleport hosts work without per-host key acceptance.

#### cisofy-lynis apt source blocks `apt-get update` on satellite-linked sites
**Symptom:** `apt-get update` fails silently (empty error, rc≠0) on nbn_accelerate or other sites.

**Cause:** `/etc/apt/sources.list.d/cisofy-lynis.list` contains a `deb https://packages.cisofy.com/...` entry. Sites on satellite links cannot reach this host.

**Fix:** The `custom_apt_update_cache.yml` helper now comments out that line via `ansible.builtin.lineinfile` (with `backrefs: true`) before running apt. Check for other unreachable third-party apt sources when `apt-get update` fails with empty errors.

#### Broad nightly `pkill -9 python3` kills url-capture.service
**Symptom**: `url-capture.service` is killed at 23:59 every night; journal shows kill + restart at 00:00:02. Orphan pre-midnight chunk uploads immediately after restart. No data loss observed but lifecycle is not clean.

**Cause**: `roles/smc_application/tasks/main.yml` task `Kill Python3 processes to avoid stale processes` installs a root crontab:
```
59 23 * * * pkill -9 python3 >/dev/null 2>&1
```
This was intended for `webapp.py` (WH flavor). It kills **all** python3 processes, including `url_capture_manager.py`.

**Fix**: Replace broad `pkill -9 python3` with a narrowly targeted kill (process name or pid file). Gate it to the specific flavor that needs it (`hotspot_flavor == 'wh'`). Not yet implemented as of 2026-05-07.

#### `rsync_urlcapture.sh.j2` — two bugs fixed (2026-05-01)
Even though v1 rsync crons are removed under url_capture v2, the script stays deployed for manual rollback use. Two bugs were corrected in the template:

1. **`yearmonth_today` not evaluated**: Was a literal string `$(date +%Y%m)` missing the outer `$()` → never expanded → rsync failed to find today's directory. Fixed by wrapping in command substitution.

2. **Missing month-boundary rsync**: On the 1st of the month there was no block to rsync the previous month's data. Added: a conditional block that fires only when today ≠ yesterday's month and rsyncs the prior month's directory.

**Location**: `roles/smc_url_capture/templates/rsync_urlcapture.sh.j2`

#### Expected daily url-capture volume: ~270 files/day
5-minute chunks over ~22.5h (accounting for midnight boundary restart overhead) = ~270 `.pcap.gz` files per day in `urlcapture_storage/<hostname>/YYYYMMDD/`. Lower counts indicate service gaps. May 4, 2026 showed 249 files due to the SSH deadlock incident (~1.75h gap).

#### Healthy check commands (post-deploy verification)
```bash
# Service status
tsh ssh root@<host> "systemctl status url-capture.service --no-pager && journalctl -u url-capture.service -n 10 --no-pager"

# Remote storage file count for today
tsh ssh root@<host> "ssh -i /var/local/sslurlcapture/sslurlcapture.id_rsa -o StrictHostKeyChecking=no sslurlcapture@teleport.apn.au 'ls /home/sslurlcapture/urlcapture_storage/<host>/$(date +%Y%m%d)/ | wc -l'"
```

### PIN/Session Enforcement Degraded While Content Filtering Still Works (`nbn_accelerate` / `rcp`)

| Field | Value |
|---|---|
| Error text | Users report PIN/session behavior inconsistent while web filtering still blocks content |
| Typical context | Host in storage-degraded or read-only state; automation attempts to restart policy services but write paths fail |
| Cause class | Control-plane partial failure: per-user mark refresh failed, but baseline DNS/HTTP filter redirect path remains active |
| Immediate checks | `systemctl status netfilter-persistent`; `iptables -t mangle -S ECLIPSE_MARK`; `iptables -t mangle -S ECLIPSE_METERED_TIME`; `dig @127.0.0.1 www.pornhub.com`; `tail -n 200 /var/log/squid/access.log \| egrep 'TCP_DENIED|403|302'` |
| Detection pattern | `ECLIPSE_MARK` and `ECLIPSE_METERED_TIME` chains empty, `netfilter-persistent` failed, but Squid denies and Umbrella block IP responses still present |
| Operational impact | Baseline filtering still enforced; per-user/PIN granularity unreliable (stale sessions may continue, new/rollover PIN behavior inconsistent) |
| Fix pattern | Recover host to RW / alternate disk, restore `netfilter-persistent`, repopulate mangle mark chains via normal role/service path, then validate end-to-end PIN issuance/expiry flow |
| Validation commands | `iptables -t mangle -S ECLIPSE_MARK` shows populated rules; non-zero connmark distribution for active bridge_501 users; month rollover PIN expiry/new PIN flow verified from app to kernel marks |

---
