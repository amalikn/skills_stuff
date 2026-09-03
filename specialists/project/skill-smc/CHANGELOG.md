# skill-smc Changelog

## 20260827_1800 — Code notes documented as an authoring surface; stale lint paragraph corrected (v0.1.24 -> v0.1.25)

**New section in `references/08_ansible-authoring.md`: "Code notes: where the long explanation goes, and what it can and cannot survive."** RULE-006's comment/note split was governed but undocumented
here, so an agent reading the authoring reference had no idea the surface existed. Covers the routing test (**if being unaware of it would cause a bug, it goes in the file**), the prohibition on
referencing notes from code, and what a note now records.

**Provenance and its ranking are the load-bearing part.** A note carries a normalized `sha256`, three lines of verbatim context either side, the authoring branch, and the commit with a `(dirty)`
marker. Ranked strictly: content hash authoritative, commit tested by *ancestry rather than equality* so it survives a merge, branch a display label — and **metadata may only clear a warning, never
raise one**.

**The measurement worth carrying forward:** of 24 notes anchored on `internet-label-rename`, tested against `master`, **21 were out of range**, 1 moved, 2 drifted, 0 exact — `smc_rsyslog/tasks/main.yml`
is 26 lines there against ~300 on the branch. Out-of-range **crashes extension activation**, and a crashed activation never regenerates `INDEX.json`, so a reload does not clear it. Hence the
operational rule: run `check_note_anchors.py` after any branch switch or out-of-editor edit, not only after authoring — re-anchoring is driven by `onDidChangeTextDocument`, which fires for nothing when
a checkout, a `sed` pass or a lint autofix rewrites a closed file.

**Corrected a paragraph that had gone stale.** The key-order section said `key-order` "belongs in `.ansible-lint` `skip_list`" *if the noise is ever worth silencing* — that was done on 2026-08-27. The
rule had been firing **94 times across 42 role files**. Now records the skip as applied and scoped to the `[task]` subrule, with the consequence stated: `.ansible-lint` and `CONVENTIONS.md` are both
governance symlinks, so the convention and its enforcement are **operator-local** and a colleague cloning the repo gets neither.

**Also recorded:** the extension is a private fork (`amalikn.code-context-notes`), not the Marketplace build, and the publisher differs deliberately so VS Code cannot auto-update over it; storage is
`.code-context-notes/` and the MCP `--storage-dir` must match the extension setting; and the store has **no history and no file-level recovery** — verified, not assumed, by `git ls-files` returning
zero and no commit in the governance repo ever touching it.

Routing added to `RUNBOOK.md` and to the section list at the head of `08_ansible-authoring.md`, so the new content is reachable rather than only present.

## 20260825_1800 — Raspberry Pi capture group added to the broad collector (v0.1.23 -> v0.1.24)

Completes the collector added earlier the same day, which shipped the x86 set only. **164 captures now, across 18 groups.**

### Added

- `scripts/collect-smc-evidence-full.sh` — new **`rpi` group, 20 captures**, and real per-host platform gating rather than the previous
  "detect and warn" placeholder. The capture list is now filtered from the detected platform: `rpi` runs only on a Pi, and the four x86-only probes
  (`dmidecode` ×3, `smartctl`) are dropped there instead of filling the summary with absences that read like findings. `--only rpi` against an x86 host
  skips cleanly with a message.
- The group is built around the questions the Ubuntu 26.04 migration has to answer, so `--only rpi` across the fleet doubles as the phase-0 audit that
  `ansible-wifi.tasks.ubuntu-migration-open-items.20260821` asks for: EEPROM date against the 26.04 boot floor, boot-partition size against the
  three-asset-set requirement, `copymods` state, piboot layout presence, revision code for tryboot eligibility, plus throttling, SD health and zram.

### Verified live

Validated against **marta-marta-smc01** (`rct`) and **violet-valley-smc01** (`wh`), both Pi 4B Rev 1.5 / aarch64 / Ubuntu 22.04: all 20 rpi captures
return, **zero genuine failures** on either host, and the only non-ok results are the two correct pre-piboot absences (`autoboot-txt`, `piboot-units`).
x86 gating re-checked on yakanarra-smc01.

Two findings surfaced by the first run, both concrete migration input rather than tool output:

- **EEPROM on marta-marta is 2023-01-11**, comfortably past the 2022-11-25 floor, so that box clears the 26.04 boot prerequisite. Worth noting the
  report's `LATEST` (2022-01-25) is *older* than `CURRENT` — "up to date" there means "nothing newer in `/lib/firmware`", not "current with upstream".
- **`/boot/firmware` is 253 MB with 119 MB already used for a single asset set (47%).** 26.04 keeps up to three. Three sets do not fit in 253 MB, which
  makes the boot-partition item a measured blocker rather than a theoretical one.

### Learned

- **`life_time` / `pre_eol_info` do not exist on an SD-booted Pi 4** — they are eMMC attributes. `/sys/block/mmcblk0/device/` exposes `cid`, `csd`,
  `ssr`, `fwrev`, `manfid`, `oemid`, `serial`, `date` and no wear-level pair. The plan written the day before had specified those two files; the
  hardware disagreed, and the capture now reads what is actually there. Any guidance claiming to read SD wear-levelling from them on this hardware is
  wrong.
- Writing shell into a bash array from a generator script is an escaping trap: a double-escaped `$` produced `\\$a`, which expanded **locally** at
  array-definition time and tripped `set -u` with "a: unbound variable". Both offending captures were rewritten to use `head -n 1` with brace expansion
  and no shell variables at all, and the generator now asserts that no capture line contains a double-escaped `$`.

## 20260825_1745 — broad diagnostic collector added; narrow collector's interfacecheck path corrected (v0.1.22 -> v0.1.23)

Onboarding a new RCP site (yakanarra) needed a wider capture than the routing-focused collector provides, and running the existing one surfaced a
path bug in it.

### Added

- `scripts/collect-smc-evidence-full.sh` — broad read-only capture: **144 captures across 17 groups** (`identity os overlay storage services network
  dhcp dns firewall qos wifi voip portal monitoring rise access logs`), covering every subsystem in `references/02_service-map.md`. Complements rather
  than replaces `collect-smc-evidence.sh`, which stays narrow and stable because two analysers depend on its output contract.
  - **One SSH session per host.** The narrow collector opens a Teleport session per capture; at this scale that would be 144 sequential sessions. This
    builds a single remote script with `===SMC-CAPTURE===` delimiters and splits the stream locally. Measured 144 captures in ~25s against
    yakanarra-smc01 and umoona-smc01.
  - **Credential redaction on by default.** A broad capture reads service configs, and this fleet has no ansible-vault, so Teleport join tokens and
    SIP secrets would otherwise land on disk. The key is kept and the value replaced with `<REDACTED>`; `--no-redact` opts out. Pattern-based, so a
    sensible default and not a guarantee.
  - **Absences are classified, not lumped in with failures** — `absent (no such systemd unit)` / `(command not installed)` / `(no such file or
    directory)` vs a genuine `FAILED (rc=N)`. On a healthy box most non-zero rcs mean "not deployed on this flavour", which is the finding.
  - x86 capture set. Platform is detected per host; a Pi runs the platform-neutral groups and is reported as not-yet-implemented for the Pi-specific
    set rather than being probed with `dmidecode`/`smartctl`. The RPi capture list is specified in a comment block at the foot of the script.

### Fixed

- `scripts/collect-smc-evidence.sh` — the `interfacecheck` capture read `/usr/local/bin/interfacecheckv2.sh`. `smc_network` renders it to the
  **filesystem root** (`roles/smc_network/tasks/ubuntu.yml:346` -> `/interfacecheckv2.sh`). The capture had therefore been failing on **every site,
  silently, for the life of the script** — it reports `FAILED` in the manifest, which reads as a finding about the box rather than a bug in the tool.
  Verified absent at the old path and present at the new one on yakanarra, umoona and pandanus-park.

### Learned (live, 2026-08-25)

- **`systemctl status asterisk` reporting `active (exited)` is not proof Asterisk is running.** The unit is an LSB init wrapper, so systemd reports
  success once the script returns 0 whether or not a daemon survives. Confirmed on **umoona-smc01**: unit `active (exited)` since 09:41, **zero**
  asterisk processes, no `/var/run/asterisk/` control socket, every `asterisk -rx` query failing with "Unable to connect to remote asterisk". Note this
  is the same site whose 2026-08-19 CDR investigation concluded "handsets not in use" from an unchanged `Master.csv` — worth re-reading that conclusion
  against this, since a dead PBX and an unused one produce the same empty CDR file. Not chased in this session.
- Portal layout is not what a `application/config` glob assumes: `/var/www/` holds `kohana-base` (which uses `system/config`), `apn-mqtt-client` and
  `html`. The capture now lists `/var/www` and finds config dirs rather than guessing a path.
- **umoona-smc01 has no database server at all** — `mariadb`/`mysql` units not-found and zero `mariadb-server`/`mysql-server` packages installed. The
  capture now distinguishes "not running" from "not installed".
