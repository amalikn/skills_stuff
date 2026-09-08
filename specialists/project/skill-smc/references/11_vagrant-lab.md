# SMC Vagrant Lab

## Contents
- Overview
- Network topology
- Key Vagrant nuances and known issues
- Bring-up procedure
- Useful commands

## 12. Vagrant Lab — family-friendly-vsmc01

### 12.1 Overview

Vagrantfile: `/Volumes/Data/_vagrant/vagrant_stuff/family-friendly-vsmc01/Vagrantfile`

Three VMs defined; only two are typically used:

| VM | Box | RAM/CPU | Role |
|---|---|---|---|
| `family-friendly-vsmc01` | `bento/ubuntu-22.04` | 2GB / 1 | SMC under test |
| `cf-test-client` | `cloudicio/ubuntu-desktop 24.04.1` | 8GB / 4 | Ubuntu Desktop client on VLAN 501 |
| `cf-test-client-02` | `stromweld/windows-11` | — | Windows 11 client (inactive/optional) |

### 12.2 Network topology

**vsmc01 adapter map** (bento/ubuntu-22.04 keeps `ethN` naming in VirtualBox):

| VirtualBox Adapter | Guest Interface | intnet / type | Purpose |
|---|---|---|---|
| adapter 1 (nat1) | `eth0` | NAT (172.29.10.0/24) | Vagrant management + internet access |
| adapter 2 | `eth1` | public\_network (bridged en0) | WAN1 — Mac Wi-Fi |
| adapter 3 | `eth2` | public\_network (no auto\_config) | WAN2 — Mac Wi-Fi (second) |
| adapter 4 | `eth3` | intnet `switch01_unused` (promisc) | Switch01 placeholder — promisc only |
| adapter 5 | `eth4` | intnet `smc01_lan` (promisc) | LAN segment shared with client |

**cf-test-client adapter map** (Ubuntu Desktop 24.04 uses predictable names — NOT `ethN`):

| VirtualBox Adapter | Guest Interface | intnet / type | Purpose |
|---|---|---|---|
| adapter 1 (default NAT) | `enp0s8` | NAT | Vagrant SSH; suppressed as default route |
| adapter 2 | `enp0s9` | intnet `smc01_lan` DHCP | LAN — gets IP from SMC DHCP on VLAN 501 |

> **Critical naming distinction**: The vsmc01 SMC uses `eth0–eth4` (VirtualBox bento box keeps legacy naming). The cf-test-client uses `enp0s8/enp0s9` (Ubuntu Desktop 24.04 predictable names). Scripts or provisioners that assume `eth0/eth1` on the client will silently fail.

### 12.3 Key Vagrant nuances and known issues

**1 — NAT default route suppression on cf-test-client**

Problem: VirtualBox gives `enp0s8` (NAT) a default gateway with low metric (~100), which wins over the SMC gateway on `enp0s9` (metric ~20101). Traffic bypasses the captive portal.

Fix (in Vagrantfile, `run: always`): Writes a netplan override that persists across DHCP renewals and reboots:
```
/etc/netplan/99-no-default-via-enp0s8.yaml:
  network.version: 2
  ethernets.enp0s8.dhcp4: true
  ethernets.enp0s8.dhcp4-overrides.use-routes: false
```
Then `netplan apply && ip route del default dev enp0s8 || true`.

Verify routing is correct:
```bash
# On cf-test-client — should show ONLY SMC default route
ip route show default
# Expected: default via 10.0.0.1 dev enp0s9 proto dhcp metric 20100  (only one line)
```

**2 — VirtualBox orphaned VM cleanup**

If a previous `vagrant up` failed mid-provision, the VM directory may exist on disk but not be registered in VirtualBox. `vagrant up` will fail with `VERR_ALREADY_EXISTS`.

Fix:
```bash
VBoxManage registervm ~/VirtualBox\ VMs/cf-test-client/cf-test-client.vbox
VBoxManage unregistervm "cf-test-client" --delete
```
Never `rm -rf` the VM directory — leaves orphaned disk records in VirtualBox internal media registry causing future conflicts.

**3 — VirtualBox Guest Additions compile failure on Apple Silicon**

`vboxguest` kernel module compile fails with `#error "Not on AMD64 or x86"` on ARM64 Mac. This is expected and **ignorable** — Guest Additions only affect shared folders, clipboard, and display. cf-test-client has `synced_folder disabled: true`; no shared folders are needed.

