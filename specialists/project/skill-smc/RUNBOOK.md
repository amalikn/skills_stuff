# SMC Box Operational Runbook

**Validated against:** malik-rct01 (RCT flavor, ARM64, Ubuntu 22.04, overlayroot enabled)
**Scope:** x86 and ARM64 SMC appliances managed by `ansible-wifi`

This file is the navigation index for the `skill-smc` specialist pack. Load only the focused reference needed for the task instead of reading every SMC detail up front.

## SMC-Related Workspaces

| Path                                                          | Relationship                                                                                  |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `/Volumes/Data/_ansible/ansible-wifi`                         | Production Ansible source for SMC roles, inventories, topology, and URL-capture deployment    |
| `/Volumes/Data/_ansible/ansible-malik`                        | Operator playbooks for SMC operations, including `smc_get_pcapv*.yml` fetch/process workflows |
| `/Volumes/Data/_ai/_scripts/scripts_stuff/python/dns_query`   | DNS reporting and workbook pipeline consuming SMC URL-capture PCAP output                     |
| `/Volumes/Data/_ansible/local-knowledge-ansible/ansible-wifi` | Local-only SMC plans, reports, OPA artifacts, and investigation knowledge for `ansible-wifi`  |

Reference hygiene: when a URL-capture or PCAP-layout change affects more than one workspace, update the relevant focused reference plus the relevant repo governance files in the same session where
practical.

## Reference Routing

| Task                                                                                                                                                | Read                                           |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Basic SMC definition, inventory flavors, remote access, satellite constraints, APN vs NBN Accelerate cluster differences                            | `references/01_overview.md`                    |
| Service names, config paths, monitoring collectors, RCT vs x86 service map                                                                          | `references/02_service-map.md`                 |
| External communication paths and inbound/outbound flows; **how to reach/query a backend's API or dashboard** (Grafana, Graylog, Teleport Application | `references/03_communication-flows.md`         |
|   Access, mTLS/token auth); **backdoor root SSH to a box when `tsh ssh` itself is hung/unreachable** (raw reverse tunnel, port = 50000 + siteid)    |   §Backdoor SSH Access                         |
| `wifi-02.activ8me.net.au` / `202.171.100.138` — APN's OWN keepalived/LVS VIP, not a third party; static `/etc/hosts` entry; per-site public egress  | `references/03_communication-flows.md`         |
|   IP check (`curl -sS https://api.ipify.org`) and known values; `cw-teleport01` as an APN-side diagnostic vantage point                             |                                                |
| Port 80 to `202.171.100.138` fails ("No route to host", ~1 RTT) while ping and port 443 work — source-IP allowlist reject, not a routing failure    | `references/06_failure-modes.md` §Port-80      |
|                                                                                                                                                     |   Source-IP Allowlist                          |
| "Is it them or us?" — locating where an ICMP rejection was generated via TTL comparison, reject-vs-drop latency, and on-box tooling gotchas (no     | `references/05_troubleshooting.md` §Cross-Tier |
|   `traceroute`; `mtr -I` ignores `--interface`; tcpdump buffering and ICMP filters; curl exit 7 vs 56)                                              |                                                |
| Dependency relationships between network, DNS, portal, monitoring, and access systems                                                               | `references/04_dependency-tree.md`             |
| Live incident triage, alerts, service failures, DHCP/DNS/WiFi/VoIP/HA issues                                                                        | `references/05_troubleshooting.md`             |
| Known failure signatures and fix patterns                                                                                                           | `references/06_failure-modes.md`               |
| Box unreachable by both `tsh` and reverse tunnel, fixed by power cycle — read before blaming the SD card/disk. Cross-flavor: `wh` (windjana-gorge,  | `references/06_failure-modes.md` §Silent       |
|   kupungarri) and `rcp` (pandanus-park)                                                                                                             |   Total Hang                                   |
| When did this site actually die? 3-year Prometheus retention; why Graylog silence is not proof a box was down; how to actually query Graylog for it | `references/06_failure-modes.md` §Silent       |
|   (Teleport App Access, not a bare `curl`) is in `references/03_communication-flows.md`                                                             |   Total Hang                                   |
| Why `rct` self-recovers and `wh`/`rcp` do not — tstik vs `watchdog.auto_reboot: 0` vs no RISE at all, no hardware watchdog anywhere in repo         | `references/06_failure-modes.md` §Silent       |
|                                                                                                                                                     |   Total Hang                                   |
| Hardware differences, overlayroot, disk write behavior, persistence risk                                                                            | `references/07_hardware-overlay.md`            |
| Overlayroot copy_up cost model, `recurse=0` escape hatch, log capping (`smc_rise_logcaps`)                                                          | `references/07_hardware-overlay.md` §8         |
| Box reboot-looping every few minutes (overlay RAM exhaustion)                                                                                       | `references/05_troubleshooting.md` Tier 8b     |
| Ansible topology vars, cache coherence, validation commands, generator drift, smc_ltp sub-group, "low touch" onboarding history                     | `references/08_ansible-authoring.md`           |
| Code notes: RULE-006 comment/note split, note provenance (context, branch, commit), what survives a branch switch, `check_note_anchors.py`          | `references/08_ansible-authoring.md`           |
|                                                                                                                                                     |   §Code notes                                  |
| URL capture v2, PCAP layout, fetch/process workflows, dns_query assumptions                                                                         | `references/09_url-capture-pcap.md`            |
| Captive portal, Eclipse config sync, Kohana issues, portal PHP (mod_php, not PHP-FPM)                                                               | `references/10_captive-portal.md`              |
| Local Vagrant lab bring-up and known virtualization issues                                                                                          | `references/11_vagrant-lab.md`                 |
| Family-friendly VLAN 501 access, filtering stack, MAC randomization, CAKE                                                                           | `references/12_content-filtering.md`           |
| Coverage gaps, live-validation limits, stale assumptions                                                                                            | `references/13_known-issues.md`                |
| Verified SNMP OIDs on the SMC box itself (net-snmp agent, canary 2026-09-24), the machine-readable list the controller reads                         | `references/snmp-oid-registry.yaml`          |
| Pin validity (mangle) vs pin issuance (Apache access log) — two mechanisms, marks-≠-activations pitfalls, fleet case study                          | `references/14_pin-activation-diagnosis.md`    |
| Reusable read-only scripts: WAN-routing/topology-drift investigation tooling (evidence capture, drift analyser, topology/hardware cross-check),     | `scripts/README.md`                            |
|   plus ansible-lint pre-push/CI gate scripts, fleet hardware/service-health + portal-FQDN-status audit, and pin-activation diagnosis                |                                                |
| Cambium asset-register naming grammar, per-site drift, `rcp`-vs-`nbn_accelerate` R195P rule, R195P IP-derivation formula, extraction gotchas        | `references/15_cambium-asset-registers.md`     |

## Runtime Paths

- ansible-wifi venv: `/Volumes/Data/_ai/_skills/skills-working-cache/ansible-wifi/venv`
- skill-smc venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-smc/venv`
- ephemeral logs, pid files, and sockets: `/Volumes/Data/_ai/_skills/skills-runtime/<skill>/`

Prefer the working-cache venvs when running SMC validation tooling (`ansible-lint`, `yamllint`, `ansible-inventory`, `ansible-playbook`) to keep versions stable across sessions.