- `GROUPS` is a **bash special variable** (the current user's group IDs). Assigning to it in a script is silently ignored — it cost one debug cycle
  here, and any future script in this pack should avoid the name.

## 20260818_1350 — pre-push gate mechanics corrected, plaintext-secret exposure recorded (v0.1.21 -> v0.1.22)

Pushing the `rise` branch turned the pre-push hook into its own investigation, and it corrected guidance this pack had been giving.

### Changed

- `references/08_ansible-authoring.md` — **correction**: the Validation section previously advised putting
  `/Volumes/Data/_ai/_skills/skills-runtime/ansible-wifi/.venv/bin` on `PATH` when the hook fails. That venv is now known to be the *cause*, not the cure — it carries `ansible-core 2.17` with two
  collections and
  no `netaddr` against brew's 95, so it cannot resolve `selinux` (`ansible.posix`) at `roles/smc_system/tasks/main.yml:137` and fails the syntax-check stage for any push reaching that role,
  whatever you changed.
- Same file — new section documenting the gate's four stages and their differing semantics: only the ansible-lint stage has a baseline; yamllint has none and fails on any error in a touched file;
  syntax-check
  covers root-level playbooks only. Plus the properties that matter in practice — `line_is_changed` is evaluated **before** the baseline (so a baseline entry can never hide your own line), every
  finding in a new
  file blocks unconditionally, the baseline is `file|rule` keyed and lives in `.git/` so it is per-machine, the parser stores a finding's **column** as its rule when one is present, and the
  correct order of work
  is own-lines first, baseline second, whitespace last — getting that order wrong turned a 43-finding job into a 404-finding one.
- `references/13_known-issues.md` — new section on plaintext secrets in `group_vars` with no `ansible-vault` anywhere, and the `cw/group_vars/graylog.yml` copy that carried APN's cluster UUID, master
  `password_secret`, root password hash, three tokens and Teams webhook. Records the client/server asymmetry worth checking whenever a cluster is cloned: the client half had been adapted for
  communitywifi, the
  server half had not.

### Status

Repo side: `origin/rise` e1077c17 -> 213c0e4a (8 commits), governance repo main c6228ce -> 1f09cee. Detail in `ansible-wifi` `CHANGELOG.md` `20260818_1350`.

## 20260818_1300 — delye-smc01 RESOLVED; `overlay.size_ratio` proven inert; fleet percentages corrected (v0.1.20 -> v0.1.21)

Operator deployed `smc_rise_logcaps` to `delye-smc01` and re-enabled overlayroot. Verified on-box: reboot loop broken (1 h 18 min uptime, single boot), `laravel.log` 2.63 GiB -> **753 KB**, overlay at
15% used, latent log exposure down from ~85% of budget to **4%**, `rise-logcaps.timer` active, `rise-watchdog` running normally again now that `/media/root-ro` exists.

Verifying that deployment surfaced an error in this pack's own numbers. `df` reported a 3.9 GiB overlay where the documented budget was 3.05 GiB, which traced to **`overlay.size_ratio` being
completely
inert**: overlayroot 0.47ubuntu1 mounts the upper layer as `mount -t tmpfs tmpfs-root "${root_rw}"` with no `-o size`, and the only option keys it parses are `swap`, `recurse`, `debug`, `dir` and
`driver`. `size=40%` is parsed into an unused shell variable by a generic key/value parser that validates nothing, so it is discarded without error or warning. The real budget is always the kernel
tmpfs default of **50% of RAM** — measured 3.812 GiB on a 7.625 GiB box, exactly 50.0%.

### Changed

- `references/07_hardware-overlay.md` §8 — new subsection "`overlay.size_ratio` is inert" walking the five-step parse-and-discard path with the source lines; the ASCII structure diagram and the cost
  model's budget sentence corrected from "~40% RAM / ~3.05 GiB" to "always 50% of RAM / 3.81 GiB measured", with an explicit warning that earlier notes used the wrong denominator.
- `references/13_known-issues.md` — the `delye-smc01` entry retitled **RESOLVED** with a before/after verification table; its arithmetic corrected (laravel.log was **69%** of budget, not 86%); and the
  six-host fleet exposure table re-divided against the real budget (mimbi **32%** not 40%, hoppys-camp **15%** not 19%, etc.), with post-fix delye added at 4%.
- Repo side (`ansible-wifi`): `rise_logcap.py` now **measures** the budget via `statvfs` on the live tmpfs instead of computing `RAM x size_ratio` — verified to match `df` exactly on three hosts; the
  three RISE `group_vars` carry a block comment recording that `size_ratio` is inert so nobody tunes it expecting an effect.

### Note on the correction

The failure analysis is unchanged — only the denominator moved, and it moved in the safe direction (more headroom than assumed, not less). But every percentage published in `20260818_1130` and
`20260818_1200` was overstated by ~22%, which is why the tables were corrected in place rather than left standing with a footnote.

## 20260818_1200 — RISE metric delivery path: agent mode, remote_write allowlist, and the alerting void (v0.1.19 -> v0.1.20)

Follow-up to `20260818_1130`. Asking what the log-cap work should emit surfaced that **no `rise_*` metric was alerted on anywhere** — the central rule set carries 29 alerts and zero references to the
RISE surface, despite it having been emitted for over a year. `delye-smc01` reboot-looped with every relevant signal present on the box and nothing watching any of them. Three facts explain how that
was possible, and all three are now documented because each one is a trap for the next person.

### Changed

- `references/02_service-map.md` — new "RISE metric delivery" section recording that **Prometheus runs in agent mode on the SMC boxes** (no local TSDB, **no rule evaluation**, so
  `smc_prometheus/templates/rules.yml.j2` has never been evaluated and all SMC alerting must be central); that `remote_write` applies a **keep-allowlist** which silently drops anything unmatched
  (measured: 6.36M samples sent, 4.89M dropped, 0 failed); and that `node_textfile_mtime_seconds` survives that allowlist via `node_.*`, which is why the `Host*TextfileCollectorNotUpdated` pattern is
  the reliable dead-collector detector — and the only correct way to detect a dead `rise_watchdog`, whose own `rise_watchdog_unit_active` goes **stale rather than to 0** when it dies.
- Same file — full metric table for `rise_logcaps.prom`, marking `total_log_bytes` / `largest_file_bytes` / `overlay_budget_bytes` as **leading** indicators and `rise_overlay_used_pct` as **trailing**
  (it only moves after copy_up has already happened, by which point the host is looping).
- Same file — Graylog shipping for RISE confirmed live: `/var/log/rise/*.log` and `/opt/rise/status/*.json` are already tailed, so anything written under `rise_paths.log_dir` / `status_dir` ships with
  no config change. Plus the trap that `roles/smc_graylog/files/apn-fluentbit-config-file` is referenced by **no task in any role** — the live config is served by the Graylog server, so editing the
  repo file changes nothing on the fleet.

### Status

Repo-side changes (6 new central alert rules, 3 new leading-indicator metrics, `rise_.*` added to the remote_write allowlist) live in `ansible-wifi` `CHANGELOG.md` `20260818_1200`. Alert rules
validated
with `promtool check rules` on `black-hill-3-smc01` (rc=0). Central ingestion could not be verified end to end — the Grafana tunnel is refused and agent mode blocks querying the box's own TSDB —
so the
evidence is indirect: `samples_failed_total` 0 on a working `remote_write`, and the pre-existing `HostSbdm*` alerts depend on the same pipe and allowlist. Nothing deployed.

## 20260818_1130 — overlayroot copy_up cost model, `smc_rise_logcaps`, and three fleet-class findings (v0.1.18 → v0.1.19)

`delye-smc01` was reboot-looping every ~5 minutes. Root cause was a 2.63 GiB Laravel log with no logrotate stanza anywhere on the box, against a 3.05 GiB overlay budget. The generalisable lesson —
and the reason this warranted reference changes rather than just an issue note — is that **overlayroot copy_up charges a file's size at first write, not its write rate**, which inverts normal
disk-space intuition: a 2.6 GiB log appended at 4 KB/min is far more dangerous than a 10 MB log appended at 4 MB/min.

Verified at source (overlayroot 0.47ubuntu1) that `recurse=0` — already set fleet-wide — leaves every non-`/` fstab entry outside the overlay entirely, so moving volatile paths onto their own mount is
the permanent fix. That is deferred (no spare partition on most boxes); `roles/smc_rise_logcaps` is the interim mitigation, built on filesystem discovery rather than an enumerated path list.

Five classification bugs and two silent-failure modes were found by running read-only scans against six live production hosts rather than by reasoning — recorded because the method mattered more than
any individual bug.

### Changed

- `references/07_hardware-overlay.md` §8 — three new subsections: the copy_up cost model (including that **reading does not trigger copy_up**, which is what makes live fleet assessment safe);
  `recurse=0` verified at source with the actual shell snippet, plus why a loop-mounted image file cannot substitute for a real partition; and `smc_rise_logcaps`' five-bucket model with the mechanics
  that are easy to get wrong (`copytruncate` mandatory, `size` not `daily`, rsyslog not reopening on truncate, never truncating a `.gz`, `su root adm` not `su root root`).
- `references/13_known-issues.md` — four new sections: the `delye-smc01` reboot loop with triage notes; `rise-watchdog.service` failing `226/NAMESPACE` on any overlay-disabled or x86 host (fleet-class,
  previously undetected, scope still unmeasured); Ubuntu's stock rsyslog logrotate having no size limit, with measured `auth.log`/`syslog.1` sizes across three hosts and the harness warning about
  omitting `/etc/logrotate.conf`; and the legacy `ozai/hc.log` still writing post-RISE plus the graylog-sidecar logs that accumulate forever because they are already under any size threshold. Includes
  the six-host fleet log-exposure table (mimbi-smc01 at ~40% of its overlay budget).
- `references/05_troubleshooting.md` — new **Tier 8b: Box Reboot-Looping Every Few Minutes**, a six-step workflow whose first step is establishing that `rise_watchdog.py` reboots and
  `rise_healthcheck.py` never does.
- `references/02_service-map.md` — `rise_logcap.py` / `rise-logcaps.timer` registered with its outputs.
- `RUNBOOK.md`, `SKILL.md`, `manifest.json` — version 0.1.18 → 0.1.19; routing row added for reboot-loop triage.

### Status

The role and the watchdog fix are **written but deployed nowhere**. `delye-smc01` remains running with overlayroot disabled and unremediated. `nbn_wh` was not assessed (expired Teleport profile).
Repo-side detail lives in `ansible-wifi` `CHANGELOG.md` `20260818_1115` and memory-keeper keys `ansible-wifi.*.20260818`.

## 20260803_1825 — new-looma-smc01 second whole-host outage confirmed via live Prometheus (v0.1.17 → v0.1.18)

Operator reported "new-looma-smc01 is back online." Rather than take the status at face value, queried `mcp-grafana-apn` (already live from the previous session's Grafana work) for `up{instance=~"new-looma.*"}` over the last 7 days.

**Confirmed:** both the self-scrape (`job="prometheus"`) and `node_exporter` targets for `new-looma-smc01` went dark simultaneously from **2026-08-01 23:40 UTC to 2026-08-03 06:40 UTC (31h)**, then both resumed together — the signature of a whole-host/network outage, not a single failed service. A second, earlier 18h gap in the same window (2026-07-29 11:10 → 2026-07-30 05:10 UTC) lines up exactly with the already-documented topology cross-wiring fix (`08_ansible-authoring.md`), confirming that gap is already explained. This newer 31h gap is not — no `tsh ssh` access was used this session, so root cause is confirmed-timeline-only, not diagnosed.

### Changed

- `references/13_known-issues.md` — new paragraph appended to the existing "new-looma-smc01" section documenting the confirmed 31h outage, its whole-host signature, cross-reference to the already-explained earlier gap, and an open question about whether it relates to the still-open `my_node_network_device_info` zero-series gap (also new-looma-specific).
- `manifest.json` — new `diagnostics` entry (6th); version bumped 0.1.17 → 0.1.18.

### Evidence basis

Live `mcp-grafana-apn` `query_prometheus` reads this session (`up{instance=~"new-looma.*"}`, instant + 7-day range). Timestamps converted via direct `date -u -r <epoch>` — not estimated. No SSH/tsh access to the box itself this session.

## 20260803_1810 — Grafana CW exploration unblocked: dashboard inventory + RISE metric names (v0.1.16 → v0.1.17)

Operator supplied the missing NBN-instance service-account token and confirmed a session restart had happened, unblocking the `mcp-grafana-nbn` connection left stuck at the end of the previous session (blank-token 401, MCP process caching old env). Explored both flavor-specific Grafana instances rather than just confirming connectivity.

**Confirmed:** `mcp-grafana-apn` (20 dashboards) and `mcp-grafana-nbn` (9 dashboards) are not mirrors. The 11 APN-only dashboards include a RISE health/watchdog framework (RISE SMC Health Detail, RISE SMC Table, RISE Dashboard) that has no NBN counterpart because RISE is deployed only to `rct`/`wh` flavors — confirmed via the `flavor=~"rct|wh"` gate in the "Pending sites" panel query, not just dashboard absence. Pulled the actual Prometheus metric names behind the four `rise_*` textfile collectors that previously had `—` placeholders in `02_service-map.md` (`rise_healthcheck_health_score_*`, `rise_healthcheck_health_penalty*`, `rise_overlay_used_pct`/`_inodes_free_pct`/`_active`, `rise_zram_*`, `rise_watchdog_up`/`_active`/`_boot_firmware_used_pct`/`_unit_active`), plus the offline-vs-pending fleet-rollup logic (offline = watchdog seen in last 30d but not last 5m; pending = node_exporter up on rct/wh but watchdog series never existed).

### Changed

- `references/03_communication-flows.md` — new "Dashboard inventory" subsection under Grafana/Prometheus MCP Access: full table of the 11 APN-only dashboards with UIDs and purpose, plus the RISE-flavor-gate explanation for why they're absent from the NBN instance.
- `references/02_service-map.md` — Monitoring/Metrics textfile-collector table rows for the four `rise_*` scripts now note their systemd unit/flavor gate; new "RISE Health/Watchdog Framework" subsection with the full metric table and the offline/pending distinction.
- `manifest.json` — new `diagnostics` entry (5th) capturing the dashboard-inventory and RISE-metric findings; version bumped 0.1.16 → 0.1.17.

### Evidence basis

Live `mcp-grafana-apn`/`mcp-grafana-nbn` reads this session: `search_dashboards` (both instances), `get_dashboard_summary` and `get_dashboard_panel_queries` (RISE SMC Health Detail, RISE SMC Table, Sites not reporting, SMC Table, Data Backlog, RPi SD Card Status). RPi hardware detail cross-checked against already-confirmed `07_hardware-overlay.md` content — no new hardware facts, dashboard is a visualization of already-documented state.

## 20260803_1745 — ClamAV freshclam root cause confirmed: ClamAV 0.103.x end-of-life (v0.1.15 → v0.1.16)

Operator asked "what could be the reason for the ClamAV error" following the fleet sweep in the previous entry. Rather than restate the open hypotheses, verified via `WebSearch` against clamav.net and the Cisco-Talos/clamav GitHub issue tracker before answering.

**Confirmed root cause**: ClamAV's 0.103 branch reached end-of-life for database updates on 2025-09-14. This fleet runs `clamav 0.103.11`/`.12` uniformly, squarely in the EOL'd branch — after the cutoff, ClamAV's CDN actively rejects `freshclam` from any 0.103.x client with HTTP 403 ("Forbidden; Blocked by CDN"), exactly the signature captured on all 26 hosts. This also explains the 10-month staggered failure-date spread from the previous entry: each host only flips to `failed` the first time its `freshclam` timer runs *after* the cutoff, so hosts with different timer schedules trip it at different times rather than all at once. Not a cw-cluster-specific network/firewall issue — this is documented, expected upstream behavior for any fleet still on 0.103.x. Fix is a version upgrade (1.0 or 1.4 LTS), not a retry; no automated ClamAV-version-update pipeline exists for this cluster to do that automatically.

### Changed

- `references/13_known-issues.md` — ClamAV bug row rewritten from "root cause not investigated, 3 open hypotheses" to "root cause confirmed," with the EOL date, the CDN-block mechanism, and the staggered-date explanation; "Fix location" column updated from "not investigated" to the concrete upgrade path.
- `references/08_ansible-authoring.md`, `references/01_overview.md` — ClamAV/Lynis rows updated to reference the confirmed root cause instead of open hypotheses.
- `manifest.json` — new `diagnostics` entry (3rd) capturing the confirmed root cause with its sources; version bumped 0.1.15 → 0.1.16.

### Evidence basis

`WebSearch` against `blog.clamav.net` (the official EOL announcement) and `github.com/Cisco-Talos/clamav` issue tracker (multiple community reports of the identical error signature) — external, citable sources, not inferred from this fleet's data alone. Cross-checked against this session's own captured data (uniform 0.103.x package version, exit code 17, exact error text match) for internal consistency.

## 20260803_1730 — Full NBN Accelerate fleet sweep: 28 hosts, hardware inventory, fleet-wide ClamAV finding (v0.1.14 → v0.1.15)

Operator requested a thorough analysis of "all the NBN Accelerate sites" including hardware details and the state of installed apps/scripts/services — a full fleet sweep, not a spot-check, superseding the 2-host check in the previous entry. Built two new reusable tools (`scripts/collect-fleet-health.sh`, `scripts/fleet-health.justfile`) and ran them against all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh` hosts (28 total).

**Hardware inventory (new — no prior live chassis data existed for this cluster):** 11× AAEON BOXER-6641 (i5-8500T, 15Gi RAM, Transcend SSD) + 15× AAEON BOXER-6404 (Celeron J1900, 7.7Gi RAM, Innodisk CFast) for `nbn_accelerate`; both `nbn_wh` hosts are genuine Raspberry Pi-class (Cortex-A72, Swissbit microSD) — operator confirmed `nbn_wh` is the `wh`-flavor equivalent on this cluster.

**Major finding: `clamav-freshclam` confirmed failed fleet-wide, 26/26 `nbn_accelerate` hosts** (not the 2 found in the earlier spot-check) — same CDN-blocked exit-17 signature on every host, but failure *dates* span 10 continuous months (2025-10-02 → 2026-07-30), indicating an ongoing degradation still actively catching hosts, not a single past incident.

**Resolved during write-up (operator-confirmed mid-session):** `nbn_wh` overlayroot is not yet active on either host — this is a planned-but-not-yet-executed rollout (`smc_rise_deploy.yml` already targets `nbn_wh`), not a bug or stalled deployment.

**Other findings:** kernel-version drift (5.15.0-79 to 5.15.0-133) corroborating the earlier no-automated-kernel-pipeline structural finding; `koonibba-smc01` at 95% disk usage with the fleet's oldest kernel; `isc-dhcp-server6` failed on 28/28 hosts (confirmed benign — IPv6 disabled by policy); `fwupd-refresh` failed on 3/28 hosts (minor); `nbn_wh` swap/zram absence contradicting the platform table's universal RPi-zram claim (unresolved).

### Added

- `scripts/collect-fleet-health.sh` — new reusable, flavor-agnostic hardware/security/service-health evidence-capture script (read-only, hardcoded command bundles, same safety contract as `collect-smc-evidence.sh`). Bundles ~20 commands into 4 grouped captures per host to stay tractable over satellite links at fleet scale.
- `scripts/fleet-health.justfile` — task-runner wrapping the script, ships with the current NBN Accelerate site list plus `freshclam-check`/`failed-units-check`/`chassis-models` quick-check recipes. Dogfooded after writing — found and fixed 2 real bugs (a `just`-working-directory path assumption, and the same exit-code-of-last-command quirk documented in the collection script) before trusting it.
- `scripts/README.md` — new safety-classification rows, "What each script is for" section, and a documented lesson on `just -f <path>`'s working-directory behavior.
- `references/07_hardware-overlay.md` — new "NBN Accelerate / NBN WH Hardware Inventory" section with the full chassis/CPU/RAM/storage/kernel table and all findings above.
- `references/13_known-issues.md` — "Known Operational Bugs (NBN Accelerate cluster)" section rewritten for the full 28-host sweep (was 2-host); coverage-gap row updated to "largely closed."
- `references/01_overview.md`, `references/08_ansible-authoring.md` — evidence-basis and flavor-gate rows updated to reflect full-fleet validation.
- `references/04_dependency-tree.md` — separately, added `smc_ltp`/ClamAV/Lynis Level-4 entries and flagged a naming-collision risk between `smc_ltp`'s CNMaestro provisioning and a pre-existing generic `cnmaestro-provisioning`/`redis` dependency row (unresolved — may be the same mechanism described two ways, or two genuinely separate paths).
- `manifest.json` — new `diagnostics` entry for the full sweep; version bumped 0.1.14 → 0.1.15.

### Operational note

Raw per-host evidence relocated from `skill-smc/evidence/` to `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` per this pack's evidence-retention policy — skill-smc holds analysis and tooling, not case-specific raw captures.

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands, this session, 28/28 targeted hosts. Two-batch capture: batch 1 crashed at 11/28 hosts after a same-session edit to the running script file corrupted its execution (a documented gotcha now — never edit a script file while it's still running); batch 2 recaptured the remainder with the fixed script. Not covered: `cw` flavor (central-infra only), `aurukun-smc03` (unreachable at capture time).

## 20260803_1615 — First live NBN Accelerate validation: confirms cluster comparison, finds ClamAV CDN-block (v0.1.13 → v0.1.14)

Operator made `tsh login` available for the NBN Accelerate cluster (`teleport.communitywifi.net.au`) and invited exploratory commands — the first-ever live access this pack has had to that cluster, closing (partially) the "code-inspection-only" caveat that's sat on every NBN Accelerate claim since the gap-fill earlier today. Ran read-only diagnostic commands against two `nbn_accelerate` hosts, `warakurna-smc01` and `indulkana-smc01`.

**Every prior code-inspection-only claim checked came back confirmed, 2/2 hosts:** Teleport domain (`teleport.communitywifi.net.au:443`), HTTPS-only portal (permanent HTTP→HTTPS redirect, on-box TLS termination at `/etc/ssl/communitywifi.net.au/`), `wifi-community-app-backend` present, ClamAV + Lynis both installed, Asterisk absent, DNS stack is standard unbound+stubby (not `smc_ltp`/bind9, as expected — neither host is an `smc_ltp` member).

**New finding, not previously known:** `clamav-freshclam.service` has been failing on both hosts — `warakurna-smc01` since 2026-07-23, `indulkana-smc01` since 2026-06-21 — identical signature (exit code 17, `Forbidden; Blocked by CDN`, freshclam gives up permanently rather than retrying). ClamAV's virus database is stale/frozen on both; the daemon itself stays active but with degraded detection. Root cause not investigated (read-only session, no remediation attempted).

### Added / Changed

- `references/13_known-issues.md` — new "Known Operational Bugs (NBN Accelerate cluster — first live check, 2026-08-03)" section with the confirmed-claims summary and the ClamAV/freshclam bug row; "NBN Accelerate cluster coverage gap" row updated from "not live-validated" to "first live spot-check done."
- `references/08_ansible-authoring.md` — ClamAV+Lynis gate row updated with the live-confirmed install + the freshclam finding.
- `references/01_overview.md` — evidence-basis paragraph updated: partially live-validated as of 2026-08-03; `nbn_wh`/`cw` flavors still unvalidated.
- `manifest.json` — new `diagnostics` entry (first use of this previously-empty field) capturing the live-validation results and the ClamAV finding; version bumped 0.1.13 → 0.1.14.

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands against `warakurna-smc01` and `indulkana-smc01`, this session. No writes/remediation performed. `nbn_wh` and `cw` flavors, and every other NBN Accelerate site, remain unvalidated — this is a 2-host spot-check, not a fleet sweep.

## 20260803_1545 — project-coherence sweep: routing/architecture staleness fixed (v0.1.12 → v0.1.13)

`project-coherence` run covering today's cumulative changes (NBN Accelerate gap-fill through the smc_ltp manual-mechanism confirmation). Content files (Tier 1) were already coherent — this pass caught two Tier 2/routing staleness items that hadn't been touched during the piecemeal content edits:

### Changed

- `context-map.yaml` — `ansible_authoring` and `smcbox_basics` routing descriptions extended to mention `smc_ltp`/"low touch" onboarding and the APN-vs-NBN-Accelerate comparison respectively; previously only the underlying reference files had been updated, not this machine-readable routing layer.
- `ARCHITECTURE.md` — governance-pack size figure corrected from a stale "~125k chars" (last accurate 2026-06-26) to the current ~470k chars / 35 files — had drifted across multiple sessions' worth of content growth, not just today's.
- `RUNBOOK.md`, `AI_NAVIGATION.md` — `08_ansible-authoring.md` routing rows extended to mention `smc_ltp` and onboarding history, matching the pattern already applied to the `01_overview.md` row for NBN Accelerate.

### Validated

Stale-reference grep across the whole pack for old figures/phrases ("cnMaestro mDNS", "only rcp/guda-guda", "Community WiFi cluster", "~125k chars") — all remaining hits are correctly-framed historical/correction narrative in `CHANGELOG.md`/`SCRATCHPAD.md`/the "corrected 2026-08-03" notes, no live incorrect claims found. `README.md`, `SYSTEM_PROMPT.md` reviewed — generic pointers, no stale figures. `.remember/today-2026-08-03.md` reviewed — out of scope for this pack's own coherence pass (self-managed by the global `remember` skill, not a skill-smc-authored file).

Version bumped 0.1.12 → 0.1.13; governance pack regenerated.

## 20260803_1530 — smc_ltp/"low touch" mechanism confirmed: manual step, no enforcement (v0.1.11 → v0.1.12)

Final piece of the smc_ltp/"low touch" thread, same day: operator confirmed the one remaining open question — whether low-touch onboarding tooling itself assigns `smc_ltp` group membership, or it's a manual step. **It's manual.** No tooling automatically adds a new low-touch site to `smc_ltp:children`, and nothing checks or enforces that it happened. This directly explains the root cause of the 3-site gap fixed in the previous entry — a manual, unenforced step is exactly the kind of thing that silently drops during a busy onboarding.

### Changed

- `references/08_ansible-authoring.md` — "smc_ltp Sub-Group" low-touch resolution paragraph updated with the confirmed mechanism and an explicit operational implication: verify `smc_ltp:children` membership explicitly for any future low-touch site rather than assuming it's automatic.
- `references/13_known-issues.md` — the "low touch ↔ `smc_ltp` link" row's status upgraded to include "mechanism confirmed manual"; reframed as a standing risk for future low-touch sites, not a one-off closed by this correction.
- `manifest.json` — `smc_ltp`/low-touch `stable_facts` entry updated with the confirmed mechanism; confidence raised to 0.92; version bumped 0.1.11 → 0.1.12.

### Evidence basis

Operator-confirmed directly, relayed to this session. No independent verification possible from Ansible source alone (absence of automation is what's being confirmed, not a positive code finding).

## 20260803_1515 — smc_ltp/"low touch" correlation resolved: 3 sites added to the group, 7 members confirmed (v0.1.10 → v0.1.11)

Follow-up to the "low touch" onboarding entry below, same day. That entry flagged, but did not conclude, whether "low touch" onboarding and `smc_ltp` membership were mechanistically linked (4 of 7 low-touch sites were `smc_ltp` members; 3 — `umoona`/`warburton`/`beagle-bay` — were not). Operator confirmed the link is real: every low-touch site is meant to be an `smc_ltp` member, and the 3 missing ones were a plain inventory gap, not a coincidental overlap of two unrelated rollout decisions.

Operator made and verified the fix directly in `ansible-wifi`: added `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` host groups to `inventories/rcp/prod`, plus each site's own `:children` block, matching the existing pattern for the other 4 sites. Verified via `ansible-inventory --list` (all 7 now under `smc_ltp:children`) and `ansible-playbook --syntax-check smc_ltp.yml` (clean). **Uncommitted** — a real production Ansible inventory change, not yet run against any live SMC.

### Changed

- `references/08_ansible-authoring.md` — "smc_ltp Sub-Group" section updated: membership is now 7 sites, not 4; the site/date table's `smc_ltp member?` column updated; the low-touch section's "flagged, not concluded" framing replaced with "Resolved 2026-08-03 (link confirmed, not coincidental)" and the fix/verification steps documented. The underlying *mechanism* (does low-touch tooling itself assign `smc_ltp` membership, or is it manual) remains unestablished — only the intended end-state membership is now confirmed.
- `references/02_service-map.md`, `references/13_known-issues.md` — DNS resolver row and coverage-gap row updated to 7 sites and "resolved" status.
- `references/01_overview.md`, `SKILL.md`, `references/05_troubleshooting.md` — quick-reference/table mentions of `smc_ltp` membership updated from 4 to 7 sites.
- `manifest.json` — both `smc_ltp`-related `stable_facts` entries updated to reflect 7 members and the resolved correlation; version bumped 0.1.10 → 0.1.11.

### Evidence basis

Operator-directed and operator-verified (`ansible-inventory --list`, `ansible-playbook --syntax-check`) file-level change relayed to this session; not independently re-verified by this session, and not yet run against any live SMC or committed to the ansible-wifi repo.

## 20260803_1445 — "Low touch" onboarding method and site deployment history added (v0.1.9 → v0.1.10)

Operator supplied install dates for a cohort of `rcp` sites, confirming a named **"low touch" onboarding method**: `guda-guda` (pilot, 2025-04-15), then a year later `umoona` (2026-04-12), `warburton`, `beagle-bay`, `pandanus-park`, `old-looma`, `new-looma`. Genuinely new information not previously documented anywhere in this pack.

### Added

- `references/08_ansible-authoring.md` — new "'Low Touch' Onboarding Method and Site Deployment History" section (added to Contents list): the full site/date/`smc_ltp`-membership table; the flagged-not-concluded observation that all 4 `smc_ltp` sites are also low-touch sites (3 of 4 `smc_ltp` non-pilot members plus the pilot itself), while `umoona`/`warburton`/`beagle-bay` are low-touch without `smc_ltp`; and a direct-grep finding that "low touch" currently has no Ansible-code representation — the one `low_touch`-named var in the repo (`smc_bases_low_touch_provisioning` on `pierre-rcp01`, not a cohort member) is set but never read by any role or playbook.
- `references/13_known-issues.md` — new open-question row capturing the unresolved `smc_ltp`/low-touch correlation; updated the pre-existing "cnmaestro-provisioning internals" coverage-gap row to reflect that the deployment side is now well-documented (only the CNMaestro API's own runtime behavior remains unknown).
- `manifest.json` — new `stable_facts` entry for the low-touch cohort/dates and the orphaned-var finding; version bumped 0.1.9 → 0.1.10.

### Evidence basis

Site list and dates are operator-provided, cross-referenced against independently-observed netplan/hook render timestamps already in this pack's routing-issue-derived content (consistent, not contradictory — renders land 1-92 days after each stated install date, matching later unrelated remediation work touching those files). The `smc_ltp` overlap and the orphaned `smc_bases_low_touch_provisioning` var are this session's own repo-wide grep findings. Not live-validated against any site.

## 20260803_1400 — smc_ltp properly explored and documented; membership undercount fixed (v0.1.8 → v0.1.9)

Operator flagged that `smc_ltp` "has not been explored and documented properly" — a fair call. Prior coverage was a side effect of the 2026-07-03 DNS RCA (which only established that `smc_ltp` gates the unbound-vs-bind DNS split) and had never been independently re-verified since. Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, and `roles/smc_dns_mgmt/tasks/main.yml` (this session, cross-checked against a parallel same-day pass done from the ansible-wifi side, which reached the same conclusions independently) found two things wrong with the prior documentation:

1. **Membership undercount.** Every prior mention said "currently only `rcp`/guda-guda". That was based on a `.yml`-scoped grep that missed `inventories/rcp/prod` — an INI-format static inventory file, not a `topology_vars`-generated one. The group actually has 4 members: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`.
2. **Purpose mislabeled.** Prior docs called it "cnMaestro mDNS" — wrong on both halves. It has two unrelated purposes, neither of which is mDNS: (1) a separate `smc_ltp.yml` playbook runs CNMaestro-managed Cambium ePMP/cnPilot wireless-backhaul provisioning (auto-allocates management IPs, SSIDs, per-model config for cnPilot/XV2/ePMP Force/ePMP 3000L hardware); (2) `smc_bases.yml`'s `dns_mgmt` play switches the DNS resolver stack from unbound+stubby to bind9+RPZ (zone file literally named `db.cambium-rpz`, tying the DNS switch to the same Cambium backhaul context).

### Added / Fixed

- `references/08_ansible-authoring.md` — new "smc_ltp Sub-Group — CNMaestro Backhaul Provisioning + DNS Architecture Switch" section: membership mechanism (static INI group, not topology_vars), both purposes in full, the `smc_dhcpd` LTP-specific apparmor/service-user fix, and an explicit "LTP acronym not expanded anywhere in the codebase — do not guess" note. Added to the Contents list.
- `references/01_overview.md`, `references/02_service-map.md`, `references/13_known-issues.md` — corrected the "only `rcp`/guda-guda" undercount to the 4-site list and cross-referenced the new 08_ansible-authoring.md section instead of restating it.
- `SKILL.md` Tier 3 DNS quick-reference and `references/05_troubleshooting.md` Tier 3b/3c — same undercount fixed; Tier 3c now notes the CNMaestro-provisioning angle so a "DNS is fine but backhaul radios aren't provisioning" report on one of these 4 sites doesn't get misdiagnosed as a DNS issue.
- `manifest.json` — new `stable_facts` entry capturing the corrected membership, dual purpose, and the open "LTP acronym" question; version bumped 0.1.8 → 0.1.9.

### Evidence basis

Direct read of the playbook/role/inventory files listed above (this session). Not live-validated against any of the 4 member hosts via `tsh ssh` — the CNMaestro-provisioning and DNS-switch mechanisms are confirmed from Ansible source, not from a live box.

## 20260803_1230 — NBN Accelerate cluster gap-fill (v0.1.7 → v0.1.8)

Operator request: ~95% of this pack's operational detail was extracted from APN-cluster (`rcp`/`rct`/`wh`, `teleport.apn.au`) work; the NBN Accelerate cluster (`cw`/`nbn_accelerate`/`nbn_wh`,
`teleport.communitywifi.net.au`) had only the flavor→domain mapping documented (from the 2026-07-31 SSH/Teleport corrections). Ran a three-pronged research sweep (inventory group_vars diff across
all 7 flavors, repo-wide grep for flavor-conditional branching in roles/templates, doc/ADR/OPA search in local-knowledge-ansible/ansible-wifi) to fill the gap with a structured comparison rather
than assuming parity between the two clusters.

### Added

- `references/01_overview.md` — new "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" section: both clusters share a 1-central-infra + N-site-fleet topology, but NBN Accelerate is
  materially thinner (no graylog/opensearch, no kernel-update Jenkins pipeline) and has real functional differences beyond the SSH endpoint (mobile-app backend + kiosk mode on `nbn_accelerate`
  only, HTTPS-only portal protocol, different blocked-URL redirect domain, ClamAV+Lynis hardening on `nbn_accelerate` only, VoIP/Asterisk on `rcp` only). Documents the selector mechanism
  (`hotspot_flavor` hardware-class split spans both clusters; `inventory_dir.split('/')|last` drives flavor-exclusive gates; nothing branches on the literal strings cw/community/communitywifi).
- `references/08_ansible-authoring.md` — new "Flavor/Cluster Conditional Branching (Selector Reference)" section: table of confirmed flavor-exclusive role gates (ClamAV/Lynis, VoIP/Asterisk,
  `smc_qos`, `smc_ltp`) with their exact conditions, plus the `smc_autossh` Teleport-endpoint selection mechanism (`teleport_fqdn` per-inventory group_var, host_var overrides for staging domains).
- `references/10_captive-portal.md` — new §11.9: `smc_bases_portal_protocol` (http vs https) and `smc_bases_blocked_url_redirect` differences between clusters, flagged explicitly as
  code-inspection-only (not live-validated against a cw-cluster host), with implications for §11.1–11.8's APN-cluster-derived verification commands.
- `references/13_known-issues.md` — new "NBN Accelerate cluster coverage gap" row (Knowledge Gaps table) stating the live-validation boundary explicitly; two new Skill Staleness Risks entries: a
  "community wifi" naming-collision warning (used generically for `rcp` sites in `issues/apn/routing-issue/`, distinct from the cw-flavor customer — a false-positive risk for future greps), and an
  OPA `flavors.json`/`environments.json` coverage note (no `cw`/`apn`/`rct`/`wh` entries — not established whether intentional).
- `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md` — `01_overview.md` routing rows updated to mention the new APN vs NBN Accelerate comparison content.

### Evidence basis

Structural findings: direct read of all 7 inventories' `group_vars/*.yml` and `prod` files. Behavioral findings: repo-wide grep across `roles/*/tasks/main.yml`, `roles/*/templates/*.j2`,
`smc_bases.yml`. Doc/ADR/OPA findings: search of `local-knowledge-ansible/ansible-wifi/{.archcore,issues,opa,docs,.remember}`. None of this is live-validated against a running `nbn_accelerate`/
`nbn_wh`/`cw` host — flagged as such in every new section rather than presented as fleet-confirmed fact, consistent with this pack's existing evidence-labeling convention.

## 20260731_1312 — Fed back Pia Wadjari labeling case + proposed convention; multiwan-disable git archaeology

Operator worked in `local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/` on internet-link topics (dual-switch bonding, label/metadata convention, manual ingress shaping, dormant
multi-WAN VRF/fwmark), initially without checking here first — that workspace's own governance now flags this happened and corrects the resulting mechanism mis-citations. Two genuinely new pieces
of information from that session, not previously here, fed back per operator request:

### Added

- `references/03_communication-flows.md` — under the existing label-inversion note: Pia Wadjari as a second confirmed instance (Starlink active/`internet` label, SkyMuster Plus backup/`starlink`
  label — inverse of Horn Island), agreed with the operator's colleague Sandro that deployment proceeds as scheduled, and the concrete retrofit proposal (role-based `active-internet`/
  `standby-internet` labels + `provider:`/`link_type:` metadata fields) with a rough 2-3 week timeline once agreed — the existing note only said a retrofit was "planned" with no detail on what it
  would look like.
