---
Title: Storage, filesystems and data architecture
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: Storage, filesystems and data architecture decisions, failure modes and validation.
---

# Storage, filesystems and data architecture

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Capacity vocabulary and layouts](#capacity-vocabulary-and-layouts)
- [ZFS rules](#zfs-rules)
- [Ceph rules](#ceph-rules)
- [Two sites: stretch or replicate](#two-sites-stretch-or-replicate)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Growing a VM disk](#growing-a-vm-disk)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Workload characterisation and capacity vocabulary for block, file and object storage.
- Local ZFS, replicated ZFS and Ceph: layout, failure domains, headroom.
- Databases on this storage: fsync, WAL placement, consistent snapshots.

## Decision rules

Workload first:

- Characterise access type, working set, read/write mix, random vs sequential, I/O size, sync share (fsync/O_DSYNC), latency percentiles, growth and retention.
- Throughput = IOPS x I/O size. Small sync writes are latency-bound; large sequential reads are bandwidth-bound.
- Benchmark with the real block size, sync semantics and a data set larger than every cache. Otherwise the result measures RAM.

Choosing the storage model:

| Need                                        | Choose                                  | Why                                                  |
| ------------------------------------------- | --------------------------------------- | ---------------------------------------------------- |
| One host, integrity, snapshots              | local ZFS mirror                        | checksums, cheap snapshots, simple recovery          |
| Small cluster, minutes of RPO acceptable    | local ZFS + scheduled replication       | low cost, no storage network, RPO = interval         |
| Zero RPO VM disks, live migration, 4+ nodes | Ceph RBD                                | synchronous replicas, self-healing                   |
| Shared files between hosts or users         | NFS/SMB from a dedicated NAS, or CephFS | file locking and permissions semantics               |
| Backups, artifacts, logs at scale           | object storage (S3 API)                 | cheap capacity, versioning/object lock where offered |

- Snapshots and replicas share deletion authority and logical corruption with production. They never replace an independent, tested backup.
- Encryption needs key custody and recovery. A lost key turns an intact backup into noise.

Databases:

- PostgreSQL needs fsync honoured end to end. Never disable `fsync` or put WAL on storage that lies about flushes.
- Measure commit latency with `pg_test_fsync` on the target device. Put WAL on low-latency media.
- Separate datasets for data and WAL so recordsize and snapshot policy can differ.
- A filesystem snapshot is crash-consistent only if it captures data and WAL atomically. Otherwise use the database backup API (see the backup reference).

## Capacity vocabulary and layouts

Separate raw, usable (after redundancy), provisioned (thin promises), consumed, reclaimable (snapshots, trim) and protected (backed up) capacity.

| Layout                     | Usable fraction (before metadata/padding) | Tolerates                          | Random-IOPS character                                   |
| -------------------------- | ----------------------------------------- | ---------------------------------- | ------------------------------------------------------- |
| Mirror (2-way) per vdev    | 1/2                                       | 1 disk per vdev                    | reads scale with disks; writes ~ one disk per vdev      |
| RAID-Z1 / Z2 / Z3, width w | (w-p)/w, p = 1/2/3                        | p disks per vdev                   | ~ one disk per vdev (VERIFIED_PRIMARY, PVE ZFS chapter) |
| Ceph replicated size s     | 1/s                                       | s-1 copies, if min_size allows I/O | network + OSD latency bound                             |
| Ceph EC k+m                | k/(k+m)                                   | m chunks                           | higher CPU and write latency than replicas              |

- Ceph plan limit: `usable_plan = raw / size * nearfull_ratio * (N - f) / N` for N equal failure domains, f of which may be lost and re-replicated.
- Ceph full ratios default: nearfull 0.85, backfillfull 0.90, full 0.95. At full the cluster blocks client writes. VERIFIED_PRIMARY, [mon-config], checked 2026-10-29.
- Thin provisioning needs an alert below each of those thresholds and a pre-agreed response.

## ZFS rules

Each rule VERIFIED_PRIMARY, [pve-zfs] or [openzfs-tuning], checked 2026-10-29, unless marked.

- Give ZFS raw disks through an HBA (IT mode). Never a hardware RAID controller with its own cache.
- `ashift` is per vdev and fixed at creation; 2^ashift is the smallest I/O. Use 12 (4 KiB) unless the sector is larger. Too small causes read-modify-write.
- `recordsize` defaults to 128 KiB and applies to new writes only. Match it to the application I/O; OpenZFS suggests 16 KiB for InnoDB.
- Zvols use `volblocksize`, set only at creation.
- RAID-Z with a small `volblocksize` loses space to parity and padding. A VM pool on RAID-Z can use far more space than guests see.
- Prefer mirrors for VM and random I/O. Use RAID-Z for capacity and sequential data.
- ARC: Proxmox VE 8.1+ installers cap ARC at 10% of RAM, clamped to 16 GiB. Older installs set no limit. Count the cap in host reserve.
- A SLOG helps only synchronous writes and needs power-loss protection. L2ARC helps only when the working set exceeds ARC and costs RAM for headers.
- dRAID spreads spare capacity across all disks for faster rebuild on wide pools. Its fixed stripe width wastes space on small blocks ([draid]).
- Scrub on a schedule: checksums detect corruption only on data that is read.
- Resilver time >= `allocated_bytes_on_vdev / sustained_write_rate_of_new_disk`. Busy RAID-Z pools take longer (UNVERIFIED as a multiplier; measure).

## Ceph rules

Each rule VERIFIED_PRIMARY, [pveceph] or [mon-config], checked 2026-10-29.

- At least three (preferably identical) nodes. OSD memory target 4 GiB per OSD by default. 10 Gbps+ dedicated network, more for NVMe.
- Proxmox pools default to size 3, min_size 2. Never set min_size 1: it accepts writes with a single copy and risks data loss.
- EC pools: min_size defaults to k+1 when m > 1. Ceph recommends k+2 for safety. Below min_size the pool blocks I/O.
- Monitors need a majority. Run an odd number (3 or 5) in distinct failure domains.
- CRUSH places replicas across the configured failure domain: host by default, rack or row when the map encodes them ([crush]).
- Encode the real rack and power topology in the CRUSH map.

```text
CRUSH rule: replicated, failure domain = rack, size 3, min_size 2

                        +--------------+
                        | root default |
                        +------+-------+
             +-----------------+-----------------+
             |                 |                 |
     :::: rack A ::::  :::: rack B ::::  :::: rack C ::::
       host1  host2      host3  host4      host5  host6
             |                 |                 |
        X copy 1            copy 2            copy 3      one copy of each PG per rack

  rack A lost --> 2 copies >= min_size 2 --> I/O continues, degraded
  no 4th rack --> cannot re-replicate; one more rack loss --> 1 copy < min_size --> I/O blocks

  Legend: :::: failure domain   X rack A failed   --> consequence
```

- Hyperconverged sizing: plan at least four nodes per failure domain set for size 3. Three nodes keep I/O after one loss but leave no re-replication target during a failure or maintenance; a fourth
  live node is worth more than a cold spare. Size so the surviving N-1 nodes stay below nearfull (0.85 default) after recovery. Derived from the defaults above and `just ceph`; the "four" is a design
  rule, not a Ceph requirement.
- A two-replica pool is unsafe either way: min_size 1 accepts writes on one copy, and min_size 2 blocks writes on any single node loss.
- A rack failure domain with size 3 needs at least three racks, and four to re-replicate after a rack loss (diagram above).
- Put databases on a tier sized with growth before monitoring and log stores are added; they are the usual tier overrun.

## Two sites: stretch or replicate

Decide between one cluster stretched across sites and two independent clusters with asynchronous replication.

- Stretch mode keeps OSDs in exactly two zones with two replicas each (size 4) and a tiebreaker monitor in a third site; erasure-coded pools are not allowed, and while degraded the pools run at
  min_size 1, so Ceph recommends SSD OSDs only. VERIFIED_PRIMARY, [ceph-stretch], checked 2026-10-29.
- Inter-site latency: Red Hat Ceph Storage documents about 10 ms RTT between the two data sites, with the tiebreaker tolerating more; the Ceph project blog states the same 10 ms figure and up to 100
  ms for the tiebreaker. It is a guideline, not an enforced limit. VERIFIED_PRIMARY (vendor documentation), [rhcs-stretch]; VERIFIED_SECONDARY, [ceph-stretch-blog]; checked 2026-10-29.
- Every client write waits for the remote replicas, so the inter-site RTT adds directly to write latency on every write, at both sites.
- Default for sites more than one metro apart (RTT near or above 10 ms): two independent clusters and asynchronous replication (RBD mirroring or platform replication). State RPO > 0 openly and measure
  it against each service's declared RPO.
- RBD mirroring is asynchronous: journal-based (crash-consistent, every write recorded twice, so write latency nearly doubles) or snapshot-based (deltas between scheduled mirror-snapshots; a partially
  applied delta is rolled back at failover). Each `rbd-mirror` daemon must reach every monitor and OSD of both clusters. VERIFIED_PRIMARY, [rbd-mirror], checked 2026-10-29.
- Two clusters still need an active-active or active-passive decision per service. It changes runbooks and DNS or routing, not storage.

```text
TWO SITES: measured RTT decides the shape

  RTT <= ~10 ms and SSD OSDs          RTT > ~10 ms, or HDD OSDs, or different cities
  +-----------+  sync  +-----------+  +-----------+  async   +-----------+
  | site A    |<======>| site B    |  | cluster A |--------->| cluster B |
  | 2 copies  |        | 2 copies  |  | size 3    | rbd-     | size 3    |
  +-----+-----+        +-----+-----+  +-----------+ mirror   +-----------+
        |    tiebreaker mon  |          RPO > 0, measured; each site self-heals locally
        +------> site C <----+
  one cluster, size 4, writes pay RTT     two clusters, writes pay local latency only

  Legend: <====> synchronous replica traffic   ---> asynchronous replication
```

## Patterns and anti-patterns

| Pattern                                | Use when                  | Anti-pattern                               | Why it fails                                             |
| -------------------------------------- | ------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| ZFS mirrors for VM disks               | random I/O, small blocks  | RAID-Z with small volblocksize             | parity and padding inflate space; one-disk IOPS per vdev |
| HBA in IT mode                         | any ZFS pool              | hardware RAID under ZFS                    | ZFS cannot see or repair disk errors; cache can lie      |
| size 3 / min_size 2, domain = host+    | Ceph replicated pools     | min_size 1                                 | writes land on one copy; the next failure loses data     |
| N > replica count failure domains      | self-healing Ceph         | exactly 3 nodes with size 3                | stays degraded until the node returns                    |
| Plan to nearfull after one domain loss | Ceph capacity             | fill to raw / size                         | recovery hits backfillfull or full and blocks writes     |
| Database backup API or atomic snapshot | databases                 | file copy of a live data directory         | restores a torn, inconsistent database                   |
| PLP SSD for SLOG and WAL               | sync-heavy workloads      | consumer SSD without power-loss protection | high sync latency; acknowledged writes lost on power cut |
| Two clusters plus async replication    | sites in different metros | one cluster stretched over ~12-14 ms RTT   | every write pays the RTT; outside the ~10 ms guideline   |

> **Learned 2026-11-21** · single-node SeaweedFS capacity · VERIFIED_PRIMARY (observed) · Source: continuum-app `compose.yaml` (SeaweedFS 4.54, 8b25b18), SeaweedFS log "failed to find
> writable volumes ... Not enough data nodes found" · Falsifier: a full single-node SeaweedFS that refuses S3 puts at once with an error.
> A single-node `weed server` holds at most `-volume.max` x `-master.volumeSizeLimitMB` (8 x 64 MB = 512 MB here). When full, S3 puts did not fail fast: restic and the
> client waited until their own timeouts, so the symptom was "every upload hangs", not "disk full". Size the store for the largest test run, watch the volume count, and look in
> the SeaweedFS log first when uploads stall.
>
> ```yaml
> command: ["server", "-dir=/data", "-master.volumeSizeLimitMB=64", "-volume.max=64", "-s3"]   # 64 x 64 MB = 4 GB (was 8 = 512 MB, filled)
> ```

## Failure modes and tests

| Failure                          | Symptom                                       | Blast radius                 | Proving test                                                           |
| -------------------------------- | --------------------------------------------- | ---------------------------- | ---------------------------------------------------------------------- |
| Wrong vdev layout or no spare    | degraded pool, slow resilver                  | every dataset on the pool    | pull a disk under load; measure degraded latency and resilver time     |
| CRUSH domain is osd, not host    | PGs go inactive when one host stops           | every pool using that rule   | stop all OSDs on one host; no PG goes inactive                         |
| nearfull reached during recovery | backfill stalls; writes block at full         | whole Ceph cluster           | fill to plan limit, fail a node; recovery completes below backfillfull |
| Consumer SSD without PLP         | high commit latency, lost acknowledged writes | databases on that device     | fio sync 4k QD1 and `pg_test_fsync` on the real device                 |
| No scrub schedule                | latent corruption found only on restore       | data read rarely             | scrub and deep-scrub history and error counters in monitoring          |
| Thin pool overcommitted          | guests see I/O errors at 100%                 | all thin volumes on the pool | alert test below each threshold; agreed response rehearsed             |
| Async replica lag above the RPO  | mirror lag grows during write bursts          | services failed over to B    | measure lag under peak writes; fail over and count lost writes         |
| Benchmark averaged over phases   | pass in the PoC, slow in the rebuild window   | every service on the cluster | p95/p99 per phase: steady, node down, rebuilding, restored, backup     |

## Worked example

Four hosts, each 4 x 3.84 TB = 15.36 TB raw; one pool, size 3, min_size 2; must re-replicate after losing one host; demand 10 TB.

1. Raw = 4 x 15.36 = 61.44 TB. After one host loss = 46.08 TB.
2. Plan = 46.08 / 3 x 0.85 = 13.056 TB. Same as 61.44 / 3 x 0.85 x 3/4.

```text
$ just ceph examples/ceph-capacity.json
  vm-rbd  width 3  min_size 2  raw_tb 61.44  surviving_raw_tb 46.08  plan_tb 13.056  demand_tb 10
  status pass, findings []   (exit 0)
```

3. Now drop to three hosts, set min_size 1, and add an EC 4+2 archive pool (input saved as `pools.json`):

```text
$ just ceph examples/ceph-3-hosts-bad.json                     (exit 1)
  vm-rbd: losing 1 domain(s) leaves 2 for 3 placements; data stays degraded until the domain returns
  vm-rbd: min_size 1 is below 2; writes would be accepted with no redundancy
  vm-rbd: demand 10 TB exceeds the plan limit 8.70 TB after losing 1 domain(s)
  ec-archive: 6 placements need 6 failure domains; only 3 exist
```

4. Decision: keep four or more hosts, restore min_size 2, and hold EC 4+2 until six failure domains exist.

## Growing a VM disk

One order on every platform: read the current state, snapshot, grow the virtual disk, wait where the platform is asynchronous, then grow the partition and filesystem inside the guest. `just
disk-grow` ([disk_grow.py](../scripts/disk_grow.py) with [disk_grow_guest.sh](../scripts/disk_grow_guest.sh)) prints that plan for `aws`, `proxmox-vm`, `proxmox-ct`, `libvirt` and `qemu-img`,
runs only the reads with `--check`, and writes only with `--apply`.

| Platform | Snapshot | Grow the disk | Guest step | Evidence |
| --- | --- | --- | --- | --- |
| AWS EBS | `ec2 create-snapshot` (point in time at initiation) | `ec2 modify-volume --size N [--volume-type gp3]`, usable at `optimizing` | growpart + fs grow | VERIFIED_PRIMARY ([ebs-modify]); used 2026-11-27 and 2026-11-28 |
| Proxmox VM | `qm snapshot <vmid> <name>` (ZFS, LVM-thin, Ceph, qcow2) | `qm disk resize <vmid> <disk> <N>G` (absolute, or `+N`; no shrink) | rescan + growpart + fs grow | VERIFIED_PRIMARY ([qm], 9.3.1) |
| Proxmox CT | `pct snapshot <vmid> <name>` | `pct resize <vmid> rootfs <N>G` (no shrink) | none: pct grows the filesystem | resize VERIFIED_PRIMARY ([pct], 9.3.1); fs grow UNVERIFIED until a CT run |
| libvirt/QEMU (running) | `virsh snapshot-create-as <dom> <name> --atomic` (internal, qcow2) | `virsh blockresize <dom> <target> <N>G --extend` (`--extend` refuses a shrink) | rescan + growpart + fs grow | VERIFIED_PRIMARY ([virsh]) |
| qemu-img (stopped) | `qemu-img snapshot -c <name> <img>` | `qemu-img resize <img> <N>G` (shrink needs `--shrink`) | after the next boot | UNVERIFIED (no run yet) |

> **Learned 2026-11-28** · any VM root disk · VERIFIED_PRIMARY (two production EBS grows, online, no restart) · Source: ansible-wifi Pad TASK-71 · Falsifier: an EBS or virtio grow that needs a guest
> restart before growpart sees the new size
> Grow the root disk online, in the order snapshot, grow the virtual disk, growpart, filesystem grow. Do not wait for the EBS snapshot to finish: it is point in time at initiation. The
> modification is usable once it reaches `optimizing`, which took under 15 s for a 300 to 500 GB gp2 to gp3 change. Find the guest device from the mount's MAJ:MIN, not from `df`: an
> EC2 Ubuntu root shows as `/dev/root`. `findmnt -o MAJ:MIN` pads its value with spaces, so trim it before using it as a `/sys/dev/block` path; the first real `--check` run failed on that.
> A bigger disk only buys time when an application keeps data with no retention. In this case it was session recordings and audit logs, 241 of 263 GB. Set retention and a disk alert in
> the same change.

```bash
# scripts/disk_grow_guest.sh (skill-systems-architect, 2026-11-28): resolve the device under a mount, then pick the grow path
MAJMIN=$(findmnt -nvo MAJ:MIN "${MOUNT}" | tr -d ' ')
NAME=$(basename "$(readlink -f "/sys/dev/block/${MAJMIN}")")
TYPE=$(lsblk -dno TYPE "/dev/${NAME}")
case ${TYPE} in
  part) grow_partition "$(lsblk -dno PKNAME "/dev/${NAME}")" "$(cat "/sys/class/block/${NAME}/partition")"
        grow_fs "/dev/${NAME}" "${FSTYPE}" ;;
  lvm)  ...  # single PV only: growpart the PV partition, pvresize, lvextend -r -l +100%FREE
```

## Review checklist

- [ ] Workload measured: I/O size, sync share, working set, p99 latency target.
- [ ] Raw, usable, provisioned and protected capacity stated separately.
- [ ] ZFS: HBA in IT mode; ashift fixed deliberately; mirrors for VM pools; ARC cap counted in host reserve.
- [ ] Ceph: `just ceph` passes; min_size >= 2 (replica) or k+1 (EC); failure domains > placements.
- [ ] CRUSH map encodes the real host, rack and power topology.
- [ ] Two sites: RTT measured; stretch only within ~10 ms with SSD OSDs, otherwise two clusters with a measured RPO.
- [ ] Storage benchmarks report p95/p99 per phase (steady, node down, rebuilding, restored), not one average.
- [ ] Alerts below nearfull, backfillfull and full; thin-pool response agreed.
- [ ] Scrub schedule running and its errors alerted.
- [ ] Database backups use the database API or atomic snapshots; `pg_test_fsync` result recorded.
- [ ] Network architect has storage latency, throughput, MTU and rebuild traffic; data-loss combinations recorded.

## Further reading

Links checked 2026-10-29.

Primary sources cited above (VERIFIED_PRIMARY, checked 2026-10-29)

- [pve-zfs]: Proxmox VE ZFS chapter source. [pveceph]: Proxmox VE Ceph chapter source.
- [mon-config]: Ceph monitor config reference (full ratios, quorum). [crush]: Ceph CRUSH maps. [openzfs-tuning]: OpenZFS workload tuning.
- [ebs-modify]: AWS EBS Elastic Volumes (modify a volume). [qm], [pct]: Proxmox VE 9.3.1 man pages (disk resize, snapshot). [virsh]: libvirt blockresize and snapshot-create-as (checked 2026-11-28).

OpenZFS

- [Workload tuning](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html): read this for ashift, recordsize, compression and database-specific settings.
- [RAID-Z](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/RAIDZ.html): read this for parity, padding and why small blocks waste space on RAID-Z.
- [dRAID](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/dRAID%20Howto.html): read this for distributed spares and rebuild speed on wide pools.
- [zpoolconcepts(7)](https://openzfs.github.io/openzfs-docs/man/master/7/zpoolconcepts.7.html): read this for vdev types, special/log/cache devices and failure semantics.
- [Module parameters](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Module%20Parameters.html): read this for ARC sizing and other kernel tunables.
- [Proxmox VE host administration (ZFS)](https://pve.proxmox.com/pve-docs/chapter-sysadmin.html): read this for ZFS as deployed by Proxmox, ARC limits and disk replacement.

Ceph

- [Architecture](https://docs.ceph.com/en/latest/architecture/): read this for RADOS, CRUSH, PGs and how clients find data.
- [CRUSH maps](https://docs.ceph.com/en/latest/rados/operations/crush-map/): read this for encoding racks/rows and writing failure-domain rules.
- [Pools](https://docs.ceph.com/en/latest/rados/operations/pools/): read this for size, min_size and pool flags.
- [Erasure code](https://docs.ceph.com/en/latest/rados/operations/erasure-code/): read this for k+m profiles and their trade-offs.
- [Placement groups](https://docs.ceph.com/en/latest/rados/operations/placement-groups/): read this for PG counts and the autoscaler.
- [Hardware recommendations](https://docs.ceph.com/en/latest/start/hardware-recommendations/): read this for CPU, RAM, media and network sizing.
- [ceph-stretch]: stretch mode, its limits and the tiebreaker monitor. [rbd-mirror]: journal and snapshot RBD mirroring between clusters.
- [rhcs-stretch]: Red Hat Ceph Storage stretch clusters, including the inter-site latency guideline.
- [ceph-stretch-blog]: Ceph project blog on stretch clusters (10 ms data sites, 100 ms tiebreaker).

Measurement and security

- [fio documentation](https://fio.readthedocs.io/en/latest/fio_doc.html): read this for building benchmarks with the right block size, queue depth and sync mode.
- [NIST SP 800-209 storage security](https://csrc.nist.gov/pubs/sp/800/209/final): read this for storage infrastructure security controls including backup isolation.

[pve-zfs]: https://raw.githubusercontent.com/proxmox/pve-docs/master/local-zfs.adoc
[pveceph]: https://raw.githubusercontent.com/proxmox/pve-docs/master/pveceph.adoc
[mon-config]: https://docs.ceph.com/en/latest/rados/configuration/mon-config-ref/
[crush]: https://docs.ceph.com/en/latest/rados/operations/crush-map/
[ebs-modify]: https://docs.aws.amazon.com/ebs/latest/userguide/ebs-modify-volume.html
[qm]: https://pve.proxmox.com/pve-docs/qm.1.html
[pct]: https://pve.proxmox.com/pve-docs/pct.1.html
[virsh]: https://www.libvirt.org/manpages/virsh.html
[openzfs-tuning]: https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html
[draid]: https://openzfs.github.io/openzfs-docs/Basic%20Concepts/dRAID%20Howto.html
[ceph-stretch]: https://docs.ceph.com/en/latest/rados/operations/stretch-mode/
[rbd-mirror]: https://docs.ceph.com/en/latest/rbd/rbd-mirroring/
[rhcs-stretch]: https://docs.redhat.com/en/documentation/red_hat_ceph_storage/9/html/administration_guide/stretch-clusters-for-ceph-storage
[ceph-stretch-blog]: https://ceph.io/en/news/blog/2025/stretch-cluuuuuuuuusters-part1/

> **Learned 2026-11-22** · compress and deduplicate before you encrypt on the client · VERIFIED_PRIMARY (continuum measurements) · Source: continuum TD-250, continuum-app f8d2870,
> 7c27a49 · Falsifier: a backup tool that deduplicates client-encrypted data.
> Once data is encrypted on the device, the backup tool (restic) can neither compress nor deduplicate it: every upload is stored full-size. Compress on the device first
> (zstd level 3: a 171 MiB workspace tar to 78 MiB in 0.2 s; a 213 MiB move 19.7 -> 16 s) and skip unchanged objects by their plaintext digest (reuse the stored ciphertext's
> address). Readers should recognise compressed data by its frame magic so older objects still read, and cap decompression size. Retention must keep every object a
> manifest still names. Each restic invocation also costs a repository open (about 0.7 s on a dev S3): remember facts that stay true (repository exists, snapshot ids).


> **Learned 2026-11-24** · TerraMaster F4-424 Pro (Intel i3-N305), Proxmox VE 9.2 · VERIFIED_PRIMARY for the hardware limits (TerraMaster spec page, Intel ARK), design
> otherwise · Source: home NAS project `docs/research/hardware-gpu-research-20261124_2300.md`, `docs/research/doc-review-20261124_2300.md`, doc 07 · Falsifier: a spec
> sheet showing PCIe 3.0 x2 or x4 M.2 on this model
> Small N305 NAS boxes size the design: both M.2 slots are PCIe 3.0 x1 (about 1 GB/s), so a second NVMe is worth more as the boot-pool mirror than as a fast pool or special
> vdev; no Thunderbolt/USB4, no PCIe slot or OCuLink, so an external GPU is not practical and the iGPU's media engine (QuickSync) carries transcoding; one SO-DIMM slot with a
> 32 GB vendor maximum caps guest plus ARC planning. Put app databases, thumbnails and ML caches on NVMe and bulk originals on HDD mirror pairs that grow a pair at a time.
> Off-site backup must be named before a cloud photo service is cancelled. No visual surface.

> **Learned 2026-11-25** · SMART gate on disks that hold nothing yet · USER_STATED (operator decision DL-040) with VERIFIED_PRIMARY test results · Source: home NAS
> project DL-040, `docs/references/06-storage-provisioning-and-host-validation.md` record · Falsifier: a case where a disk failing only the extended test
> costs more than rebuilding an empty pool
> The extended SMART test on a 12 TB drive takes about 17 hours. When the disks hold nothing yet, waiting for it buys only early detection of a bad drive,
> which on an empty pool costs a resilver or a rebuild, not data. A sound shortcut: overall health PASSED, zero reallocated, pending and uncorrectable
> sectors, a passed short test as the latest result, then build the pool and rerun the extended tests on the empty pool, with a written rule that no
> data is copied until they pass and an alert when they finish. Heavy writes during a test can abort it; a reboot resets it.
