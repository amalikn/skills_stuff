# Capability extension

## Decision rubric

Define the operator-visible outcome and acceptance test first. Evaluate OpenWISP core; Monitoring, Controller, Notifications, and Network Topology modules; documented Django/settings and NetJSON
extension seams; compatible external FOSS or collectors; and only then a narrow custom adapter. At each transition, state why the preceding supported choice cannot meet the result.

Assess maintenance, licence, target image and Python compatibility, effective settings, worker/network reachability, data model and source-of-truth semantics, permissions, operational load,
testability, upgrade/rollback cost, and the consumer that proves success. A module with the right model but no reachable collector is not an operational fit. A data store that accepts an observation
does not thereby become the inventory authority.

## Integration boundary

OpenWISP Controller is oriented around supported configuration backends and OpenWrt-adjacent conventions. Closed firmware may fit passive monitoring while lacking a supported configuration or
firmware-control path. Preserve that boundary instead of building an implicit device controller. Use NetJSON only at the documented seam and version; use external collectors/adapters when they have
clear ownership and a testable contract. Claim O-C08.

## Worked capability-gap decision

Request: graph a closed-firmware radio's peer signal. First check [Monitoring metric and chart support](https://openwisp.io/docs/26.09/monitoring/user/metrics.html)
for the installed version and whether a stock field honestly represents dBm. If not, inspect its documented custom metric/settings seam and whether its worker can
consume a neutral observation; use a small adapter plus metric registration when that produces a fresh point and visible chart. Only then consider an external FOSS
collector/store if OpenWISP's data model or retention cannot meet the result. A custom Django app is justified for a durable new model/notification/permission seam;
a settings hook is narrower for registered metrics. A from-scratch controller or core patch is not justified by a missing chart.

For each choice record module/version, source documentation, licence/maintenance, network vantage, process settings, schema fit, owner of the data, required
permissions and operator-visible acceptance. UNC's passive path is a worked case, not proof OpenWISP controls closed firmware. A missing vendor API/driver cannot be
papered over by a Django extension; route vendor commands and RF interpretation to equipment expertise. Read [passive ingestion](passive-ingestion.md) for the mapper
and [customisation and upgrades](customisation-and-upgrades.md) for the process seam.
