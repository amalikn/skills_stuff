# SMC Dependency Tree

## 4. Dependency Tree

Services in order of criticality (what breaks everything downstream when down):

```
Level 0 — Foundation
  overlayroot         → must be healthy before any file write has effect
  network             → everything depends on connectivity

Level 1 — Remote Management
  teleport            → all remote access (SSH, Ansible, CI) is lost without this
  autossh-teleport-openssh → Teleport tunnel; without it teleport node is unreachable

Level 2 — Local Services
  isc-dhcp-server     → WiFi clients cannot get IPs
  unbound / named     → clients cannot resolve DNS
  hostapd             → WiFi clients cannot associate

Level 3 — Monitoring
  autossh-prometheus-federation → metrics federation to central Prometheus lost
  node_exporter       → all system metrics stop
  prometheus (local)  → local metrics storage, speedtest scraping

Level 4 — Optional / Flavor-Specific
  asterisk            → VoIP (rcp only, apn-cluster-exclusive — never on cw-cluster flavors)
  keepalived          → HA VIP failover (non-RCT only)
  cnmaestro-provisioning → WiFi AP cloud provisioning
  redis               → required by cnmaestro-provisioning
  apache2             → web app access (RCT: Kohana + Tstik)
  clamav-daemon / clamav-freshclam → antivirus hardening (nbn_accelerate only, apn-cluster-exclusive-absent)
  lynis               → security-audit CLI, on-demand only, no daemon (nbn_accelerate only)
  smc_ltp (7 rcp sites — see 08_ansible-authoring.md) → bind9/named replaces unbound+stubby;
                         CNMaestro Cambium ePMP/cnPilot backhaul provisioning via a SEPARATE
                         smc_cnmaestro_provisioning role/playbook (smc_ltp.yml) — distinct
                         mechanism from the "cnmaestro-provisioning" service two rows above; do
                         not conflate the two without checking which one a given host actually runs
```

**smc_ltp vs the generic `cnmaestro-provisioning` service — a naming collision risk, not yet fully resolved.** The Level 4 `cnmaestro-provisioning`/`redis` row above (WiFi AP cloud provisioning,
`systemctl status cnmaestro-provisioning`, `redis-cli ping` — see `05_troubleshooting.md` Tier 4) predates the 2026-08-03 `smc_ltp` exploration and appears to describe a different mechanism: the
`smc_ltp`-only path found 2026-08-03 uses `roles/smc_cnmaestro_provisioning` (a Python script + static YAML config, no Redis dependency observed) invoked by the standalone `smc_ltp.yml` playbook, not
a `cnmaestro-provisioning` systemd service. Both provision Cambium/CNMaestro-managed wireless gear, so the naming overlap could be: (a) two genuinely separate provisioning paths for different hardware
roles, (b) the same underlying mechanism described two different ways by different sessions, or (c) the Level 4 row above being written from a different flavor's architecture (RCT) than `smc_ltp`
(`rcp`-only). Not resolved — check which flavor/host a given "cnmaestro-provisioning" troubleshooting reference actually applies to before assuming it's the same thing as `smc_ltp`'s CNMaestro
provisioning. See `08_ansible-authoring.md` "smc_ltp Sub-Group" for the `smc_ltp` mechanism in full.

**Resolved 2026-09-21 — answer (b): one mechanism, two versions on two branches.** The 2026-08-03 reading came from `master`, whose `cnmaestro-provisioning.py` is 3,222 lines with no Redis. The
ansible-wifi `big_push` branch (36 commits by Daniel Gravolin, last 2026-08-25, not merged into `master`) grows the same script to 4,514 lines and adds Redis, from commit `5b415d9b` (2025-10-15):
automatic location IDs and lot numbers. Verified live, read-only, the same day: `umoona-smc01` runs a 4,509-line copy byte-identical to `big_push` commit `40c283b6`, with `redis-server` active;
`pandanus-park-smc01` runs a 4,509-line copy that matches no commit on any branch, i.e. it was deployed from uncommitted changes. So the Redis-dependent service is the `smc_ltp` low-touch script as
the fleet actually runs it, and `master` is behind the fleet. `big_push` also routes cnMaestro calls through the internal Wi-Fi dashboard (`wifi.prod.apn-services.com.au`), handles replacement
devices, and sends WhatsApp installer and Teams NOC alerts. Recorded by the unified-network-controller architecture brief (point 3), which pins `big_push` as the low-touch source until it is merged.

---

