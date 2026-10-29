---
Title: Edge appliances and remote site boxes
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Unattended Linux site boxes (Raspberry Pi class and small x86) at remote, high-latency sites: read-only A/B images, signed health-checked updates, boot-time
  config rendering, identity partitions, pull-based jobs, flash wear and honest write measurement, watchdogs, power and crash-safe telemetry.
---

# Edge appliances and remote site boxes

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Image layout and updates](#image-layout-and-updates)
- [Pull-based jobs over poor links](#pull-based-jobs-over-poor-links)
- [Flash wear and RAM placement](#flash-wear-and-ram-placement)
- [Measuring writes honestly](#measuring-writes-honestly)
- [Hangs, watchdogs and power](#hangs-watchdogs-and-power)
- [Telemetry spool and time](#telemetry-spool-and-time)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- One Linux box per site (Raspberry Pi class on SD or eMMC, or small x86 on industrial flash or SSD) that runs essential local services unattended, reached over satellite, cellular or other high-RTT,
  intermittent links, where a site visit costs days.
- Covers image layout, updates and rollback, configuration rendering, device identity, job execution, flash wear, write measurement, watchdogs, power and store-and-forward telemetry.
- Not covered: the WAN, VPN and site network (skill-network-architect), a vendor's device facts (its platform pack, for example skill-smc), and general Linux
  lifecycle ([linux-unix](linux-unix.md)) or facility power
  ([compute-and-facilities](compute-and-facilities.md)).
- The failure modes that dominate here are storage wear, power quality, silent hangs and lost sessions, not CPU.

## Decision rules

| Decision            | Rule and threshold                                                                                                 | Evidence                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------ |
| Root filesystem     | Read-only system image; the box never edits itself in place                                                        | Design rule                    |
| Rollback            | Two system slots (A/B) on the same medium; install to the idle slot; commit only after a health check              | VERIFIED_PRIMARY [RAUC] [MEN]  |
| Configuration       | One image per architecture; per-site values rendered into RAM at every boot from a signed variable set             | Design rule                    |
| Identity            | Device keys and the way home live on read-only, redundant partitions apart from any writable state                 | Design rule                    |
| Writable area       | Disposable: a corrupt data partition is reformatted and rebuilt from identity plus central records                 | Design rule                    |
| Mounts              | Every non-root mount is `nofail` (or has a repair-and-continue path) so boot always reaches the network            | VERIFIED_PRIMARY [MNT]         |
| Churn paths         | Each high-write path gets its own capped tmpfs; the sum of caps is checked against RAM                             | VERIFIED_PRIMARY [TMPFS]       |
| Daemon directories  | Anything on tmpfs that a daemon needs but does not create is declared in tmpfiles.d or the unit's `*Directory=`    | VERIFIED_PRIMARY [TMPF] [EXEC] |
| Execution           | Pull, not push: the box holds a durable job state machine; the controller never presumes success from dispatch     | Design rule                    |
| Hangs               | A hardware watchdog via `RuntimeWatchdogSec=`, proven on a spare; timeout inside the platform maximum (Pi ~15 s)   | VERIFIED_PRIMARY [WDT] [SYSC]  |
| Recovery visibility | Every automatic recovery (watchdog reboot, power cycle) emits an event                                             | Design rule                    |
| Flash writes        | Image and identity writes are postponed while supply voltage is unhealthy                                          | Design rule                    |
| Telemetry           | Atomic batches, a capped spool with counted drops, no readings before time sync, ack only after the data is stored | Design rule                    |
| Endurance           | Size from measured device bytes per day x years against rated TBW; track percent life used per month               | Arithmetic; vendor datasheet   |

## Image layout and updates

"The box never edits itself": one signed release (OS image plus application extensions plus configuration templates) is installed into the idle slot, the box boots it once, a health check commits it,
and anything else falls back. Drift disappears by construction and the running version is knowable.

```text
ONE MEDIUM, A/B LAYOUT (one SD card, eMMC or disk)

+----------+---------------+---------------+-------------+------------+-----------+-----------------------+
| boot /   | system A (ro) | system B (ro) | identity A  | identity B | rescue R  | data (rw, disposable) |
| firmware | release N     | release N+1   | (ro) site   | (ro) copy  | (factory) | leases, small logs,   |
|          | committed     | trial boot    | vars, keys  | of A       | hw bind   | job journal, spool    |
+----------+---------------+---------------+-------------+------------+-----------+-----------------------+
  boot once into B --> health check passes --> mark good (commit); check fails or no commit --> back to A
  data corrupt --> reformat, rebuild from identity + central records; all identity copies lost --> site visit
  Legend: (ro) read-only in service   (rw) writable   --> transition
```

- Tooling (VERIFIED_PRIMARY, checked 2026-10-29): RAUC installs signed bundles into redundant slots, supports A/B/C and factory-system layouts, and uses `rauc status mark-good` with a boot-attempts
  counter for confirmation and fallback; it can stream a bundle from a server that supports HTTP Range requests [RAUC]. SWUpdate supports double copy with fall-back and a single-copy rescue system
  [SWU]. Mender writes a full image to a dual redundant partition scheme and rolls back if the device reboots before the update is committed [MEN]. Eclipse hawkBit is a domain-independent back end for
  rolling out updates to edge devices [HB].
- Raspberry Pi firmware: `tryboot_a_b=1` in `autoboot.txt` makes the tryboot switch at the partition level, so a one-shot reboot boots the other slot once and a later reboot returns to the committed
  one (VERIFIED_PRIMARY [RPI-CFG], checked 2026-10-29).
- One disk with no second-disk fallback: move rollback into the image layout. A writable root edited in place cannot be its own known-good copy.
- Anti-rollback: accept only a manifest with a higher monotonic number than the last accepted; a downgrade is a new, higher-numbered manifest that carries the older release. Upgrade and rollback are
  then one path ([TUF] describes rollback attacks).
- Release governance: approve immutable releases, not packages. Each release carries hashes, a signature key ID and an SBOM; none is offered without them. Retain every release installed or committed
  anywhere plus the two before each. Plan release size and resumable download for the slowest link.
- Keep three rollback layers separate and test each: image (OS release), service or configuration transaction (local agent), and boot entry (firmware or bootloader). One does not cover the others.
- Device identity: generate each box's key pair at issuance; only the public key goes to the controller; a reset makes a new identity and the old one is revoked. Never clone a fleet-wide private key.
  A site fingerprint that changes flags a swapped or moved box.
- Firmware settings are desired state: boot order, watchdog, power-on after AC loss, Secure Boot. Report them beside the firmware version.
- Convert existing boxes at a planned visit; a remote conversion that bricks a box costs the visit anyway.

## Pull-based jobs over poor links

Push configuration management over SSH loses the session when the link drops; a terminal multiplexer keeps a shell, not the controller's TCP session. Decouple transport from execution.

```text
DURABLE JOB STATE ON THE BOX: controller reconciles, never presumes

  RECEIVED --> VERIFIED --> STAGED --> APPLYING --> VERIFYING --> COMMITTED
     |  signature, ID,         |            |             |
     |  generation checked     |            +--> timed rollback for network changes
     X  rejected               X failed     +--> REVERTED (reported after the WAN returns)
  Legend: --> state transition   X terminal failure   every state is persisted before the next step
```

- Each job has an immutable ID and a generation; delivery is at least once, so every operation is idempotent on the box.
- Replace a configuration agent on an immutable image with a fixed set of signed, typed operations (restart, diagnostics, downstream firmware, tests).
- Report stages separately: accepted, target reached, installed, service healthy. A progress bar does not prove recovery.
- After a rebuild, re-derive intent from signed central records but inspect device state before replaying any non-idempotent step.
- Essential local services (routing and NAT, DHCP, DNS, portal, filtering, local voice) keep running with the controller and WAN down; the box runs its committed release. Keep an out-of-band way back
  that does not share fate with the primary access path.
- Gate any fleet change on the real target population (hardware class, image type); never roll to one class on another class's measurements.

## Flash wear and RAM placement

- Write rate, not capacity, decides flash life. Years of life = rated TBW / (device bytes per day x 365). Small single-device industrial flash at multi-GB/day is a consumable on a few-year horizon,
  and wear can keep falling faster than the write rate after a fix.
- Audit the standard writers before buying hardware: capture spools (retention), persistent journal (`Storage=volatile` with a cap [JRN]), syslog files, log-shipper self-logs, and list or package
  refresh artefacts (clean after import).
- Per-path capped tmpfs for churn gives the largest single reduction. A measured fleet change (journal, `/tmp`, metrics textfile and agent TSDB moved to tmpfs) cut block-level writes 48-80%, leaving a
  2-4 GB/day floor from local logs (VERIFIED_PRIMARY for that fleet; re-measure on yours).
- Always cap tmpfs. Without `size=` or `nr_blocks=` the default is half of RAM [TMPFS]. With a cap, a runaway writer fails one consumer with ENOSPC instead of exhausting RAM; a cap is a ceiling, not a
  preallocation.
- Rank tmpfs mounts by what "full" costs: stale metrics < failed temp operation < metrics gap < lost logs. Size RAM buffers for the longest upstream outage, and treat any tmpfs holding the only copy
  of data as a loss window on reboot or power cut.
- tmpfiles.d creates volatile files and directories at boot [TMPF]; `RuntimeDirectory=`, `LogsDirectory=` and related settings create a unit's own directories [EXEC]. A one-time configuration task
  does not survive the next boot: in one fleet, 13 of 15 boxes were latently broken by a directory moved to tmpfs and created only at deploy time, and two lost their proxy at their first reboot. Force
  a canary reboot after every tmpfs change.
- A storage-mode change is not a cleanup: after `Storage=volatile`, remove the old persistent journal and sweep for orphaned state.
- A whole root in RAM (overlay) suits only small, mostly static boxes. Overlay copy-up is whole-file: changing one byte of a large file copies all of it to the RAM upper layer, and a RAM upper layer
  sized by default takes a large share of memory. Large state (filter databases, PBX state, leases) belongs on disk.
- On SD-booted boxes give every write class a frequency and a location: image writes only to the idle slot during a release, identity only on rare variable changes, a small `noatime` writable area
  with a long commit interval for the rest.
- Before relocating local logs, trace the log shipper's input (file tail, socket or journal) and prove the remote path is lossless end to end, including request-size limits on any proxy in front of
  the collector.

## Measuring writes honestly

| Instrument                          | What it counts                             | Blind spot                                                              |
| ----------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------- |
| fatrace (fanotify)                  | file access events on device-backed mounts | bytes; page-cache coalescing; tmpfs, proc and sysfs are not watched     |
| 5-10 minute sampling window         | steady writers                             | once-a-day bursts of hundreds of MB                                     |
| `/proc/<pid>/io` sampled per minute | bytes of processes alive at sample time    | short-lived processes; 30-42% of device bytes unattributed in one fleet |
| `/proc/diskstats`, SMART            | bytes that reached the device, wear        | which process wrote them                                                |

- fatrace marks only mounts whose source is a real device path (plus ZFS), so tmpfs never appears in its output (VERIFIED_PRIMARY [FAT] source, checked 2026-10-29). Use it for relative ranking; quote
  wear from block-layer bytes and SMART.
- Pair any window with a 24-hour large-file scan (`find / -xdev -mmin -1440 -size +4M`) and block-layer attribution.
- The denominator is device bytes; per-process sums are a floor. A consistent unattributed band across hosts is instrument loss, not a hidden writer.
- Name the accounting class (new file, replaced inode, growth, rewrite in place) before excluding a writer as "invisible".
- Confirm per drive model which SMART attribute and column (VALUE or RAW) carries life remaining, and that the series reaches the central store.

## Hangs, watchdogs and power

- Update rollback does not fix a kernel or SoC lockup; a hardware watchdog does. With `RuntimeWatchdogSec=` set, systemd programs and pings `/dev/watchdog0` (or the configured device) [SYSC]. Prove it
  on a spare: a forced hang reboots the box and a healthy box never does.
- Raspberry Pi (BCM2835 family) watchdog: a 20-bit register counted in 1/65536 s ticks, so the maximum timeout is about 15-16 s; keep the systemd timeout inside it (VERIFIED_PRIMARY [WDT], driver
  source, checked 2026-10-29). Identify each x86 model's watchdog driver separately.
- Give the single site box an independent power-cycle path as well; software health checks cannot fix a hang.
- Any automatic recovery must emit an event to monitoring. An external board that power-cycles on loss of internet hides how often the box hangs.
- On a RAM-backed root, kernel logs are lost with the power cycle. Ship kernel logs off-box or keep a small ramoops/pstore area, which logs oopses and panics to RAM that survives a restart on hardware
  that supports it [RAMOOPS].
- Undervoltage: read the latched sources. `vcgencmd get_throttled` bit 0 is "undervoltage detected" now and bit 16 "undervoltage has occurred" since boot [RPI-OS]; the kernel log counts events. An
  instantaneous gauge scraped every minute can read 0 while the kernel logs thousands a day.
- Feed Pi-class boxes from a correctly sized regulated supply and cable. Postpone image and identity writes while voltage is unhealthy.
- Solar or battery sites: dark periods that start before dawn in winter and boots at nearly the same clock time each day point to power, not the link. Size battery autonomy for the winter worst case
  and classify each outage with boot evidence before blaming connectivity.
- Run boxes in UTC; apply a per-site zone only in schedules and reports.

## Telemetry spool and time

```text
STORE AND FORWARD: bounded, counted, acknowledged after storage

  read (after time sync) --> batch: temp, fsync, rename, rising seq --> spool (cap: hours AND MB)
                                                                         |  full: drop oldest, count it
  ingest <-- send newest batch first, then backlog oldest first <--------+
    |  reject: skew above a few minutes, or dated in the future
    +--> store --> verify stored --> ack --> box deletes batch  (at least once; idempotent by device+time)
  Legend: --> data flow   <-- send order
```

- Devices without a battery-backed real-time clock boot with a wrong clock, sometimes months behind, until NTP steps it. Gate time-stamped readings, TLS and certificate checks on a confirmed sync.
- Know which filesystems are volatile: a spool on a RAM overlay is lost at every reboot.
- Deliver current state before backfill so dashboards recover first.

## Patterns and anti-patterns

| Pattern                                    | Use when                       | Anti-pattern                                   | Why it fails                                            |
| ------------------------------------------ | ------------------------------ | ---------------------------------------------- | ------------------------------------------------------- |
| Read-only A/B image with health commit     | any unattended remote box      | in-place package and config management         | drift, unknown version, no known-good copy              |
| Boot-time render from signed variables     | many sites, one image          | per-site configuration files edited on the box | site config not reproducible or revertible              |
| Identity on redundant read-only partitions | box must always get home       | keys on the writable data partition            | one corrupt partition cuts the box off                  |
| Pull with durable job state                | high-RTT or intermittent links | push over SSH from a central controller        | dropped session leaves unknown, half-applied state      |
| Capped tmpfs per churn path                | flash-backed boxes             | uncapped tmpfs or whole root in RAM            | RAM exhausted; real state lost on reboot                |
| tmpfiles.d for tmpfs directories           | daemon directories on tmpfs    | mkdir once from configuration management       | directory missing at next boot; service down            |
| Hardware watchdog plus recovery event      | single box per site            | rely on software health checks                 | kernel hangs need a site visit; hang rate stays unknown |
| Block-device bytes as the denominator      | wear analysis                  | syscall tracer counts or process sums          | wrong ranking; inflated shares; tmpfs invisible         |

## Failure modes and tests

| Failure                    | Signal                                     | Proving test                                                                  |
| -------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------- |
| Bad release                | health check fails after trial boot        | install a release that fails its check; box returns to the committed slot     |
| Bad variable set           | services fail after a config change        | push a broken set; box reverts on its own within the agreed time              |
| Data partition corrupt     | emergency mode, or box unreachable         | corrupt the data partition on a spare; box reformats, rebuilds, reports in    |
| Directory missing on tmpfs | service fails at first boot after a change | reboot a canary after every tmpfs change; all services start                  |
| tmpfs full                 | ENOSPC for one consumer                    | fill each capped mount; only its consumer fails; fill alert fires             |
| Silent hang                | all exporters stop in one scrape           | trigger a kernel hang on a spare; watchdog reboots it; recovery event arrives |
| Undervoltage mid-write     | corrupt slot or identity                   | drop supply below threshold during an install; the write is postponed         |
| Link drops mid-job         | job stuck, state unknown                   | cut the WAN during APPLYING; box finishes or reverts and reports on return    |
| Spool overflow             | drops during a long outage                 | block ingest beyond the cap; drops are counted and visible after recovery     |
| Readings with a bad clock  | samples dated months back                  | boot with NTP blocked; no readings until sync; ingest rejects skew            |

## Worked example

Choosing the next lever for a flash-backed box (illustrative datasheet values; read the real TBW from the vendor datasheet).

1. Device: 64 GB industrial card rated 30 TBW. Measured device writes 10 GB/day from `/proc/diskstats` deltas over 7 days.
2. Life = 30,000 GB / (10 GB/day x 365) = 8.2 years nominal. Percent life used per month is the leading indicator; a card that lost 12 points in three months is on a 2-year path whatever the nominal
   figure says, so trust the measured trend over the arithmetic.
3. Move journal, `/tmp`, textfile collector and agent TSDB to capped tmpfs: caps 256 MB + 256 MB + 16 MB + 128 MB = 656 MB of ceilings on an 8 GB box (8%); the sum is checked against RAM, not
   preallocated.
4. Re-measure: 3 GB/day (a 70% cut, inside the 48-80% seen in one fleet). Life = 30,000 / (3 x 365) = 27 years nominal; the residual floor is local logging, so the next lever comes from a fresh
   ranking, not from assuming the job is done.
5. Reboot a canary: every service starts with its tmpfs directories created by tmpfiles.d; each tmpfs mount reports to monitoring; fill alerts fire at about 80% on mounts that carry data.

All values are illustrative except the cited fleet range; measure on your hardware.

## Review checklist

- [ ] Release is a signed, read-only image installed to the idle slot and committed only after a health check; fallback tested on a spare.
- [ ] Anti-rollback counter, release retention and SBOM, hashes and signature required for every release.
- [ ] Identity on redundant read-only partitions; data partition disposable and rebuild tested; all non-root mounts `nofail`.
- [ ] Jobs pulled with durable state, IDs and generations; network changes have a timed local rollback; controller reconciles from reports.
- [ ] Every churn path on its own capped tmpfs; caps summed against RAM; daemon directories in tmpfiles.d; canary rebooted after each change.
- [ ] Wear quoted from block-device bytes and SMART; per-model SMART life attribute confirmed; series present centrally.
- [ ] Hardware watchdog set within the platform maximum and proven; independent power cycle; every recovery emits an event.
- [ ] Undervoltage read from latched bits or kernel counts; flash writes postponed on low voltage; supply sized; solar autonomy sized for winter.
- [ ] Telemetry spool capped by time and size with counted drops; readings gated on time sync; ack after storage.
- [ ] Kernel logs survive a hang (off-box or ramoops); boxes run in UTC.

## Further reading

Updates and images (VERIFIED_PRIMARY, checked 2026-10-29):

- [RAUC] [RAUC documentation](https://rauc.readthedocs.io/en/latest/): read this for slots, bundle signing, boot confirmation and HTTP streaming.
- [SWU] [SWUpdate documentation](https://sbabic.github.io/swupdate/overview.html): read this for double-copy and rescue-system strategies.
- [MEN] [Mender introduction](https://docs.mender.io/overview/introduction): read this for dual-partition updates and automatic rollback.
- [HB] [Eclipse hawkBit](https://eclipse.dev/hawkbit/): read this for a rollout and campaign back end for device fleets.
- [RPI-CFG] [Raspberry Pi config.txt: autoboot.txt and tryboot](https://www.raspberrypi.com/documentation/computers/config_txt.html): read this for partition-level A/B boot on Pi firmware.
- [TUF] [The Update Framework specification](https://theupdateframework.github.io/specification/latest/): read this for rollback and freeze attacks on update systems.

systemd, kernel and filesystems (VERIFIED_PRIMARY, checked 2026-10-29):

- [TMPFS] [Linux tmpfs](https://docs.kernel.org/filesystems/tmpfs.html): read this for `size=` defaults and RAM accounting.
- [TMPF] [tmpfiles.d manual](https://www.freedesktop.org/software/systemd/man/latest/tmpfiles.d.html): read this for creating volatile directories at boot.
- [EXEC] [systemd.exec manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html): read this for `RuntimeDirectory=` and `LogsDirectory=`.
- [MNT] [systemd.mount manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.mount.html): read this for `nofail` and boot ordering.
- [SYSC] [systemd-system.conf manual](https://www.freedesktop.org/software/systemd/man/latest/systemd-system.conf.html): read this for `RuntimeWatchdogSec=` and the hardware watchdog.
- [JRN] [journald.conf manual](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html): read this for `Storage=volatile` and caps.
- [RAMOOPS] [Ramoops oops/panic logger](https://docs.kernel.org/admin-guide/ramoops.html): read this for keeping crash logs across a reboot.
- [WDT] [bcm2835_wdt.c](https://github.com/torvalds/linux/blob/master/drivers/watchdog/bcm2835_wdt.c): read this for the Pi watchdog tick and maximum.

Measurement and hardware:

- [FAT] [fatrace source](https://github.com/martinpitt/fatrace/blob/master/fatrace.c): read this for which mounts it watches (VERIFIED_PRIMARY, checked 2026-10-29).
- [RPI-OS] [Raspberry Pi OS: vcgencmd get_throttled](https://www.raspberrypi.com/documentation/computers/os.html): read this for the throttling and undervoltage
  bits (VERIFIED_PRIMARY, checked 2026-10-29).
- [smartmontools](https://www.smartmontools.org/): read this for SMART attributes, `smartctl` and the drive database.
- [JEDEC JESD218 SSD endurance](https://www.jedec.org/standards-documents/docs/jesd218b01): read this for how TBW endurance ratings are defined.