**4 — vsmc Ansible networkd race condition (eth1 bounce → SSH drop)**

**Symptom**: `smc_network` handler `Reload systemd-networkd service` fires, then Ansible reports `UNREACHABLE` (SSH timeout on Teleport port 65535). Play ends: `ok=91 changed=64 unreachable=1`.

**Root cause chain**:
1. networkd reload → networkd-dispatcher fires `configured.d/00-interface-activation.sh`
2. Script unconditionally bounces eth1: `ip link set eth1 down; ip link set eth1 up`
3. eth1 bounce → dhclient@eth1 gets `ENETDOWN` → tries to renew stale lease (172.20.10.2 = old iPhone hotspot IP, wrong network)
4. `timeout 10` in `/etc/dhcp/dhclient.eth1.conf` too short for WiFi bridge DHCP → no DHCPACK → lease expires
5. Default route via eth1 disappears
6. Teleport tunnel cannot reach `teleport.apn.au` (no internet route) → SSH banner exchange times out
7. Ansible marks UNREACHABLE before `wait_for_connection` can recover

**Fix**: `roles/smc_network/templates/00-interface-activation.sh.j2` — Vagrant guard added:
- When `smc_bases_vagrant_interface` is defined: skip eth1 bounce entirely; only bring interface up if it is currently down (no down/up cycle).
- `smc_bases_vagrant_interface: eth0` set in `host_vars/family-friendly-vsmc01.yml`.

**Physical SMC not affected**: Wired DHCP is fast; interface reaches `routable` within the timeout; loop stops naturally.

**Ansible provisioning on vsmc01**: Ansible is not run by Vagrant directly. After `vagrant up family-friendly-vsmc01`, run from the Mac:
```bash
cd /Volumes/Data/_ansible/ansible-wifi
ansible-playbook smc_bases.yml -l family-friendly-vsmc01 --diff
```
Key vars: `smc_bases_vagrant_interface` set in host_vars → activates all Vagrant guards (eth1 bounce skip, dirmngr IPv6 disable).

**5 — unbound on first Ansible run**

`interface-automatic: no` is required in `unbound.conf.j2` (fixed 2026-06-26). Without it, unbound tries to bind `::1` as a companion to `0.0.0.0` even with `do-ip6: no`, which fails fatally when IPv6 is disabled by sysctl. Second run succeeds (socket state changes). The template fix makes the first run reliable.

**6 — PHP PPA on Vagrant**

dirmngr defaults to AAAA lookup for apt.releases.phpunit.de. On IPv6-disabled Vagrant VMs, this causes `No route to host`. Fix: `disable-ipv6` in `/etc/gnupg/dirmngr.conf`, applied by `ubuntu-php-install-configure.yml` when `smc_bases_vagrant_interface` is defined.

### 12.4 Bring-up procedure

```bash
# 1. Start SMC VM
cd /Volumes/Data/_vagrant/vagrant_stuff/family-friendly-vsmc01
vagrant up family-friendly-vsmc01

# 2. Provision SMC with Ansible (from ansible-wifi repo root)
ansible-playbook smc_bases.yml -l family-friendly-vsmc01 --diff

# 3. Start client VM
vagrant up cf-test-client

# 4. Verify client routing (only one default route via SMC)
vagrant ssh cf-test-client -- ip route show default

# 5. Test portal from client
vagrant ssh cf-test-client -- curl -s wifi.a8me.au | grep -E "btn-apn|Terms|Start"

# 6. Test captive redirect from client
vagrant ssh cf-test-client -- curl -sv http://1.1.1.1/ 2>&1 | grep -E "Location|302"
```

### 12.5 Useful commands

```bash
# SSH to vsmc01 directly
vagrant ssh family-friendly-vsmc01

# SSH to cf-test-client
vagrant ssh cf-test-client

# Check cf-test-client has correct default route
vagrant ssh cf-test-client -- ip route

# Portal smoke test from SMC itself
vagrant ssh family-friendly-vsmc01 -- curl -s wifi.a8me.au | grep -E "Terms|Undefined|btn-apn"

# Check iptables VLAN 501 rules on SMC
vagrant ssh family-friendly-vsmc01 -- iptables -t mangle -S ECLIPSE_MARK
vagrant ssh family-friendly-vsmc01 -- iptables -S FORWARD | grep 501

# Check DHCP leases (what IP did the client get?)
vagrant ssh family-friendly-vsmc01 -- cat /var/lib/dhcp/dhcpd.leases | grep -A5 "binding state active"
```

---
