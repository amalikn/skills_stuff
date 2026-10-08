---
Title: Nautobot core data model
Category: skill-reference
Status: current
Authority: Installed Nautobot 3.2.3 source and its bundled documentation; the cited lines win over this summary
Scope: >-
  Modelling decisions and REST payloads for Locations and Location Types, tenancy, Platforms and network_driver, Manufacturers, Device Families and Device
  Types, Interfaces and VLAN modes, VLANs and VLAN Groups, Prefix types, IP assignment, Virtual Chassis, Modules, Cables and paths, Contacts and Teams,
  Statuses, Roles and Tags, Software Versions and Image Files
Last reviewed: 2026-10-05
Summary: Twelve verified modelling recipes for the Nautobot 3.2.3 core data model, each with the rule the model enforces, a payload, a gotcha and a source line.
---

# Nautobot core data model

Verified against: Nautobot 3.2.3 (installed source in a 3.2.3 container, and the docs bundled in the package), checked 2026-10-05.

Source paths are relative to `site-packages/`; `docs/...` is the page under `nautobot/project-static/docs/` (published at `https://archive.docs.nautobot.com/projects/core/en/v3.2.3/<same path>/`).
Payloads go to `https://nautobot.example/api/<path>` with `Authorization: Token $NAUTOBOT_TOKEN`; related objects may be given as UUID or natural-key string (see the operations cookbook, section 2).
Device Lifecycle Management is not installed; its software models are in core since 2.2.

## Summary