- `references/03_communication-flows.md` — under the existing multiwan/VRF note: the specific disable commit (`c19a61fa`, apparent incidental collateral of an unrelated URL-capture refactor, not a
  deliberate decision) and an important nuance the existing note didn't have — the fwmark script being dead does not mean VRF is fully out of play; `netplan.yml.j2`'s per-WAN VRF *allocation* is
  still live and rendered into every deploy today, only the fwmark `ip rule`s that would use those tables are missing. Flagged as an open, not-yet-checked question whether any live SMC carries
  orphaned `vrf-<tableid>` devices as a result.

### Not added (already covered, verified during this pass)

- Topic 1 (dual-switch bonding design) — already fully promoted into `references/08_ansible-authoring.md`, correctly citing the source workspace's own analysis doc. No gap found.
- Topic 3 (manual ingress-shaping script) — already fully documented (`references/03_communication-flows.md`, `13_known-issues.md`), established 2026-07-29. The source workspace had independently
  rediscovered this and initially mis-described it as "unknown" — corrected there after this check, not here (nothing here was stale).
- The core label-inversion mechanism and the `dhclient-enter-hooks.j2` override itself — already accurate and complete here; it was the *source workspace's* citation of `ubuntu-dhclient-script.j2`
  that was wrong, not anything in this file.

