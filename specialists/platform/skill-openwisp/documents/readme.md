---
Title: OpenWISP documentation snapshots
Category: source-index
Status: current
Authority: Official OpenWISP documentation snapshots
Scope: Local evidence copies used to maintain version-sensitive `skill-openwisp` guidance
Last reviewed: 2026-10-05
Summary: Curated official OpenWISP pages retained locally with source URLs, version scope, and checksums; they are evidence copies, not a second routing layer.
---

## OpenWISP documentation snapshots

These files are official-documentation snapshots fetched on 2026-10-01. The release page establishes the 26.09 component context. The Controller and Monitoring settings pages are explicitly current
documentation: use them for general configuration principles only, never as proof that an observed 1.3 installation has identical settings or runtime behavior.
For exact 26.09 collection/backfill format and graph RECEIVE behavior, consult the versioned official REST/Network Topology pages linked from
[passive ingestion](../references/passive-ingestion.md) and [topology and FOSS](../references/topology-and-foss.md). The local `dev` snapshots may drift from 26.09;
neither proves Controller or Monitoring 1.3 runtime behavior. The settings copies help maintain [customisation and upgrades](../references/customisation-and-upgrades.md).

| File | Official source | Version scope | SHA-256 |
| --- | --- | --- | --- |
| [openwisp-26.09-release-notes.html](openwisp-26.09-release-notes.html) | `https://openwisp.io/docs/dev/releases/26.09.html` | Versioned OpenWISP 26.09 release context | `b6b61bc1378da1df700f14785d6cccc3e055eccb644eea978ff4437f6d533a68` |
| [openwisp-controller-current-settings.html](openwisp-controller-current-settings.html) | `https://openwisp.io/docs/dev/controller/user/settings.html` | Current generic Controller settings; not 1.3 runtime proof | `7215fe2f490f63e47cb844d90e7b048fb9f983fa8af72f72596e79b7cb472d79` |
| [openwisp-monitoring-current-settings.html](openwisp-monitoring-current-settings.html) | `https://openwisp.io/docs/dev/monitoring/user/settings.html` | Current generic Monitoring settings; not 1.3 runtime proof | `a82bb92c16bc39d498b0c304a5dde1b6a2e6ebc3117d5c3f31e8d327025b400a` |
| [openwisp-26.09-monitoring-rest-api.html](openwisp-26.09-monitoring-rest-api.html) | `https://openwisp.io/docs/26.09/monitoring/user/rest-api.html` | Versioned 26.09 Monitoring REST API (push, backfill time format, charts, metrics); fetched 2026-10-05 | `5caec0fb0191441efedca0e20e0751c3fb1fcb11463d51798c924418a7b39d22` |
| [openwisp-26.09-monitoring-settings.html](openwisp-26.09-monitoring-settings.html) | `https://openwisp.io/docs/26.09/monitoring/user/settings.html` | Versioned 26.09 Monitoring settings (retention, auto checks, metrics); fetched 2026-10-05 | `9e7211655b0635be71f15e27094e6c188b5d5b5bc12c8bf78f4e720805817286` |
| [openwisp-26.09-monitoring-checks.html](openwisp-26.09-monitoring-checks.html) | `https://openwisp.io/docs/26.09/monitoring/user/checks.html` | Versioned 26.09 Monitoring stock checks; fetched 2026-10-05 | `0d5909d9b8ec674a63624f69dca490563c7450ef2f2a744f8c17703f9c68b903` |
| [openwisp-26.09-monitoring-management-commands.html](openwisp-26.09-monitoring-management-commands.html) | `https://openwisp.io/docs/26.09/monitoring/user/management-commands.html` | Versioned 26.09 `run_checks`, `migrate_timeseries`; fetched 2026-10-05 | `fe12a094159bde105f099311af9afe43f28bf3d0e5e131d8ff8cee8e05af80f6` |
| [openwisp-26.09-monitoring-developer-utils.html](openwisp-26.09-monitoring-developer-utils.html) | `https://openwisp.io/docs/26.09/monitoring/developer/utils.html` | Versioned 26.09 `register_metric`/`register_chart` and metric config; fetched 2026-10-05 | `1bafacf240d5af51847f1b1609b96362e161128f78f9884079a9531d3fd626f1` |
| [openwisp-26.09-controller-rest-api.html](openwisp-26.09-controller-rest-api.html) | `https://openwisp.io/docs/26.09/controller/user/rest-api.html` | Versioned 26.09 Controller REST API (devices, groups, deactivate/delete); fetched 2026-10-05 | `4aaf7b8c5e9f79655f14749bca587c29b2e7cd023f6ad6b4f606d76caabef791` |
| [openwisp-26.09-controller-settings.html](openwisp-26.09-controller-settings.html) | `https://openwisp.io/docs/26.09/controller/user/settings.html` | Versioned 26.09 Controller settings (name uniqueness, hardware_id); fetched 2026-10-05 | `330cbde8983c85c9661f97051b9bb58a5d5bd6c22d8cdb4b8cda19df76a9c640` |
| [openwisp-26.09-users-rest-api.html](openwisp-26.09-users-rest-api.html) | `https://openwisp.io/docs/26.09/users/user/rest-api.html` | Versioned 26.09 Users REST API (token, Bearer auth, pagination); fetched 2026-10-05 | `ea40f26be959d0bf3ff54a9a550c7a3441b87a9ce14466ff8ffe5e1a510e5477` |
| [openwisp-26.09-users-basic-concepts.html](openwisp-26.09-users-basic-concepts.html) | `https://openwisp.io/docs/26.09/users/user/basic-concepts.html` | Versioned 26.09 organizations, managers, owners, shared objects; fetched 2026-10-05 | `c80b05d895d9a9122c94aea8ef03c67f1ba9f5d13ec26b2a407dbb3f44fcbd16` |
| [openwisp-26.09-notifications-settings.html](openwisp-26.09-notifications-settings.html) | `https://openwisp.io/docs/26.09/notifications/user/settings.html` | Versioned 26.09 Notifications settings; fetched 2026-10-05 | `42802702d6f5e57d27c8b3aad62eb6ad9cff3b78be19b1e032766ecd7d7aefc8` |
| [openwisp-26.09-notifications-developer-notification-types.html](openwisp-26.09-notifications-developer-notification-types.html) | `https://openwisp.io/docs/26.09/notifications/developer/notification-types.html` | Versioned 26.09 notification type registration; fetched 2026-10-05 | `4ce3a3edc6d37387c11acc8fae305f62349b0dd56855c4b45d14d8202e9b7bb7` |
| [openwisp-26.09-docker-settings.html](openwisp-26.09-docker-settings.html) | `https://openwisp.io/docs/26.09/docker/user/settings.html` | Versioned 26.09 docker-openwisp environment variables; fetched 2026-10-05 | `e429a7d26322d4771ea602baab83100aaed362791cac79a2e983308bd631c081` |
| [openwisp-26.09-docker-customization.html](openwisp-26.09-docker-customization.html) | `https://openwisp.io/docs/26.09/docker/user/customization.html` | Versioned 26.09 docker-openwisp custom Django settings mount; fetched 2026-10-05 | `1f1dd1656df39c312ffa66c16239393559aa75bcd717c4427b06028a97fb70b3` |

The `openwisp-26.09-*` rows were fetched on 2026-10-05 from the versioned 26.09 pages and back
[the operations cookbook](../references/operations-cookbook.md).

Do not edit snapshots to change their content. Replace a file only by re-fetching the named source, recalculating its checksum, and updating this index and any affected claim evidence.
