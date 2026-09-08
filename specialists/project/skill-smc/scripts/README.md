Title: skill-smc — Reusable Diagnostic and Validation Scripts
Category: script-inventory
Status: current
Authority: local-supplement
Scope: Reusable read-only diagnostic tooling for SMC WAN-routing/topology-drift investigations and fleet-wide hardware/service-health audits, plus generic ansible-lint pre-push/CI gate scripts for the ansible-wifi repo
Summary: Three categories — (1) WAN-routing diagnostics (evidence capture + drift analysis + topology/hardware cross-check + task-runner template), promoted from the 2026-07-29/30 APN routing-issue
  investigation; (2) ansible-lint baseline/delta-gate scripts, promoted 2026-07-31 from `local-knowledge-ansible/ansible-wifi/scripts/`, for a pre-push hook that blocks only NEW lint violations;
  (3) fleet hardware/security/service-health audit (evidence capture + task-runner), written 2026-08-03 for the first full NBN Accelerate cluster sweep.
  Read before running the WAN-routing tools: the "hook covers netplan" discriminator they automate, and why it works, is documented in `../references/03_communication-flows.md`.

# scripts/

Promoted **2026-07-29** (evidence capture + drift analysis) and **2026-07-30** (topology/hardware cross-check) from `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/scripts/`, where
they were built and live-validated across all seven `rcp` sites during that investigation. Kept here so a future WAN-routing investigation — any site, any flavor — doesn't have to re-derive the
discriminator or re-write the capture set from scratch.

**These are deliberately separate copies from the investigation folder's originals, not symlinks.** Promotion is a review checkpoint, not a relocation — the copies here are genericized (no
hardcoded site lists, `OUTDIR_ROOT` override, etc.) and are meant to diverge from whatever an investigation folder's working copy does next. When an investigation script changes in a way worth
having everywhere, diff it against the promoted copy and re-apply deliberately (see e.g. the `dmidecode-model` capture below) rather than assuming the two stay in sync automatically.

**Promotion checklist — every time a script is promoted or an existing promoted script is updated:**
1. Copy/update the script itself here, genericized (no investigation-specific hardcoding).
2. Add or update its row in the safety-classification table and its own `###` section below.
3. **Update `routing-diagnostics.justfile`** with any new recipe the script needs — a script with
   no justfile recipe is easy to forget exists. Confirmed missed once (2026-07-30) before being
   caught and fixed in the same pass; treat this as a mandatory step, not an afterthought.
4. Cross-reference the relevant `../references/*.md` file if the script encodes a lesson worth
   capturing there too (it usually does).

**Safety classification, per the parent policy — every script here is catalogued. An uncatalogued script must be treated as `unknown` safety until inspected.**

