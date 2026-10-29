---
Title: APN operator context
Category: operator-context
Status: current
Authority: internal
Scope: APN-specific architecture knowledge for skill-network-architect and skill-systems-architect
Last reviewed: 2026-10-29
Summary: Index of what both architects need to know about the APN estate, harvested from the APN projects on 2026-10-29; contained here so the general references stay operator-neutral.
---

# APN operator context

Read this folder only when the work concerns the APN estate. The general references in `references/` stay operator-neutral; every item here links back to the general section it applies, so a lesson
learned at APN is also findable as a pattern.

## Rules for this folder

- Facts only at the level an architect needs: no customer, community or people names, no IP addresses, credentials, prices, margins or invoice figures. Carrier figures live in the projects, always
  ex-GST, and are never copied here.
- Each item gives the fact, why it matters, the evidence path in the APN projects and the general section it applies to.
- Device, firmware and SMC facts belong to skill-smc, skill-cambium and skill-mikrotik; Nautobot and OpenWISP facts to their platform packs. Link, do not copy.
- Write-backs: a new APN lesson goes to the matching file here, and its generic form to the general reference (SKILL.md, Standing Write-Back Contract).
- The systems pack reads this folder by path (`../skill-network-architect/operator/apn/`); there is no copy.

## Estate in one paragraph

An Australian ISP serving remote and regional communities: subscriber access over nbn, Opticomm (owned by Uniti Group) and an aggregator's backhaul, and geostationary satellite to remote sites; at
each remote site a Raspberry-Pi-class site box (SMC) in the user's path with MikroTik and Cambium equipment behind it; central services on Proxmox; fleet intent in Nautobot and telemetry in OpenWISP
and Prometheus/Grafana under the unified-network-controller project; access through Teleport; a voice platform on Asterisk with carrier SIP trunks.

## Files

- [access-and-voice.md](access-and-voice.md): wholesale access (nbn, Opticomm, aggregator), the subscriber-edge lab (vBNG), voice platform and trunks.
  Feeds australian-access-networks, service-provider-edge, voice-and-sip.
- [site-fleet-network.md](site-fleet-network.md): remote-site network: site shapes, satellite constraints, management access, discovery, site services.
  Feeds remote-site-fleet, network-services, security-and-segmentation, routing-and-switching.
- [oss-bss-and-fleet-data.md](oss-bss-and-fleet-data.md): OSS/BSS data, billing reconciliation flows, fleet source of truth and telemetry.
  Feeds the systems references service-provider-systems and fleet-management.
- [site-boxes-and-platforms.md](site-boxes-and-platforms.md): site-box resilience and flash wear, central platforms, colocation and cloud exit, AI platform.
  Feeds the systems references edge-appliances, storage-and-data, migration-and-hybrid, ai-inference-platforms.

## Source projects

Under `/Volumes/Data/_ai/_project/project_stuff/apn/`; read the project, not this index, for anything time-sensitive.

| Project                                                               | Architecture topic                                                           |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `unified-network-controller`                                          | fleet source of truth, telemetry, discovery, controller design               |
| `smc-resiliency`, `smc-squid-redesign`, `smc-file-writing-analysis`   | site-box resilience, caching proxy over satellite, flash write reduction     |
| `cambium-swap`, `switching-refresh`                                   | vendor exit and controller dependencies; switching baseline                  |
| `teleport`                                                            | zero-trust access to the fleet                                               |
| `vbng` (`podbng-lab`)                                                 | subscriber edge (BNG, RADIUS, CGNAT) lab                                     |
| `opticomm-profitability`, `vocus-profitability`                       | wholesale constructs and reconciliation (figures stay in the projects)       |
| `voip-analysis`, `apn-sip-setup`                                      | voice platform, trunks, call records                                         |
| `aws-to-local`, `equinix-cost-cutting`                                | cloud repatriation, colocation design and power                              |
| `enterprise-strategy`, `technology-strategy_2027-2030`, `ai-strategy` | platform strategy, decision frameworks, AI platform                          |
| two community and program folders                                     | remote-community Wi-Fi and a government program (named in the projects only) |
