Title: skill-smc — Reusable Diagnostic and Validation Scripts
Category: script-inventory
Status: current
Authority: local-supplement
Scope: Reusable read-only diagnostic tooling for SMC WAN-routing/topology-drift investigations, fleet-wide hardware/service-health audits, and captive-portal pin-activation diagnosis, plus generic
  ansible-lint pre-push/CI gate scripts for the ansible-wifi repo
Summary: Five categories — (1) WAN-routing diagnostics (evidence capture + drift analysis + topology/hardware cross-check + task-runner template), promoted from the 2026-07-29/30 APN routing-issue
  investigation; (2) ansible-lint baseline/delta-gate scripts, promoted 2026-07-31 from `local-knowledge-ansible/ansible-wifi/scripts/`, for a pre-push hook that blocks only NEW lint violations; (3)
  fleet hardware/security/service-health audit (evidence capture + task-runner), written 2026-08-03 for the first full NBN Accelerate cluster sweep, extended 2026-09-11 with a portal-FQDN-regression
  capture; (4) pack governance validation (check_governance.py), added 2026-09-08 to turn this pack's own routing/version-discipline rules into assertions; (5) captive-portal pin-activation diagnosis
  — `audit-pin-activation.sh` (fleet-wide per-site totals) and `correlate-pin-activation.sh` (per-pin timeline: IP + MAC + lease window + live status for every real activation at one site), both added
  2026-09-11 from the nbn_accelerate/nbn_wh portal-FQDN regression investigation.
Read before running the WAN-routing tools: the "hook covers netplan" discriminator they automate, and why it works, is documented in `../references/03_communication-flows.md`. Read before running
either pin-activation tool: `../references/14_pin-activation-diagnosis.md` — the mechanisms they check answer different questions and neither alone is reliable, and §14.4 documents a real join-order
  bug that `correlate-pin-activation.sh` exists specifically to avoid.

# scripts/

Promoted **2026-07-29** (evidence capture + drift analysis) and **2026-07-30** (topology/hardware cross-check) from `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/scripts/`, where they
were built and live-validated across all seven `rcp` sites during that investigation. Kept here so a future WAN-routing investigation — any site, any flavor — doesn't have to re-derive the
discriminator or re-write the capture set from scratch.

**These are deliberately separate copies from the investigation folder's originals, not symlinks.** Promotion is a review checkpoint, not a relocation — the copies here are genericized (no hardcoded
site lists, `OUTDIR_ROOT` override, etc.) and are meant to diverge from whatever an investigation folder's working copy does next. When an investigation script changes in a way worth having
everywhere, diff it against the promoted copy and re-apply deliberately (see e.g. the `dmidecode-model` capture below) rather than assuming the two stay in sync automatically.

**Promotion checklist — every time a script is promoted or an existing promoted script is updated:**
1. Copy/update the script itself here, genericized (no investigation-specific hardcoding).
2. Add or update its row in the safety-classification table and its own `###` section below.
3. **Update `routing-diagnostics.justfile`** with any new recipe the script needs — a script with no justfile recipe is easy to forget exists. Confirmed missed once (2026-07-30) before being caught
   and fixed in the same pass; treat this as a mandatory step, not an afterthought.
4. Cross-reference the relevant `../references/*.md` file if the script encodes a lesson worth capturing there too (it usually does).

**Safety classification, per the parent policy — every script here is catalogued. An uncatalogued script must be treated as `unknown` safety until inspected.**

| Script                              | Touches                 | Safety    | Notes                                                                                                                    |
| ----------------------------------- | ----------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------ |
| [survey_snmp_tooling.sh](survey_snmp_tooling.sh) | Live SMC appliances | **read-only** | Reports per box whether `snmpget` is present and whether overlayroot is mounted, scoped by Teleport flavour label (`FLAVOURS`, default `rcp,nbn_accelerate`). Both facts vary per box and neither can be inferred from the flavour — that mistake is what it exists to prevent |
| [install_packages.sh](install_packages.sh) | Live SMC appliances | **modifies-state** | Installs apt packages across flavour-scoped boxes. Idempotent, `--dry-run` first, verifies the resulting binary rather than apt's exit code, waits on the dpkg lock via `DPkg::Lock::Timeout`, and refuses boxes with overlayroot mounted unless `--force-overlay`. Defaults to 5 workers for constrained backhaul |
| [collect-smc-evidence.sh](collect-smc-evidence.sh) | Live SMC appliances     | **read-only** | Remote command set is hardcoded; the script takes host names only, never arbitrary commands. **Requires explicit hosts as** |
|                                     |   over Teleport         |           |   **arguments — no default site list** (genericized from the original, which defaulted to one investigation's            |
|                                     |                         |           |   specific sites)                                                                                                        |
| [collect-smc-evidence-full.sh](collect-smc-evidence-full.sh) | Live SMC appliances     | **read-only** | The wide companion to `collect-smc-evidence.sh`: 144 captures across 17 subsystem groups, for triage and pre/post-deploy |
|                                     |   over Teleport         |           |   baselines rather than the routing question. Same hardcoded-command, host-names-only contract. **One SSH session per host** |
|                                     |                         |           |   (delimited stream split locally) instead of one per capture — 144 captures in ~25s. `--only`/`--skip` select groups;   |
|                                     |                         |           |   **redacts credentials by default**, `--no-redact` to disable. x86 capture set; detects Raspberry Pi and says so rather |
|                                     |                         |           |   than running x86-only probes against it                                                                                |
| [analyse-routing-drift.py](analyse-routing-drift.py) | Local `evidence/` tree, | **read-only** | `git show` only; never checks out, never writes to the ansible repo. `--flavor` selects                                  |
|                                     |   local `ansible-wifi`  |           |   `inventories/<flavor>/topology_vars`; `--commit` selects the comparison ref — both default to the original             |
|                                     |   git objects           |           |   investigation's `rcp`/`fb419e6c` and should be overridden per new investigation                                        |
| [analyse-topology-interface-match.py](analyse-topology-interface-match.py) | Local `evidence/` tree, | **read-only** | Reads `topology_vars/<site>.yml` from the working tree (not a specific commit — pre-deploy sanity check, not historical  |
|                                     |   local `ansible-wifi`  |           |   drift analysis); `--flavor` overridable                                                                                |
|                                     |   working tree          |           |                                                                                                                          |
| [routing-diagnostics.justfile](routing-diagnostics.justfile) | Wraps the three         | **read-only** | A **template**, not a ready-to-run file — copy it into a new investigation folder and edit the `sites`/`deployed`/`flavor` |
|                                     |   scripts above         |           |   variables at the top before use                                                                                        |