## 20260731_1215 — Two residual gaps closed from the routing-issue Problem 3 deep-dive

Operator asked, from the routing-issue investigation folder, "was all the information in this project fed back to skill-smc?" — a spot-check after the 20260731_1245 full extraction pass (below,
despite the out-of-order stamp — see the note on CHANGELOG stamps not matching wall-clock order) and the earlier 20260729_2324 pass. Both were thorough; this check found the coverage was
otherwise complete, with two specific, narrow gaps in the Problem 3 (starlink `INPUT` DROP) deep-dive.

### Added

- `references/03_communication-flows.md` — the DHCP-bypasses-netfilter-`INPUT` mechanism: ISC `dhclient` uses a raw `AF_PACKET` socket for its own port-68 traffic, tapping frames at the link
  layer before/parallel to `NF_INET_LOCAL_IN`, for both the initial lease and later renewals — this is *why* the starlink DROP rule (already documented) never blocks DHCP, and generalizes to any
  interface-scoped DROP/REJECT rule on this fleet. Live-confirmed on Warburton.
- `references/13_known-issues.md` — new Known Site Issues row: warburton-smc01's unexplained 1.68M-packet/3.3GB starlink DROP-rule counter (live tcpdump ruled out self-generated traffic and
  public-internet exposure; source remains unresolved).