| Script | Touches | Safety | Notes |
|---|---|---|---|
| [collect-smc-evidence.sh](collect-smc-evidence.sh) | Live SMC appliances over Teleport | **read-only** | Remote command set is hardcoded; the script takes host names only, never arbitrary commands. **Requires explicit hosts as arguments — no default site list** (genericized from the original, which defaulted to one investigation's specific sites) |
| [collect-smc-evidence-full.sh](collect-smc-evidence-full.sh) | Live SMC appliances over Teleport | **read-only** | The wide companion to `collect-smc-evidence.sh`: 144 captures across 17 subsystem groups, for triage and pre/post-deploy baselines rather than the routing question. Same hardcoded-command, host-names-only contract. **One SSH session per host** (delimited stream split locally) instead of one per capture — 144 captures in ~25s. `--only`/`--skip` select groups; **redacts credentials by default**, `--no-redact` to disable. x86 capture set; detects Raspberry Pi and says so rather than running x86-only probes against it |
| [analyse-routing-drift.py](analyse-routing-drift.py) | Local `evidence/` tree, local `ansible-wifi` git objects | **read-only** | `git show` only; never checks out, never writes to the ansible repo. `--flavor` selects `inventories/<flavor>/topology_vars`; `--commit` selects the comparison ref — both default to the original investigation's `rcp`/`fb419e6c` and should be overridden per new investigation |
| [analyse-topology-interface-match.py](analyse-topology-interface-match.py) | Local `evidence/` tree, local `ansible-wifi` working tree | **read-only** | Reads `topology_vars/<site>.yml` from the working tree (not a specific commit — pre-deploy sanity check, not historical drift analysis); `--flavor` overridable |
| [routing-diagnostics.justfile](routing-diagnostics.justfile) | Wraps the three scripts above | **read-only** | A **template**, not a ready-to-run file — copy it into a new investigation folder and edit the `sites`/`deployed`/`flavor` variables at the top before use |

**Nothing here may write to an SMC.** If a future task needs a mutating command, run it by hand under change control and record it in the investigation's own analysis — do not add it to
`collect-smc-evidence.sh`. The read-only contract is what makes it safe to run these against production sites without a change window.

**Fleet hardware/security/service-health audit (promoted 2026-08-03, different category — full-fleet hardware/software inventory, not WAN-routing-specific):**

| Script | Touches | Safety | Notes |
|---|---|---|---|
| [collect-fleet-health.sh](collect-fleet-health.sh) | Live SMC appliances over Teleport | **read-only** | Same hardcoded-command, host-names-only contract as `collect-smc-evidence.sh`. Bundles ~20 read-only commands into 4 grouped captures (not one-command-per-round-trip) to stay tractable at fleet scale over satellite links — see the script's own header note |
| [fleet-health.justfile](fleet-health.justfile) | Wraps `collect-fleet-health.sh` | **read-only** | Unlike `routing-diagnostics.justfile`, ships with a real current site list (the NBN Accelerate cluster, confirmed live via `tsh ls` 2026-08-03) rather than a placeholder — edit `sites` or override on the command line for a different fleet |

**Requires explicit hosts as arguments — no default site list in the script itself** (the justfile's `sites` variable supplies the default site list for `just collect`, the script always requires args).

**Ansible-lint pre-push/CI gate (promoted 2026-07-31, different category — no SMC/host access at all):**

| Script | Touches | Safety | Notes |
|---|---|---|---|
| [lint-baseline-refresh.sh](lint-baseline-refresh.sh) | Local git repo only (`ansible-lint --generate-ignore`) | **read-only w.r.t. the repo's tracked content** | Writes only to `.git/.ansible-lint-ignore` (an untracked git-internal file, not repo content). Genericized: config path defaults to `<repo_root>/.ansible-lint`, override with `ANSIBLE_LINT_CONFIG=<path>` — the two scripts this was promoted from disagreed on a hardcoded path (`local-knowledge/` vs `local-knowledge-ansible/`); this removes that class of drift |
| [ansible-lint-delta-gate.sh](ansible-lint-delta-gate.sh) | Local git repo only (`git diff`/`git cat-file`, `ansible-lint`) | **read-only** | Never writes anything; exits non-zero only to block a push/commit. Same `ANSIBLE_LINT_CONFIG` override as above. Falls back through `@{upstream}` → `origin/master` → `origin/main` → empty-tree for the comparison base, so it works on a fresh clone with no upstream configured |

### `lint-baseline-refresh.sh`

Regenerates `.git/.ansible-lint-ignore` from every currently-lintable file (`*.yml`, `*.yaml`,
`*.j2` tracked by git), sorted and deduplicated. Run this deliberately when you want to accept the
current violation set as the new baseline (e.g. after a bulk cleanup, or when first adopting the
delta-gate on a repo with existing debt) — **not** as part of every normal lint run, since that
would silently re-baseline away violations introduced since the last refresh.

```bash
scripts/lint-baseline-refresh.sh
# override config location if not at <repo_root>/.ansible-lint:
ANSIBLE_LINT_CONFIG=/path/to/.ansible-lint scripts/lint-baseline-refresh.sh
```

### `ansible-lint-delta-gate.sh`

Meant to run from a pre-push hook (or CI) with the set of changed ansible files as arguments. Runs
`ansible-lint` against exactly those files, then classifies every violation:

- **New file** (didn't exist at the merge-base with upstream) → always blocking.
- **Existing file, violation on a line the diff actually touched** → blocking.
- **Existing file, violation on an untouched line, and it's in the baseline** → allowed (pre-existing debt, not yours).
- **Existing file, violation on an untouched line, NOT in the baseline** → blocking (a genuinely new finding on an old line — e.g. a rule version bump surfacing something new).
- **Warnings** → never blocking.

```bash
scripts/ansible-lint-delta-gate.sh roles/smc_network/tasks/ubuntu.yml roles/smc_dns/templates/unbound.conf.j2
```

Exits 0 (with `clean` or `no new violations`) when safe to proceed, non-zero with the blocking
violation list on stderr otherwise. Requires `ansible-lint` on `PATH` (or set
`ANSIBLE_LINT_VENV_BIN` to a venv's `bin/` directory, same convention both scripts share).

## What each script is for

### `collect-smc-evidence-full.sh`

The broad one. Use it when the question is "what is going on with this box" rather than a specific routing fault, and when you want a **baseline before
a deploy and a matching capture after it**.

```bash
./collect-smc-evidence-full.sh yakanarra                    # everything, redacted
./collect-smc-evidence-full.sh yakanarra --only network,rise
./collect-smc-evidence-full.sh umoona --skip voip,portal
./collect-smc-evidence-full.sh --list-groups
```

Output is `evidence-full/<stamp>/<host>/<group>/<capture>.txt`, plus a per-host `SUMMARY.txt` and a run-level `MANIFEST.txt`.

**Groups:** `identity os overlay storage services network dhcp dns firewall qos wifi voip portal monitoring rise access rpi logs`.

**Why one SSH session.** The narrow collector opens one Teleport session per capture. At 144 captures that would be 144 sequential sessions — slow over
a satellite link and noisy in the audit log. This script builds a single remote bash script with `===SMC-CAPTURE===` delimiters and splits the stream
locally. Measured: 144 captures in ~25s per host.

**Read the SUMMARY first.** Absences are classified rather than lumped together as failures, because on a healthy box most non-zero exit codes mean a
subsystem is simply not deployed on that flavour — which is itself the finding:

| Status | Means |
|---|---|
| `ok (N lines)` | captured |
| `empty` | ran fine, no output (e.g. no apt holds) — usually a real answer |
| `absent (no such systemd unit)` | rc=4, the service is not installed here |
| `absent (command not installed)` | rc=127 |
| `absent (no such file or directory)` | rc=1/2 |
| `FAILED (rc=N)` | anything else — the only status that means something actually went wrong |

**Credentials.** This fleet stores secrets in plaintext (no ansible-vault anywhere — see `../references/13_known-issues.md`), and a broad capture reads
service configs, so Teleport join tokens, Asterisk SIP secrets and Graylog tokens land in the output. Captures are therefore **redacted by default**:
the key is preserved and the value replaced with `<REDACTED>`, so "a secret is configured here" stays visible while the secret does not. Redaction is
pattern-based — a sensible default, not a guarantee. Read a capture directory before attaching it to anything.

**Two traps this script exists to make visible**, both confirmed live on 2026-08-25:

- **`systemctl status asterisk` reporting `active (exited)` is not proof Asterisk is running.** The unit is an LSB init wrapper, so systemd reports
  success once the script returns 0 whether or not a daemon survives. On umoona-smc01 the unit was `active (exited)` with **zero** asterisk processes,
  no control socket, and every `asterisk -rx` query failing. The `voip|asterisk-procs` and `voip|asterisk-ctl-socket` captures exist so this reads as a
  diagnosis instead of five confusing failures.
- **A textfile collector that stopped writing does not alert as broken** — it alerts as no-data, or not at all. `monitoring|textfile-mtimes` is
  therefore captured alongside the contents; the staleness windows are in `../references/02_service-map.md`.

**Platform.** Both capture sets are implemented — x86 (BOXER-6404/6641) and ARM64 Raspberry Pi 4B — and the list is filtered per host from detected
platform. The `rpi` group runs only on a Pi; the x86-only probes (`dmidecode` ×3, `smartctl`) are dropped there rather than filling the summary with
absences that read like findings. A host whose platform cannot be identified gets the platform-neutral set. Asking for `--only rpi` against an x86 host
skips it cleanly with a message rather than erroring.

The **`rpi` group (20 captures)** is built around the questions the Ubuntu 26.04 migration actually has to answer, so a fleet sweep with `--only rpi`
doubles as the phase-0 audit:

| Capture | Why |
|---|---|
| `revision` | The revision code decides tryboot eligibility and RAM. An 8 GB 4B is only ever `d03114`/`d03115` (rev 1.4/1.5), and the tryboot EEPROM write-protect caveat applies solely to rev 1.0/1.1 — so this settles whether A/B boot is available on the box |
| `eeprom-version` | **26.04 will not boot** on a Pi 4/400/CM4 with EEPROM older than 2022-11-25 (Pi 5/500/CM5: 2025-02-11) |
| `boot-partition` | 26.04 keeps up to three boot asset sets; older images allocated only 256 MB and upgraded systems keep it |
| `piboot-layout` / `autoboot-txt` / `piboot-units` | Canonical ships piboot A/B from 25.10. Absent on 22.04 — capturing the absence is the before-picture, not a fault |
| `copymods` | Its meaning **inverts** across the migration: a fault condition on 22.04 that `smc_update_kernel` tears down, and the platform default under dracut on 26.04 |
| `throttled` | `get_throttled` bitmask plus temp/volts — undervoltage is a real field failure here. Bits 0/2 are live; bits 16/18 are since-boot history |
| `sd-card` / `mmc-errors` | SD identity and wear-relevant fields, plus MMC I/O errors from dmesg |
| `zram` / `zram-units` | `rct`/`wh` only; the legacy ozai-zram vs rise-zram mismatch has bitten this fleet before |

Two deliberate exclusions, both learned from the hardware rather than assumed:

- **`life_time` / `pre_eol_info` are not captured.** They are eMMC attributes and an SD-booted Pi 4 does not expose them — verified on
  marta-marta-smc01, where `/sys/block/mmcblk0/device/` holds `cid`, `csd`, `ssr`, `fwrev`, `manfid`, `oemid`, `serial`, `date` and no wear-level pair.
  Anything claiming to read SD wear-levelling from those two files on this hardware is wrong. `cid`/`csd`/`ssr` are captured instead.
- **`flash-kernel` is never invoked**, only its config read — it writes to the boot partition. The same reasoning excludes `rpi-eeprom-update -a`; the
  bare command used here only reports.

### `collect-smc-evidence.sh`

Captures the following read-only views from each appliance into `<output-root>/evidence/<YYYYMMDD_hhmm>/<host>/`:

| Capture | Command | Why it matters |
|---|---|---|
| `ip-route` | `ip route show` | The ECMP pool and any stray `metric 100` default — the primary evidence for a Problem-1-class fault |
| `ip-route-table-all` | `ip route show table all` | The per-interface tables the dhclient hook builds for `role: internet` interfaces |
| `ip-rule` | `ip rule show` | A source rule per interface proves the hook recognised that interface |
| `ip-addr` / `ip-link` | `ip -br addr` / `ip -br link` | Which interfaces hold a CGNAT lease; the deterministic `72:77:77:*` generated MACs |
| `dmidecode-model` | `dmidecode -s system-product-name` | Which SMC chassis this is — different models use different physical NIC naming schemes (`enp1s0`-`enp4s0` vs `eno1`/`enp3s0`/...), and `topology_vars` can silently assume the wrong one. Feeds `analyse-topology-interface-match.py`'s cross-model naming hint |
| `netplan` | `cat /etc/netplan/*.yaml` | What `smc_network` actually rendered — compare against the deployed topology |
| `dhclient-enter-hooks` | `cat /etc/dhcp/dhclient-enter-hooks` | What `smc_application` rendered — **the interface list that decides ECMP membership** |
| `dhclient-enter-hooks-d` | `cat /etc/dhcp/dhclient-enter-hooks.d/*` | Stock Debian fragments only; kept to prove the override is not here (see capture trap below) |
| `dhclient-script` | `cat /etc/dhcp/dhclient-script` | Base `add_default_gateway()` and `is_router_reachable()` |
| `dhclient-units` | `systemctl list-units 'dhclient@*'` | Which interfaces are actually being leased |
| `iptables-save` | `iptables-save` | All tables in one dump — the authoritative ruleset snapshot |
| `iptables-filter` / `-nat` / `-mangle` / `-raw` | `iptables [-t <table>] -S` | Per-table views — `filter`-only misses NAT/mangle entirely (see capture trap below) |
| `interfacecheck` | `cat /usr/local/bin/interfacecheckv2.sh` | The ping check and its `dhclient@` restart behaviour |
| `internet-ingress-shaping-script` / `internet-shaping-service` / `internet-shaping-unit-status` | script/unit/status | The manual TBF/`ifb` ingress-shaping mechanism — see `../references/03_communication-flows.md`, "Manual TBF/`ifb` Ingress Shaping" |
| `tc-qdisc` / `ip-link-ifb` | `tc -s qdisc show` / `ip -br link show type ifb` | Actual configured shaping rate/burst/latency and traffic counters, and which `ifb*` redirects exist |
| `netplan-mtime` / `hook-mtime` | `stat --format='%Y %y %n' ...` | Last-modified time of netplan vs the dhclient hook — directly shows how far apart `smc_network` and `smc_application` were last actually run |

**Two capture-path traps, both hit and corrected on 2026-07-29** — see `../references/03_communication-flows.md` for the full write-up:

- **The dhclient override is `/etc/dhcp/dhclient-enter-hooks`, without an extension.** `/etc/dhcp/dhclient-enter-hooks.d/` contains only stock Debian fragments and does **not** contain
  `add_default_gateway()`. Capturing only the `.d/` directory silently yields the wrong file with no error.
- **`iptables -S` shows only the `filter` table.** `smc_iptables` templates declare `*filter`, `*mangle` and `*nat`, and the role also references `-t raw`. A filter-only capture misses NAT and
  mangle entirely.

### `analyse-routing-drift.py`

Reads a capture directory and correlates it against the topology committed at a given commit (`--commit`, `--flavor`). For each site it reports the switch01 primary count in git, the live ECMP
members, the stray `metric 100` interface, and any interface holding a lease with no matching `ip rule` (leased but unrecognised by the hook). This automates **the discriminator**: a site is
healthy exactly when the dhclient hook's `case` arm covers every uplink VLAN netplan defines (excluding the SMP-backup VLANs, which are meant to be absent). Full mechanism write-up in
`../references/03_communication-flows.md`.

`--markdown` emits a table ready to paste into an analysis document.

### `analyse-topology-interface-match.py`

Cross-checks a site's committed `topology_vars/<site>.yml` against what the box's live `netplan` actually has, in both directions: every physical interface name and VLAN-parent pairing
topology_vars declares is checked against netplan, and every real (`macaddress:`-bearing) VLAN on the box is checked for a matching topology_vars entry. Also flags a physical interface name
that isn't typical for the box's `dmidecode`-reported model, when the model is in the script's `KNOWN_MODELS` table.

**Run this before editing any site's `topology_vars`, or before deploying to a site you haven't touched recently** — none of `yamllint`/`ansible-lint`/`--syntax-check` catch a topology file that
parses fine but names the wrong physical NIC or points a VLAN at the wrong parent. Confirmed live at New Looma (2026-07-30): `topology_vars` named a WAN interface `eno1` — a NIC name that exists
on a *different* SMC chassis model, not the BOXER-6404 actually deployed there — and had the WAN/LAN-trunk physical roles completely cross-wired. `yamllint`/`ansible-lint`/`--syntax-check` all
passed anyway. See the "Mandatory pre-check" note in `../references/08_ansible-authoring.md` for the full incident.

```bash
./analyse-topology-interface-match.py <site>                    # newest capture
./analyse-topology-interface-match.py <site> <capture-dir>
./analyse-topology-interface-match.py <site> --flavor rct
```

### `collect-fleet-health.sh`

Captures a broad hardware + software-inventory snapshot from each appliance into
`<output-root>/evidence/<YYYYMMDD_hhmm>/<host>/`, grouped into 4 files instead of one-per-command
(see the script header for why):

| Capture file | Covers | Why it matters |
|---|---|---|
| `01-identity-hardware.txt` | hostname/uptime/kernel/OS, `dmidecode` manufacturer/product/serial, CPU (`lscpu`), RAM (`free -h`), disks (`lsblk`, `df -h`), `smartmon.prom`/`sbdm.prom` textfile-collector SSD health, overlayroot mount state | The chassis-model + resource baseline this pack never had for `nbn_accelerate`/`nbn_wh` before 2026-08-03 |
| `02-services-security.txt` | `systemctl --failed`, Teleport/autossh state, DNS-stack (`unbound`/`stubby`/`named`), ClamAV daemon + `freshclam` detailed status, Lynis presence, full list of running services | ClamAV/Lynis is an `nbn_accelerate`-only hardening gate (`08_ansible-authoring.md`) — the `freshclam` status specifically checks for the CDN-block finding first seen 2026-08-03 on `warakurna`/`indulkana` |
| `03-apps-scripts-cron.txt` | `apn-mqtt-client`/`cnmaestro-provisioning`/`url_capture` presence, Kohana portal git reflog, `graylog-sidecar`/`node_exporter`/`prometheus`/`fluent-bit`/`cnmaestro-provisioning` service state, `/usr/local/{bin,sbin,lib}` listing, `crontab -l`, `/etc/cron.d/`, `systemctl list-timers` | Surfaces undocumented custom scripts the way the rcp-fleet audits in `smc-file-writing-analysis` found several — don't assume the documented app list is exhaustive |
| `04-portal-packages.txt` | Apache vhost config, mobile-app-backend + Kohana portal dir presence, installed versions of `bind9`/`unbound`/`stubby`/`apache2`/`php*`/`clamav`/`lynis`/`prometheus`/`node-exporter`/`fluent-bit`/`teleport`/`isc-dhcp-server` | Confirms/refutes the code-inspection-only portal-protocol and package claims in `01_overview.md`/`10_captive-portal.md` |

```bash
./collect-fleet-health.sh warakurna indulkana bungardi        # named sites
# or, with the pre-populated NBN Accelerate site list:
just -f fleet-health.justfile collect
just -f fleet-health.justfile freshclam-check                 # quick cross-host summary
just -f fleet-health.justfile chassis-models
```

**Sites with more than one numbered host (e.g. `aurukun-smc01`/`aurukun-smc02`) must be passed
with their full `-smcNN` suffix** — a bare `aurukun` always resolves to `aurukun-smc01`.

**`just -f <path>` runs recipes with cwd = the justfile's own directory, not the invoker's cwd —
confirmed the hard way on the first real fleet run.** `fleet-health.justfile` lives in `scripts/`,
but `collect-fleet-health.sh` writes `evidence/` into its *parent* directory (skill-smc root) by
default. A recipe written as `./scripts/collect-fleet-health.sh` or a bare `evidence` path looks
correct when read, but silently resolves to a nonexistent `scripts/scripts/...` or `scripts/
evidence/` and fails (or worse, reports a misleading "no captures yet" instead of an error).
`fleet-health.justfile`'s recipes use `./collect-fleet-health.sh` (sibling file) and `../evidence`
(one level up) for this reason — if you add a recipe to a justfile that lives in `scripts/`,
match that convention, and **run every new recipe for real before trusting it**, the way this one
was dogfooded: three of its four quick-check recipes had real bugs (wrong paths, and the same
exit-code-of-last-command quirk documented in `collect-fleet-health.sh`'s header) that a syntax
check alone would never have caught.

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
