# API and CLIs

The REST API is the one interface; the GUI, `pvesh`, `pveum`, `qm`, `pct` and `pvesm` all sit on it. Sources: [API wiki](../documents/research-sources-20261107/pve-wiki-api.md),
[pvesh(1)](../documents/research-sources-20261107/pve-pvesh-man1.md), [pveum(1)](../documents/research-sources-20261107/pve-pveum-man1.md).

## Contents

- [REST API](#rest-api)
- [Authentication](#authentication)
- [CLIs](#clis)
- [Safe readers and writers](#safe-readers-and-writers)

## REST API

- HTTPS on port 8006, base URL `https://<node>:8006/api2/json/`. Any node in a cluster answers for every node (calls are proxied). `VERIFIED_PRIMARY` (API wiki) for the URL; the proxying is
  `VERIFIED_PRIMARY` from `proxyto => 'node'` in the installed source ([excerpt](../documents/research-sources-20261107/pve-9.1.5-installed-storage-download-url-permissions.txt)).
- GET reads, POST creates, PUT changes, DELETE removes. Long operations return a task id (`UPID:...`); poll `/nodes/{node}/tasks/{upid}/status` until `status` is `stopped` and check `exitstatus` is
  `OK`. `VERIFIED_PRIMARY` for UPID tasks (the API viewer documents them); polling shape observed on 9.1.5.
- The schema is browsable in the API viewer on any node (`/pve-docs/api-viewer/`) and locally with `pvesh usage <path> --verbose`, which also prints the required permissions. `VERIFIED_PRIMARY`
  (pvesh(1); `pvesh usage` observed on 9.1.5).

## Authentication

- **Ticket**: `POST /access/ticket` with username and password returns a ticket cookie (`PVEAuthCookie`, valid two hours) and a `CSRFPreventionToken` that every write must send. `VERIFIED_PRIMARY`
  (API wiki).
- **API token**: header `Authorization: PVEAPIToken=user@realm!tokenid=<secret>`; no CSRF token needed. Preferred for automation ([access-control.md](access-control.md)). `VERIFIED_PRIMARY` (API
  wiki).
- TLS: the node's certificate is self-signed by the cluster CA unless replaced ([security-certificates-firewall.md](security-certificates-firewall.md)); clients either trust that CA, pin the
  fingerprint, or (lab only) skip verification.

## CLIs

| Tool         | Covers                                                                             | Note                                                    |
| ------------ | ---------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `pvesh`      | Any API path: `get`, `create`, `set`, `delete`, `ls`, `usage`                      | Runs as root locally, no ticket; `--output-format json` |
| `pveum`      | Users, groups, roles, ACLs, tokens, pools, realms, TFA                             | `user permissions` shows effective rights               |
| `qm`         | VMs: create, set, start, stop, clone, template, disk import, guest agent, terminal | `qm help <cmd>` per subcommand                          |
| `pct`        | Containers                                                                         | `pct enter`, `pct exec`                                 |
| `pvesm`      | Storage: status, list, set, alloc, free, export/import                             | `--content` replaces the list                           |
| `pvecm`      | Cluster: create, add, status, expected                                             |                                                         |
| `vzdump`     | Backups                                                                            | [backup-and-restore.md](backup-and-restore.md)          |
| `ha-manager` | HA resources and rules                                                             | [ha-and-replication.md](ha-and-replication.md)          |
| `pvenode`    | Node: certificates, ACME, wake-on-LAN, tasks                                       |                                                         |

`VERIFIED_PRIMARY` for each tool's existence and scope (admin guide chapters in the research sources).

## Safe readers and writers

- A reader uses GET only (`pvesh get`, `qm config`, `pct config`, `pvesm status`) and states which identity it reads as: a token sees only what its ACLs allow, so an empty list can mean "no rights",
  not "nothing there".
- A writer prints its plan, needs `--apply`, changes the smallest scope (a pool, a VMID range), waits for the task and checks its exit status, and reads the result back. Never treat an HTTP 200 on a
  POST as success: it means the task started.
- Batch reads per host: one SSH session running several `pvesh get` calls (the pattern in `scripts/pve_ssh.py`) is about one round trip instead of one per path.
- `pvesh` output in JSON is stable to parse; the default `text` format is for people.

> **Learned 2026-11-07 (h)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /nodes/localhost/apt/update`, `/apt/repositories`, `/cluster/resources`,
> `/nodes/localhost/tasks --vmid`) · Falsifier: a 9.x node where GET /nodes/{node}/apt/update triggers a package-list refresh
> `GET /nodes/{node}/apt/update` lists pending updates from the cached lists without refreshing them (the refresh is the POST); `GET /nodes/{node}/apt/repositories` reports each file's format (`list`
> or `sources`) and each entry's `Enabled`; `GET /cluster/resources` carries `pool` on pool members; `GET /nodes/{node}/tasks --vmid <id>` names the user and `tokenid` behind each task, which is how
> to prove what an automation token actually did.
