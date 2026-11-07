---
Title: Research sources 2026-11-07
Category: reference
Status: current
Authority: local-supplement
Scope: Verbatim copies of the external pages and lab source excerpts skill-proxmox relies on
Last reviewed: 2026-11-07
Summary: >-
  Index of the captures fetched on 2026-11-07 (Proxmox VE docs and wiki, bpg provider docs and issues, OpenTofu docs, bugzilla lists,
  edk2 sources), with URL and what each supports.
---

# Research sources 2026-11-07

Each file is the page as fetched on 2026-11-07 and kept verbatim: Markdown from the all-scraper fetcher (`fetch --markdown`, which
starts each file with a `Contents of <url>:` line), raw HTML where the Markdown fetch was cut at about 100 KB (the qm, sysadmin and
pmxcfs chapters, the Roadmap), raw text or JSON from GitHub and bugzilla. The three edk2 files and the Proxmox package excerpt were
copied from smc-resiliency's `docs/x86/x86-ab-boot-research-sources-20261107_1504/` (same day). The installed-source excerpt was read
on a lab node; its host is withheld. These files are exempt from the pack's redaction scan except for private keys, because published
pages carry example addresses. context7 (`/bpg/terraform-provider-proxmox`) was also queried on 2026-11-07 for `import_from`; its answer
matched the vm resource page and is not saved separately. The replication chapter capture is partial (the fetcher kept about 6 KB). One edit to a capture: the provider index's example SSH
key (a truncated documentation placeholder, not a real key) has its BEGIN delimiter replaced so the private-key scan stays strict.

