# Upgrade and troubleshooting

Upgrade order for the three moving parts (Parallels Desktop, Vagrant, vagrant-parallels) and a triage table for the failures a lab meets. Captures named `[file]` are in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Before an upgrade](#before-an-upgrade)
- [Upgrade order](#upgrade-order)
- [Triage table](#triage-table)
- [A wedged guest](#a-wedged-guest)

## Before an upgrade

1. Record versions: `vagrant --version`, `vagrant plugin list`, `prlctl --version`, and the pinned box versions (`just inventory-lab`).
2. Finish or snapshot running stages; a Parallels update can stop or suspend running VMs.
3. Read the release notes of each part for the versions in between: vagrant-parallels has tied fixes to Parallels releases (2.4.4 for Parallels 20.2 shared folders, 2.4.3 for Enterprise licences;
   [vp-changelog-github.md]).
4. Keep the pinned box locally before anything else, while the registry still serves it ([boxes-and-pinning.md](boxes-and-pinning.md#the-box-registry)).

## Upgrade order

Parallels Desktop first (it carries the CLI and Tools), then `vagrant plugin update vagrant-parallels`, then Vagrant itself; if plugins fail to load after a Vagrant upgrade, `vagrant plugin repair` is
the command for it (UNVERIFIED: not in the captured docs); the order is a recommendation, UNVERIFIED as a vendor statement. Then: `vagrant up` one machine, check Tools state, shared folders and
`prlctl exec`, and only then the rest. Parallels Tools in existing guests stay at their old version until updated (`update_guest_tools` or the Parallels menu); `outdated` Tools kept working for exec
and shutdown in the lab (observed 2026-11-07).

## Triage table

| Symptom                                                            | Likely cause                                    | Check                                        | Source                         |
| ------------------------------------------------------------------ | ----------------------------------------------- | -------------------------------------------- | ------------------------------ |
| "Vagrant has detected that you have an edition of Parallels        | Standard edition, or Enterprise with            | `prlsrvctl info --license --json` (edition   | [vp-issue-485.md]              |
|   Desktop for Mac installed that is not supported"                 |   vagrant-parallels before 2.4.3                |   only), `vagrant plugin list`               |                                |
| Two VMs, one IP; `vagrant ssh` reaches the wrong VM                | same `/etc/machine-id` (box regression or       | `cat /etc/machine-id` on                     | [vp-issue-441.md],             |
|                                                                    |   a clone)                                      |   both; `prlctl list -a -f`                  |   [vp-issue-1562.md]           |
| "Vagrant was unable to mount Parallels Desktop shared folders      | Parallels 20.2 moved to `prl_fsd`; plugin       | `vagrant plugin list`; Tools state           | [vp-issue-483.md]              |
|   ... prl_fs"                                                      |   before 2.4.4                                  |                                              |                                |
| Shared folder fails on an Ubuntu 26.04 guest | AppArmor blocks `prl_fsd`/`fusermount3` | `journalctl -k -g apparmor` in the guest | [vp-issue-522.md] |
| Static private IP lands on a new interface (Fedora 36+)            | Vagrant's network configuration for that guest  | `ip addr` in the guest                       | [vp-issue-462.md]              |
| Error with more than four networks on Apple silicon                | Parallels limit on M-series (reported)          | count `vm.network` lines                     | [vp-issue-410.md]              |
| `prlctl exec`: "Unable to open new session", "PrlJob_GetResult:    | Tools not running yet after a reset or reboot   | retry with a deadline; `prlctl capture`      | USER_STATED, lab 2026-11-07    |
|   Invalid argument"                                                |                                                 |                                              |                                |
| `prlctl exec` hangs                                                | guest wedged (panic, emergency shell,           | `prlctl capture <vm> --file x.png`           | USER_STATED, lab 2026-11-07    |
|                                                                    |   full disk)                                    |                                              |                                |
| `timeout: invalid time interval`                                   | a wrapper wrote `timeout 30"cmd"` (one word)    | the wrapper's quoting                        | USER_STATED, lab 2026-11-07    |
| `vagrant global-status` lists a machine that is gone               | it reads a cache                                | `vagrant global-status --prune`              | [vagrant-cli-global-status.md] |
| A linked clone stopped working after `vagrant box remove`/`prune`  | the clone's disk depends on the box image       | `vagrant box list`; restore the box from a   | [vp-configuration.md]          |
|                                                                    |                                                 |   repackaged file                            |                                |
| A second disk appears on every boot                                | a `customize` adding a device                   | `vagrantfile_lint.py`                        | [vp-configuration.md]          |
|                                                                    |   without `post-import`                         |                                              |                                |
| `vagrant up` waits with "Host unreachable. Retrying..." after a macOS upgrade (Sequoia 15.5) | macOS Local Network privacy denies the terminal app access to the VM network | System Settings, Privacy & Security, Local Network: allow the terminal and editor | [vp-issue-510.md] (reporter's fix, VERIFIED_SECONDARY) |
| Files missing or stale after `vagrant upload` of a folder          | upload into an existing directory               | upload to a fresh path per run               | USER_STATED,                   |
|                                                                    |                                                 |                                              |   smc-resiliency 2026-11-06    |

## A wedged guest

1. `prlctl capture <vm> --file <png>` and look at it: that decides everything else.
2. A login prompt: the guest is up; Tools or the network are not. Wait and retry `prlctl exec <vm> true` with a deadline; check `prlctl list -i` for `GuestTools.state`.
3. A panic, emergency or initramfs shell, a GRUB prompt: the boot itself failed. Record the capture; then `prlctl reset <vm>` (a write) or roll back a snapshot; for a lab under test, the capture is
   the result.
4. A blank console: `prlctl status <vm>`; a suspended VM resumes with `prlctl start`, `prlctl stop --drop-state` discards the state.
