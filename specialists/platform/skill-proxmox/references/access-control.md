# Access control

Users, realms, groups, roles, privileges, ACLs, pools and API tokens, and the least-privilege pattern for automation. Sources: [pveum
chapter](../documents/research-sources-20261107/pve-admin-chapter-pveum.md), [pveum(1)](../documents/research-sources-20261107/pve-pveum-man1.md), [bpg provider
index](../documents/research-sources-20261107/bpg-provider-index.md), [installed download-url
check](../documents/research-sources-20261107/pve-9.1.5-installed-storage-download-url-permissions.txt).

## Contents

- [Model](#model)
- [API tokens and privilege separation](#api-tokens-and-privilege-separation)
- [Privileges that matter](#privileges-that-matter)
- [Least-privilege pattern for automation](#least-privilege-pattern-for-automation)
- [Worked example: an OpenTofu identity](#worked-example-an-opentofu-identity)
- [Audit](#audit)

## Model

- **Realms**: `pam` (Linux users; `root@pam` is the unconfined superuser and cannot be deleted), `pve` (Proxmox VE authentication server, passwords in pmxcfs), plus LDAP, Active Directory and OpenID
  Connect; configured in `/etc/pve/domains.cfg`. A user id is `name@realm`. `VERIFIED_PRIMARY` (pveum chapter, Users and Authentication Realms).
- **Roles** are named privilege sets. Built-ins include `Administrator` (everything), `NoAccess`, `PVEAdmin`, `PVEVMAdmin`, `PVEAuditor`, `PVESDNAdmin`; custom roles via `pveum role add`.
  `VERIFIED_PRIMARY`.
- **ACLs** bind a role to a user, group or token on a path: `/`, `/nodes/{node}`, `/vms/{vmid}`, `/storage/{storeid}`, `/pool/{pool}`, `/sdn/zones/{zone}[/{vnet}]`, `/access/...`, `/mapping/...`.
  Propagation is on by default. Rules: user grants replace group grants; deeper paths replace inherited grants; `NoAccess` cancels other roles on a path. `VERIFIED_PRIMARY` (Objects and Paths,
  Inheritance).
- **Pools** group VMs, containers and storages so one ACL on `/pool/<pool>` covers every member. `VERIFIED_PRIMARY` (Pools).
- Effective rights on a path: `pveum user permissions <user@realm> --path <path>`. `VERIFIED_PRIMARY` (pveum(1)).

## API tokens and privilege separation

- Token id is `user@realm!tokenid`; the secret (a UUID) is shown **once**, at creation. HTTP header: `Authorization: PVEAPIToken=user@realm!tokenid=<secret>`; a token needs no CSRF token.
  `VERIFIED_PRIMARY` ([API wiki](../documents/research-sources-20261107/pve-wiki-api.md)).
- Two kinds: **separated privileges** (the default: the token needs its own ACLs and its effective rights are the **intersection** of the user's and the token's) and **full privileges** (`--privsep
  0`: identical to the user). "Privilege separated tokens can never have permissions on any given path that their associated user does not have." `VERIFIED_PRIMARY` (pveum chapter).
- So a privilege-separated token needs the ACL **twice**: once for the user (the ceiling) and once for the token. Granting only the token gives it nothing. `VERIFIED_PRIMARY` (follows from the
  intersection rule; the audit flags it as `token-acl-without-user`).
- Set `--expire <epoch>` so abandoned automation stops; default is the user's expiry (none). `VERIFIED_PRIMARY` (pveum(1)).
- A token user needs no password: create it with `pveum user add name@pve` and no `--password`, so it cannot log in to the GUI. `VERIFIED_SECONDARY` (follows from the pve realm; observed in the lab).
- Some operations are root-only even for an Administrator token (container bind mounts, privileged-container features, `arch`, device passthrough without a mapping). `VERIFIED_SECONDARY` (bpg provider
  index).

## Privileges that matter

| Need                              | Privileges                                                                                                                    | Where                            |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Create and configure VMs          | `VM.Allocate`, `VM.Audit`, `VM.Config.*` (CDROM, CPU, Cloudinit, Disk, HWType, Memory, Network, Options),                     | `/pool/<pool>`                   |
|                                   |   `VM.PowerMgmt`, `VM.Console`                                                                                                |                                  |
| Read guest agent info (addresses) | `VM.GuestAgent.Audit` (not `Unrestricted`, which runs arbitrary agent commands)                                               | `/pool/<pool>`                   |
| Put disks on a storage            | `Datastore.AllocateSpace`, `Datastore.Audit`                                                                                  | `/storage/<id>`                  |
| Attach NICs to bridges or VNets   | `SDN.Use`                                                                                                                     | `/sdn/zones/localnetwork` or     |
|                                   |                                                                                                                               |   a zone                         |
| See the pool                      | `Pool.Audit`                                                                                                                  | `/pool/<pool>`                   |
| Read node status (provider needs) | `Sys.Audit`                                                                                                                   | `/nodes`                         |
| Download a URL to a storage       | `Datastore.AllocateTemplate` + (`Sys.Audit`, `Sys.Modify` on `/`) or `Sys.AccessNetwork` on the node                          | storage and node                 |
| Dangerous: avoid for automation   | `Sys.Modify`, `Permissions.Modify`, `User.Modify`, `Realm.*`, `Sys.Console`, `VM.GuestAgent.Unrestricted`                     | —                                |

Privilege names `VERIFIED_PRIMARY` (pveum privilege list); the download row from the installed 9.1.5 source. The pveum chapter warns that `Permissions.Modify` and `Sys.Modify` "should be handled with
care".

Since 9.0 `VM.Monitor` is gone (QEMU monitor access needs `Sys.Audit`, agent commands the `VM.GuestAgent.*` privileges) and
replication needs `VM.Replicate`: custom roles written for 8.x need review after the upgrade. `VERIFIED_PRIMARY` (Roadmap, 9.0
breaking changes).

## Least-privilege pattern for automation

1. One **pool** per automation scope; the automation only touches guests in it.
2. One **custom role** with exactly the VM, datastore, pool and `SDN.Use` privileges above, and a second **read role** with `Sys.Audit`.
3. One **user** in the `pve` realm with no password.
4. One **privilege-separated token** (`--privsep 1`, with `--expire` when the work has an end).
5. ACLs to **both** the user and the token: the role on `/pool/<pool>`, each `/storage/<id>` it writes, `/sdn/zones/localnetwork` for plain bridges and `/sdn/zones/<zone>`
   for each SDN zone its guests join; the read role on `/nodes`.
6. The secret goes straight from `token add` into a password manager in the same command and is never printed or written to disk.
7. Split by capability when several tools share a node: a read-only audit role (`VM.Audit`, `Datastore.Audit`, `Sys.Audit`,
   `Pool.Audit`, `SDN.Audit`) for pollers, a lifecycle role for provisioning, a console role, a backup role, each on its own token.
   `VERIFIED_SECONDARY` (a vendor's published minimal-token guide,
   [captured](../documents/research-sources-20261107/community-proxploy-minimal-privilege-token.md)); it fits the intersection rule above.
8. Anything that needs a wider right (downloading images, `Sys.Modify`, root-only features) runs as a separate, reviewed root step, not through the token.

## Worked example: an OpenTofu identity

smc-resiliency's x86 lab (`spike/x86/pve_lab_setup.sh`, uncommitted on 2026-11-07, re-read after its zone ACL was added; host and password-manager paths removed) applies the pattern; plan by
default, writes only with `--apply`, every step
skips what exists:

```bash
VM_PRIVS="VM.Allocate,VM.Audit,VM.Config.CDROM,VM.Config.CPU,VM.Config.Cloudinit,VM.Config.Disk,VM.Config.HWType,VM.Config.Memory"
VM_PRIVS+=",VM.Config.Network,VM.Config.Options,VM.Console,VM.PowerMgmt,VM.GuestAgent.Audit,Datastore.AllocateSpace,Datastore.Audit"
VM_PRIVS+=",Pool.Audit,SDN.Use"
step "role SmcX86Tofu (${VM_PRIVS})" \
  "pveum role list --output-format json | grep -q '\"roleid\":\"SmcX86Tofu\"' && pveum role modify SmcX86Tofu --privs '${VM_PRIVS}' || pveum role add SmcX86Tofu --privs '${VM_PRIVS}'"
step "role SmcX86Read (Sys.Audit)" "... || pveum role add SmcX86Read --privs Sys.Audit"
step "user ${USER_ID} (no password: token only)" "... || pveum user add ${USER_ID} --comment '...'"
secret=$(on_pve "pveum user token add ${USER_ID} tofu --privsep 1 --comment '...' --output-format json" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["value"])')    # straight into the password manager, read back by length
for path in /pool/smc-x86 /storage/local /storage/local-lvm /sdn/zones/localnetwork /sdn/zones/dhcp; do
  step "ACL ${path}" "pveum acl modify ${path} --roles SmcX86Tofu --users ${USER_ID} --tokens '${TOKEN_ID}'"
done
step "ACL /nodes" "pveum acl modify /nodes --roles SmcX86Read --users ${USER_ID} --tokens '${TOKEN_ID}'"
```

The root step also adds `import` to `local` and downloads the pinned cloud image with a SHA256 check into `local:import/`, so the token never needs `Sys.Modify` or `Sys.AccessNetwork`
([storage.md](storage.md#the-import-content-type)).

> **Learned 2026-11-07 (e)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: lab node read-only (`pvesh get /access/acl`, `/access/users --full 1`, task log of VM 901) and
> `spike/x86/pve_lab_setup.sh` in smc-resiliency (uncommitted on 2026-11-07) · Falsifier: a 9.x node where this role set cannot create, resize and start a VM in the pool
> The role above (17 privileges) on `/pool/<pool>`, two storages and `/sdn/zones/localnetwork`, plus `Sys.Audit` on `/nodes`, granted to both a password-less `pve` user and its `--privsep 1` token,
> was enough for the bpg provider to create a q35/OVMF VM with an EFI disk, an imported qcow2 system disk, a cloud-init drive and a NIC on `vmbr0`, resize the disk and start it: the node's task log
> shows `qmcreate`, `resize` and `qmstart` by that token.

<!-- next write-back entry -->

> **Learned 2026-11-07 (f)** · Proxmox VE 9.1.5 (libpve-storage-perl 9.1.0) · VERIFIED_PRIMARY · Source: installed `PVE/API2/Storage/Status.pm` download_url permissions (captured in
> documents/research-sources-20261107) · Falsifier: a 9.1 node that refuses download-url to a token holding Datastore.AllocateTemplate on the storage and Sys.AccessNetwork on the node
> `download-url` (the provider's `download_file`) accepts `Sys.AccessNetwork` on `/nodes/{node}` as an alternative to `Sys.Audit` + `Sys.Modify` on `/`; the bpg docs and the pveum privilege list do
> not mention it yet. It still lets the caller make the node fetch any URL, so the pattern keeps downloads in a root step.

## Audit

`just token_audit --host <node>` (read-only) flags: tokens with `privsep=0`; grants on `/` whose role holds a dangerous privilege (except `root@pam`); dangerous privileges on a token anywhere; token
ACLs with no matching user ACL; tokens that never expire. Exit 1 on any high finding ([scripts/README.md](../scripts/README.md)).

> **Learned 2026-11-07 (g)** · Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: `pve_token_audit.py --host` against the lab node, 2026-11-07 · Falsifier: none needed for the observation; the generic
> rule is the pveum intersection rule
> On the lab node two older automation identities (an MCP server user and a first OpenTofu user) each had `PVEAdmin` on `/` and a token with `privsep=0`: four high findings beside the clean
> pool-scoped identity. A token made for a quick start tends to stay; audit before adding a new one.

> **Learned 2026-11-07** · PVE 9.2.26 · VERIFIED_PRIMARY · Source: smc-resiliency `lab/infra/proxmox/pve_lab_setup.sh` (per-VMID ACL loop), node task log
> `qmcreate:902 ... 403 Permission check failed (/vms/902, VM.Config.Options)` · Falsifier: a privilege-separated token with the role only on
> `/pool/<pool>` creating a VM with `pool_id` on 9.2
> A pool ACL does not cover a VM while it is being created: the create checks `/vms/<vmid>` before the VM joins the pool (9.1.5 created VM 901
> with the pool ACL alone; after the upgrade to 9.2.26 VM 902 failed). Grant the role on `/vms/<id>` for each ID in the lab's range
> (`pveum acl modify /vms/900 ... /vms/909 --roles <role> --users <user> --tokens '<user>!<token>'`), which keeps the token to that range.