| File | URL | Supports |
| --- | --- | --- |
| [bpg-issues-cloud-init.json](bpg-issues-cloud-init.json) | <https://api.github.com/search/issues?per_page=30&sort=updated&q=repo:bpg/terraform-provider-proxmox+cloud-init+is:issue> | GitHub issue search: provider cloud-init issues (JSON) |
| [bpg-issues-efi-disk.json](bpg-issues-efi-disk.json) | <https://api.github.com/search/issues?per_page=30&sort=updated&q=repo:bpg/terraform-provider-proxmox+efi_disk> | GitHub issue search: efi_disk issues and PRs |
| [bpg-issues-import-from.json](bpg-issues-import-from.json) | <https://api.github.com/search/issues?per_page=30&sort=updated&q=repo:bpg/terraform-provider-proxmox+import_from> | GitHub issue search: import_from issues and PRs |
| [bpg-provider-CHANGELOG.md](bpg-provider-CHANGELOG.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/CHANGELOG.md> | Provider changelog: 0.111 to 0.120 breaking changes |
| [bpg-provider-guide-cloud-image.md](bpg-provider-guide-cloud-image.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/docs/guides/cloud-image.md> | Cloud image guide: download_file and import_from |
| [bpg-provider-guide-known-issues.md](bpg-provider-guide-known-issues.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/docs/guides/known-issues.md> | Provider known issues (VMDK import, API limits) |
| [bpg-provider-index.md](bpg-provider-index.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/docs/index.md> | Provider auth, environment variables, SSH table, root-only operations, sample role |
| [bpg-provider-releases-latest.json](bpg-provider-releases-latest.json) | <https://api.github.com/repos/bpg/terraform-provider-proxmox/releases/latest> | Latest release v0.120.0 (2026-11-02) |
| [bpg-provider-virtual_environment_acl.md](bpg-provider-virtual_environment_acl.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/docs/resources/virtual_environment_acl.md> | ACL resource |
| [bpg-provider-virtual_environment_download_file.md](bpg-provider-virtual_environment_download_file.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/docs/resources/virtual_environment_download_file.md> | download_file: import content type, Sys.Audit + Sys.Modify |
| [bpg-provider-virtual_environment_user_token.md](bpg-provider-virtual_environment_user_token.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/docs/resources/virtual_environment_user_token.md> | user_token resource |
| [bpg-provider-virtual_environment_vm.md](bpg-provider-virtual_environment_vm.md) | <https://raw.githubusercontent.com/bpg/terraform-provider-proxmox/main/docs/resources/virtual_environment_vm.md> | VM resource: efi_disk, import_from, agent, serial_device, stop_on_destroy |
| [community-forum-api-token-config.md](community-forum-api-token-config.md) | <https://forum.proxmox.com/threads/api-token-config.92465/> | Forum: the token header carries the secret, not the token id |
| [community-proxploy-minimal-privilege-token.md](community-proxploy-minimal-privilege-token.md) | <https://docs.proxploy.dev/getting-started/proxmox-token/> | Vendor guide: roles split by capability, privsep tokens (secondary) |
| [edk2-BdsEntry.c.txt](edk2-BdsEntry.c.txt) | <https://raw.githubusercontent.com/tianocore/edk2/master/MdeModulePkg/Universal/BdsDxe/BdsEntry.c> | BootNext cached, deleted, booted (copied from smc-resiliency research) |
| [edk2-QemuBootOrderLib.c.txt](edk2-QemuBootOrderLib.c.txt) | <https://raw.githubusercontent.com/tianocore/edk2/master/OvmfPkg/Library/QemuBootOrderLib/QemuBootOrderLib.c> | BootOrder rewritten from fw_cfg; HD() options pruned (copied) |
| [edk2-ovmf-BdsPlatform.c.txt](edk2-ovmf-BdsPlatform.c.txt) | <https://raw.githubusercontent.com/tianocore/edk2/master/OvmfPkg/Library/PlatformBootManagerLib/BdsPlatform.c> | OVMF calls SetBootOrderFromQemu each boot (copied) |
| [opentofu-backend-local.md](opentofu-backend-local.md) | <https://opentofu.org/docs/language/settings/backends/local/> | Local backend path |
| [opentofu-dependency-lock.md](opentofu-dependency-lock.md) | <https://opentofu.org/docs/language/files/dependency-lock/> | Commit .terraform.lock.hcl |
| [proxmox-trixie-no-subscription-edk2-qemu-packages-excerpt.txt](proxmox-trixie-no-subscription-edk2-qemu-packages-excerpt.txt) | <http://download.proxmox.com/debian/pve/dists/trixie/pve-no-subscription/binary-amd64/Packages.gz> | pve-edk2-firmware and pve-qemu-kvm repository versions (copied) |
| [pve-9.1.5-installed-storage-download-url-permissions.txt](pve-9.1.5-installed-storage-download-url-permissions.txt) | lab node, `/usr/share/perl5/PVE/API2/Storage/Status.pm` (read-only) | download-url permission check: Sys.AccessNetwork alternative |
| [pve-admin-chapter-ha-manager.md](pve-admin-chapter-ha-manager.md) | <https://pve.proxmox.com/pve-docs/chapter-ha-manager.html> | HA requirements, rules, fencing |
| [pve-admin-chapter-pct.md](pve-admin-chapter-pct.md) | <https://pve.proxmox.com/pve-docs/chapter-pct.html> | Containers, templates, unprivileged, features |
| [pve-admin-chapter-pmxcfs.html](pve-admin-chapter-pmxcfs.html) | <https://pve.proxmox.com/pve-docs/chapter-pmxcfs.html> | pmxcfs: database-backed, 128 MiB, read-only without quorum, file table (raw HTML) |
| [pve-admin-chapter-pve-firewall.md](pve-admin-chapter-pve-firewall.md) | <https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html> | Firewall levels, default block, nftables |
| [pve-admin-chapter-pvecm.md](pve-admin-chapter-pvecm.md) | <https://pve.proxmox.com/pve-docs/chapter-pvecm.html> | Cluster create and join, quorum, QDevice, cluster network |
| [pve-admin-chapter-pvesdn.md](pve-admin-chapter-pvesdn.md) | <https://pve.proxmox.com/pve-docs/chapter-pvesdn.html> | SDN zones, VNets, subnets, DHCP IPAM, support status, IPAM plugins |
| [pve-admin-chapter-pvesm.md](pve-admin-chapter-pvesm.md) | <https://pve.proxmox.com/pve-docs/chapter-pvesm.html> | Storage types, content types incl. import, directory layout |
| [pve-admin-chapter-pvesr.md](pve-admin-chapter-pvesr.md) | <https://pve.proxmox.com/pve-docs/chapter-pvesr.html> | Storage replication (partial extract) |
| [pve-admin-chapter-pveum.md](pve-admin-chapter-pveum.md) | <https://pve.proxmox.com/pve-docs/chapter-pveum.html> | Users, realms, tokens, privsep, privileges, ACL paths, inheritance, pools |
| [pve-admin-chapter-qm.html](pve-admin-chapter-qm.html) | <https://pve.proxmox.com/pve-docs/chapter-qm.html> | VMs: machine, CPU, EFI disk, boot order, cloud-init, agent, clones, hookscripts (raw HTML) |
| [pve-admin-chapter-sysadmin.html](pve-admin-chapter-sysadmin.html) | <https://pve.proxmox.com/pve-docs/chapter-sysadmin.html> | Updates, daily check, metric servers, certificate renewal (raw HTML) |
| [pve-admin-chapter-vzdump.md](pve-admin-chapter-vzdump.md) | <https://pve.proxmox.com/pve-docs/chapter-vzdump.html> | Backup modes, fleecing, retention, protected backups |
| [pve-bugzilla-cloudinit.csv](pve-bugzilla-cloudinit.csv) | <https://bugzilla.proxmox.com/buglist.cgi?ctype=csv&quicksearch=cloud-init> | Open cloud-init bugs (CSV) |
| [pve-bugzilla-ovmf.csv](pve-bugzilla-ovmf.csv) | <https://bugzilla.proxmox.com/buglist.cgi?ctype=csv&quicksearch=ovmf%20efidisk> | OVMF and EFI disk bugs (CSV) |
| [pve-bugzilla-sdn-dhcp.csv](pve-bugzilla-sdn-dhcp.csv) | <https://bugzilla.proxmox.com/buglist.cgi?ctype=csv&quicksearch=sdn%20dhcp> | SDN DHCP bugs (CSV) |
| [pve-pvesh-man1.md](pve-pvesh-man1.md) | <https://pve.proxmox.com/pve-docs/pvesh.1.html> | pvesh verbs and output formats |
| [pve-pveum-man1.md](pve-pveum-man1.md) | <https://pve.proxmox.com/pve-docs/pveum.1.html> | pveum syntax: token add, user permissions, expire |
| [pve-qm-conf-man5.md](pve-qm-conf-man5.md) | <https://pve.proxmox.com/pve-docs/qm.conf.5.html> | efidisk0 options, net firewall flag, watchdog |
| [pve-wiki-api.md](pve-wiki-api.md) | <https://pve.proxmox.com/wiki/Proxmox_VE_API> | API URL, tickets, CSRF, token header |
| [pve-wiki-certificate-management.md](pve-wiki-certificate-management.md) | <https://pve.proxmox.com/wiki/Certificate_Management> | Node certificates, ACME |
| [pve-wiki-cloud-init-support.md](pve-wiki-cloud-init-support.md) | <https://pve.proxmox.com/wiki/Cloud-Init_Support> | Cloud-init |
| [pve-wiki-external-metric-server.md](pve-wiki-external-metric-server.md) | <https://pve.proxmox.com/wiki/External_Metric_Server> | Graphite, InfluxDB |
| [pve-wiki-network-configuration.md](pve-wiki-network-configuration.md) | <https://pve.proxmox.com/wiki/Network_Configuration> | ifupdown2, bridges, VLAN-aware bridge |
| [pve-wiki-package-repositories.md](pve-wiki-package-repositories.md) | <https://pve.proxmox.com/wiki/Package_Repositories> | Enterprise, no-subscription, test, deb822 |
| [pve-wiki-qemu-guest-agent.md](pve-wiki-qemu-guest-agent.md) | <https://pve.proxmox.com/wiki/Qemu-guest-agent> | Guest agent |
| [pve-wiki-roadmap.html](pve-wiki-roadmap.html) | <https://pve.proxmox.com/wiki/Roadmap> | 9.0, 9.1, 9.2 release notes and known issues (raw HTML) |
| [pve-wiki-serial-terminal.md](pve-wiki-serial-terminal.md) | <https://pve.proxmox.com/wiki/Serial_Terminal> | Serial console |
| [pve-wiki-storage-pbs.md](pve-wiki-storage-pbs.md) | <https://pve.proxmox.com/wiki/Storage:_Proxmox_Backup_Server> | PBS storage, client-side encryption |
| [pve-wiki-system-software-updates.md](pve-wiki-system-software-updates.md) | <https://pve.proxmox.com/wiki/System_Software_Updates> | apt full-upgrade, never apt upgrade |
| [pve-wiki-upgrade-from-8-to-9.md](pve-wiki-upgrade-from-8-to-9.md) | <https://pve.proxmox.com/wiki/Upgrade_from_8_to_9> | pve8to9, trixie, Ceph Squid prerequisite |
