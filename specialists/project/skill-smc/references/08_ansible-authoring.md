# SMC Ansible Authoring

## Contents

- [9. Ansible Authoring Workflows](#9-ansible-authoring-workflows)
- [tmpfs relocations need `tmpfiles.d`, not just a `file:` task (2026-07-28)](#tmpfs-relocations-need-tmpfilesd-not-just-a-file-task-2026-07-28)
- [Reclaiming state that a role's own tooling can't see (`smc_system` journal reclaim, 2026-07-28)](#reclaiming-state-that-a-roles-own-tooling-cant-see-smc_system-journal-reclaim-2026-07-28)
- [Narrowing tags: ask what the tag EXCLUDES (2026-07-28)](#narrowing-tags-ask-what-the-tag-excludes-2026-07-28)
- [`smc_network` VRF template requires netplan ≥ 0.106 — the whole fleet runs 0.104 (2026-08-25)](#smc_network-vrf-template-requires-netplan-0106-the-whole-fleet-runs-0104-2026-08-25)
- [`smc_rsyslog`'s squid stop fails on squid's own drain window — fixed 2026-08-26](#smc_rsyslogs-squid-stop-fails-on-squids-own-drain-window-fixed-2026-08-26)
- [Guarded pre-split syslog reclaim in `smc_rsyslog` (added 2026-08-26)](#guarded-pre-split-syslog-reclaim-in-smc_rsyslog-added-2026-08-26)
- Operational learning capture
- Task key order (`when:` last, `tags:` after it) — and why ansible-lint disagrees
- Code notes: RULE-006 split, note provenance, and what survives a branch switch
- Flavor/cluster conditional branching (selector reference)
- smc_ltp sub-group (CNMaestro backhaul provisioning + DNS architecture switch)
- "Low touch" onboarding method and site deployment history
- IPv6 disable policy
- Skill runtime paths
- Canonical source rules
- Topology change workflow
- Variable rename / refactor workflow
- Cache coherence rules
- Inventory path convention
- Cross-branch file fetch tool
- Playbook run safety
- Validation command reference

## 9. Ansible Authoring Workflows

### Operational Learning Capture (Mandatory)

For any SMC incident/debug fix in `ansible-wifi` that changes behavior, defaults, or troubleshooting assumptions:

1. Update the relevant focused reference in this specialist pack during the same work session.
2. Add a short entry under troubleshooting/failure-mode sections with:
   - exact error signature
   - root cause class
   - source-of-truth file path(s)
   - fix pattern
   - validation command(s)
3. Treat the reference update as part of done criteria for the task, not optional follow-up.

### Task key order: `when:` goes LAST, with `tags:` after it (operator convention, 2026-08-27)

**House convention for every task written in `ansible-wifi`.** Put `when:` at the **end** of the task, and where a task also carries `tags:`, `tags:` follows `when:`.

```yaml
- name: Deploy auth.log volume-reduction rsyslog filter
  copy:
    src: 11-auth-volume.conf
    dest: /etc/rsyslog.d/11-auth-volume.conf
    mode: '0644'
  notify: Restart rsyslog service
  when:
    - hotspot_flavor == 'rcp'
  tags:
    - rsyslog
```

Applies to nested tasks inside a `block:` exactly as it does at the top level — a `block` task reads `['name', 'block', 'when']`.

**`ansible-lint`'s `key-order` rule disagrees and that is expected.** It wants `when` *before* `block` (`"You can improve the task key order to: when, block"`). The house convention wins; the rule
fires consistently against both new and pre-existing tasks, so its findings here carry no signal. As at 2026-08-27 it reported 16 pre-existing vs 3 newly-written findings across `smc_system` +
`smc_asterisk` — i.e. the existing code already follows the house style, not the linter.

**That silencing has since been done, 2026-08-27.** A `.ansible-lint` now carries `key-order[task]` in `skip_list`, scoped to the `[task]` subrule so `key-order[play]` still fires. Verified precise:
`key-order[task]` drops to 0 while 77 `fqcn`, 34 `yaml[indentation]` and 6 comment findings all still report. The rule had been firing **94 times across 42 role files**, so it disagreed with
essentially every task in the repo rather than with a few stragglers.

**Consequence worth knowing before relying on it:** `.ansible-lint` and `CONVENTIONS.md` are both governance *symlinks*, so the convention and its enforcement are **operator-local**. A colleague
cloning `ansible-wifi` gets neither — they still see all 94 findings and no written convention. If it should bind the team, both must become real tracked files in the company repo.

**Reordering an existing task is riskier than it looks — three traps hit on 2026-08-27:**

1. **A `when:` can be an inline scalar or a block.** `when: (expr)` on one line and `when:` followed by an indented list are both valid, and a mover written for one silently skips the other.
2. **Never locate the insertion point with a naive first-match.** Searching the whole file for the next ` when:` matched an *unrelated task 370 lines earlier*, which moved a guard into a `debug:` task
   referencing an undefined variable while the task that needed it silently lost its `when:` entirely — turning a run-once guard into an every-run action. Anchor structurally: find the task, then the
   end of *its* block.
3. **Gate the edit on data-equality, not on "it still parses".** Compare `yaml.safe_load` before and after: a key reorder must be `IDENTICAL`. That comparison is what caught trap 2 — the file parsed
   fine both times and `--syntax-check` passed while a guard was missing.

Related: comments in this repo follow `skill-ccn` (Code Context Notes) — see the operator convention note under Canonical Source Rules.

### Flavor/Cluster Conditional Branching (Selector Reference — 2026-08-03)

**No role branches on cluster identity (`cw`/`community`/`communitywifi`/`apn`) directly.** Every flavor-conditional found repo-wide keys off one of two variables, both derived from the inventory
folder name:

- `hotspot_flavor` — hardware-class selector, groups `{rct, wh, nbn_wh}` as "big box" (overlayroot + GPS + telemetry) vs `{rcp, nbn_accelerate}` as "small box". This spans **both** clusters — it is a
  hardware split, not a cluster split. Used in `roles/smc_teleport/templates/teleport.yaml.j2` and `roles/smc_system/tasks/main.yml`.
- `inventory_dir.split('/')|last` — exact flavor name (`rcp`, `rct`, `wh`, `apn`, `cw`, `nbn_accelerate`, `nbn_wh`). Used for flavor-exclusive role gates.

**Confirmed flavor-exclusive gates (not hardware-driven):**

| Gate                                           | Condition                                                                                      | Effect                                             |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `smc_bases.yml` ClamAV + Lynis | `inventory_dir.split('/') | last == 'nbn_accelerate'` | Security hardening applied only on cw-cluster's |
|  |  |  |   small-box flavor — no apn-cluster equivalent |
|  |  |  |   (`rcp` does not get this). **Live-confirmed at** |
|  |  |  |   **full fleet scale 2026-08-03** (26/26 reachable |
|  |  |  |   `nbn_accelerate` hosts): both packages installed |
|  |  |  |   on every host, all uniformly |
|  |  |  |   `clamav 0.103.11`/`.12`. **Root cause** |
|  |  |  |   **confirmed 2026-08-03**: ClamAV 0.103.x reached |
|  |  |  |   end-of-life for database updates on 2025-09-14, |
|  |  |  |   and its CDN now hard-blocks `freshclam` from any |
|  |  |  |   0.103.x client (HTTP 403) — every host is |
|  |  |  |   affected, fix is a version upgrade, not a retry. |
|  |  |  |   See `13_known-issues.md` "Known Operational Bugs |
|  |  |  |   (NBN Accelerate cluster)" for full detail. |
| `smc_rise_deploy.yml` RISE/overlayroot rollout | `inventory_dir.split('/') | last in ['rct', 'wh', 'nbn_wh']` | `nbn_wh` is explicitly a RISE-rollout target |
|  |  |  |   alongside `rct`/`wh` — the mechanism that |
|  |  |  |   (eventually) enables overlayroot on RPi-class |
|  |  |  |   flavors. **Live-confirmed 2026-08-03**: |
|  |  |  |   overlayroot is NOT YET active on either `nbn_wh` |
|  |  |  |   host — operator confirmed this is a |
|  |  |  |   planned-but-not-yet-executed rollout, not a |
|  |  |  |   stalled deployment or code gap. |
|  |  |  |   `nbn_accelerate`/`rcp` are never targeted (they |
|  |  |  |   don't use overlayroot at all — bare ext4, per |
|  |  |  |   `07_hardware-overlay.md`'s "Read-Only Migration |
|  |  |  |   Status" table). |
| `smc_bases.yml` VoIP (Asterisk) | `inventory_dir.split('/') | last == 'rcp'` | Asterisk + firewall rules (SIP 5060, RTP |
|  |  |  |   10000-20000, Cambium TFTP 69) — apn-cluster |
|  |  |  |   exclusive, never applied on |
|  |  |  |   `nbn_accelerate`/`nbn_wh` |
| `smc_qos` role | `inventory_dir.split('/') | last == 'rct'` | QoS role exists but silently no-ops on |
|  |  |  |   `rcp`/`nbn_accelerate`/`wh` — see |
|  |  |  |   `13_known-issues.md` |
| `smc_ltp` sub-group (CNMaestro backhaul + DNS  | `'smc_ltp' in group_names`; group membership from `inventories/rcp/prod` (static INI), vars    | `rcp`-only (apn-cluster), no cw-cluster equivalent |
|   switch — see below)                          |   from `inventories/rcp/group_vars/smc_ltp.yml`                                                |                                                    |

**`smc_autossh` cluster/Teleport-endpoint selection.** `roles/smc_autossh/tasks/main.yml` copies pem/key files from `roles/smc_autossh/files/{{ teleport_fqdn }}/...`. `teleport_fqdn` is set in
`smc_bases.yml` from the per-inventory group_var `smc_bases_teleport_fqdn` (`inventories/{rcp,rct,wh}/group_vars/smc_bases.yml` → `teleport.apn.au`;
`inventories/{nbn_accelerate,nbn_wh}/group_vars/smc_bases.yml` → `teleport.communitywifi.net.au`). Individual hosts can override further (e.g. a host_var pointing at `teleport.apntest.au` or
`telestage.communitywifi.net.au` for staging). This is a **pure SSH-endpoint selection** — nothing else in the `smc_autossh` role, or in `smc_graylog`/`teleport_core`/`jenkins_core`, branches on
cluster identity; only the *values* (graylog server URL, teleport fqdn, jenkins fqdn) differ via group_vars, following the identical pattern on both clusters.

**When authoring a new cw-cluster-specific task**, follow the same `inventory_dir.split('/')|last == '<flavor>'` pattern as the ClamAV/Lynis and VoIP gates above — do not introduce a new
`cw`/`community` string check, since no existing code does that and it would be an inconsistent selector. See `01_overview.md` "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" for the
full cross-cluster comparison this section supports.

---

### smc_ltp Sub-Group — CNMaestro Backhaul Provisioning + DNS Architecture Switch (documented 2026-08-03)

Previously under-explored: earlier passes only captured `smc_ltp`'s DNS-gating side effect (see `02_service-map.md`) and mislabeled it as "cnMaestro mDNS" in the summary tables above. It is not
mDNS-related at all. Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`, `roles/smc_cnmaestro_provisioning/`, and `roles/smc_dns_mgmt/tasks/main.yml` gives
the full picture:

**Membership.** `smc_ltp` is a **static** Ansible group defined in `inventories/rcp/prod` (INI inventory — not generated by `topology_vars.py`, so it will not show up in a `topology_vars/*.yml`
review). 7 `rcp` sites are members, each via a per-site `<site>_smc_ltp` child group: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona`. `rcp`-exclusive — no
other flavor (`apn`, `rct`, `wh`, `cw`, `nbn_accelerate`, `nbn_wh`) defines an `smc_ltp` group or any `smc_ltp_*` var. **Corrected 2026-08-03 (same day, twice)**: first found 4 members from direct
`inventories/rcp/prod` read; operator then confirmed the group is meant to track every "low touch" onboarding site (see below) and directed adding the 3 that were missing (`warburton`, `beagle-bay`,
`umoona`) — a real inventory gap, not a re-read miss. Verified via `ansible-inventory -i inventories/rcp/prod --playbook-dir . --list` (`smc_ltp:children` lists all 7) and `ansible-playbook -i
inventories/rcp/prod --syntax-check smc_ltp.yml` (clean). File-level Ansible inventory change, uncommitted as of this edit — not yet run against any live SMC; adding a host here makes it *eligible*
for the `dns_mgmt` play and `smc_ltp.yml` on the next real run, it does not trigger anything itself.

**Purpose 1 — CNMaestro wireless backhaul/CPE provisioning.** A standalone top-level playbook, `smc_ltp.yml` (separate entry point from `smc_bases.yml`), targets `hosts: smc_ltp` and runs the
`smc_cnmaestro_provisioning` role (`roles/smc_cnmaestro_provisioning/files/cnmaestro-provisioning.py`) against `smc_ltp_cnmaestro_provisioning` (defined in `inventories/rcp/group_vars/smc_ltp.yml`).
This auto-provisions Cambium wireless equipment via the CNMaestro cloud API: cnPilot r195P (home CPE), XV2-2T0/XV2-22H (indoor/outdoor enterprise AP), ePMP Force 300-16/300-25 (SM/AP backhaul radios,
incl. EP2P mode), and ePMP 3000L — auto-allocating management/provisioning IP ranges (`10.255.x.x`, `192.168.254.x`, `10.0.x.x`), SSID prefixes (`WifiBridge_`, `WifiP2P_`), and per-model config
templates. Some LTP hosts override branding at the host level (e.g. `whprov-smc01.yml` uses `WHProv`-prefixed SSIDs instead of the group default). `smc_bases_teleport`/iptables plays in
`smc_bases.yml` also reference `smc_ltp_cnmaestro_address|default('')` as a harmless empty default on non-LTP hosts — this is not evidence LTP applies fleet-wide, just a shared var namespace.

**Purpose 2 — DNS resolver architecture switch.** `smc_bases.yml`'s `dns_mgmt` play (`hosts: smc_ltp`) runs `smc_dns_mgmt`, which stops+masks `unbound` if it holds port 53, installs `bind9`, and
deploys `named.conf.local` + an RPZ zone file **literally named `db.cambium-rpz`** — the filename itself ties this DNS switch directly to the Cambium wireless-backhaul context above, most likely so
the private management/provisioning IP ranges used by the ePMP/cnPilot mesh (which will never resolve via public DNS) get a local zone. This *replaces* the unbound+stubby DNS-over-TLS setup every
other host gets — see `02_service-map.md` for the full DNS-resolver comparison.

**`smc_dhcpd` LTP-specific fix.** `roles/smc_dhcpd/tasks/ubuntu.yml` has an apparmor-profile-removal + service-user block gated `when: "'smc_ltp' in group_names"` — runs `isc-dhcp-server` as root
instead of the default `dhcpd` user on LTP hosts, unrelated to the DNS or CNMaestro purposes above.

**Open question — the acronym.** "LTP" is not expanded anywhere in the codebase (no comment, no README, no commit message found). Functional purpose is well-evidenced from code; the literal meaning of
the letters is not — do not guess/state one as fact without an operator confirmation.

---

### "Low Touch" Onboarding Method and Site Deployment History (operator-confirmed 2026-08-03)

**Not previously documented anywhere in this pack.** Operator supplied install dates for a specific cohort of `rcp` sites, confirming these were deployed via a named **"low touch" onboarding method**:

| Site          | Install date                                                                                  | `smc_ltp` member?                 |
| ------------- | --------------------------------------------------------------------------------------------- | --------------------------------- |
| **guda-guda** | **2025-04-15 — pilot site**, a full year before the next low-touch site                       | Yes                               |
| Horn Island   | 2025-11-23 (not low-touch — predates the method's next use, listed for timeline context only) | No                                |
| Umoona        | 2026-04-12                                                                                    | Yes (added 2026-08-03, see below) |
| Warburton     | 2026-05-02                                                                                    | Yes (added 2026-08-03, see below) |
| Beagle Bay    | 2026-05-12                                                                                    | Yes (added 2026-08-03, see below) |
| Pandanus Park | 2026-06-17                                                                                    | Yes                               |
| Old Looma     | 2026-07-16                                                                                    | Yes                               |
| New Looma     | 2026-07-25                                                                                    | Yes                               |

**Resolved 2026-08-03 (link confirmed, not coincidental).** Initially only 4 of the 7 low-touch sites showed up in `smc_ltp` (`guda-guda`, `pandanus-park`, `old-looma`, `new-looma`);
`umoona`/`warburton`/ `beagle-bay` were flagged as a possible-but-unconfirmed correlation. Operator confirmed directly: every low-touch site is meant to be an `smc_ltp` member, and the 3 missing ones
were a plain inventory gap — not a coincidental overlap of two unrelated rollout decisions. Fixed by adding `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` child groups to
`inventories/rcp/prod`'s `smc_ltp:children` block, operator-directed. **Mechanism confirmed 2026-08-03 (same day, third correction): it's a manual step someone has to remember** — low-touch onboarding
tooling does not itself assign `smc_ltp` group membership; a human has to add the site to `inventories/rcp/prod` separately, with no automated check that it happened. This directly explains how 3 of 7
sites ended up missing in the first place — a manual, un-enforced step is exactly the kind of thing that silently drops during a busy onboarding. **Operational implication:** when a new low-touch site
is onboarded, adding it to `smc_ltp:children` is not automatic — confirm it explicitly (e.g. `ansible-inventory -i inventories/rcp/prod --list | grep -A1 smc_ltp`) rather than assuming low-touch
deployment alone guarantees group membership.

**What "low touch" means in Ansible code terms: currently nothing.** Repo-wide grep for `low_touch`/`low-touch` in `ansible-wifi` finds exactly one hit: `smc_bases_low_touch_provisioning: true` in
`inventories/rcp/host_vars/pierre-rcp01.yml` — and **no role or playbook anywhere reads that variable**. It is a set-but-never-consumed host_var. **Do not conflate this with the operator's "low touch"
onboarding method above** — `pierre-rcp01` is not in the low-touch site cohort the operator described, and the var's naming proximity is likely coincidental (or a vestige of an earlier/different,
possibly not-yet-implemented automation attempt) rather than evidence the method is Ansible-encoded. The actual "low touch" method, whatever it consists of operationally, currently leaves no trace in
Ansible logic that this pack has found — it is an operational/process distinction, not (yet) a code path.

**Confidence / evidence basis:** site list and dates are operator-provided, cross-referenced against independently-observed netplan/hook render timestamps in the routing-issue investigation (which
land 1-92 days after each site's operator-given install date — consistent with "installed then later touched by unrelated remediation work", not a contradiction). The `smc_ltp`-overlap observation and
the orphaned `smc_bases_low_touch_provisioning` var are this session's own direct-grep findings. See `13_known-issues.md` for the now-resolved history of this correlation (initially flagged as
unconfirmed, then operator-confirmed and fixed same day).

---

### Isolated jinja2 Testing Is Not Proof of Ansible's Real Templating Behavior (`regex_replace` backreferences — 2026-07-29)

**The rule:** for any `regex_replace` (or similarly escaping-heavy filter) that uses a backreference (`\1`), do not trust an isolated `jinja2.Environment().from_string()` test as proof the same
expression will behave identically inside `ansible-playbook`. Only a real `ansible-playbook --check --diff -v` against a live host counts as validation for escape-sensitive template expressions.

**How it bit us:** `roles/smc_network/tasks/ubuntu.yml` needed a filter to build the list of expected `dhclient.<name>.conf` filenames from `interfaces|dict2items`, for a find/delete-extraneous
cleanup pass (routing-issue investigation, `apn/routing-issue/docs/smc-network-idempotency-gap-20260729_1958.md`). Two attempts, both validated in isolation, both wrong in a real run:

1. `map('regex_replace', '^(.*)$', 'dhclient.\1.conf')` — single backslash. Isolated testing caught that Jinja2's string-literal lexer converts `\1` to an octal escape (`chr(1)`) before the regex
   engine ever runs — clearly broken, not the interesting failure.
2. `'dhclient.\\1.conf'` — double backslash "fix". Re-tested in isolation with the same `jinja2.Environment()` harness, using the exact same interpreter Ansible itself uses, and got the correct
   filenames. Declared fixed. **It was not.** A real `ansible-playbook --check --diff -v` against a live Pandanus Park box showed `dhclient_conf_keep` resolving to eight copies of the literal,
   un-substituted string `dhclient.\1.conf` — Ansible's actual Jinja/regex_replace evaluation differs from what an isolated `jinja2.Environment()` test shows for identical source text. Had this
   shipped, the delete task (`when: item.path|basename not in dhclient_conf_keep`) would have matched and deleted **all 16 files, including all 8 real, currently-active interfaces** (`enp1s0`,
   `enp2s0`, `vlan521/522/531/532/621/631`) — confirmed via the `--diff` output, not inferred.

**Fix:** avoid the escaping question entirely — rebuild as a task-level loop with `~` string concatenation instead of `regex_replace`:
```yaml
- name: Determine expected /etc/dhcp/dhclient.<interface>.conf filenames
  set_fact:
    dhclient_conf_keep: "{{ dhclient_conf_keep + ['dhclient.' ~ item.value.name ~ '.conf'] }}"
  when: item.value.role|default('none') in ['internet', 'starlink']
  loop: "{{ interfaces|dict2items }}"
```
`~` concatenation has no escaping layer to get wrong — there is no backslash for any templating pass to reinterpret. Re-ran the identical live `--check --diff` and confirmed `dhclient_conf_keep` built
up to exactly the real interface filenames, correctly sparing them while flagging only the genuine orphans.

**General lesson:** "I tested the Jinja2 expression in isolation and it produced the right string" is not validation for anything involving backslash escaping — Ansible's own templating layer (env
markers, `AnsibleUnsafeText`, filter plugin wrapping) can diverge from vanilla `jinja2.Environment()` behavior for the same source text. Prefer concatenation (`~`) or list-building filters over
`regex_replace` backreferences wherever a simpler construct can do the same job — and when a backreference is unavoidable, validate it live before trusting it.

**The architectural gap underneath this bug, worth stating on its own:** one templated artifact being self-cleaning does not imply a sibling artifact rendered by the same role is too — each generated
file's lifecycle has to be audited independently. `roles/smc_network/tasks/ubuntu.yml` already had a correct find/delete-extraneous pattern for netplan (`00-ansible.yaml` is a single fully-overwritten
file, plus an explicit find+delete pass for any other stray `.yaml`), so it looked idempotent. But the *separate* per-interface `dhclient.<name>.conf` files it also renders (one `copy` task per
interface, gated on `role == 'internet'`/`'starlink'`) had no equivalent cleanup anywhere in the role — proven live, files over a year stale on every affected site. Before assuming a role is
idempotent on removal because you've verified one of its outputs, check every distinct file/artifact it templates separately; `grep` for every `copy`/`template` task in the role and ask "what deletes
this when its `when:` condition stops matching" for each one individually. (Currently low-stakes here specifically: `dhclient@<iface>.service` is only ever instantiated by `networkd-dispatcher` when
the netplan device is real, so an orphaned conf file with no matching interface is inert clutter today — see `03_communication-flows.md` — but the gap itself is the kind of thing that makes future "is
this file real?" audits unreliable, independent of whether it's currently harmful.)

**Topology-cloning risk — confirmed live, not hypothetical.** When a new site's `topology_vars/<site>.yml` is authored by copying an existing site's file as a starting point, the VLAN IDs (or other
per-site values) can be left uncorrected and this survives `yamllint`/`ansible-lint`/`ansible-playbook --syntax-check` silently — none of those check that IDs are semantically correct for the site,
only that the YAML is well-formed. Pandanus Park's `topology_vars` file was confirmed byte-identical to Umoona's (except hostname) going back to before the currently-deployed commit, with wrong
`vlanid` values that went undetected for roughly five weeks after install. Live MAC forensics (the deterministic-seed technique in `03_communication-flows.md`) is what caught it, not any validation
step in the normal authoring workflow. When authoring a new site by cloning an existing one's topology file, diff every `vlanid`/interface-key value against the site's real cabling documentation
before committing — do not trust that lint passing means the values are right for the new site.

**Mandatory pre-check: verify physical interface names against the live box, not just VLAN IDs — before any topology_vars edit or any Ansible run touching a site's interfaces.** Confirmed live at New
Looma (2026-07-30): `topology_vars/new-looma.yml`'s `internet01`/`internet02` were named `eno1`/`enp3s0`, and `switch01`/`switch02` were named `enp2s0`/`enp1s0` — a complete cross-wiring, not just
wrong VLAN IDs. `eno1` doesn't exist on this box's hardware at all; it's the naming convention of a **different SMC model** (BOXER-6641, e.g. Old Looma) than the one actually deployed here
(BOXER-6404, same class as Umoona/Pandanus Park, real NICs `enp1s0`-`enp4s0`). Meanwhile the box's two real, currently-leased WAN NICs (`enp1s0`, `enp2s0`) were assigned to `switch01`/`switch02` (the
LAN trunk role) instead of `internet01`/`internet02` — silently swapping which physical port the WAN role and the LAN-trunk role point to. This survived `yamllint`/`ansible-lint`/ `--syntax-check`
exactly like the vlanid-cloning bug above, for the same reason: none of those tools know what hardware model a site actually runs, only that the YAML is well-formed.

**Do this before touching any site's topology_vars, or before running any playbook against a site whose topology_vars provenance is uncertain:**
```bash
tsh ssh root@<site>-smc01 'dmidecode -s system-product-name'          # which SMC model — determines the real NIC naming scheme
tsh ssh root@<site>-smc01 "grep -E '^\s+(enp|eno|eth)[a-z0-9]*:' /etc/netplan/00-ansible.yaml"   # the box's actual physical interface names
tsh ssh root@<site>-smc01 'systemctl list-units "dhclient@*" --all'    # which of those names are actually active WAN NICs right now
```
Cross-check the model against a known-good site of the same model (this fleet has at least two: BOXER-6404 uses `enp1s0`/`enp2s0` for WAN and `enp3s0`/`enp4s0` for the LAN trunk, confirmed at
Umoona/Pandanus Park; BOXER-6641 uses `eno1`/`enp3s0` for WAN, confirmed at Old Looma) — do not assume a `topology_vars` file's existing physical interface names are correct for the box just because
the file parses and the site is currently "working" (New Looma's case shows a box can partially route traffic — 3 of 12 real interfaces were live — while this exact bug sits uncorrected). Full
writeup: `issues/apn/routing-issue/docs/backup-vlan-trunk-fixed-and-new-looma-online-20260730_1520.md` in the local-knowledge repo (§ New Looma reconstruction, once committed).

**A third distinct topology_vars authoring bug class, confirmed at rocket-bore-smc01 (2026-07-28) — role mistagging, not naming or cloning.** Both the `switch` interface and `internet02` were tagged
`role: internet` in this site's `topology_vars` — producing redundant routing tables for what should be one LAN-trunk interface and one WAN interface with distinct roles. Same underlying netplan 0.104
`vrf:`-key-unsupported regression as the family-friendly-smc01/BOXER6404 case applied here too; yimidarra-smc01 was used to confirm a VRF-less topology works as the fallback while the netplan-version
fix is pending. This is a third failure mode alongside vlanid-cloning and physical-interface-naming above — `role:` values themselves can be wrong even when interface names and VLAN IDs are correct,
and none of `yamllint`/`ansible-lint`/`--syntax-check` catch it either. When auditing a site's topology_vars, check all three independently: VLAN IDs, physical interface names against live hardware,
and `role:` assignment per interface.

**Handler-name reuse across different `listen` topics is safe, not a collision risk.** Ansible matches handlers by their `listen` topic, not by uniqueness of `name` — `smc_network`'s handler file
reuses the same four handler names (`Schedule a Teleport service restart in 2 minutes`, `Ensure we have an operational ssh connection`, `Delete Teleport service restart job`, etc.) across four
different protected-restart `listen` blocks, and `smc_application`'s ported copy of the same pattern reuses them a fifth time in a different role entirely. If you see the same handler `name` appear
multiple times across a role's handler file or across roles, that's this codebase's established convention for the protected-restart pattern, not a bug to fix.

---

### SSH Cipher Negotiation Fix Location (smc_sshd role — 2026-06-10, corrected 2026-06-24)

**Symptom:** a remote host (SSL cert copy target) was hardened to modern-only SSH ciphers (`chacha20-poly1305`, `aes256-gcm`, `aes128-gcm`) and the SMC's SSH client didn't propose any of them by
default, breaking `sslcertcopy.sh`'s cert-copy step; a `basename` call further down the script also crashed once the connection itself started failing.

**First-attempt fix (2026-06-10) put the cipher flags in the wrong place** — added directly to `roles/smc_url_capture/files/sslcertcopy.sh` and `templates/sslcertcopy.sh.j2` as explicit `-c
<cipher-list>` flags, plus a guard around the `basename` crash. This worked for that one script but only that one script.

**Corrected fix (2026-06-24):** reverted the per-script patches and moved the cipher preference into `smc_sshd`'s `ssh_config` template instead — prepending the modern cipher list at the client-config
level applies to every SSH client call the box makes, not just this one script. If another role/script hits the same "modern-cipher-only remote host" failure in the future, check `smc_sshd`'s
`ssh_config` template first rather than re-patching the calling script.

### Tag Hazard: destroy/recreate blocks must carry their repair tasks (2026-07-28)

**The rule:** if a tagged block *destroys and recreates* state, every task that repairs permissions, ownership, or content on that recreated state must carry the **same tag**. Otherwise the
tag-limited run is guaranteed broken while the full untagged run stays correct — so the defect is invisible in normal use and only fires when someone runs the tag.

**How it bit us:** `roles/smc_application/tasks/main.yml` has a `tags: wifi_dev_repo` block that does `file: path=/var/www/html/wifi state=absent` then re-clones the portal repo. Git recreates
`application/cache` and `application/logs` at `0755 root:root` (both are tracked only via a `.gitignore` stub, so umask 022 applies). The tasks that chmod them to `0777` sat in a **separate untagged
block**. Result: a `--tags wifi_dev_repo` run on 2026-07-21 left the captive portal dead on 10 of 16 `rcp` sites for 7 days. See `06_failure-modes.md` and `10_captive-portal.md` §11.8.

**Non-obvious detail — tag the `stat` too.** The perms block is gated by `when: wifi_stat.stat.exists`, and `wifi_stat` is registered by a preceding `stat` task. Tagging only the block makes a
tag-limited run evaluate `when` against an **undefined variable** and fail. Both must carry the tag, or neither works.

**Safe by construction:** adding a tag never removes a task from untagged full runs (untagged runs execute everything), so this class of fix is purely additive — there is no full-run behaviour change
to regression-test.

**Audit pattern** — look for a tagged block containing `state: absent` / `git:` / `unarchive:` and check what fixes up the result:
```bash
grep -n "clear old\|state: absent\|tags:" roles/<role>/tasks/main.yml
ansible-playbook -i <inv> <playbook> --tags <tag> --list-tasks   # does the repair task appear?
```

`--list-tasks` under the tag is the authoritative check — it shows exactly what a tag-limited run would execute. Surveyed `smc_application`'s other destroy/reclone blocks
(`wifi_community_app_backend_git`, `telemetry_git`): both untagged, so not vulnerable. The pattern is not role-specific — worth checking elsewhere.

### apt-daily Timer Mask (smc_system role — 2026-07-15)

**Change:** Added a task to `roles/smc_system/tasks/main.yml`, in the same block as the existing `unattended-upgrades` disable, stopping/disabling/masking `apt-daily.timer` and
`apt-daily-upgrade.timer`:
```yaml
- name: Stop and mask apt-daily timers (prevents periodic apt/dpkg lock contention)
  systemd:
    name: "{{ item }}"
    state: stopped
    enabled: no
    masked: yes
  loop:
    - apt-daily.timer
    - apt-daily-upgrade.timer
```

**Why:** the pre-existing `APT::Periodic::Update-Package-Lists`/`Unattended-Upgrade` = `"0"` task (same block) only gates *what* `apt.systemd.daily` does once it fires — the timers still fire on their
own schedule and still take the apt/dpkg lock for an update+cleanup pass regardless. Root cause of transient `apt-get clean failed` collisions during concurrent Ansible runs (found during the
smc-file-writing-analysis fleet rollout, 2026-07-14 — 3 collisions: jigalong ×2, bidyadanga ×1, each failing early in the play before reaching any target task, no partial state, clean on retry). Also
a real contributor to ongoing write volume: `gpgv` (apt package-list signature verification, triggered by this same timer) was found to be the dominant `fatrace` writer on most rcp nodes *after* the
status.json/graylog-sidecar/journald fixes were rolled out — not the `apt_info.py` textfile collector, as the write path (`/tmp/apt.data.*`) initially suggested. Confirmed by checking `fatrace`'s
`top_proc` output, not just `top_path` — a temp file's path alone doesn't tell you which process is writing it.

**Gotcha — `masked`, not just `stopped`/`disabled`:** a stopped-and-disabled (but unmasked) timer can still be re-triggered by another unit's dependency chain. Mask it so it can't fire at all.

**Applies to:** All Ubuntu SMC flavors (rcp, rct, wh) via `when: os_distribution == 'Ubuntu'` — same `smc_system` role, shared across flavors via `smc_bases.yml`. Deployed live to all 12/12 rcp nodes
(2026-07-15, ansible-wifi commit `0c51cb1`); **not yet rolled to rct/wh** — same gap exists there too, but that's outside the smc-file-writing-analysis project's scope. Worth flagging to whoever owns
that flavor.

**Validation:**
```bash
tsh ssh root@<node> 'systemctl is-enabled apt-daily.timer apt-daily-upgrade.timer'
# Expect: masked / masked
```

---

### apt_info.py cache.update() Removal (smc_node_exporter role — 2026-07-15)

**Change:** Removed the upstream default `cache.update()` call from `roles/smc_node_exporter/files/apt_info.py` (the node_exporter textfile-collector script, cron `*/5 * * * *`). The script now just
does `cache = apt.cache.Cache(); cache.open()`, no update.

**Why:** `cache.update()` on every 5-min cron tick is a full `apt update` — network fetch + `gpgv` Release-signature verification against every configured repo, 288×/day. This is the actual root cause
of persistent `gpgv`/`/tmp/apt.data.*` writes, independent of and untouched by the apt-daily-timer mask above (it's not the same trigger — it's this script's own `cache.update()` call). That call is
also what fires `20apt-esm-hook.conf`'s `APT::Update::Pre-Invoke` hook, starting `apt-news.service`+`esm-cache.service` (see next entry) as a *side effect* — do not assume masking those two services
fixes the gpgv writes; it doesn't, this does. Confirmed safe: the script's own comment already tolerated `cache.update()` failing (`contextlib.suppress(LockFailedException, FetchFailedException)`,
falling back to the existing index) — a "packages pending upgrade" gauge doesn't need a live network refresh every 5 min, especially once the apt-daily timer (which used to do a real daily refresh) is
masked anyway.

**Applies to:** rcp only (deployed). Not yet checked on rct/wh — likely the same gap if they run this same textfile-collector script.

**Validation:**
```bash
tsh ssh root@<node> 'grep -c "^import contextlib" /usr/local/lib/apt_info.py; grep -c "^\s*cache\.update()" /usr/local/lib/apt_info.py'
# Expect: 0 / 0
tsh ssh root@<node> 'python3 /usr/local/lib/apt_info.py | head -3'
# Expect: valid Prometheus output, exit 0
```

---

### `/tmp` + `textfile_collector` → Size-Capped tmpfs (smc_system + smc_node_exporter roles — 2026-07-15)

**Change:** `smc_system` mounts `/tmp` as tmpfs, size-capped at 512M (not systemd's 50%-of-RAM default). `smc_node_exporter` mounts `/var/lib/node_exporter/textfile_collector/` as its own 16M tmpfs.

**Why:** on rcp (no overlayroot yet), `/tmp` is real lower-disk — confirmed via `findmnt`.
Size-capped deliberately: without a cap, a runaway write trades today's contained failure mode (disk full, `ENOSPC`) for **RAM exhaustion / OOM-killer picking an arbitrary victim process** on these
  4-8GB boxes — a materially worse outcome. `textfile_collector` content is fully regenerated by its own collector script every cron tick, same accepted-loss-on-reboot tradeoff already used for
  `/var/lib/fluent-bit/pos` (smc_graylog, see below).

**Gotcha 1 — `tmp.mount` isn't loadable out of the box.** Ubuntu/Debian ship `tmp.mount` only as a *reference template* at `/usr/share/systemd/tmp.mount`, not in the actual unit search path
(`LoadState=not-found` confirmed live until fixed). It must be symlinked in first:
```yaml
- name: Symlink tmp.mount unit from the systemd-shipped reference template
  file:
    src: /usr/share/systemd/tmp.mount
    dest: /etc/systemd/system/tmp.mount
    state: link
```

**Gotcha 2 — first activation doesn't reliably pick up a same-run drop-in, and don't `state: restarted` unconditionally either.** Even after `daemon_reload`, the *first* `systemctl start tmp.mount`
right after symlinking it in used the base unit's default `size=50%` instead of a same-run drop-in override — a manual `systemctl restart tmp.mount` fixed it immediately after. The naive fix (`state:
restarted` on every run) breaks worse: restarting `tmp.mount` unmounts and remounts `/tmp`, which is also where **Ansible's own AnsiBallZ module payload for that very task is running from** — the
remount shadows the module's own working files mid-execution, so it reports `Module result deserialization failed: No start of json char found` on *every single run*, even though the underlying
`systemctl restart` genuinely succeeds every time (verified live: `/tmp` at the correct cap, `unattended-upgrades` masked, no other collateral damage). **Fix:** `state: started` (idempotent, no-op
once active) plus a `notify`-triggered handler that only fires when the drop-in content actually changes, dispatched fire-and-forget:
```yaml
# task
- name: Write tmp.mount size-cap override
  copy: {dest: /etc/systemd/system/tmp.mount.d/99-smc-size-cap.conf, content: "...", ...}
  notify: Restart tmp.mount
- name: Enable and start tmp.mount
  systemd: {name: tmp.mount, enabled: yes, state: started}
# handlers/main.yml
- name: Restart tmp.mount
  systemd: {name: tmp.mount, state: restarted}
  environment:
    TMPDIR: /var/tmp      # was async:15 + poll:0 until 2026-08-25 — see Gotcha 5
```
This class of bug (a task that restarts something Ansible's own execution depends on) will recur for any future unit that touches `/tmp` — remember it's not specific to `tmp.mount`.

**Superseded detail:** the `async: 15` + `poll: 0` fire-and-forget dispatch described above was the *original* fix for the handler's own broken result, and it held from 2026-07-15 until 2026-08-25. It
is no longer correct — it traded this task's broken result for a remount still in flight when the play ended, which then killed the *next* play. Gotcha 5 replaces it with the same `TMPDIR` pin Gotcha
3 applies to the task.

**Gotcha 3 — first-activation self-wipe of Ansible's own module payload (found 2026-07-23, new-looma onboarding).** On a node's *first* onboarding, the "Enable and start tmp.mount" task fatals with
`Module result deserialization failed: No start of json char found` → `FileNotFoundError: /tmp/ansible_systemd_payload_*.zip`. Cause: AnsiballZ self-extracts the module's payload honoring the **remote
shell's `TMPDIR`** (defaults to `/tmp`), which is *independent of* ansible's `remote_tmp` (set to `/var/tmp/${USER}/` in this repo's `ansible.cfg` — that governs module *args*, not the AnsiballZ
extraction dir). The moment the task activates `tmp.mount`, a fresh tmpfs is mounted over `/tmp`, wiping the payload the running module is executing from → it dies before it can return JSON. The
`Restart tmp.mount` handler still fires and the mount *does* end up active, so a blind re-run "works" (second pass finds `/tmp` already mounted, no re-wipe) — which is why this looked like a transient
error rather than a bug. **Fix (deployed 2026-07-23, `smc_system` role):** pin `TMPDIR` off `/tmp` for that one task so the payload survives the remount:
```yaml
- name: Enable and start tmp.mount (relocates /tmp to size-capped tmpfs)
  systemd: {name: tmp.mount, enabled: yes, state: started}
  environment:
    TMPDIR: /var/tmp
```
Note this is a *different* mechanism from `remote_tmp` — setting `remote_tmp` alone does **not** fix it, because AnsiballZ extraction follows `TMPDIR`. Same reasoning applies to any future task that
mounts over a directory Ansible might be staging into.

**Gotcha 4 — changing the `/tmp` size cap doesn't apply live on a busy node (found 2026-07-23, 512M→256M resize).** When you edit the `size=` in `99-smc-size-cap.conf` and redeploy, the `Restart
tmp.mount` handler fires and reports `changed`, but on a node whose `/tmp` is in use (systemd `PrivateTmp`, X11 sockets, any process with a cwd/open fd there) the **remount silently does not take** —
`systemctl restart tmp.mount` = stop+start, the stop can't unmount a busy filesystem, so systemd leaves the existing mount at the *old* size and the "start" is a no-op. The handler still shows
`changed` (systemd accepted the restart), so the recap looks successful while `findmnt -nb -o SIZE /tmp` still reports the old value. Observed live: only 2/15 nodes (the ones whose `/tmp` happened to
be unmountable at that instant) actually resized; the other 13 stayed at the old cap. **The drop-in config is correct, so it applies on next reboot** — but to apply it *live* without a reboot, remount
in place:
```bash
# per node (safe as long as current /tmp usage < the new cap):
mount -o remount,size=256M /tmp
findmnt -nb -o SIZE /tmp   # confirm it actually changed
```
`mount -o remount` changes the cap in place without unmounting, so it works on a busy `/tmp` where `systemctl restart` can't. **Growing** a tmpfs (e.g. fluent-bit/pos 64m→256m via the `mount` module)
has no such issue — that's already a plain remount and applies cleanly. Only **shrinking `/tmp`** hits this, and the remount must keep the cap above current usage. Consider adding an explicit `mount
-o remount` (or a reboot note) to the role if live-apply-on-resize is ever required rather than reboot-eventual.

**Gotcha 5 — the async handler leaked the remount into the NEXT play (found 2026-08-25, yakanarra-smc01 first install).** Same root cause as Gotcha 3, one play later. On a first install
`smc_bases.yml` runs the System play (activates `tmp.mount`, handler fires `Restart tmp.mount`), and the very next play — `Network` — fatals on its `setup` task:
```
FileNotFoundError: [Errno 2] No such file or directory:
  '/tmp/ansible_setup_payload_mng66ar0/ansible_setup_payload.zip'
MODULE FAILURE: No start of json char found
```
The System play itself reports clean (`ok=59 changed=16`), so the recap points at the Network play and the `smc_network` role, which are innocent. Cause: the handler was dispatched `async: 15` +
`poll: 0`, so Ansible did **not** wait for the remount. The play ended, `Network`'s `setup` module started unpacking its AnsiballZ payload into the *old* `/tmp`, and the in-flight remount swapped a
fresh empty tmpfs over it mid-import. Gotcha 3's `TMPDIR` pin did not cover this because it was applied only to the one `Enable and start tmp.mount` task, not to the handler and not to any later play.

Verified live on yakanarra-smc01 the same day: `findmnt /tmp` → `tmpfs size=262144k`, `ActiveEnterTimestamp` = the failing run's timestamp, `uptime` 6h50m (no reboot) — i.e. `/tmp` genuinely flipped
to tmpfs mid-play, exactly between the two plays.

**Fix (`roles/smc_system/handlers/main.yml`, 2026-08-25):** drop `async`/`poll` and pin the handler's own `TMPDIR` instead — the pin removes the reason async existed, and synchronous execution
guarantees the remount is finished before the play hands over.
```yaml
- name: Restart tmp.mount
  systemd:
    name: tmp.mount
    state: restarted
  environment:
    TMPDIR: /var/tmp
```
**Recognising it in the wild:** first install only (the handler fires on drop-in change, so a second run is clean and the whole thing looks transient — same trap as Gotcha 3). Nothing is left
half-configured: the System play completed, and every play from the failing one onward simply never ran, so a plain re-run of the same command finishes the host.

**Generalise:** whenever a task reconfigures a directory Ansible stages into, pin `TMPDIR` on **every** task and handler in that blast radius — not just the one that fatals. Fixing only the task that
visibly failed leaves the race one step downstream, which is exactly what happened between 2026-07-23 and 2026-08-25.

**Applies to:** rcp only (`hotspot_flavor == 'rcp'` gate) — rct/wh already get `/tmp` on tmpfs for free via overlayroot's upper dir, no change needed there.

### Making the size-capped tmpfs mounts visible to Prometheus (node_exporter, 2026-07-23)

node_exporter's filesystem collector **excludes tmpfs by default in this fleet** — the `smc_node_exporter` unit (`roles/smc_node_exporter/files/node_exporter.service`) shipped
`--collector.filesystem.fs-types-exclude=^(tmpfs|squashfs|nsfs|vboxsf)$`, so **none** of the four size-capped tmpfs mounts (`/tmp`, `/var/lib/prometheus`, `/var/lib/node_exporter/textfile_collector`,
`/var/lib/fluent-bit/pos`) produced `node_filesystem_*` series — a monitoring blind spot (a filling tmpfs, especially fbpos where "full" = log loss, would trip no alert).

**Fix: drop `tmpfs|` from the fs-types-exclude regex** (→ `^(squashfs|nsfs|vboxsf)$`). Do **not** use `--collector.filesystem.fs-types-include=tmpfs` — an `-include` acts as a whitelist and would make
tmpfs the *only* published fstype, dropping the real root-disk `/` metrics. Removing it from the exclude is the correct "include tmpfs" mechanism.

Why this is cleanly scoped (verified live on mornington, `findmnt -t tmpfs` = 9 mounts): the **existing** `--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|run)($|/)` already drops
`/dev/shm` and every `/run/*` tmpfs, so removing the fs-type exclusion surfaces **exactly** the four `/tmp`/`/var/...` mounts and nothing noisy (no `/dev/shm`, no `/run/*`, no PrivateTmp — those
aren't separate mounts in the host namespace). systemd note: **do not** add `#` comment lines inside the `\`-continued `ExecStart` block — systemd does not support comments mid-continuation and it
breaks unit parsing (keep the rationale in this doc instead).

Deploy: `smc_prometheus.yml --tags node_exporter` (copies the unit, restarts node_exporter — brief scrape gap only). Verified 2026-07-23 across 15/16 nodes (new-looma offline at the time): all four
mounts publish `node_filesystem_size_bytes{fstype="tmpfs"}` in central Prometheus; fbpos %-used reads 6–9%, matching live `findmnt`. Alert query: `100*(1 -
node_filesystem_avail_bytes{mountpoint="/var/lib/fluent-bit/pos"}/node_filesystem_size_bytes{mountpoint="/var/lib/fluent-bit/pos"})`, warn ~80%.

**Validation:**
```bash
tsh ssh root@<node> 'df -h /tmp /var/lib/node_exporter/textfile_collector'
# Expect: /tmp = 256M tmpfs (was 512M until 2026-07-23), textfile_collector = 16M tmpfs
tsh ssh root@<node> 'systemctl --failed'
# Expect: only the already-known masked-timer entries (they always show "failed" by design) --
# investigate anything else live before assuming it's related to this change.
```

### Prometheus TSDB tmpfs — first-install `stop` guard (smc_prometheus role — 2026-07-23)

**Symptom (fresh-node onboarding):** `smc_prometheus.yml` fatals at "Stop prometheus before relocating its data directory" with `Could not find the requested service prometheus`. The stop task exists
so an *already-running* prometheus releases its open handles into the old data dir before the tmpfs is mounted over `/var/lib/prometheus` (correct ordering on an upgrade). But on a **never-installed**
node the service doesn't exist yet and the `service` module fatals — and because the install task comes *after* the stop, a blind re-run fails at the same point every time (it never reaches the
install). This is the same "first-install ordering" class as the `tmp.mount` gotchas above.

**Fix (deployed 2026-07-23):** gather `service_facts` and guard the stop so it's skipped when the unit isn't present yet:
```yaml
- name: Gather service facts (guard the first-install stop below)
  service_facts:
  when: [ansible_distribution == 'Ubuntu', hotspot_flavor == 'rcp']

- name: Stop prometheus before relocating its data directory
  service: {name: prometheus, state: stopped}
  when:
    - ansible_distribution == 'Ubuntu'
    - hotspot_flavor == 'rcp'
    - "'prometheus.service' in ansible_facts.services"
```
Prefer the `service_facts` guard over `failed_when: false`/`ignore_errors` — the guard *skips* cleanly (no red error line), whereas suppression still prints an alarming trace and hides genuine
failures. General rule for onboarding playbooks: any "stop/restart X before reconfiguring it" task must tolerate X-not-yet-installed on first run.

---

### apt-news.service + esm-cache.service Mask (smc_system role — 2026-07-15)

**Change:** Masks `apt-news.service` and `esm-cache.service` via a direct symlink, not the `systemd` module's `masked: yes`:
```yaml
- name: Mask apt-news and esm-cache services (no functional loss, no ESM/Pro attachment)
  file:
    src: /dev/null
    dest: "/etc/systemd/system/{{ item }}"
    state: link
  loop:
    - apt-news.service
    - esm-cache.service
```

**Why:** these fire via `20apt-esm-hook.conf`'s `APT::Update::Pre-Invoke` hook on any apt cache-open — a downstream side effect of `apt_info.py`'s `cache.update()` (see above), not an independent
cause. Belt-and-suspenders cleanup for any other trigger of that hook (manual apt commands, future ansible apt tasks). No functional loss: `apt-news.service` only fetches a cosmetic MOTD banner;
`esm-cache.service` maintains ESM entitlement caches for a subscription that doesn't exist on this fleet (`ua status --format json` → `attached: false` on every node checked).

**Gotcha — these units are version-gated, `systemd: masked: yes` fails hard where they don't exist.** Only shipped by `ubuntu-advantage-tools` **≥28.x** — confirmed live: 27.9~22.04.1 (tjuntjuntjara)
does not ship them at all, 28.1~22.04 (horn-island) does. `systemd: masked: yes` queries current unit state first via `systemctl show`, and fails with `Could not find the requested service` wherever
the unit's `LoadState` is `not-found` — genuinely the case on any node still on the older package version, not a check-mode artifact (compare to the `tmp.mount` gotcha above, which *was*
check-mode-only). **Fix:** mask via a direct `/dev/null` symlink instead (what `systemctl mask` does under the hood) — this doesn't require the unit to exist or be loadable, since
`/etc/systemd/system/` takes priority over `/lib/systemd/system/` in systemd's unit search order regardless, so it stays correct fleet-wide even as nodes eventually pick up the newer package.
**General lesson:** before assuming a `masked: yes` failure is the same known check-mode-only false-positive as a previous session's finding, check live (`systemctl show -p LoadState`, `dpkg -L
<package>`) whether the unit genuinely exists on *that* node — package version drift across a fleet provisioned/updated at different times is a real, recurring cause here.

**Applies to:** rcp, all Ubuntu flavors technically (`when: os_distribution == 'Ubuntu'`, no flavor gate) — not yet checked on rct/wh.

**Validation:**
```bash
tsh ssh root@<node> 'systemctl show apt-news.service esm-cache.service -p LoadState --value'
# Expect: masked / masked (works regardless of ubuntu-advantage-tools version)
```

---

### nl80211 rsyslog Drop Filter — DEPLOYED 2026-07-15, REMOVED 2026-07-17 (never actually worked)

**Original change:** `/etc/rsyslog.d/00-drop-nl80211.conf` (`if $msg contains 'nl80211' then stop`), numbered `00-` so it evaluates before the default rules that would otherwise write the message.

**Original why:** 13 Cambium APs relay wireless-driver debug chatter over UDP 514 into rsyslog — `nl80211` is the Linux kernel wireless netlink API name, and this string only ever appears in that
AP-relayed debug output (SMCs have no local wireless hardware). horn-island-smc01 alone generated 557MB/day this way (root cause found 2026-06-04). Dropping before any output action was also meant to
stop it reaching Fluent Bit, which tails `/var/log/syslog` directly (ADR-006).

**THE BUG — found and fixed 2026-07-17: this filter never actually worked.** `$msg contains 'nl80211'` checks the rsyslog `$msg` property, but every real AP-relayed line has the form `<AP-hostname>
nl80211: <message-body>` — rsyslog's BSD-syslog parser splits `TAG: MSG` on ingest, so `nl80211` here is the syslog **TAG**/`$programname`, never part of `$msg`. The filter was checking the wrong
field from day one.

**Verified live on horn-island with paired `logger` probes** (non-destructive local test messages):
```bash
logger -t nl80211 'TESTPROBE'          # tag=nl80211, matches real AP format
# -> landed in /var/log/syslog, NOT dropped

logger -t testtag 'nl80211: TESTPROBE' # nl80211 inside the message body instead
# -> correctly dropped
```
This is why the original "Gotcha" note below (now struck through) was itself wrong: the write-count fluctuation it described as "expected, filter is exercised but doesn't cover all chatter" was
actually the filter **never being exercised at all** for real traffic. Every fatrace/write-count improvement this project ever attributed to this filter — including the 2026-07-16 "horn-island fully
resolved" post-fix verification — was in fact 100% attributable to the AP-side Event Logging Severity fix (Debug→Warning via cnMaestro), not this filter.

~~**Gotcha — does not cover all AP chatter, only this specific string.** Verified live after deploying: `nl80211:`-tagged lines stop appearing, but other AP debug messages (`deauth`/`mgmt` events,
"Unknown event N") still pass through unfiltered.~~ — **struck through, was based on a false premise**: the filter was never blocking anything, so the "quiet window" observed at deploy-verification
time was the AP not emitting a qualifying burst at that moment, not the filter working.

**Fix (2026-07-17):** removed rather than patched, since the root cause is corrected at the AP config layer — no local rsyslog filter is needed once APs stop emitting at `Debug` verbosity, and a
broken filter that looks correct is worse than no filter. `roles/smc_rsyslog/tasks/main.yml`'s `copy` task replaced with a `file: state=absent` task (commit `9d9b0b9`). Deployed live to all 12/12 rcp
nodes (dry-run + live clean, verified via `tsh ssh`: file absent, rsyslog active, every node). **There is now no local backstop for this issue class** — horn-island/mornington rely entirely on AP-side
Event Logging Severity being correct going forward. See `smc-file-writing-analysis/docs/log-audit-results.md` `20260717_1330` for the full verification narrative and
`smc-file-writing-analysis/SCRATCHPAD.md` Open items for the still-open "audit all APs at both sites in one cnMaestro pass" recommendation.

**Lesson for future rsyslog filters on this project:** when filtering on content that arrives via relayed/forwarded syslog (UDP 514 from an external device), check whether the target string lands in
`$msg` or in `$programname`/`$syslogtag` before writing the filter — do not assume `$msg` contains the full line. Verify with a paired `logger -t <tag> '<body>'` probe before trusting a "quiet window"
as proof the filter works.

---

### wifi/dhcp/system rsyslog Log-Group Split → tmpfs, restart-after-mount (smc_rsyslog role — 2026-07-20)

**Change:** `/etc/rsyslog.d/10-log-groups.conf` routes `dhcpd`/`dhclient` → `dhcp.log`, AP/Cambium-relayed chatter (`nl80211`/`mgmt`/`WPA`/`hostapd*`/`ap_sta_set_authorized`/`ioctl`/
`WIFI-4-CLIENT-*`) → `wifi.log`, and `systemd`/`CRON`/`networkd-dispatcher`/`netifd`/`teleport`/ `postfix/qmgr` → `system.log`, each with `stop` so it's a move off `/var/log/syslog`, not a copy.
`/var/log/smc-groups/` is mounted as a 64M tmpfs (rcp only).

**Why:** confirmed live 2026-07-20 (3 nodes: tjuntjuntjara, mornington, jigalong) that rcp runs **no overlayroot at all** (`overlayroot=""`) — every `/var/log/syslog` write hits the real SSD directly,
unlike rct/wh where overlayroot's tmpfs upper dir already absorbs this for free. See `07_hardware-overlay.md` and `AGENTS.md` "Overlayroot Context".

**THE BUG — same failure class as the Prometheus `stop-before-mount` entry above, but hit live instead of caught by reasoning first.** The Prometheus entry above already documents this exact pattern
(mounting tmpfs over a directory a running process already has open silently shadows its file handles) — that lesson existed in this file before this rollout, and it still wasn't applied: the
`smc_rsyslog` mount task shipped with no `notify`. On the tjuntjuntjara canary, a manual pre-deployment test had already made rsyslog open `wifi.log`/`dhcp.log`/`system.log` on the real disk (no tmpfs
mount existed yet at that point). The later Ansible run mounted tmpfs over the same directory without restarting rsyslog. Result: `ls`/`tail` on the group files showed nothing (the new, empty tmpfs),
`dhcpd`/`dhclient` kept leaking into `/var/log/syslog`, and — the dangerous part — `/proc/<rsyslogd-pid>/fd/` showed the open FDs as completely valid, target path intact, **no `(deleted)` marker**,
because mount-shadowing doesn't unlink the underlying file the way the Prometheus entry's scenario did; it just makes it unreachable by path. rsyslog kept writing real bytes to a real-disk inode that
had become invisible to any normal check. A clean Ansible recap (`ok=18 changed=5 failed=0`) gave zero indication of this — the task that mounts tmpfs reported "changed" correctly, but "changed" only
describes the mount action, not whether the log-writing process noticed.

**Caught only because the operator explicitly asked "is it actually applied" and "are the log files being written" after the run — not by any of my own verification.** Recap success does not verify
content; this is the same "read the file body, don't trust the confirmation" gap RULE-007 exists for, just for a running process's file handles instead of a doc edit.

**Fix:** added `notify: Restart rsyslog service` to the mount task itself (not just the conf-deploy task) — a bare `state: mounted` mount action can report "changed" without the conf file changing at
all (e.g. first-ever mount, or an fstab option tweak), and that's exactly the case that needs the restart most.

**Generalized rule for any future tmpfs-mount task in this codebase:** if the directory being mounted might already have a writer process with it open — which is always true once *any* prior version
of the role has run, including a manual test during development — the mount task itself must `notify` (or directly trigger) a restart of that writer. Don't rely on a separate "ensure service started"
task later in the role; `state: started` is a no-op if the process is already running, exactly like the Prometheus entry already warned.

**Applies to:** rcp only (`hotspot_flavor == 'rcp'`) — rct/wh get this for free via overlayroot.

**Validation:**
```bash
tsh ssh root@<node> 'mount | grep smc-groups; ls -la /proc/$(pgrep -f rsyslogd|head -1)/fd/ | grep smc-groups'
tsh ssh root@<node> "logger -t dhcpd 'verify'; sleep 1; cat /var/log/smc-groups/dhcp.log"
# Expect: tmpfs mount present, fd targets match live paths (not just non-"(deleted)"), and the
# logger probe's output actually appears in the file -- not just that the mount/task recap is clean.
```

---

### Prometheus TSDB → tmpfs, stop-before-mount (smc_prometheus role — 2026-07-15)

**Change:** Mounts `/var/lib/prometheus` as a 128M tmpfs on rcp, with an explicit `service: {name: prometheus, state: stopped}` task immediately *before* the mount task.

**Why:** Prometheus here runs in **agent mode** (`--storage.agent.retention.max-time 120m`), remote_write-ing continuously to a central server — the local TSDB is architecturally a 2-hour scrape
buffer, not a durable store. Confirmed live across 5 nodes before implementing: actual disk usage 2.0M-4.3M, well within the 128M cap.

**Gotcha — mounting tmpfs over an already-running service's data directory needs an explicit stop first, not just a mount-then-rely-on-later-start-task.** The existing "ensure prometheus is enabled
and started" task later in the role uses `state: started`, which is a no-op on any node where the service is already running — true for every node in a rollout like this one. Without an explicit stop
first, the live process keeps its open file handles into the now-shadowed old directory and never actually picks up the new tmpfs-backed path, defeating the whole point of the mount, until some
unrelated future restart. Caught by reasoning through the task order *before* deploying live (the same class of problem as the `tmp.mount` self-disruption bug above — a mount happening underneath a
still-active consumer of the old path — but this one only needed a plain `stop` first, not the async/fire-and-forget trick, since Prometheus doesn't share Ansible's own execution directory the way
`/tmp` does).

**Applies to:** rcp only (`hotspot_flavor == 'rcp'`) — rct/wh already get this for free via overlayroot.

**Validation:**
```bash
tsh ssh root@<node> 'df -h /var/lib/prometheus; journalctl -u prometheus --since "-2min" | grep fs_type'
# Expect: tmpfs 128M; fs_type=TMPFS_MAGIC logged on the most recent startup
```

---

### interfacecheckv2.sh NaN-on-parse-failure (smc_network role — 2026-07-15)

**Change:** When the `sed` extraction of ping loss/RTT values from the summary line comes back empty, write `NaN` to the Prometheus metric instead of feeding the empty string into `bc`.

**Why:** An empty `sed` match feeding straight into `bc` produces an empty `bc` result, which then gets written into the Prometheus exposition line with no value at all — invalid format, causing
node_exporter to log a parse error every collection cycle (root cause of the 2,880 log entries/day fleet-wide finding). `NaN` is the correct could-not-determine value in Prometheus/OpenMetrics — not
`0`, which would falsely read as "0% loss"/"0s RTT" (perfect connectivity), which is not what happened.

**Status:** fix drafted and committed (`ae838c2`) 2026-07-15, **deploy deferred to a later session** per operator instruction — not yet on any node.

**Applies to:** `smc_network` role, deployed via `smc_bases.yml --tags network` when actioned.

---

### smartmon.py Part 1 rollout gap: collector script and relabel config are two separate tags (2026-07-15)

**Lesson:** the 2026-07-13 Part 1 implementation touches two different files in two different roles/tags — `roles/smc_node_exporter/files/smartmon.py` (the collector, `--tags node_exporter`) and the
`write_relabel_configs` addition in `roles/smc_prometheus/templates/prometheus.yml.j2` (`--tags prometheus`). A 2026-07-15 rollout of the collector to the remaining 10 nodes ran only `--tags
node_exporter` and was recorded as "Part 1: 12/12" — but the relabel-config half was never deployed to those 10 nodes, meaning the new `smartmon_active_disk_remaining_lifetime_perc` metric was being
generated locally but silently dropped before reaching the central Prometheus server (the exact same "silently dropped, not matching the keep-list" failure mode Part 1 was fixing in the first place).
Not caught until an unrelated later rollout's dry-run diff happened to show the same file changing. **When rolling any fix that touches both `smc_node_exporter` and `smc_prometheus` config, deploy
both tags together, or explicitly track both as separate rollout items — do not assume one tag's rollout covers the other.**

---

### Journald Volatile Storage (smc_system role — 2026-06-30)

**Change:** Added journald volatile storage task to `roles/smc_system/tasks/main.yml`.

Creates `/etc/systemd/journald.conf.d/99-smc-volatile.conf`:
```ini
[Journal]
Storage=volatile
RuntimeMaxUse=200M
```

**Why:** journald was writing 163–333MB/day to SSD (rcp fleet). `Storage=volatile` moves journal to `/run/log/journal/` (RAM tmpfs), eliminating continuous SSD wear. `RuntimeMaxUse=200M` caps RAM
usage on log storms.

**Safety:** rsyslog reads journald via `imjournal` from `/run/log/journal/` — works with volatile. Fluent Bit pipeline (syslog + misclog tail inputs) is unaffected. `ForwardToSyslog` not needed.

**Handler added:** `roles/smc_system/handlers/main.yml` — `Restart journald` (restarts `systemd-journald` to apply config changes).

**Applies to:** All Ubuntu SMC flavors (rcp, rct, wh) via `when: os_distribution == 'Ubuntu'`.

**Validation:**
```bash
# After playbook run:
tsh ssh root@<node> 'journalctl --disk-usage'
# Expect: /run/log/journal/... (RAM path, not /var/log/journal/)
tsh ssh root@<node> 'cat /etc/systemd/journald.conf.d/99-smc-volatile.conf'
```

---

### smc_graylog RISE Defaults Bug — rcp Override (2026-06-30)

**Bug:** `roles/smc_graylog/defaults/main.yml` sets RISE-specific defaults for all flavors:
```yaml
graylog_sidecar_extra_tags:
  - rise
graylog_sidecar_extra_log_files:
  - "/var/log/rise"
  - "/opt/rise/status"
```

On **rct/wh** these paths exist (RISE is deployed) — no crash. On **rcp** they don't exist → sidecar validates `list_log_files` on startup → fatal crash-loop.

**Symptom:**
```
level=error msg="stat /var/log/rise: no such file or directory"
level=fatal msg="Please provide a list of directories for list_log_files."
```

**Fix:** Added to `inventories/rcp/group_vars/smc_bases.yml`:
```yaml
graylog_sidecar_extra_tags: []
graylog_sidecar_extra_log_files: []
```

**Critical:** Any re-run of `smc_graylog` against rcp redeploys `sidecar.yml` from template, overwriting manual fixes with RISE defaults. The group_vars override must be in place before running the
role on any rcp node.

**Validation:**
```bash
tsh ssh root@<rcp-node> 'systemctl is-active graylog-sidecar'
# expect: active
```

---

### Fluent Bit Position Directory → tmpfs (smc_graylog role — 2026-06-30)

**Change:** Added tmpfs bind-mount task to `roles/smc_graylog/tasks/main.yml`.

Mounts tmpfs (64M) over `/var/lib/fluent-bit/pos/` at role execution. Size documented as `fluent_bit_pos_tmpfs_size: 64m` in `roles/smc_graylog/vars/main.yml`.

**Why:** The pos directory holds SQLite WAL files (25–32MB across fleet, one file per tailed log source). These were written every 5 seconds — 1,419–2,633 write events per 5-minute window per node.
tmpfs eliminates all SSD writes from this source.

**Safety:** pos files track the read offset per tailed file. On wipe (reboot or remount):
- Fluent Bit re-reads from last known Graylog position (duplicate window)
- Graylog deduplicates by message hash — no log loss; brief duplication only

**Validation:**
```bash
tsh ssh root@<node> 'mount | grep fluent'
# expect: tmpfs on /var/lib/fluent-bit/pos type tmpfs (rw,...)
```

---

### Graylog Sidecar Log Redirect → `/run/` RAM (smc_graylog role — 2026-06-30)

**Change:** Sidecar log path moved from `/var/log/graylog-sidecar/` (SSD) to `/run/graylog-sidecar/` (RAM tmpfs). Three file changes:

1. `roles/smc_graylog/templates/sidecar.yml.j2` — `log_path` updated to `/run/graylog-sidecar`; `list_log_files` entry updated to `/run/graylog-sidecar/sidecar.log` (Fluent Bit tail path)
2. `roles/smc_graylog/tasks/main.yml` — directory creation task target updated to `/run/graylog-sidecar`
3. `roles/smc_graylog/tasks/main.yml` — new task deploys `/etc/tmpfiles.d/graylog-sidecar.tmpdir.conf` to recreate the `/run/` directory at boot

**Why:** Sidecar stderr/stdout log flood caused 1,101–153,116 writes/5min (worst: mornington, 8-month-old stale sidecar process with stderr fallback). `/run/` is tmpfs — writes hit RAM only.

**Boot persistence:** `systemd-tmpfiles-setup.service` recreates `/run/graylog-sidecar/` at boot from the tmpfiles.d conf. No sidecar state is lost — sidecar logs are ephemeral by design.

**Validation:**
```bash
tsh ssh root@<node> 'cat /etc/tmpfiles.d/graylog-sidecar.tmpdir.conf'
tsh ssh root@<node> 'systemctl is-active graylog-sidecar'
```

---

### apn-mqtt-client status.json → tmpfs symlink (smc_application role — 2026-07-13/14)

**Change:** brand-new automation block added to `roles/smc_application/tasks/main.yml` (no prior ansible-wifi role managed this app — its cron task traces to an unmerged `origin/mqtt_update` branch,
yet was live in production fleet-wide, a "phantom-deployed" gap worth remembering when auditing what's actually running vs what `rise-multi` shows). Stat-guarded so it's a safe no-op on nodes without
the app:
```yaml
- block:
    - name: Check if apn-mqtt-client app is installed on this node
      stat: {path: /var/www/apn-mqtt-client}
      register: apn_mqtt_client_dir
    - name: Deploy tmpfiles.d to create /run/apn-mqtt-client at boot
      copy: {src: apn-mqtt-client-tmpfiles.conf, dest: /etc/tmpfiles.d/apn-mqtt-client.conf}
      when: apn_mqtt_client_dir.stat.exists
    - name: Symlink status.json to tmpfs to eliminate SSD writes
      file: {src: /run/apn-mqtt-client/status.json, dest: /var/www/apn-mqtt-client/status.json, state: link}
      when: apn_mqtt_client_dir.stat.exists
  when: hotspot_flavor in ['rcp', 'nbn_accelerate']
```

**Why:** `status.json` was the single highest-frequency writer on every rcp node where the app is present — up to ~2,900 write events per 5-minute fatrace window on the busiest node (mornington),
rewriting continuously, forever, unbounded. Proven fix first on burringurrah (2026-07-13, 80% total-write reduction confirmed same-day), then rolled fleet-wide (2026-07-14) — deployed to all 12/12 rcp
nodes, verified `status.json` no longer appears in any node's top-5 fatrace writers afterward.

**Gotcha — "app absent" needs direct verification, not inference from a sample.** 3 nodes (tjuntjuntjara, kalumburu, umoona) were initially classified "N/A — app absent" based on
`apn-mqtt-client`/`status.json` not appearing in a short fatrace capture window. Direct check (`ls -la /var/www/apn-mqtt-client`) found the app genuinely installed on all three — one (kalumburu) had a
`status.json` actively written the day before the correction. The app is installed fleet-wide; there are no genuine N/A nodes on rcp for this fix. **Absence from a sample is not proof of absence** —
if a fix's applicability is being scoped from fatrace output alone, verify the target file/directory's existence directly before excluding a node.

**Validation:**
```bash
tsh ssh root@<node> 'readlink /var/www/apn-mqtt-client/status.json'
# Expect: /run/apn-mqtt-client/status.json
tsh ssh root@<node> 'ls -la /var/www/apn-mqtt-client'  # confirms app presence directly, don't infer from fatrace alone
```

---

### url_capture v2 — Legacy Directory Auto-Cleanup (smc_url_capture role — 2026-07-14)

**Change:** `roles/smc_url_capture/tasks/v2_setup.yml` gained a final check-then-remove step — after the existing flush/clear logic empties `smc_url_capture_dir` (`/url_capture`) of its legacy v1
`.pcap` files, a new `find` (recurse: false, hidden: true) + `file: state=absent` pair removes the now-empty top-level directory itself, guarded on `matched == 0` so it never touches a directory that
still has unflushed content for any reason.

**Why:** the existing logic only ever cleared file *contents*, leaving an empty `/url_capture` directory behind on every node migrated to v2. Found and manually `rmdir`'d on 3 already-migrated nodes
(burringurrah, tjuntjuntjara, horn-island) during the 2026-07-14 fleet rollout before folding the cleanup into the role so it's automatic for every node going forward.

**Gotcha:** `rm -rf` on the legacy dir was blocked by the local OPA governance gate (destructive bash pattern hard block) when attempted via a raw `tsh ssh ... rm -rf` command outside Ansible — use
`rmdir` for manual one-off cleanup (fails safely on non-empty dirs anyway) or let the role's guarded `file: state=absent` task handle it.

**Validation:**
```bash
tsh ssh root@<node> 'ls -la /url_capture'   # should fail with "No such file or directory" post-v2
```

---

### IPv6 Disable Policy (Fleet vs Vagrant)

When changing IPv6 behavior in `roles/smc_network/tasks/ubuntu.yml`, keep production-fleet consistency as the default.

- Production/default path: use the existing GRUB-based behavior already in repo (`/etc/default/grub` with `ipv6.disable=1`, then `update-grub` + reboot).
- Do not introduce mixed GRUB formatting or append-style rewrites across only a subset of hosts unless a coordinated fleet-wide change is explicitly approved.
- Vagrant troubleshooting changes should be scoped as lab-only behavior (for example, gated by `smc_bases_vagrant_interface is defined`) and must not silently alter production host configuration
  conventions.
- If a Vagrant-only workaround is needed without fleet GRUB drift, prefer explicit Vagrant-only controls and document them in the same change.

#### unbound `interface-automatic` on IPv6-disabled Vagrant VMs

**Symptom:** `unbound[PID]: error: can't bind socket: Cannot assign requested address for ::1 port 53` → `fatal error: could not open ports`. Unbound fails to start even with `do-ip6: no` and
`interface: 0.0.0.0` in the config.

**Root cause:** `interface-automatic: yes` combined with `interface: 0.0.0.0` causes unbound to probe for a matching IPv6 wildcard socket at startup — separate from the `do-ip6` DNS processing flag.
On Vagrant VMs where `$DISABLE_IPV6` sets `net.ipv6.conf.lo.disable_ipv6=1`, the loopback has no `::1` address. The IPv6 socket probe → bind fails → fatal startup error.

**Fix in `roles/smc_dns/templates/unbound.conf.j2`:**
```jinja2
{% if smc_bases_vagrant_interface is defined %}
        interface-automatic: no
{% else %}
        interface-automatic: yes
{% endif %}
```

**Why physical SMC is unaffected:** Physical boxes have IPv6 on loopback (`::1` present). The probe succeeds silently; `do-ip6: no` then prevents IPv6 DNS queries from being served. No operational
change to fleet behavior.

**Note:** Adding `control-interface: 127.0.0.1` to the `remote-control:` section (port 8953) is correct hardening but does NOT fix the port 53 error — they are independent socket bindings.

### Skill Runtime Paths

For local skill tooling consistency, use these dedicated working-cache venvs:
- ansible-wifi venv: `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`
- skill-smc venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`
- ephemeral logs, pid files, and sockets: `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/`

When executing validation commands from this reference, prefer invoking tools from the ansible-wifi working-cache venv to avoid host-level version drift.

### Canonical Source Rules

1. `inventories/*/topology_vars/<site>.yml` — canonical topology source. Edit these.
2. `inventories/*/topology_vars/.<site>.yml` — generated cache (mtime-gated). Never edit.
3. `roles/smc_generate_smc_files/templates/` — future-site generator templates. Changes here must stay consistent with manual edits to existing sites.

### Design Recommendation (Not Yet Implemented): Bond Doubled RCP/NBN-Accelerate Internet Circuits

**Status: design recommendation, 2026-07-31 — not implemented, not canary-tested.** Scoped to RCP and NBN-Accelerate flavor sites only, where internet circuits terminate on two independent L2 switches
(`switch01`/`switch02`) downstream of the SMC. `topology_vars` today models each such circuit as **two separate interfaces** (e.g. `internet03`=vlan521/switch01, `internet04`=vlan531/ switch02) — both
permanently defined, both in the default VRF, both polled every cycle by `interfacecheckv2.sh`, even though only one ever has a live cable at a time (manual cold-standby: a technician physically moves
the cable to switch02 if switch01 fails). For old-looma this means 18 pings/cycle where 9 would suffice.

The team considered bridging `switch01`/`switch02` under one shared VLAN tag to collapse this, and correctly worried that if a technician ever leaves both legs live simultaneously, two independent WAN
CPEs would race for DHCP on one broadcast domain. **That risk assessment is right, but bridging
+ STP is the wrong fix for it** — STP blocks *redundant paths between bridges* via loop detection;
here there is no loop for STP to see (the CPEs aren't bridges), so STP would not prevent the dual-live condition at all.

**Recommended mechanism: Linux bonding, `mode=active-backup`, not bridging.** Only the active slave ever passes frames up the stack — the backup slave is excluded from the forwarding path
structurally, even if it independently shows carrier/link-up, so a technician leaving both legs physically live causes no DHCP race and no ARP instability. One logical `bond_internetNN` interface also
replaces two for VRF attachment and health-check purposes, restoring the 1:1 interface-to-circuit ratio `interfacecheckv2.sh` was implicitly designed around.

```yaml
bonds:
  bond_internet03:
    interfaces: [vlan521, vlan531]   # vlan521 → switch01, vlan531 → switch02
    parameters:
      mode: active-backup
      primary: vlan521
      mii-monitor-interval: 0        # required — cannot mix MII and ARP monitoring on one bond
      arp-interval: 100
      arp-ip-targets: [<circuit's known CPE gateway IP>]
      arp-validate: all
```

**Monitoring must be ARP-based, not MII-based** — `switch01`/`switch02` sit between the SMC and the CPE, so SMC↔switch carrier stays up even if the actual WAN device behind that switch port has died;
`miimon` alone is blind to that. `arp_interval`/`arp_ip_target` (the circuit's known/fixed CPE gateway IP) tests end-to-end reachability, matching what `interfacecheckv2.sh` already does via ping
today.

**Known implementation risk — verify before any fleet rollout.** Bonding a VLAN device as a bond slave (VLAN created first, then enslaved) is the reverse of netplan's own documented bond-then-VLAN
pattern and has documented systemd-networkd boot-time race bugs: [systemd #7020]( https://github.com/systemd/systemd/issues/7020) and [systemd #15280](
https://github.com/systemd/systemd/issues/15280). Ubuntu 20.04/22.04 SMCs use systemd-networkd as the netplan renderer by default, so this applies directly — comparable in kind to the netplan
0.104→0.107 VRF syntax incompatibility already found on rocket-bore-smc01/yimidarra-smc01 (elsewhere in this file). **Do not roll out fleet-wide on reasoning alone** — canary one non-critical circuit
at one site, reboot 3× minimum, confirm `cat /proc/net/bonding/bond_internetNN` survives each reboot, and confirm active-backup failover by physically unplugging the primary leg's cable before
trusting the pattern.

**Rollout scope note:** this is a schema change. `type: bond` is not currently a recognized interface type in `topology_vars`/`roles/smc_generate_smc_files` — only `ethernet | vlan | bridge |
loopback` are — and `interfacecheckv2.sh` role-filtering/VRF attachment need to point at the bond interface, not its two legs, once added. Scope the change to RCP/NBN-Accelerate only; this dual-switch
pattern does not exist fleet-wide across all 7 flavors. Full analysis:
`local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/internet-link-active-standby-handling-analysis-20260731_1107.md`.

### Topology Change Workflow

```
1. Identify the flavor and canonical topology file
   inventories/<flavor>/topology_vars/<site>.yml

2. Edit the canonical source only
   (never touch the hidden .*.yml cache file)

3. Assess cross-flavor impact
   - topology_vars/<site>.yml change → single flavor only
   - group_vars/** change → all 7 flavors affected
   - topology_vars.py plugin change → all 7 flavors affected

4. Find consuming roles
   grep -r "topology_interfaces" roles/
   grep -r "topology_bridges" roles/
   grep -r "topology_vrfs" roles/

   Confirmed 2026-07-29 (rcp, APN routing-issue investigation) — every role whose templates filter
   on `interface.role` (internet/starlink/user/management/provision/nbn_modem) goes stale the same
   way if topology changes and it isn't re-run. All render from the same topology-derived
   `interfaces` dict as smc_network/smc_application:
     - smc_network (tag `network`)       — netplan, dhclient confs, rt_tables, interfacecheck
     - smc_application (tag `application`) — dhclient-enter-hooks (ECMP/default-route membership)
     - smc_iptables (tag `iptables`)      — builds internets/starlinks/users/managements/
                                             provisionings/nbn_modems ACL lists from `.role`
     - smc_qos (tag `qos`)                — shapes only `role == 'internet'` interfaces
     - smc_node_exporter (tag `node_exporter`) — SEPARATE PLAYBOOK, smc_prometheus.yml, not
                                             smc_bases.yml — easy to omit from a remediation run.
                                             Also COMPUTES the ECMP-health alert threshold as
                                             count(internet interfaces)/2+1, so a stale topology
                                             miscalibrates the alert, not just interface labels.
     - smc_keepalived (tag `keepalived`)  — looks up a VRRP interface by ID from the same dict,
                                             but is NOT `.role`-filtered like the others — lower
                                             risk, flagged for completeness, not confirmed broken.
   Checked and NOT implicated: smc_dhcpd, smc_hostapd (LAN-side / bridge_500,501 only).
   A remediation run scoped to `smc_bases.yml --tags network,application` alone is incomplete —
   add `iptables,qos` to that tag list, and run `smc_prometheus.yml --tags node_exporter`
   separately. Evidence: local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/
   problem2-live-root-cause-20260729_2112.md

5. Check generator template drift
   Compare roles/smc_generate_smc_files/templates/ against your change
   Future sites generated from the template must stay consistent

6. Delete stale cache (important after git checkout — mtime may be stale)
   rm inventories/<flavor>/topology_vars/.<site>.yml

7. Run validation sequence (in order)
   yamllint <changed_files>
   ansible-lint <changed_playbooks>
   ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --list
   ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --host <site>
   ansible-playbook --syntax-check <playbook>
```

### Variable Rename / Refactor Workflow

```
1. Enumerate all source changes required
   (topology_vars YAML, group_vars, host_vars, role defaults/vars)

2. Grep all consuming roles and templates
   grep -rn "old_variable_name" roles/
   grep -rn "old_variable_name" inventories/

3. Check generator templates for drift
   grep -rn "old_variable_name" roles/smc_generate_smc_files/

4. Identify cache files that will auto-regenerate vs. stale caches
   Delete relevant hidden .*.yml files to force fresh generation

5. Run full validation sequence after changes
```

**Guardrailed single-site interface-key rename pattern** (pia-wadjari, `internetNN`→`a-internetNN` / `starlinkNN`→`s-internetNN`): when renaming interface *keys* specifically (not general variables),
prefer scoping the rename to one site's `topology_vars/<site>.yml` plus the generator templates under `roles/smc_generate_smc_files/templates/` that produce future sites — not a repo-wide rename of
existing sites. This works cleanly here because `vars_plugins/topology_vars.py` is already raw-ID agnostic (it preserves whatever interface keys a site defines) and consumer templates (e.g.
`roles/smc_iptables/templates/iptables.smp.j2`, `roles/smc_qos/templates/50-qos.sh.j2`) branch on `interface.role`, never on the `internetNN`/`starlinkNN` key prefix itself — so leaving other sites'
existing keys unchanged does not break anything. **Before assuming this shortcut applies to some other variable rename, confirm the same two properties hold** (the vars plugin is ID-agnostic, and
every consumer branches on a semantic field rather than the key name) — if either is false, a single-site guardrail leaves other sites on an inconsistent scheme with no code path enforcing
consistency. Regenerate the hidden `.<site>.yml` cache via `ansible-inventory`, never hand-edit it.

### Cache Coherence Rules

After a `git checkout` or branch switch, hidden `.*.yml` cache files may appear current (mtime preserved by git) but contain stale content. Always delete cache files for affected sites before relying
on topology output:

```bash
# Delete single site cache
rm inventories/<flavor>/topology_vars/.<site>.yml

# Delete all cache files for a flavor (safe — they regenerate on next run)
find inventories/<flavor>/topology_vars/ -name '.*.yml' -delete
```

### Inventory Path Convention

Each flavor's `inventories/<flavor>/` directory contains **two separate inventory files**, `prod` and `stage` (e.g. `inventories/rcp/prod`, `inventories/rcp/stage`) — not a nested directory structure.
Always pass `-i inventories/<flavor>/prod` (or `/stage`) explicitly to `ansible-playbook`/`ansible-inventory`. Passing the bare `-i inventories/<flavor>` directory instead loads **both** `prod` and
`stage` as inventory sources in one run — every host in both environments becomes a valid target, and only an explicit `--limit <host>` protects you from touching the wrong one. This was caught live
2026-07-20: a canary rollout used `-i inventories/rcp` (bare directory) instead of `-i inventories/rcp/prod`; `--limit tjuntjuntjara-smc01` happened to keep the actual blast radius correct since that
host is unambiguously in `prod`, but the imprecise inventory path was still a latent risk that should be fixed before it causes a real cross-environment mistake. This convention was already documented
in the Validation Command Reference below (`ansible-inventory -i inventories/<flavor>/prod ...`) but wasn't called out as a standalone rule — do not rely on spotting it embedded in an example.

### Cross-Branch File Fetch Tool

`scripts/fetch-commit-files.sh` (added 2026-07-21) pulls specific files out of a given commit/ref and writes them into the current working tree, without merging or cherry-picking the whole
commit/branch. Built for exactly the situation that prompted it: a colleague's branch (`origin/fix_rcp_wifi_commit`) had already added `group_vars`/`host_vars`/`topology_vars` for two sites
(`old-looma-smc01`, `new-looma-smc01`) that were never merged into `rise-multi` — `old-looma` was showing up as a live Teleport/Prometheus target with zero presence in the local inventory because of
this, not because it was deliberately unmanaged.

```bash
scripts/fetch-commit-files.sh <commit-ish> <file1> [file2] ... [--force]
scripts/fetch-commit-files.sh <commit-ish> --file-list <path> [--force]
```

- Verifies the commit resolves locally first — if it's on a remote branch you haven't fetched, `git fetch --all` first (`git branch --all --contains <sha>` finds which remote/branch has it).
- Verifies each requested file actually exists in that commit's tree before doing anything.
- **Never silently overwrites a local file that already exists and differs** — shows the diff and skips it unless `--force` is passed. Safe to re-run; already-matching files report `unchanged`.
- Never runs `git add`/`git commit` — review with `git status`/`git diff` afterward, same as any other change in this codebase (ansible-wifi commits are held local pending explicit operator decision
  per this project's standing practice).
- Accepts a file list via `--file-list <path>` (one path per line, `#` comments and blank lines ignored) for bulk fetches instead of long positional argument lists.

**Gotcha found during the looma fetch — vars alone don't make a host live.** Even at the source commit, `old-looma-smc01`/`new-looma-smc01` were **not** registered as hosts in `inventories/rcp/prod`
or `/stage` — only the `group_vars`/`host_vars`/`topology_vars` files existed. `group_vars`/`host_vars` only apply to hosts actually declared in the inventory and assigned to that group/hostname —
fetching the vars files is necessary but not sufficient to bring a site under active management. Check `git show <ref>:inventories/<flavor>/prod` for the actual host entry before assuming a fetched
var-file set is deployable as-is.

### Playbook Run Safety (Overlayroot)

- Changes made via playbooks that do not remount the lower dir are **volatile** — they survive until next reboot only. **This applies to rct/wh only**, where overlayroot is real.
- Verify with: `mount | grep root-ro` on target before running critical plays
- The `smc_bases.yml` playbook handles overlayroot remount; run it first or ensure it runs as a dependency
- **rcp has NO overlayroot at all** (confirmed live 2026-07-20 on tjuntjuntjara/mornington/jigalong — see `07_hardware-overlay.md`). On rcp, playbook changes are **permanent**, not volatile — they
  land on the real ext4 root (or an explicit tmpfs mount, if the role adds one) and persist across reboots exactly like changes to any normal Linux host. Do not assume rcp changes need a "did it
  survive reboot" check the way rct/wh changes do; assume the opposite — an rcp mistake stays until explicitly reverted.

### Validation Command Reference

```bash
# YAML syntax
yamllint inventories/<flavor>/topology_vars/<site>.yml

# Ansible lint
ansible-lint roles/<role_name>/

# Inventory list (warns on plugin errors)
ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --list

# Per-host variable dump (verifies topology_vars plugin output)
ansible-inventory -i inventories/<flavor>/prod --playbook-dir . --host <site>

# Playbook syntax check
ansible-playbook -i inventories/<flavor>/prod --syntax-check smc_bases.yml

# Lint baseline refresh (regenerate .git/.ansible-lint-ignore from current violations)
scripts/lint-baseline-refresh.sh

# Lint delta gate (fail only on NEW violations in changed files/lines — used by pre-push hook)
scripts/ansible-lint-delta-gate.sh <changed-file1> <changed-file2> ...
```

Both lint scripts above are promoted, generalized copies at `skill-smc/scripts/lint-baseline-refresh.sh` and `skill-smc/scripts/ansible-lint-delta-gate.sh` — see `skill-smc/scripts/README.md` for the
full mechanism (baseline-ignore file format, changed-line detection, why pre-existing violations in untouched lines are not blocking).

### Pre-push gate: four stages, three different rule sets (established 2026-08-18)

The hook runs four stages and they do **not** share semantics. Identifying which one is complaining is most of the debugging:

| Stage                             | Baseline?                         | Scope                                                                    |
| --------------------------------- | --------------------------------- | ------------------------------------------------------------------------ |
| `repo_knowledge_capture`          | n/a                               | snapshot into `local-knowledge-ansible`                                  |
| ansible-lint **delta** gate       | yes (`.git/.ansible-lint-ignore`) | changed-lines aware                                                      |
| **yamllint**                      | **no**                            | every changed file; any *error* fails the push                           |
| `ansible-playbook --syntax-check` | n/a                               | **root-level playbooks only** — role task files are never syntax-checked |

Properties worth knowing before you fight it:

- The delta gate checks `line_is_changed` **before** it consults the baseline. A baseline entry can therefore never hide a finding on a line you wrote, which is what makes refreshing the baseline a
  legitimate record of inherited debt rather than a `noqa` in disguise.
- Every finding in a **new** file blocks unconditionally. There is no baseline escape for new files, so a new role must be lint-clean on its own terms.
- The baseline is keyed `file|rule`, coarsely — one entry covers every instance of that rule in that file — and it lives in `.git/`, so it is **not version-controlled**. Refreshing it unblocks your
  machine only; the next clone hits the same wall.
- The gate's parser mis-reads findings that carry a column (`file:line:col: rule:`) and stores the **column number** as the rule. That is why the baseline contains entries like
  `smc_rise_deploy_stage0.yml 11`. Any generator must reproduce the quirk or its entries will not match.
- The gate computes changed ranges from `base..HEAD` but lints the **working tree**. With uncommitted changes the two disagree and it reports phantom blocks — commit first, then re-run.
- **Order matters.** Fix findings on your own lines first, refresh the baseline second, do whitespace last. A blanket whitespace pass early expands the changed-line set and drags hundreds of inherited
  findings into the blocking set — that mistake turned a 43-finding job into a 404-finding one.
- yamllint has no baseline, so inherited whitespace defects in a file you touch block the push even though they predate you. That cleanup is unavoidable; keep it whitespace-only and in its own commit.

### The hook's ansible venv is under-provisioned (corrected 2026-08-18)

Earlier revisions of this section said that if the hook fails you should ensure `/Volumes/Data/_ai/_skills/skills-runtime/ansible-wifi/.venv/bin` is on `PATH`. **That is now known to be the cause
rather than the cure.** The hook already prepends it, and that venv carries `ansible-core 2.17.14` with only **two** collections (`community.general`, `community.grafana`) and no `netaddr`, where brew
has the full bundle — core 2.21.3 and **95** collections.

Consequence: the venv cannot resolve `selinux` (`ansible.posix`) used at `roles/smc_system/tasks/main.yml:137`, so the syntax-check stage fails for **any** push touching a playbook that reaches that
role, independent of what you changed. It also surfaces as `Ansible requires blocking IO on stdin/stdout/stderr` under the hook's redirection. This plausibly explains long-uncommitted `smc_bases.yml`
work.

Until the venv is repaired (install the missing collections, or point the hook at brew): verify with the brew toolchain, and if you bypass with `--no-verify`, run all four stages by hand first and
note that the bypass **also skips `repo_knowledge_capture`**, so no governance snapshot is taken.

### OPA Policy Layer (deployment governance gate)

`ansible-wifi` carries an [Open Policy Agent](https://www.openpolicyagent.org/) layer under `opa/` that enforces fleet deployment rules independent of `ansible-lint`/`yamllint` — it checks semantic
correctness (is this deployment safe/consistent), not syntax.

```
opa/
  policies/
    smc_url_capture.rego   # url_capture version, tmpfs, and capture config rules
    inventory_vars.rego    # required host/group var completeness rules
    site_deployment.rego   # deployment gate rules (flavor match, commit pin, blast radius)
  tests/
    smc_url_capture_test.rego
  data/
    flavors.json, environments.json   # collapsed lookup data (avoids OPA CLI merge errors)
```

| Package                        | Deny rules                                                                   | Warn rules                                 |
| ------------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------ |
| `ansible_wifi.smc_url_capture` | v1 on prod without approval, tmpfs cap range, chunk seconds range            | non-bridge capture iface                   |
| `ansible_wifi.inventory_vars`  | missing `teleport_fqdn`, bad `eclipse_siteid`, unknown `url_capture` version | orphaned host                              |
| `ansible_wifi.site_deployment` | cross-flavor deploy, unpinned wifi repo commit                               | multi-site blast radius, mixed v1/v2 fleet |

```bash
# Evaluate against a host input file
opa eval -d opa/policies/ -d opa/data/ -i input/<site>-smc01.json 'data.ansible_wifi.smc_url_capture.deny'

# Run policy unit tests
opa test opa/policies/ opa/tests/ -v

# Conftest (YAML lint integration, not yet wired into CI — ROADMAP backlog item)
conftest test inventories/rcp/host_vars/<site>-smc01.yml --policy opa/policies/
```

**ADR-001 — env gate overrides flavor gate.** The per-flavor `required_version` deny rule (e.g. rcp must run `smc_url_capture` v2) only fires when `env_cfg.url_capture.required_version != null` in
`opa/data/environments.json`. `stage` sets this to `null` — permissive regardless of what the flavor requires; `prod` sets a non-null value to actually enforce the gate. Precedence is **env-gate
first, then flavor-gate** — do not assume a flavor's `required_version` alone determines whether a v1 deployment is denied; check which environment the input targets first.

**Gotcha (live-confirmed):** the local OPA governance gate also blocks destructive shell commands (e.g. `rm -rf` on a legacy directory) as a safety net independent of the deploy-policy packages above
— if a destructive command is unexpectedly refused, check whether this gate fired before assuming a shell/permissions problem.

---

---

## tmpfs relocations need `tmpfiles.d`, not just a `file:` task (2026-07-28)

**Pattern to follow for any future tmpfs relocation in `ansible-wifi`.** Full rationale and the incident that produced it:
`smc-file-writing-analysis/.archcore/rules/RULE-016-tmpfs-relocation-needs-tmpfiles-for-daemon-dirs.md` and `docs/log-audit-results.md` `20260728_1240`.

### The failure mode

`roles/smc_rsyslog` relocates squid/mosquitto logs onto the `/var/log/smc-groups` tmpfs, creating their subdirs with `file: state: directory`. That is a **one-time deploy action**, and tmpfs contents
are destroyed on every reboot. squid and mosquitto do not create their own log directory — they abort. Result: squid `FATAL` at boot and a user-facing outage.

**The part that makes it dangerous:** the relocation block is guarded on `stat.islnk` ("not yet relocated"), which is correct for idempotency but means the subdir-creation task **no-ops on a node that
has already been relocated** — including one that has since rebooted and lost the directory. So "just re-run the playbook" does not fix it. There is no self-healing path.

**And it is invisible until a reboot.** On 2026-07-28 only 2 of 15 nodes had failed; the other 13 carried the same defect with pre-deploy uptimes. Never conclude a tmpfs relocation is reboot-safe from
"all nodes healthy" — correlate against uptime first.

### The required shape

```yaml
- name: Ensure smc-groups tmpfs subdirs are recreated on every boot (tmpfiles.d)
  template:
    src: smc-log-groups.tmpfiles.conf.j2
    dest: /etc/tmpfiles.d/smc-log-groups.conf
    owner: root
    group: root
    mode: '0644'
  register: smc_loggroups_tmpfiles
  when: hotspot_flavor == 'rcp'

- name: Apply the tmpfiles rules now (heals a node that already lost its subdirs)
  command: systemd-tmpfiles --create /etc/tmpfiles.d/smc-log-groups.conf
  when:
    - hotspot_flavor == 'rcp'
    - smc_loggroups_tmpfiles is changed
  changed_when: true
```

Four things that matter:

1. **Keep owner/mode in sync** with the `file:` tasks that create the same dirs (`proxy:proxy 0750` for squid, `mosquitto:mosquitto 0740` for mosquitto).
2. **Gate optional daemons in the template.** mosquitto is absent on tjuntjuntjara; a `tmpfiles.d` rule naming a non-existent user makes `systemd-tmpfiles` log a hard error every boot. Use `{% if
   'mosquitto.service' in (ansible_facts.services | default({})) %}` — which requires `service_facts` to have run earlier in the role (it already does, for the mosquitto relocation guard).
3. **Apply immediately**, so an already-broken node is healed by the run rather than waiting for its next boot.
4. **Ordering needs no special handling** — `systemd-tmpfiles-setup.service` is `After=local-fs.target` (so after the fstab tmpfs mounts) and completes within `sysinit.target`, before
   `multi-user.target` starts squid/mosquitto.

### Verifying without breaking production

Don't delete the live directory to prove recreation (the OPA destructive-command gate will block it, correctly). Use a scratch rule on the same tmpfs — `d /var/log/smc-groups/_tmpfiles_probe 0750
proxy proxy -` → `systemd-tmpfiles --create <file>` → confirm owner/mode → remove probe. Same mechanism, zero service risk.

## Reclaiming state that a role's own tooling can't see (`smc_system` journal reclaim, 2026-07-28)

`roles/smc_system` now removes the orphaned `/var/log/journal` left behind by the `Storage=volatile` conversion. Two authoring points generalise:

- **Guard on runtime evidence, not on config intent.** The reclaim fires only when `/run/log/journal` exists — proof journald is *actually* volatile. Guarding on "we wrote `Storage=volatile` to the
  drop-in" would delete live logs on a node whose journald had not restarted yet.
- **`meta: flush_handlers` before destructive follow-up work.** The volatile config notifies `Restart journald`; without flushing, a first-time conversion would delete the journal while journald still
  held it open and was still writing persistently.

See `07_hardware-overlay.md` for the fleet numbers and why `journalctl --vacuum-*` cannot do this job.

---

## Narrowing tags: ask what the tag EXCLUDES (2026-07-28)

Full rule: `smc-file-writing-analysis/.archcore/rules/RULE-017-narrowing-tag-must-select-the-repair-tasks.md`. Incident detail: `docs/log-audit-results.md` `20260728_1500`.

### The failure

`roles/smc_application` has a block that wipes and re-clones `/var/www/html/wifi` (`file: state=absent force=yes` then `git`), and a **separate** block that chmods `application/cache` and
`application/logs` to 0777 so Apache (`www-data`) can write them. Git recreates those directories at 0755 root:root.

A `wifi_git` tag was added in July 2026 to scope a commit-bump deploy narrowly. It tagged the **destructive** block and left the **repair** block untagged. The narrow run therefore wiped and never
repaired, `Kohana::init()`'s `is_writable(APPPATH.'cache')` threw before routing, and **10 of 16 rcp captive portals were down for 7 days.**

**Rule: if a tagged block destroys or recreates state, every task that repairs that state must carry the same tag.** Ask what a new tag excludes, not just what it includes.

### Why it stayed invisible for a week

Worth knowing as a diagnostic signature, because all four properties fight detection:

- Kohana prints the error itself, so the response is **HTTP 200** with a plain-text body. A status-code health check passes. **HTTP 200 is not a health check** — assert on body content.
- It throws in `init()` before routing, so nothing reaches PHP's error handler and `apache2/error.log` stays clean.
- The `kohana status:update:*` CLI crons run **as root**, pass the writability check, and keep feeding Eclipse — upstream data keeps flowing, so nothing alerts.
- Already-authorised sessions are unaffected (enforcement is iptables/conntrack), so the site looks half-alive rather than down.

### `--tags` on this role is destructive, not a repair path

`--tags wifi_dev_repo` (renamed from `wifi_git` 2026-07-28) **wipes and re-clones the portal**. Confirmed by check-mode dry run: `clear old /var/www/html/wifi repository` reports `changed`. Do not
reach for it to fix permissions. The safe repair is ad-hoc:

```bash
ansible -i inventories/rcp/prod <hosts> -m file \
  -a "path=/var/www/html/wifi/application/{cache,logs} state=directory mode=0777 owner=root group=root"
```

Also note `roles/smc_teleport/templates/teleport.yaml.j2` runs `cat /var/www/html/wifi/application/config/site.txt` **every 60 s** as the Teleport `id` dynamic label — that label drops for every node
during the wipe window.

### Tracing an identifier in this repo

Two traps, both hit during the 2026-07-28 audit:

1. **The same word is often both a tag and a variable.** `wifi_git` was 3 tag declarations against 30 variable usages (`{{ wifi_git.repo }}`, the role-invocation vars in `smc_bases.yml` and
   `smc_rise_deploy.yml`, `smc_bases_wifi_git` in five inventory flavors, plus the `jenkins_wifi_git`/`ansible_wifi_git` family). Classify every hit before editing, and anchor the edit regex
   (`^\s*tags:\s*<name>$`) rather than doing a blind replace.
2. **A yml-only grep is not enough — include `*.j2`.** `roles/smc_teleport/templates/teleport.yaml.j2` consumes `wifi_git` as template data, and the first audit sweep (yml/yaml/sh/cfg/md) missed it
   entirely.

### Renaming a tag fails silently

Ansible emits **no unmatched-tag warning**. After the rename, `--tags wifi_git` still **exits 0 and runs 37 tasks** — all of them `always`-tagged (apt cache, lock clearing, fact gathering) and
**none** of them `smc_application`. A stale saved command produces a run that looks successful and never touches the thing it names. Flush runbook and shell-history copies whenever a tag is renamed.

### Verification order that actually catches this

`--syntax-check` and `--list-tasks` tell you selection, never behaviour. Only `--check` reveals that a selected task is destructive:

1. `--tags X --list-tasks` and `--skip-tags X --list-tasks` — what is in, what is now out.
2. `--check` against one host — read which tasks report **changed**.
3. Confirm no regression to the broad tag (`--tags application` here) and to full runs. Tags are additive, so adding one never removes a task from an untagged full run.

## `smc_network` VRF template requires netplan ≥ 0.106 — the whole fleet runs 0.104 (2026-08-25)

`roles/smc_network/templates/netplan.yml.j2` emits a `vrf:` key for **every** interface with `role: internet` or `role: starlink`, state `present`, type ethernet/vlan, plus a top-level `vrfs:` block.
There is **no feature flag and no version guard** — see the `vrf_candidates` loop. Introduced by commit `5eb127bf` (2025-10-16).

**Which branches carry it — 4 of 28** (17 `vrf` references each): `rise-multi`, `internet-label-rename`, `starlink-qos`, and `refs/heads/fb419e6c1109682d1518f98402d0145fdcef079e` (a malformed
40-hex-named branch whose tip `b40ea909` matches `rise-multi` — effectively a twin). **Every other branch renders no VRF**, including `master` (tip `a58f2fe2`, 2026-07-24) and `fix_rcp_wifi_commit`
(tip `fb419e6c`, 2026-06-23); neither contains `5eb127bf`. There is no `main` branch — `master` is the VRF-free mainline.

**Ref-ambiguity trap, cost a wrong answer once (2026-08-25):** that 40-hex branch name collides with a commit ID, and git silently resolves the bare name to the **commit**, not the branch — while
printing only an `advice.objectNameWarning`. `git show <40hex>:path` and `git merge-base --is-ancestor X <40hex>` therefore answer about commit `fb419e6c` (0 `vrf`, does not contain `5eb127bf`), while
`git branch --contains` lists the branch ref (17 `vrf`, does contain it). The two disagree and both look authoritative. **Always use the full `refs/heads/<name>` form** when a branch name is 40 hex
characters, and treat a branch-vs-`git show` contradiction as a ref-resolution bug before treating it as a revert.

Every rcp SMC runs **netplan.io 0.104-0ubuntu2.1**, which has no VRF support whatsoever — its package changelog contains zero `vrf` mentions. `netplan generate` therefore hard-fails:

```
/etc/netplan/00-ansible.yaml:12:7: Error in network definition: unknown key 'vrf'
```

jammy-updates offers 0.107.1 as candidate. **UNVERIFIED:** that 0.107.1 accepts this template's exact `vrf:`/`vrfs:` schema — settle it by rendering the template and running `netplan generate` on an
upgraded lab box before deploying VRF anywhere.

### Why this stayed hidden for ten months

**Not because a VRF-free branch was used — the July 2026 work ran from `rise-multi`, which does carry VRF.** The July write-reduction commits (`594653b9`, `af2edf56`, `5332e9b3`, `b40ea909`) are
reachable only from `rise-multi` / `internet-label-rename` / the 40-hex twin, all VRF-carrying, and are *absent* from `master` and `fix_rcp_wifi_commit`. So the protection was **not** branch choice.

The protection was **tags**. `smc_network` sits behind `tags: network` (`smc_bases.yml`). Every rollout of the program used `--tags system` / `application` / `url_capture` / `rsyslog` / `smc_graylog`
/ `prometheus` — **`network` was never once among them**, so the netplan task never executed.

**Decisive evidence — `/etc/netplan/00-ansible.yaml` mtimes, all 16 rcp nodes, live 2026-08-25.** Every file predates the July work, and every one has **zero** `vrf` keys:

| mtime   | Nodes                                                                                                                               |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 2024    | tjuntjuntjara (03-06), bidyadanga (04-09), mornington (06-01), burringurrah (07-26)                                                 |
| 2025    | guda-guda (04-02), wujal-wujal (05-06), horn-island (11-23)                                                                         |
| 2026 H1 | jigalong (01-23), kalumburu (02-13), umoona (04-13), warburton (05-02), mowanjum (05-04), beagle-bay (05-14), pandanus-park (06-19) |
| 2026 H2 | old-looma (07-16) — the newest, and still pre-dating the 07-21 onboarding                                                           |

Had `smc_network` run even once during the July passes, those mtimes would read July and the runs would have failed on the spot. The **older, VRF-free renderings came from `master` /
`fix_rcp_wifi_commit`** (the branches used for network-affecting work), and tags then froze them in place while the project worked from a VRF-carrying branch beside them.

So months of green runs on a VRF-carrying branch proved nothing about the VRF code, which had never executed on hardware.

**It surfaced on the first node to get a full untagged run** — yakanarra-smc01, newly onboarded 2026-08-25, where onboarding necessarily runs everything.

**General lesson — the inverse of "Narrowing tags: ask what the tag EXCLUDES":** tag scoping does not merely limit blast radius, it **conceals untested code indefinitely**. A branch is not validated
by repeated tagged runs; only the tags actually used are. Before onboarding a new node — the one operation that runs every role — diff the untagged roles against what has actually been exercised on
the fleet.

### Failure mode is a delayed, remote-isolating outage

The `template:` task writes `/etc/netplan/00-ansible.yaml` **before** the `netplan generate` task validates it, and it overwrites in place with no `backup: yes`. So a failed run leaves an invalid
netplan as the node's only network config. The box keeps running because the live config lives in `/run/systemd/network` — but `/run` is **tmpfs**, so on reboot the netplan generator fails, no
`.network` units are written, and a remote site comes up unreachable. The playbook failure looks survivable; it is a latent outage.

**Recovery used on yakanarra (2026-08-25), no `netplan apply` involved:**

```bash
cp -a /etc/netplan/00-ansible.yaml /root/00-ansible.yaml.broken-vrf-<ts>.bak
mkdir -p /root/netrun-before-<ts> && cp -a /run/systemd/network/. /root/netrun-before-<ts>/
awk '/^  vrfs:/{exit} !/^      vrf: vrf-/{print}' /etc/netplan/00-ansible.yaml > /tmp/np.new
install -m 0600 -o root -g root /tmp/np.new /etc/netplan/00-ansible.yaml
netplan generate                                        # must exit 0
diff -r /root/netrun-before-<ts> /run/systemd/network   # must be identical
```

Stripping the 10 `vrf:` lines and the trailing `vrfs:` block reproduces the pre-VRF rendering exactly — `activation-mode: manual` on role:internet/starlink interfaces is pre-existing behaviour and
stays. The `diff` is the real gate: identical output proves the repair changed no intended network state and nothing new applies at reboot. **Never `netplan apply` on a remote SMC to fix this** —
`generate` is sufficient to clear the boot hazard, and `apply` risks the uplink carrying your own session.

### VRF commented out at source 2026-08-25 (interim, on `internet-label-rename`)

Rather than gate the feature properly, the operator asked for VRF to be **commented out and revisited later**. Two files changed, **uncommitted**:

- `roles/smc_network/templates/netplan.yml.j2` — the per-interface `vrf:` key and the top-level `vrfs:` block are each wrapped in a Jinja `{# … #}` comment carrying a banner that states the netplan
  0.104 incompatibility, the over-broad selector, and the two conditions required before re-enabling. **The computation is deliberately left intact** (`vrf_candidates`, `tablenames`, `tableids`,
  `vrf_membership`, `vrfs` still build and simply go unused), so re-enabling is just deleting the two comment wrappers. Safe because `tablenames`/`tableids` are read by nothing else in the template.
- `roles/smc_network/tasks/ubuntu.yml` — the `Ensure VRF kernel module is loaded` modprobe task commented out. Nothing else needs the module: the multi-WAN tasks in the same file were already
  commented out, and `smc_dhcpd`'s `vrf` strings are documentation about an unrelated concept. It is a no-op on live hosts — commenting it out does not unload a module a previous run loaded.

`roles/smc_network/templates/multiwan-setup.sh.j2` carries the same `role: internet|starlink` selector but needed **no change** — every task that deploys it is already commented out, so it is never
rendered.

**Verification that matters:** `ansible-playbook smc_bases.yml -i inventories/rcp/prod --limit yakanarra-smc01 --tags network --check --diff` reports the netplan template task as **`ok`, not
`changed`** — i.e. the commented template renders **byte-identical** to the hand-repaired file already on the box. That simultaneously proves the template no longer emits VRF *and* that the
`awk`-strip recovery above reproduced the true pre-VRF rendering. Only 4 tasks would change on a real run, all pre-existing role behaviour (three apt-cache tasks and the hostnamed/journald/rsyslog
restart); the VRF modprobe no longer appears among them.

**Still true after this change:** `--tags network` remains untested on the fleet at large — the role has not run on 15 of 17 nodes in over a year, so it may surface unrelated drift. Prefer tagged runs
that exclude `network` unless there is a reason to re-render netplan. **The underlying design faults are unfixed, only silenced:** the selector is still `role`-based and the template task still writes
before `netplan generate` validates, with no `backup: yes` — that last one converts any future template error into the same reboot-isolation hazard and is worth fixing on its own merits.

## `smc_rsyslog`'s squid stop fails on squid's own drain window — fixed 2026-08-26

**Symptom:** `TASK [smc_rsyslog : Stop squid before repointing its log directory]` → `FAILED! => "Unable to stop service squid: Job for squid.service canceled."` — and the play aborts, leaving the
node half-relocated.

**The stop actually succeeds.** Timeline captured on yakanarra-smc01 2026-08-26:

```
14:44:47  systemd[1]: Stopping Squid Web Proxy Server...
14:45:18  systemd[1]: squid.service: Deactivated successfully     <- 31s later
14:45:19  systemd[1]: Started Squid Web Proxy Server
```

squid drains established connections for **`shutdown_lifetime` (squid default 30s**, not overridden anywhere in `/etc/squid` on the rcp fleet) before exiting. That exceeds how long the `systemd`
module waits on the DBus job, so the module reports the job cancelled and fails the task while systemd completes the stop a second or two later. Same failure hit the 2026-07-23 fleet rollout — it was
worked around then, not fixed, so it recurred.

**Why aborting here is the dangerous part, not the stop itself:** the block's remaining tasks — create the tmpfs subdir, remove the real dir, symlink, restart squid, then mosquitto, then the
**`/etc/tmpfiles.d/smc-log-groups.conf`** rule — all get skipped. The specific state to fear is squid symlinked onto the tmpfs *without* that tmpfiles rule: tmpfs is wiped at boot, squid cannot create
its own log directory, it aborts, and iptables redirects tcp/80 into a dead proxy with no fail-open (RULE-016). On yakanarra the abort happened *before* the symlink, so it was benign — that is
ordering luck, not design.

**The fix** (`roles/smc_rsyslog/tasks/main.yml`) — do not trust the module's verdict, decide from the service's actual state:

```yaml
- name: Stop squid before repointing its log directory
  systemd: { name: squid, state: stopped }
  register: smc_squid_stop
  failed_when: false            # module can report "canceled" while the stop still completes
- name: Wait for squid to finish draining and stop
  command: systemctl is-active squid
  register: smc_squid_active
  changed_when: false
  failed_when: false
  check_mode: false
  until: smc_squid_active.stdout | trim != 'active'
  retries: 20                   # 20 x 3s = 60s, comfortably past the 30s drain
  delay: 3
  when: not ansible_check_mode
- name: Fail if squid is still running after the drain window
  fail: { msg: "squid did not stop within 60s ..." }
  when:
    - not ansible_check_mode
    - smc_squid_active.stdout | default('') | trim == 'active'
```

`failed_when: false` on its own would swallow a genuine failure; the poll-then-`fail` pair is what keeps the play honest — it still aborts if squid is really stuck, just on evidence rather than on a
DBus timeout. mosquitto's identical stop/symlink/start block was **left alone**: it has no drain and has never exhibited this.

**Deliberately NOT done:** setting `shutdown_lifetime 5` in `squid.conf`. That would also cure the symptom, but it changes live proxy behaviour fleet-wide (abrupt client disconnects on every squid
restart) to work around a deploy-tooling problem. Fix the tooling, not the service.

**`--check` cannot validate this block, for two independent reasons.** Check mode never actually stops squid, so the drain is not reproduced; and the pre-existing `file: state=absent` → `file:
state=link` pair fails in check mode with `the directory /var/log/squid is not empty, refusing to convert it`, because the removal is simulated and the symlink task then sees a populated directory.
That failure is not a defect and predates this change — it is the standard check-mode limitation for sequential delete-then-create chains. **Verify this block with a real run against one node, never
with `--check`.**

**Style note:** the new tasks use short module names (`systemd`, `command`, `fail`) and `smc_*` register prefixes, matching this file's existing convention. `ansible-lint` flags `fqcn[action-core]`
and `var-naming[no-role-prefix]` on them — it flags 34 findings across the whole file for the same two rules, so converting only the new t

## Guarded pre-split syslog reclaim in `smc_rsyslog` (added 2026-08-26)

**The gap it closes:** the wifi/dhcp/system log-group split relocates *future* writes onto the smc-groups tmpfs but strands whatever accumulated on real disk beforehand. yakanarra-smc01 held a 171 MB
`/var/log/syslog` + 66 MB `syslog.1` + 15 MB `auth.log` — **273 MB of `/var/log`, reclaimed to 25 MB.** Every future onboarding of a node that ran unsplit under load repeats this. Same shape as the
~44 GB orphaned-journal gap closed in `smc_system`, and fixed the same way: a task, not a manual cleanup.

**This is NOT a rotation-policy change.** Stock weekly rotation is adequate once the split is live — verified 2026-08-26, all 16 rcp nodes last rotated 2026-08-23 and sit at 1.8–16 MB. Post-split
growth is ~2 MB/day (measured 1,016 bytes/30s). Only the pre-split residue needs clearing, once.

### Three details that are load-bearing

1. **`su root syslog` inside the one-shot config is mandatory.** `/var/log` is `root:syslog 0775` on 14 of 16 rcp nodes, and logrotate refuses a group-writable parent unless told which user to drop
   to. `/etc/logrotate.conf` carries that directive globally so the daily timer is fine — **but a standalone config invoked directly does not inherit it** and silently skips every log with `parent
   directory has insecure permissions`. That error on all 13 stock logs looks exactly like fleet-wide breakage and is not; see the diagnosis note below.
2. **No `delaycompress`.** The stock rsyslog config has it, which is why forcing a rotation there only renames and reclaims nothing until a second pass. Dropping it means one pass actually frees
   space.
3. **The config goes in `/run`, never `/etc/logrotate.d`.** A file left in `logrotate.d` would re-run on every daily tick and fight the stock config for the same logs. It is written, used, and removed
   within the block.

### Guard discipline — runtime evidence, mirroring the journal reclaim

Gated on `findmnt -no FSTYPE /var/log/smc-groups` returning `tmpfs` — **runtime proof the split is genuinely live**, not "we copied the config file". A node whose tmpfs failed to mount still has
rsyslog writing everything to `/var/log/syslog`, and rotating there would quietly discard live logs on a schedule while the real fault went unnoticed. `meta: flush_handlers` runs first so rsyslog is
already on the split config before its size is judged. A size floor, `smc_rsyslog_syslog_reclaim_min_mb` (default 50), makes it self-limiting: after the reclaim syslog is a few KB, so the gate fails
on every later run.

### Verified both ways on yakanarra, 2026-08-26

- **Skip path** — default threshold, syslog small: reclaim tasks not entered.
- **Fire path** — `-e smc_rsyslog_syslog_reclaim_min_mb=0`: all three tasks changed; syslog rotated and recreated; `auth.log` recreated on the next authpriv event (rsyslog recreates on write, so it is
  briefly absent — expected, not a fault); one-shot config gone from `/run`; nothing added to `/etc/logrotate.d`; rsyslog/squid/mosquitto active; `logger` round-trip landed.
- **Re-run at default** — skipped again, confirming self-limiting.
- `smc_rsyslog` is **fully idempotent (0 changed)**. A `changed=3` on every run is the play preamble's apt housekeeping (`Clear APT/dpkg locks`, `Clean apt cache`, `Update apt cache`), not this role.

### Diagnosing "logrotate is skipping everything"

Before concluding rotation is broken fleet-wide, check **how logrotate was invoked**. `logrotate -f /etc/logrotate.d/rsyslog` bypasses `/etc/logrotate.conf` and therefore its global `su`; the daily
timer path does not. Confirm with `ls -l --time-style=+%F /var/log/syslog.1` across nodes — if they all share a recent rotation date, rotation is working and the invocation was the problem.asks would
make them the inconsistent ones.

---

## Code notes: where the long explanation goes, and what it can and cannot survive (2026-08-27)

`ansible-wifi` follows **RULE-006**: a **one- or two-line** comment in the source stating the constraint or hazard, and the long form — forensics, measurements, the incident it came from, the
alternatives rejected — in a *code note* anchored to the code it explains. The routing test is the only part worth memorising: **if being unaware of it would cause a bug, it goes in the file.** A note
is invisible to anyone without the extension, so safety-critical context must never be opt-in.

Never reference a note from the code. No "see code note", no note IDs — the notes are operator-local and a company-repo reader cannot follow the pointer.

### The extension is a private fork, not the Marketplace build

Installed as **`amalikn.code-context-notes`**, built from `github.com/amalikn/code-context-notes` (fork of MIT `jnahian/code-context-notes`). The publisher differs deliberately: a matching
publisher+name is the same extension ID, and VS Code would treat a higher Marketplace version as an update and silently replace the fork.

Storage is `.code-context-notes/` (renamed from `.code-notes/` on 2026-08-27), a symlink into `ansible-wifi-root-governance/`. The MCP server must be passed a matching `--storage-dir` or the
extension and the server write to different directories.

### What a note records, and the ranking that matters

Line range, a normalized `sha256` content hash, **three lines of verbatim context either side**, the authoring **branch**, and the **commit** — with `(dirty)` when the tree was modified, which it
nearly always is. The ranking is strict and is the whole design:

1. **content hash + context** — authoritative, content-addressed, immune to SHA rewriting
2. **commit ancestry** — tested by `git merge-base --is-ancestor`, *not* equality, so it stays true as the branch advances and becomes true at merge
3. **branch name** — a display label

**Metadata may only ever clear a warning, never raise one.** That is what makes merges, rebases and squash-merges degrade gracefully instead of dimming valid notes.

### Notes survive a checkout; their anchors do not

The store lives outside the repo, so `git checkout` never touches the notes — but an anchor is a line range into *one branch's* reality. Measured 2026-08-27: of 24 notes anchored on
`internet-label-rename`, tested against `master`, **21 were out of range**, 1 moved, 2 drifted, **0 exact**. `roles/smc_rsyslog/tasks/main.yml` is 26 lines on `master` against ~300 on the branch.

Out-of-range is not cosmetic: it **crashes extension activation**, and a crashed activation never regenerates `INDEX.json`, so a reload does not clear it. The fork re-anchors annotated files from disk
on a branch change, which handles the merge case, but it cannot invent code that is not on the branch.

### The operational rule

**Run `check_note_anchors.py` after any branch switch or out-of-editor edit — not only after authoring notes.** Re-anchoring is driven by `onDidChangeTextDocument`, which fires for *nothing* when a
`git checkout`, a `sed` pass, or an ansible-lint autofix rewrites a file nobody has open. Those edits leave every note in the file stale with nothing reporting it.

The checker classifies a hash mismatch as `MOVED` (the content is elsewhere in the file) or `DRIFTED` (it matches nowhere — the exact-match pass is spent and only fuzzy matching can still find it).
Both exit 0: they describe anchor *quality*, not a broken extension. Out-of-range remains the only exit 1.

### Storage has no history and no recovery

Verified 2026-08-27 rather than assumed: `git ls-files` returns zero for the store and **no commit in the governance repo's history has ever touched it**. The long-held belief that relocating notes to
governance versioned them was untrue — a `.gitignore` pattern written for another purpose had been quietly ignoring them. Untracked is now the recorded decision, and the consequence is not softened:
the `.md` files are the sole source of truth.

Full workflow, note types, and the three helper scripts: `skill-code-context-notes` (alias `skill-ccn`).
