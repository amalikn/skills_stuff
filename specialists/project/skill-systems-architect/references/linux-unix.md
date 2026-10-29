---
Title: Linux, Unix and OS architecture
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: Linux, Unix and OS architecture decisions, lifecycle tracking, patch rings, logging, time and failure modes, with verified Debian/Ubuntu support dates.
---

# Linux, Unix and OS architecture

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Lifecycle and EOL dates](#lifecycle-and-eol-dates)
- [Patch rings](#patch-rings)
- [Boot, trust and recovery chain](#boot-trust-and-recovery-chain)
- [Time, logging, hardening and performance](#time-logging-hardening-and-performance)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Linux, BSD and other Unix hosts: lifecycle, patching, boot trust, time, logging, hardening and performance diagnosis.
- Record per host class: distribution and point release, kernel (GA or HWE/backport), boot mode (UEFI/BIOS, Secure Boot state), package sources and pins.
- Also record: init/service manager, filesystem and encryption, hardware/firmware versions, workload owner and support lifecycle.
- BSD/Unix variants: never reuse Linux commands or assumptions without checking that platform.

## Decision rules

| Decision                     | Rule and threshold                                                                                        | Evidence                              |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| Major upgrade timing         | Finish the next major upgrade before end of regular security support, not the last date                   | Design rule; dates [D1][U1]           |
| Debian 11 hosts              | Free LTS ended 2026-08-31. Each remaining host is a finding: upgrade, isolate, or paid ELTS with an owner | VERIFIED_PRIMARY [D1]                 |
| Debian 12 hosts              | On LTS now. Finish bookworm -> trixie before 2028-06-30; start with slow-access edge hosts                | VERIFIED_PRIMARY [D1][D2]             |
| Debian LTS coverage          | A separate team, not Debian Security; reduced architecture and package set. Check each host               | VERIFIED_PRIMARY [D2]                 |
| Ubuntu past standard support | ESM needs Ubuntu Pro. Record the entitlement as USER_STATED until verified                                | VERIFIED_PRIMARY [U1]                 |
| Automatic security updates   | Keep unattended-upgrades on the security origin. Automatic reboot stays off unless set                    | VERIFIED_PRIMARY [D3]                 |
| Pending reboot               | Alert when a pending reboot is older than one ring cycle                                                  | Design rule (UNVERIFIED as universal) |
| Time service                 | Use chrony or ntpd to serve time, run full NTP or use NTS. systemd-timesyncd is SNTP only                 | VERIFIED_PRIMARY [S2]                 |
| Time sources                 | Three or more upstream sources for an internal tier. Allow a bounded `makestep` only at boot              | Design rule                           |
| Journal size                 | Defaults: `SystemMaxUse` 10%, `SystemKeepFree` 15%, each capped at 4G. Set explicit caps on small disks   | VERIFIED_PRIMARY [S1]                 |
| Remote reboot                | Unattended only when unlock, network and the access path return with no one on site                       | Design rule                           |
| Lifecycle claims             | Store the date and the check date beside every claim; re-check at each review                             | Design rule                           |
| Host model: mutable          | apt + config management: small fleets, stateful services, slow-link edge. Cost: drift, rebuild drills     | Design rule                           |
| Host model: immutable        | Rebuild to change: stateless roles, CI runners, container hosts. Needs image pipeline, state separation   | Design rule                           |
| Host model: appliance        | Vendor-managed OS for single-purpose devices. Vendor lifecycle and patch speed become your risk           | Design rule                           |

## Lifecycle and EOL dates

Track three dates per release: end of regular security support, end of LTS/ESM, end of any paid extension.

| Release                     | Regular security / standard support ends                  | LTS / ESM ends                           | Evidence                            |
| --------------------------- | --------------------------------------------------------- | ---------------------------------------- | ----------------------------------- |
| Debian 13 trixie            | 2028-08-09                                                | LTS 2030-06-30; paid ELTS 2035-06-30     | VERIFIED_PRIMARY [D1]               |
| (released 2025-08-09)       |                                                           |                                          |                                     |
| Debian 12 bookworm          | 2026-07-11 (EOL column); LTS took over 2026-06-11 per the | LTS 2028-06-30; ELTS 2033-06-30          | VERIFIED_PRIMARY [D1][D2]           |
|                             | LTS wiki                                                  |                                          |                                     |
| Debian 11 bullseye          | ended 2024-08-14                                          | LTS ended 2026-08-31; ELTS to 2031-06-30 | VERIFIED_PRIMARY [D1]               |
| Ubuntu 26.04 LTS (Apr 2026) | May 2031                                                  | May 2036 (Ubuntu Pro)                    | VERIFIED_PRIMARY [U1]               |
| Ubuntu 24.04 LTS (Apr 2024) | May 2029                                                  | Ubuntu Pro (check page)                  | VERIFIED_PRIMARY [U1]               |
| Ubuntu 22.04 LTS            | May 2027                                                  | May 2032 (Ubuntu Pro)                    | VERIFIED_SECONDARY (Canonical table |
|                             |                                                           |                                          | not extractable)                    |
| Ubuntu 20.04 LTS            | ended May 2025                                            | ESM to May 2030                          | VERIFIED_SECONDARY                  |

## Patch rings

| Ring                       | Scope              | Start   | Method                        | Gate before the next ring                               |
| -------------------------- | ------------------ | ------- | ----------------------------- | ------------------------------------------------------- |
| 0 lab / canary             | 1-2 hosts per role | day 0   | Auto-apply; watch 24-72 h     | Services healthy, reboot OK, no new alerts              |
| 1 early prod               | ~10%, mixed sites  | day 2-3 | Auto or batch apply           | Error rates and journal errors flat; rollback rehearsed |
| 2 broad prod               | Remainder          | day 5-7 | Batched, bounded concurrency  | Remote access confirmed per site before each wave       |
| 3 critical / hard to reach | Named hosts        | Window  | Manual, console path verified | Service check per host                                  |

- Ring sizes and soak times are a starting design (UNVERIFIED as universal values). Size them from failure-domain and rollback evidence.
- Upstream Debian config allows the `Debian-Security` origin and the stable point-release origin (`label=Debian`) (VERIFIED_PRIMARY [D3], checked 2026-10-29).
- Automatic reboot needs `Unattended-Upgrade::Automatic-Reboot "true"` [D3]. Read the packaged `/etc/apt/apt.conf.d/50unattended-upgrades` per release; Ubuntu ships its own origins.
- Kernel, libc, openssl and systemd updates need a restart. Track `/var/run/reboot-required` (Debian/Ubuntu) and `needrestart`; reboot per ring.
- Keep the previous kernel selectable. Verify console or out-of-band access before a remote kernel or bootloader change.
- Run a major upgrade (Debian N -> N+1, Ubuntu LTS -> LTS) as a migration: backup or snapshot, release notes, canary per role, tested rollback.

## Boot, trust and recovery chain

```text
Boot trust chain: every stage must pass unattended before a remote reboot is safe

+----------+     +--------+     +------+     +------------------+     +---------+     +----------+
| UEFI     | --> | shim   | --> | GRUB | --> | kernel +         | --> | systemd | --> | services |
| firmware |     | MS-sig |     |      |     | initramfs (LUKS) |     |         |     |          |
+----------+     +--------+     +------+     +------------------+     +---------+     +----------+
     |               |                                |                    |
     X firmware      X unsigned DKMS, ZFS             X no unlock: TPM,    X identity, DNS,
       update stuck:   or NIC module refused:           passphrase or        time or mount
       needs console   sign it or enrol a MOK           network unlock       missing

Legend: --> next boot stage   X failure at that stage and its remedy
```

- Disk encryption needs a recovery path without the normal identity stack: escrowed LUKS recovery key, documented unlock method, console route.
- Out-of-tree modules (DKMS, ZFS, vendor NIC drivers) fail under Secure Boot unless signed. Test on a canary before fleet rollout.

## Time, logging, hardening and performance

- Time is a dependency of TLS, Kerberos, SSH/X.509 certificate validity, TOTP, log correlation and backups. Monitor offset, not "service running".
- journald `Storage=auto` persists only if `/var/log/journal` exists (VERIFIED_PRIMARY [S1], checked 2026-10-29).
- Upstream systemd 262 documents `persistent` as the compile-time default; distribution builds and older versions differ [S1].
- Verify with `systemd-analyze cat-config systemd/journald.conf`. Set `MaxRetentionSec` only with a documented reason.
- Local journals are not an audit store. Ship logs off-host (journald remote, rsyslog, Vector/Fluent Bit, OTel collector) with buffering, in UTC.
- Isolate with namespaces/cgroups, capabilities, and AppArmor (Debian/Ubuntu default) or SELinux.
- Sandbox units with `ProtectSystem=`, `PrivateTmp=`, `NoNewPrivileges=`, `CapabilityBoundingSet=`. Score them with `systemd-analyze security`.
- Use signed repositories, pinned critical packages and reproducible images. Read exact-version manuals before writing sysctl, systemd or storage config.
- Separate kernel, driver, firmware, user-space and application changes in change records; compatibility fails across these boundaries.
- Diagnose down the stack: workload -> process -> scheduler/memory -> filesystem/block -> driver -> hardware. Apply USE per resource; read PSI (`/proc/pressure/*`).
- Separate CPU saturation, lock contention, memory pressure/reclaim, swap, I/O queueing and external dependency latency.

## Patterns and anti-patterns

| Pattern                          | Use when                     | Anti-pattern                                | Why it fails                                           |
| -------------------------------- | ---------------------------- | ------------------------------------------- | ------------------------------------------------------ |
| Patch rings with gates           | More than a handful of hosts | Patch every host from one cron job          | One bad package stops every role at once               |
| Previous kernel kept selectable  | Kernel or bootloader change  | Purge old kernels on install                | No local fallback when a remote host fails to boot     |
| Off-host logs in UTC             | Any audit or incident need   | Local journal as the audit store            | Lost with the disk, editable by root, skewed by clocks |
| Tailored CIS or STIG baseline    | Hardening a role             | Paste a baseline unchanged                  | Breaks services; deviations go undocumented            |
| Sandboxed, scored systemd units  | Long-running services        | Run services as root with all capabilities  | One compromise owns the host                           |
| USE plus PSI per resource        | Performance diagnosis        | Read load average or "free" memory alone    | Hides which resource saturates                         |
| Major upgrade run as a migration | Debian N -> N+1, LTS -> LTS  | In-place upgrade with no snapshot or backup | No rollback when a package or driver breaks            |

## Failure modes and tests

| Failure                           | Symptom                                            | Blast radius                    | Proving test                                                          |
| --------------------------------- | -------------------------------------------------- | ------------------------------- | --------------------------------------------------------------------- |
| Release past security support     | No new advisories for its packages                 | Every service on the host       | EOL register row compared with [D1]/[U1]                              |
| Reboots pile up                   | Fix installed, old kernel or library still running | Fleet-wide exposure window      | Count hosts whose reboot flag is older than one ring cycle            |
| Unsigned module under Secure Boot | ZFS or NIC driver missing after kernel update      | Storage or network on that host | Canary kernel update with Secure Boot on; confirm the module loads    |
| LUKS unlock needs a person        | Remote host waits at a passphrase prompt           | Whole host until a site visit   | Scheduled remote reboot of a canary; time to service ready            |
| Clock drift                       | TLS or Kerberos failures, out-of-order logs        | Every client of that host       | Alert on chrony offset; inject a step change in the lab               |
| Volatile or oversized journal     | Logs lost on reboot, or disk full                  | Host and its services           | `/var/log/journal` exists; caps shown by `systemd-analyze cat-config` |
| Configuration drift               | Second converge run reports changes                | Role-wide inconsistency         | Run configuration management twice; the second run changes nothing    |
| Interrupted package update        | dpkg lock, half-configured packages                | Patching stops on that host     | Kill an upgrade in the lab; recover with `dpkg --configure -a`        |
| Host lost or disk full            | Service down or crashing                           | Roles on the host               | Fill a lab disk; then replace a host from source of truth and restore |

## Worked example

Edge fleet: 60 Debian 12 hosts, 16 GiB root filesystem, one maintenance window per site per month.

1. Journal defaults: `SystemMaxUse` 10% = 1.6 GiB; `SystemKeepFree` 15% = 2.4 GiB; neither reaches the 4G cap [S1]. Set `SystemMaxUse=512M` and ship logs off-host.
2. Runway: 2026-10-29 to the Debian 12 LTS end (2028-06-30) is 20 months [D1].
3. Capacity: at 8 hosts per window, 60 hosts need 8 windows (7.5 rounded up), about 8 months.
4. Add 1 month of canary and 2 spare windows: about 11 months, finishing around 2027-09, 9 months before LTS ends.
5. Steps 3-4 use illustrative figures; replace them with measured upgrade time per host and real window counts.

## Review checklist

- [ ] Every host class has release, kernel, boot mode, Secure Boot state and owner recorded.
- [ ] Every release has three lifecycle dates with source and check date; no host is unsupported without an owner and a dated decision.
- [ ] Patch rings, gates and the pending-reboot alert exist; the previous kernel stays selectable.
- [ ] Remote reboot is proven: unlock, network and access return without a person on site.
- [ ] Time uses three or more sources and offset is alerted; journal persistence and caps are verified; logs leave the host in UTC.
- [ ] Baseline deviations are recorded; units are sandboxed and scored.
- [ ] Idempotence, interrupted update, disk full, restore and host replacement are tested.

## Further reading

Evidence IDs used above are tagged in brackets. Decision rules stay in this file; read these for depth.

Lifecycle and support:
- [D1] [Debian releases index](https://www.debian.org/releases/) - read this for EOL, LTS and ELTS dates per release (VERIFIED_PRIMARY, checked 2026-10-29).
- [D2] [Debian LTS wiki](https://wiki.debian.org/LTS) - read this for LTS architecture coverage and the team boundary (VERIFIED_PRIMARY, checked 2026-10-29).
- [U1] [Ubuntu release cycle](https://ubuntu.com/about/release-cycle) - read this for standard support vs Ubuntu Pro ESM dates (VERIFIED_PRIMARY, checked 2026-10-29).
- [Debian 13 release notes](https://www.debian.org/releases/trixie/releasenotes) - read this before any bookworm -> trixie upgrade (pointer).

Patching:
- [D3] [unattended-upgrades Debian config][d3url] - read this for origin patterns and reboot options (VERIFIED_PRIMARY, checked 2026-10-29).
- [Debian wiki: PeriodicUpdates](https://wiki.debian.org/PeriodicUpdates) - read this for enabling and debugging unattended upgrades (pointer).

systemd, time and logs:
- [S1] [journald.conf(5)][s1url] - read this for Storage=, size caps and retention (VERIFIED_PRIMARY, systemd 262, checked 2026-10-29).
- [S2] [systemd-timesyncd.service(8)][s2url] - read this for the SNTP-only limit (VERIFIED_PRIMARY, checked 2026-10-29).
- [systemd.exec(5)](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html) - read this for unit sandboxing directives (pointer).
- [chrony FAQ](https://chrony-project.org/faq.html) - read this for makestep, NTS and client/server design (pointer).

Kernel and hardening:
- [Linux kernel admin guide](https://docs.kernel.org/admin-guide/index.html) - read this for sysctl, cgroups and boot parameters (VERIFIED_PRIMARY, checked 2026-10-29).
- [Kernel PSI documentation](https://docs.kernel.org/accounting/psi.html) - read this for pressure-stall metrics (pointer).
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) - read this for a hardening baseline to tailor, not paste (pointer).

[d3url]: https://github.com/mvo5/unattended-upgrades/blob/master/data/50unattended-upgrades.Debian

[s1url]: https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html

[s2url]: https://www.freedesktop.org/software/systemd/man/latest/systemd-timesyncd.service.html
