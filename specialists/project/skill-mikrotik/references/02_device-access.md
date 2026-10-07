---
Title: MikroTik device access
Category: reference
Status: current
Authority: local-supplement
Scope: How to reach the MikroTik switch and AP behind an SMC without exposing the password
Last reviewed: 2026-10-07
Summary: KeePass entry, Teleport port-forward through the SMC, local sshpass client, read-only guard, and why no secret may run on the SMC.
---

# MikroTik Device Access

## KeePass entry

`<secret:keepassxc:Network/mikrotik switch & metal ap>` (operator added 2026-10-07). UserName `admin`. Notes: "450Gx4 switch - 10.255.0.5", "metal ap - 10.255.0.20". The same login works on both
devices at every `rct` site surveyed so far (VERIFIED-OBSERVED 2026-10-07). Read with `kp show -a UserName` / `kp show -s -a Password` into a shell variable only; never echo it.

The entry was titled "microtik …" until the operator corrected it on 2026-10-07; scripts and docs use the corrected title.

## Path to the device

The devices have addresses on the site management VLAN (`10.255.0.0/24`, `bridge-vlan500` on the switch) and no route from outside the site. The SMC is the only way in:

1. `tsh --proxy=teleport.apn.au ssh -N -L 127.0.0.1:<port>:<device-ip>:22 root@<site>-smc01` forwards a local port through the SMC.
2. A local `ssh` to `127.0.0.1:<port>` reaches RouterOS SSH. `sshpass -e` reads the password from `SSHPASS`, never from argv.

`scripts/mikrotik_exec.sh` does both, picks a random local port, waits for it with `nc`, and tears the forward down on exit.

## Why the password never runs on the SMC

Teleport records every exec command in its audit log, and the SMC's syslog (with those audit lines) is shipped to Graylog. VERIFIED-OBSERVED (kupungarri-smc01 entries from 2026-08-28, read 2026-10-07): commands run through `tsh ssh` appear verbatim in Graylog as
teleport `[AUDIT] exec` and `Started local command execution` lines under the site's `source`. Anything typed into a command on the SMC, including an `sshpass -p` argument, ends up there. Only a TCP forward crosses the SMC.

## Read-only guard

`scripts/mikrotik_exec.sh` refuses a command unless it contains a read-only verb (`print`, `export`, `monitor … once`, `get`) or starts with `:put`/`:local`. `MT_ALLOW_WRITE=1` overrides it; use that only
with the operator's go-ahead for a specific change.

## Host keys

Not pinned (`StrictHostKeyChecking=no`, `UserKnownHostsFile=/dev/null`): the local port and the device behind it change on every run, so a pinned key would be wrong more often than right. The trust
anchor is the Teleport session to the SMC.