## 20260731_1330 — Broadened cross-repo feed-back governance (prevent future full-sweep need)

Follow-up to the 20260731_1245 extraction pass: the operator asked that ansible-wifi and
local-knowledge-ansible/ansible-wifi (current and future subfolders) always consult skill-smc and
always feed new knowledge back via `skill-slurp-chat`/`project-coherence`, so this kind of exhaustive
sweep never has to happen again.

### Changed

- `AGENTS.md` "Cross-repo trigger rule" — broadened scope from "when triggered from ansible-wifi"
  to explicitly cover the whole `local-knowledge-ansible/ansible-wifi` tree (current and future
  subfolders, via the existing `@`-import convention those subfolders already use). Broadened the
  trigger-condition list beyond "fixes, architecture decisions, failure modes" to explicitly include
  unimplemented design recommendations, ADRs/rules/specs, OPA policy changes, reusable scripts, and
  ROADMAP decisions. Named `skill-slurp-chat` as an equally mandatory trigger point alongside
  `project-coherence` (previously only the latter was named). Added a closeout self-check.

### Corresponding changes in ansible-wifi's own governance (not this pack, but the other half of the loop)

- `ansible-wifi-root-governance/AGENTS.md` (symlinked as `/Volumes/Data/_ansible/ansible-wifi/AGENTS.md` — a single edit covers both), `.archcore/rule-002`, `.agents/task-patterns.md`, and
  `.agents/validation.md` were broadened identically, and rule-002 was renamed to drop the
  "incident/debug fixes" framing that had been the actual root cause of the extraction-pass gaps.
  See that repo's own `CHANGELOG.md` entry `20260731_1330` for detail.