**Nothing here may write to an SMC.** If a future task needs a mutating command, run it by hand under change control and record it in the investigation's own analysis — do not add it to
`collect-smc-evidence.sh`. The read-only contract is what makes it safe to run these against production sites without a change window.

**Fleet hardware/security/service-health audit (promoted 2026-08-03, different category — full-fleet hardware/software inventory, not WAN-routing-specific):**

| Script                  | Touches                          | Safety    | Notes                                                                                                                       |
| ----------------------- | -------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------- |
| [collect-fleet-health.sh](collect-fleet-health.sh) | Live SMC appliances              | **read-only** | Same hardcoded-command, host-names-only contract as `collect-smc-evidence.sh`. Bundles ~20 read-only commands into 5        |
|                         |   over Teleport                  |           |   grouped captures (not one-command-per-round-trip) to stay tractable at fleet scale over satellite links — see the         |
|                         |                                  |           |   script's own header note. Capture 5 (`05-portal-fqdn-status`, added 2026-09-11) is the config-side half of the            |
|                         |                                  |           |   pin-activation diagnosis below — run alongside `audit-pin-activation.sh` when investigating a suspected                   |
|                         |                                  |           |   portal-issuance problem                                                                                                   |
| [fleet-health.justfile](fleet-health.justfile) | Wraps `collect-fleet-health.sh`  | **read-only** | Unlike `routing-diagnostics.justfile`, ships with a real current site list (the NBN Accelerate cluster, confirmed live via  |
|                         |   `audit-pin-activation.sh`      |           |   `tsh ls` 2026-08-03) rather than a placeholder — edit `sites` or override on the command line for a different fleet. Also |
|                         |                                  |           |   wraps `audit-pin-activation.sh` (`pin-audit`/`pin-audit-sites`) and a `portal-fqdn-check` quick-check, added 2026-09-11   |

**Requires explicit hosts as arguments — no default site list in the script itself** (the justfile's `sites` variable supplies the default site list for `just collect`, the script always requires
args).

**Captive-portal pin-activation diagnosis (added 2026-09-11, different category — live-impact confirmation, not hardware/software inventory):**

