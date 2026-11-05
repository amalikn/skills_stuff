# SMC URL Capture and PCAP Workflows

## Contents

- [10. url_capture v2 — Python Streaming Service](#10-url_capture-v2--python-streaming-service)
  - [Why the Rewrite](#why-the-rewrite)
  - [What Replaced It](#what-replaced-it)
  - [Architecture](#architecture)
  - [Key Design Decisions](#key-design-decisions)
  - [Remote Storage Layout](#remote-storage-layout)
  - [Ansible Role Changes (smc_url_capture)](#ansible-role-changes-smc_url_capture)
  - [systemd Service](#systemd-service)
  - [Verification (on SMC node after deploy)](#verification-on-smc-node-after-deploy)
  - [Ansible verification](#ansible-verification)
  - [Fetching pcaps (smc_get_pcapv7.yml)](#fetching-pcaps-smc_get_pcapv7yml)
  - [Learned 2026-11-05 — v7 fetch timeouts, and the resumable v8 (`smc_get_pcapv8.yml`)](#learned-2026-11-05--v7-fetch-timeouts-and-the-resumable-v8-smc_get_pcapv8yml)
  - [Rollout Policy](#rollout-policy)
  - [Fleet Deployment Lessons (2026-05-18)](#fleet-deployment-lessons-2026-05-18)
  - [PIN/Session Enforcement Degraded While Content Filtering Still Works (`nbn_accelerate` / `rcp`)](#pinsession-enforcement-degraded-while-content-filtering-still-works-nbn_accelerate--rcp)
- [Learned 2026-10-29 — "URL capture" captures DNS queries only](#learned-2026-10-29--url-capture-captures-dns-queries-only)
- [Learned 2026-11-05 (b) — what the DNS capture holds, its gaps, and the pcapfix cost](#learned-2026-11-05-b--what-the-dns-capture-holds-its-gaps-and-the-pcapfix-cost)

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

> **Branch reach (checked 2026-10-27):** v2 (`c19a61fa`, 2026-06-09 onward) is on `rise-multi` and side branches, not on `rise`, which still carries only the v1 role (`url_capturev1.sh`, no
> `v2_setup.yml`). A `smc_url_capture` run from `rise` deploys v1. See `13_known-issues.md` (Branch reach).

### Why the Rewrite

The legacy `screen` + cron architecture had three problems:
1. **SSD wear** — tcpdump wrote one large continuous `.pcap` to `/url_capture/` (SSD); rsync shipped data up to 8 hours late accumulating ~22MB/day on disk with no rotation.
2. **Fragile supervision** — a `*/2` cron checked whether a `screen` session existed; race condition possible if cron fired while tcpdump was dying. Restart latency up to 2 min.
3. **No observability** — state was visible only via `screen -ls`; no structured logs, no stats.

### What Replaced It

A single Python daemon (`url_capture_manager.py`) installed as a **systemd service** replaces all three cron jobs.

| Removed cron          | Replaced by                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `*/2` screen watchdog | `systemd Restart=always` (15 s → 60 s restart delay)                                                             |
| `23:59` midnight kill | Boundary-aware chunk duration — the last chunk before midnight is shortened so the next day starts in a new file |
| `0,8,16` rsync        | Continuous `drain_queue()` loop inside daemon                                                                    |
| `screen` package      | Removed from role package list                                                                                   |

During migration, `v1_teardown.yml` removes the v1 crons, stops the legacy `screen` capture, waits for tcpdump to close the active file, then performs a full rsync flush of `/url_capture/` to the
legacy remote hostname directory. That final flush is a hard gate: SSH or rsync failure must fail the play rather than being ignored.

`v2_setup.yml` also performs an idempotent legacy-data safety flush before starting or restarting v2. If any old `/url_capture/YYYYMM/*.pcap` files still exist locally, it rsyncs only missing or
changed legacy PCAPs to the legacy remote hostname directory, marks changed only when files transfer, and fails the play on SSH or rsync errors. After that flush completes successfully, `v2_setup.yml`
clears the contents of the local legacy `/url_capture/` directory so already-flushed v1 files do not remain on the SMC disk.

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

| Mode                     | Queue                                  | On upload failure                            |
| ------------------------ | -------------------------------------- | -------------------------------------------- |
| `tmpfs-buffer` (default) | `/run/url_capture/` (RAM, 256 MB cap)  | Queue in RAM; evict oldest when cap hit      |
| `stream-only`            | None                                   | Drop chunk; increment `dropped` counter      |
| `disk-spool`             | `/url_capture/spool/` (disk, 1 GB cap) | Accumulate on disk; drain when link recovers |

**Why tmpfs-buffer is default:** satellite links drop frequently but briefly. 256 MB holds ~50–250 chunks — enough to survive hours of outage without SSD writes.

**Explicit tmpfs mount:** v2 mounts `/run/url_capture` with `run-url_capture.mount`. This makes the RAM-backed buffer visible as its own mount in `findmnt` output instead of only inheriting the parent
`/run` tmpfs mount.

**tmpfs vs zram:** tmpfs is a RAM-backed virtual filesystem. zram is compressed RAM used as swap. URL capture uses tmpfs for low-latency staging — not zram. pcap data compresses poorly (high entropy)
so zram's compression advantage is minimal here.

### Key Design Decisions

- **tcpdump primary** (not dumpcap): already in use, operationally familiar, supports `-w -` for direct pipeline. dumpcap has stronger ring/rotation but adds new operational path.
- **5-minute chunks**: 288 files/day. Chosen for upload atomicity and RAM efficiency. The chunk that reaches midnight in Melbourne local time is shortened so pcap contents do not span calendar days.
- **YYYYMMDD/ subfolders on remote**: keeps per-day dir to 288 files (manageable for `ls`). Flat YYYYMM/ would be ~8,640 files/month per SMC. The folder date is derived from the timestamp embedded in
  the `.pcap.gz` filename, not upload wall-clock time, so a chunk that starts just before midnight stays under the capture-start day.
- **Filename keeps full hostname**: `amata-smc01-bridge_501-20260421_083000.pcap.gz`. Canonical source identifies the SMC by full hostname for unambiguous attribution.
- **SIGTERM handler**: sets a stop flag and terminates the tcpdump subprocess cleanly on `systemctl stop`. Without this, tcpdump stays as an orphan writing to work dir.
- **Work dir stays on tmpfs**: default work dir is `/run/url_capture/work`, not `/tmp`, so current chunks and queued chunks stay on the same RAM-backed filesystem. The manager also falls back to
  copy+unlink when a non-default mode crosses filesystems.
- **Mount is explicit**: `url-capture.service` requires `run-url_capture.mount`, whose `Where=/run/url_capture` and `Type=tmpfs` make the RAM buffer obvious during operations.
- **Orphan work recovery**: on startup the manager scans `/run/url_capture/work` for closed orphan `.pcap` or `.pcap.gz` files from interrupted captures, compresses/queues/uploads them through the
  normal path, and removes empty pcap headers.
- **`--healthcheck` flag**: prints stats JSON and exits 0 for cron/nagios health checks without stopping the service.

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
- `roles/smc_url_capture/templates/run-url_capture.mount.j2` — explicit tmpfs mount for `/run/url_capture`

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
- `roles/smc_url_capture/templates/rsync_urlcapture.sh.j2` — legacy rsync script; still deployed to `/var/local/sslurlcapture/rsync_urlcapture.sh` for manual rollback use (no cron)

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

Use `ansible-malik/smc_get_pcapv7.yml` (v7) for mixed legacy/v2 URL-capture pulls. During migration a site may still have legacy monthly `YYYYMM/` directories, v2 daily `YYYYMMDD/` directories, or
both. v7 handles both layouts for the requested month.

**v7 fetch flow:**
1. Prompts for `YYYYMM` (e.g. `202604`)
2. Finds matching `YYYYMM` and `YYYYMMDD` dirs for that month under each host dir
3. Groups matching dirs by site into `site_capture_dir_map`
4. Tars all matched dirs per site into one monthly archive: `amata-smc01-bridge_501-202604-monthly.tar.gz`
5. Rsyncs archives to local `fetched/nbn_accelerate/` or `fetched/rcp/`: one `rsync -avP --checksum --inplace` per Teleport host after all its tars are built, files sent in name order. **A fetched
   file's mtime is when its tar was built on the Teleport host (`-a` keeps the source mtime), not when it arrived**; only the file in flight shows the current time. A long "gap" before the newest file
   is therefore the transfer, not a stall: check by sampling that file's size twice (2026-11-05, rcp 202610: tars built 12:25-12:44, ~7.5 GB at ~9 Mbit/s single stream, newest file at 14:34).
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

Note: the extracted folder uses the **short site name** (`amata`) from the regex `'^(.*?)-smc0.*'` applied to the archive filename. The pcap filenames themselves retain the full hostname
(`amata-smc01-...`) as captured at source. Do not expect `YYYYMM` or `YYYYMMDD` subdirectories under the extracted site folder after `--tags process_files`; the processing step intentionally flattens
them.

Validation anchor: APN `202605` was validated with mixed inputs from `kalumburu-smc01` (legacy `202605/` plus v2 `20260501/`...) and `jigalong-smc01` (legacy `202605/` only). The process run completed
with `checked_pcap_count=1696`, no retained `.pcap.gz` files, and final pcaps directly under `extracted/rcp/kalumburu/` and `extracted/rcp/jigalong/`.

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

### Learned 2026-11-05 — v7 fetch timeouts, and the resumable v8 (`smc_get_pcapv8.yml`)

VERIFIED-OBSERVED (rcp 202610 on apn-teleport01, operator's ansible-apn VM) · Source: `ansible-malik/smc_get_pcapv8.yml` (working tree, not yet committed at this entry) · Falsifier: a v7 fetch of
> 2 h that completes, or a v8 re-run that rebuilds tars already staged.

**Why v7 failed.** rcp 202610 was 17 tars, 10.75 GB. v7's rsync runs as `async: 7200, poll: 0`; async is the hard limit (the status task's `retries: 300 × delay: 60` never mattered). At ~1.2 MB/s one
stream (reference 03, Learned 2026-11-05) the transfer needed ~2.5 h, so Ansible killed rsync at 7,200 s (`Timeout exceeded`, attempt 121). The cleanup task never ran, so the tars stayed in
`/tmp/url_capture/<YYYYMMDD_HHMM>/` (11 GB in a 94%-full root). A re-run of v7 would have wiped `/tmp/url_capture` first and rebuilt every tar.

**v8 = v7 with a resumable fetch (process step unchanged):**
1. Picks the staging dir automatically: `resume_dir` if given, else the dir under `staging_root` (`/tmp/url_capture`) holding the newest `*-bridge_501-<YYYYMM>-monthly.tar.gz[.partial]` (v7 timestamp
   dirs count), else a new `/tmp/url_capture/<flavor>-<YYYYMM>`. Other months' dirs are never picked.
2. No wipe of `/tmp/url_capture` at the start; only the chosen dir is deleted, at the end.
3. Tars are written as `<name>.partial` and renamed when tar exits 0; `creates:` skips a finished tar (`-e rebuild_tars=true` forces a rebuild, e.g. after fetching a month still being captured).
4. rsync: `-a --partial --inplace --exclude='*.partial'`, size+mtime quick check (no `--checksum`), retried `rsync_attempts` (5) times inside one async job of `rsync_async_timeout` (21600 s).
5. Every expected tar is stat'ed on both sides; the staging dir is deleted only if all sizes match.

```yaml
# ansible-malik/smc_get_pcapv8.yml (2026-11-05): staging dir choice
zipped_files_dir: >-
  {{
    resume_dir if (resume_dir | default('') | length > 0)
    else ((earlier_tars.files | sort(attribute='mtime') | last).path | dirname) if (earlier_tars.files | length > 0)
    else (staging_root ~ '/' ~ flavor ~ '-' ~ one_month_prior)
  }}
# tar per site: complete or absent, never half-written under the final name
shell: >
  tar --use-compress-program=pigz -cf {{ tar_part | quote }} -C {{ (url_capture_path ~ '/' ~ site_name) | quote }}
  {{ item.value | map('quote') | join(' ') }} && mv -f {{ tar_part | quote }} {{ tar_final | quote }}
args:
  creates: "{{ omit if (rebuild_tars | bool) else tar_final }}"
```

**The capture store is EFS; the `find` module is slow on it.** `/home/sslurlcapture/urlcapture_storage` on apn-teleport01 is NFS 4.1 through efs-utils (`127.0.0.1:/`, `amazon-efs-mount-watchdog`).
`find: recurse: yes, depth: 2` still lists and stats every entry inside each depth-2 dir before discarding it: one NFS `getattr` per capture file (stack `nfs4_proc_getattr` / `rpc_wait_bit_killable`,
process in state `D`), minutes per task across ~2,274 site/day dirs; v7 has two such tasks (month dirs, day dirs). GNU find with `-maxdepth 2` never opens those dirs: 1.65 s for 202610 (2 month dirs,
527 day dirs, 17 sites). v8 uses:

```yaml
# ansible-malik/smc_get_pcapv8.yml (2026-11-05): one pruned scan instead of two find-module calls
- name: Find YYYYMM and YYYYMMDD capture dirs for requested month at depth 2
  shell: >
    find {{ url_capture_path | quote }} -mindepth 2 -maxdepth 2 -type d
    \( -name {{ one_month_prior | quote }} -o -name '{{ one_month_prior }}[0-9][0-9]' \) -print
  register: capture_dir_scan
  changed_when: false
```
Its output is reshaped into v7's `found_month_dirs` / `found_day_dirs` (`{files: [{path}]}`), so the tasks after it are unchanged. Mock-tested locally (resume, new dir, override, rsync retry, rsync
fails, rsync copies nothing, rebuild, decoy dirs); first real run 2026-11-05 resumed `/tmp/url_capture/20261105_1218` (17 tars reused) and passed at 17:04: size check, staging dir deleted, 17 tars (10
GB) gzip-valid. Promoted over v6 on 2026-11-05 (operator-approved) after the 202610 process run finished (154,097 checked pcaps, 143 fixed); v8 is the active playbook.

**A fetched file's timestamp is not its arrival time** (step 5 of the v7 flow above) holds for v8 too.

**Resume a failed fetch:** run the same fetch command again; nothing to pass.

### Rollout Policy

- Canary on 1–3 SMC nodes first
- Verify the expected remote storage appears for the site: legacy `YYYYMM/`, v2 `YYYYMMDD/`, or both during migration
- Verify `journalctl -u url-capture` shows clean chunk/upload cycles
- Staged fleet rollout after canary passes
- `rsync_urlcapture.sh` stays deployed (no cron) as manual drain option during canary

### Fleet Deployment Lessons (2026-05-18)

#### Ansible + Teleport: host key verification fails for new hosts
**Symptom:** `ansible-playbook` fails with `Host key verification failed` on a host that `tsh ssh` reaches fine.

**Cause:** The `*.teleport.apn.au` block in `~/.ssh/config` has `ProxyCommand` (tsh) but no `UserKnownHostsFile`. Ansible falls back to `~/.ssh/known_hosts`, which has no entry for new
Teleport-managed hosts. tsh uses `~/.tsh/known_hosts` (Teleport CA-signed) which trusts all cluster hosts automatically.

**Fix:** Add `UserKnownHostsFile /Users/malik.ahmad/.tsh/known_hosts` to the `Host *.teleport.apn.au !teleport.apn.au` block in `~/.ssh/config`. This is a one-time fix — all future Teleport hosts work
without per-host key acceptance.

#### cisofy-lynis apt source blocks `apt-get update` on satellite-linked sites
**Symptom:** `apt-get update` fails silently (empty error, rc≠0) on nbn_accelerate or other sites.

**Cause:** `/etc/apt/sources.list.d/cisofy-lynis.list` contains a `deb https://packages.cisofy.com/...` entry. Sites on satellite links cannot reach this host.

**Fix:** The `custom_apt_update_cache.yml` helper now comments out that line via `ansible.builtin.lineinfile` (with `backrefs: true`) before running apt. Check for other unreachable third-party apt
sources when `apt-get update` fails with empty errors.

#### Broad nightly `pkill -9 python3` kills url-capture.service
**Symptom**: `url-capture.service` is killed at 23:59 every night; journal shows kill + restart at 00:00:02. Orphan pre-midnight chunk uploads immediately after restart. No data loss observed but
lifecycle is not clean.

**Cause**: `roles/smc_application/tasks/main.yml` task `Kill Python3 processes to avoid stale processes` installs a root crontab:
```
59 23 * * * pkill -9 python3 >/dev/null 2>&1
```
This was intended for `webapp.py` (WH flavor). It kills **all** python3 processes, including `url_capture_manager.py`.

**Fix**: Replace broad `pkill -9 python3` with a narrowly targeted kill (process name or pid file). Gate it to the specific flavor that needs it (`hotspot_flavor == 'wh'`). Not yet implemented as of
2026-05-07.

#### `rsync_urlcapture.sh.j2` — two bugs fixed (2026-05-01)
Even though v1 rsync crons are removed under url_capture v2, the script stays deployed for manual rollback use. Two bugs were corrected in the template:

1. **`yearmonth_today` not evaluated**: Was a literal string `$(date +%Y%m)` missing the outer `$()` → never expanded → rsync failed to find today's directory. Fixed by wrapping in command
   substitution.

2. **Missing month-boundary rsync**: On the 1st of the month there was no block to rsync the previous month's data. Added: a conditional block that fires only when today ≠ yesterday's month and rsyncs
   the prior month's directory.

**Location**: `roles/smc_url_capture/templates/rsync_urlcapture.sh.j2`

#### Expected daily url-capture volume: ~270 files/day
5-minute chunks over ~22.5h (accounting for midnight boundary restart overhead) = ~270 `.pcap.gz` files per day in `urlcapture_storage/<hostname>/YYYYMMDD/`. Lower counts indicate service gaps. May 4,
2026 showed 249 files due to the SSH deadlock incident (~1.75h gap).

#### Healthy check commands (post-deploy verification)
```bash
# Service status
tsh ssh root@<host> "systemctl status url-capture.service --no-pager && journalctl -u url-capture.service -n 10 --no-pager"

# Remote storage file count for today
tsh ssh root@<host> "ssh -i /var/local/sslurlcapture/sslurlcapture.id_rsa -o StrictHostKeyChecking=no sslurlcapture@teleport.apn.au 'ls /home/sslurlcapture/urlcapture_storage/<host>/$(date +%Y%m%d)/ | wc -l'"
```

### PIN/Session Enforcement Degraded While Content Filtering Still Works (`nbn_accelerate` / `rcp`)

| Field              | Value                                                                                                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Error text         | Users report PIN/session behavior inconsistent while web filtering still blocks content                                                                                         |
| Typical context    | Host in storage-degraded or read-only state; automation attempts to restart policy services but write paths fail                                                                |
| Cause class        | Control-plane partial failure: per-user mark refresh failed, but baseline DNS/HTTP filter redirect path remains active                                                          |
| Immediate checks   | `systemctl status netfilter-persistent`; `iptables -t mangle -S ECLIPSE_MARK`; `iptables -t mangle -S ECLIPSE_METERED_TIME`; `dig @127.0.0.1 www.pornhub.com`; `tail -n 200     | 403                                                                                                                                                                             | 302'`                                                                                                                                                                           |
|  |   /var/log/squid/access.log \| egrep 'TCP_DENIED |  |  |
| Detection pattern  | `ECLIPSE_MARK` and `ECLIPSE_METERED_TIME` chains empty, `netfilter-persistent` failed, but Squid denies and Umbrella block IP responses still present                           |
| Operational impact | Baseline filtering still enforced; per-user/PIN granularity unreliable (stale sessions may continue, new/rollover PIN behavior inconsistent)                                    |
| Fix pattern        | Recover host to RW / alternate disk, restore `netfilter-persistent`, repopulate mangle mark chains via normal role/service path, then validate end-to-end PIN                   |
|                    |   issuance/expiry flow                                                                                                                                                          |
| Validation         | `iptables -t mangle -S ECLIPSE_MARK` shows populated rules; non-zero connmark distribution for active bridge_501 users; month rollover PIN expiry/new PIN flow verified from    |
|   commands         |   app to kernel marks                                                                                                                                                           |

---

## Learned 2026-10-29 — "URL capture" captures DNS queries only

The deployed role's script starts one `tcpdump` per interface with the filter `dst port 53`, so the PCAPs hold DNS queries (domain names), not URLs or paths. `VERIFIED-CODE`:

```bash
# roles/smc_url_capture/files/url_capturev1.sh:121 (ansible-wifi f471c101)
screen -dmS "tcpdump-$int-screen-since-$spawntime" tcpdump -i $int "dst port 53" -nv -Z root -B 8192 -p -s 1500 -w $TODAYS_PATH/$SMC_HOSTNAME-$int-...
```

- Clients using DNS over HTTPS or TLS (RFC 8484, RFC 7858) are invisible to it; the counts are of domains queried, not of traffic.
- Per-application or "top applications per site" reporting is not derivable: the SMC exports interface byte and rate counters on the backhaul, with no flow export or classification. ARP or MAC counts
  are not a connected-devices metric either. Source: apn `docs/wifi-metrics-coverage.xlsx` rows URL Capture, Backhaul Top Applications and Devices Connected (apn 5cba35f).
- DNS query logs of end users are personal information: a design that keeps them needs a privacy basis.

## Learned 2026-11-05 (b) — what the DNS capture holds, its gaps, and the pcapfix cost

VERIFIED-CODE and VERIFIED-OBSERVED (APN/rcp and CW nbn_accelerate 202610 on the operator's Mac; one day per site measured, scratch copies deleted) · Source: ansible-wifi `rise-multi` `c19a61fa`
`roles/smc_url_capture/files/url_capture_manager.py` (line 29, lines 160-185); dns_query `scripts/dns2pdv12.py` · Falsifier: an IPv6 DNS query in a v2 chunk, or a month with no corrupt v2 chunk

- **v2 capture command:** `timeout 300 tcpdump -i bridge_501 "ip and (udp or tcp) and dst port 53 and not src port 53" -p -s 1500 -n -U -w <chunk>` (or `dumpcap ... -a duration:` with `--capture-tool
  dumpcap`). It holds client **queries only** (no answers), **IPv4 only** (`ip` excludes IPv6; 0 IPv6 packets in a sampled chunk), full Ethernet frames (client source MAC present; destination is the
  bridge MAC). A **new tcpdump per 5-minute chunk** leaves a short gap 288 times a day; v2 dropped v1's `-B 8192` and records no kernel drop count.
- **One day, 2026-10-10:** mornington 1,797,566 queries, 662 MACs, 23,735 domains, 68 MB pcap.gz; umoona 4,613 queries, 30 MACs, 325 KB. Mornington: 97.7% of queries to the SMC resolver, **2.3%
  straight to outside resolvers** (resolver logs would miss them), 85% A, 14% AAAA, 0.4% PTR/`.local`; one MAC sent 17.6% of queries (NAT router or busy device, unknown).
- **Smaller formats, measured:** 5-field records (time, MAC, IP, type, name) gzipped 3.2-6.3x smaller than pcap.gz; daily (domain, MAC, count) 27-59x smaller. The report (`dns2pdv12.py`) needs only
  domains and distinct source MACs.
- **pcapfix cost:** process step for 202610 (rcp + nbn_accelerate) ran pcapfix on **154,097** pcaps (55 GB): ~10 ms per file, ~25 min serial; **143 corrupt** (96 legacy v1 files, **47 v2 chunks**,
  0.03% of v2), so v2 chunks still need checking. Parallel: 2,000 chunks 9.7 s serial vs 1.5 s with `xargs -P 12`.
- **macOS tcpdump 4.99.1 (Apple 161) cannot read a pcap from stdin** (`tcpdump: unknown file format` on `gzip -dc f | tcpdump -r -`); decompress to a file first.
- **Proposal, not decided:** convert each chunk on the Teleport host into lossless per-query JSONL records (monthly Parquet) and fetch those instead of PCAPs: local-knowledge-ansible
  `ansible-wifi/plans/url-capture-dns-records-plan-20261105_1747.md`.

```python
# url_capture_manager.py (rise-multi c19a61fa), capture per chunk
DEFAULT_BPF = "ip and (udp or tcp) and dst port 53 and not src port 53"
cmd = ["timeout", str(duration_seconds), "tcpdump", "-i", args.iface, args.bpf, "-p", "-s", "1500", "-n", "-U", "-w", str(out_pcap)]
```
No visual surface.