## 20260731_1245 — Full local-knowledge-ansible/ansible-wifi extraction pass

Operator asked for an exhaustive sweep of every markdown file under
`local-knowledge-ansible/ansible-wifi/` and subfolders to confirm nothing was missed. Covered
directly: `ai-tooling/`, `opa/`, `plans/`, `scripts/` (top-level lint scripts), `history/`,
`graphify-out/GRAPH_REPORT.md`, `issues/garimba-smc01/`, `issues/amata-smc01/`,
`issues/rcp-fleet/`, `issues/internet-link-handling/`, and the `ansible-wifi-root-governance/`
top-level docs (ROADMAP.md, CONVENTIONS.md, `.serena/memories/`). Delegated to subagents:
`ansible-wifi-root-governance/.archcore/` (6 ADRs, 5 rules, 1 guide, 2 specs) and
`issues/apn/routing-issue/docs/` (20 files) against current pack content; a third background sweep
covered `.remember/` daily logs for anything that fell through the ADR-promotion workflow.
`snapshots/` (59 timestamped dirs) and `history/current/` confirmed to be point-in-time copies of
the ansible-wifi repo's own AGENTS.md, not distinct knowledge — spot-checked via diff, not deep-read.

### Added

- `references/06_failure-modes.md` — amata-smc01 disk-path failure (ATA/COMRESET, `DID_BAD_TARGET`,
  forced read-only root) as a new failure-mode entry, flagged still-open per ROADMAP.md.
- `references/07_hardware-overlay.md` — `smc_disk_failover` role mechanism (EFI BootNext on
  connectivity failure, not storage-health failure; not guaranteed to run cleanly under active I/O
  corruption).
- `references/13_known-issues.md` — amata-smc01 open-incident row; `smc_qos` misgated to `rct`-only
  (silently no-ops on rcp/nbn_accelerate); Horn Island's unconditional `starlink01`/`starlink02`
  topology block; Pandanus Park chronic `interfacecheckv2.sh` restart loop; Old Looma `smc_iptables`
  ACL drift (Asterisk/MQTT/Cambium-TFTP rules missing); mercedes-cove null-property portal bug;
  duplicate `[horn-island_smc_bases]` inventory declaration; bungardi-smc01 multi-incident cluster
  (hostapd driver hang masquerading as apt lock contention, nl80211 netlink wedge, Teleport
  cert/reverse-tunnel issues, WAN-level eth0 flakiness); an unreconciled-duplicate-fix flag for two
  differently-described apt-daily-upgrade fixes that may or may not be the same change.
