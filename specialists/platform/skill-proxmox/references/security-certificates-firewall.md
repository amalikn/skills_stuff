# Security, certificates and firewall

Node certificates and ACME, the PVE firewall, and hardening basics. Sources: [Certificate Management](../documents/research-sources-20261107/pve-wiki-certificate-management.md), [firewall
chapter](../documents/research-sources-20261107/pve-admin-chapter-pve-firewall.md), [pveum chapter](../documents/research-sources-20261107/pve-admin-chapter-pveum.md).

## Contents

- [Certificates](#certificates)
- [Firewall](#firewall)
- [Hardening checklist](#hardening-checklist)

## Certificates

- Each cluster has its own CA (`/etc/pve/pve-root-ca.pem`); each node gets `/etc/pve/nodes/<node>/pve-ssl.pem` signed by it, used by `pveproxy` by default. **Do not replace or edit**
  `pve-ssl.pem`/`pve-ssl.key` or the cluster CA files. `VERIFIED_PRIMARY` (Certificate Management).
- To serve a trusted certificate, either upload a custom one (it lands in `/etc/pve/local/pveproxy-ssl.pem` and `.key`, the key without a password) or use the built-in ACME client (Let's Encrypt):
  `pvenode acme account register <name> <mail>`, a DNS or HTTP plugin (`pvenode acme plugin add dns <id> --api <provider> --data <file>`), then `pvenode acme cert order`. Renewal runs from
  `pve-daily-update.service`. `VERIFIED_PRIMARY` (Certificate Management; sysadmin chapter for renewal).
- Clients: trust the cluster CA or the public CA; skipping verification (`insecure = true` in the provider) is for a lab node only, and should be written down as such where it is set.

## Firewall

- Three levels with their own files in pmxcfs: cluster (`/etc/pve/firewall/cluster.fw`, `enable: 1` turns it on cluster-wide, default off), host (`/etc/pve/nodes/<node>/host.fw`) and guest
  (`/etc/pve/firewall/<vmid>.fw`), plus security groups, IP sets and aliases. A guest NIC is filtered only when its `firewall=1` flag is set. `VERIFIED_PRIMARY` (firewall chapter).
- "If you enable the firewall, traffic to all hosts will be blocked by default", except from the local network to the web UI (8006), SSH (22) and cluster traffic: add explicit rules for management
  networks **before** enabling. `VERIFIED_PRIMARY`.
- The newer nftables-based `proxmox-firewall` is needed for rules on forwarded traffic and on VNets. `VERIFIED_PRIMARY` (firewall chapter). Known: with the SDN firewall, DHCP to VNet guests can be
  dropped even with UDP 67/68 allowed (bugzilla 7022, open on 2026-11-07).

## Hardening checklist

- `root@pam` with TFA; everyday administration through named users in groups, not root. `VERIFIED_SECONDARY` (pveum chapter, TFA and groups).
- Automation through pool-scoped, privilege-separated tokens with an expiry ([access-control.md](access-control.md)); audit with `just token_audit`.
- No `Sys.Modify`, `Permissions.Modify` or `Sys.Console` for automation; `VM.GuestAgent.Unrestricted` and `VM.GuestAgent.FileWrite` only where a workflow needs them (they run commands or write files
  inside guests).
- Management interface (8006, 22) on a management network only; firewall rules for it in `cluster.fw`.
- Secrets (token values, PBS encryption keys, ACME plugin credentials) in a password manager; never in repositories, state files or logs.
