---
Title: Security, certificates and firewall
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/security-certificates-firewall.md
Last reviewed: 2026-11-19
Summary: Node certificates and ACME, the PVE firewall and its nftables backend, and a hardening checklist.
---

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

> **Learned 2026-11-25** · Proxmox VE 9.2.2 · VERIFIED_PRIMARY (installed /usr/share/perl5/PVE/CLI/pvenode.pm lines 98-164 and PVE/API2/ACMEAccount.pm
> `tos_url`; `pvesh usage /cluster/acme/account --verbose`) · Source: home NAS project, scripts/host/pve_acme_account.sh at 6f2602f · Falsifier: a
> `pvenode acme account register` that takes the ToS agreement as an option, or a pvesh create that still prompts
> `pvenode acme account register` cannot run unattended: without `--directory` it offers a menu, and it always asks "Do you agree to the above terms?" through
> PVE::PTY::read_line, which needs a tty. The API takes agreement as a parameter: `--tos_url` ("setting this indicates agreement"). Run as root on the node,
> pvesh acts as root@pam, the only identity allowed to register (a root token is refused). The meta call gives the current ToS URL. A GUI-registered
> account may carry no contact address (`pvesh get /cluster/acme/account/<name>` shows `account` with createdAt, key, status only).
> ```bash
> tos="$(pvesh get /cluster/acme/meta --directory "$DIR" --output-format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["termsOfService"])')"
> [ -e /etc/pve/priv/acme/"$NAME" ] || pvesh create /cluster/acme/account --name "$NAME" --contact "$MAIL" --directory "$DIR" --tos_url "$tos"
> ```

> **Learned 2026-11-25 (b)** · Proxmox VE 9.2.2 on Debian 13, OpenSSH 10.0p2 · VERIFIED_PRIMARY (node /etc/ssh/sshd_config line 12 `Include`, line 33
> `PermitRootLogin yes`; sshd_config(5) "the first obtained value will be used"; `sshd -T` after the change) · Source: home NAS project,
> scripts/host/pve_sshd.sh at 83daf35 · Falsifier: a PVE install whose sshd_config sets PermitRootLogin before the Include line
> The installer leaves root SSH open to passwords (`PermitRootLogin yes` in the main file). Because Debian's Include of sshd_config.d comes first and sshd
> keeps the first value, a drop-in overrides it without editing the packaged file (no conffile prompt on upgrade). Guard the lockout: refuse when root
> has no key (on PVE /root/.ssh/authorized_keys is a symlink into /etc/pve/priv), validate with `sshd -t` and roll back, reload (open sessions stay),
> and check `sshd -T`, which prints `without-password` for prohibit-password. The web UI login (PAM realm via pveproxy) and its Shell are unaffected.
> ```bash
> grep -qE '^(ssh-|ecdsa-|sk-)' /root/.ssh/authorized_keys || exit 1
> printf 'PermitRootLogin prohibit-password\n' >/etc/ssh/sshd_config.d/10-root-keys.conf
> sshd -t || { rm -f /etc/ssh/sshd_config.d/10-root-keys.conf; exit 1; }
> systemctl reload ssh.service; sshd -T | grep -qx 'permitrootlogin without-password'
> ```

> **Learned 2026-11-25 (c)** · PVE 9.2.2 · VERIFIED_PRIMARY (pveproxy(8) read on the node; `pve-firewall localnet`; `iptables -S PVEFW-HOST-IN`; `ip -6 -br
> addr` after the change) · Source: home NAS project, scripts/host/pve_pveproxy.sh, pve_ipv6.sh, tofu/host/firewall.tf at 38688f6 · Falsifier: a PVE
> release whose pveproxy ignores /etc/default/pveproxy ACLs, or whose services fail with IPv6 off by sysctl
> Three host-exposure layers that worked together on a single node: (1) /etc/default/pveproxy `ALLOW_FROM="127.0.0.1,::1,<lan>/24,fe80::/10"`,
> `DENY_FROM="all"`, `POLICY="allow"` (both-match allows, deny-only refuses), restart, check loopback 200 and roll back if not; (2) the datacenter
> firewall with input DROP and explicit LAN ACCEPT for 8006, 22 and Ping (pve-firewall also allows 8006/22 from the detected local network; guest NICs
> with firewall=0 are untouched, so it can be enabled while guests serve); (3) IPv6 off by sysctl, not `ipv6.disable=1`: all and default
> `disable_ipv6=1`, then `lo` back to 0, which keeps `[::]` listeners (pveproxy, sshd) and postfix/chrony on `::1`. Containers keep IPv6 (namespaces
> reset IPv6 conf; `net.core.devconf_inherit_init_net=0`).
> ```text
> /etc/sysctl.d/90-nas-ipv6-off.conf: net.ipv6.conf.all.disable_ipv6 = 1 / net.ipv6.conf.default.disable_ipv6 = 1 / net.ipv6.conf.lo.disable_ipv6 = 0
> ```
