---
Title: Research sources 2026-11-09
Category: reference
Status: current
Authority: local-supplement
Scope: Verbatim copies of the external pages fetched for the 2026-11-09 gap review of skill-proxmox
Last reviewed: 2026-11-09
Summary: >-
  Index of the captures fetched on 2026-11-09 (pveceph and notifications chapters, PVE, PBS and PDM roadmaps, bpg latest release),
  with URL and what each supports.
---

# Research sources 2026-11-09

Each file is the page as fetched with `curl` on 2026-11-09 and kept verbatim (raw HTML, or JSON from the GitHub API). The admin-guide chapters for qm, pvecm and pveum
used in the same review were already captured in [research-sources-20261107](../research-sources-20261107/readme.md) and were read again, not refetched.

| File | URL | Supports |
| --- | --- | --- |
| [bpg-provider-releases-latest.json](bpg-provider-releases-latest.json) | <https://api.github.com/repos/bpg/terraform-provider-proxmox/releases/latest> | Latest release still v0.120.0 (2026-11-02), re-checked 2026-11-09 |
| [pbs-wiki-roadmap.html](pbs-wiki-roadmap.html) | <https://pbs.proxmox.com/wiki/Roadmap> | PBS 4.0 to 4.2 release notes: S3 datastores supported in 4.2, encrypted push sync (raw HTML) |
| [pdm-docs-roadmap.html](pdm-docs-roadmap.html) | <https://pdm.proxmox.com/docs/roadmap.html> | PDM 1.0 and 1.1 release notes: remotes, cross-cluster migration, Ceph view, auto-install (raw HTML) |
| [pdm-wiki-roadmap.html](pdm-wiki-roadmap.html) | <https://pve.proxmox.com/wiki/Proxmox_Datacenter_Manager_Roadmap> | Old PDM wiki roadmap; says it moved to the PDM docs at 1.0 (raw HTML) |
| [pve-admin-chapter-notifications.html](pve-admin-chapter-notifications.html) | <https://pve.proxmox.com/pve-docs/chapter-notifications.html> | Notification targets, matchers, events, templates (raw HTML) |
| [pve-admin-chapter-pveceph.html](pve-admin-chapter-pveceph.html) | <https://pve.proxmox.com/pve-docs/chapter-pveceph.html> | pveceph install, init, mon, mgr, OSD, pools, CephFS, sizing (raw HTML) |
| [pve-wiki-roadmap.html](pve-wiki-roadmap.html) | <https://pve.proxmox.com/wiki/Roadmap> | Release history including 9.2 for arm64 (2026-08-05) (raw HTML) |