- `references/08_ansible-authoring.md` — OPA policy layer overview (packages, `opa eval`/`opa
  test`/`conftest` usage, ADR-001's env-gate-before-flavor-gate precedence); a design recommendation
  for bonding (not bridging) doubled RCP/NBN-Accelerate internet circuits (`mode=active-backup`,
  ARP-based monitoring, systemd-networkd VLAN-as-bond-slave race-bug risk); a third topology_vars
  authoring-bug class (role mistagging, confirmed at rocket-bore-smc01, alongside the existing
  vlanid-cloning and physical-interface-naming bugs); the SSH cipher-negotiation fix's correct home
  (`smc_sshd`'s `ssh_config` template, not per-script patches); a guardrailed single-site
  interface-key rename pattern (pia-wadjari) with the two preconditions that make it safe to reuse.
- `references/12_content-filtering.md` — SPEC-002's bridge_500-unconditional-ACCEPT fact as an
  explicit differential-diagnosis note ("VLAN 500 works, 501 doesn't" = by design, not a fault).
- `references/03_communication-flows.md` — corrected the stale "`smc_qos` planned, not started"
  claim (the role exists, is just misgated) with the per-site missing-shaping data; two
  generalizable WAN-path diagnostic techniques (RX=0 rules out firewall causes; sibling-VLAN
  isolation test) from the dark-VLAN Starlink-backup investigation.
- `references/05_troubleshooting.md` / `06_failure-modes.md` — noted the `custom_apt_install.yml`
  "invalid loop data" fix was superseded by a wholesale file replacement, not the originally
  documented in-place patch.
- **`scripts/lint-baseline-refresh.sh` + `scripts/ansible-lint-delta-gate.sh`** — promoted and
  genericized from `local-knowledge-ansible/ansible-wifi/scripts/`. Config path is now
  repo-root-relative (`ANSIBLE_LINT_CONFIG` override) instead of two hardcoded paths that disagreed
  with each other (`local-knowledge/` vs `local-knowledge-ansible/`). See `scripts/README.md`
  (retitled to cover both the WAN-routing and lint-gate script categories).

### Corrected (post-pass, operator-flagged, two rounds)

- `install.md` + `adapter.md` — first correction round stated SMC access "must go through `tsh ssh`
  via the `ssh-manager` MCP." **Also wrong** — no `ssh-manager` (or any SSH-wrapping) MCP is used at
  all; access is a direct `tsh ssh root@<hostname>` shell command, no MCP involved. Rewrote both to
  remove the MCP framing entirely: a plain "Live SSH access — direct `tsh ssh`, no MCP" section, and
  `mcp-grafana` as the only MCP left in the execution layer. Fixed the stale `ssh_list_servers`/
  `ssh_execute` verification steps to a direct `tsh ssh` check.
- `references/01_overview.md` "Remote Access" + `references/13_known-issues.md` — the Teleport
  cluster domain was previously assumed single-value fleet-wide (`teleport.apn.au`). Operator
  confirmed the actual split: `rcp`/`rct`/`wh`/`apn` → `teleport.apn.au`;
  `nbn_accelerate`/`nbn_wh`/`cw` → `teleport.communitywifi.net.au` (all 7 flavors covered). Added
  this mapping table to `01_overview.md`, `install.md`, and closed the coverage-gap row in
  `13_known-issues.md` that had briefly flagged it as unresolved.

### Not promoted (reviewed, judged not durable/in-scope)

- `ai-tooling/*.md` — meta design-rationale docs for skill-smc itself (already implemented, matches
  current pack state); not operational SMC knowledge.
- `plans/20260317_1656_interface-id-rename-plan.md` — historical, fully superseded by the
  guardrailed-rename pattern now captured in `08_ansible-authoring.md`.
- `graphify-out/` — mostly vendored-Ansible-collection graph noise; the one durable pointer
  (overlayroot-persistence roadmap item) was already covered by existing Tier 8 content.
- `snapshots/`, `history/` (except the one url-capture-v2 migration doc, already captured
  pre-session) — point-in-time governance-file backups, not distinct knowledge.

## 20260729_2324 — WAN-routing coverage expansion + reusable diagnostic scripts (APN routing-issue investigation)

Full pass to make sure the APN routing-issue investigation's learnings actually made it into this pack, prompted by an operator audit question ("did you capture all the information in the docs
folder into skill-smc?"). Answer was initially no — a subagent audit against all 11 investigation docs found real gaps, all closed in this pass.

### Added

- `references/03_communication-flows.md` — new "Manual TBF/`ifb` Ingress Shaping" subsection: a live, fleet-wide, NOT-Ansible-managed shaping mechanism previously undocumented anywhere in this
  pack. Also added: the extensionless-`dhclient-enter-hooks`-vs-`.d/`-decoy capture trap; `dhclient@<iface>.service`'s instantiation-only-when-the-netplan-device-is-real behaviour; switch02
  (`53x`) being cold-standby by design at every site except Horn Island, with the leased-vs-empty-slot triage refinement; the `LAN1`/`LAN2` Testra-managed uplink pair, outside the VLAN scheme and
  unmapped to `topology_vars`; the missing-route-vs-real-ARP-failure diagnostic (the actual Problem 2 mechanism at old-looma/umoona, live-verified 2026-07-29 — supersedes the dish-bypass theory
  for those two sites specifically).
- `references/08_ansible-authoring.md` — the confirmed list of roles that consume `interface.role` and go stale on topology drift the same way `smc_application` does (`smc_iptables`, `smc_qos`,
  `smc_node_exporter` — the last in a *separate playbook*, easy to miss); the topology-cloning authoring risk (a new site's `topology_vars` copied from an existing site can carry wrong VLAN IDs
  silently past every lint/syntax check); the standalone principle that one templated artifact being self-cleaning doesn't imply a sibling artifact from the same role is too; handler-name reuse
  across different `listen` topics being safe, not a collision.
- `references/13_known-issues.md` — new Known Operational Bug row: `my_node_network_device_info` returns zero series on old-looma/new-looma/horn-island despite `node_exporter` being up.
- `references/05_troubleshooting.md` — Tier 1 gained the `tsh ls`-vs-single-`ssh` technique for distinguishing a transient connection blip from a box that's fully deregistered from Teleport; Tier
  7 gained a step for metric-specific monitoring gaps that survive `up{instance=...} == 1`.
- `references/12_content-filtering.md` — one-line cross-reference so its existing "no per-user `tc`/`htb` shaping" claim isn't misread as "no `tc` shaping anywhere on the fleet."
- **New `scripts/` directory** — `collect-smc-evidence.sh` (read-only evidence capture) and `analyse-routing-drift.py` (the "hook covers netplan" drift discriminator), promoted from the
  investigation folder and genericized for reuse (no hardcoded default site list; `--flavor`/`--commit` override the investigation-specific defaults). Plus `routing-diagnostics.justfile`, a
  template task-runner to copy into a future investigation folder. See `scripts/README.md`.

### Corrected

- `references/03_communication-flows.md` — the dish-management-address bullet previously stated the dish-not-in-clean-bypass theory as the accepted cause of "lease held, gateway unreachable."
  Live testing 2026-07-29 showed this is not the cause on the two sites where it reproduced (the same MAC legitimately answers as gateway on every WAN interface there, healthy and broken alike) —
  qualified accordingly, downgraded from "the cause" to "a real, separate observation."
- `references/03_communication-flows.md` — the `smc_application` dhclient-restart-handler-has-no-safety-net bullet was stale relative to a same-day fix; updated from present-tense gap description
  to past-tense-fixed-with-caveat (ported, dry-run validated, not yet tested under a real connection loss).

Full narrative: `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/problem2-live-root-cause-20260729_2112.md` and
`old-looma-umoona-topology-fix-20260729_2316.md`.

## 20260728_1240 — v0.1.5: captive-portal PHP SAPI correction + APPPATH/cache failure mode + Ansible tag hazard (project-coherence run)

Triggered by `project-coherence` on ansible-wifi after a 7-day captive-portal outage across 10 of 16 in-scope `rcp` sites (2026-07-21 → 07-28). Investigating it surfaced two materially wrong architecture claims in this pack, both of the same kind the 2026-07-03 run already flagged: a single host's behaviour written up as fleet-wide truth.

### Corrected

- `references/10_captive-portal.md` §11.1 — previously stated flatly that "PHP-FPM processes `.php` files". **Wrong for the production fleet.** Verified on three sampled `rcp` hosts (horn-island, kalumburu, mornington): zero `php*-fpm` packages installed, `libapache2-mod-php` present, `apache2ctl -M` shows `php_module (shared)`, and no `/etc/php/8.1/fpm/` directory exists. Production runs **mod_php as `www-data`**. Replaced with a scoped, evidence-cited statement.
- `references/10_captive-portal.md` §11.4 — claimed a permanent Ansible `SetHandler` fix "landed 2026-06-26". **False.** Repo-wide grep finds no `SetHandler` in any role template (only a vendored `community.general` test fixture), and the enabled-modules list in `ubuntu-apache-install-configure.yml` is only `rewrite` and `ssl` — no `proxy`, no `proxy_fcgi`. This matches the long-standing ansible-wifi SCRATCHPAD open item recording the change was reverted. Section retitled as historical/ff-smc01-only with a supersession note at the top; the trailing "the Ansible template approach is now canonical" line corrected.
- `references/10_captive-portal.md` §11.7 — the verification snippet told you to test PHP-FPM processing and to read `error.log`. Replaced with a SAPI check (`apache2ctl -M`), a cache/logs perms check, an explicit warning that the §11.8 failure leaves the error log empty, and a warning not to probe `localhost` with a `Host:` header (Apache serves `000-default` and returns a healthy-looking 10671-byte page on a fully dead portal — this produced a wrong "no impact" conclusion during the incident).

### Added

- `references/10_captive-portal.md` §11.8 — new failure mode: `Directory APPPATH/cache must be writable`. Covers the Kohana `core.php:281` bootstrap check, the matching `log/file.php:31` check on `APPPATH/logs` (fix both or the failure just moves one step later), why the response is **HTTP 200** with an empty apache error log, the correct probe form, and the fix command.
- `references/06_failure-modes.md` — matching failure-mode table entry with error signature, cause class, source-of-truth paths, immediate checks, resolution, and the detection gap.
- `references/08_ansible-authoring.md` — new "Tag Hazard" entry: a tagged block that destroys and recreates state must carry its repair tasks under the same tag, including any `stat` task whose registered variable gates the repair block's `when` (otherwise a tag-limited run evaluates `when` against an undefined variable and fails). Includes the `--list-tasks` audit pattern.
- `references/13_known-issues.md` — new fleet-wide risk row: no HTTP-level captive-portal monitoring exists anywhere, and the Kohana usage/status crons run as **root** so they keep succeeding through an outage; also notes a status-code-only probe cannot detect this failure. Plus a staleness-risk note recording this as the **third** instance of the single-host-generalized-to-fleet pattern in this pack (after the 2026-07-03 DNS row and the 2026-07-09 MySQL row).
- `manifest.json` — three new `stable_facts` entries (mod_php not PHP-FPM; the Kohana writability check and its HTTP-200 signature; the Ansible tag-hazard rule). Version bumped 0.1.4 → 0.1.5; `updated_at` set to 2026-07-28T12:40:00Z.

### Related (outside this pack)

- `local-knowledge-ansible/ansible-wifi/issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md` — full RCA.
- `ansible-wifi/.archcore/rules/rule-005-tagged-destroy-blocks-must-carry-repair-tasks.md` — new permanent rule.
- `ansible-wifi/roles/smc_application/tasks/main.yml` — the actual fix (uncommitted at time of writing).

## 20260703_1300 — v0.1.4: DNS architecture corrections + garimba-smc01 failure mode (project-coherence run)

Triggered by `project-coherence` on ansible-wifi after the garimba-smc01 DNS RCA (revisions 2-3) surfaced factual errors in this pack's DNS documentation that predated the incident — rule-002 had never actually been applied for a DNS-domain incident before, and the domain routing table had no explicit DNS row.

### Corrected

- `references/02_service-map.md` — DNS resolver row previously claimed "unbound = RCT flavor / bind = non-RCT flavors", generalized from the single initial RCT-only validation. Corrected: the real gate is `smc_ltp` inventory-group membership (orthogonal to flavor, currently only coincides with `rcp`/guda-guda). Also fixed Stubby's documented listen port (was wrongly given as `127.0.0.1:5353` — that's actually unbound's own `smc_ltp`-only port; Stubby listens on `127.0.0.1@60053`).
- `references/13_known-issues.md` — added a staleness-risk note generalizing the lesson: single-host-validated claims in this pack should not be assumed to hold across all flavors without an independent check.

### Added

- `references/02_service-map.md` — new `systemd-resolved` row documenting the SMC's own DNS path (separate from the DHCP/LAN unbound/stubby/bind path), and Stubby's upstream chain (single upstream, no failover, reached via an autossh **local port forward** — not a reverse tunnel — to Teleport).
- `references/06_failure-modes.md` — new failure-mode entry: domain-specific host DNS resolution delay on non-`smc_ltp` hosts (`DNSStubListener=no` exposes host glibc directly to WAN-path DNS anomalies). First confirmed on garimba-smc01, 2026-07-03.
- `references/13_known-issues.md` — new "Fleet-Wide Architecture Risks" section: Stubby's single-upstream-no-failover design and the lack of monitoring for the autossh local forward / Stubby upstream reachability, both fleet-wide, both discovered incidentally during the garimba-smc01 RCA.
- `.archcore/rules/rule-002-*.md` (ansible-wifi repo) and `AGENTS.md` (ansible-wifi repo) — added an explicit DNS domain row to the domain-routing tables, since none existed despite DNS being a documented troubleshooting area.
- `manifest.json` — new `stable_facts` entry on the `smc_ltp`-vs-flavor DNS gating; version bumped 0.1.3 → 0.1.4; `updated_at` set to 2026-07-03T13:00:00Z.
- `SCRATCHPAD.md` — current state and session history updated.

## 20260626_1845 — v0.1.3: project-coherence checklist + references/10-13 content update

### Added

- `AGENTS.md` — `## Project-coherence checklist` section: explicit Tier 1-4 update instructions for when `project-coherence` runs on this pack, with domain-to-reference routing table and cross-repo trigger rule from ansible-wifi sessions.

### Updated

- `references/10_captive-portal.md` — captive portal two-tier arch, Eclipse config.txt sync mechanism, PHP-FPM SetHandler + a2enconf alternative, PHP short_open_tag (PHP 8.1), Kohana exception handler.
- `references/11_vagrant-lab.md` — vsmc networkd race condition full root cause chain (eth1 bounce → stale DHCP lease → default route drop → Teleport unreachable); Vagrant guard fix.
- `references/12_content-filtering.md` — Eclipse identity model (T&C → auto-PIN → MAC binding → connmark), MAC randomization impact table (stable/bypass/rotate), CAKE fair queuing on bridge_501 with WAN capacity rationale.
- `manifest.json` — version bumped 0.1.2 → 0.1.3; `updated_at` set to 2026-06-26T18:45:00Z.
- `SCRATCHPAD.md` — current state updated; session history entry added; open items updated for v0.1.3.

### Notes

- Content updates fed from ansible-wifi 2026-06-26 session RUNBOOK audit (MK keys: `ansible-wifi.runbook.sections-11-12-13.20260626`, `ansible-wifi.runbook.gap-fill-audit.20260626`).
- Governance-pack regeneration pending (`.ai-context/governance-pack.md` is stale after this change).

## 20260626_1820 — Coherence sweep: repomix config, adapter.md, spec, ARCHITECTURE.md

### Fixed

- `repomix.config.json` — added `README.md`, `ARCHITECTURE.md`, `SCRATCHPAD.md`, `.archcore/**/*.md`, `.archcore/**/*.json` to `include`; moved `.archcore/**` out of `ignore`
- `exports/claude_code/project/skill-smc/adapter.md` — added install-status rows for all 12 governance files added since initial adapter.md creation: `manifest.json`, `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `repomix.config.json`, `.archcore/`
- `.archcore/specs/spec-specialist-pack-file-roles.md` — added file-role rows for `README.md`, `ARCHITECTURE.md`, `SCRATCHPAD.md`, `repomix.config.json`, `.archcore/`
- `ARCHITECTURE.md` — corrected stale repomix token count (was "25 files / ~33k tokens"; now "~125k chars")

### Notes

- Generated by `skill-project-coherence`.
- Coherence greps: clean — no live stale references found.

## 20260626_1812 — README and ARCHITECTURE added

### Added

- `README.md` — folder index, purpose, key file table, governance pointers, install link
- `ARCHITECTURE.md` — component table, information flow, installed surface diagram, key decisions, related workspaces

## 20260626_1810 — Archcore promotion

### Added

- `.archcore/rules/rule-progressive-disclosure-loading.md` — load only the specific reference needed for the task
- `.archcore/rules/rule-reference-update-discipline.md` — cross-file consistency on reference add/edit
- `.archcore/rules/rule-manifest-version-discipline.md` — bump version + updated_at on any content change
- `.archcore/adr/adr-progressive-disclosure-structure.md` — ADR documenting the v0.1.2 monolithic→split decision
- `.archcore/specs/spec-specialist-pack-file-roles.md` — authoritative table of file roles and install surface

### Deleted

- `ARCHCORE_PROMOTION_CANDIDATES.md` — consumed by promotion (all 5 candidates written successfully)

### Notes

- Generated by `skill-ai-it` in `promote` mode.

## 20260626_1808 — Governance scaffold bootstrap

### Added

- `AGENTS.md` — agent policy for maintaining this specialist pack; @-imports `skills_stuff/AGENTS.md`
- `CLAUDE.md` — thin Claude Code wrapper over `AGENTS.md`
- `AI_NAVIGATION.md` — human-readable context router with task-to-reference routing table
- `context-map.yaml` — machine-readable routing map for all 13 references
- `SCRATCHPAD.md` — working memory, populated from session history
- `repomix.config.json` — packs all 25 pack files into `.ai-context/governance-pack.md`
- `.archcore/` — initialized via `archcore init`
- `ARCHCORE_PROMOTION_CANDIDATES.md` — 5 candidates: 3 rules, 1 ADR, 1 spec

### Notes

- Generated by `skill-ai-it` in `bootstrap` mode.
- Graphify: no code files found, no graph output (docs-only pack — expected).
- Repomix: 25 files / 32,896 tokens packed to `.ai-context/governance-pack.md`.

## 0.1.2 — 2026-06-26

- Split the monolithic `RUNBOOK.md` into focused progressive-disclosure files under `references/`.
- Replaced root `RUNBOOK.md` with a concise navigation index and task-to-reference routing table.
- Moved known issues into `references/13_known-issues.md`.
- Removed empty placeholder resource directories.
- Updated Claude Code adapter/install docs to copy the indexed runbook plus focused references.

## 0.1.1 — 2026-06-26

- Aligned canonical source references with installed client adapter references.
- Added known issues as an explicit discoverable reference for coverage gaps and staleness risk.
- Corrected skill venv guidance to use `skills-working-cache/<skill>/venv` and reserve `skills-runtime/` for ephemeral runtime state.
- Normalized OS wording to Ubuntu 20.04+ with Ubuntu 22.04 confirmed in production.
- Updated package metadata version to 0.1.1.

## Unreleased — 2026-05-08

- Corrected SMC expansion to **Site Management Controller** across skill source and exported adapter references.
- Added related workspace mapping for `ansible-wifi`, `ansible-malik`, `dns_query`, and `local-knowledge-ansible/ansible-wifi`.
- Updated runbook guidance so URL-capture/PCAP layout changes are reconciled across the related SMC workspaces.

## 0.1.0 — 2026-04-15

Initial creation.

- SKILL.md: SMC box definition, troubleshooting decision tree (Tiers 1-7), Prometheus alert reference, Ansible authoring rules, communication flows quick reference
- RUNBOOK.md: 9-section deep reference — service map (50+ services), comms flows, dependency tree, failure modes, hardware differences, overlayroot detail, full Ansible workflows
- PROFILE.md: SMC box definition, inventory flavors (apn, cw, nbn_accelerate, nbn_wh, rcp, rct, wh), Teleport access pattern, overlayroot structure
- Validated against live malik-rct01 (RCT flavor, ARM64, Raspberry Pi 4, Ubuntu 22.04)

### Key corrections from live validation (differ from generic docs)

| Assumption | Validated Reality (RCT) |
|---|---|
| DNS = BIND/named | RCT uses Unbound + Stubby (DNS-over-TLS) |
| Traditional swap | RCT uses zram (`/dev/zram0`, ~1.2 GB) |
| iptables chain = `ECLIPSE_*` | Actual chain: `MANAGEMENT` |
| asterisk present | Not deployed on RCT |
| keepalived present | Not deployed on RCT |
| 40 GB storage | Real ext4 FS = 60 GB at `/media/root-ro`; overlayroot = 984 MB tmpfs |
