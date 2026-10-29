---
Title: Containers, orchestration and platform services
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: Containers, orchestration and platform services decisions, failure modes and validation.
---

# Containers, orchestration and platform services

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Platform layers and failure domains](#platform-layers-and-failure-domains)
- [Single-host compose stacks](#single-host-compose-stacks)
- [Kubernetes essentials](#kubernetes-essentials)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Choosing the smallest runtime that meets the need: compose on a VM, Podman/systemd, or Kubernetes.
- Workload contract, stateful services, and recovery of the platform itself.
- Supply chain and security proportionate to risk.

## Decision rules

Choose the smallest suitable runtime:

| Need                                               | Choose                                                 | Gives up                                            |
| -------------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------- |
| One app, vendor-supported image set, one site      | VM running Docker/Podman compose                       | automatic cross-host restart (use hypervisor HA)    |
| Several stacks, small team, restart on host loss   | compose per VM + hypervisor HA + backups               | rolling upgrades without downtime                   |
| Many services, frequent releases, horizontal scale | Kubernetes (3 control-plane nodes minimum for HA)      | simplicity; adds etcd, CNI, CSI, ingress to operate |
| Edge box with one or two services                  | Podman/systemd (Quadlet) or Docker with restart policy | central scheduling                                  |

- Kubernetes answers a demonstrated need. It is not the default foundation.
- Hypervisor HA plus compose often meets RTO targets of minutes at far lower operating cost.
- Containers share the guest kernel: a kernel bug or panic hits every container on that VM. Use VMs for hard tenant isolation.

Workload contract (define before deploying):

- Image digest, architecture (amd64 or arm64 for edge), resources, data paths, secrets, identity, health endpoints.
- Graceful termination (SIGTERM handling, grace period), upgrade order and schema-migration behaviour.
- Readiness must reflect the ability to serve. Capacity includes image pulls, log growth, eviction and one degraded node.

Stateful services:

- Decide which state lives inside the platform and who owns application-consistent backup and restore.
- Validate storage attach and detach, permissions, recovery order, schema compatibility and failover.
- An operator or controller is another dependency, with its own upgrade, access and DR path.
- Reverting a manifest does not revert migrated data. Back up the database before every schema-changing upgrade; test restore with the old image.

Supply chain and security:

- Pinned artifacts, least-privilege service identity, rootless runtimes where possible, read-only root filesystems, admission control.
- Build provenance proportionate to risk; SLSA levels give the vocabulary.
- Keep registry, GitOps reconciler, credentials and break-glass recoverable while the platform is down.
- A private registry inside the cluster it serves is a circular dependency.
- Coordinate CNI, ingress, egress, DNS and network policy with the network architect.

## Platform layers and failure domains

```text
Platform layers: a failure at any layer takes down every layer above it on that host

  +--------------------------------------------------------------+
  | application (Nautobot, OpenWISP, Grafana, ...)               |  owner: app team
  +--------------------------------------------------------------+
  | containers: image + config + secrets + volumes               |  pinned digest
  +--------------------------------------------------------------+
  | runtime / orchestrator (dockerd, podman, kubelet + etcd)     |  restart policy
  +--------------------------------------------------------------+
  | guest OS / VM  (kernel shared by all containers in it)       |  patch cadence
  +--------------------------------------------------------------+
  | hypervisor cluster: quorum, HA restart, storage              |  virtualisation reference
  +--------------------------------------------------------------+
  | host hardware, power, network                                |  compute reference
  +--------------------------------------------------------------+
  Replicas help only when they land on different hosts and racks in the bottom two layers.
```

## Single-host compose stacks

- Compose starts dependencies first but by default waits only until they run, not until ready. VERIFIED_PRIMARY, [compose-order], checked 2026-10-29.
- Gate dependents with `depends_on: condition: service_healthy` plus a `healthcheck` (for Postgres, `pg_isready`).
- Restart policies: `no`, `on-failure[:max-retries]`, `always`, `unless-stopped`. VERIFIED_PRIMARY, [docker-restart], checked 2026-10-29.
- `unless-stopped` does not restart a container that was stopped, even after a daemon restart.
- A restart policy applies only after a container has run for 10 seconds.
- Docker Engine does not restart a container just because its healthcheck reports unhealthy (UNVERIFIED in the docs read; test it or add a watchdog).
- Named volumes and bind mounts hold the state; the container is disposable. Back up databases with their own tools, not live volume copies.
- Bound log growth with logging-driver size and rotation, or ship logs to the central collector.
- Pin images by digest or exact tag. `latest` makes rollback and DR non-reproducible.

## Kubernetes essentials

- etcd needs a majority: quorum = (n/2)+1. Run 3 or 5 members; an even count adds no tolerance. VERIFIED_PRIMARY, [etcd-faq], checked 2026-10-29.
- Snapshot etcd regularly and encrypt the snapshots; they hold cluster secrets. VERIFIED_PRIMARY, [k8s-etcd], checked 2026-10-29.
- Losing etcd without a snapshot loses the cluster state, not the container images.
- PodDisruptionBudgets limit voluntary disruption (drain, upgrade). They do not protect against node crashes. VERIFIED_PRIMARY, [k8s-disruptions].
- Requests drive scheduling. Limits drive CPU throttling and memory OOM kills.
- Size nodes for requests + daemon overhead + one node's worth of evicted pods.
- Spread replicas with topology spread constraints or anti-affinity. A replica count alone proves nothing.
- Probes: readiness gates traffic; liveness restarts; startup protects slow starters.
- A liveness probe that checks a dependency turns a database blip into a restart storm.

## Patterns and anti-patterns

| Pattern                               | Use when                   | Anti-pattern                            | Why it fails                                      |
| ------------------------------------- | -------------------------- | --------------------------------------- | ------------------------------------------------- |
| Compose on a VM + hypervisor HA       | few stacks, RTO in minutes | Kubernetes for two services             | etcd, CNI, CSI and upgrades outweigh the benefit  |
| Health-gated `depends_on`             | app depends on a database  | plain `depends_on`                      | app starts before the DB is ready and crash-loops |
| Pinned digest                         | every production image     | `latest` tag                            | rollback and DR rebuild pull a different image    |
| etcd across 3 failure domains         | Kubernetes control plane   | 2 of 3 etcd members in one zone         | that zone's loss stops the control plane          |
| Readiness checks own ability to serve | every service              | liveness probe on a dependency          | a dependency blip restarts every pod              |
| Registry mirror outside the cluster   | DR and cold start          | registry only inside the served cluster | cannot pull images to rebuild the cluster         |

## Failure modes and tests

| Failure                                            | Symptom                             | Blast radius             | Proving test                                                        |
| -------------------------------------------------- | ----------------------------------- | ------------------------ | ------------------------------------------------------------------- |
| Restart policy missing or `unless-stopped` after a | stack down after reboot             | every service on the VM  | reboot the VM; all services healthy without intervention            |
| manual stop                                        |                                     |                          |                                                                     |
| No healthcheck condition                           | crash loops after DB restart        | dependents of the DB     | restart the DB alone; dependents recover without crash loops        |
| All replicas on one node                           | outage on a single node loss        | the replicated service   | cordon and drain, or kill the node; service stays up                |
| No etcd snapshot                                   | cluster state unrecoverable         | every workload in        | restore an etcd snapshot into a lab cluster                         |
|                                                    |                                     | the cluster              |                                                                     |
| Schema migrated forward                            | rollback image cannot read the data | the service and its data | roll back the image in staging after a migration; record the result |
| Registry only in the primary site                  | DR rebuild cannot pull images       | every service in DR      | rebuild DR from a mirror or registry replica with the               |
|                                                    |                                     |                          | primary offline                                                     |

## Worked example

Four Kubernetes workers of 64 GiB in two zones (w1, w2 in zone A; w3, w4 in zone B). Reserve 6 GiB per node for OS, kubelet and daemons. Pod memory requests 150 GiB. Headroom 0.1.

1. Normal: 4 x (64 - 6) x 0.9 = 208.8 GiB. Lose one worker: 3 x 58 x 0.9 = 156.6 GiB. Lose zone A: 2 x 58 x 0.9 = 104.4 GiB.

```text
$ just capacity examples/k8s-workers.json               (exit 1)
  normal       effective 208.8  demand 150  deficit 0
  lose-w1      effective 156.6  demand 150  deficit 0
  lose-zone-a  effective 104.4  demand 150  deficit 45.6
```

2. Control plane: three etcd members, two in zone A, one in zone B (input `etcd.json`, same shape as `examples/quorum.json`):

```text
$ just quorum examples/etcd-2-zones.json                    (exit 1)
  any single member lost --> 2 of 3, quorate
  domain:zone-a lost --> 1 of 3: "cluster loses quorum (2 of 3 votes needed)"
$ just quorum examples/etcd-3-zones.json                 (one member per zone A, B, C)
  every member and every zone lost --> 2 of 3, quorate   status pass (exit 0)
```

3. Decision: put etcd in three zones. Either accept that zone-A loss sheds 45.6 GiB of pods, or cap requests at 104 GiB, or add workers in zone B.
4. For etcd, leave out the `qdevice` key: QDevice rules are Proxmox-specific. Only the majority arithmetic carries over.

## Review checklist

- [ ] Runtime choice justified against the table; Kubernetes only for a demonstrated need.
- [ ] Images pinned by digest; registry or mirror reachable when the primary site is down.
- [ ] Compose: health-gated dependencies, restart policy tested by a VM reboot, log rotation set.
- [ ] Kubernetes: etcd odd-sized across failure domains (`just quorum`); encrypted snapshots restored in a lab.
- [ ] Node capacity covers requests after one node and one zone loss (`just capacity`).
- [ ] Replicas spread by topology constraints; PDBs set; liveness never checks a dependency.
- [ ] Database backup taken before every schema-changing upgrade; old-image restore tested.
- [ ] Break-glass, GitOps and credentials recoverable without the platform.

## Further reading

Links checked 2026-10-29.

Primary sources cited above (VERIFIED_PRIMARY, checked 2026-10-29)

- [docker-restart]: Docker restart policies. [compose-order]: Compose startup order.
- [etcd-faq]: etcd FAQ. [k8s-etcd]: Kubernetes etcd operations. [k8s-disruptions]: Kubernetes disruptions.

Docker and Podman

- [Docker restart policies](https://docs.docker.com/engine/containers/start-containers-automatically/): read this for exact restart semantics per policy.
- [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/): read this for health-gated dependencies.
- [Docker volumes](https://docs.docker.com/engine/storage/volumes/): read this for where state lives and how to back it up.
- [Docker logging drivers](https://docs.docker.com/engine/logging/configure/): read this for log rotation and shipping.
- [Docker rootless mode](https://docs.docker.com/engine/security/rootless/): read this for running the daemon without root and its limits.
- [Podman Quadlet (podman-systemd.unit)](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html): read this for systemd-managed containers on small hosts.

Kubernetes

- [Cluster architecture](https://kubernetes.io/docs/concepts/architecture/): read this for control plane, node components and their dependencies.
- [Operating etcd](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/): read this for etcd sizing, snapshot and restore.
- [Disruptions and PDBs](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/): read this for voluntary vs involuntary disruption.
- [Topology spread constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/): read this for spreading replicas across failure domains.
- [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/): read this for liveness, readiness and startup probe design.

Security and practice

- [NIST SP 800-190](https://csrc.nist.gov/pubs/sp/800/190/final): read this for container threat model and countermeasures.
- [SLSA v1.0](https://slsa.dev/spec/v1.0/): read this for build provenance levels.
- [The Twelve-Factor App](https://12factor.net/): read this for config, statelessness and disposability rules that make containers recoverable.

[docker-restart]: https://docs.docker.com/engine/containers/start-containers-automatically/ [compose-order]: https://docs.docker.com/compose/how-tos/startup-order/ [etcd-faq]:
https://etcd.io/docs/v3.5/faq/ [k8s-etcd]: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/ [k8s-disruptions]:
https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
