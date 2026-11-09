---
Title: Operations cookbook
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/operations-cookbook.md
Last reviewed: 2026-11-07
Summary: Exact, verified syntax for common tasks: orienting on a node, pvesh API calls, users and tokens, storage, VMs, containers and updates, each marked read or write.
---

# Operations cookbook

Verified against: Proxmox VE 9.1.5 (lab node, read-only, 2026-11-07) and the current 9.x documentation fetched 2026-11-07.

Exact syntax for the tasks that come up most. Every command here is a read unless marked **write**; a write needs the engaging project's authorization and a plan printed first. Sources are verbatim
captures in [documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [1. Orient on a node](#1-orient-on-a-node)
- [2. The API through pvesh](#2-the-api-through-pvesh)
- [3. Users, roles, ACLs and tokens](#3-users-roles-acls-and-tokens)
- [4. Storage](#4-storage)
- [5. VMs](#5-vms)
- [6. Containers](#6-containers)
- [7. Updates](#7-updates)
- [8. Summary table](#8-summary-table)

## 1. Orient on a node

```bash
pveversion -v | head -5                                 # PVE, kernel and key package versions
pvesh get /nodes/localhost/version --output-format json # {"release":"9.1","version":"9.1.5",...}
pvecm status 2>/dev/null || echo "not clustered"        # quorum and votes
pvesm status                                            # every storage: type, active, used
qm list; pct list                                       # guests on this node
```

`localhost` in an API path resolves to the node the command runs on (observed on 9.1.5, 2026-11-07). `just node_report --host <node>` does all of this and more in one SSH round trip
([scripts/README.md](../scripts/README.md)).

## 2. The API through pvesh

`pvesh` calls the REST API locally as root, without a ticket: `pvesh get|create|set|delete <api_path>`, `--output-format json|json-pretty|text|yaml` `VERIFIED_PRIMARY`
([pvesh(1)](../documents/research-sources-20261107/pve-pvesh-man1.md)). Only `get` is a
read: `create`, `set` and `delete` are POST, PUT and DELETE. Remote HTTP use is in [api-and-cli.md](api-and-cli.md).

```bash
pvesh get /cluster/resources --output-format json      # every guest, storage and node, with pool membership
pvesh get /nodes/localhost/storage --output-format json
pvesh get /access/users --full 1 --output-format json  # users with their tokens (privsep, expire)
pvesh get /access/acl --output-format json             # path, roleid, type user|group|token, ugid, propagate
pvesh get /access/roles --output-format json           # privs as a comma-separated string, built-in roles included
pvesh get /nodes/localhost/apt/update --output-format json        # pending updates from the cached lists (GET: no refresh)
pvesh get /nodes/localhost/apt/repositories --output-format json  # files, format (list|sources), Enabled, Suites
```

## 3. Users, roles, ACLs and tokens

Syntax `VERIFIED_PRIMARY` from the [pveum chapter](../documents/research-sources-20261107/pve-admin-chapter-pveum.md) and [pveum(1)](../documents/research-sources-20261107/pve-pveum-man1.md); the
pattern itself is in [access-control.md](access-control.md).

```bash
pveum role list; pveum user list; pveum acl list; pveum pool list            # reads
pveum user permissions <user@realm> --path /pool/<pool>                      # effective privileges on a path (read)
pveum pool add <pool> --comment "..."                                        # write
pveum role add <Role> --privs "VM.Allocate,VM.Audit,..."                     # write; `role modify` to change
pveum user add <name>@pve --comment "..."                                    # write; no --password: token-only identity
pveum user token add <name>@pve <tokenid> --privsep 1 --output-format json   # write; prints the secret ONCE
pveum acl modify /pool/<pool> --roles <Role> --users <name>@pve --tokens '<name>@pve!<tokenid>'   # write
```

The token secret appears only in the `token add` output: capture it into a password manager in the same pipeline and never echo it ([worked
example](access-control.md#worked-example-an-opentofu-identity)).

## 4. Storage

```bash
pvesm status; pvesm list <storage> --content import               # reads
pvesh get /storage --output-format json                           # storage.cfg as JSON
pvesm set <storage> --content images,rootdir,iso,vztmpl,backup,snippets,import   # write: the FULL list replaces the old one
```

`--content` replaces the list; name every type you keep. Content types and directory layout: [storage.md](storage.md).

## 5. VMs

```bash
qm config <vmid>; qm status <vmid>; qm pending <vmid>                            # reads
qm set <vmid> --efidisk0 <storage>:1,format=qcow2,efitype=4m,pre-enrolled-keys=0  # write
qm set <vmid> --scsi0 <storage>:0,import-from=<storage>:import/<file>.qcow2       # write: import a disk image
qm set <vmid> --serial0 socket --vga serial0                                      # write: serial console
qm set <vmid> --boot order=scsi0;net0                                             # write
qm terminal <vmid>                                                                # attach to serial0
qm guest cmd <vmid> network-get-interfaces                                       # read, needs the guest agent
qm template <vmid>; qm clone <template> <newid> --name <n> [--full]               # writes
```

Syntax `VERIFIED_PRIMARY` from the [qm chapter](../documents/research-sources-20261107/pve-admin-chapter-qm.html). Firmware and boot behaviour: [qemu-vms.md](qemu-vms.md).

## 6. Containers

```bash
pct list; pct config <ctid>                                                       # reads
pveam update; pveam available --section system; pveam list <storage>             # template index (update refreshes it: a write)
pct create <ctid> <storage>:vztmpl/<template> --unprivileged 1 --hostname <h>     # write
pct enter <ctid>                                                                  # shell inside
```

## 7. Updates

```bash
pvesh get /nodes/localhost/apt/update --output-format json   # cached list; does NOT refresh
systemctl show pve-daily-update.service -p ExecMainExitTimestamp -p Result   # when the list was last refreshed
apt update && apt full-upgrade                               # write; never `apt upgrade` (upgrade-and-troubleshooting.md)
```

## 8. Summary table

| Task                    | Read                                        | Write (authorized only)                             |
| ----------------------- | ------------------------------------------- | --------------------------------------------------- |
| Version                 | `pveversion -v`, `GET /version`             | —                                                   |
| Who can do what         | `pveum user permissions`, `GET /access/acl` | `pveum acl modify`                                  |
| Pending updates         | `GET /nodes/{node}/apt/update`              | `apt update && apt full-upgrade`                    |
| Storage content types   | `GET /storage`                              | `pvesm set <id> --content <full list>`              |
| VM firmware and boot    | `qm config`                                 | `qm set --efidisk0 ... --boot order=...`            |
| Disk from a cloud image | `pvesm list <id> --content import`          | `qm set --scsi0 <st>:0,import-from=<st>:import/<f>` |
| Least-privilege audit   | `just token_audit --host <node>`            | —                                                   |