| Script                      | Touches         | Safety    | Notes                                                                                                                                    |
| --------------------------- | --------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| [audit-pin-activation.sh](audit-pin-activation.sh) | Live SMC        | **read-only** | Same hardcoded-command, host-names-only contract as `collect-fleet-health.sh`. Checks TWO independent mechanisms per host —              |
|                             |   appliances    |           |   `iptables -t mangle -L ECLIPSE_MARK` (pin validity now) and the Apache `wifi/access` log across both `access.log` and                  |
|                             |   over Teleport |           |   `other_vhosts_access.log` with all rotations (pin issuance over time) — and prints a comparison table. Read                            |
|                             |                 |           |   `../references/14_pin-activation-diagnosis.md` before interpreting results; the two mechanisms answer different questions and reading  |
|                             |                 |           |   either one alone has misled in practice (see that file's pitfalls section)                                                             |
| [correlate-pin-activation.sh](correlate-pin-activation.sh) | Live SMC        | **read-only** | Different question from the script above: not "is this site healthy" but "for THIS site, give me every real activation with its IP, MAC, |
|                             |   appliances    |           |   DHCP lease window, and current live status." Joins the Apache `wifi/access` log (WHEN/WHICH-IP) against `/var/lib/dhcp/dhcpd.leases`   |
|                             |   over Teleport |           |   (WHICH-MAC, keyed on IP over a time window) against `iptables -t mangle` (is that MAC live NOW). Picks the lease block whose `starts`  |
|                             |                 |           |   epoch is the latest one still `<=` the activation time — NOT just "the last block in the file for that IP", which is provably wrong    |
|                             |                 |           |   (confirmed live 2026-09-11, hope-vale: a later lease renewal can start after an earlier real activation). Flags its own best-effort    |
|                             |                 |           |   fallback explicitly rather than silently guessing. See `../references/14_pin-activation-diagnosis.md` §14.4.                           |

**Requires explicit hosts as arguments — no default site list in the script itself**, same contract as the other fleet-scale scripts above.

**Ansible-lint pre-push/CI gate (promoted 2026-07-31, different category — no SMC/host access at all):**

| Script                     | Touches                                  | Safety               | Notes                                                                                                 |
| -------------------------- | ---------------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------- |
| [lint-baseline-refresh.sh](lint-baseline-refresh.sh) | Local git repo                           | **read-only w.r.t. the** | Writes only to `.git/.ansible-lint-ignore` (an untracked git-internal file, not repo content).        |
|                            |   only                                   |   **repo's**         |   Genericized: config path defaults to `<repo_root>/.ansible-lint`, override with                     |
|                            |   (`ansible-lint --generate-ignore`)     |   **tracked content** |   `ANSIBLE_LINT_CONFIG=<path>` — the two scripts this was promoted from disagreed on a hardcoded path |
|                            |                                          |                      |   (`local-knowledge/` vs `local-knowledge-ansible/`); this removes that class of drift                |
| [ansible-lint-delta-gate.sh](ansible-lint-delta-gate.sh) | Local git repo only                      | **read-only**        | Never writes anything; exits non-zero only to block a push/commit. Same `ANSIBLE_LINT_CONFIG`         |
|                            |   (`git diff`/`git cat-file`,            |                      |   override as above. Falls back through `@{upstream}` → `origin/master` → `origin/main` → empty-tree  |
|                            |   `ansible-lint`)                        |                      |   for the comparison base, so it works on a fresh clone with no upstream configured                   |

### `lint-baseline-refresh.sh`

Regenerates `.git/.ansible-lint-ignore` from every currently-lintable file (`*.yml`, `*.yaml`, `*.j2` tracked by git), sorted and deduplicated. Run this deliberately when you want to accept the
current violation set as the new baseline (e.g. after a bulk cleanup, or when first adopting the delta-gate on a repo with existing debt) — **not** as part of every normal lint run, since that would
silently re-baseline away violations introduced since the last refresh.

```bash
scripts/lint-baseline-refresh.sh
# override config location if not at <repo_root>/.ansible-lint:
ANSIBLE_LINT_CONFIG=/path/to/.ansible-lint scripts/lint-baseline-refresh.sh
```

### `ansible-lint-delta-gate.sh`

Meant to run from a pre-push hook (or CI) with the set of changed ansible files as arguments. Runs `ansible-lint` against exactly those files, then classifies every violation:

- **New file** (didn't exist at the merge-base with upstream) → always blocking.
- **Existing file, violation on a line the diff actually touched** → blocking.
- **Existing file, violation on an untouched line, and it's in the baseline** → allowed (pre-existing debt, not yours).
- **Existing file, violation on an untouched line, NOT in the baseline** → blocking (a genuinely new finding on an old line — e.g. a rule version bump surfacing something new).
- **Warnings** → never blocking.

```bash
scripts/ansible-lint-delta-gate.sh roles/smc_network/tasks/ubuntu.yml roles/smc_dns/templates/unbound.conf.j2
```

Exits 0 (with `clean` or `no new violations`) when safe to proceed, non-zero with the blocking violation list on stderr otherwise. Requires `ansible-lint` on `PATH` (or set `ANSIBLE_LINT_VENV_BIN` to
a venv's `bin/` directory, same convention both scripts share).

**Pack governance validation (added 2026-09-08, different category — no SMC/host access, checks this pack's own file structure):**

| Script              | Touches                | Safety    | Notes                                                                                                                                     |
| ------------------- | ---------------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| [check_governance.py](check_governance.py) | This pack's own files  | **read-only** | Stdlib-only; turns this pack's governance claims (RUNBOOK.md/SKILL.md/AI_NAVIGATION.md/context-map.yaml reference routing, manifest.json  |
|                     |   only (read-only)     |           |   single-source version discipline) into assertions that fail. Exit 0 = pass. Run before claiming any durable governance change           |
|                     |                        |           |   is complete                                                                                                                             |

### `check_governance.py`

```bash
python3 scripts/check_governance.py
```

Two check families, tuned to this pack's stated rules (see the file's own CONFIG section for the exact registries and per-entry exemption reasons):

- **Catalog coverage** — every `references/*.md` file is named in `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`, and `context-map.yaml` (the four surfaces
  `.archcore/rules/rule-reference-update-discipline.md` requires a per-file row in), and every script in `scripts/` is named in this file. Fails in both directions — a stale catalog entry, or an
  uncataloged new file.
- **Version single-source** — no governance surface hardcodes a duplicate of this pack's own version number (`.archcore/rules/rule-manifest-version-discipline.md`); `manifest.json` is the sole
  version-of-record. The check derives the current major.minor line from `manifest.json` at run time rather than matching any semver-shaped number, so it does not collide with unrelated software
  versions mentioned in the references (ClamAV, ansible-lint, etc.).

When it fails, fix the pack, not the check. Adding a new governance surface or a new duplicated-fact convention requires extending the checker's CONFIG registries in the same pass — see the file's own
module docstring.

## Contents

- [What each script is for](#what-each-script-is-for)
- [Usage](#usage)
- [Requirements](#requirements)
- [Evidence retention](#evidence-retention)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules)

---

## What each script is for

### `collect-smc-evidence-full.sh`

The broad one. Use it when the question is "what is going on with this box" rather than a specific routing fault, and when you want a **baseline before a deploy and a matching capture after it**.

```bash
./collect-smc-evidence-full.sh yakanarra                    # everything, redacted
./collect-smc-evidence-full.sh yakanarra --only network,rise
./collect-smc-evidence-full.sh umoona --skip voip,portal
./collect-smc-evidence-full.sh --list-groups
```

Output is `evidence-full/<stamp>/<host>/<group>/<capture>.txt`, plus a per-host `SUMMARY.txt` and a run-level `MANIFEST.txt`.

**Groups:** `identity os overlay storage services network dhcp dns firewall qos wifi voip portal monitoring rise access rpi logs`.

**Why one SSH session.** The narrow collector opens one Teleport session per capture. At 144 captures that would be 144 sequential sessions — slow over a satellite link and noisy in the audit log.
This script builds a single remote bash script with `===SMC-CAPTURE===` delimiters and splits the stream locally. Measured: 144 captures in ~25s per host.

**Read the SUMMARY first.** Absences are classified rather than lumped together as failures, because on a healthy box most non-zero exit codes mean a subsystem is simply not deployed on that flavour —
which is itself the finding:

| Status                               | Means                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------ |
| `ok (N lines)`                       | captured                                                                 |
| `empty`                              | ran fine, no output (e.g. no apt holds) — usually a real answer          |
| `absent (no such systemd unit)`      | rc=4, the service is not installed here                                  |
| `absent (command not installed)`     | rc=127                                                                   |
| `absent (no such file or directory)` | rc=1/2                                                                   |
| `FAILED (rc=N)`                      | anything else — the only status that means something actually went wrong |

**Credentials.** This fleet stores secrets in plaintext (no ansible-vault anywhere — see `../references/13_known-issues.md`), and a broad capture reads service configs, so Teleport join tokens,
Asterisk SIP secrets and Graylog tokens land in the output. Captures are therefore **redacted by default**: the key is preserved and the value replaced with `<REDACTED>`, so "a secret is configured
here" stays visible while the secret does not. Redaction is pattern-based — a sensible default, not a guarantee. Read a capture directory before attaching it to anything.

**Two traps this script exists to make visible**, both confirmed live on 2026-08-25:

- **`systemctl status asterisk` reporting `active (exited)` is not proof Asterisk is running.** The unit is an LSB init wrapper, so systemd reports success once the script returns 0 whether or not a
  daemon survives. On umoona-smc01 the unit was `active (exited)` with **zero** asterisk processes, no control socket, and every `asterisk -rx` query failing. The `voip|asterisk-procs` and
  `voip|asterisk-ctl-socket` captures exist so this reads as a diagnosis instead of five confusing failures.
- **A textfile collector that stopped writing does not alert as broken** — it alerts as no-data, or not at all. `monitoring|textfile-mtimes` is therefore captured alongside the contents; the staleness
  windows are in `../references/02_service-map.md`.

**Platform.** Both capture sets are implemented — x86 (BOXER-6404/6641) and ARM64 Raspberry Pi 4B — and the list is filtered per host from detected platform. The `rpi` group runs only on a Pi; the
x86-only probes (`dmidecode` ×3, `smartctl`) are dropped there rather than filling the summary with absences that read like findings. A host whose platform cannot be identified gets the
platform-neutral set. Asking for `--only rpi` against an x86 host skips it cleanly with a message rather than erroring.

The **`rpi` group (20 captures)** is built around the questions the Ubuntu 26.04 migration actually has to answer, so a fleet sweep with `--only rpi` doubles as the phase-0 audit:

| Capture                    | Why                                                                                                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `revision`                 | The revision code decides tryboot eligibility and RAM. An 8 GB 4B is only ever `d03114`/`d03115` (rev 1.4/1.5), and the tryboot EEPROM write-protect caveat applies     |
|                            |   solely to rev 1.0/1.1 — so this settles whether A/B boot is available on the box                                                                                      |
| `eeprom-version`           | **26.04 will not boot** on a Pi 4/400/CM4 with EEPROM older than 2022-11-25 (Pi 5/500/CM5: 2025-02-11)                                                                  |
| `boot-partition`           | 26.04 keeps up to three boot asset sets; older images allocated only 256 MB and upgraded systems keep it                                                                |
| `piboot-layout` /          | Canonical ships piboot A/B from 25.10. Absent on 22.04 — capturing the absence is the before-picture, not a fault                                                       |
|   `autoboot-txt`           |                                                                                                                                                                         |
|   / `piboot-units`         |                                                                                                                                                                         |
| `copymods`                 | Its meaning **inverts** across the migration: a fault condition on 22.04 that `smc_update_kernel` tears down, and the platform default under dracut on 26.04            |
| `throttled`                | `get_throttled` bitmask plus temp/volts — undervoltage is a real field failure here. Bits 0/2 are live; bits 16/18 are since-boot history                               |
| `sd-card` / `mmc-errors`   | SD identity and wear-relevant fields, plus MMC I/O errors from dmesg                                                                                                    |
| `zram` / `zram-units`      | `rct`/`wh` only; the legacy ozai-zram vs rise-zram mismatch has bitten this fleet before                                                                                |

Two deliberate exclusions, both learned from the hardware rather than assumed:

- **`life_time` / `pre_eol_info` are not captured.** They are eMMC attributes and an SD-booted Pi 4 does not expose them — verified on marta-marta-smc01, where `/sys/block/mmcblk0/device/` holds
  `cid`, `csd`, `ssr`, `fwrev`, `manfid`, `oemid`, `serial`, `date` and no wear-level pair. Anything claiming to read SD wear-levelling from those two files on this hardware is wrong.
  `cid`/`csd`/`ssr` are captured instead.
- **`flash-kernel` is never invoked**, only its config read — it writes to the boot partition. The same reasoning excludes `rpi-eeprom-update -a`; the bare command used here only reports.

### `collect-smc-evidence.sh`

Captures the following read-only views from each appliance into `<output-root>/evidence/<YYYYMMDD_hhmm>/<host>/`:

| Capture                                      | Command                                | Why it matters                                                                                               |
| -------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `ip-route`                                   | `ip route show`                        | The ECMP pool and any stray `metric 100` default — the primary evidence for a Problem-1-class fault          |
| `ip-route-table-all`                         | `ip route show table all`              | The per-interface tables the dhclient hook builds for `role: internet` interfaces                            |
| `ip-rule`                                    | `ip rule show`                         | A source rule per interface proves the hook recognised that interface                                        |
| `ip-addr` / `ip-link`                        | `ip -br addr` / `ip -br link`          | Which interfaces hold a CGNAT lease; the deterministic `72:77:77:*` generated MACs                           |
| `dmidecode-model`                            | `dmidecode -s system-product-name`     | Which SMC chassis this is — different models use different physical NIC naming schemes (`enp1s0`-`enp4s0` vs |
|                                              |                                        |   `eno1`/`enp3s0`/...), and `topology_vars` can silently assume the wrong one. Feeds                         |
|                                              |                                        |   `analyse-topology-interface-match.py`'s cross-model naming hint                                            |
| `netplan`                                    | `cat /etc/netplan/*.yaml`              | What `smc_network` actually rendered — compare against the deployed topology                                 |
| `dhclient-enter-hooks`                       | `cat /etc/dhcp/dhclient-enter-hooks`   | What `smc_application` rendered — **the interface list that decides ECMP membership**                        |
| `dhclient-enter-hooks-d`                     | `cat /etc/dhcp/dhclient-enter-hooks.\` | Stock Debian fragments only; kept to prove the override is not here (see capture trap below)                 |
|                                              |   `d/*`                                |                                                                                                              |
| `dhclient-script`                            | `cat /etc/dhcp/dhclient-script`        | Base `add_default_gateway()` and `is_router_reachable()`                                                     |
| `dhclient-units`                             | `systemctl list-units 'dhclient@*'`    | Which interfaces are actually being leased                                                                   |
| `iptables-save`                              | `iptables-save`                        | All tables in one dump — the authoritative ruleset snapshot                                                  |
| `iptables-filter` / `-nat` / `-mangle`       | `iptables [-t <table>] -S`             | Per-table views — `filter`-only misses NAT/mangle entirely (see capture trap below)                          |
|   / `-raw`                                   |                                        |                                                                                                              |
| `interfacecheck`                             | `cat /usr/local/bin/\`                 | The ping check and its `dhclient@` restart behaviour                                                         |
|                                              |   `interfacecheckv2.sh`                |                                                                                                              |
| `internet-ingress-shaping-script` /          | script/unit/status                     | The manual TBF/`ifb` ingress-shaping mechanism — see `../references/03_communication-flows.md`, "Manual      |
|   `internet-shaping-service`                 |                                        |   TBF/`ifb` Ingress Shaping"                                                                                 |
|   / `internet-shaping-unit-status`           |                                        |                                                                                                              |
| `tc-qdisc` / `ip-link-ifb`                   | `tc -s qdisc show`                     | Actual configured shaping rate/burst/latency and traffic counters, and which `ifb*` redirects exist          |
|                                              |   / `ip -br link show type ifb`        |                                                                                                              |
| `netplan-mtime` / `hook-mtime`               | `stat --format='%Y %y %n' ...`         | Last-modified time of netplan vs the dhclient hook — directly shows how far apart `smc_network` and          |
|                                              |                                        |   `smc_application` were last actually run                                                                   |

**Two capture-path traps, both hit and corrected on 2026-07-29** — see `../references/03_communication-flows.md` for the full write-up:

- **The dhclient override is `/etc/dhcp/dhclient-enter-hooks`, without an extension.** `/etc/dhcp/dhclient-enter-hooks.d/` contains only stock Debian fragments and does **not** contain
  `add_default_gateway()`. Capturing only the `.d/` directory silently yields the wrong file with no error.
- **`iptables -S` shows only the `filter` table.** `smc_iptables` templates declare `*filter`, `*mangle` and `*nat`, and the role also references `-t raw`. A filter-only capture misses NAT and mangle
  entirely.

### `analyse-routing-drift.py`

Reads a capture directory and correlates it against the topology committed at a given commit (`--commit`, `--flavor`). For each site it reports the switch01 primary count in git, the live ECMP
members, the stray `metric 100` interface, and any interface holding a lease with no matching `ip rule` (leased but unrecognised by the hook). This automates **the discriminator**: a site is healthy
exactly when the dhclient hook's `case` arm covers every uplink VLAN netplan defines (excluding the SMP-backup VLANs, which are meant to be absent). Full mechanism write-up in
`../references/03_communication-flows.md`.

`--markdown` emits a table ready to paste into an analysis document.

### `analyse-topology-interface-match.py`

Cross-checks a site's committed `topology_vars/<site>.yml` against what the box's live `netplan` actually has, in both directions: every physical interface name and VLAN-parent pairing topology_vars
declares is checked against netplan, and every real (`macaddress:`-bearing) VLAN on the box is checked for a matching topology_vars entry. Also flags a physical interface name that isn't typical for
the box's `dmidecode`-reported model, when the model is in the script's `KNOWN_MODELS` table.

**Run this before editing any site's `topology_vars`, or before deploying to a site you haven't touched recently** — none of `yamllint`/`ansible-lint`/`--syntax-check` catch a topology file that
parses fine but names the wrong physical NIC or points a VLAN at the wrong parent. Confirmed live at New Looma (2026-07-30): `topology_vars` named a WAN interface `eno1` — a NIC name that exists on a
*different* SMC chassis model, not the BOXER-6404 actually deployed there — and had the WAN/LAN-trunk physical roles completely cross-wired. `yamllint`/`ansible-lint`/`--syntax-check` all passed
anyway. See the "Mandatory pre-check" note in `../references/08_ansible-authoring.md` for the full incident.

```bash
./analyse-topology-interface-match.py <site>                    # newest capture
./analyse-topology-interface-match.py <site> <capture-dir>
./analyse-topology-interface-match.py <site> --flavor rct
```

### `collect-fleet-health.sh`

Captures a broad hardware + software-inventory snapshot from each appliance into `<output-root>/evidence/<YYYYMMDD_hhmm>/<host>/`, grouped into 5 files instead of one-per-command (see the script
header for why):

| Capture file | Covers | Why it matters |
|---|---|---|
| `01-identity-hardware.txt` | hostname/uptime/kernel/OS, `dmidecode` manufacturer/product/serial, CPU (`lscpu`), RAM (`free -h`), disks (`lsblk`, `df -h`), | The chassis-model + resource baseline |
|  |   `smartmon.prom`/`sbdm.prom` textfile-collector SSD health, overlayroot mount state |   this pack never had for |
|  |  |   `nbn_accelerate`/`nbn_wh` |
|  |  |   before 2026-08-03 |
| `02-services-security.txt` | `systemctl --failed`, Teleport/autossh state, DNS-stack (`unbound`/`stubby`/`named`), ClamAV daemon + `freshclam` detailed status, | ClamAV/Lynis is an `nbn_accelerate`-only |
|  |   Lynis presence, full list of running services |   hardening gate |
|  |  |   (`08_ansible-authoring.md`) — the |
|  |  |   `freshclam` status specifically checks |
|  |  |   for the CDN-block finding first seen |
|  |  |   2026-08-03 on `warakurna`/`indulkana` |
| `03-apps-scripts-cron.txt` | `apn-mqtt-client`/`cnmaestro-provisioning`/`url_capture` presence, Kohana portal git reflog, | Surfaces undocumented custom scripts the |
|  |   `graylog-sidecar`/`node_exporter`/`prometheus`/`fluent-bit`/`cnmaestro-provisioning` service state, `/usr/local/{bin,sbin,lib}` |   way the rcp-fleet audits in |
|  |   listing, `crontab -l`, `/etc/cron.d/`, `systemctl list-timers` |   `smc-file-writing-analysis` found |
|  |  |   several — don't assume the documented |
|  |  |   app list is exhaustive |
| `04-portal-packages.txt` | Apache vhost config, mobile-app-backend + Kohana portal dir presence, installed versions of | Confirms/refutes the code-inspection-only |
|  |   `bind9`/`unbound`/`stubby`/`apache2`/`php*`/`clamav`/`lynis`/`prometheus`/`node-exporter`/`fluent-bit`/`teleport`/`isc-dhcp-server` |   portal-protocol and package claims in |
|  |  |   `01_overview.md`/`10_captive-portal.md` |
| `05-portal-fqdn-status.txt` | `deny_info` captive-portal directive, `squid.conf` mtime, enabled Apache vhosts, `sslcertcopy` cron entries | Settles whether a box still carries the |
|   (added 2026-09-11) |  |   portal-FQDN regression (config points |
|  |  |   at the Teleport hostname instead of the |
|  |  |   real portal domain) — see |
|  |  |   `13_known-issues.md` and |
|  |  |   `14_pin-activation-diagnosis.md`. |
|  |  |   `squid.conf` mtime matters as much as |
|  |  |   the value: git being fixed doesn't mean |
|  |  |   the box regenerated it |

```bash
./collect-fleet-health.sh warakurna indulkana bungardi        # named sites
# or, with the pre-populated NBN Accelerate site list:
just -f fleet-health.justfile collect
just -f fleet-health.justfile portal-fqdn-check                # quick cross-host summary of capture 5
just -f fleet-health.justfile freshclam-check                 # quick cross-host summary
just -f fleet-health.justfile chassis-models
```

**Sites with more than one numbered host (e.g. `aurukun-smc01`/`aurukun-smc02`) must be passed with their full `-smcNN` suffix** — a bare `aurukun` always resolves to `aurukun-smc01`.

**`just -f <path>` runs recipes with cwd = the justfile's own directory, not the invoker's cwd — confirmed the hard way on the first real fleet run.** `fleet-health.justfile` lives in `scripts/`, but
`collect-fleet-health.sh` writes `evidence/` into its *parent* directory (skill-smc root) by default. A recipe written as `./scripts/collect-fleet-health.sh` or a bare `evidence` path looks correct
when read, but silently resolves to a nonexistent `scripts/scripts/...` or `scripts/ evidence/` and fails (or worse, reports a misleading "no captures yet" instead of an error).
`fleet-health.justfile`'s recipes use `./collect-fleet-health.sh` (sibling file) and `../evidence` (one level up) for this reason — if you add a recipe to a justfile that lives in `scripts/`, match
that convention, and **run every new recipe for real before trusting it**, the way this one was dogfooded: three of its four quick-check recipes had real bugs (wrong paths, and the same
exit-code-of-last-command quirk documented in `collect-fleet-health.sh`'s header) that a syntax check alone would never have caught.

### `audit-pin-activation.sh`

Checks the two independent mechanisms described in `../references/14_pin-activation-diagnosis.md` per appliance and prints a comparison table — this is the live-impact confirmation, not a config check
(that's `collect-fleet-health.sh`'s `05-portal-fqdn-status` capture, above). Run both together when investigating a suspected portal-issuance problem: config state explains *why*, this script confirms
*whether it's actually happening* and *how severely*.

| Column                      | Source                                      | Meaning                                                                                                                  |
| --------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `marks`                     | `iptables -t mangle -L ECLIPSE_MARK`        | Currently-valid pins, right now — a snapshot, not a rate                                                                 |
| `3128(nopin)` / `3131(pin)` | `iptables -t nat -L SQUID_REDIRECT`         | Packet counts per tier — cumulative since the NAT rules were last reloaded, not "now" (can span over a year on a box     |
|                             |                                             |   that hasn't been re-provisioned)                                                                                       |
| `302`                       | Apache `wifi/access` log, both              | Successful pin activations in whatever window this box's log retention covers (~14 days typical on this fleet)           |
|                             |   `access.log*` and                         |                                                                                                                          |
|                             |   `other_vhosts_access.log*`, all rotations |                                                                                                                          |
| `200`                       | same log                                    | Failed activation attempts (portal re-rendered with an inline error instead of redirecting)                              |
| `404`                       | same log                                    | Requests to the endpoint that didn't resolve — usually a stale/malformed link, not a portal failure                      |

```bash
./audit-pin-activation.sh hope-vale kowanyama galiwinku       # named sites
# or, with the pre-populated NBN Accelerate site list:
just -f fleet-health.justfile pin-audit
just -f fleet-health.justfile pin-audit-sites "hope-vale kowanyama"
```

**Read the two "pitfalls" bullets in `../references/14_pin-activation-diagnosis.md` before treating a `marks` reading of `0` as "site dead," or a `302` count of `0` as proof no one has a working pin —
both were confirmed live on 2026-09-11 to individually mislead on an otherwise-healthy site. The table above is only trustworthy read as a whole, columns cross-checked against each other, not any
single column in isolation.**

### `correlate-pin-activation.sh`

Answers a different question from the script above: not "is this site's pin pipeline healthy" but "for this ONE site, walk me through every real activation" — one row per successful (`302`)
`wifi/access` POST, joined against that client's DHCP lease (for the MAC) and the current mangle table (is that MAC's pin still live). Written 2026-09-11 in direct response to an operator request for
this exact per-pin timeline, after a manual one-off version of the same join (done live against `hope-vale-smc01`) proved the idea sound but used a naive "last lease block in the file" lookup.

**The join-order bug this script exists to fix.** `dhcpd.leases` is append-only; a later lease renewal for the same IP can have a `starts` timestamp AFTER an earlier real activation under an *older*
lease for that IP. Taking "the last block in the file" (what the manual one-off version did) picks the wrong MAC in that case. This script instead scans every lease block recorded for the activated IP
and picks the one whose `starts` epoch is the **latest one still `<=` the activation epoch** — the lease that was actually in force at that instant. Confirmed live 2026-09-11 on `hope-vale-smc01`:
across a 30-activation sample, 4 of 30 IPs had no lease block that had already started by their activation time (their earliest known lease started later) — the script flags these explicitly as a
best-effort fallback rather than silently asserting a MAC it can't confirm.

**Handles missing data explicitly, not silently** — per the operator's own requirement ("as long as the data is there in the files"): an IP with no lease record at all in `dhcpd.leases` prints
`no-lease-found`; a matched lease block that itself lacks a `hardware ethernet` line (confirmed to occur live) prints `no-mac-in-lease-record` rather than an unlabelled blank field. Both are visibly
distinct from a normal successful join.

| Column                      | Source                               | Meaning                                                                                                        |
| --------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `IP`                        | Apache `wifi/access` log             | Client IP that submitted the activation                                                                        |
| `Activated`                 | Apache `wifi/access` log             | Timestamp of the successful (`302`) activation                                                                 |
| `MAC`                       | `/var/lib/dhcp/dhcpd.leases`         | The MAC holding that IP at (or nearest before) the activation instant — see join-order note above              |
| `Lease start` / `Lease end` | `/var/lib/dhcp/dhcpd.leases`         | The matched lease's own window (both are epoch `starts`/`ends` fields, converted to local time)                |
| `Live?`                     | `iptables -t mangle -L ECLIPSE_MARK` | Is that MAC's pin valid **right now** (check time, not activation time — a since-expired pin correctly reads `no`) |

```bash
./correlate-pin-activation.sh hope-vale                 # one site, default last 30 activations
./correlate-pin-activation.sh hope-vale kowanyama        # multiple sites, one table each
LOOKBACK=60 ./correlate-pin-activation.sh bungardi       # widen the activation window
```

**Runs entirely from a non-Linux operator machine.** The one GNU-`date`-dependent step (Apache-log-timestamp → epoch) happens on the remote Ubuntu box over `tsh ssh`; the join itself and the
lease-epoch → human-readable conversion happen locally with a portable `date -d` / `date -r` fallback, so this works unmodified from a Mac.

### `teleport-tunnel.sh`

Opens a `tsh` local-port-forward tunnel from this workstation to any device reachable from a site's SMC box — Cambium APs/SMs, or anything else on that site's management network. Written 2026-09-17
for `cambium-swap`/`skill-cambium` device-access work, then generalised and moved here since it's Teleport tunneling, not a Cambium-specific concern — this pack owns `tsh`/Teleport mechanics, per each
pack's own `RUNBOOK.md`/`AGENTS.md` boundary.

**Site -> SMC-host is resolved live from ansible-wifi's own inventory, never hardcoded.** Each site has a `[<site>_smc_bases]` group in exactly one `inventories/<flavour>/prod` file; the script
`grep`s for it and `awk`s out the first host listed. Only the flavour->Teleport-target split (`nbn_accelerate`/`nbn_wh`/`cw` -> `teleport.communitywifi.net.au`, `rcp`/`rct`/`wh`/`apn` ->
`teleport.apn.au`) is a small fixed table in the script — that's a structural fact about the two Teleport deployments (see `../references/01_overview.md`'s split table), not per-site data.

```bash
./teleport-tunnel.sh hope-vale 10.255.3.1 20001 443 120     # a Cambium XV2's web UI
./teleport-tunnel.sh burringurrah 10.255.11.45               # defaults: local port 20000, 443, 120s
```

Requires an active `tsh login --proxy=<target>` session for the site's Teleport target already — does not log in for you (`rcp`/`rct`/`wh`-flavour targets need interactive MFA). Blocks for
`duration_seconds` once the tunnel is confirmed listening; background it (`&`) to keep working while it's open.

**Port convention for concurrent dispatch (2026-09-18):** when more than one tunnel might be open at once — parallel subagents, or several device families in one session — assign each family its own
fixed `local_port` so tunnels never collide and a stale leftover on a shared port can't mask a fresh one. Reserved range `20101`-`20199`; current assignments: XV2 `20101`, ePMP `20102`, cnWave
`20103`. Extend this list rather than picking new numbers ad hoc. R195P needs no tunnel (nested SSH via the SMC box, not a local port-forward).

| Script               | Touches                                                 | Safety                          | Notes                                                                             |
| -------------------- | ------------------------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------- |
| `teleport-tunnel.sh` | `tsh` (Teleport session), ansible-wifi                  | `external-network`,             | Opens a real tunnel to a live device; never writes anything, never                |
|                      |   inventories (read-only)                               |   `requires-credentials`        |   touches ansible-wifi                                                            |

## Usage

```bash
# One-off, no justfile:
./collect-smc-evidence.sh <site1> <site2> ...
./analyse-routing-drift.py --flavor <flavor> --commit <ref>
./collect-fleet-health.sh <site1> <site2> ...

# Or copy routing-diagnostics.justfile into your investigation folder, edit its top variables, then:
just collect
just analyse-md

# fleet-health.justfile ships with a real site list already — usable directly from skill-smc/scripts/:
just -f fleet-health.justfile collect
just -f fleet-health.justfile pin-audit
```

## Requirements

- `tsh` logged in to the relevant Teleport cluster (`tsh login`).
- `just` (optional — only needed if using the justfile template), `bash`, Python 3 (standard library only — no third-party imports).
- A local clone of `ansible-wifi` at `/Volumes/Data/_ansible/ansible-wifi` for the topology comparisons.

## Evidence retention

Captures are the only record of live state at a point in time and **should be kept**, not deleted to save space — they cannot be regenerated for a past date. Write them into your investigation
folder's own `evidence/` directory (via `OUTDIR_ROOT=<investigation-path> ./collect-smc-evidence.sh ...` or `./collect-fleet-health.sh ...`), not into this skill-smc directory — skill-smc holds
reusable knowledge and tooling, not case-specific evidence. See the parent repo's canonical-source-of-truth policy on keeping investigation artifacts local to their investigation folder.

**The 2026-08-03 NBN Accelerate fleet sweep was captured without `OUTDIR_ROOT` set** (script default, under `skill-smc/evidence/`) — relocate that capture to a case-specific
`local-knowledge-ansible/ansible-wifi/issues/` folder per this policy once collection finishes, rather than leaving raw per-host evidence inside the skill-smc pack long-term. The *analysis*
(conclusions, confirmed/refuted claims, new findings) belongs in `references/*.md`; the raw capture files do not.

<!-- BEGIN MANAGED: skill-ai-it:scripts --> <!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->

