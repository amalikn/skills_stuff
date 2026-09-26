# skill-smc Changelog

## Contents

- [20260927_0308 — smc_dhcpd: debounced hook and StartLimit adopted on the rehearsal branch; the vars-plugin and dhcpd.conf.j2 cautions recorded (v0.1.62 -> v0.1.63)](#20260927_0308--smc_dhcpd-debounced-hook-and-startlimit-adopted-on-the-rehearsal-branch-the-vars-plugin-and-dhcpdconfj2-cautions-recorded-v0162---v0163)
- [20260927_0258 — apn-cnmaestro01 hostname corrected to apn-cnmaestro01.apn.au (operator) (v0.1.61 -> v0.1.62)](#20260927_0258--apn-cnmaestro01-hostname-corrected-to-apn-cnmaestro01apnau-operator-v0161---v0162)
- [20260927_0252 — dhcpd start-limit: both fixes proved on the virtual SMC; the issue is filed in local-knowledge-ansible (v0.1.60 -> v0.1.61)](#20260927_0252--dhcpd-start-limit-both-fixes-proved-on-the-virtual-smc-the-issue-is-filed-in-local-knowledge-ansible-v0160---v0161)
- [20260927_0230 — netplan apply vs the dhcpd restart hook: isc-dhcp-server start-limit-hit recorded, reload surface named (v0.1.59 -> v0.1.60)](#20260927_0230--netplan-apply-vs-the-dhcpd-restart-hook-isc-dhcp-server-start-limit-hit-recorded-reload-surface-named-v0159---v0160)
- [20260926_2121 — OrbStack virtual SMC malik-rcp01: container-style host adaptations recorded; working-cache venvs absent (v0.1.58 -> v0.1.59)](#20260926_2121--orbstack-virtual-smc-malik-rcp01-container-style-host-adaptations-recorded-working-cache-venvs-absent-v0158---v0159)
- [20260926_1815 — Low-touch hook verified live on umoona-smc01; leases persist the hook variables; all devices on apn-cnmaestro01 (v0.1.57 -> v0.1.58)](#20260926_1815--low-touch-hook-verified-live-on-umoona-smc01-leases-persist-the-hook-variables-all-devices-on-apn-cnmaestro01-v0157---v0158)
- [20260924_1957 — SMC physical port order and usual cabling recorded (v0.1.56 -> v0.1.57)](#20260924_1957--smc-physical-port-order-and-usual-cabling-recorded-v0156---v0157)
- [20260924_1945 — x86 VLAN interface layout recorded with its Nautobot mirror; `ip -j` read confirmed (v0.1.55 -> v0.1.56)](#20260924_1945--x86-vlan-interface-layout-recorded-with-its-nautobot-mirror-ip--j-read-confirmed-v0155---v0156)
- [20260924_1522 — `ifPhysAddress` verified on all three snmpd canaries; the identity anchor is now confirmed over SNMP every collector cycle (v0.1.54 -> v0.1.55)](#20260924_1522--ifphysaddress-verified-on-all-three-snmpd-canaries-the-identity-anchor-is-now-confirmed-over-snmp-every-collector-cycle-v0154---v0155)
- [20260924_1222 — Neighbour table: mornington has refused 2,230 allocations at the 1024 cap; `gc_thresh1` = 1 corrected as not the cause of ARP loss (v0.1.53 -> v0.1.54)](#20260924_1222--neighbour-table-mornington-has-refused-2230-allocations-at-the-1024-cap-gc_thresh1--1-corrected-as-not-the-cause-of-arp-loss-v0153---v0154)
- [20260924_1205 — TP-Link site switches reached behind the SMC; `tplink-switch.sh` access, discovery and redacted config capture (v0.1.52 -> v0.1.53)](#20260924_1205--tp-link-site-switches-reached-behind-the-smc-tplink-switchsh-access-discovery-and-redacted-config-capture-v0152---v0153)
- [20260922_1750 — Overlayroot is RPi and WH only; x86 tmpfs paths differ per box; fping on three x86 SMCs (v0.1.51 -> v0.1.52)](#20260922_1750--overlayroot-is-rpi-and-wh-only-x86-tmpfs-paths-differ-per-box-fping-on-three-x86-smcs-v0151---v0152)
- [20260921_2242 — Low-touch provisioning: the Redis-backed script is the fleet's version, from ansible-wifi's big_push branch, not master (v0.1.50 -> v0.1.51)](#20260921_2242--low-touch-provisioning-the-redis-backed-script-is-the-fleets-version-from-ansible-wifis-big_push-branch-not-master-v0150---v0151)
- [20260921_1310 — Multi-SMC sites: any box reaches the whole management address space; jump-host and host-key consequences (v0.1.49 -> v0.1.50)](#20260921_1310--multi-smc-sites-any-box-reaches-the-whole-management-address-space-jump-host-and-host-key-consequences-v0149---v0150)
- [20260921_1237 — Plain-OpenSSH `ProxyJump` to devices behind an SMC box verified; nbn_accelerate `~/.ssh/config` block; per-site device host keys (v0.1.48 -> v0.1.49)](#20260921_1237--plain-openssh-proxyjump-to-devices-behind-an-smc-box-verified-nbn_accelerate-sshconfig-block-per-site-device-host-keys-v0148---v0149)
- [20260920_2342 — Path checking widened past five files; 20 split filenames joined; ansible-wifi declared as a sibling root (v0.1.47 -> v0.1.48)](#20260920_2342--path-checking-widened-past-five-files-20-split-filenames-joined-ansible-wifi-declared-as-a-sibling-root-v0147---v0148)
- [20260920_1846 — `snmpget` installed across rcp/nbn_accelerate; two fleet assumptions disproved (v0.1.46 -> v0.1.47)](#20260920_1846--snmpget-installed-across-rcpnbn_accelerate-two-fleet-assumptions-disproved-v0146---v0147)
- [20260918_1700 — teleport-tunnel.sh port convention for concurrent dispatch (v0.1.45 -> v0.1.46)](#20260918_1700--teleport-tunnelsh-port-convention-for-concurrent-dispatch-v0145---v0146)
- [20260918_1620 — `--cluster=` vs `--proxy=` incident documented: an agent misdiagnosis that faked a real outage (v0.1.44 -> v0.1.45)](#20260918_1620----cluster-vs---proxy-incident-documented-an-agent-misdiagnosis-that-faked-a-real-outage-v0144---v0145)
- [20260918_1153 — unified-network-controller added as a Related Workspace (v0.1.43 -> v0.1.44)](#20260918_1153--unified-network-controller-added-as-a-related-workspace-v0143---v0144)
- [20260917_0001 — Other Raspberry Pi OS options assessed; Ubuntu Server remains the only recommended full-SMC platform (v0.1.42 -> v0.1.43)](#20260917_0001--other-raspberry-pi-os-options-assessed-ubuntu-server-remains-the-only-recommended-full-smc-platform-v0142---v0143)
- [20260917_0000 — Ubuntu Server retained for Raspberry Pi SMCs; Core is a greenfield-only option pending an appliance canary (v0.1.41 -> v0.1.42)](#20260917_0000--ubuntu-server-retained-for-raspberry-pi-smcs-core-is-a-greenfield-only-option-pending-an-appliance-canary-v0141---v0142)
- [20260917_1620 — teleport-tunnel.sh added: generic ansible-wifi-inventory-driven tunnel helper, moved from skill-cambium (v0.1.40 -> v0.1.41)](#20260917_1620--teleport-tunnelsh-added-generic-ansible-wifi-inventory-driven-tunnel-helper-moved-from-skill-cambium-v0140---v0141)
- [20260914_1300 — Cambium radio/AP estate by flavour recorded from the cambium-swap continuity project (v0.1.39 -> v0.1.40)](#20260914_1300--cambium-radioap-estate-by-flavour-recorded-from-the-cambium-swap-continuity-project-v0139---v0140)
- [20260911_1732 — Per-pin activation timeline tool added: correlate-pin-activation.sh, fixes a live-confirmed lease join-order bug (v0.1.38 -> v0.1.39)](#20260911_1732--per-pin-activation-timeline-tool-added-correlate-pin-activationsh-fixes-a-live-confirmed-lease-join-order-bug-v0138---v0139)
- [20260911_1240 — Incident closed: all 3 sites' fix + recovery confirmed live in references/13_known-issues.md (v0.1.37 -> v0.1.38)](#20260911_1240--incident-closed-all-3-sites-fix--recovery-confirmed-live-in-references13_known-issuesmd-v0137---v0138)
- [20260911_1210 — Correction: kaltjiti-fergon-smc01 was never affected; bungardi-smc01 fixed live (v0.1.36 -> v0.1.37)](#20260911_1210--correction-kaltjiti-fergon-smc01-was-never-affected-bungardi-smc01-fixed-live-v0136---v0137)
- [20260911_1120 — bungardi-smc01 confirmed as third broken site; Eclipse "PIN Last Issued" admin report documented as a third corroborating evidence source (v0.1.35 -> v0.1.36)](#20260911_1120--bungardi-smc01-confirmed-as-third-broken-site-eclipse-pin-last-issued-admin-report-documented-as-a-third-corroborating-evidence-source-v0135---v0136)
- [20260911_1115 — Pin-activation diagnosis added: two independent mechanisms, `audit-pin-activation.sh`, portal-FQDN-regression capture, live fleet case study (v0.1.34 -> v0.1.35)](#20260911_1115--pin-activation-diagnosis-added-two-independent-mechanisms-audit-pin-activationsh-portal-fqdn-regression-capture-live-fleet-case-study-v0134---v0135)
- [20260908_1955 — skill-ai-it refresh: navigation-control upgrade, `check_governance.py` adopted, `AI_NAVIGATION.md` declared project-managed (v0.1.33 -> v0.1.34)](#20260908_1955--skill-ai-it-refresh-navigation-control-upgrade-check_governancepy-adopted-ai_navigationmd-declared-project-managed-v0133---v0134)
- [20260908_1515 — `wifi-02.activ8me.net.au` is APN's own LVS VIP, not a third party; port-80 source-IP allowlist failure mode; reject-vs-drop diagnostics (v0.1.32 -> v0.1.33)](#20260908_1515--wifi-02activ8menetau-is-apns-own-lvs-vip-not-a-third-party-port-80-source-ip-allowlist-failure-mode-reject-vs-drop-diagnostics-v0132---v0133)
- [20260908_1430 — galiwinku-smc01 multi-WAN session write-back: ECMP hash-pinning root cause, VRF-disable landed, topology/monitoring gaps (v0.1.31 -> v0.1.32)](#20260908_1430--galiwinku-smc01-multi-wan-session-write-back-ecmp-hash-pinning-root-cause-vrf-disable-landed-topologymonitoring-gaps-v0131---v0132)
- [20260908_1330 — Backdoor SSH access documented: raw reverse-tunnel path around a hung Teleport node agent, confirmed live against nbn_accelerate (v0.1.30 -> v0.1.31)](#20260908_1330--backdoor-ssh-access-documented-raw-reverse-tunnel-path-around-a-hung-teleport-node-agent-confirmed-live-against-nbn_accelerate-v0130---v0131)
- [20260908_1200 — Pack-structure self-audit: RUNBOOK version drift, install.md staleness, reference-update-discipline gap, vestigial evidence/, and archcore status promotion (v0.1.29 -> v0.1.30)](#20260908_1200--pack-structure-self-audit-runbook-version-drift-installmd-staleness-reference-update-discipline-gap-vestigial-evidence-and-archcore-status-promotion-v0129---v0130)
- [20260907_1600 — Two Ansible silent-failure gotchas, an `rcp` systemd-mask fix, and the `auto_reboot: 0` truthy-string bug fed back from `ansible-wifi` (v0.1.28 -> v0.1.29)](#20260907_1600--two-ansible-silent-failure-gotchas-an-rcp-systemd-mask-fix-and-the-auto_reboot-0-truthy-string-bug-fed-back-from-ansible-wifi-v0128---v0129)
- [20260907_1530 — Silent Total Hang confirmed on `rcp` (pandanus-park-smc01), first non-`wh` instance (v0.1.27 -> v0.1.28)](#20260907_1530--silent-total-hang-confirmed-on-rcp-pandanus-park-smc01-first-non-wh-instance-v0127---v0128)
- [20260907_1200 — Standing write-back contract added to SKILL.md: the update obligation now travels with the skill, not each consuming project's governance file (v0.1.26 -> v0.1.27)](#20260907_1200--standing-write-back-contract-added-to-skillmd-the-update-obligation-now-travels-with-the-skill-not-each-consuming-projects-governance-file-v0126---v0127)
- [20260904_1000 — WAN uplink dead-DHCP failure mode documented, self-heal cron distinguished from real flapping (v0.1.25 -> v0.1.26)](#20260904_1000--wan-uplink-dead-dhcp-failure-mode-documented-self-heal-cron-distinguished-from-real-flapping-v0125---v0126)
- [20260827_1800 — Code notes documented as an authoring surface; stale lint paragraph corrected (v0.1.24 -> v0.1.25)](#20260827_1800--code-notes-documented-as-an-authoring-surface-stale-lint-paragraph-corrected-v0124---v0125)
- [20260825_1800 — Raspberry Pi capture group added to the broad collector (v0.1.23 -> v0.1.24)](#20260825_1800--raspberry-pi-capture-group-added-to-the-broad-collector-v0123---v0124)
- [20260825_1745 — broad diagnostic collector added; narrow collector's interfacecheck path corrected (v0.1.22 -> v0.1.23)](#20260825_1745--broad-diagnostic-collector-added-narrow-collectors-interfacecheck-path-corrected-v0122---v0123)
- [20260818_1350 — pre-push gate mechanics corrected, plaintext-secret exposure recorded (v0.1.21 -> v0.1.22)](#20260818_1350--pre-push-gate-mechanics-corrected-plaintext-secret-exposure-recorded-v0121---v0122)
- [20260818_1300 — delye-smc01 RESOLVED; `overlay.size_ratio` proven inert; fleet percentages corrected (v0.1.20 -> v0.1.21)](#20260818_1300--delye-smc01-resolved-overlaysize_ratio-proven-inert-fleet-percentages-corrected-v0120---v0121)
- [20260818_1200 — RISE metric delivery path: agent mode, remote_write allowlist, and the alerting void (v0.1.19 -> v0.1.20)](#20260818_1200--rise-metric-delivery-path-agent-mode-remote_write-allowlist-and-the-alerting-void-v0119---v0120)
- [20260818_1130 — overlayroot copy_up cost model, `smc_rise_logcaps`, and three fleet-class findings (v0.1.18 → v0.1.19)](#20260818_1130--overlayroot-copy_up-cost-model-smc_rise_logcaps-and-three-fleet-class-findings-v0118--v0119)
- [20260803_1825 — new-looma-smc01 second whole-host outage confirmed via live Prometheus (v0.1.17 → v0.1.18)](#20260803_1825--new-looma-smc01-second-whole-host-outage-confirmed-via-live-prometheus-v0117--v0118)
- [20260803_1810 — Grafana CW exploration unblocked: dashboard inventory + RISE metric names (v0.1.16 → v0.1.17)](#20260803_1810--grafana-cw-exploration-unblocked-dashboard-inventory--rise-metric-names-v0116--v0117)
- [20260803_1745 — ClamAV freshclam root cause confirmed: ClamAV 0.103.x end-of-life (v0.1.15 → v0.1.16)](#20260803_1745--clamav-freshclam-root-cause-confirmed-clamav-0103x-end-of-life-v0115--v0116)
- [20260803_1730 — Full NBN Accelerate fleet sweep: 28 hosts, hardware inventory, fleet-wide ClamAV finding (v0.1.14 → v0.1.15)](#20260803_1730--full-nbn-accelerate-fleet-sweep-28-hosts-hardware-inventory-fleet-wide-clamav-finding-v0114--v0115)
- [20260803_1615 — First live NBN Accelerate validation: confirms cluster comparison, finds ClamAV CDN-block (v0.1.13 → v0.1.14)](#20260803_1615--first-live-nbn-accelerate-validation-confirms-cluster-comparison-finds-clamav-cdn-block-v0113--v0114)
- [20260803_1545 — project-coherence sweep: routing/architecture staleness fixed (v0.1.12 → v0.1.13)](#20260803_1545--project-coherence-sweep-routingarchitecture-staleness-fixed-v0112--v0113)
- [20260803_1530 — smc_ltp/"low touch" mechanism confirmed: manual step, no enforcement (v0.1.11 → v0.1.12)](#20260803_1530--smc_ltplow-touch-mechanism-confirmed-manual-step-no-enforcement-v0111--v0112)
- [20260803_1515 — smc_ltp/"low touch" correlation resolved: 3 sites added to the group, 7 members confirmed (v0.1.10 → v0.1.11)](#20260803_1515--smc_ltplow-touch-correlation-resolved-3-sites-added-to-the-group-7-members-confirmed-v0110--v0111)
- [20260803_1445 — "Low touch" onboarding method and site deployment history added (v0.1.9 → v0.1.10)](#20260803_1445--low-touch-onboarding-method-and-site-deployment-history-added-v019--v0110)
- [20260803_1400 — smc_ltp properly explored and documented; membership undercount fixed (v0.1.8 → v0.1.9)](#20260803_1400--smc_ltp-properly-explored-and-documented-membership-undercount-fixed-v018--v019)
- [20260803_1230 — NBN Accelerate cluster gap-fill (v0.1.7 → v0.1.8)](#20260803_1230--nbn-accelerate-cluster-gap-fill-v017--v018)
- [20260731_1312 — Fed back Pia Wadjari labeling case + proposed convention; multiwan-disable git archaeology](#20260731_1312--fed-back-pia-wadjari-labeling-case--proposed-convention-multiwan-disable-git-archaeology)
- [20260731_1215 — Two residual gaps closed from the routing-issue Problem 3 deep-dive](#20260731_1215--two-residual-gaps-closed-from-the-routing-issue-problem-3-deep-dive)
- [20260731_1330 — Broadened cross-repo feed-back governance (prevent future full-sweep need)](#20260731_1330--broadened-cross-repo-feed-back-governance-prevent-future-full-sweep-need)
- [20260731_1245 — Full local-knowledge-ansible/ansible-wifi extraction pass](#20260731_1245--full-local-knowledge-ansibleansible-wifi-extraction-pass)
- [20260729_2324 — WAN-routing coverage expansion + reusable diagnostic scripts (APN routing-issue investigation)](#20260729_2324--wan-routing-coverage-expansion--reusable-diagnostic-scripts-apn-routing-issue-investigation)
- [20260728_1240 — v0.1.5: captive-portal PHP SAPI correction + APPPATH/cache failure mode + Ansible tag hazard (project-coherence run)](#20260728_1240--v015-captive-portal-php-sapi-correction--apppathcache-failure-mode--ansible-tag-hazard-project-coherence-run)
- [20260703_1300 — v0.1.4: DNS architecture corrections + garimba-smc01 failure mode (project-coherence run)](#20260703_1300--v014-dns-architecture-corrections--garimba-smc01-failure-mode-project-coherence-run)
- [20260626_1845 — v0.1.3: project-coherence checklist + references/10-13 content update](#20260626_1845--v013-project-coherence-checklist--references10-13-content-update)
- [20260626_1820 — Coherence sweep: repomix config, adapter.md, spec, ARCHITECTURE.md](#20260626_1820--coherence-sweep-repomix-config-adaptermd-spec-architecturemd)
- [20260626_1812 — README and ARCHITECTURE added](#20260626_1812--readme-and-architecture-added)
- [20260626_1810 — Archcore promotion](#20260626_1810--archcore-promotion)
- [20260626_1808 — Governance scaffold bootstrap](#20260626_1808--governance-scaffold-bootstrap)
- [0.1.2 — 2026-06-26](#012--2026-06-26)
- [0.1.1 — 2026-06-26](#011--2026-06-26)
- [Unreleased — 2026-05-08](#unreleased--2026-05-08)
- [0.1.0 — 2026-04-15](#010--2026-04-15)

---

## 20260927_0308 — smc_dhcpd: debounced hook and StartLimit adopted on the rehearsal branch; the vars-plugin and dhcpd.conf.j2 cautions recorded (v0.1.62 -> v0.1.63)

`references/08_ansible-authoring.md`: new section on the `smc_dhcpd` change committed on ansible-wifi branch `unc-virtual-smc-malik-rcp01` (operator's yes, 2026-09-27): the dispatcher hook debounced
through one re-armed transient unit, `StartLimitIntervalSec=60`/`StartLimitBurst=20` in the role's unit file; 1 restart under a full apply and a bridge bounce on the stage box. Two cautions learnt
applying it: a play outside the repo gets no topology variables from the vars plugin (pass them with `-e @`), and a full `smc_dhcpd` run on the stage box would drop the Step 4 device-seen `execute()`
line from `dhcpd.conf` until Q10's template variable exists in `dhcpd.conf.j2`.

## 20260927_0258 — apn-cnmaestro01 hostname corrected to apn-cnmaestro01.apn.au (operator) (v0.1.61 -> v0.1.62)

`references/08_ansible-authoring.md`: the on-prem cnMaestro hostname read `apn-cnmaestro01.apn.net.au` (2026-09-26 write-back); the operator corrected it to `apn-cnmaestro01.apn.au` on 2026-09-27, and
it resolves (52.64.230.196). One-word fix; `USER_STATED`.

## 20260927_0252 — dhcpd start-limit: both fixes proved on the virtual SMC; the issue is filed in local-knowledge-ansible (v0.1.60 -> v0.1.61)

`references/06_failure-modes.md`: the 2026-09-27 section now carries the proof — on `malik-rcp01` a `StartLimitIntervalSec=60`/`StartLimitBurst=20` drop-in kept `isc-dhcp-server` active through a full
`netplan apply` (6 restarts) and a three-bridge bounce (3 restarts); a debounced hook (`systemd-run --on-active=5`, re-armed per event) did the same with 1 restart each. The issue with the hook's
source, the unit file and the options lives in local-knowledge-ansible issues/rcp-fleet/rcp-dhcpd-start-limit-on-link-flap-20260927_0238.md (commit `8a43a95`, proof section added the same night). No
playbook changed; physical hardware still `UNVERIFIED`.

## 20260927_0230 — netplan apply vs the dhcpd restart hook: isc-dhcp-server start-limit-hit recorded, reload surface named (v0.1.59 -> v0.1.60)

`references/06_failure-modes.md`: new section on the `smc_dhcpd` role's networkd-dispatcher `routable.d` hook restarting `isc-dhcp-server` for every link that becomes routable, so a full `netplan
apply` (twelve links bouncing at once on `malik-rcp01`) drives the unit into systemd's `start-limit-hit` even on an unchanged config; the reload surface the role's own handler uses (`netplan generate`
then `networkctl reload`) touches only changed links, and a reset-failed plus restart of the bridge-bound services belongs after any apply or rollback. Found 2026-09-27 during
unified-network-controller's Step 7 rehearsal (its `wc-local/scripts/smc_intent.py`), on the virtual SMC only; the physical-box link count under a real reload is marked `UNVERIFIED`. No change to any
playbook.

## 20260926_2121 — OrbStack virtual SMC malik-rcp01: container-style host adaptations recorded; working-cache venvs absent (v0.1.58 -> v0.1.59)

From the unified-network-controller supplement Step 4 rehearsal (2026-09-26 evening).

- `references/11_vagrant-lab.md` §12.6 (new): the stage host `malik-rcp01` is an OrbStack amd64 Ubuntu 22.04 machine (`lxc`), not a Vagrant VM. Every real-box assumption `smc_bases.yml` made false
  there and its one adaptation, all behind the stage host var `smc_bases_container: true`: no bootloader (GRUB block skipped), the management NIC is also the WAN (`use-routes: true`), networkd's DUID
  moved the DHCP lease (`dhcp-identifier: mac`), `/etc/cloud` absent (already ignored), and the `on commit` block only for `smc_ltp` (stage-only `[malik_smc_ltp]` group; never `smc_ltp.yml` against
  it, a logging stand-in replaces the cnMaestro script). Also: `setsid` is not on macOS; `ntp`'s postinst takes a minute in the container; package retries hide a failure for an hour.
- `SKILL.md` Runtime Environments: both working-cache venvs the section named are absent on this Mac (verified); Homebrew `ansible-playbook` core 2.21.4, `ansible-lint` and `yamllint` are what run
  ansible-wifi until a venv is created.
- `references/06_failure-modes.md` (new subsection) and `references/01_overview.md`: an expired `tsh` certificate makes every device look failed (94 of 156 critical on 2026-09-25, 17,309 `cert has
  expired` lines, no alarm); `aurukun-smc01` refusing SSH on 2026-09-22/23 read as a site failure while smc02 and smc03 were fine. Check `tsh status` per cluster first; the multi-SMC fallback recorded
  as `USER_STATED` on 2026-09-21 is now implemented in the controller's pushes.
- `references/08_ansible-authoring.md`: the controller's proposed second `execute()` line on the low-touch hook (gated, Option 43 unchanged per Q9), where the spool lives, and the stage rehearsal
  pointer.

## 20260926_1815 — Low-touch hook verified live on umoona-smc01; leases persist the hook variables; all devices on apn-cnmaestro01 (v0.1.57 -> v0.1.58)

`references/08_ansible-authoring.md`: read-only verification on umoona-smc01 for the unified-network-controller's Step 4 baseline. The live `on commit` block equals the `master` template and
`big_push` does not change it (only the script: the box runs the 4,509-line build with redis-server active); provisioning shared-network `192.168.11.0/24`, 20-second Cambium leases, Option 43 still
`https://3.105.84.178`; `dhcpd.leases` persists `clhw`, `clip`, `clvci` per lease (811 Cambium blocks of 1,338); one `log.<MAC>` per device under `/var/local/cnmaestro-provisioning/`. Aurukun's smc02
and smc03 are Teleport nodes but not Nautobot Devices. Operator statement, 2026-09-26: every apn and nbn device is managed by on-prem `apn-cnmaestro01` (Teleport node present; the stated hostname
`apn-cnmaestro01.apn.net.au` did not resolve publicly). Capture kept in unified-network-controller `captures/`.

## 20260924_1957 — SMC physical port order and usual cabling recorded (v0.1.56 -> v0.1.57)

`references/02_service-map.md`: left-to-right port order for the BOXER-6404 and BOXER-6641 as the operator stated it, the usual cabling (ports 1-2 internet, port 3 trunk to switch 1, port 4 trunk to
switch 2) confirmed on mornington, kalumburu and hope-vale, how the uplink VLANs split across the two trunks, and that `vlan621`/`vlan631` held no address on either 6641 site.

## 20260924_1945 — x86 VLAN interface layout recorded with its Nautobot mirror; `ip -j` read confirmed (v0.1.55 -> v0.1.56)

`references/02_service-map.md`: the x86 boxes' bridge-member sub-interfaces and standalone internet VLAN interfaces, counted on the three canaries (10 on the BOXER-6404, 16 on each 6641), the one-call
JSON read (`ip -d -j link show type vlan`, iproute2 5.15), and unified-network-controller's per-box Nautobot record of them (`virtual` interfaces with parent, bridge and site VLAN; bridges per device,
not in the device-type template; drift reported against the box and `topology_vars`). Also recorded there: the operator's target (2026-09-24), Nautobot as the source each SMC syncs its network setup
from and applies, with rollback; the box read is the retrofit.

## 20260924_1522 — `ifPhysAddress` verified on all three snmpd canaries; the identity anchor is now confirmed over SNMP every collector cycle (v0.1.54 -> v0.1.55)

`references/snmp-oid-registry.yaml`: `.1.3.6.1.2.1.2.2.1.6` ifPhysAddress moves from `not_yet_read` to the verified set, walked on kalumburu-smc01, mornington-smc01 (apn) and hope-vale-smc01 (nbn).
The physical `enp*` ports report their burned-in MACs, equal to what Nautobot holds; the lowest (the identity anchor) is `enp1s0` on all three. Consumer: unified-network-controller
`wc-local/scripts/smc_collect.py`, now run by the 20-minute collector cycle, which reports anchor drift and never writes it. Also recorded: `sysUpTime` is the snmpd agent's uptime, not the host's (0
days on all three, snmpd installed today), so the SMC uptime OpenWISP shows is agent uptime; `hrSystemUptime` is added to `not_yet_read`. Two governance failures that predated this entry are fixed:
`SKILL.md` now names the consumer by its full path under the `apn-projects` sibling root, and the example marker in `references/08_ansible-authoring.md` is back on the line it exempts (a rewrap had
moved it down one).

## 20260924_1222 — Neighbour table: mornington has refused 2,230 allocations at the 1024 cap; `gc_thresh1` = 1 corrected as not the cause of ARP loss (v0.1.53 -> v0.1.54)

`ip -s ntable show name arp_cache` (read-only): mornington-smc01, 48 weeks up at 795 entries, shows `forced_gc_runs` 5,666,597 and `table_fulls` 2,230, so it has hit the 1024 hard cap and dropped
packets; kalumburu-smc01 shows 145 and 0. `13_known-issues.md`'s neighbour-table section now carries the counters, what each threshold does to customer traffic, monitoring and the SMC, why
whole-subnet sweeps make it worse, and the proposal reordered (`gc_thresh3` is the fix, `gc_thresh1` a nice-to-have) with a fleet `table_fulls` survey as the first rollout step. Correction to v0.1.53:
the `gc_thresh1` of 1 is not why quiet devices leave ARP; both tables exceed the kernel default of 128 too. `16_tplink-site-switches.md` and `scripts/tplink-switch.sh` say so now.

## 20260924_1205 — TP-Link site switches reached behind the SMC; `tplink-switch.sh` access, discovery and redacted config capture (v0.1.52 -> v0.1.53)

Both kalumburu switches (10.255.0.2 Switch1, 10.255.0.3 Switch 2, SG2428P firmware 5.30.1) logged into with KeePass `/Network/tplink switch` from kalumburu-smc01. New
`references/16_tplink-site-switches.md`: the per-site candidates from unified-network-controller's sweeps, the credential, the SSH quirks (`HostKeyAlgorithms=+ssh-rsa`, `MACs=hmac-sha2-256`, no exec
channel, CR for Enter, swallowed first keystroke, client-first banner), the three `enable` cases, why discovery cannot use ARP (`gc_thresh1` is 1 on the SMCs, not the kernel's 128), and the rule never
to sweep `bridge_501`. New `scripts/tplink-switch.sh` with `tplink_cli_driver.py`: read-only commands, `--discover`, `--shell` and `--backup` (redacted running-config, leak-checked against the known
passwords). Telnet is refused on both switches. The login password was once typed into Switch1's CLI after an `enable` that needed none; the driver now sends a password only when a prompt asks for
one. RUNBOOK routing, SKILL.md references and `scripts/README.md` updated. `13_known-issues.md` gains a neighbour-table finding and a proposed `gc_thresh1/2/3` standard of 1024/4096/16384 (proposal
only; the SMCs run 1/512/1024 and mornington holds 757 entries).

## 20260922_1750 — Overlayroot is RPi and WH only; x86 tmpfs paths differ per box; fping on three x86 SMCs (v0.1.51 -> v0.1.52)

SKILL.md said "All SMC boxes run overlayroot". Wrong, per the operator (2026-09-22): only RPi and WH boxes do. It now says so, matching what `references/07_hardware-overlay.md` already recorded per
flavour. `07_hardware-overlay.md` gains an x86 section: plain ext4 root (an apt install persists), and the tmpfs mounts, which differ per box. `/tmp` is tmpfs on mowanjum-smc01 but ext4 on
hope-vale-smc01, so use `/run`. fping 5.1 was installed by apt on mowanjum-smc01, hope-vale-smc01 and horn-island-smc01 for unified-network-controller's reachability pre-check. No ansible-wifi role
installs it yet.

## 20260921_2242 — Low-touch provisioning: the Redis-backed script is the fleet's version, from ansible-wifi's big_push branch, not master (v0.1.50 -> v0.1.51)

`references/04_dependency-tree.md` resolves its open "naming collision" item: the Redis-dependent `cnmaestro-provisioning` service and the `smc_ltp` low-touch script are one mechanism at two versions.
`master` holds the older 3,222-line script with no Redis; the unmerged `big_push` branch (Daniel Gravolin, 36 commits) holds the 4,514-line Redis version. Checked live, read-only: `umoona-smc01` runs
`big_push` commit `40c283b6`; `pandanus-park-smc01` runs a copy matching no commit (deployed from uncommitted changes). Consumer: `unified-network-controller`'s architecture brief, point 3.

## 20260921_1310 — Multi-SMC sites: any box reaches the whole management address space; jump-host and host-key consequences (v0.1.49 -> v0.1.50)

`references/01_overview.md` "Remote Access": at a multi-SMC site the boxes share one management address space as a VRRP-style set, and failover runs through the switching layer and the wireless
network, so any box is a valid jump host for every device at the site (operator-stated, 2026-09-21, aurukun as the example). A fixed `ProxyJump` does not fail over on its own; device host keys stay
keyed by site. Consumer: `unified-network-controller`'s options register, D3.6 sketch — one site agent and one Nautobot Namespace per site, not per box.

## 20260921_1237 — Plain-OpenSSH `ProxyJump` to devices behind an SMC box verified; nbn_accelerate `~/.ssh/config` block; per-site device host keys (v0.1.48 -> v0.1.49)

`references/01_overview.md` "Remote Access" gains a verified path from the operator Mac straight to a device behind an SMC box: OpenSSH `ProxyJump`, with `tsh proxy ssh` as the first hop's
`ProxyCommand` and an ordinary `-W` channel through the box. Nothing is installed on the box and the device credential stays on the Mac. Verified 2026-09-21 against `galiwinku-smc01` →
`GAL_XV2_AP32_IP3_32` (`10.255.3.32`).

- `~/.tsh/known_hosts` trusts the host CA only for `*.teleport.<domain>`; a bare node name as `HostName` fails host-key verification. `HostKeyAlias` to the FQDN form, or using the FQDN, fixes it.
- An `nbn_accelerate` wildcard block (`*.teleport.communitywifi.net.au`, `--proxy=` only) now sits in the operator's `~/.ssh/config` beside the `tsh config`-generated APN one, verified live.
- Device host keys collide across sites because management subnets overlap: key them per site (`HostKeyAlias=<site>-<ip>` or a per-site `UserKnownHostsFile`).
- Device password via `sshpass -e` from an env var, never `-p` (argv exposure).

Consumer: `unified-network-controller` `docs/inventory/device-access-via-proxyjump-and-tbot-20260921_1232.md`, which also records the tbot (production) form and its open checks.

## 20260920_2342 — Path checking widened past five files; 20 split filenames joined; ansible-wifi declared as a sibling root (v0.1.47 -> v0.1.48)

Ported from `unified-network-controller`'s staleness audit of the same evening, which found the same defects there and promoted the underlying rule to
`unified-network-controller/.archcore/rules/govern-a-derived-population-never-a-hand-list.rule.md`.

**Nineteen split filenames, the most of any package in this family.** A wide table cell wraps mid-filename and leaves the token ending in a backslash with its tail on the next row — unfollowable for a
reader, and invisible to `check_referenced_paths`, which skips anything that does not look like a path. So the defect hid from the very check that should have caught it. All joined across `SKILL.md`,
`references/07_hardware-overlay.md`, `references/13_known-issues.md` and `scripts/README.md`; one was a THREE-row split. `check_split_path_tokens()` now asserts the shape directly and scans every
markdown file in the package, not only the governance surfaces.

**`SURFACES` was a hand-list of five files**, so `ARCHITECTURE.md`, `PROFILE.md`, `SYSTEM_PROMPT.md` and anything added later were outside every path check. Now derived from the tree. `CHANGELOG.md`
and `SCRATCHPAD.md` are excluded with the reason stated in the code: both are append-only history, and SCRATCHPAD's 2026-06-26 entry recording that a dead `references/PROFILE.md` pointer was *removed*
reads to a path check as a live broken reference. Exempt history by marker, never by rewriting it. `references/**` is excluded for a different stated reason — its slash notation is mostly device
paths, CIDR blocks and systemd units rather than repo paths.

**`SIBLING_ROOTS` added, with `ansible-wifi` as the important one.** This package's entire subject is that repository, and its prose names roles, inventories and flavour files by their path there.
Those references are now *verified* rather than merely unchecked: if ansible-wifi renames a role, this package's routing into it fails loudly. An absent root prints SKIPPED, never passed.

**Bare basenames resolve on a unique match only.** `01_overview.md` unambiguously means `references/01_overview.md` within one package, so it resolves; a name carried by more than one file is reported
as ambiguous rather than silently accepted, and a rename still fails. Evidence-collector OUTPUT filenames (`MANIFEST.txt`, `SUMMARY.txt`, the numbered capture files), git refs (`origin/main`) and the
Apache log name `wifi/access` are registered as conditional paths with per-entry reasons — they are not repo paths despite the shape.

Both new check behaviours negative-tested in both directions. Checks **184 -> 286**.


## 20260920_1846 — `snmpget` installed across rcp/nbn_accelerate; two fleet assumptions disproved (v0.1.46 -> v0.1.47)

### Done — all 45 rcp/nbn_accelerate boxes now have `snmpget`

19 already had it, 25 were installed, and `mindi-rardi-smc01` completed on a retry after a dpkg lock cleared. Verified by a full re-run reporting **45/45 already present**. The other 314 SMC boxes
(`rct` 292, `wh` 20, `nbn_wh` 2) were deliberately left alone — do not assume `snmpget` exists on an `rct` box.

This closes the failure the work started from: a device sweep shelling out to `snmpget` from a box that lacked it recorded 20 healthy APs across two sites as unreachable.

### Two fleet-wide assumptions this disproved

- **`snmpget` presence never followed the flavour.** An earlier entry recorded it as an `rcp`-versus-`nbn_accelerate` split, drawn from three boxes that happened to line up. Surveying showed both
  flavours on both sides. Probe for a binary; never infer it from a label.
- **Overlayroot is not fleet-wide.** This pack states that all SMC boxes run overlayroot and lose writes on reboot. **None of the 45 rcp/nbn_accelerate boxes had it mounted**, which is why an apt
  install persists on them. The rule appears to hold on the `rct`/`wh` side, where it was presumably written. Check per box.

### Added — `scripts/install_packages.sh`, generic by request

Replaces the one-off snmp installer. Takes `--packages` and `--verify`, scopes by Teleport flavour, and assumes Ubuntu 22.04+ with no OS branching. It verifies the resulting binary rather than apt's
exit code, skips boxes that already have it, refuses boxes with overlayroot mounted unless `--force-overlay`, and defaults to 5 workers because these sites sit on constrained, sometimes satellite,
backhaul.

It also passes `DPkg::Lock::Timeout` so apt waits for the dpkg lock instead of losing the race. That came from `mindi-rardi-smc01`, which blocked itself: an earlier `apt-get install` of the same
package was **orphaned when its `tsh` session dropped** and held the lock while every later attempt failed against it. Do not kill an apt holding the lock without checking what it is — killing
mid-transaction can leave dpkg half-configured.

### Added — `scripts/survey_snmp_tooling.sh`

Read-only per-box report of `snmpget` presence and overlayroot state, flavour-scoped. Both scripts are cataloged in `scripts/README.md`.

## 20260918_1700 — teleport-tunnel.sh port convention for concurrent dispatch (v0.1.45 -> v0.1.46)

Operator instruction, while dispatching a live `get_config()` verification across the 4 Cambium device families: when more than one tunnel might be open at once — parallel subagents, or several device
families worked in one session — each family needs a fixed local port so concurrent tunnels never collide and a stale leftover on a shared port can't mask a fresh one. Also: agents were found calling
`tsh ssh -L ...` by hand instead of `scripts/teleport-tunnel.sh` for this dispatch — reinforced that the script is the required path, not raw `tsh`.

### Changed — `scripts/teleport-tunnel.sh`, `scripts/README.md`

- Added a port-convention block to both: reserved range `20101`-`20199` for ad hoc Cambium device-tunnel work, current fixed assignments XV2 `20101`, ePMP `20102`, cnWave `20103` (R195P needs no
  tunnel — nested SSH via the SMC box). Future assignments extend this list rather than picking numbers ad hoc.
- Also swapped remaining "cluster" wording in both files' prose for "Teleport target"/"Teleport deployment" (operator instruction, matching the 20260918_1620 entry's convention) — the literal
  `--cluster=` CLI flag name and the script's internal `CLUSTER` shell variable are the only exceptions, left as-is (real Teleport syntax / code rename out of scope).

### Notes

- No `check_governance.py` failure expected — verified by reading both files back after writing.

## 20260918_1620 — `--cluster=` vs `--proxy=` incident documented: an agent misdiagnosis that faked a real outage (v0.1.44 -> v0.1.45)

Two independent `cambium-swap` agent sessions ran `tsh ls`/`tsh ssh` against `teleport.communitywifi.net.au` using `--cluster=` instead of `--proxy=`, got `transport: authentication handshake failed:
EOF` on every attempt, and concluded (wrongly, on both counts) that the Teleport target was suffering a fleet-wide outage and that `hope-vale-smc01` was missing/decommissioned. The operator reproduced
and disproved both claims directly in under a minute: `tsh status` showed a fully valid cached session, `curl .../webapi/ping` returned a clean 200, and `tsh ls --proxy=teleport.communitywifi.net.au`
listed the full node roster including `hope-vale-smc01`, which then connected cleanly via `tsh ssh --proxy=... root@hope-vale-smc01`.

### Changed — `references/01_overview.md`

- Added an incident-dated addendum to the "Remote Access" section, directly under the existing 2026-09-17 `--proxy` tunnel note: `--cluster=` is never a substitute for `--proxy=` on this Teleport
  target, for any command (not just `-L` tunnels) — `teleport.communitywifi.net.au` is its own root Teleport target with its own login profile, not subordinate to `teleport.apn.au`, so `--cluster=`
  tries to route to it via a trust relationship that doesn't exist and fails with a transport-layer error indistinguishable from a real outage. Points to `scripts/teleport-tunnel.sh` (already correct)
  for the tunnel case, and flags that a hand-written `tsh ls`/`tsh ssh <cmd>` call still needs `--proxy=` added explicitly since the script doesn't cover that shape.

### Notes

- No new script — `scripts/teleport-tunnel.sh` already hardcoded `--proxy` correctly before this incident; the gap was agents bypassing it with raw `tsh` calls, not a defect in the script itself.
- No `check_governance.py` in this pack to run; verified by reading `references/01_overview.md` back after writing.

## 20260918_1153 — unified-network-controller added as a Related Workspace (v0.1.43 -> v0.1.44)

Operator split the "Option 3" FOSS controller workstream out of `cambium-swap` into its own sibling project, `unified-network-controller`, and asked that this pack and `skill-cambium` both know about
it, and it about them.

### Changed — `SKILL.md`

- Added `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller` to the Related Workspaces table: the FOSS network controller build (Nautobot + adapter layer) intended to eventually
  replace/complement `smc_cnmaestro_provisioning`'s role. Same cross-reference discipline as the existing `skill-cambium` relationship — call `skill-cambium` first for device-layer questions, this
  pack for SMC/Ansible-layer questions.

### Notes

- No `check_governance.py` in this pack to run; verified by reading `SKILL.md` back after writing.

## 20260917_0001 — Other Raspberry Pi OS options assessed; Ubuntu Server remains the only recommended full-SMC platform (v0.1.42 -> v0.1.43)

Extended the Raspberry Pi operating-system assessment in `references/07_hardware-overlay.md`. Raspberry Pi OS Lite is the closest technical alternative, but its Pi-specific Debian/APT model still
requires a complete port and qualification of the Ubuntu-based SMC automation without an established benefit. Debian has the same porting cost. OpenWrt is suitable only for a reduced router/AP
product; Fedora IoT/CoreOS, NixOS and comparable immutable/declarative choices create another full appliance-platform redesign. No production repository, fleet configuration or device image changed.
Primary Raspberry Pi and OpenWrt documentation was read directly on 2026-09-17. Manifest bumped to v0.1.43.

## 20260917_0000 — Ubuntu Server retained for Raspberry Pi SMCs; Core is a greenfield-only option pending an appliance canary (v0.1.41 -> v0.1.42)

Recorded a design recommendation in `references/07_hardware-overlay.md`: retain Ubuntu Server LTS for new Raspberry Pi SMCs. The existing fleet is a root-managed, package-based network appliance with
direct systemd, filesystem, netfilter, DHCP/DNS, hostapd, Teleport and monitoring control; RISE overlayroot already supplies a disposable-root strategy without changing that operating model. Ubuntu
Core is a valid embedded platform but is not a drop-in Server replacement: Core uses image/snap lifecycle management and strict confinement, and does not run classic snaps. Reconsider it only as a
separately designed, reduced-scope appliance with a Pi canary proving privileged networking, access, observability, update/recovery and constrained-link behaviour. No production repository, fleet
configuration or device image was changed. Canonical documentation was read directly on 2026-09-17. Manifest bumped to v0.1.42.

## 20260917_1620 — teleport-tunnel.sh added: generic ansible-wifi-inventory-driven tunnel helper, moved from skill-cambium (v0.1.40 -> v0.1.41)

### Added

- `scripts/teleport-tunnel.sh` — opens a `tsh` local-port-forward tunnel to any device reachable from a site's SMC box. Written first in `skill-cambium` for its own Cambium device-access work, then
  moved here on operator correction ("it's not Cambium tunnel, it's teleport tunnel") since this pack owns `tsh`/Teleport mechanics, per each pack's boundary. Resolves site -> SMC-host live from
  ansible-wifi's own `[<site>_smc_bases]` inventory groups (never hardcoded); only the flavour->cluster split is a small fixed table in the script, since that's structural (see
  `references/01_overview.md`'s Cluster split table), not per-site data.
- `scripts/README.md` — new `teleport-tunnel.sh` section and safety-table row.

### Notes

- `skill-cambium`'s own `just tunnel` recipe now calls this script's canonical path directly rather than keeping a copy — same cross-pack pattern `cambium-portal.sh` already uses in the other
  direction (that script lives in `skill-cambium`, `skill-smc` had nothing calling it).
- `python3 scripts/check_governance.py`: 182/182 passing.

## 20260914_1300 — Cambium radio/AP estate by flavour recorded from the cambium-swap continuity project (v0.1.39 -> v0.1.40)

**Trigger:** bootstrapping `apn/cambium-swap` (Cambium / cnMaestro vendor-continuity investigation after the reported Cambium Networks, Ltd administration notice) invoked this skill for SMC-side
Cambium touchpoints. Standing write-back contract applied.

**Added** to `references/07_hardware-overlay.md` a new section, "Cambium radio and AP estate by flavour (operator-stated 2026-09-14)":

- RCT runs ePMP 1000 2.4 GHz and 5 GHz Connectorized APs; WH runs ePMP 1000.
- Both are being migrated to MikroTik "metal" APs (operator confirmed) and XV2-2T0, because ePMP 1000 is old and unsupported.
- The `smc_ltp` hardware profiles are listed, alongside the full fleet list.
- ePMP terminology: AP and SM, not DN.
- SMC-side continuity facts:
  - DHCP option 43 carries the cnMaestro IP, not the FQDN.
  - `lt-cnmaestro.apn.au` is On-Premises.
  - The r195P routers are pinned to cnMaestro Cloud.
  - The live `cambium-rpz` zone contents are unrecorded.
  - The cnMaestro 90-day Anchor grace period ends device onboarding.

No ansible-wifi change. Read back after writing.

## 20260911_1732 — Per-pin activation timeline tool added: correlate-pin-activation.sh, fixes a live-confirmed lease join-order bug (v0.1.38 -> v0.1.39)

**Trigger:** while confirming `bungardi-smc01`'s portal-FQDN fix (v0.1.38), the operator asked for a specific per-pin view that neither existing script gives: "for this site, tell me when a pin was
activated, what IP it had, what MAC address, when did the lease start, when did it end" — a timeline, not `audit-pin-activation.sh`'s per-site totals. A manual one-off version of this join, run live
against `hope-vale-smc01` to answer the immediate question, worked but used `tail -1` to pick the current lease block for each activated IP.

**Bug found during that manual run, before it was promoted to a script:** `dhcpd.leases` is append-only, and `tail -1` picks the LAST lease block recorded for an IP — which is not necessarily the one
that was actually in force at a given historical activation time. Confirmed live: `hope-vale-smc01`, IP `10.0.36.28` — its last-in-file lease block has `starts epoch` = 15:53:29, but the real
`wifi/access` activation for that IP was logged at 15:52:41, **48 seconds earlier**. The correct block (an earlier renewal) was further up the file.

**Fix: `scripts/correlate-pin-activation.sh` added**, doing the join properly — for each IP, scans every recorded lease block and picks the one whose `starts` epoch is the *latest one still `<=` the
activation epoch*, not the file's last word on that IP. Falls back to the earliest known lease (flagged with an explicit WARNING note) when no lease had started by activation time at all — confirmed
on a live 30-activation sample against `hope-vale-smc01`, this happened for 4 of 30 IPs. Also handles two other data gaps found live rather than failing silently: an IP with no lease record at all
(`no-lease-found`) and a matched lease block missing its `hardware ethernet` line (`no-mac-in-lease-record`, added after a live run produced a blank, unlabelled field for exactly this case). Runs from
a non-Linux operator machine: the one GNU-`date`-dependent step happens remotely on the Ubuntu appliance over `tsh ssh`; the join and lease-epoch formatting happen locally with a portable `date
-d`/`date -r` fallback.

**Also updated:** `references/14_pin-activation-diagnosis.md` §14.4 rewritten with the join-order bug, the confirmed evidence, and the correct algorithm (previously just a one-line manual `grep`
example); §14.8 tooling list gained the new script. `scripts/README.md` gained a full write-up (table + usage) mirroring the existing `audit-pin-activation.sh` entry, plus updates to the file's
top-of-doc summary/read-first pointers. `fleet-health.justfile` gained a `pin-correlate` recipe alongside the existing `pin-audit`/`pin-audit-sites`.

**Verification:** live-run against `hope-vale-smc01` (30-row and 60-row lookback), plus three isolated synthetic-fixture unit tests covering the no-lease, lease-starts-after-activation (WARNING), and
missing-hardware-ethernet-line code paths individually — all three confirmed correct in isolation before trusting the live-data run's coverage of them.

## 20260911_1240 — Incident closed: all 3 sites' fix + recovery confirmed live in references/13_known-issues.md (v0.1.37 -> v0.1.38)

**Trigger:** the previous entry's known-issues update left a dangling "see the fix confirmation above" reference that pointed at nothing — the actual fix-and-recovery evidence (11:37:50 first new
activation on `hope-vale`/`kowanyama`, `bungardi` fixed ~11:58) had only been written to the `ansible-wifi`-side RCA doc, `SCRATCHPAD.md`, and memory-keeper, never into `skill-smc` itself. Closed that
gap and updated with the full live recovery trajectory tracked afterward.

- `references/13_known-issues.md`: rewrote the "Still actively broken" bullet (now stale — all 3 fixed) into a "RESOLVED 2026-09-11" bullet with the actual fix mechanism (`smc_squid` tag only), timing
  (11:34 for hope-vale/kowanyama, ~11:58 for bungardi via backdoor-SSH), first-activation confirmation timing (3–9 minutes), and the observed post-fix trajectory (`kowanyama` 1→10, `hope-vale` 2→6
  across ~1 hour of live tracking) — useful as a reference shape for how fast recovery should look after this class of fix in future incidents.

Applied to: `references/13_known-issues.md`, `manifest.json`, `CHANGELOG.md`.

---

## 20260911_1210 — Correction: kaltjiti-fergon-smc01 was never affected; bungardi-smc01 fixed live (v0.1.36 -> v0.1.37)

**Trigger:** Operator asked which sites carry the stale `teleport.communitywifi.net.au.conf` vhost/cron for cleanup. A fresh, isolated live re-check (fixing an exit-code handling bug in the sweep
script itself along the way — `grep -c` returning 1 on zero matches was making `tsh` report a false connection error) found `kaltjiti-fergon-smc01` has a single vhost only, `squid.conf` dated
2024-08-07 (predates the regression entirely), and correct `deny_info`. It was **never affected** — the v0.1.35/v0.1.36 entries wrongly listed it as a 4th site "fixed 2026-09-08, same batch as
`galiwinku`". Traced to output-interleaving corruption in the very first parallel-`tsh ssh` sweep (multiple sessions appending to one shared file with no per-host isolation), which a later "clean"
rerun did not fully purge before the finding was written up and catalogued.

- `references/13_known-issues.md`: corrected the "fixed but with leftover cruft" list (now `hope-vale`/`kowanyama`/`bungardi`/`galiwinku`/`doomadgee`/`darlngunaya`, not `kaltjiti-fergon`) and added an
  explicit correction note with the root cause and a process lesson (verify a fleet-sweep finding against a single, isolated, freshly-read capture before writing it into this file).
- `references/14_pin-activation-diagnosis.md`: relabeled `kaltjiti-fergon-smc01`'s row in the §14.7 case-study table from "(fixed 2026-09-08, same batch)" to "(control — never affected)"; the numeric
  data in that row (150 marks, 179 activations) was independently re-verified live and is accurate, only the narrative label was wrong.
- **`bungardi-smc01` fixed live ~11:58** (operator, via the backdoor-SSH path documented in `03_communication-flows.md` §Backdoor SSH Access) — re-verified: `deny_info` correct, `squid.conf`
  regenerated. All 3 originally-broken sites (`hope-vale`/`kowanyama`/`bungardi`) are now fixed; recovery-confirmation watch extended to cover `bungardi` the same way as the other two.
- Superseded, not silently edited: the v0.1.35/v0.1.36 `CHANGELOG.md` entries above are left as the historical record of what was believed at the time, per this pack's convention of correcting forward
  rather than rewriting past entries.

Applied to: `references/13_known-issues.md`, `references/14_pin-activation-diagnosis.md`, `manifest.json`, `CHANGELOG.md`. Also corrected in `ansible-wifi`'s own case files:
`local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/teleport-fqdn/portal-fqdn-regression-20260911_1140.md` and `SCRATCHPAD.md`.

---

## 20260911_1120 — bungardi-smc01 confirmed as third broken site; Eclipse "PIN Last Issued" admin report documented as a third corroborating evidence source (v0.1.35 -> v0.1.36)

**Trigger:** Operator shared a screenshot of the Eclipse admin "PIN Last Issued" report (per-site last-issue date, all `nbn_accelerate`/`nbn_wh` communities) and flagged `bungardi` as still
suspiciously unresolved from the prior session's "unreachable" status, plus a batch of sites showing `Sep 10` as possibly-nothing-but-worth-checking.

- `bungardi-smc01`'s Teleport tunnel recovered on retry (the earlier "no tunnel connection found" was transient). Live-audited: `deny_info` still points at `teleport.communitywifi.net.au`,
  `squid.conf` mtime 2025-09-18, 2 marks / 2 activations in the log window — same dead signature as `hope-vale`/`kowanyama`. **Third confirmed-broken site.**
- Ran `audit-pin-activation.sh` against the six operator-flagged `Sep 10`/`Sep 9` sites (`arawerr`, `loanbun`, `burawa`, `warakurna`, `pipalyatjara`, `mungkarta`): all showed healthy 302 counts
  (57–526) — cleared as false alarms, normal daily variance.
- Documented the Eclipse "PIN Last Issued" report itself in `references/14_pin-activation-diagnosis.md` §14.6 as a third independent evidence source (outside this fleet's own tooling) — corrects the
  prior framing that pin-generation data was Eclipse-side and effectively unreachable; it's unreachable from *this fleet's* tooling specifically, but the operator has a working admin view for it.
  Landed on the same three sites as both of this pack's own mechanisms, independently.
- Updated `references/13_known-issues.md`'s `bungardi-smc01` entry from "could not be verified live" to confirmed-broken, and updated the "still actively broken" list fleet-wide from 2 sites to 3.
- Updated the §14.7 case-study table with `bungardi`'s real numbers.

Applied to: `references/13_known-issues.md`, `references/14_pin-activation-diagnosis.md`, `manifest.json`, `CHANGELOG.md`.

---

## 20260911_1115 — Pin-activation diagnosis added: two independent mechanisms, `audit-pin-activation.sh`, portal-FQDN-regression capture, live fleet case study (v0.1.34 -> v0.1.35)

**Trigger:** Operator-directed investigation into low utilization at 3 suspected `nbn_accelerate` sites, escalated to a full fleet sweep across `nbn_accelerate` + `nbn_wh`, then handed the operator's
own diagnostic methodology (previously undocumented in this pack) for distinguishing pin validity from pin issuance, with an instruction to turn it into reusable tooling.

- New `references/14_pin-activation-diagnosis.md`: the two independent mechanisms — `iptables -t mangle -L ECLIPSE_MARK` (pin valid right now, a snapshot) vs the Apache `wifi/access` log audit trail
  (pin actually issued, an audit trail over time; `302`=success, `200`=failure) — plus tier routing (`iptables -t nat -L SQUID_REDIRECT`, ports 3128/3130/3131), MAC↔IP correlation via `dhcpd.leases`,
  the controller code path (`wifi.php action_access` → Eclipse `get_free_pin_monthly` → mark applied → redirect, verified 9-second mark-to-first-allowed-flow timing), and five pitfalls found live
  during this investigation (log location varies by box — `access.log` absent entirely on `bungardi-smc01`; marks ≠ activations — an Eclipse-pushed mark on `hope-vale-smc01` had no local activation
  POST; the inverse — `amata-smc01` read 0 current marks against 628 recent activations, so mark count alone is not a reliable "is this site dead" signal; pin-generation timestamps are Eclipse-side
  only; local per-box MariaDB is in-progress work, not the production pin store — operator-confirmed, do not chase it).
- New `scripts/audit-pin-activation.sh`: runs both mechanisms per host in one SSH round-trip, prints a comparison table (marks / 3128 / 3131 / 302 / 200 / 404). Same hardcoded-command,
  host-names-only, no-default-site-list contract as the existing fleet scripts. Dogfooded live against `hope-vale-smc01` and `amata-smc01` before being catalogued — the `amata` zero-marks finding
  above came directly out of that dogfooding run, not a hypothetical.
- `scripts/collect-fleet-health.sh`: added capture 5, `05-portal-fqdn-status` (`deny_info`, `squid.conf` mtime, enabled Apache vhosts, `sslcertcopy` cron) — the config-side half of this diagnosis.
  Dogfooded live against `hope-vale-smc01`.
- `scripts/fleet-health.justfile`: added `pin-audit`/`pin-audit-sites` (wraps the new script) and `portal-fqdn-check` (quick cross-host summary of capture 5, same pattern as `freshclam-check`) — logic
  verified against a real capture before being trusted.
- `references/13_known-issues.md`: new dated entry documenting **two separate portal-FQDN regressions**, not one — `nbn_accelerate` (2025-06-27 to 2025-07-28, ~1 month, deliberate revert) and `nbn_wh`
  (2025-07-01 to 2026-09-03, **~14 months**, fixed *incidentally* inside an unrelated squid-blocklist-transport commit whose headline never mentions the portal fix). Live fleet-sweep status as of
  2026-09-11: `hope-vale-smc01` and `kowanyama-smc01` still actively broken (confirmed by both mechanisms — 1–2 successful activations in a 15-day window vs 179–893 at every control site);
  `galiwinku-smc01` and `kaltjiti-fergon-smc01` fixed 2026-09-08 (same batch, `kaltjiti-fergon` not previously documented as affected); `doomadgee-smc01` fixed at the original 2025-07-28 revert;
  `bungardi-smc01` (`nbn_wh`) unverifiable live — Teleport tunnel registration failure, matches a known intermittent pattern on this fleet, flagged as the highest-priority open unknown;
  `darlngunaya-smc01` (`nbn_wh`) never affected (config predates the regression entirely). Process lesson recorded: a fix bundled inside an unrelated commit is exactly what a headline-only write-back
  sweep misses — `git show --stat` on every commit touching a shared vars file, not just commits that name it, needed for this class of regression.
- `references/10_captive-portal.md` §11.7: cross-reference added — "portal responding" (existing end-to-end verification) is not the same claim as "pins are being issued" (new reference).
- Catalogued the new reference file in all four required surfaces (`RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`, `context-map.yaml`) and the new script in `scripts/README.md`, per
  `rule-reference-update-discipline.md`.

Applied to: `references/14_pin-activation-diagnosis.md` (new), `scripts/audit-pin-activation.sh` (new), `scripts/collect-fleet-health.sh`, `scripts/fleet-health.justfile`, `scripts/README.md`,
`references/13_known-issues.md`, `references/10_captive-portal.md`, `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `manifest.json`, `CHANGELOG.md`.

---

## 20260908_1955 — skill-ai-it refresh: navigation-control upgrade, `check_governance.py` adopted, `AI_NAVIGATION.md` declared project-managed (v0.1.33 -> v0.1.34)

**Trigger:** `/skill-ai-it bootstrap` invoked against this pack. All base governance (`README.md`, `AGENTS.md`, `CLAUDE.md`) and navigation (`AI_NAVIGATION.md`, `context-map.yaml`) files already
existed, so per skill-ai-it's own mode-selection rules the correct action was `refresh`, not a fresh bootstrap.

- Ran the deterministic navigation-control upgrade (`upgrade_navigation_control_layer.py`): refreshed `context-map.yaml` (added `audit_checks`, `promotion_rules`, `context_recovery`, `update_rules`,
  `skill_ai_it_version`) and inserted a managed inventory block into `scripts/README.md`.
- `AGENTS.md`'s `skill-ai-it:navigation` block predated the version-marker convention and carried only generic, non-project-specific content; upgraded it in place to the current template
  (`2026-08-11-governance-checks-layer-v1`).
- `AI_NAVIGATION.md`'s `skill-ai-it:navigation` block is genuinely project-specific — a 13-file task-to-reference routing table and specialist-pack file-role priorities the generic template has no
  equivalent for. Overwriting it would have destroyed real content, so it was declared project-managed (`<!-- skill-ai-it:manual reason="..." -->`) instead; the two sections the validator still
  expected (generated-context support-only policy, context compaction recovery, companion consistency) were hand-added, tailored to this pack's actual files rather than copied verbatim from the
  generic template.
- Adopted `scripts/check_governance.py` (this pack had none): turns `.archcore/rules/rule-reference-update-discipline.md` (references named in `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md`,
  `context-map.yaml`) and `.archcore/rules/rule-manifest-version-discipline.md` (`manifest.json` as sole version-of-record) into executable assertions. First run surfaced 35 false positives from a
  generic first pass — remote-appliance script paths (`sbdm.py`, `smartmon.py`, etc.), sibling-repo (`ansible-wifi`) file mentions, and a version regex that collided with unrelated software versions
  (ClamAV `0.103.11`, ansible-lint `0.0.53`) — each was traced to its actual source and either registered in `CONDITIONAL_PATHS` with a reason or fixed at the regex level (the version check now
  derives its match pattern from `manifest.json`'s own major.minor at run time instead of matching any semver-shaped number). One genuine finding survived: the checker itself was not yet cataloged in
  `scripts/README.md`; fixed by adding a fourth script category there.
- Wired the checker into `AGENTS.md` via the `skill-ai-it:governance-checks` managed block.
- `validate_navigation_control_layer.py` now reports a clean PASS (26/26) with 0 warnings, 0 failures.
- The mechanical upgrade step's own `CHANGELOG.md` entry had been appended at the end of the file (chronological), breaking this pack's newest-first convention with no `Contents` row; folded into this
  entry instead, at the top, in the pack's own order.

Applied to: `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `scripts/README.md`, `scripts/check_governance.py` (new), `manifest.json`, `CHANGELOG.md`.

---

## 20260908_1515 — `wifi-02.activ8me.net.au` is APN's own LVS VIP, not a third party; port-80 source-IP allowlist failure mode; reject-vs-drop diagnostics (v0.1.32 -> v0.1.33)

**Trigger:** a live diagnostic session investigating why `galiwinku-smc01` (`nbn_accelerate`) could not reach `wifi-02.activ8me.net.au` on port 80 produced eight findings — one of them an architecture
correction that changes escalation routing. Applying the skill's standing write-back contract (`SKILL.md`), extending the references that already cover this territory rather than duplicating them.

**Corrected (the important one):**
1. `references/03_communication-flows.md` — new `### wifi-02.activ8me.net.au / 202.171.100.138 is APN's OWN keepalived/LVS VIP` subsection. **Despite the `activ8me` domain, this endpoint is APN
   infrastructure, not an external vendor service** — keepalived `vrrp_instance VI_138`, director pair `202.171.100.132`/`.133` on `bond1.1005`, load-balancing to real servers `lweb03.apn.net.au`
   (`172.16.254.73`) and `lweb04.apn.net.au` (`172.16.254.74`). The pack previously did not document this host **at all**; the only nearby entry was `wifi.activ8me.net.au:443` (the remote Eclipse
   portal-config server in `10_captive-portal.md`), which the new section explicitly distinguishes so the two are not conflated. Also records that the name is a **static `/etc/hosts` entry** on every
   `nbn_accelerate` SMC, so DNS is never a variable in failures involving it. **This changes escalation routing: failures here are APN-internal, not a vendor ticket.**

**Added:**
1. `references/06_failure-modes.md` — new "Port-80 Source-IP Allowlist on the APN VIP" entry. The port-80 virtual service enforces a source-IP ACL: `119.12.209.0/24` (the fleet's NAT pool) permitted,
   everything else rejected at the director with ICMP type 3 code 13 (admin prohibited); port 443 is unrestricted. Documents the memorable symptom signature (**port 80 fails "No route to host" in ~1
   RTT while ping succeeds and 443 works** = an ICMP admin-prohibited reject, not a routing failure) and the distinction that matters most in practice: `curl` **exit 56** / "Connection reset by peer"
   means TCP fully ESTABLISHED then app-reset — the *normal* behaviour of this endpoint — whereas `curl` **exit 7** / "No route to host" means it never established. Root cause at galiwinku: carrier
   NAT placed the site in `119.12.211.0/24` instead of the pool, with **no config change on either side and no alerting**. Confirmed with two independent out-of-range sources (`119.12.211.80`,
   `3.104.50.51`). Fix path: add the range to the allowlist, or preferably restore the site to the pool. Investigation limit recorded: `202.171.100.132:22` is filtered from `cw-teleport01`, so the
   rule text itself could not be read in-session.
2. `references/03_communication-flows.md` — new `### Per-Site Public Egress IP` subsection. All of a multi-WAN SMC's circuits can share **one** public IP (galiwinku: all 7 circuits → `119.12.211.80`,
   converging at carrier hop `10.191.0.13`), which invalidates most per-circuit theories about remote-end behaviour. Records the check (`curl -sS https://api.ipify.org` — HTTPS deliberately, since
   port 80 may be the thing under investigation), the known 2026-09-08 values (galiwinku `119.12.211.80` out-of-pool, amata `119.12.209.20`, kowanyama `119.12.209.111`), and a recommendation for a
   fleet-wide audit that would catch this class of silent breakage.
3. `references/03_communication-flows.md` §Backdoor SSH Access — `cw-teleport01` documented as an **APN-side diagnostic vantage point**, not only an SSH stepping stone: internal APN reachability to
   `172.16.254.73`/`.74` at ~10.5–10.8 ms and `202.171.100.132` at ~11.8 ms, useful for testing LVS backends and VIPs directly. Added as a capability note on the existing subsection rather than a new
   one, since the backdoor-SSH mechanics were already covered by the v0.1.31 write-back. Includes the SSH-filtered caveat.
4. `references/05_troubleshooting.md` — new `### Cross-Tier: Reject vs Drop, Where a Rejection Was Generated, and On-Box Tooling Gotchas` section. The generalizable method: **compare the returned ICMP
   error's TTL against known-good replies from the same host** — matching TTLs prove a far-end origin, a much higher TTL means a nearby middlebox forged it (worked example: admin-prohibited at `ttl
   49` identical to genuine ping replies, ~13–14 hops away; the quoted SYN at `ttl 51`, sent at 64). Plus reject-vs-drop by latency (~1 RTT vs multi-second timeout), and six on-box tooling gotchas: no
   `traceroute` (use `mtr`/`nping`/`nmap`/`tracepath`/`busybox`); `mtr --interface` binds in `-T` but **not** in ICMP mode (silently egressed via `eno1` when `vlan534` was requested — always check hop
   1); `mtr` "0.0% loss" counts an ICMP *rejection* as a response; `tcpdump` buffers so mid-run reads show nothing; a `host <ip>` filter misses returning ICMP errors (use `'host <ip> or icmp'` with
   `-vv`); and `curl ... 2>&1 | tail -1` masks the exit code that distinguishes 7 from 56.
5. `references/13_known-issues.md` — new dated section recording an **upstream keepalived config bug not owned by `ansible-wifi`**: the virtual_server uses `lb_algo rr`, which does not honour
   `real_server` weights (only `wrr` does), so the `weight 65535` on lweb04 against lweb03's default `1` reads as a drain intent that is silently ignored — lweb03 still takes ~50% of new connections.
   Explicitly recorded as **not** the cause of the 2026-09-08 incident (both backends verified healthy, HTTP 200 plain and with `Host: corellia`), so the entry is not misread as a resolved root cause.
   Also notes `persistence_timeout 86400` pins each client source IP to one real server for 24 hours.
6. `references/03_communication-flows.md` §WAN Uplink Addressing — two bullets extending the existing source-policy-routing coverage rather than duplicating it. (a) **A stale `ip rule` does not always
   mean a stale render**: rules persist when a DHCP lease drops too (observed at galiwinku for `vlan525`/`vlan523` after both lost their addresses), so check whether the rule's source IP is still
   assigned to distinguish lease residue from render residue — the pre-existing "topology file can shrink" bullet only covered the render case. (b) **Squid's transparent redirect is scoped to LAN
   clients**: `-A PREROUTING -i bridge_501 -p tcp --dport 80 -j SQUID_REDIRECT` never sees traffic the SMC originates itself, a common false lead when diagnosing port-80 failures from a root shell.
7. `RUNBOOK.md` — three new routing rows: the APN VIP / public-egress-IP entry, the port-80 allowlist symptom, and the "is it them or us?" diagnostic section.

**Already covered, extended rather than duplicated:** per-WAN-source `ip rule` → dedicated routing table was already documented in `03_communication-flows.md` (the `dhclient-enter-hooks` branch table)
and `02_service-map.md`; only the lease-residue nuance and the Squid scoping were new. `cw-teleport01` already had a backdoor-SSH section from the v0.1.31 write-back; only its diagnostic-vantage
capability was added.

**Manifest/version:** `manifest.json` version bumped `0.1.32` -> `0.1.33`, `updated_at` set to `2026-09-08T15:15:00Z`, and a new `stable_facts` entry added recording the VIP ownership correction, the
static `/etc/hosts` resolution, and the port-80 allowlist as durable architectural facts.

## 20260908_1430 — galiwinku-smc01 multi-WAN session write-back: ECMP hash-pinning root cause, VRF-disable landed, topology/monitoring gaps (v0.1.31 -> v0.1.32)

**Trigger:** a live diagnostic session against `galiwinku-smc01` (`nbn_accelerate`) investigating a WAN circuit outage surfaced eight findings spanning topology, a self-heal script hazard, two
already-tracked-but-now-superseded VRF/multi-WAN facts, a fleet-wide ECMP routing root cause, a monitoring blind spot, and an access-automation pattern. Applying the skill's standing write-back
contract (`SKILL.md`) across the reference set that already covers this territory, correcting rather than duplicating where content already existed.

**Added:**
1. `references/01_overview.md` — new "WAN Uplink Topology Pattern" subsection: direct-to-NTD physical ports and switch-trunked multi-circuit access-VLAN ports can coexist on one multi-WAN box
   (confirmed at galiwinku: `eno1`/`enp3s0` direct-to-NTD, `enp2s0`/`enp1s0` trunking 4 access-VLANs each to two separate switches), and why that split matters for triage. Cross-referenced against the
   pre-existing switch01/switch02 active-standby bonding design in `08_ansible-authoring.md` to distinguish the two patterns explicitly.
2. `references/06_failure-modes.md` — new "interfacecheckv2.sh's Unconditional dhclient Restart Can Worsen a Marginal Link" entry, directly following the pre-existing aurukun-smc03 self-heal-cron
   entry it qualifies: that entry concluded the cron was blameless against an already-dead circuit; this one documents the opposite case (galiwinku `vlan523`, 2026-09-08) where the same restart-with-
   no-backoff behavior turned a recoverable, briefly-degraded link into a full DHCP lease loss.
3. `references/06_failure-modes.md` — new "ECMP Multipath Hashing Pins Fixed-Destination Traffic to a Single (Possibly Dead) Nexthop" entry — the most generalizable finding of the session.
   `net.ipv4.fib_multipath_hash_policy` defaults to `0` (L3-only) fleet-wide (nothing in Ansible sets it), so any fixed-destination flow (DNS to `8.8.8.8`, a monitoring target, the Teleport bastion IP
   itself) is permanently pinned to one ECMP nexthop regardless of its health. Documents the recognizable symptom signature ("FQDN ping fails inconsistently, IP ping doesn't, `/etc/hosts` 'fixes'
   it"), the live-testable no-reboot fix (`fib_multipath_hash_policy=1`, verified via `ip route get ... sport <N>`), and the important caveat that the fix does not give seamless mid-connection
   failover — backed by real `autossh-teleport-openssh` log evidence of a failed reconnect attempt hashing onto a dead nexthop. Applied on galiwinku only
   (`/etc/sysctl.d/60-smc-multiwan-fib-hash.conf`, on-box, uncommitted to ansible-wifi); fleet-wide rollout proposed but deliberately deferred pending observation.
4. `references/05_troubleshooting.md` Tier 1 — cross-reference from the autossh tunnel check to the new ECMP hash-pinning entry, since a reconnect failure there can look like a broken tunnel when it's
   actually a hash-pinned dead nexthop.
5. `references/13_known-issues.md` "Fleet-Wide Architecture Risks" — new row documenting the missing per-device `role="internet"` Prometheus alert: `NodeStarlinkInterfacecheckPacketLoss` only covers
   aggregated `role="starlink"`, and `HostInterfacecheckTextfileCollectorNotUpdated` only detects the collector script itself going stale, not an individual internet-role device failing while the
   script keeps running. This is why the galiwinku outage needed manual SSH diagnosis. Cross-referenced from `SKILL.md`'s and `06_failure-modes.md`'s own "Key Prometheus Alerts" tables so neither
   reads as complete coverage on its own.
6. `references/03_communication-flows.md` §Backdoor SSH Access — added the specific credential-delivery mechanism for agentic/automated sessions: `kp clip -a Password "<entry>"` (silent, no stdout)
   plus an AppleScript `write text (the clipboard)` targeted at a specific iTerm session GUID, so the plaintext never appears in any tool-call argument or output. The `kp clip`-to-vault workflow
   itself was already documented; only this specific automation-safe delivery detail was missing.

**Corrected:**
1. `references/03_communication-flows.md` — the "Nothing in ansible-wifi builds the ECMP multipath default" bullet previously theorized (explicitly flagged "inferred, not verified") that the Kohana
   wifi app builds the multipath route via `kohana status:gateway`. Corrected: that call only registers a lease with the portal app: it does not construct or manage any route. The real mechanism,
   confirmed live at galiwinku 2026-09-08, is emergent kernel behavior — independent per-interface `dhclient` instances each install a same-metric default route, and the kernel merges same-
   destination/same-metric routes from different devices into one ECMP group with **no health-based nexthop eviction of any kind**. This is the mechanism the new ECMP hash-pinning failure-mode entry
   (above) depends on, and now correctly attributes it.
2. `references/03_communication-flows.md` and `references/08_ansible-authoring.md` — the VRF-allocation-in-`netplan.yml.j2` "still live and rendered into every deploy today" claim (2026-07-31) and the
   "commented out at source... uncommitted" note (2026-08-25) are both now stale in the same way: the interim disable landed as commit `f2fb439f` ("Onboard yakanarra, disable VRF emission...",
   2026-08-27), confirmed present on `internet-label-rename`/`squid-redesign` and confirmed **absent from `master`** as of 2026-09-08 (`git merge-base --is-ancestor` check). Both files updated to
   state the branch-scoped, commit-pinned current reality rather than a since-superseded snapshot. `multiwan-setup.sh.j2`'s deploying task block remains commented out on the same commit — neither
   mechanism is live anywhere in the fleet; this reconfirms, rather than changes, the pack's prior "not deployed" conclusion for both.

**Not applicable, no action taken:** the session also confirmed `multiwan-setup.sh` itself (the fwmark/nft/tc-shaping allocator) remains fully undeployed with no doc drift to correct beyond the VRF
branch/commit update above — the pack already documented it correctly as dead code.

**Manifest/version:** `manifest.json` version bumped `0.1.31` -> `0.1.32`, `updated_at` set to `2026-09-08T14:30:00Z`, and a new `stable_facts` entry added summarizing the
ECMP/`fib_multipath_hash_policy` finding as a fleet-wide architectural fact (see the file for full text).

## 20260908_1330 — Backdoor SSH access documented: raw reverse-tunnel path around a hung Teleport node agent, confirmed live against nbn_accelerate (v0.1.30 -> v0.1.31)

**Trigger:** operator used a previously-undocumented "backdoor" SSH path to reach `galiwinku-smc01` (`nbn_accelerate`) after being blocked on the normal `tsh ssh` route, and asked for the mechanism to
be captured for future use. Operator confirmed the same path also works across the `APN` project fleet (`rcp`/`wh`/`rct` flavors), though that side was not independently re-validated live in this
session. Operator also corrected pre-existing terminology drift: the Teleport cluster domain splits by **project** (APN, nbn_accelerate), not by flavor — flavors nest under a project, so
`01_overview.md` and the diagrams in `03_communication-flows.md` were also fixed (`teleport.<flavor>.au` -> `teleport.<project>.au`).

**Added:**
1. `references/03_communication-flows.md` — new `### Backdoor SSH Access` subsection under `## 3. Communication Flows`, documenting the `smc_autossh` role's independent `autossh-teleport-openssh`
   reverse tunnel: the port formula (`50000 + site_eclipse_siteid`, `smc_bases.yml:78`), the per-project bastion table (nbn_accelerate project → `teleport.communitywifi.net.au` / `cw-teleport01` /
   `3.104.50.51`; APN project → `teleport.apn.au` / `13.54.242.59`), the two-hop procedure (`tsh ssh` to the bastion, then `ssh -p <port> root@127.0.0.1` straight into the box's own sshd), and the
   credential source (KeePassXC `Network/SMC`, retrieved via `kp clip` per `security-and-secrets-guide.md` — never the literal value in this doc). Also notes the two caveats that matter operationally:
   no Teleport session recording on this path, and it only rescues a *stuck Teleport agent*, not a *stuck kernel* (the tunnel service itself has to still be alive).
2. `manifest.json` `stable_facts[1]` expanded from a one-line port-formula fact to cross-reference the new subsection and record the live-confirmation date/scope.
3. `RUNBOOK.md` routing-table row for `references/03_communication-flows.md` extended to surface the backdoor-access use case alongside the existing Grafana/Graylog/Teleport-App entries.
4. `references/03_communication-flows.md`'s own `## Contents` block gained indented, hyperlinked sub-entries for all 11 `###` subsections (previously only its single `##` heading was listed). Required
   a `*`-bullet marker rather than `-` — the repo's `markdown-wrap-toc.sh` hook only manages `- [text](#anchor)` entries tied to real `##` headings and silently strips anything else added that way; a
   `*`-bullet link renders identically in GFM but falls outside the hook's managed block.

**Follow-up staleness pass (same session, same fix):** a detailed staleness audit scoped to this write-back found the `teleport.<flavor>.au` mislabel also present in `SKILL.md` (x2) and `PROFILE.md` —
sibling surfaces that should have been caught in the original terminology fix above but were missed because the audit only checked `01_overview.md`/`03_communication-flows.md`. Fixed both, and fixed
this pack's own `SCRATCHPAD.md` "Phase" line which still asserted `v0.1.30` as current. Regenerated `.ai-context/governance-pack.md` via `repomix` (per its own generated-file convention — never
hand-edited) so all fixes propagate there too. Verified the `apn`/`cw` central-infra claim in the new bastion table against live inventory (`host_vars` glob for `*-smc0*.yml`: 0 matches in both `apn/`
and `cw/`, confirming central-infra-only, no site hosts) rather than trusting the pre-existing `01_overview.md` assertion at face value.

**Not independently re-tested:** the `apn`-side claim (`rcp`/`wh`/`rct`) is operator-stated, not re-validated against a live `apn` host in this session — recorded as such in the new subsection rather
than asserted as independently confirmed.

**Follow-up coherence sweep (same session, pushing the fix outward):** the staleness pass above only found direct restatements of the old wording. A coherence sweep found two places that assumed the
old flavor-based model without containing the literal stale string: (1) `references/05_troubleshooting.md` Tier 1 ("Box Unreachable") didn't mention that a box absent from the `tsh ls` roster is still
reachable via the backdoor tunnel — added a cross-reference so operators get a working root shell instead of being stuck external-only. (2) `references/13_known-issues.md`'s "Flavor → Teleport cluster
domain mapping" row title and content asserted the split was by flavor — retitled to "Project → Teleport cluster domain mapping" with a corrective note, and added a pointer to the new backdoor
section. Reviewed and left alone: `13_known-issues.md`'s brief "per flavor's Teleport cluster" parenthetical elsewhere (line ~29) — imprecise but not false, since each flavor does map to exactly one
cluster; not worth the churn. `AI_NAVIGATION.md`/`context-map.yaml` already route generically to `03_communication-flows.md` for "external comms paths" and needed no new dedicated row. `.archcore/`
rules and `scripts/*` were checked and don't encode this assumption (the one script referencing a Teleport domain, `fleet-health.justfile`, hardcodes the literal domain rather than assuming a
flavor-keyed split). Regenerated `.ai-context/governance-pack.md` again after these two edits.

## 20260908_1200 — Pack-structure self-audit: RUNBOOK version drift, install.md staleness, reference-update-discipline gap, vestigial evidence/, and archcore status promotion (v0.1.29 -> v0.1.30)

**Trigger:** operator asked for a detailed structural review of the pack itself (not its SMC content) — is `skill-smc` organized correctly as a Claude Code skill, and does the file layout match what a
skill should look like. Confirmed the installed surface (`SKILL.md` + `RUNBOOK.md` + `references/` + `scripts/`) is correctly lean and matches `.archcore/specs/spec-specialist-pack-file-roles.md`, but
found five governance/hygiene defects in the surrounding pack scaffolding.

**Fixed:**
1. `RUNBOOK.md` carried its own `**Version:** 0.1.28` line, stale against `manifest.json`'s `0.1.29` — a duplicate version stamp in a file declared "navigation index only" is a guaranteed drift source
   since no rule updates it on every bump. Removed the line entirely rather than syncing it once; `manifest.json` is already the sole version authority per `context-map.yaml`'s `authority_order`.
2. `exports/claude_code/project/skill-smc/install.md`'s "Current Install State" section had been frozen at `Canonical version: 0.1.6` since the 2026-04-17 Phase 2 MCP-wiring entry — 20+ versions
   stale, and misleadingly labeled "Current". Retitled to "Install History" (a point-in-time log, not a live tracker), added an explicit note to check `manifest.json` for the live version, and
   appended a 2026-09-08 re-sync entry.
3. `.archcore/rules/rule-reference-update-discipline.md` listed only 4 surfaces to update when adding a new reference file (`RUNBOOK.md`, `SKILL.md`, `adapter.md`, `install.md`) — it never mentioned
   `AI_NAVIGATION.md` or `context-map.yaml`, even though both carry the same task-to-reference routing table and this pack's own `AGENTS.md` Tier 2 checklist already expected them kept current.
   Widened the rule to 6 surfaces to match actual practice and close the gap between codified rule and enforced behavior.
4. Removed the empty, untracked `evidence/` directory left over in canonical source — the pack's actual evidence-retention policy (documented in `scripts/README.md`) relocates captured evidence to
   `local-knowledge-ansible/ansible-wifi/issues/...`, so a permanent local `evidence/` stub serves no purpose and could be mistaken for the real retention location.
5. Promoted all four `.archcore/` governance docs (`adr-progressive-disclosure-structure.md`, `rule-manifest-version-discipline.md`, `rule-progressive-disclosure-loading.md`,
   `rule-reference-update-discipline.md`, `spec-specialist-pack-file-roles.md`) from `status: proposed` to `status: accepted` — all five are actively enforced and cited elsewhere in the pack as
   settled fact (this pack's own `AGENTS.md` treats them as working rules), so "proposed" understated their authority.

**Checked, not a defect:** `.graylog-token` (a Grafana/Graylog credential sitting in the pack root) was flagged during the initial pass as an ungitignored secret risk, then verified against
`skills_stuff/.gitignore:3` (`specialists/project/skill-smc/.graylog-token`) and confirmed already covered — `git check-ignore -v` returns a clean match. No action needed; recorded here so a future
pass doesn't re-flag it without checking.

**Not changed:** the installed skill surface itself (`SKILL.md`, `RUNBOOK.md` body content, `references/*.md`, `scripts/`) — this pass was governance/meta-hygiene only, no SMC operational content
changed.

**Evidence basis:** direct read of every top-level file, `manifest.json`, `.archcore/**`, `exports/claude_code/project/skill-smc/**`, `context-map.yaml`, `AI_NAVIGATION.md`, and `git ls-files` / `git
check-ignore` against the actual `skills_stuff` git root (not assumed from memory-keeper history).

## 20260907_1600 — Two Ansible silent-failure gotchas, an `rcp` systemd-mask fix, and the `auto_reboot: 0` truthy-string bug fed back from `ansible-wifi` (v0.1.28 -> v0.1.29)

**Trigger:** scheduled write-back audit of `ansible-wifi`'s own governance (`SCRATCHPAD.md` session history, `git log`) against `skill-smc`'s references, prompted by the operator asking whether recent
`ansible-wifi` session work — not just the pandanus-park investigation already fed back — had made it into the skill. Three recent sessions (2026-09-01, -03, -04) turned out to carry findings never
written back: the squid blocklist migration itself was already documented (`08_ansible-authoring.md` "smc_squid's blocklist refresh"), but four items bundled into or alongside that same push were not.

**Added to `08_ansible-authoring.md`:** two Ansible authoring gotchas found while fixing `smc_system`/`smc_update_kernel`. (1) A `command: lxd.lxc list ...` guard task silently no-opped fleet-wide
because `/snap/bin` is not on the `command` module's non-interactive `PATH` — the guard never actually ran, on every invocation, since it was written; fixed by using the absolute `/snap/bin/lxd.lxc`
path. (2) `failed_when: reboot_result.rc != 0` disbelieved every successful reboot because `ansible.builtin.reboot` is an action plugin that returns no `rc` key at all — this caused a real
reboot-retry loop (fifteen successful reboots each reissued) in `roles/smc_update_kernel`; fixed by deleting the `failed_when` and matching the working `smc_rise_common` handler pattern.

**Added to `13_known-issues.md`:** (1) A new "Fleet-Wide Architecture Risks" row — `watchdog.auto_reboot: 0` does not actually disable automatic RISE-watchdog reboots. Two independent template/logic
defects confirmed live via `/opt/rise/status/watchdog.json` (which emits the quoted string `"0"`, truthy in Python); unresolved, flagged do-not-apply-blind pending an operator decision, since a prior
commit (`fb7ff6fa`) deliberately narrowed a related reboot condition and may be guarding a case this defect's fix would reopen. (2) A new "Known Operational Bugs (rcp fleet)" row — four units
(`isc-dhcp-server6`, `fwupd-refresh`, `dhclient@eth0`, an ASUS keyboard-backlight unit) fail on every boot on `rcp` hardware for structural, non-configurable reasons and are now masked
(`hotspot_flavor == 'rcp'` only, commit `2dee86a8`) with a `reset-failed` pass to clear the stale state masking alone leaves behind. Kept distinct from the superficially similar
`isc-dhcp-server6`/`fwupd-refresh` rows already documented under the NBN Accelerate cluster sweep — same service names, different fleet, different fix, not the same finding.

**Not written back — flagged, not guessed:** the `2026-09-03` overlay/journald correction ("enabling overlay shrinks the journal budget, not grows it") and the squidGuard-tree overlay copy-up estimate
(~550-600 MB one-off per boot) were checked against `07_hardware-overlay.md` and judged adequately covered by existing content there (the squidguard-as-largest-writer and journald-volatile-trap
sections) rather than write-back gaps — left alone to avoid duplicating or subtly re-deriving numbers that are already sourced elsewhere in that file.

## 20260907_1530 — Silent Total Hang confirmed on `rcp` (pandanus-park-smc01), first non-`wh` instance (v0.1.27 -> v0.1.28)

**Trigger:** operator report ("pandanus park is offline") in `ansible-wifi`, unrelated to any fleet sweep. Investigation followed the `06_failure-modes.md` §Silent Total Hang playbook
(`up{instance=~...}` on `apn-prometheus01`) and, once the new Teleport-App Graylog access method from `03_communication-flows.md` was available, cross-checked with a full Graylog message search — the
first time this signature has had real log corroboration rather than Prometheus alone, since both prior `wh` cases had non-functional Graylog sidecars.

**Finding: the signature is not RPi/`wh`-specific.** pandanus-park-smc01 (`rcp`, x86, single-SMC site, no `smc02`) went dark 2026-09-05 ~08:29-08:40 UTC with the identical fingerprint: `prometheus`,
`node_exporter` and `speedtest_exporter` all stop in the same scrape; `node_load1`/`MemAvailable` flat with no trend beforehand; boot time unchanged (no reboot, ~78 days uptime at death); zero
`panic`/`OOM`/`I/O error`/`EXT4-fs error` in the hour before. Full Graylog search confirmed **zero log messages of any kind, any path**, from the last line (08:40:03 UTC) through the investigation
time (2026-09-07 05:00 UTC) — a genuinely dead box, not a metrics-only gap.

**Fix: `references/06_failure-modes.md` §Silent Total Hang rewritten as cross-flavor.** Retitled from "on RPi `wh`" to flavor-neutral; added a "Why `rcp` is exposed too" subsection (simpler cause than
`wh` — `rcp` never ran RISE at all, so there's no inert safety net to explain, there's just none); added a dedicated pandanus-park evidence subsection; corrected the forensic-destruction section to
note `rcp` is **not** overlayroot, so unlike the `wh` cases this is the first real chance to pull on-disk `dmesg`/kernel evidence after the next recovery reboot (`journalctl -k -b -1`); updated "Fleet
status" and "Recommended fix" to cover both flavors (x86 hardware-watchdog driver, e.g. `iTCO_wdt`/`sp5100_tco`, TBD per chassis). `RUNBOOK.md`'s three §Silent Total Hang routing rows were broadened
to mention both flavors and to point at `03_communication-flows.md` for the actual Graylog query method.

**Open follow-up, not done in this pass:** no fleet-wide `up{flavor="rcp"}` absence sweep has been run to check whether other single-SMC `rcp` sites carry the same undetected exposure. pandanus-park
itself is still dark as of this writing — no on-site power cycle performed yet, so the on-disk forensic opportunity above is theoretical until the next reboot.

## 20260907_1200 — Standing write-back contract added to SKILL.md: the update obligation now travels with the skill, not each consuming project's governance file (v0.1.26 -> v0.1.27)

**Trigger:** operator observation from `apn/smc-file-writing-analysis` — a Graylog REST API access method (Teleport Application Access + mTLS) had existed in that project's own tooling since
2026-07-23 but sat undocumented in `skill-smc` for six weeks, because no existing routing-table category matched "how do I reach an external system's API." That project's `AGENTS.md` was patched to
add the missing category (see that project's own changelog/scratchpad), but the operator raised a sharper structural question: why does *every* consuming project need its own copy of "you must update
skill-smc" boilerplate at all? A brand-new third project that has never heard of skill-smc, and invokes it for the first time, should not need pre-existing governance text telling it to write back
here — the obligation should be inherent to invoking the skill.

**Fix: added a "Standing Write-Back Contract" section to `SKILL.md`, immediately after "Use When."** It states plainly that this skill is the shared cross-project source of truth, that any session
invoking it for SMC/`ansible-wifi` work must write new findings back to the appropriate `references/*.md` file before ending the session *regardless of what the calling project's own governance file
says*, and that a project's own `AGENTS.md`/`CLAUDE.md` restating this is reinforcement, not the source of the rule. Because `SKILL.md` is what loads into context on every invocation of this skill
(`/skill-smc`, or automatic matching against its one-line description), this travels with the skill itself rather than needing to be re-derived or copy-pasted into each new project's governance.

**Also corrected in the same pass:** `SKILL.md`'s own `## Source` footer had drifted — it still read `version: 0.1.24` while `manifest.json` was already at `0.1.26`, a small instance of the exact
class of staleness this skill exists to catch elsewhere. Both are now `0.1.27` and will be bumped together going forward.

## 20260904_1000 — WAN uplink dead-DHCP failure mode documented, self-heal cron distinguished from real flapping (v0.1.25 -> v0.1.26)

**New entry in `references/06_failure-modes.md`: "WAN Uplink Stuck With No DHCP Lease, Self-Heal Cron Masquerades as 'Flapping'."** Root-caused live on `aurukun-smc03` (`nbn_accelerate`) via `tsh`.
Operator reported `enp2s0` (uplink into NTD2) failing to ping and later refined it to "flapping every five minutes." Physical layer was clean throughout — carrier up, 1Gbps full duplex, only 2 real
`igb` link transitions in 24h — but the interface had held no DHCP lease for 11+ days (lease expired 2026-08-24, confirmed from `/var/lib/dhcp/dhclient.<iface>.leases`), predating the NTD's own
20h-uptime figure by over a week.

**The reusable finding: `/interfacecheckv2.sh` (Ansible-deployed, `*/5 * * * *` cron on every SMC box) is a false-flap generator whenever an uplink is genuinely dead.** It pings 8.8.8.8 out every
`internet0X`/`vlanNNN` interface and restarts `dhclient@<iface>` on failure. A permanently-dead uplink fails every single check, so the box bounces its own DHCP client on an exact 5-minute cadence
forever — 288 restarts/24h, matching 24h/5min precisely. That churn is indistinguishable from real flapping in logs/monitoring unless you check the kernel `igb` driver log for the TRUE physical
transition count.

**One live confirmation test separated "probably upstream" from "confirmed upstream":** manually bounced the interface (`ip link down`/`up`) and force-restarted `dhclient` fresh — same zero-DHCPOFFER
result immediately after a clean reset. Rules out stuck local NIC/driver state; the fault sits on the carrier/NTD DHCP path, not fixable from ansible/smc.

**Also recorded:** a `tsh ssh` gotcha (a bare `--` separator before the remote command is forwarded literally to the remote bash and errors "invalid option" — drop it) and a cross-reference to the
2026-08-03 fleet-hardware-audit manifest entry noting `aurukun-smc03` was already unreachable during that earlier sweep, which may or may not be related to this circuit's history.

## 20260827_1800 — Code notes documented as an authoring surface; stale lint paragraph corrected (v0.1.24 -> v0.1.25)

**New section in `references/08_ansible-authoring.md`: "Code notes: where the long explanation goes, and what it can and cannot survive."** RULE-006's comment/note split was governed but undocumented
here, so an agent reading the authoring reference had no idea the surface existed. Covers the routing test (**if being unaware of it would cause a bug, it goes in the file**), the prohibition on
referencing notes from code, and what a note now records.

**Provenance and its ranking are the load-bearing part.** A note carries a normalized `sha256`, three lines of verbatim context either side, the authoring branch, and the commit with a `(dirty)`
marker. Ranked strictly: content hash authoritative, commit tested by *ancestry rather than equality* so it survives a merge, branch a display label — and **metadata may only clear a warning, never
raise one**.

**The measurement worth carrying forward:** of 24 notes anchored on `internet-label-rename`, tested against `master`, **21 were out of range**, 1 moved, 2 drifted, 0 exact —
`smc_rsyslog/tasks/main.yml` is 26 lines there against ~300 on the branch. Out-of-range **crashes extension activation**, and a crashed activation never regenerates `INDEX.json`, so a reload does not
clear it. Hence the operational rule: run `check_note_anchors.py` after any branch switch or out-of-editor edit, not only after authoring — re-anchoring is driven by `onDidChangeTextDocument`, which
fires for nothing when a checkout, a `sed` pass or a lint autofix rewrites a closed file.

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

- `scripts/collect-smc-evidence-full.sh` — new **`rpi` group, 20 captures**, and real per-host platform gating rather than the previous "detect and warn" placeholder. The capture list is now filtered
  from the detected platform: `rpi` runs only on a Pi, and the four x86-only probes (`dmidecode` ×3, `smartctl`) are dropped there instead of filling the summary with absences that read like findings.
  `--only rpi` against an x86 host skips cleanly with a message.
- The group is built around the questions the Ubuntu 26.04 migration has to answer, so `--only rpi` across the fleet doubles as the phase-0 audit that
  `ansible-wifi.tasks.ubuntu-migration-open-items.20260821` asks for: EEPROM date against the 26.04 boot floor, boot-partition size against the three-asset-set requirement, `copymods` state, piboot
  layout presence, revision code for tryboot eligibility, plus throttling, SD health and zram.

### Verified live

Validated against **marta-marta-smc01** (`rct`) and **violet-valley-smc01** (`wh`), both Pi 4B Rev 1.5 / aarch64 / Ubuntu 22.04: all 20 rpi captures return, **zero genuine failures** on either host,
and the only non-ok results are the two correct pre-piboot absences (`autoboot-txt`, `piboot-units`). x86 gating re-checked on yakanarra-smc01.

Two findings surfaced by the first run, both concrete migration input rather than tool output:

- **EEPROM on marta-marta is 2023-01-11**, comfortably past the 2022-11-25 floor, so that box clears the 26.04 boot prerequisite. Worth noting the report's `LATEST` (2022-01-25) is *older* than
  `CURRENT` — "up to date" there means "nothing newer in `/lib/firmware`", not "current with upstream".
- **`/boot/firmware` is 253 MB with 119 MB already used for a single asset set (47%).** 26.04 keeps up to three. Three sets do not fit in 253 MB, which makes the boot-partition item a measured blocker
  rather than a theoretical one.

### Learned

- **`life_time` / `pre_eol_info` do not exist on an SD-booted Pi 4** — they are eMMC attributes. `/sys/block/mmcblk0/device/` exposes `cid`, `csd`, `ssr`, `fwrev`, `manfid`, `oemid`, `serial`, `date`
  and no wear-level pair. The plan written the day before had specified those two files; the hardware disagreed, and the capture now reads what is actually there. Any guidance claiming to read SD
  wear-levelling from them on this hardware is wrong.
- Writing shell into a bash array from a generator script is an escaping trap: a double-escaped `$` produced `\\$a`, which expanded **locally** at array-definition time and tripped `set -u` with "a:
  unbound variable". Both offending captures were rewritten to use `head -n 1` with brace expansion and no shell variables at all, and the generator now asserts that no capture line contains a
  double-escaped `$`.

## 20260825_1745 — broad diagnostic collector added; narrow collector's interfacecheck path corrected (v0.1.22 -> v0.1.23)

Onboarding a new RCP site (yakanarra) needed a wider capture than the routing-focused collector provides, and running the existing one surfaced a path bug in it.

### Added

- `scripts/collect-smc-evidence-full.sh` — broad read-only capture: **144 captures across 17 groups** (`identity os overlay storage services network dhcp dns firewall qos wifi voip portal monitoring
  rise access logs`), covering every subsystem in `references/02_service-map.md`. Complements rather than replaces `collect-smc-evidence.sh`, which stays narrow and stable because two analysers depend
  on its output contract.
  - **One SSH session per host.** The narrow collector opens a Teleport session per capture; at this scale that would be 144 sequential sessions. This builds a single remote script with
    `===SMC-CAPTURE===` delimiters and splits the stream locally. Measured 144 captures in ~25s against yakanarra-smc01 and umoona-smc01.
  - **Credential redaction on by default.** A broad capture reads service configs, and this fleet has no ansible-vault, so Teleport join tokens and SIP secrets would otherwise land on disk. The key is
    kept and the value replaced with `<REDACTED>`; `--no-redact` opts out. Pattern-based, so a sensible default and not a guarantee.
  - **Absences are classified, not lumped in with failures** — `absent (no such systemd unit)` / `(command not installed)` / `(no such file or directory)` vs a genuine `FAILED (rc=N)`. On a healthy
    box most non-zero rcs mean "not deployed on this flavour", which is the finding.
  - x86 capture set. Platform is detected per host; a Pi runs the platform-neutral groups and is reported as not-yet-implemented for the Pi-specific set rather than being probed with
    `dmidecode`/`smartctl`. The RPi capture list is specified in a comment block at the foot of the script.

### Fixed

- `scripts/collect-smc-evidence.sh` — the `interfacecheck` capture read `/usr/local/bin/interfacecheckv2.sh`. `smc_network` renders it to the **filesystem root**
  (`roles/smc_network/tasks/ubuntu.yml:346` -> `/interfacecheckv2.sh`). The capture had therefore been failing on **every site, silently, for the life of the script** — it reports `FAILED` in the
  manifest, which reads as a finding about the box rather than a bug in the tool. Verified absent at the old path and present at the new one on yakanarra, umoona and pandanus-park.

### Learned (live, 2026-08-25)

- **`systemctl status asterisk` reporting `active (exited)` is not proof Asterisk is running.** The unit is an LSB init wrapper, so systemd reports success once the script returns 0 whether or not a
  daemon survives. Confirmed on **umoona-smc01**: unit `active (exited)` since 09:41, **zero** asterisk processes, no `/var/run/asterisk/` control socket, every `asterisk -rx` query failing with
  "Unable to connect to remote asterisk". Note this is the same site whose 2026-08-19 CDR investigation concluded "handsets not in use" from an unchanged `Master.csv` — worth re-reading that
  conclusion against this, since a dead PBX and an unused one produce the same empty CDR file. Not chased in this session.
- Portal layout is not what a `application/config` glob assumes: `/var/www/` holds `kohana-base` (which uses `system/config`), `apn-mqtt-client` and `html`. The capture now lists `/var/www` and finds
  config dirs rather than guessing a path.
- **umoona-smc01 has no database server at all** — `mariadb`/`mysql` units not-found and zero `mariadb-server`/`mysql-server` packages installed. The capture now distinguishes "not running" from "not
  installed".
- `GROUPS` is a **bash special variable** (the current user's group IDs). Assigning to it in a script is silently ignored — it cost one debug cycle here, and any future script in this pack should
  avoid the name.

## 20260818_1350 — pre-push gate mechanics corrected, plaintext-secret exposure recorded (v0.1.21 -> v0.1.22)

Pushing the `rise` branch turned the pre-push hook into its own investigation, and it corrected guidance this pack had been giving.

### Changed

- `references/08_ansible-authoring.md` — **correction**: the Validation section previously advised putting `/Volumes/Data/_ai/_skills/skills-runtime/ansible-wifi/.venv/bin` on `PATH` when the hook
  fails. That venv is now known to be the *cause*, not the cure — it carries `ansible-core 2.17` with two collections and no `netaddr` against brew's 95, so it cannot resolve `selinux`
  (`ansible.posix`) at `roles/smc_system/tasks/main.yml:137` and fails the syntax-check stage for any push reaching that role, whatever you changed.
- Same file — new section documenting the gate's four stages and their differing semantics: only the ansible-lint stage has a baseline; yamllint has none and fails on any error in a touched file;
  syntax-check covers root-level playbooks only. Plus the properties that matter in practice — `line_is_changed` is evaluated **before** the baseline (so a baseline entry can never hide your own
  line), every finding in a new file blocks unconditionally, the baseline is `file|rule` keyed and lives in `.git/` so it is per-machine, the parser stores a finding's **column** as its rule when one
  is present, and the correct order of work is own-lines first, baseline second, whitespace last — getting that order wrong turned a 43-finding job into a 404-finding one.
- `references/13_known-issues.md` — new section on plaintext secrets in `group_vars` with no `ansible-vault` anywhere, and the `cw/group_vars/graylog.yml` copy that carried APN's cluster UUID, master
  `password_secret`, root password hash, three tokens and Teams webhook. Records the client/server asymmetry worth checking whenever a cluster is cloned: the client half had been adapted for
  communitywifi, the server half had not.

### Status

Repo side: `origin/rise` e1077c17 -> 213c0e4a (8 commits), governance repo main c6228ce -> 1f09cee. Detail in `ansible-wifi` `CHANGELOG.md` `20260818_1350`.

## 20260818_1300 — delye-smc01 RESOLVED; `overlay.size_ratio` proven inert; fleet percentages corrected (v0.1.20 -> v0.1.21)

Operator deployed `smc_rise_logcaps` to `delye-smc01` and re-enabled overlayroot. Verified on-box: reboot loop broken (1 h 18 min uptime, single boot), `laravel.log` 2.63 GiB -> **753 KB**, overlay at
15% used, latent log exposure down from ~85% of budget to **4%**, `rise-logcaps.timer` active, `rise-watchdog` running normally again now that `/media/root-ro` exists.

Verifying that deployment surfaced an error in this pack's own numbers. `df` reported a 3.9 GiB overlay where the documented budget was 3.05 GiB, which traced to **`overlay.size_ratio` being
completely inert**: overlayroot 0.47ubuntu1 mounts the upper layer as `mount -t tmpfs tmpfs-root "${root_rw}"` with no `-o size`, and the only option keys it parses are `swap`, `recurse`, `debug`,
`dir` and `driver`. `size=40%` is parsed into an unused shell variable by a generic key/value parser that validates nothing, so it is discarded without error or warning. The real budget is always the
kernel tmpfs default of **50% of RAM** — measured 3.812 GiB on a 7.625 GiB box, exactly 50.0%.

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
validated with `promtool check rules` on `black-hill-3-smc01` (rc=0). Central ingestion could not be verified end to end — the Grafana tunnel is refused and agent mode blocks querying the box's own
TSDB — so the evidence is indirect: `samples_failed_total` 0 on a working `remote_write`, and the pre-existing `HostSbdm*` alerts depend on the same pipe and allowlist. Nothing deployed.

## 20260818_1130 — overlayroot copy_up cost model, `smc_rise_logcaps`, and three fleet-class findings (v0.1.18 → v0.1.19)

`delye-smc01` was reboot-looping every ~5 minutes. Root cause was a 2.63 GiB Laravel log with no logrotate stanza anywhere on the box, against a 3.05 GiB overlay budget. The generalisable lesson — and
the reason this warranted reference changes rather than just an issue note — is that **overlayroot copy_up charges a file's size at first write, not its write rate**, which inverts normal disk-space
intuition: a 2.6 GiB log appended at 4 KB/min is far more dangerous than a 10 MB log appended at 4 MB/min.

Verified at source (overlayroot 0.47ubuntu1) that `recurse=0` — already set fleet-wide — leaves every non-`/` fstab entry outside the overlay entirely, so moving volatile paths onto their own mount is
the permanent fix. That is deferred (no spare partition on most boxes); `roles/smc_rise_logcaps` is the interim mitigation, built on filesystem discovery rather than an enumerated path list.

Five classification bugs and two silent-failure modes were found by running read-only scans against six live production hosts rather than by reasoning — recorded because the method mattered more than
any individual bug.

### Changed

- `references/07_hardware-overlay.md` §8 — three new subsections: the copy_up cost model (including that **reading does not trigger copy_up**, which is what makes live fleet assessment safe);
  `recurse=0` verified at source with the actual shell snippet, plus why a loop-mounted image file cannot substitute for a real partition; and `smc_rise_logcaps`' five-bucket model with the mechanics
  that are easy to get wrong (`copytruncate` mandatory, `size` not `daily`, rsyslog not reopening on truncate, never truncating a `.gz`, `su root adm` not `su root root`).
- `references/13_known-issues.md` — four new sections: the `delye-smc01` reboot loop with triage notes; `rise-watchdog.service` failing `226/NAMESPACE` on any overlay-disabled or x86 host
  (fleet-class, previously undetected, scope still unmeasured); Ubuntu's stock rsyslog logrotate having no size limit, with measured `auth.log`/`syslog.1` sizes across three hosts and the harness
  warning about omitting `/etc/logrotate.conf`; and the legacy `ozai/hc.log` still writing post-RISE plus the graylog-sidecar logs that accumulate forever because they are already under any size
  threshold. Includes the six-host fleet log-exposure table (mimbi-smc01 at ~40% of its overlay budget).
- `references/05_troubleshooting.md` — new **Tier 8b: Box Reboot-Looping Every Few Minutes**, a six-step workflow whose first step is establishing that `rise_watchdog.py` reboots and
  `rise_healthcheck.py` never does.
- `references/02_service-map.md` — `rise_logcap.py` / `rise-logcaps.timer` registered with its outputs.
- `RUNBOOK.md`, `SKILL.md`, `manifest.json` — version 0.1.18 → 0.1.19; routing row added for reboot-loop triage.

### Status

The role and the watchdog fix are **written but deployed nowhere**. `delye-smc01` remains running with overlayroot disabled and unremediated. `nbn_wh` was not assessed (expired Teleport profile).
Repo-side detail lives in `ansible-wifi` `CHANGELOG.md` `20260818_1115` and memory-keeper keys `ansible-wifi.*.20260818`.

## 20260803_1825 — new-looma-smc01 second whole-host outage confirmed via live Prometheus (v0.1.17 → v0.1.18)

Operator reported "new-looma-smc01 is back online." Rather than take the status at face value, queried `mcp-grafana-apn` (already live from the previous session's Grafana work) for
`up{instance=~"new-looma.*"}` over the last 7 days.

**Confirmed:** both the self-scrape (`job="prometheus"`) and `node_exporter` targets for `new-looma-smc01` went dark simultaneously from **2026-08-01 23:40 UTC to 2026-08-03 06:40 UTC (31h)**, then
both resumed together — the signature of a whole-host/network outage, not a single failed service. A second, earlier 18h gap in the same window (2026-07-29 11:10 → 2026-07-30 05:10 UTC) lines up
exactly with the already-documented topology cross-wiring fix (`08_ansible-authoring.md`), confirming that gap is already explained. This newer 31h gap is not — no `tsh ssh` access was used this
session, so root cause is confirmed-timeline-only, not diagnosed.

### Changed

- `references/13_known-issues.md` — new paragraph appended to the existing "new-looma-smc01" section documenting the confirmed 31h outage, its whole-host signature, cross-reference to the
  already-explained earlier gap, and an open question about whether it relates to the still-open `my_node_network_device_info` zero-series gap (also new-looma-specific).
- `manifest.json` — new `diagnostics` entry (6th); version bumped 0.1.17 → 0.1.18.

### Evidence basis

Live `mcp-grafana-apn` `query_prometheus` reads this session (`up{instance=~"new-looma.*"}`, instant + 7-day range). Timestamps converted via direct `date -u -r <epoch>` — not estimated. No SSH/tsh
access to the box itself this session.

## 20260803_1810 — Grafana CW exploration unblocked: dashboard inventory + RISE metric names (v0.1.16 → v0.1.17)

Operator supplied the missing NBN-instance service-account token and confirmed a session restart had happened, unblocking the `mcp-grafana-nbn` connection left stuck at the end of the previous session
(blank-token 401, MCP process caching old env). Explored both flavor-specific Grafana instances rather than just confirming connectivity.

**Confirmed:** `mcp-grafana-apn` (20 dashboards) and `mcp-grafana-nbn` (9 dashboards) are not mirrors. The 11 APN-only dashboards include a RISE health/watchdog framework (RISE SMC Health Detail, RISE
SMC Table, RISE Dashboard) that has no NBN counterpart because RISE is deployed only to `rct`/`wh` flavors — confirmed via the `flavor=~"rct|wh"` gate in the "Pending sites" panel query, not just
dashboard absence. Pulled the actual Prometheus metric names behind the four `rise_*` textfile collectors that previously had `—` placeholders in `02_service-map.md`
(`rise_healthcheck_health_score_*`, `rise_healthcheck_health_penalty*`, `rise_overlay_used_pct`/`_inodes_free_pct`/`_active`, `rise_zram_*`,
`rise_watchdog_up`/`_active`/`_boot_firmware_used_pct`/`_unit_active`), plus the offline-vs-pending fleet-rollup logic (offline = watchdog seen in last 30d but not last 5m; pending = node_exporter up
on rct/wh but watchdog series never existed).

### Changed

- `references/03_communication-flows.md` — new "Dashboard inventory" subsection under Grafana/Prometheus MCP Access: full table of the 11 APN-only dashboards with UIDs and purpose, plus the
  RISE-flavor-gate explanation for why they're absent from the NBN instance.
- `references/02_service-map.md` — Monitoring/Metrics textfile-collector table rows for the four `rise_*` scripts now note their systemd unit/flavor gate; new "RISE Health/Watchdog Framework"
  subsection with the full metric table and the offline/pending distinction.
- `manifest.json` — new `diagnostics` entry (5th) capturing the dashboard-inventory and RISE-metric findings; version bumped 0.1.16 → 0.1.17.

### Evidence basis

Live `mcp-grafana-apn`/`mcp-grafana-nbn` reads this session: `search_dashboards` (both instances), `get_dashboard_summary` and `get_dashboard_panel_queries` (RISE SMC Health Detail, RISE SMC Table,
Sites not reporting, SMC Table, Data Backlog, RPi SD Card Status). RPi hardware detail cross-checked against already-confirmed `07_hardware-overlay.md` content — no new hardware facts, dashboard is a
visualization of already-documented state.

## 20260803_1745 — ClamAV freshclam root cause confirmed: ClamAV 0.103.x end-of-life (v0.1.15 → v0.1.16)

Operator asked "what could be the reason for the ClamAV error" following the fleet sweep in the previous entry. Rather than restate the open hypotheses, verified via `WebSearch` against clamav.net and
the Cisco-Talos/clamav GitHub issue tracker before answering.

**Confirmed root cause**: ClamAV's 0.103 branch reached end-of-life for database updates on 2025-09-14. This fleet runs `clamav 0.103.11`/`.12` uniformly, squarely in the EOL'd branch — after the
cutoff, ClamAV's CDN actively rejects `freshclam` from any 0.103.x client with HTTP 403 ("Forbidden; Blocked by CDN"), exactly the signature captured on all 26 hosts. This also explains the 10-month
staggered failure-date spread from the previous entry: each host only flips to `failed` the first time its `freshclam` timer runs *after* the cutoff, so hosts with different timer schedules trip it at
different times rather than all at once. Not a cw-cluster-specific network/firewall issue — this is documented, expected upstream behavior for any fleet still on 0.103.x. Fix is a version upgrade (1.0
or 1.4 LTS), not a retry; no automated ClamAV-version-update pipeline exists for this cluster to do that automatically.

### Changed

- `references/13_known-issues.md` — ClamAV bug row rewritten from "root cause not investigated, 3 open hypotheses" to "root cause confirmed," with the EOL date, the CDN-block mechanism, and the
  staggered-date explanation; "Fix location" column updated from "not investigated" to the concrete upgrade path.
- `references/08_ansible-authoring.md`, `references/01_overview.md` — ClamAV/Lynis rows updated to reference the confirmed root cause instead of open hypotheses.
- `manifest.json` — new `diagnostics` entry (3rd) capturing the confirmed root cause with its sources; version bumped 0.1.15 → 0.1.16.

### Evidence basis

`WebSearch` against `blog.clamav.net` (the official EOL announcement) and `github.com/Cisco-Talos/clamav` issue tracker (multiple community reports of the identical error signature) — external,
citable sources, not inferred from this fleet's data alone. Cross-checked against this session's own captured data (uniform 0.103.x package version, exit code 17, exact error text match) for internal
consistency.

## 20260803_1730 — Full NBN Accelerate fleet sweep: 28 hosts, hardware inventory, fleet-wide ClamAV finding (v0.1.14 → v0.1.15)

Operator requested a thorough analysis of "all the NBN Accelerate sites" including hardware details and the state of installed apps/scripts/services — a full fleet sweep, not a spot-check, superseding
the 2-host check in the previous entry. Built two new reusable tools (`scripts/collect-fleet-health.sh`, `scripts/fleet-health.justfile`) and ran them against all 26 reachable `nbn_accelerate` hosts
plus both `nbn_wh` hosts (28 total).

**Hardware inventory (new — no prior live chassis data existed for this cluster):** 11× AAEON BOXER-6641 (i5-8500T, 15Gi RAM, Transcend SSD) + 15× AAEON BOXER-6404 (Celeron J1900, 7.7Gi RAM, Innodisk
CFast) for `nbn_accelerate`; both `nbn_wh` hosts are genuine Raspberry Pi-class (Cortex-A72, Swissbit microSD) — operator confirmed `nbn_wh` is the `wh`-flavor equivalent on this cluster.

**Major finding: `clamav-freshclam` confirmed failed fleet-wide, 26/26 `nbn_accelerate` hosts** (not the 2 found in the earlier spot-check) — same CDN-blocked exit-17 signature on every host, but
failure *dates* span 10 continuous months (2025-10-02 → 2026-07-30), indicating an ongoing degradation still actively catching hosts, not a single past incident.

**Resolved during write-up (operator-confirmed mid-session):** `nbn_wh` overlayroot is not yet active on either host — this is a planned-but-not-yet-executed rollout (`smc_rise_deploy.yml` already
targets `nbn_wh`), not a bug or stalled deployment.

**Other findings:** kernel-version drift (5.15.0-79 to 5.15.0-133) corroborating the earlier no-automated-kernel-pipeline structural finding; `koonibba-smc01` at 95% disk usage with the fleet's oldest
kernel; `isc-dhcp-server6` failed on 28/28 hosts (confirmed benign — IPv6 disabled by policy); `fwupd-refresh` failed on 3/28 hosts (minor); `nbn_wh` swap/zram absence contradicting the platform
table's universal RPi-zram claim (unresolved).

### Added

- `scripts/collect-fleet-health.sh` — new reusable, flavor-agnostic hardware/security/service-health evidence-capture script (read-only, hardcoded command bundles, same safety contract as
  `collect-smc-evidence.sh`). Bundles ~20 commands into 4 grouped captures per host to stay tractable over satellite links at fleet scale.
- `scripts/fleet-health.justfile` — task-runner wrapping the script, ships with the current NBN Accelerate site list plus `freshclam-check`/`failed-units-check`/`chassis-models` quick-check recipes.
  Dogfooded after writing — found and fixed 2 real bugs (a `just`-working-directory path assumption, and the same exit-code-of-last-command quirk documented in the collection script) before trusting
  it.
- `scripts/README.md` — new safety-classification rows, "What each script is for" section, and a documented lesson on `just -f <path>`'s working-directory behavior.
- `references/07_hardware-overlay.md` — new "NBN Accelerate / NBN WH Hardware Inventory" section with the full chassis/CPU/RAM/storage/kernel table and all findings above.
- `references/13_known-issues.md` — "Known Operational Bugs (NBN Accelerate cluster)" section rewritten for the full 28-host sweep (was 2-host); coverage-gap row updated to "largely closed."
- `references/01_overview.md`, `references/08_ansible-authoring.md` — evidence-basis and flavor-gate rows updated to reflect full-fleet validation.
- `references/04_dependency-tree.md` — separately, added `smc_ltp`/ClamAV/Lynis Level-4 entries and flagged a naming-collision risk between `smc_ltp`'s CNMaestro provisioning and a pre-existing
  generic `cnmaestro-provisioning`/`redis` dependency row (unresolved — may be the same mechanism described two ways, or two genuinely separate paths).
- `manifest.json` — new `diagnostics` entry for the full sweep; version bumped 0.1.14 → 0.1.15.

### Operational note

Raw per-host evidence relocated from `skill-smc/evidence/` to `local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` per this pack's evidence-retention policy —
skill-smc holds analysis and tooling, not case-specific raw captures.

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands, this session, 28/28 targeted hosts. Two-batch capture: batch 1 crashed at 11/28 hosts after a same-session edit to the running script file corrupted
its execution (a documented gotcha now — never edit a script file while it's still running); batch 2 recaptured the remainder with the fixed script. Not covered: `cw` flavor (central-infra only),
`aurukun-smc03` (unreachable at capture time).

## 20260803_1615 — First live NBN Accelerate validation: confirms cluster comparison, finds ClamAV CDN-block (v0.1.13 → v0.1.14)

Operator made `tsh login` available for the NBN Accelerate cluster (`teleport.communitywifi.net.au`) and invited exploratory commands — the first-ever live access this pack has had to that cluster,
closing (partially) the "code-inspection-only" caveat that's sat on every NBN Accelerate claim since the gap-fill earlier today. Ran read-only diagnostic commands against two `nbn_accelerate` hosts,
`warakurna-smc01` and `indulkana-smc01`.

**Every prior code-inspection-only claim checked came back confirmed, 2/2 hosts:** Teleport domain (`teleport.communitywifi.net.au:443`), HTTPS-only portal (permanent HTTP→HTTPS redirect, on-box TLS
termination at `/etc/ssl/communitywifi.net.au/`), `wifi-community-app-backend` present, ClamAV + Lynis both installed, Asterisk absent, DNS stack is standard unbound+stubby (not `smc_ltp`/bind9, as
expected — neither host is an `smc_ltp` member).

**New finding, not previously known:** `clamav-freshclam.service` has been failing on both hosts — `warakurna-smc01` since 2026-07-23, `indulkana-smc01` since 2026-06-21 — identical signature (exit
code 17, `Forbidden; Blocked by CDN`, freshclam gives up permanently rather than retrying). ClamAV's virus database is stale/frozen on both; the daemon itself stays active but with degraded detection.
Root cause not investigated (read-only session, no remediation attempted).

### Added / Changed

- `references/13_known-issues.md` — new "Known Operational Bugs (NBN Accelerate cluster — first live check, 2026-08-03)" section with the confirmed-claims summary and the ClamAV/freshclam bug row;
  "NBN Accelerate cluster coverage gap" row updated from "not live-validated" to "first live spot-check done."
- `references/08_ansible-authoring.md` — ClamAV+Lynis gate row updated with the live-confirmed install + the freshclam finding.
- `references/01_overview.md` — evidence-basis paragraph updated: partially live-validated as of 2026-08-03; `nbn_wh`/`cw` flavors still unvalidated.
- `manifest.json` — new `diagnostics` entry (first use of this previously-empty field) capturing the live-validation results and the ClamAV finding; version bumped 0.1.13 → 0.1.14.

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands against `warakurna-smc01` and `indulkana-smc01`, this session. No writes/remediation performed. `nbn_wh` and `cw` flavors, and every other NBN
Accelerate site, remain unvalidated — this is a 2-host spot-check, not a fleet sweep.

## 20260803_1545 — project-coherence sweep: routing/architecture staleness fixed (v0.1.12 → v0.1.13)

`project-coherence` run covering today's cumulative changes (NBN Accelerate gap-fill through the smc_ltp manual-mechanism confirmation). Content files (Tier 1) were already coherent — this pass caught
two Tier 2/routing staleness items that hadn't been touched during the piecemeal content edits:

### Changed

- `context-map.yaml` — `ansible_authoring` and `smcbox_basics` routing descriptions extended to mention `smc_ltp`/"low touch" onboarding and the APN-vs-NBN-Accelerate comparison respectively;
  previously only the underlying reference files had been updated, not this machine-readable routing layer.
- `ARCHITECTURE.md` — governance-pack size figure corrected from a stale "~125k chars" (last accurate 2026-06-26) to the current ~470k chars / 35 files — had drifted across multiple sessions' worth of
  content growth, not just today's.
- `RUNBOOK.md`, `AI_NAVIGATION.md` — `08_ansible-authoring.md` routing rows extended to mention `smc_ltp` and onboarding history, matching the pattern already applied to the `01_overview.md` row for
  NBN Accelerate.

### Validated

Stale-reference grep across the whole pack for old figures/phrases ("cnMaestro mDNS", "only rcp/guda-guda", "Community WiFi cluster", "~125k chars") — all remaining hits are correctly-framed
historical/correction narrative in `CHANGELOG.md`/`SCRATCHPAD.md`/the "corrected 2026-08-03" notes, no live incorrect claims found. `README.md`, `SYSTEM_PROMPT.md` reviewed — generic pointers, no
stale figures. `.remember/today-2026-08-03.md` reviewed — out of scope for this pack's own coherence pass (self-managed by the global `remember` skill, not a skill-smc-authored file).

Version bumped 0.1.12 → 0.1.13; governance pack regenerated.

## 20260803_1530 — smc_ltp/"low touch" mechanism confirmed: manual step, no enforcement (v0.1.11 → v0.1.12)

Final piece of the smc_ltp/"low touch" thread, same day: operator confirmed the one remaining open question — whether low-touch onboarding tooling itself assigns `smc_ltp` group membership, or it's a
manual step. **It's manual.** No tooling automatically adds a new low-touch site to `smc_ltp:children`, and nothing checks or enforces that it happened. This directly explains the root cause of the
3-site gap fixed in the previous entry — a manual, unenforced step is exactly the kind of thing that silently drops during a busy onboarding.

### Changed

- `references/08_ansible-authoring.md` — "smc_ltp Sub-Group" low-touch resolution paragraph updated with the confirmed mechanism and an explicit operational implication: verify `smc_ltp:children`
  membership explicitly for any future low-touch site rather than assuming it's automatic.
- `references/13_known-issues.md` — the "low touch ↔ `smc_ltp` link" row's status upgraded to include "mechanism confirmed manual"; reframed as a standing risk for future low-touch sites, not a
  one-off closed by this correction.
- `manifest.json` — `smc_ltp`/low-touch `stable_facts` entry updated with the confirmed mechanism; confidence raised to 0.92; version bumped 0.1.11 → 0.1.12.

### Evidence basis

Operator-confirmed directly, relayed to this session. No independent verification possible from Ansible source alone (absence of automation is what's being confirmed, not a positive code finding).

## 20260803_1515 — smc_ltp/"low touch" correlation resolved: 3 sites added to the group, 7 members confirmed (v0.1.10 → v0.1.11)

Follow-up to the "low touch" onboarding entry below, same day. That entry flagged, but did not conclude, whether "low touch" onboarding and `smc_ltp` membership were mechanistically linked (4 of 7
low-touch sites were `smc_ltp` members; 3 — `umoona`/`warburton`/`beagle-bay` — were not). Operator confirmed the link is real: every low-touch site is meant to be an `smc_ltp` member, and the 3
missing ones were a plain inventory gap, not a coincidental overlap of two unrelated rollout decisions.

Operator made and verified the fix directly in `ansible-wifi`: added `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` host groups to `inventories/rcp/prod`, plus each site's own `:children`
block, matching the existing pattern for the other 4 sites. Verified via `ansible-inventory --list` (all 7 now under `smc_ltp:children`) and `ansible-playbook --syntax-check smc_ltp.yml` (clean).
**Uncommitted** — a real production Ansible inventory change, not yet run against any live SMC.

### Changed

- `references/08_ansible-authoring.md` — "smc_ltp Sub-Group" section updated: membership is now 7 sites, not 4; the site/date table's `smc_ltp member?` column updated; the low-touch section's
  "flagged, not concluded" framing replaced with "Resolved 2026-08-03 (link confirmed, not coincidental)" and the fix/verification steps documented. The underlying *mechanism* (does low-touch tooling
  itself assign `smc_ltp` membership, or is it manual) remains unestablished — only the intended end-state membership is now confirmed.
- `references/02_service-map.md`, `references/13_known-issues.md` — DNS resolver row and coverage-gap row updated to 7 sites and "resolved" status.
- `references/01_overview.md`, `SKILL.md`, `references/05_troubleshooting.md` — quick-reference/table mentions of `smc_ltp` membership updated from 4 to 7 sites.
- `manifest.json` — both `smc_ltp`-related `stable_facts` entries updated to reflect 7 members and the resolved correlation; version bumped 0.1.10 → 0.1.11.

### Evidence basis

Operator-directed and operator-verified (`ansible-inventory --list`, `ansible-playbook --syntax-check`) file-level change relayed to this session; not independently re-verified by this session, and
not yet run against any live SMC or committed to the ansible-wifi repo.

## 20260803_1445 — "Low touch" onboarding method and site deployment history added (v0.1.9 → v0.1.10)

Operator supplied install dates for a cohort of `rcp` sites, confirming a named **"low touch" onboarding method**: `guda-guda` (pilot, 2025-04-15), then a year later `umoona` (2026-04-12),
`warburton`, `beagle-bay`, `pandanus-park`, `old-looma`, `new-looma`. Genuinely new information not previously documented anywhere in this pack.

### Added

- `references/08_ansible-authoring.md` — new "'Low Touch' Onboarding Method and Site Deployment History" section (added to Contents list): the full site/date/`smc_ltp`-membership table; the
  flagged-not-concluded observation that all 4 `smc_ltp` sites are also low-touch sites (3 of 4 `smc_ltp` non-pilot members plus the pilot itself), while `umoona`/`warburton`/`beagle-bay` are
  low-touch without `smc_ltp`; and a direct-grep finding that "low touch" currently has no Ansible-code representation — the one `low_touch`-named var in the repo (`smc_bases_low_touch_provisioning`
  on `pierre-rcp01`, not a cohort member) is set but never read by any role or playbook.
- `references/13_known-issues.md` — new open-question row capturing the unresolved `smc_ltp`/low-touch correlation; updated the pre-existing "cnmaestro-provisioning internals" coverage-gap row to
  reflect that the deployment side is now well-documented (only the CNMaestro API's own runtime behavior remains unknown).
- `manifest.json` — new `stable_facts` entry for the low-touch cohort/dates and the orphaned-var finding; version bumped 0.1.9 → 0.1.10.

### Evidence basis

Site list and dates are operator-provided, cross-referenced against independently-observed netplan/hook render timestamps already in this pack's routing-issue-derived content (consistent, not
contradictory — renders land 1-92 days after each stated install date, matching later unrelated remediation work touching those files). The `smc_ltp` overlap and the orphaned
`smc_bases_low_touch_provisioning` var are this session's own repo-wide grep findings. Not live-validated against any site.

## 20260803_1400 — smc_ltp properly explored and documented; membership undercount fixed (v0.1.8 → v0.1.9)

Operator flagged that `smc_ltp` "has not been explored and documented properly" — a fair call. Prior coverage was a side effect of the 2026-07-03 DNS RCA (which only established that `smc_ltp` gates
the unbound-vs-bind DNS split) and had never been independently re-verified since. Direct read of `smc_ltp.yml`, `inventories/rcp/group_vars/smc_ltp.yml`, `inventories/rcp/prod`,
`roles/smc_cnmaestro_provisioning/`, and `roles/smc_dns_mgmt/tasks/main.yml` (this session, cross-checked against a parallel same-day pass done from the ansible-wifi side, which reached the same
conclusions independently) found two things wrong with the prior documentation:

1. **Membership undercount.** Every prior mention said "currently only `rcp`/guda-guda". That was based on a `.yml`-scoped grep that missed `inventories/rcp/prod` — an INI-format static inventory
   file, not a `topology_vars`-generated one. The group actually has 4 members: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`.
2. **Purpose mislabeled.** Prior docs called it "cnMaestro mDNS" — wrong on both halves. It has two unrelated purposes, neither of which is mDNS: (1) a separate `smc_ltp.yml` playbook runs
   CNMaestro-managed Cambium ePMP/cnPilot wireless-backhaul provisioning (auto-allocates management IPs, SSIDs, per-model config for cnPilot/XV2/ePMP Force/ePMP 3000L hardware); (2) `smc_bases.yml`'s
   `dns_mgmt` play switches the DNS resolver stack from unbound+stubby to bind9+RPZ (zone file literally named `db.cambium-rpz`, tying the DNS switch to the same Cambium backhaul context).

### Added / Fixed

- `references/08_ansible-authoring.md` — new "smc_ltp Sub-Group — CNMaestro Backhaul Provisioning + DNS Architecture Switch" section: membership mechanism (static INI group, not topology_vars), both
  purposes in full, the `smc_dhcpd` LTP-specific apparmor/service-user fix, and an explicit "LTP acronym not expanded anywhere in the codebase — do not guess" note. Added to the Contents list.
- `references/01_overview.md`, `references/02_service-map.md`, `references/13_known-issues.md` — corrected the "only `rcp`/guda-guda" undercount to the 4-site list and cross-referenced the new
  08_ansible-authoring.md section instead of restating it.
- `SKILL.md` Tier 3 DNS quick-reference and `references/05_troubleshooting.md` Tier 3b/3c — same undercount fixed; Tier 3c now notes the CNMaestro-provisioning angle so a "DNS is fine but backhaul
  radios aren't provisioning" report on one of these 4 sites doesn't get misdiagnosed as a DNS issue.
- `manifest.json` — new `stable_facts` entry capturing the corrected membership, dual purpose, and the open "LTP acronym" question; version bumped 0.1.8 → 0.1.9.

### Evidence basis

Direct read of the playbook/role/inventory files listed above (this session). Not live-validated against any of the 4 member hosts via `tsh ssh` — the CNMaestro-provisioning and DNS-switch mechanisms
are confirmed from Ansible source, not from a live box.

## 20260803_1230 — NBN Accelerate cluster gap-fill (v0.1.7 → v0.1.8)

Operator request: ~95% of this pack's operational detail was extracted from APN-cluster (`rcp`/`rct`/`wh`, `teleport.apn.au`) work; the NBN Accelerate cluster (`cw`/`nbn_accelerate`/`nbn_wh`,
`teleport.communitywifi.net.au`) had only the flavor→domain mapping documented (from the 2026-07-31 SSH/Teleport corrections). Ran a three-pronged research sweep (inventory group_vars diff across all
7 flavors, repo-wide grep for flavor-conditional branching in roles/templates, doc/ADR/OPA search in local-knowledge-ansible/ansible-wifi) to fill the gap with a structured comparison rather than
assuming parity between the two clusters.

### Added

- `references/01_overview.md` — new "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" section: both clusters share a 1-central-infra + N-site-fleet topology, but NBN Accelerate is
  materially thinner (no graylog/opensearch, no kernel-update Jenkins pipeline) and has real functional differences beyond the SSH endpoint (mobile-app backend + kiosk mode on `nbn_accelerate` only,
  HTTPS-only portal protocol, different blocked-URL redirect domain, ClamAV+Lynis hardening on `nbn_accelerate` only, VoIP/Asterisk on `rcp` only). Documents the selector mechanism (`hotspot_flavor`
  hardware-class split spans both clusters; `inventory_dir.split('/')|last` drives flavor-exclusive gates; nothing branches on the literal strings cw/community/communitywifi).
- `references/08_ansible-authoring.md` — new "Flavor/Cluster Conditional Branching (Selector Reference)" section: table of confirmed flavor-exclusive role gates (ClamAV/Lynis, VoIP/Asterisk,
  `smc_qos`, `smc_ltp`) with their exact conditions, plus the `smc_autossh` Teleport-endpoint selection mechanism (`teleport_fqdn` per-inventory group_var, host_var overrides for staging domains).
- `references/10_captive-portal.md` — new §11.9: `smc_bases_portal_protocol` (http vs https) and `smc_bases_blocked_url_redirect` differences between clusters, flagged explicitly as
  code-inspection-only (not live-validated against a cw-cluster host), with implications for §11.1–11.8's APN-cluster-derived verification commands.
- `references/13_known-issues.md` — new "NBN Accelerate cluster coverage gap" row (Knowledge Gaps table) stating the live-validation boundary explicitly; two new Skill Staleness Risks entries: a
  "community wifi" naming-collision warning (used generically for `rcp` sites in `issues/apn/routing-issue/`, distinct from the cw-flavor customer — a false-positive risk for future greps), and an OPA
  `flavors.json`/`environments.json` coverage note (no `cw`/`apn`/`rct`/`wh` entries — not established whether intentional).
- `RUNBOOK.md`, `SKILL.md`, `AI_NAVIGATION.md` — `01_overview.md` routing rows updated to mention the new APN vs NBN Accelerate comparison content.

### Evidence basis

Structural findings: direct read of all 7 inventories' `group_vars/*.yml` and `prod` files. Behavioral findings: repo-wide grep across `roles/*/tasks/main.yml`, `roles/*/templates/*.j2`,
`smc_bases.yml`. Doc/ADR/OPA findings: search of `local-knowledge-ansible/ansible-wifi/{.archcore,issues,opa,docs,.remember}`. None of this is live-validated against a running `nbn_accelerate`/
`nbn_wh`/`cw` host — flagged as such in every new section rather than presented as fleet-confirmed fact, consistent with this pack's existing evidence-labeling convention.

## 20260731_1312 — Fed back Pia Wadjari labeling case + proposed convention; multiwan-disable git archaeology

Operator worked in `local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/` on internet-link topics (dual-switch bonding, label/metadata convention, manual ingress shaping, dormant
multi-WAN VRF/fwmark), initially without checking here first — that workspace's own governance now flags this happened and corrects the resulting mechanism mis-citations. Two genuinely new pieces of
information from that session, not previously here, fed back per operator request:

### Added

- `references/03_communication-flows.md` — under the existing label-inversion note: Pia Wadjari as a second confirmed instance (Starlink active/`internet` label, SkyMuster Plus backup/`starlink` label
  — inverse of Horn Island), agreed with the operator's colleague Sandro that deployment proceeds as scheduled, and the concrete retrofit proposal (role-based `active-internet`/ `standby-internet`
  labels + `provider:`/`link_type:` metadata fields) with a rough 2-3 week timeline once agreed — the existing note only said a retrofit was "planned" with no detail on what it would look like.
- `references/03_communication-flows.md` — under the existing multiwan/VRF note: the specific disable commit (`c19a61fa`, apparent incidental collateral of an unrelated URL-capture refactor, not a
  deliberate decision) and an important nuance the existing note didn't have — the fwmark script being dead does not mean VRF is fully out of play; `netplan.yml.j2`'s per-WAN VRF *allocation* is still
  live and rendered into every deploy today, only the fwmark `ip rule`s that would use those tables are missing. Flagged as an open, not-yet-checked question whether any live SMC carries orphaned
  `vrf-<tableid>` devices as a result.

### Not added (already covered, verified during this pass)

- Topic 1 (dual-switch bonding design) — already fully promoted into `references/08_ansible-authoring.md`, correctly citing the source workspace's own analysis doc. No gap found.
- Topic 3 (manual ingress-shaping script) — already fully documented (`references/03_communication-flows.md`, `13_known-issues.md`), established 2026-07-29. The source workspace had independently
  rediscovered this and initially mis-described it as "unknown" — corrected there after this check, not here (nothing here was stale).
- The core label-inversion mechanism and the `dhclient-enter-hooks.j2` override itself — already accurate and complete here; it was the *source workspace's* citation of `ubuntu-dhclient-script.j2`
  that was wrong, not anything in this file.

## 20260731_1215 — Two residual gaps closed from the routing-issue Problem 3 deep-dive

Operator asked, from the routing-issue investigation folder, "was all the information in this project fed back to skill-smc?" — a spot-check after the 20260731_1245 full extraction pass (below,
despite the out-of-order stamp — see the note on CHANGELOG stamps not matching wall-clock order) and the earlier 20260729_2324 pass. Both were thorough; this check found the coverage was otherwise
complete, with two specific, narrow gaps in the Problem 3 (starlink `INPUT` DROP) deep-dive.

### Added

- `references/03_communication-flows.md` — the DHCP-bypasses-netfilter-`INPUT` mechanism: ISC `dhclient` uses a raw `AF_PACKET` socket for its own port-68 traffic, tapping frames at the link layer
  before/parallel to `NF_INET_LOCAL_IN`, for both the initial lease and later renewals — this is *why* the starlink DROP rule (already documented) never blocks DHCP, and generalizes to any
  interface-scoped DROP/REJECT rule on this fleet. Live-confirmed on Warburton.
- `references/13_known-issues.md` — new Known Site Issues row: warburton-smc01's unexplained 1.68M-packet/3.3GB starlink DROP-rule counter (live tcpdump ruled out self-generated traffic and
  public-internet exposure; source remains unresolved).

## 20260731_1330 — Broadened cross-repo feed-back governance (prevent future full-sweep need)

Follow-up to the 20260731_1245 extraction pass: the operator asked that ansible-wifi and local-knowledge-ansible/ansible-wifi (current and future subfolders) always consult skill-smc and always feed
new knowledge back via `skill-slurp-chat`/`project-coherence`, so this kind of exhaustive sweep never has to happen again.

### Changed

- `AGENTS.md` "Cross-repo trigger rule" — broadened scope from "when triggered from ansible-wifi" to explicitly cover the whole `local-knowledge-ansible/ansible-wifi` tree (current and future
  subfolders, via the existing `@`-import convention those subfolders already use). Broadened the trigger-condition list beyond "fixes, architecture decisions, failure modes" to explicitly include
  unimplemented design recommendations, ADRs/rules/specs, OPA policy changes, reusable scripts, and ROADMAP decisions. Named `skill-slurp-chat` as an equally mandatory trigger point alongside
  `project-coherence` (previously only the latter was named). Added a closeout self-check.

### Corresponding changes in ansible-wifi's own governance (not this pack, but the other half of the loop)

- `ansible-wifi-root-governance/AGENTS.md` (symlinked as `/Volumes/Data/_ansible/ansible-wifi/AGENTS.md` — a single edit covers both), `.archcore/rule-002`, `.agents/task-patterns.md`, and
  `.agents/validation.md` were broadened identically, and rule-002 was renamed to drop the "incident/debug fixes" framing that had been the actual root cause of the extraction-pass gaps. See that
  repo's own `CHANGELOG.md` entry `20260731_1330` for detail.

## 20260731_1245 — Full local-knowledge-ansible/ansible-wifi extraction pass

Operator asked for an exhaustive sweep of every markdown file under `local-knowledge-ansible/ansible-wifi/` and subfolders to confirm nothing was missed. Covered directly: `ai-tooling/`, `opa/`,
`plans/`, `scripts/` (top-level lint scripts), `history/`, `graphify-out/GRAPH_REPORT.md`, `issues/garimba-smc01/`, `issues/amata-smc01/`, `issues/rcp-fleet/`, `issues/internet-link-handling/`, and
the `ansible-wifi-root-governance/` top-level docs (ROADMAP.md, CONVENTIONS.md, `.serena/memories/`). Delegated to subagents: `ansible-wifi-root-governance/.archcore/` (6 ADRs, 5 rules, 1 guide, 2
specs) and `issues/apn/routing-issue/docs/` (20 files) against current pack content; a third background sweep covered `.remember/` daily logs for anything that fell through the ADR-promotion workflow.
`snapshots/` (59 timestamped dirs) and `history/current/` confirmed to be point-in-time copies of the ansible-wifi repo's own AGENTS.md, not distinct knowledge — spot-checked via diff, not deep-read.

### Added

- `references/06_failure-modes.md` — amata-smc01 disk-path failure (ATA/COMRESET, `DID_BAD_TARGET`, forced read-only root) as a new failure-mode entry, flagged still-open per ROADMAP.md.
- `references/07_hardware-overlay.md` — `smc_disk_failover` role mechanism (EFI BootNext on connectivity failure, not storage-health failure; not guaranteed to run cleanly under active I/O
  corruption).
- `references/13_known-issues.md` — amata-smc01 open-incident row; `smc_qos` misgated to `rct`-only (silently no-ops on rcp/nbn_accelerate); Horn Island's unconditional `starlink01`/`starlink02`
  topology block; Pandanus Park chronic `interfacecheckv2.sh` restart loop; Old Looma `smc_iptables` ACL drift (Asterisk/MQTT/Cambium-TFTP rules missing); mercedes-cove null-property portal bug;
  duplicate `[horn-island_smc_bases]` inventory declaration; bungardi-smc01 multi-incident cluster (hostapd driver hang masquerading as apt lock contention, nl80211 netlink wedge, Teleport
  cert/reverse-tunnel issues, WAN-level eth0 flakiness); an unreconciled-duplicate-fix flag for two differently-described apt-daily-upgrade fixes that may or may not be the same change.
- `references/08_ansible-authoring.md` — OPA policy layer overview (packages, `opa eval`/`opa test`/`conftest` usage, ADR-001's env-gate-before-flavor-gate precedence); a design recommendation for
  bonding (not bridging) doubled RCP/NBN-Accelerate internet circuits (`mode=active-backup`, ARP-based monitoring, systemd-networkd VLAN-as-bond-slave race-bug risk); a third topology_vars
  authoring-bug class (role mistagging, confirmed at rocket-bore-smc01, alongside the existing vlanid-cloning and physical-interface-naming bugs); the SSH cipher-negotiation fix's correct home
  (`smc_sshd`'s `ssh_config` template, not per-script patches); a guardrailed single-site interface-key rename pattern (pia-wadjari) with the two preconditions that make it safe to reuse.
- `references/12_content-filtering.md` — SPEC-002's bridge_500-unconditional-ACCEPT fact as an explicit differential-diagnosis note ("VLAN 500 works, 501 doesn't" = by design, not a fault).
- `references/03_communication-flows.md` — corrected the stale "`smc_qos` planned, not started" claim (the role exists, is just misgated) with the per-site missing-shaping data; two generalizable
  WAN-path diagnostic techniques (RX=0 rules out firewall causes; sibling-VLAN isolation test) from the dark-VLAN Starlink-backup investigation.
- `references/05_troubleshooting.md` / `06_failure-modes.md` — noted the `custom_apt_install.yml` "invalid loop data" fix was superseded by a wholesale file replacement, not the originally documented
  in-place patch.
- **`scripts/lint-baseline-refresh.sh` + `scripts/ansible-lint-delta-gate.sh`** — promoted and genericized from `local-knowledge-ansible/ansible-wifi/scripts/`. Config path is now repo-root-relative
  (`ANSIBLE_LINT_CONFIG` override) instead of two hardcoded paths that disagreed with each other (`local-knowledge/` vs `local-knowledge-ansible/`). See `scripts/README.md` (retitled to cover both the
  WAN-routing and lint-gate script categories).

### Corrected (post-pass, operator-flagged, two rounds)

- `install.md` + `adapter.md` — first correction round stated SMC access "must go through `tsh ssh` via the `ssh-manager` MCP." **Also wrong** — no `ssh-manager` (or any SSH-wrapping) MCP is used at
  all; access is a direct `tsh ssh root@<hostname>` shell command, no MCP involved. Rewrote both to remove the MCP framing entirely: a plain "Live SSH access — direct `tsh ssh`, no MCP" section, and
  `mcp-grafana` as the only MCP left in the execution layer. Fixed the stale `ssh_list_servers`/ `ssh_execute` verification steps to a direct `tsh ssh` check.
- `references/01_overview.md` "Remote Access" + `references/13_known-issues.md` — the Teleport cluster domain was previously assumed single-value fleet-wide (`teleport.apn.au`). Operator confirmed the
  actual split: `rcp`/`rct`/`wh`/`apn` → `teleport.apn.au`; `nbn_accelerate`/`nbn_wh`/`cw` → `teleport.communitywifi.net.au` (all 7 flavors covered). Added this mapping table to `01_overview.md`,
  `install.md`, and closed the coverage-gap row in `13_known-issues.md` that had briefly flagged it as unresolved.

### Not promoted (reviewed, judged not durable/in-scope)

- `ai-tooling/*.md` — meta design-rationale docs for skill-smc itself (already implemented, matches current pack state); not operational SMC knowledge.
- `plans/20260317_1656_interface-id-rename-plan.md` — historical, fully superseded by the guardrailed-rename pattern now captured in `08_ansible-authoring.md`.
- `graphify-out/` — mostly vendored-Ansible-collection graph noise; the one durable pointer (overlayroot-persistence roadmap item) was already covered by existing Tier 8 content.
- `snapshots/`, `history/` (except the one url-capture-v2 migration doc, already captured pre-session) — point-in-time governance-file backups, not distinct knowledge.

## 20260729_2324 — WAN-routing coverage expansion + reusable diagnostic scripts (APN routing-issue investigation)

Full pass to make sure the APN routing-issue investigation's learnings actually made it into this pack, prompted by an operator audit question ("did you capture all the information in the docs folder
into skill-smc?"). Answer was initially no — a subagent audit against all 11 investigation docs found real gaps, all closed in this pass.

### Added

- `references/03_communication-flows.md` — new "Manual TBF/`ifb` Ingress Shaping" subsection: a live, fleet-wide, NOT-Ansible-managed shaping mechanism previously undocumented anywhere in this pack.
  Also added: the extensionless-`dhclient-enter-hooks`-vs-`.d/`-decoy capture trap; `dhclient@<iface>.service`'s instantiation-only-when-the-netplan-device-is-real behaviour; switch02 (`53x`) being
  cold-standby by design at every site except Horn Island, with the leased-vs-empty-slot triage refinement; the `LAN1`/`LAN2` Testra-managed uplink pair, outside the VLAN scheme and unmapped to
  `topology_vars`; the missing-route-vs-real-ARP-failure diagnostic (the actual Problem 2 mechanism at old-looma/umoona, live-verified 2026-07-29 — supersedes the dish-bypass theory for those two
  sites specifically).
- `references/08_ansible-authoring.md` — the confirmed list of roles that consume `interface.role` and go stale on topology drift the same way `smc_application` does (`smc_iptables`, `smc_qos`,
  `smc_node_exporter` — the last in a *separate playbook*, easy to miss); the topology-cloning authoring risk (a new site's `topology_vars` copied from an existing site can carry wrong VLAN IDs
  silently past every lint/syntax check); the standalone principle that one templated artifact being self-cleaning doesn't imply a sibling artifact from the same role is too; handler-name reuse across
  different `listen` topics being safe, not a collision.
- `references/13_known-issues.md` — new Known Operational Bug row: `my_node_network_device_info` returns zero series on old-looma/new-looma/horn-island despite `node_exporter` being up.
- `references/05_troubleshooting.md` — Tier 1 gained the `tsh ls`-vs-single-`ssh` technique for distinguishing a transient connection blip from a box that's fully deregistered from Teleport; Tier 7
  gained a step for metric-specific monitoring gaps that survive `up{instance=...} == 1`.
- `references/12_content-filtering.md` — one-line cross-reference so its existing "no per-user `tc`/`htb` shaping" claim isn't misread as "no `tc` shaping anywhere on the fleet."
- **New `scripts/` directory** — `collect-smc-evidence.sh` (read-only evidence capture) and `analyse-routing-drift.py` (the "hook covers netplan" drift discriminator), promoted from the investigation
  folder and genericized for reuse (no hardcoded default site list; `--flavor`/`--commit` override the investigation-specific defaults). Plus `routing-diagnostics.justfile`, a template task-runner to
  copy into a future investigation folder. See `scripts/README.md`.

### Corrected

- `references/03_communication-flows.md` — the dish-management-address bullet previously stated the dish-not-in-clean-bypass theory as the accepted cause of "lease held, gateway unreachable." Live
  testing 2026-07-29 showed this is not the cause on the two sites where it reproduced (the same MAC legitimately answers as gateway on every WAN interface there, healthy and broken alike) — qualified
  accordingly, downgraded from "the cause" to "a real, separate observation."
- `references/03_communication-flows.md` — the `smc_application` dhclient-restart-handler-has-no-safety-net bullet was stale relative to a same-day fix; updated from present-tense gap description to
  past-tense-fixed-with-caveat (ported, dry-run validated, not yet tested under a real connection loss).

Full narrative: `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/problem2-live-root-cause-20260729_2112.md` and `old-looma-umoona-topology-fix-20260729_2316.md`.

## 20260728_1240 — v0.1.5: captive-portal PHP SAPI correction + APPPATH/cache failure mode + Ansible tag hazard (project-coherence run)

Triggered by `project-coherence` on ansible-wifi after a 7-day captive-portal outage across 10 of 16 in-scope `rcp` sites (2026-07-21 → 07-28). Investigating it surfaced two materially wrong
architecture claims in this pack, both of the same kind the 2026-07-03 run already flagged: a single host's behaviour written up as fleet-wide truth.

### Corrected

- `references/10_captive-portal.md` §11.1 — previously stated flatly that "PHP-FPM processes `.php` files". **Wrong for the production fleet.** Verified on three sampled `rcp` hosts (horn-island,
  kalumburu, mornington): zero `php*-fpm` packages installed, `libapache2-mod-php` present, `apache2ctl -M` shows `php_module (shared)`, and no `/etc/php/8.1/fpm/` directory exists. Production runs
  **mod_php as `www-data`**. Replaced with a scoped, evidence-cited statement.
- `references/10_captive-portal.md` §11.4 — claimed a permanent Ansible `SetHandler` fix "landed 2026-06-26". **False.** Repo-wide grep finds no `SetHandler` in any role template (only a vendored
  `community.general` test fixture), and the enabled-modules list in `ubuntu-apache-install-configure.yml` is only `rewrite` and `ssl` — no `proxy`, no `proxy_fcgi`. This matches the long-standing
  ansible-wifi SCRATCHPAD open item recording the change was reverted. Section retitled as historical/ff-smc01-only with a supersession note at the top; the trailing "the Ansible template approach is
  now canonical" line corrected.
- `references/10_captive-portal.md` §11.7 — the verification snippet told you to test PHP-FPM processing and to read `error.log`. Replaced with a SAPI check (`apache2ctl -M`), a cache/logs perms
  check, an explicit warning that the §11.8 failure leaves the error log empty, and a warning not to probe `localhost` with a `Host:` header (Apache serves `000-default` and returns a healthy-looking
  10671-byte page on a fully dead portal — this produced a wrong "no impact" conclusion during the incident).

### Added

- `references/10_captive-portal.md` §11.8 — new failure mode: `Directory APPPATH/cache must be writable`. Covers the Kohana `core.php:281` bootstrap check, the matching `log/file.php:31` check on
  `APPPATH/logs` (fix both or the failure just moves one step later), why the response is **HTTP 200** with an empty apache error log, the correct probe form, and the fix command.
- `references/06_failure-modes.md` — matching failure-mode table entry with error signature, cause class, source-of-truth paths, immediate checks, resolution, and the detection gap.
- `references/08_ansible-authoring.md` — new "Tag Hazard" entry: a tagged block that destroys and recreates state must carry its repair tasks under the same tag, including any `stat` task whose
  registered variable gates the repair block's `when` (otherwise a tag-limited run evaluates `when` against an undefined variable and fails). Includes the `--list-tasks` audit pattern.
- `references/13_known-issues.md` — new fleet-wide risk row: no HTTP-level captive-portal monitoring exists anywhere, and the Kohana usage/status crons run as **root** so they keep succeeding through
  an outage; also notes a status-code-only probe cannot detect this failure. Plus a staleness-risk note recording this as the **third** instance of the single-host-generalized-to-fleet pattern in this
  pack (after the 2026-07-03 DNS row and the 2026-07-09 MySQL row).
- `manifest.json` — three new `stable_facts` entries (mod_php not PHP-FPM; the Kohana writability check and its HTTP-200 signature; the Ansible tag-hazard rule). Version bumped 0.1.4 → 0.1.5;
  `updated_at` set to 2026-07-28T12:40:00Z.

### Related (outside this pack)

- `local-knowledge-ansible/ansible-wifi/issues/rcp-fleet/rcp-captive-portal-cache-perms-outage-20260728_1240.md` — full RCA.
- `ansible-wifi/.archcore/rules/rule-005-tagged-destroy-blocks-must-carry-repair-tasks.md` — new permanent rule.
- `ansible-wifi/roles/smc_application/tasks/main.yml` — the actual fix (uncommitted at time of writing).

## 20260703_1300 — v0.1.4: DNS architecture corrections + garimba-smc01 failure mode (project-coherence run)

Triggered by `project-coherence` on ansible-wifi after the garimba-smc01 DNS RCA (revisions 2-3) surfaced factual errors in this pack's DNS documentation that predated the incident — rule-002 had
never actually been applied for a DNS-domain incident before, and the domain routing table had no explicit DNS row.

### Corrected

- `references/02_service-map.md` — DNS resolver row previously claimed "unbound = RCT flavor / bind = non-RCT flavors", generalized from the single initial RCT-only validation. Corrected: the real
  gate is `smc_ltp` inventory-group membership (orthogonal to flavor, currently only coincides with `rcp`/guda-guda). Also fixed Stubby's documented listen port (was wrongly given as `127.0.0.1:5353`
  — that's actually unbound's own `smc_ltp`-only port; Stubby listens on `127.0.0.1@60053`).
- `references/13_known-issues.md` — added a staleness-risk note generalizing the lesson: single-host-validated claims in this pack should not be assumed to hold across all flavors without an
  independent check.

### Added

- `references/02_service-map.md` — new `systemd-resolved` row documenting the SMC's own DNS path (separate from the DHCP/LAN unbound/stubby/bind path), and Stubby's upstream chain (single upstream, no
  failover, reached via an autossh **local port forward** — not a reverse tunnel — to Teleport).
- `references/06_failure-modes.md` — new failure-mode entry: domain-specific host DNS resolution delay on non-`smc_ltp` hosts (`DNSStubListener=no` exposes host glibc directly to WAN-path DNS
  anomalies). First confirmed on garimba-smc01, 2026-07-03.
- `references/13_known-issues.md` — new "Fleet-Wide Architecture Risks" section: Stubby's single-upstream-no-failover design and the lack of monitoring for the autossh local forward / Stubby upstream
  reachability, both fleet-wide, both discovered incidentally during the garimba-smc01 RCA.
- `.archcore/rules/rule-002-*.md` (ansible-wifi repo) and `AGENTS.md` (ansible-wifi repo) — added an explicit DNS domain row to the domain-routing tables, since none existed despite DNS being a
  documented troubleshooting area.
- `manifest.json` — new `stable_facts` entry on the `smc_ltp`-vs-flavor DNS gating; version bumped 0.1.3 → 0.1.4; `updated_at` set to 2026-07-03T13:00:00Z.
- `SCRATCHPAD.md` — current state and session history updated.

## 20260626_1845 — v0.1.3: project-coherence checklist + references/10-13 content update

### Added

- `AGENTS.md` — `## Project-coherence checklist` section: explicit Tier 1-4 update instructions for when `project-coherence` runs on this pack, with domain-to-reference routing table and cross-repo
  trigger rule from ansible-wifi sessions.

### Updated

- `references/10_captive-portal.md` — captive portal two-tier arch, Eclipse config.txt sync mechanism, PHP-FPM SetHandler + a2enconf alternative, PHP short_open_tag (PHP 8.1), Kohana exception
  handler.
- `references/11_vagrant-lab.md` — vsmc networkd race condition full root cause chain (eth1 bounce → stale DHCP lease → default route drop → Teleport unreachable); Vagrant guard fix.
- `references/12_content-filtering.md` — Eclipse identity model (T&C → auto-PIN → MAC binding → connmark), MAC randomization impact table (stable/bypass/rotate), CAKE fair queuing on bridge_501 with
  WAN capacity rationale.
- `manifest.json` — version bumped 0.1.2 → 0.1.3; `updated_at` set to 2026-06-26T18:45:00Z.
- `SCRATCHPAD.md` — current state updated; session history entry added; open items updated for v0.1.3.

### Notes

- Content updates fed from ansible-wifi 2026-06-26 session RUNBOOK audit (MK keys: `ansible-wifi.runbook.sections-11-12-13.20260626`, `ansible-wifi.runbook.gap-fill-audit.20260626`).
- Governance-pack regeneration pending (`.ai-context/governance-pack.md` is stale after this change).

## 20260626_1820 — Coherence sweep: repomix config, adapter.md, spec, ARCHITECTURE.md

### Fixed

- `repomix.config.json` — added `README.md`, `ARCHITECTURE.md`, `SCRATCHPAD.md`, `.archcore/**/*.md`, `.archcore/**/*.json` to `include`; moved `.archcore/**` out of `ignore`
- `exports/claude_code/project/skill-smc/adapter.md` — added install-status rows for all 12 governance files added since initial adapter.md creation: `manifest.json`, `README.md`, `ARCHITECTURE.md`,
  `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`, `repomix.config.json`, `.archcore/`
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

| Assumption                   | Validated Reality (RCT)                                              |
| ---------------------------- | -------------------------------------------------------------------- |
| DNS = BIND/named             | RCT uses Unbound + Stubby (DNS-over-TLS)                             |
| Traditional swap             | RCT uses zram (`/dev/zram0`, ~1.2 GB)                                |
| iptables chain = `ECLIPSE_*` | Actual chain: `MANAGEMENT`                                           |
| asterisk present             | Not deployed on RCT                                                  |
| keepalived present           | Not deployed on RCT                                                  |
| 40 GB storage                | Real ext4 FS = 60 GB at `/media/root-ro`; overlayroot = 984 MB tmpfs |
