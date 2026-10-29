---
Title: FOSS-first tool selection
Category: reference
Status: current
Authority: authored-guidance
Scope: Shared by skill-network-architect and skill-systems-architect
Last reviewed: 2026-10-29
Summary: >-
  How to choose a tool when one is actually needed: selection order, licence observations for common candidates (checked 2026-10-29), patterns and
  anti-patterns, and an assessment checklist.
---

# FOSS-first tool selection

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Licence observations](#licence-observations)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- Load this file only when a tool choice is actually required.
- FOSS-first applies to proposed add-ons. It does not replace the operator's working stack without a stated reason.
- Windows, macOS and commercial network platforms remain valid architecture knowledge; they are not proposed add-ons.

## Decision rules

- Order: state the capability and constraint; reuse an installed suitable tool; evaluate maintained FOSS; record any gap.
- "Free to use", "source available", "free hosted tier" and "FOSS" are four different claims.
- Read the exact release licence, dependencies, edition limits, plugins, images and redistribution terms before committing.
- A FOSS controller can manage proprietary hardware. That does not make the firmware FOSS.
- Licences change between releases. Recheck at every major upgrade, not only at selection.
- Treat MCP servers and agent plugins as executable dependencies with narrowly scoped access.
- No architecture skill requires an MCP server. Prefer existing supported APIs and CLIs.
- Keep the architecture portable: requirements, identities, flow contracts, failure analysis, ADRs and tests outlive the tool.
- Keep vendor syntax in implementation artefacts and specialist packs, not in core diagrams or intent schemas.
- For proprietary platforms use vendor documentation and existing entitlements. Never recommend unlicensed software.

## Licence observations

Upstream licence files read 2026-10-29. These are file observations, not legal advice. Each row links the file read.

| Candidate           | Capability                           | Licence seen                                            | Caveat                                                        |
| ------------------- | ------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------- |
| OpenTofu            | infrastructure provisioning          | [MPL-2.0][l-tofu]                                       | providers licensed separately                                 |
| Terraform           | infrastructure provisioning          | [BUSL][l-tf]                                            | source-available, not FOSS; OpenTofu is the MPL-2.0 fork      |
| Ansible core        | configuration orchestration          | [GPL-3.0][l-ansible]                                    | collection licences vary                                      |
| Nornir              | Python fleet orchestration           | [Apache-2.0][l-nornir]                                  | plugins and transports separate                               |
| Batfish             | configuration-model verification     | [Apache-2.0][l-batfish]                                 | models only supported vendor features                         |
| SuzieQ              | live-state collection and assertions | [Apache-2.0][l-suzieq]                                  | an enterprise edition exists; check which one is in use       |
| containerlab        | network lab orchestration            | [BSD-3-Clause][l-clab]                                  | network OS images may be proprietary                          |
| FRRouting           | routing daemons                      | [mixed per-file SPDX; binary GPL-2.0+][l-frr]           | read SPDX headers and bundled notices                         |
| Nautobot            | intended inventory and automation    | [Apache-2.0][l-nautobot]                                | apps and hosted services separate                             |
| NetBox              | inventory and IPAM                   | [Apache-2.0][l-netbox]                                  | plugins and hosted services separate                          |
| Prometheus          | metrics and alerting                 | [Apache-2.0][l-prom]                                    | exporters licensed separately                                 |
| Grafana             | dashboards                           | [AGPL-3.0][l-grafana]                                   | network-use terms if modified and served; Enterprise separate |
| OpenWISP controller | device management and monitoring     | [GPL-3.0][l-openwisp]                                   | check each openwisp module and its time-series backend        |
| Kea                 | DHCP                                 | [MPL-2.0][l-kea]                                        | hook libraries licensed separately                            |
| Proxmox VE          | virtualisation                       | [AGPL-3.0-or-later][l-pve]                              | enterprise repository is a paid subscription                  |
| Teleport            | access proxy                         | [source AGPL-3.0; Community binaries modified Apache-2.0][l-teleport] | read the Community licence conditions                         |
| Graylog Open        | log management                       | [SSPL-1.0][l-graylog]                                   | source-available, not OSI-approved, since v4.0 (2021)         |

[l-tofu]: https://raw.githubusercontent.com/opentofu/opentofu/main/LICENSE
[l-tf]: https://raw.githubusercontent.com/hashicorp/terraform/main/LICENSE
[l-ansible]: https://raw.githubusercontent.com/ansible/ansible/devel/COPYING
[l-nornir]: https://github.com/nornir-automation/nornir/blob/main/LICENSE
[l-batfish]: https://github.com/batfish/batfish/blob/master/LICENSE
[l-suzieq]: https://github.com/netenglabs/suzieq/blob/develop/LICENSE
[l-clab]: https://raw.githubusercontent.com/srl-labs/containerlab/main/LICENSE
[l-frr]: https://raw.githubusercontent.com/FRRouting/frr/master/COPYING
[l-nautobot]: https://raw.githubusercontent.com/nautobot/nautobot/develop/LICENSE.txt
[l-netbox]: https://raw.githubusercontent.com/netbox-community/netbox/main/LICENSE.txt
[l-prom]: https://raw.githubusercontent.com/prometheus/prometheus/main/LICENSE
[l-grafana]: https://raw.githubusercontent.com/grafana/grafana/main/LICENSE
[l-openwisp]: https://raw.githubusercontent.com/openwisp/openwisp-controller/master/LICENSE
[l-kea]: https://raw.githubusercontent.com/isc-projects/kea/master/COPYING
[l-pve]: https://git.proxmox.com/?p=pve-manager.git;a=blob_plain;f=debian/copyright;hb=HEAD
[l-teleport]: https://raw.githubusercontent.com/gravitational/teleport/master/build.assets/LICENSE-community
[l-graylog]: https://raw.githubusercontent.com/Graylog2/graylog2-server/master/LICENSE

- Graylog licence change announcement: <https://graylog.org/post/graylog-v4-0-licensing-sspl/>
- Redis moved to source-available terms; Redis 8 adds an AGPL-3.0 option. Licence file:
  - <https://raw.githubusercontent.com/redis/redis/unstable/LICENSE.txt>
- Other candidates to investigate, licences not certified here: Linux/KVM/libvirt, OpenZFS, Ceph, Kubernetes, Podman, restic, Borg, BIND, Unbound, HAProxy, nftables, WireGuard, FreeRADIUS, FreeIPA,
  Samba, osquery.

## Patterns and anti-patterns

| Situation                            | Do                                                              | Avoid                                         | Why                                         |
| ------------------------------------ | --------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------- |
| Operator already runs a working tool | keep it; propose change only for a stated gap                   | replacing it for FOSS purity                  | migration and exit cost are real            |
| "Free" product with a paid edition   | list which features the design needs and which edition has them | assuming the free edition covers HA, SSO      | edition limits break designs late           |
|                                      |                                                                 |   or API                                      |                                             |
| Network change validation            | add a config-model step (Batfish) and live assertions (SuzieQ)  | relying on "push succeeded"                   | the push proves syntax, not behaviour       |
| Licence read once at selection       | recheck at each major upgrade                                   | trusting an old assessment                    | Terraform, Graylog and Redis all changed    |
| A tool shapes the intent schema      | keep the schema tool-neutral                                    | vendor fields in core intent                  | the tool will be replaced before the design |

## Review checklist

- [ ] Required capability stated before any product is named
- [ ] Current solution and its gap recorded
- [ ] Exact release, licence file URL and date of reading recorded
- [ ] Edition limits, plugins, images and hosted terms checked
- [ ] Dependencies, authentication, backup and export format, observability and upgrade path listed
- [ ] Operating effort and cost stated with assumptions; no invented prices
- [ ] Proof-of-concept test with stop criteria defined
- [ ] Exit path: how to leave the tool and what data comes out

## Further reading

All links resolved 2026-10-29.

Licence identification:
- [OSI approved licenses](https://opensource.org/licenses) and [Open Source Definition](https://opensource.org/osd): whether a licence is open source at all.
- [SPDX license list](https://spdx.org/licenses/): canonical identifiers to record in an assessment.
- [choosealicense.com](https://choosealicense.com/licenses/): plain-language permissions, conditions and limits.
- [REUSE](https://reuse.software/): per-file licence and copyright conventions.

Project health and supply chain:
- [OpenSSF Scorecard](https://scorecard.dev/): maintenance and security-practice signals for an upstream repository.
- [SLSA](https://slsa.dev/): build provenance levels for released binaries and images.
- [OpenChain](https://openchainproject.org/): an organisational licence-compliance process (ISO/IEC 5230).
