# Documents

Verbatim source captures behind this pack's claims, one folder per research date. Every file is listed here with its sha256; the contract
test fails when a file is missing from this table, listed but absent, or changed without a new hash. The per-date folder's own
[readme](research-sources-20261107/readme.md) gives each file's URL.

| File | Supports | sha256 |
| --- | --- | --- |
| [bpg-issues-cloud-init.json](research-sources-20261107/bpg-issues-cloud-init.json) | GitHub issue search: provider cloud-init issues (JSON) | `f01bd0967ab1db9dc8f9a9adabc0775f0ae726fd75c3e28067463c385d59bbb3` |
| [bpg-issues-efi-disk.json](research-sources-20261107/bpg-issues-efi-disk.json) | GitHub issue search: efi_disk issues and PRs | `6af299d7da652fd1f5623d78f041db2f361c40b60deb67deea65592bf81e5703` |
| [bpg-issues-import-from.json](research-sources-20261107/bpg-issues-import-from.json) | GitHub issue search: import_from issues and PRs | `b69ce656a9b02f9250cf5d1e4e63c12fa532a3d30572aa71bd0ffe96d30efce4` |
| [bpg-provider-CHANGELOG.md](research-sources-20261107/bpg-provider-CHANGELOG.md) | Provider changelog: 0.111 to 0.120 breaking changes | `d010dfa69c09eb6edbd2f037b308a9a3a341adb83c38fec04703740940acfc40` |
| [bpg-provider-guide-cloud-image.md](research-sources-20261107/bpg-provider-guide-cloud-image.md) | Cloud image guide: download_file and import_from | `ff6e75e4bd7a647c54a7d82e1b576374828a657ebbc1d1f597d5b017b931150a` |
| [bpg-provider-guide-known-issues.md](research-sources-20261107/bpg-provider-guide-known-issues.md) | Provider known issues (VMDK import, API limits) | `577acce462f32949f061eafb90bcdfdaa0fd093778c40c592600ab156a204e58` |
| [bpg-provider-index.md](research-sources-20261107/bpg-provider-index.md) | Provider auth, environment variables, SSH table, root-only operations, sample role | `6d626aac42fdb562fa1ef91637a68bd14fe3e630c91d6929907524c3386f266e` |
| [bpg-provider-releases-latest.json](research-sources-20261107/bpg-provider-releases-latest.json) | Latest release v0.120.0 (2026-11-02) | `8c831d9906c571c5e1decc39f41946374da823aa5ec1fef2f0a55504bcbb346b` |
| [bpg-provider-virtual_environment_acl.md](research-sources-20261107/bpg-provider-virtual_environment_acl.md) | ACL resource | `5b6ba5c241bff40d1750c6d3d66eb5fde0dfb0a884b23e8733f0a066198fb5da` |
| [bpg-provider-virtual_environment_download_file.md](research-sources-20261107/bpg-provider-virtual_environment_download_file.md) | download_file: import content type, Sys.Audit + Sys.Modify | `8730669a4dd03a0faab78b8aa3bf79ab101e5ff7e9813964594bb817e5faa185` |
| [bpg-provider-virtual_environment_user_token.md](research-sources-20261107/bpg-provider-virtual_environment_user_token.md) | user_token resource | `5507bc91e7ea702938256282a3eca6e06fdd83b23125c1925ac5f941056d993a` |
| [bpg-provider-virtual_environment_vm.md](research-sources-20261107/bpg-provider-virtual_environment_vm.md) | VM resource: efi_disk, import_from, agent, serial_device, stop_on_destroy | `b31c6d0c4fb9e52836444f67e689757d6bde5b9cfcedaf415017433d7044e2ba` |
| [community-forum-api-token-config.md](research-sources-20261107/community-forum-api-token-config.md) | Forum: the token header carries the secret, not the token id | `d89b1f6b9e42a2ba4a5b9e6b716cd8913f2ebe77a62dca6453de4fb4cad80ba1` |
| [community-proxploy-minimal-privilege-token.md](research-sources-20261107/community-proxploy-minimal-privilege-token.md) | Vendor guide: roles split by capability, privsep tokens (secondary) | `3ad48c24e6e9e20c465b2e3ce55a4240d801b7c6f7460b7488c4cb092f93f6b7` |
| [edk2-BdsEntry.c.txt](research-sources-20261107/edk2-BdsEntry.c.txt) | BootNext cached, deleted, booted (copied from smc-resiliency research) | `0cfe0e426f30057631305d1b8ebc17fae1d697b02a12781e545158819f62924f` |
| [edk2-QemuBootOrderLib.c.txt](research-sources-20261107/edk2-QemuBootOrderLib.c.txt) | BootOrder rewritten from fw_cfg; HD() options pruned (copied) | `6f8619faae9e9250d6f9e06290c18b5b9b1c07d574c18c25a3533bd7808f602f` |
| [edk2-ovmf-BdsPlatform.c.txt](research-sources-20261107/edk2-ovmf-BdsPlatform.c.txt) | OVMF calls SetBootOrderFromQemu each boot (copied) | `6e76733025ce10ff0a1c54bce99dca20693882bbd6996ee4452dc29aea1fbba6` |
| [opentofu-backend-local.md](research-sources-20261107/opentofu-backend-local.md) | Local backend path | `caf856ac6638a8e3a900ba644787a5819aed429e13340637cb04d187788c3c95` |
| [opentofu-dependency-lock.md](research-sources-20261107/opentofu-dependency-lock.md) | Commit .terraform.lock.hcl | `7215ec1601e6bd0048db33c834b4ed32b8a79105684dadd1e25afa2362702b66` |
| [proxmox-trixie-no-subscription-edk2-qemu-packages-excerpt.txt](research-sources-20261107/proxmox-trixie-no-subscription-edk2-qemu-packages-excerpt.txt) | pve-edk2-firmware and pve-qemu-kvm repository versions (copied) | `6265f7263c8940e2c1685f66483f7165b69af8c84dc51989234f60f09c459463` |
| [pve-9.1.5-installed-storage-download-url-permissions.txt](research-sources-20261107/pve-9.1.5-installed-storage-download-url-permissions.txt) | download-url permission check: Sys.AccessNetwork alternative | `5e6d6d1aea112d5e88ffd761c032bcd8d67406cd8223a6e193d4125a948a6b89` |
| [pve-admin-chapter-ha-manager.md](research-sources-20261107/pve-admin-chapter-ha-manager.md) | HA requirements, rules, fencing | `1a3ccc3b87c780ad233ccd44742b338e269073e0d18af05382d4d0555b90cacf` |
| [pve-admin-chapter-pct.md](research-sources-20261107/pve-admin-chapter-pct.md) | Containers, templates, unprivileged, features | `76fbf0e66b85a35d135ab0a2cce98770362d7a78b0c7261e5a9a13a650d642d3` |
| [pve-admin-chapter-pmxcfs.html](research-sources-20261107/pve-admin-chapter-pmxcfs.html) | pmxcfs: database-backed, 128 MiB, read-only without quorum, file table (raw HTML) | `adaea9099007cafa202592504e70b34a4e77bac18126e8cc5863cfc03ec1c1c2` |
| [pve-admin-chapter-pve-firewall.md](research-sources-20261107/pve-admin-chapter-pve-firewall.md) | Firewall levels, default block, nftables | `a5c0fe5cc9e4339e5dae2e686f94dd4aec08df850cd4aa0e091948fad1227361` |
| [pve-admin-chapter-pvecm.md](research-sources-20261107/pve-admin-chapter-pvecm.md) | Cluster create and join, quorum, QDevice, cluster network | `1e1f6d258ce076ba0ee031ae1b62498eca4a0894f0b70e434c3b7fba1817f18f` |
| [pve-admin-chapter-pvesdn.md](research-sources-20261107/pve-admin-chapter-pvesdn.md) | SDN zones, VNets, subnets, DHCP IPAM, support status, IPAM plugins | `b7b172e9013973ddb0d744b7bc8d997a2245d48f48613a9d7e7830e6baf60e46` |
| [pve-admin-chapter-pvesm.md](research-sources-20261107/pve-admin-chapter-pvesm.md) | Storage types, content types incl. import, directory layout | `60cfc0c06e3587e923a53101d5817b10520998b35fa976981e2c996eff11715e` |
| [pve-admin-chapter-pvesr.md](research-sources-20261107/pve-admin-chapter-pvesr.md) | Storage replication (partial extract) | `2944cd0b7e7ad0fdf9662d9a742e96f5f4d7c764ecef256bc5220ba14628cdad` |
| [pve-admin-chapter-pveum.md](research-sources-20261107/pve-admin-chapter-pveum.md) | Users, realms, tokens, privsep, privileges, ACL paths, inheritance, pools | `153ce907a948269013891a0407c424a7d29ee6cd68e6c86499305aad0c1d0667` |
| [pve-admin-chapter-qm.html](research-sources-20261107/pve-admin-chapter-qm.html) | VMs: machine, CPU, EFI disk, boot order, cloud-init, agent, clones, hookscripts (raw HTML) | `438de8b01fe5d7b45d0940c61e2c37eff7bdc3a6d12b4a3534e1c3fa3fdecef4` |
| [pve-admin-chapter-sysadmin.html](research-sources-20261107/pve-admin-chapter-sysadmin.html) | Updates, daily check, metric servers, certificate renewal (raw HTML) | `7cc942a87549fa4f1ce0debdb110a3f79ccdc5a986fa2ae6d1b784cd7164af26` |
| [pve-admin-chapter-vzdump.md](research-sources-20261107/pve-admin-chapter-vzdump.md) | Backup modes, fleecing, retention, protected backups | `e69003ca871fb00483e89c3f80cd107107e379751d0f182f7086cd102c2d5ec1` |
| [pve-bugzilla-cloudinit.csv](research-sources-20261107/pve-bugzilla-cloudinit.csv) | Open cloud-init bugs (CSV) | `6090145ef761d0ea2ecdb08c6b1cbce959437888602e2ad680d61e881037c410` |
| [pve-bugzilla-ovmf.csv](research-sources-20261107/pve-bugzilla-ovmf.csv) | OVMF and EFI disk bugs (CSV) | `4ccb4088ffae0f1023e4ed669752815c5aa15b1a2ba61ace5032332a73d14b73` |
| [pve-bugzilla-sdn-dhcp.csv](research-sources-20261107/pve-bugzilla-sdn-dhcp.csv) | SDN DHCP bugs (CSV) | `b3f03732dac03f224c10ec3bd32e55fcc2cc72a8eb65cc10f38e2ca9fcef8ac0` |
| [pve-pvesh-man1.md](research-sources-20261107/pve-pvesh-man1.md) | pvesh verbs and output formats | `3c2c721ddbfd19b2952e8879e1995b64d68536fd9872661db6e5f7f9ad532fe0` |
| [pve-pveum-man1.md](research-sources-20261107/pve-pveum-man1.md) | pveum syntax: token add, user permissions, expire | `b7d0e8d17c8ba78233b22a2e443e0ff7f928f08d7252d3ef19f8f95417b294ff` |
| [pve-qm-conf-man5.md](research-sources-20261107/pve-qm-conf-man5.md) | efidisk0 options, net firewall flag, watchdog | `962c148698a56a204e9f0d0a573cb11eef7742e8d7ac715d760b6a94c6cdc509` |
| [pve-wiki-api.md](research-sources-20261107/pve-wiki-api.md) | API URL, tickets, CSRF, token header | `8db163536a324dda36a33dc83591cb004a926e7651b6dbf91f8dc86ee9b79c4a` |
| [pve-wiki-certificate-management.md](research-sources-20261107/pve-wiki-certificate-management.md) | Node certificates, ACME | `3e4cec309da99030b6774c59c51a171551258029f74a158994850147fc4fac3d` |
| [pve-wiki-cloud-init-support.md](research-sources-20261107/pve-wiki-cloud-init-support.md) | Cloud-init | `4b260eb01e0e2343add72fb454f74e7a7bd6c4e80299e1b6dbf3278d50d5b3ae` |
| [pve-wiki-external-metric-server.md](research-sources-20261107/pve-wiki-external-metric-server.md) | Graphite, InfluxDB | `f3de9fc28b72057729a769b919ffee1255b11d6ad03d1efb22925651c57e17fb` |
| [pve-wiki-network-configuration.md](research-sources-20261107/pve-wiki-network-configuration.md) | ifupdown2, bridges, VLAN-aware bridge | `ff10473b344716290ff71076646a63c68b7172889c8e0a7742b85546d1b7f282` |
| [pve-wiki-package-repositories.md](research-sources-20261107/pve-wiki-package-repositories.md) | Enterprise, no-subscription, test, deb822 | `0b2f287f72e9c20225dd400b070173fd79f619be8c87feeb6bd1b7785c6aafe8` |
| [pve-wiki-qemu-guest-agent.md](research-sources-20261107/pve-wiki-qemu-guest-agent.md) | Guest agent | `21268f3fa2cf7462d3eea948da3d0b1faf835eeb47311549c82b25b6a2f35074` |
| [pve-wiki-roadmap.html](research-sources-20261107/pve-wiki-roadmap.html) | 9.0, 9.1, 9.2 release notes and known issues (raw HTML) | `40638e297875b9a4c71e8120e0050aad11a5213e915ff22b5f7e6f9fd0cd6fd2` |
| [pve-wiki-serial-terminal.md](research-sources-20261107/pve-wiki-serial-terminal.md) | Serial console | `654a84d5c5420f024e9dd5b9b3e4d2c0609c1eeac6e058d359200cdd732df2b4` |
| [pve-wiki-storage-pbs.md](research-sources-20261107/pve-wiki-storage-pbs.md) | PBS storage, client-side encryption | `642255148f0f7094b731c60ef25c1e56b490c3c5d79e0d8a3bbc6a43f6368685` |
| [pve-wiki-system-software-updates.md](research-sources-20261107/pve-wiki-system-software-updates.md) | apt full-upgrade, never apt upgrade | `90ab324024b23dcc339e054f2de892f4edce2ab7811d5ac7a325d1ddc231b0dc` |
| [pve-wiki-upgrade-from-8-to-9.md](research-sources-20261107/pve-wiki-upgrade-from-8-to-9.md) | pve8to9, trixie, Ceph Squid prerequisite | `0b35ac61bdcce0570196151eaca3e6dc81835266f02de62e5b159bdefe1b12a3` |
| [bpg-provider-releases-latest.json](research-sources-20261109/bpg-provider-releases-latest.json) | Latest release still v0.120.0 (2026-11-02), re-checked 2026-11-09 | `8e322847579f24f881b8293416b759202082dcfdd563b0b06957c19df4f524bb` |
| [pbs-wiki-roadmap.html](research-sources-20261109/pbs-wiki-roadmap.html) | PBS 4.0 to 4.2 release notes: S3 datastores supported in 4.2, encrypted push sync (raw HTML) | `6a78ed2b73863b2be89e13ef68d13f6d0284eaef576125edf95087f0e1e2fc12` |
| [pdm-docs-roadmap.html](research-sources-20261109/pdm-docs-roadmap.html) | PDM 1.0 and 1.1 release notes: remotes, cross-cluster migration, Ceph view, auto-install (raw HTML) | `cb3a7fce151715f00a67ea6dd0122377a2c136909bc08556067ab36b220bf953` |
| [pdm-wiki-roadmap.html](research-sources-20261109/pdm-wiki-roadmap.html) | Old PDM wiki roadmap; says it moved to the PDM docs at 1.0 (raw HTML) | `e0b3feba6a91cbdd35ea04220641b9ddd8b24ec69154fb571eafcaa26958c92d` |
| [pve-admin-chapter-notifications.html](research-sources-20261109/pve-admin-chapter-notifications.html) | Notification targets, matchers, events, templates (raw HTML) | `dc9d1dd78c6be7c6a260b5efc18376400f4c8368dc4e1bfe9efdc623da947dc3` |
| [pve-admin-chapter-pveceph.html](research-sources-20261109/pve-admin-chapter-pveceph.html) | pveceph install, init, mon, mgr, OSD, pools, CephFS, sizing (raw HTML) | `8b0df565cc89cfc2937f6c0f64f17840f24f7e50adca27f75ef61ce54dc617a5` |
| [pve-wiki-roadmap.html](research-sources-20261109/pve-wiki-roadmap.html) | Release history including 9.2 for arm64 (2026-08-05) (raw HTML) | `ae542d57d185d8f18fdef2f91719a1dd23e94ad2356197b565c0e7febf62650a` |
