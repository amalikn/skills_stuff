# SMC Troubleshooting

## Contents

- [5. Troubleshooting Workflows](#5-troubleshooting-workflows)
- Tier 1: box unreachable
- Tier 2: service down
- Tier 3: DHCP and DNS failures
- Tier 4: WiFi AP issues
- Tier 5: VoIP / Asterisk
- Tier 6: HA / failover
- Tier 7: monitoring gaps
- Tier 8: overlayroot persistence
- Tier 9: SMP iptables ipset failure
- Tier 10: smc_application loop input failure
- Tier 11: --check does not gate command+async restart handlers
- Cross-Tier: reject vs drop, ICMP-TTL origin location, on-box tooling gotchas

## 5. Troubleshooting Workflows

### Tier 1: Box Unreachable

```
1. autossh tunnel up?
   systemctl status autossh-teleport-openssh
   journalctl -u autossh-teleport-openssh --since "1h ago"

2. Network route stable?
   Prometheus: NodeNetworkDefaultRouteInstability (4+ route changes / 60min)
   ip route show

3. Teleport node healthy?
   systemctl status teleport
   journalctl -u teleport --since "30m ago"

   From the operator side, distinguish "this one connection attempt failed" from
   "the box has fully deregistered" before assuming a transient blip:
     tsh ssh root@<host>          # a single failed attempt can be a local DNS/network hiccup
     tsh ls | grep <host>         # confirms whether the node is still in the cluster roster at all
   A node present in `tsh ls` (shows "<- Tunnel") that fails one ssh attempt is likely transient —
   retry. A node ABSENT from the full `tsh ls` roster (not just this one connection failing) means
   its Teleport agent has dropped off the cluster entirely — confirmed live 2026-07-29 on a site
   whose primary WAN interfaces were simultaneously failing DHCP (no DHCPOFFERS at all), consistent
   with the Teleport tunnel riding the same failing uplink. That's a stronger, different signal than
   a single ssh timeout and points at the box's WAN/management path generally, not just one service.

   Either way, `tsh ssh` failing does not mean the box itself is unreachable: `autossh-teleport-openssh`
   runs a second, independent raw-OpenSSH reverse tunnel entirely outside Teleport (confirmed live
   2026-09-08 against a site with a hung/unreachable Teleport agent). See
   `03_communication-flows.md` §Backdoor SSH Access for the port formula and procedure — it gets you
   a root shell to actually run steps 1-4 from inside the box instead of guessing from outside.

   On a multi-WAN site, a reconnect failure here (e.g. `ssh: connect to host ... No route to host`,
   `ssh exited with error status 255; restarting ssh` in the `autossh-teleport-openssh` unit's own log)
   can be caused by ECMP hash pinning routing the reconnect onto a currently-dead nexthop rather than
   the tunnel itself being broken — see `06_failure-modes.md` "ECMP Multipath Hashing Pins
   Fixed-Destination Traffic to a Single (Possibly Dead) Nexthop". The fix there improves the odds a
   *subsequent* reconnect attempt succeeds; it does not make an already-hung attempt recover on its own.

4. Overlayroot healthy?
   mount | grep overlay
   (lower dir must be mounted; tmpfs upper dir must have headroom)
```

### Tier 2: Service Down (systemd failed)

```
1. What failed?
   journalctl -u <service> --since "1h ago"

2. Other units also failed?
   systemctl list-units --state=failed

3. Disk full?
   df -h
   Prometheus alerts: HostOutOfDiskSpace, HostOutOfInodes, HostDiskWillFillIn24Hours

4. Config error from last Ansible run?
   Check playbook run output in Jenkins / check generated config:
   - DHCP: dhcpd -t -cf /etc/dhcp/dhcpd.conf
   - Unbound (RCT): unbound-checkconf
   - named (others): named-checkconf
```

### Tier 3: DHCP Not Serving Clients

```
1. Test DHCP config:
   dhcpd -t -cf /etc/dhcp/dhcpd.conf

2. Check for errors:
   grep -i error /var/log/syslog | tail -20
   journalctl -u isc-dhcp-server --since "30m ago"

3. Verify leases:
   cat /var/lib/dhcp/dhcpd.leases | head -50

4. Check bridge exists and is up:
   ip link show bridge_501
   brctl show bridge_501
```

### Tier 3b: DNS Not Serving Clients (non-`smc_ltp` hosts — Unbound + Stubby)

**Corrected 2026-07-03, membership count corrected twice 2026-08-03**: this is gated by `smc_ltp` inventory-group membership, not flavor — applies to every flavor's hosts except those in `smc_ltp` (a
static `rcp`-only group, 7 sites — `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona`, all "low touch"-onboarded — see `08_ansible-authoring.md` "smc_ltp
Sub-Group" for the full picture, including its unrelated CNMaestro backhaul-provisioning role). This tier only covers DHCP/LAN client DNS; the SMC's own DNS resolution is a separate
`systemd-resolved`/glibc path — see `02_service-map.md` and `06_failure-modes.md` if the box itself (not a client) is slow to resolve names.

```
1. Check Unbound:
   systemctl status unbound
   unbound-checkconf
   unbound-control status
   journalctl -u unbound --since "30m ago"

2. Check Stubby (DNS-over-TLS upstream):
   systemctl status stubby
   journalctl -u stubby --since "30m ago"
   # Stubby listens on 127.0.0.1:60053; Unbound forwards here.
   # Stubby's own upstream is 127.0.0.1:60853 (single, no failover) via an
   # autossh local port forward to teleport.apn.au:853 — if journalctl shows
   # repeated connection failures, check `systemctl status autossh-teleport.service`.

3. Test resolution:
   dig @127.0.0.1 google.com
   dig @127.0.0.1:60053 google.com   # direct Stubby test
```

### Tier 3c: DNS Not Serving Clients (`smc_ltp` hosts only — BIND/named)

Applies to the 7 static `smc_ltp` member sites only: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`, `warburton`, `beagle-bay`, `umoona` (`rcp`-exclusive, all "low touch"-onboarded —
`warburton`/`beagle-bay`/`umoona` added 2026-08-03 after the operator confirmed every low-touch site should be a member). These hosts also run CNMaestro-managed Cambium ePMP/cnPilot backhaul
provisioning via a separate `smc_ltp.yml` playbook — if DNS is fine but backhaul radios aren't provisioning, check `roles/smc_cnmaestro_provisioning` and CNMaestro cloud connectivity instead, not this
tier. See `08_ansible-authoring.md` "smc_ltp Sub-Group" for the full mechanism.

```
1. Check named:
   systemctl status named
   named-checkconf
   rndc status
   journalctl -u named --since "30m ago"

2. Verify zones loaded:
   rndc reload
   ls /etc/bind/

3. Test resolution:
   dig @127.0.0.1 <local-domain>
```

### Tier 4: WiFi AP Issues

```
1. hostapd:
   systemctl status hostapd
   journalctl -u hostapd --since "1h ago"
   # Config: /etc/hostapd/

2. CNMaestro provisioning:
   systemctl status cnmaestro-provisioning
   journalctl -u cnmaestro-provisioning --since "1h ago"
   cat /var/log/cnmaestro-provisioning/*.log 2>/dev/null || ls /var/log/
   redis-cli ping     # must respond PONG
   redis-cli info server
```

### Tier 5: VoIP / Asterisk Issues (non-RCT only)

```
1. Asterisk CLI:
   asterisk -rvvv

2. Verify dialplan:
   asterisk -rx "dialplan show"
   cat /etc/asterisk/extensions.conf

3. Trunk / SIP registration:
   asterisk -rx "sip show registry"
   asterisk -rx "sip show peers"
```

### Tier 6: HA / Failover Issues (non-RCT only)

```
1. VIP assignment:
   ip addr show
   # VIP should be on active node only

2. VRRP state:
   journalctl -u keepalived --since "1h ago"
   systemctl status keepalived

3. Conntrack limit:
   cat /proc/sys/net/netfilter/nf_conntrack_count
   cat /proc/sys/net/netfilter/nf_conntrack_max
   # Alert fires at > 80%
```

### Tier 7: Monitoring Gaps

```
1. Textfile collectors stale?
   ls -la /var/lib/node_exporter/textfile_collector/
   # Check mtime vs max staleness (see Section 2 table)

   # Manually run stale collector:
   sudo python3 /opt/rise/sbdm.py
   sudo bash /opt/rise/interfacecheckv2.sh

2. Prometheus not federating?
   systemctl status autossh-prometheus-federation
   journalctl -u autossh-prometheus-federation --since "1h ago"

3. node_exporter not scraping?
   curl -s http://localhost:9100/metrics | head -20
   systemctl status node_exporter

4. A specific metric missing from Grafana/Prometheus, but node_exporter IS up?
   Don't stop at `up{instance="..."} == 1` — that only proves the scrape target is
   reachable, not that every expected metric is populated. Query the specific metric
   directly against the instance and compare to a known-healthy site:
     curl -s http://localhost:9100/metrics | grep <metric_name>
   Confirmed gap (2026-07-29, see 13_known-issues.md): `my_node_network_device_info`
   returns zero series on some rcp sites while base kernel network metrics and `up`
   are both fine on the same hosts — a per-metric gap, not a per-scrape-target one.
```

### Tier 8: Overlayroot — Ansible Changes Not Persisting

```
Problem: Ansible ran successfully but changes disappeared after reboot.

Cause: Writes went to tmpfs upper dir (/media/root-rw/overlay), not to
the real filesystem (/media/root-ro).

Verify:
   mount | grep overlay
   # Lower dir must be remounted rw for changes to persist

Ansible fix:
   The smc_bases.yml playbook handles overlayroot remount before making
   changes. If running a role directly, ensure smc_bases.yml ran first or
   that the lower dir is already mounted rw.

Manual check:
   mount | grep root-ro
   # If "ro" → changes will not persist
   # If "rw" → changes will persist
```

### Tier 8b: Box Reboot-Looping Every Few Minutes (overlay RAM exhaustion)

A short, regular reboot cycle on a RISE host with overlayroot active is almost always the tmpfs upper layer filling, not a disk, kernel or hardware fault. Work it in this order.

1. **Confirm who is rebooting.** `rise_watchdog.py` reboots (`reboot_critical` when disk >= `DISK_THRESH`, `reboot_after_cleanup` when cleanup frees too little). `rise_healthcheck.py` **never**
   reboots — it only scores and applies penalties. Do not chase the healthcheck.
   ```bash
   systemctl status rise-watchdog.service rise-healthcheck.service
   tail -50 /var/log/rise/watchdog.log
   ```
2. **Do not be reassured by `df` on the real filesystem.** The exhausted resource is RAM. Compare the overlay budget against what is actually resident:
   ```bash
   free -m                              # total RAM
   grep size_ratio inventories/<flavor>/group_vars/smc_bases.yml   # 40 on rct/wh/nbn_wh
   mount | grep 'overlayroot on / type overlay'
   df -h / /media/root-ro
   ```
Budget = `RAM x size_ratio / 100`. On a 7807 MiB Pi 4 at 40% that is ~3.05 GiB.
3. **Find the oversized file, remembering copy_up charges size at first write** (see `07_hardware-overlay.md` §8) — a slow-growing giant is far more dangerous than a fast-growing small file:
   ```bash
   find / -xdev -type f -size +20M -printf '%s\t%TY-%Tm-%Td %TH:%TM\t%p\n' 2>/dev/null | sort -rn | head -30
   ```
Or, on a host that already has the role deployed, the supported form — safe on live overlay hosts because reading does not trigger copy_up:
   ```bash
   /usr/local/bin/rise_logcap.py --report-only --json
   ```
4. **Check whether anything rotates it at all.** The 2026-08-18 `delye-smc01` case was a 2.63 GiB Laravel log with no stanza anywhere:
   ```bash
   grep -rl '<app-name>\|<log-basename>' /etc/logrotate.d/
   ```
5. **Remedy.** Truncate (keeping a tail) rather than delete, so writers holding an fd keep working — and if rsyslog owns the file, make it reopen afterwards or the truncation frees nothing:
   ```bash
   /usr/lib/rsyslog/rsyslog-rotate     # or: systemctl kill -s HUP rsyslog.service
   ```
Never truncate a `.gz`. Then deploy `smc_rise_logcaps` (`--tags logcaps`) so it cannot recur.
6. **Escape hatch if the box is unreachable between reboots**: disable overlayroot to get a stable shell (`smc_rise_disable_overlay`, or `-e disable_overlay=true` on `smc_bases.yml`), fix the file,
   then re-enable. Note the overlay-enable preflight now **fails** if any oversized file remains that the cap cannot safely truncate.

### Tier 9: `smc_iptables` SMP apply fails with `Set restricted doesn't exist`

**Status: RESOLVED 2026-06-09** — removed ipset match rule from template on `family-friendly` branch.

```
Symptom:
  TASK [smc_iptables : Generate and copy iptables configuration for smp]
  iptables-restore ... Set restricted doesn't exist

Root cause:
  fqdn2ip/ipset teardown removed runtime `restricted` set, but SMP iptables
  template still referenced `-m set --match-set restricted dst`.

Current policy:
  No site should rely on ipset classification for this path anymore.
  SMP metered-time flow must be deterministic and non-ipset.
  Service is unlimited — metered/unmetered distinction is no longer active.
  The METERED_TIME chain and ECLIPSE_METERED_TIME chain remain in the template
  for connmark-based traffic classification but do not enforce data quotas.

Source of truth:
  roles/smc_iptables/templates/iptables.smp.j2
  roles/smc_iptables/defaults/main.yml
  roles/smc_fqdn2ip/tasks/main.yml

Fix applied (2026-06-09):
  Removed line from iptables.smp.j2 METERED_TIME chain:
    -A METERED_TIME -m set ! --match-set restricted dst -j RETURN
  Retained non-ipset returns:
    -A METERED_TIME -m connmark --mark 0 -j RETURN
    -A METERED_TIME -j RETURN

Fix pattern (for reference):
  1. Remove ipset match lines from SMP template.
  2. Keep non-ipset returns (as above).
  3. Remove stale ipset feature flags/conditionals and stale comments.
  4. Validate with:
       ansible-playbook -i inventories/rct/stage smc_bases.yml -l <host> -t smc_iptables -vv
```

### Tier 10: `smc_application` fails with `Invalid data passed to 'loop'`

```
Symptom:
  TASK [smc_application : Collect archive size for each pkg (bytes)]
  Invalid data passed to 'loop' ... got this instead: php8.1-cli

Root cause:
  roles/_helpers/custom_apt_install.yml normalized package input with
  `install_package_name is sequence`, which evaluates true for strings.
  That made `pkgs` scalar instead of list for single package names.

Source of truth:
  roles/_helpers/custom_apt_install.yml (package normalization + loop users)

Fix:
  Normalize as:
    install_package_name if iterable and not string else [install_package_name]

Why:
  Loops must always receive a list; string package names like `php8.1-cli`
  must become `[php8.1-cli]`.

Validation:
  ansible-playbook --syntax-check smc_bases.yml
  ansible-playbook -i inventories/rct/stage smc_bases.yml -l <host> -t smc_application --syntax-check
```

**Superseded 2026-07-29 (old-looma/umoona topology recovery):** the `is sequence` normalization above was the first-attempt fix, but it hit a second incompatibility under `--check` mode (`Package
unavailable`). The fix actually applied was a **wholesale replacement**, not an in-place patch: `roles/_helpers/custom_apt_install.yml` and `custom_apt_update_cache.yml` were replaced with their
`rise-multi` branch versions — a simpler `apt-cache policy` check with no size-collection step. If this symptom recurs, check which version of these two helper files is deployed before re-deriving the
`is sequence` fix from scratch.

### Tier 11: `--check` does not gate `command` + `async` restart handlers

```
Symptom:
  An `ansible-playbook --check --diff` run against a live SMC, intended as a
  read-only preview, actually restarts a live service. journalctl on the
  target shows a real `ansible-ansible.legacy.command Invoked with cmd=...`
  log line for a command the run was only supposed to be previewing.

Root cause:
  `command`/`shell` modules wrapped in `async:`/`poll: 0` do not reliably
  respect --check mode in this Ansible version -- this is a general Ansible
  property, not a task-authoring mistake. No `check_mode:` directive is
  needed to trigger it; the escape happens by default. Confirmed live on
  pandanus-park-smc01, 2026-07-30: `smc_application`'s "Ubuntu Restart
  Internet interfaces" handler (`command: systemctl restart
  dhclient@*.service`, `async: 60, poll: 0`) executed for real during
  --check --diff, while the `template` task that notified it correctly
  stayed in check mode and did not write the file -- a disruptive restart
  against a configuration that was never actually updated.

Source of truth:
  roles/smc_application/handlers/main.yml ("Ubuntu Restart Internet
  interfaces" handler)
  roles/smc_network/handlers/main.yml (contrast: "Protected
  systemd-resolved restart" / "Protected systemd-networkd reload" use the
  `service:` module, state: restarted/reloaded, which DOES correctly
  respect check mode -- these were never at risk)

Why the difference:
  `service:` does not support glob unit names (`dhclient@*.service`), so
  the dhclient-restart handlers use `command:` instead -- which is the
  exact combination that bypasses check mode when wrapped in async.

Fix / mitigation:
  Do not treat `--check --diff` as a safety gate for any handler built on
  `command:`/`shell:` + `async:`. The rendered-file diff shown by
  --check --diff remains accurate as a preview of *what config would
  change* -- it is only the *handler's* behavior during that same run that
  cannot be trusted to stay inert. Review the task diff statically instead
  of relying on a live --check run when the notified handler uses this
  shape. Before running --check against any host with a pending change to
  dhclient-enter-hooks or equivalent, expect the restart to actually fire,
  and treat it the same as a real deploy for change-control purposes.

Validation:
  journalctl --since <window> | grep 'ansible-ansible.legacy.command' on
  the target after any --check run touching this handler shape, to confirm
  whether it actually executed.

Full incident writeup: local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/pandanus-park-checkmode-async-restart-incident-20260730_1140.md
```

### Cross-Tier: Reject vs Drop, Where a Rejection Was Generated, and On-Box Tooling Gotchas

Established during the 2026-09-08 galiwinku port-80 investigation (see `06_failure-modes.md` "Port-80 Source-IP Allowlist on the APN VIP"). These techniques are not specific to that incident — they
answer the general "is it them or us?" question on any SMC.

**Locate where a rejection is generated, using the ICMP error's TTL.** Compare the TTL of the returned ICMP error against the TTL of known-good replies from the same host:

- **TTLs match** → the rejection genuinely originates at the far end.
- **The error's TTL is much higher** → a nearby middlebox forged it, and the far end never saw the packet.

Worked example: the ICMP admin-prohibited arrived at `ttl 49`, identical to genuine ping replies from the same host (`ttl 49`), proving a far-end origin ~13–14 hops away. The SYN quoted inside the
ICMP error's payload showed `ttl 51` (sent at 64), corroborating the hop count independently.

**Measure the failure latency to separate a reject from a drop.** An active reject returns in **~1 RTT**; a drop/blackhole shows as a **multi-second timeout**. A "connection failed" that comes back
instantly is almost always something answering, not something missing.

**On-box tooling gotchas (SMC appliances):**

- **`traceroute` is NOT installed.** Available instead: `mtr`, `nping`, `nmap`, `tracepath`, `busybox`.
- **`mtr --interface <if>` binds correctly in TCP mode (`-T`) but NOT in ICMP mode.** An ICMP trace requested on `vlan534` silently egressed via `eno1`. **Always verify hop 1 matches the intended
  gateway before trusting any interface-bound trace** — the wrong-interface result looks completely plausible.
- **`mtr` showing "0.0% loss" at the final hop does NOT mean the service is reachable.** It counts *any* response for that TTL as success, including an ICMP rejection. A clean-looking mtr is fully
  compatible with a hard-rejected service.
- **`tcpdump` buffers its output** — reading the capture file while it is still running shows nothing. Wait for it to exit, use `-U`, or (preferred) `-w file.pcap` and decode separately.
- **A `host <ip>` tcpdump filter will NOT match returning ICMP errors.** Their outer header is gateway→us, not peer→us. Use `'host <ip> or icmp'`, and decode with `-vv` to see the embedded quoted
  packet and its TTL (which is what the TTL technique above depends on).
- **`curl -w ... 2>&1 | tail -1` masks the real error.** Capture `rc=$?` separately — exit **7** ("No route to host", never established) and exit **56** ("Connection reset by peer", established then
  reset) are completely different diagnoses and the piped one-liner hides which one you got.

---