| Job                   | Model                       | Key rule                            | Trap                                | Section |
| --------------------- | --------------------------- | ----------------------------------- | ----------------------------------- | ------- |
| Site hierarchy        | LocationType, Location      | type tree + `nestable`              | type of a Location can never change | [1](#1-locations-and-location-types) |
| Who owns it           | Tenant, TenantGroup         | groups nest; tenant name unique     | tenant is part of Device uniqueness | [2](#2-tenancy) |
| How to talk to it     | Platform `network_driver`   | netutils maps to each library       | NAPALM driver is a separate field   | [3](#3-platforms-and-network_driver) |
| What it is            | Manufacturer, DeviceType    | `model` unique per manufacturer     | family is optional grouping only    | [4](#4-manufacturers-device-families-device-types-devices) |
| Ports                 | Interface                   | `mode` gates VLAN fields            | tagged VLANs need `mode: tagged`    | [5](#5-interfaces-modes-vlans-and-lags) |
| Layer 2               | VLAN, VLANGroup             | unique vid and name per group       | one VLAN per site, unless stretched | [6](#6-vlans-and-vlan-groups) |
| Address space         | Prefix `type`               | container / network / pool          | hierarchy is advisory, not enforced | [7](#7-prefix-types-and-namespaces) |
| Addresses on ports    | IPAddressToInterface        | many-to-many, flags per assignment  | every IP needs a parent Prefix      | [8](#8-ip-addresses-and-interface-assignment) |
| Switch stacks         | VirtualChassis              | members need `vc_position`          | interfaces are not renumbered       | [9](#9-virtual-chassis) |
| Line cards and optics | Module, ModuleBay           | installed in a bay or at a Location | never both bay and location         | [10](#10-modules-and-module-bays) |
| Physical links        | Cable                       | `Connected` status makes a path     | renaming `Connected` breaks tracing | [11](#11-cables-and-paths) |
| People and labels     | Contact, Team, Status, Role | content types gate choices          | a Status must list the model        | [12](#12-contacts-teams-statuses-roles-tags-software) |

## Contents

- [Summary](#summary)
- [1. Locations and Location Types](#1-locations-and-location-types)
- [2. Tenancy](#2-tenancy)
- [3. Platforms and network_driver](#3-platforms-and-network_driver)
- [4. Manufacturers, Device Families, Device Types, Devices](#4-manufacturers-device-families-device-types-devices)
- [5. Interfaces: modes, VLANs and LAGs](#5-interfaces-modes-vlans-and-lags)
- [6. VLANs and VLAN Groups](#6-vlans-and-vlan-groups)
- [7. Prefix types and Namespaces](#7-prefix-types-and-namespaces)
- [8. IP addresses and interface assignment](#8-ip-addresses-and-interface-assignment)
- [9. Virtual Chassis](#9-virtual-chassis)
- [10. Modules and module bays](#10-modules-and-module-bays)
- [11. Cables and paths](#11-cables-and-paths)
- [12. Contacts, Teams, Statuses, Roles, Tags, software](#12-contacts-teams-statuses-roles-tags-software)

## 1. Locations and Location Types

Decision: define a short Location Type tree first (for example Region > Site > Building); mark a type `nestable` for variable depth instead of adding parallel branches. Each type lists the content
types (devices, prefixes, VLAN groups, racks) allowed at that level.

```json
POST /api/dcim/location-types/
{"name": "Site", "parent": "Region", "nestable": false, "content_types": ["dcim.device", "ipam.prefix", "ipam.vlan", "ipam.vlangroup", "dcim.rack"]}
POST /api/dcim/locations/
{"name": "site-a", "location_type": "Site", "parent": "<region-uuid>", "status": "Active", "tenant": "<tenant-uuid>"}
```

Rules enforced: a Location's type must match its parent's type (or the type's parent); a root type's Locations have no parent; names are unique per parent (`unique_together = [["parent", "name"]]`); a
Device at a Location whose type lacks `dcim.device` fails with "Devices may not associate to locations of type".

Gotcha: a Location's `location_type` can never be changed, a type with Locations cannot change parent, and a nestable type cannot be made non-nestable while nested Locations exist. Plan the tree
before loading data. `LOCATION_LIST_DEFAULT_MAX_DEPTH` limits the default list view for deep trees.

Source: `nautobot/dcim/models/locations.py:34-48,81-101,126,218,272-333`, `nautobot/dcim/models/devices.py:755`, `nautobot/dcim/api/serializers.py:242-251`;
`docs/user-guide/core-data-model/dcim/locationtype.html`, `docs/user-guide/core-data-model/dcim/location.html`.

## 2. Tenancy

Decision: a Tenant is who the object is for (customer, programme, business unit); Tenant Groups form a tree for grouping tenants. Use Tenant, not a tag, when permissions or uniqueness should follow
ownership.

```json
POST /api/tenancy/tenant-groups/   {"name": "Customers", "parent": null}
POST /api/tenancy/tenants/         {"name": "customer-a", "tenant_group": "<group-uuid>"}
```

Gotcha: with the default `DEVICE_UNIQUENESS = "location_tenant_name"`, two Devices may share a name if their Location or Tenant differs, so a name alone does not identify a Device. Other values:
`"name"` (globally unique) and `"none"`. It is a Constance setting (Admin > Config) as well as a config key.

Source: `nautobot/tenancy/models.py:18,40-55`, `nautobot/dcim/choices.py:164-175`, `nautobot/core/settings.py:863-869`, `nautobot/dcim/models/devices.py:700-712`.

## 3. Platforms and network_driver

Decision: set `network_driver` to the netutils normalised name (Netmiko-style, for example `cisco_ios`) on every Platform; consumers read the per-library name from `network_driver_mappings`, so one
field serves Ansible, NAPALM, Netmiko, Scrapli, pyATS, ntc-templates and hier_config.

```json
POST /api/dcim/platforms/
{"name": "Cisco IOS", "manufacturer": "Cisco", "network_driver": "cisco_ios", "napalm_driver": "ios"}
```

netutils 1.18.0 maps `cisco_ios` to: `ansible` `cisco.ios.ios`, `napalm` `ios`, `netmiko` `cisco_ios`, `scrapli` `cisco_iosxe`, `pyats` `iosxe`, `ntc_templates` `cisco_ios`, `netutils_parser`
`cisco_ios`, `hier_config` `ios` (137 normalised names in all).

| Consumer                       | What it reads                                                                       |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| Golden Config 3.0.7 compliance | `platform.network_driver_mappings["netutils_parser"]` to parse config sections      |
| Golden Config remediation      | `network_driver_mappings["hier_config"]`                                            |
| Golden Config Jinja path       | `jinja_path_template`, e.g. `{{obj.platform.network_driver}}.j2`                    |
| nornir-nautobot 4.4.2          | inventory sets Nornir `platform` to `platform.network_driver`; dispatcher by driver |
| Ansible `inventory` plugin     | `platforms` group names from each platform's `network_driver`                       |

Unknown or vendor-private drivers: add them with the `NETWORK_DRIVERS` setting (also editable in Admin > Config), keyed by tool:

```python
NETWORK_DRIVERS = {"netmiko": {"vendor_os": "linux"}, "netutils_parser": {"vendor_os": "linux"}}
```

Gotcha: `napalm_driver` and `napalm_args` are stored on the Platform and are not derived from `network_driver`. A driver missing from netutils returns an empty mapping silently, so Golden Config then
has no parser for that platform.

Source: `nautobot/dcim/models/devices.py:421-477`, `nautobot/dcim/utils.py:89-123`, `nautobot/core/settings.py:936-945`; `nautobot_golden_config/models.py:72,205,605`;
`nornir_nautobot/plugins/inventory/nautobot.py:29`; `nautobot-ansible` 6.3.0 `plugins/inventory/inventory.py:830-833`; `netutils.lib_mapper.NAME_TO_ALL_LIB_MAPPER` read in the container;
`docs/user-guide/core-data-model/dcim/platform.html`.

## 4. Manufacturers, Device Families, Device Types, Devices

Decision: one Device Type per orderable hardware model (`model` is unique per Manufacturer); Device Family is an optional grouping of related types; Role and Status say what a Device does and where it
is in its life.

```json
POST /api/dcim/device-types/
{"manufacturer": "Cisco", "model": "C9300-48P", "device_family": "Catalyst 9300", "u_height": 1}
POST /api/dcim/devices/
{"name": "sw1", "device_type": "<uuid>", "role": "Access Switch", "status": "Active", "location": "<site-uuid>",
 "platform": "Cisco IOS", "serial": "FOC0000X000", "software_version": "<version-uuid>"}
```

Gotcha: Device needs `device_type`, `role`, `status` and `location`. `primary_ip4` can only be set to an address already assigned to one of the device's interfaces ("is not assigned to this device").
Interface templates on the Device Type are copied only when the Device is created.

Source: `nautobot/dcim/models/devices.py:164-215` (DeviceType), `:495-652` (Device fields), `:825-848` (primary IP checks), `:916-935` (components created only when new);
`docs/user-guide/core-data-model/dcim/devicefamily.html`,
`docs/user-guide/core-data-model/dcim/devicetype.html`.

> **Learned 2026-10-08** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: one deployment's REST API, an interface template added to a Device Type after a Device of that type existed: the Device's interface list did not gain it; nautobot/dcim/models/device_component_templates.py lines 399-414 (`InterfaceTemplate.instantiate`) in the installed source · Falsifier: a 3.2.x Device that gains an interface when a template is added to its existing Device Type
> Adding an interface template to a Device Type changes only Devices created afterwards; existing Devices keep their interfaces. Back-fill them with `scripts/nautobot_template_sync.py` (plan, then `--apply`), which creates each missing interface as instantiation would: name, label, type, port_type, mgmt_only, speed, duplex and description from the template, status Active. An interface already present by name is left as it is.

> **Learned 2026-10-08** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: one deployment's REST API (`/dcim/interfaces/?...&depth=1` returned no `tagged_vlans` on a
> trunk that carries twelve; the same call with `exclude_m2m=false` returned them) · Falsifier: a 3.2.x list view that includes many-to-many fields by default
> REST **list** views leave many-to-many fields (`tagged_vlans`, tags and the like) out unless the request adds `exclude_m2m=false`. Reading a trunk's VLANs
> from a list call without it makes every trunk look empty; add the flag, or read the object by its own URL.

> **Learned 2026-10-08** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: one deployment's cable trace API (`/dcim/interfaces/<id>/trace/`) on a switch port
> cabled to a device's front port mapped to a rear port cabled to a Circuit termination · Falsifier: a trace that crosses a device between two interfaces
> A cable trace follows Cables and crosses a device only through a front port mapped to a rear port (a pass-through); it ends at any interface, never
> starts on a virtual interface (a VLAN interface cannot take a Cable) and never crosses a switch. To show a path that runs through a VLAN interface or a
> switch, assemble it from Relationships, Cables and 802.1Q membership (for example an app panel), and model a pass-through box (a carrier's NTD) with
> front and rear ports rather than two interfaces.

> **Learned 2026-10-08** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: installed `nautobot/core/ui/object_detail.py` (`Panel.render_body_content`) and
> `nautobot/core/templatetags/helpers.py` (`render_markdown`: Markdown with `fenced_code` and `tables`, then `clean_html`) · Falsifier: a 3.2.x `Panel`
> without `render_body_content`
> An app's `TemplateExtension.object_detail_panels` can carry a `Panel` subclass that overrides `render_body_content(context)` and returns
> `render_markdown(text)`: a computed Markdown table with links renders sanitised, built when the page opens (nothing stored). Job log messages render
> Markdown too.

## 5. Interfaces: modes, VLANs and LAGs

Decision: `type` says what the port is (`1000base-t`, `10gbase-x-sfpp`, `ieee802.11ax`, `virtual`, `lag`, `bridge`); `mode` says how it carries VLANs: `access`, `tagged` or `tagged-all`.

```json
POST /api/dcim/interfaces/
{"device": "<uuid>", "name": "Port-channel1", "type": "lag", "status": "Active"}
POST /api/dcim/interfaces/
{"device": "<uuid>", "name": "GigabitEthernet1/0/1", "type": "1000base-t", "status": "Active", "lag": "<lag-uuid>",
 "mode": "tagged", "untagged_vlan": "<vlan-uuid>", "tagged_vlans": ["<vlan-uuid>", "<vlan-uuid>"], "mac_address": "00:00:5E:00:53:01"}
```

| Rule                                                                | Enforced by          |
| ------------------------------------------------------------------- | -------------------- |
| `untagged_vlan` needs some `mode`                                   | model `clean()`      |
| `tagged_vlans` need `mode: tagged`; clear them before changing mode | REST serializer      |
| A VLAN must be global or at the device's Location or an ancestor    | serializer and model |
| LAG members on the same device, or the same Virtual Chassis         | model `clean()`      |
| Only physical interfaces take cables, `port_type`, `duplex`         | model `clean()`      |
| `speed` is Kbps; not valid on LAG, virtual or wireless types        | model `clean()`      |

Gotcha: `tagged-all` carries every VLAN, so do not also list `tagged_vlans`. An Interface belongs to a Device or a Module, never both.

Source: `nautobot/dcim/choices.py:778-850,1147-1156`, `nautobot/dcim/models/device_components.py:1037-1074,1197-1440`, `nautobot/dcim/api/serializers.py:712-768`;
`docs/user-guide/core-data-model/dcim/interface.html`.

> **Learned 2026-10-08** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: nautobot/dcim/choices.py lines 845, 850, 1028 and 1033 in the installed source; eight interfaces and one template created with `ieee802.11ac` over REST on one deployment · Falsifier: a 3.2.x POST of an interface or interface template with type `ieee802.11ac` or `other-wireless` that is refused
> A host's on-board radio (a Linux box's `wlan0`) is a physical interface with a wireless type, on the Device and on its type's interface template alike: `ieee802.11ac` (or the standard the radio runs), or `other-wireless` when the standard is not known. Decide "wireless" from what the host reports (`/sys/class/net/<nic>/wireless` exists), not from the name, and never default it to a copper type.

## 6. VLANs and VLAN Groups

Decision: per the docs, model a distinct VLAN per Location when sites reuse the same VID for the same purpose; one VLAN linked to several Locations only for a genuinely stretched layer 2. A VLAN Group
(optionally at one Location) enforces unique VID and name and can constrain `range`.

```json
POST /api/ipam/vlan-groups/  {"name": "site-a", "location": "<site-uuid>", "range": "1-999"}
POST /api/ipam/vlans/        {"vid": 30, "name": "wifi", "status": "Active", "vlan_group": "<group-uuid>", "location": "<site-uuid>"}
POST /api/ipam/vlan-location-assignments/  {"vlan": "<vlan-uuid>", "location": "<other-site-uuid>"}
GET  /api/ipam/vlan-groups/<uuid>/available-vlans/      (POST with name and status creates the next free VID)
```

Gotcha: `locations` is read-only on the VLAN serializer; `location` is a write-only shortcut for one Location, and reading `vlan.location` raises when there are several. A VLAN Group's Location type
must allow `ipam.vlangroup`.

Source: `nautobot/ipam/models.py:1049-1063,2270-2321,2354,2478-2483`, `nautobot/ipam/api/serializers.py:118-140`; `docs/user-guide/core-data-model/ipam/vlan.html`,
`docs/user-guide/core-data-model/ipam/vlangroup.html`.

## 7. Prefix types and Namespaces

Decision: `container` for aggregates that group subnets, `network` (default) for real subnets with hosts, `pool` for ranges inside a network where every address is usable. Prefixes are unique per
Namespace; the default Namespace is `Global`.

```json
POST /api/ipam/prefixes/  {"prefix": "198.51.100.0/24", "type": "container", "status": "Active", "namespace": "Global"}
POST /api/ipam/prefixes/  {"prefix": "198.51.100.0/26", "type": "network", "status": "Active", "location": "<site-uuid>"}
```

| Type      | First and last IPv4 address usable | Utilisation counts |
| --------- | ---------------------------------- | ------------------ |
| container | no                                 | child prefixes     |
| network   | no                                 | IP addresses       |
| pool      | yes                                | IP addresses       |

Gotcha: "Nautobot does not strictly enforce this hierarchy": a network inside a network is accepted. CSV import ignores `vrfs` and `locations` columns; use `prefix-location-assignments` or the VRF
assignment endpoints afterwards.

Source: `nautobot/ipam/choices.py:31-40`, `nautobot/ipam/models.py:189-194,643-662,1622-1652`, `nautobot/ipam/api/serializers.py:198-221`; `docs/user-guide/core-data-model/ipam/prefix.html`.

## 8. IP addresses and interface assignment

Decision: an IP Address lives in a Namespace under its closest parent Prefix; attach it to interfaces through `ip-address-to-interface`, which is many-to-many and carries per-assignment flags.

```json
POST /api/ipam/ip-addresses/            {"address": "198.51.100.10/26", "status": "Active", "type": "host", "namespace": "Global"}
POST /api/ipam/ip-address-to-interface/ {"ip_address": "<ip-uuid>", "interface": "<interface-uuid>", "is_primary": true}
PATCH /api/dcim/devices/<uuid>/         {"primary_ip4": "<ip-uuid>"}
```

IP `type`: `host`, `dhcp`, `slaac`. Assignment flags: `is_source`, `is_destination`, `is_default`, `is_preferred`, `is_primary`, `is_secondary`, `is_standby`. Use `vm_interface` instead of `interface`
for virtual machines.

Gotcha: every IP needs a parent Prefix; without one the create fails with "No suitable parent Prefix ... exists in Namespace". Create needs `namespace` or `parent`. Keep the address mask equal to the
subnet's mask; Nautobot stores what it is given.

Source: `nautobot/ipam/models.py:115-132,1684,1715,1823-1842,1913-1950`, `nautobot/ipam/choices.py:93-101`, `nautobot/ipam/api/serializers.py:315-336`;
`docs/user-guide/core-data-model/ipam/ipaddress.html`.

## 9. Virtual Chassis

Decision: use a Virtual Chassis when several boxes share one control plane (a switch stack); use a Device Redundancy Group when each keeps its own; use modules for a chassis with line cards.

```json
POST /api/dcim/virtual-chassis/  {"name": "stack-1", "domain": ""}
PATCH /api/dcim/devices/<uuid>/  {"virtual_chassis": "<vc-uuid>", "vc_position": 1, "vc_priority": 15}
PATCH /api/dcim/virtual-chassis/<vc-uuid>/  {"master": "<device-uuid>"}
```

Gotcha: a member needs `vc_position` (unique within the chassis); the master must already be a member. Interfaces are not renumbered when a device joins: member 3 still shows `.../1/0/x` until
bulk-renamed. A LAG may span members of one Virtual Chassis.

Source: `nautobot/dcim/models/devices.py:651-652,712,879-881,1248-1265`; `docs/user-guide/core-data-model/dcim/virtualchassis.html`.

## 10. Modules and module bays

Decision: model removable hardware (line cards, supervisors, transceivers) as Modules in Module Bays; a Module Type's component templates create its interfaces, which may use the bay `position` in
their names.

```json
POST /api/dcim/module-bays/  {"parent_device": "<device-uuid>", "name": "Slot 1", "position": "1"}
POST /api/dcim/modules/      {"module_type": "<type-uuid>", "parent_module_bay": "<bay-uuid>", "status": "Active", "serial": "ABC123"}
POST /api/dcim/modules/      {"module_type": "<type-uuid>", "location": "<store-uuid>", "status": "Active"}
```

Gotcha: a Module has either `parent_module_bay` (installed) or `location` (spare in stock), never both. A bay assigned a Module Family accepts only Module Types of that family.  A Module Bay has
`parent_device` or `parent_module`.

Source: `nautobot/dcim/models/devices.py:1981-2022,2120-2138`, `nautobot/dcim/models/device_components.py:1985-1999`; `docs/user-guide/core-data-model/dcim/module.html`,
`docs/user-guide/core-data-model/dcim/modulebay.html`.

## 11. Cables and paths

Decision: a Cable joins two physical terminations (interface, front/rear port, console, power, circuit termination); Nautobot traces end-to-end paths through patch panels and circuits from cables
whose status is `Connected`.

```json
POST /api/dcim/cables/
{"termination_a_type": "dcim.interface", "termination_a_id": "<uuid>", "termination_b_type": "dcim.interface", "termination_b_id": "<uuid>",
 "status": "Connected", "type": "cat6"}
POST /api/dcim/cables/   (3.2 shape, also for breakout cables)
{"terminations": {"a1": {"object_type": "dcim.interface", "id": "<uuid>"}, "b1": {"object_type": "dcim.interface", "id": "<uuid>"}}, "status": "Connected"}
```

Gotcha: a path is reachable only if every cable on it is `Connected`; do not rename or delete that Status. Virtual and wireless interfaces cannot be cabled. After bulk imports, `nautobot-server
trace_paths` rebuilds missing paths (`post_upgrade` runs it).

Source: `nautobot/dcim/models/cables.py:471`, `nautobot/dcim/api/serializers.py:896-1110`, `nautobot/core/management/commands/post_upgrade.py:119`; `docs/user-guide/core-data-model/dcim/cable.html`.

> **Learned 2026-10-08** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: one deployment's REST API: four interface-to-interface Cables created with the `termination_a_type`/`termination_a_id` shape and status Connected, each interface's `cable` and `connected_endpoint` read back; `GET /api/dcim/interfaces/?cabled=true` answered HTTP 400 "Unknown filter field" · Falsifier: a 3.2.x interface list that accepts `cabled`
> The legacy two-ended POST shape still creates a Cable on 3.2.3, and the far interface shows as `connected_endpoint` at once. There is no `cabled` filter on interfaces: to count a site's cables, list its interfaces (`?location=<id>`) and collect the distinct `cable` ids. Record a cable only on evidence of the far end, such as the exact MAC of a known physical interface in a switch's MAC table.

## 12. Contacts, Teams, Statuses, Roles, Tags, software

Decision: attach people with Contact or Team associations rather than free-text fields; keep Statuses for lifecycle and Roles for function; Tags for cross-cutting labels only.

```json
POST /api/extras/contact-associations/
{"contact": "<contact-uuid>", "associated_object_type": "dcim.location", "associated_object_id": "<uuid>", "role": "<role-uuid>", "status": "Active"}
POST /api/extras/statuses/  {"name": "Staged", "color": "2196f3", "content_types": ["dcim.device"]}
POST /api/extras/roles/     {"name": "Access Switch", "color": "4caf50", "content_types": ["dcim.device"]}
POST /api/dcim/software-versions/  {"platform": "Cisco IOS", "version": "17.9.4", "status": "Active", "long_term_support": true}
POST /api/dcim/software-image-files/  {"software_version": "<uuid>", "image_file_name": "image.bin", "status": "Active"}
```

Gotcha: a Status, Role or Tag must list the model's content type or it is rejected for that model. A Contact Association takes exactly one of `contact` or `team`, with a role and status.
 Software Image File also takes `image_file_checksum`, `hashing_algorithm`, `image_file_size`, `default_image` and `external_integration`.

Source: `nautobot/extras/models/contacts.py:49-125`, `nautobot/extras/models/statuses.py:23-46`, `nautobot/extras/models/roles.py:21`, `nautobot/extras/models/tags.py:32,53`,
`nautobot/dcim/models/devices.py:1401-1433,1500-1514`; `docs/user-guide/core-data-model/extras/contact.html`, `docs/user-guide/core-data-model/dcim/softwareversion.html`,
`docs/user-guide/core-data-model/dcim/softwareimagefile.html`.
