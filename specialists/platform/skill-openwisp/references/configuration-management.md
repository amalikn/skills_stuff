---
Title: OpenWISP configuration management
Category: skill-reference
Status: current
Authority: Installed OpenWISP images 26.09.0 (openwisp-controller 1.3, netjsonconfig 1.3) source and the versioned 26.09 documentation; the cited lines win over this summary
Scope: Templates, configuration variables, netjsonconfig backends, config status, checksum fetch, the openwisp-config agent, auto-registration, device groups, VPN automation and subnet division
Last reviewed: 2026-10-05
Summary: How OpenWISP builds, versions and delivers device configuration, verified against the installed 26.09.0 source, and what none of it does for closed-firmware devices.
---

# OpenWISP configuration management

Verified against: OpenWISP images 26.09.0 (openwisp-controller 1.3, netjsonconfig 1.3, openwisp-ipam 1.3.1, Django 5.2.17, Python 3.14), checked 2026-10-05.

Module status in the checked install: `openwisp_controller.config`, `.pki`, `.geo`, `.connection` and `.subnet_division` are all in `INSTALLED_APPS` (enabled); `openwisp_ipam` is enabled. The
openwisp-config agent is an OpenWrt package and is not part of the server images: its behaviour below comes from the 26.09 agent docs, not from installed source.

Citations name the installed file as `$P/<module>/<file>:<line>`, where `$P` is `/usr/local/lib/python3.14/site-packages` inside `openwisp-dashboard:26.09.0`. Anything not read from source or a
versioned 26.09 page is marked UNVERIFIED.

## Summary

| Job                          | Use                              | Key syntax                                           | Trap                                                              | Section |
| ---------------------------- | -------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------- | ------- |
| Reuse config across devices  | Template (generic or VPN-client) | `type`, `default`, `required`,                       | `required` forces `default`; tags apply only at registration      | [1](#1-templates) |
|                              |                                  |   `tags`, `default_values`                           |                                                                   |         |
| Per-device values            | Configuration variables          | `{{ name }}`; device > group > org > global >        | Only bare `{{ word }}`; an unknown variable is left in the output | [2](#2-configuration-variables) |
|                              |                                  |   template defaults                                  |                                                                   |         |
| Render a device config       | netjsonconfig backend            | `netjsonconfig.OpenWrt`, `netjsonconfig.OpenWisp`    | Only OpenWrt-family firmware has a backend                        | [3](#3-backends-and-the-netjson-document) |
| Know if a device took        | `Config.status`                  | `modified`, `applied`, `error`,                      | `applied` is reported by the agent, not observed by the server    | [4](#4-config-status-and-the-fetch-cycle) |
|   the config                 |                                  |   `deactivating`, `deactivated`                      |                                                                   |         |
| Put the agent on a device    | openwisp-config                  | `/etc/config/openwisp`: `url`,                       | `merge_config` keeps local sections; `unmanaged` protects them    | [5](#5-the-openwisp-config-agent) |
|                              |                                  |   `shared_secret`, `consistent_key`                  |                                                                   |         |
| Let devices self-register    | Org shared secret                | `POST /controller/device/register/`                  | Consistent key = md5 of MAC (or hardware_id) plus secret          | [6](#6-auto-registration) |
| Per-group templates and data | Device group                     | `templates`, `context`, `meta_data`                  | `meta_data` never reaches the config; `context` does              | [7](#7-device-groups) |
| Management tunnels           | VPN server + VPN-client template | `auto_cert` ("automatic tunnel provisioning")        | WireGuard/ZeroTier need a server-side updater, not just           | [8](#8-vpn-automation) |
|                              |                                  |                                                      |   the template                                                    |         |
| Per-device subnets and IPs   | Subnet division rule             | `<label>_subnet<N>_ip<M>` variables                  | Size and subnet count cannot change after creation                | [9](#9-subnet-division) |
| Closed firmware              | Inventory and monitoring only    | Device without Config                                | No backend, no agent, no fetch: nothing in sections 1-9 applies   | [10](#10-closed-firmware-devices) |

## Contents

- [Summary](#summary)
- [1. Templates](#1-templates)
- [2. Configuration variables](#2-configuration-variables)
- [3. Backends and the NetJSON document](#3-backends-and-the-netjson-document)
- [4. Config status and the fetch cycle](#4-config-status-and-the-fetch-cycle)
- [5. The openwisp-config agent](#5-the-openwisp-config-agent)
- [6. Auto-registration](#6-auto-registration)
- [7. Device groups](#7-device-groups)
- [8. VPN automation](#8-vpn-automation)
- [9. Subnet division](#9-subnet-division)
- [10. Closed-firmware devices](#10-closed-firmware-devices)

## 1. Templates

Decision: put anything shared by more than one device in a template; flag organisation-wide baselines `default`, non-removable baselines `required`, and role-specific sets with `tags`.

```json
{
  "name": "mesh-baseline",
  "organization": "<org-uuid or null for shared>",
  "type": "generic",
  "backend": "netjsonconfig.OpenWrt",
  "default": true,
  "required": false,
  "tags": ["mesh"],
  "default_values": {"wlan0_ssid": "Example-WiFi"},
  "config": {"interfaces": [{"name": "wlan0", "type": "wireless",
             "wireless": {"mode": "access_point", "radio": "radio0", "ssid": "{{ wlan0_ssid }}"}}]}
}
```

- `type` is `generic` or `vpn` (VPN-client). A `vpn` template must name a `vpn`; on any other type `vpn` and `auto_cert` are cleared on save.
- `required` implies `default`: `clean()` sets `default = True` whenever `required` is set. Required templates are assigned before default ones, so a default template can override them.
- A template with no organisation is shared: it is available to every organisation, and a shared `default` template lands on every device in the system.
- Template order matters: a template assigned later overrides an earlier one, and the device's own `config` overrides all templates.
- REST: `/api/v1/controller/template/`, and `/api/v1/controller/template/<pk>/configuration/` downloads the rendered template.

Gotcha: `tags` are matched only when a device registers (`add_tagged_templates` runs inside the register view). Tagging a template later does not reach devices that already exist.

Source: `$P/openwisp_controller/config/base/template.py:25` (`TYPE_CHOICES`), `:42-96` (fields), `:215-247` (`clean`); `$P/openwisp_controller/config/controller/views.py:345-356` (tags at
registration); `$P/openwisp_controller/config/api/urls.py`; https://openwisp.io/docs/26.09/controller/user/templates.html (snapshot `documents/openwisp-26.09-controller-templates.html`).

## 2. Configuration variables

Decision: keep per-device differences in variables, never by copying a template into a device's own config.

```json
{"interfaces": [{"name": "wlan0", "type": "wireless",
  "wireless": {"mode": "access_point", "radio": "radio0", "ssid": "{{ wlan0_ssid }}"}}]}
```

Precedence, highest first, as the 26.09 docs state and the installed code builds it:

| Rank | Source                      | Where it is set                                                                    |
| ---- | --------------------------- | ---------------------------------------------------------------------------------- |
| 1    | Device variables            | `Config.context` ("Configuration variables" on the device)                         |
| 2    | Predefined device variables | `id`, `key`, `name`, `mac_address` (plus `hardware_id` when `HARDWARE_ID_ENABLED`) |
| 3    | Group variables             | `DeviceGroup.context`                                                              |
| 4    | Organisation variables      | `OrganizationConfigSettings.context`                                               |
| 5    | Global variables            | `OPENWISP_CONTROLLER_CONTEXT` Django setting                                       |
| 6    | Template default values     | `Template.default_values`                                                          |
| 7    | System-defined              | VPN keys, IPs and subnet-division values, shown read-only in the admin             |

Gotcha: netjsonconfig substitutes only the pattern `\{\{\s*(\w*)\s*\}\}`: a bare word in double braces. Filters, dotted names and expressions are not Jinja here, and a variable missing from every
context is left in the rendered output as literal `{{ name }}` with no error. Give every template variable a `default_values` entry so validation and rendering never see a gap.

Source: `$P/netjsonconfig/utils.py:102-135` (`var_pattern`, `evaluate_vars`); `$P/openwisp_controller/config/base/config.py:1030-1066` (`get_context` order);
`$P/openwisp_controller/config/base/base.py:174-175` (global `CONTEXT`), `:221-243` (template contexts merged first); https://openwisp.io/docs/26.09/controller/user/variables.html (snapshot
`documents/openwisp-26.09-controller-variables.html`).

## 3. Backends and the NetJSON document

Decision: a device config is a NetJSON DeviceConfiguration dictionary rendered by a netjsonconfig backend; pick `netjsonconfig.OpenWrt` unless the device runs the legacy OpenWISP 1.x firmware.

```python
# OPENWISP_CONTROLLER_BACKENDS default (setting name: OPENWISP_CONTROLLER_BACKENDS)
(("netjsonconfig.OpenWrt", "OpenWRT"),
 ("netjsonconfig.OpenWisp", "OpenWISP Firmware 1.x"))
```

A minimal DeviceConfiguration and its render, run read-only with `python -c` in the dashboard container on 2026-10-05:

```python
from netjsonconfig import OpenWrt
c = {"general": {"hostname": "{{ name }}", "timezone": "UTC"},
     "interfaces": [{"name": "lan", "type": "ethernet",
                     "addresses": [{"proto": "static", "family": "ipv4", "address": "192.0.2.1", "mask": 24}]}],
     "files": [{"path": "/etc/banner.txt", "mode": "0644", "contents": "managed by {{ org }}\n"}]}
print(OpenWrt(c, context={"name": "ap-01", "org": "example"}).render())
```

```text
package system
config system 'system'
	option hostname 'ap-01'
	option timezone 'UTC'
	option zonename 'UTC'
package network
config interface 'lan'
	option device 'lan'
	option ipaddr '192.0.2.1'
	option netmask '255.255.255.0'
	option proto 'static'
# path: /etc/banner.txt
```

- Top-level keys used above: `general`, `interfaces`, `files`; the OpenWrt schema also has `radios`, `routes`, `dns_servers` and more. `OpenWisp` subclasses `OpenWrt` and adds only `tc_options` plus a
  radio `disabled` default (read from the installed classes).
- `files` is the escape hatch for anything the schema does not model: the backend writes the file as given.
- `DEFAULT_BACKEND` is the first entry of `BACKENDS`; `CONFIG_BACKEND_FIELD_SHOWN` hides the field in the admin.

Gotcha: the backend list is the whole support matrix. A device whose firmware has no netjsonconfig backend cannot use templates, variables or the fetch cycle (section 10).

Source: `$P/openwisp_controller/config/settings.py:11-29`, `:40`; `$P/netjsonconfig/backends/openwisp/openwisp.py:10-33`; live render via `python -c` in `wc-local-openwisp-dashboard-1` (read-only, no
database access), 2026-10-05.

## 4. Config status and the fetch cycle

Decision: treat `Config.status` as the agent's self-report, and the checksum as the change detector.

| Status         | Meaning (installed help text)                                                | Set by                                       |
| -------------- | ---------------------------------------------------------------------------- | -------------------------------------------- |
| `modified`     | Changed in OpenWISP, not yet applied                                         | Server, on any change that alters the render |
| `applied`      | Applied successfully                                                         | Agent `report-status`                        |
| `error`        | Caused issues and was rolled back; `error_reason` holds the device's message | Agent `report-status`                        |
| `deactivating` | Device deactivated; configuration being removed                              | Server, `deactivate()`                       |
| `deactivated`  | Configuration removed from the device; further management refused            | Agent report while `deactivating`, or server |

The device-facing endpoints (no `/api/v1/` prefix; the device key is the credential):

```text
GET  /controller/device/checksum/<uuid>/?key=<device-key>&management_ip=<ip>   -> md5 text
GET  /controller/device/download-config/<uuid>/?key=<device-key>                -> <name>.tar.gz
POST /controller/device/update-info/<uuid>/     key, os, model, system
POST /controller/device/report-status/<uuid>/   key, status=applied|error[, error_reason]
POST /controller/device/register/               secret, name, mac_address, backend[, key, hardware_id, tags]
```

- The checksum is `md5` of the generated tar.gz (`generate().getvalue()`); it is cached for 30 days and invalidated on change.
- `report-status` accepts any of the five statuses; while the config is `deactivating` any report becomes `deactivated`.
- A deactivated device gets `403 error: device deactivated` from `update-info` and `register`; `GetDeviceView` returns 404 once the config is `deactivated`.

Gotcha: every checksum request rewrites `management_ip` from its query parameter. An agent without `management_interface` sends none, so a `management_ip` set by hand over REST is cleared on the next
poll, and push operations then have no address (see [connections and firmware](connections-and-firmware.md)).

Source: `$P/openwisp_controller/config/base/config.py:68-79` (statuses), `:929-953` (`deactivate`); `$P/openwisp_controller/config/base/base.py:35` (30-day cache), `:269-274` (checksum);
`$P/openwisp_controller/config/utils.py:70-87` (`update_last_ip`), `:118-178` (URLs); `$P/openwisp_controller/config/controller/views.py:153-171`, `:205-219`, `:221-258`, `:261-294`;
https://openwisp.io/docs/26.09/controller/user/device-config-status.html.

## 5. The openwisp-config agent

Decision: install the agent on every OpenWrt device you want configured; set at least `url`, `shared_secret` and `management_interface`.

```sh
opkg update
opkg install openwisp-config
```

```text
# /etc/config/openwisp
config controller 'http'
    option url 'https://openwisp.example'
    option verify_ssl '1'
    option shared_secret '<shared-secret>'
    option consistent_key '1'
    option management_interface 'wg0'
    option tags 'mesh'
    list unmanaged 'network.loopback'
    list unmanaged 'system.@led'
```

```sh
/etc/init.d/openwisp-config restart
```

Options worth knowing (26.09 agent docs, defaults in brackets): `interval` [120 s], `merge_config` [1], `test_config` [1], `test_retries` [10], `test_script`, `hardware_id_script`, `hardware_id_key`
[1], `bootup_delay` [10 s random], `checksum_max_retries` [5], `default_hostname`, `mac_interface` [eth0].

- `merge_config 1`: remote options overwrite local ones, local-only options survive, replaced files are backed up and restored when the remote change is removed.
- `test_config 1`: after applying, the agent must reach the controller again or it restores the backup and reports `error`.
- `unmanaged` sections are never overwritten; `@type` means every section of that type.
- The 26.09 docs recommend the builds on downloads.openwisp.io because the OpenWrt feed is "not always up to date".

Gotcha: after `checksum_max_retries` 404s the agent assumes the device was deleted and exits; procd then respawns it `respawn_retry` times. Deleting and recreating a device in OpenWISP therefore needs
the agent to re-register with the same key (consistent key) or a manual `uuid`/`key` change on the device.

Source: https://openwisp.io/docs/26.09/openwrt-config-agent/user/settings.html (snapshot `documents/openwisp-26.09-openwrt-config-agent-settings.html`);
https://openwisp.io/docs/26.09/openwrt-config-agent/user/quickstart.html. Agent source not installed in the server images: UNVERIFIED against agent code.

## 6. Auto-registration

Decision: let devices register themselves with the organisation's shared secret, and keep `consistent_key` on so a reflashed device reclaims its record.

```text
POST /controller/device/register/
secret=<shared-secret>&name=ap-01&mac_address=00:00:5e:00:53:01&backend=netjsonconfig.OpenWrt&key=<md5>&tags=mesh
```

```text
registration-result: success
uuid: <hex>
key: <device-key>
hostname: ap-01
is-new: 1
```

| Setting                                          | Default | Effect                                                                             |
| ------------------------------------------------ | ------- | ---------------------------------------------------------------------------------- |
| `OPENWISP_CONTROLLER_REGISTRATION_ENABLED`       | `True`  | Global switch; per organisation also `registration_enabled` on its config settings |
| `OPENWISP_CONTROLLER_CONSISTENT_REGISTRATION`    | `True`  | Look the device up by the key it sends                                             |
| `OPENWISP_CONTROLLER_REGISTRATION_SELF_CREATION` | `True`  | `False` returns 404 "please create it first" for unknown keys                      |
| `OPENWISP_CONTROLLER_HARDWARE_ID_ENABLED`        | `False` | Key base becomes `hardware_id` instead of MAC                                      |

- Server-side key: `md5("<mac_address or hardware_id>+<shared_secret>")` when consistent registration is on; a random key otherwise.
- On re-registration only `name`, `os`, `model` and `system` are updated; a name equal to the MAC (the agent's default for `OpenWrt` hostnames) does not overwrite a set name.
- Errors: `403 error: unrecognized secret`, `403 error: registration disabled`, `400` with validation messages.

Gotcha: the key is derived from the shared secret, so rotating an organisation's `shared_secret` changes the key every device will compute; existing devices then no longer match their records on
re-registration (inference from the key formula; UNVERIFIED against a live rotation). Treat the secret as fixed per organisation.

Source: `$P/openwisp_controller/config/controller/views.py:297-475`; `$P/openwisp_controller/config/base/device.py:229-239` (`generate_key`), `:286-295`;
`$P/openwisp_controller/config/settings.py:30-32`, `:42`; `$P/openwisp_controller/config/base/multitenancy.py:17-41` (`registration_enabled`, `shared_secret`, `context`).

## 7. Device groups

Decision: use a group for a set of devices that share templates and variables; keep integration data in `meta_data`.

```json
{
  "name": "outdoor-aps",
  "organization": "<org-uuid>",
  "templates": ["<template-uuid>"],
  "context": {"wlan0_ssid": "Example-Outdoor"},
  "meta_data": {"owner_ref": "example-123"}
}
```

- `templates` are assigned to member devices automatically and swapped out when a device changes group; default and required templates are excluded from the list.
- `context` feeds rank 3 of the variable precedence (section 2).
- `meta_data` is validated against `OPENWISP_CONTROLLER_DEVICE_GROUP_SCHEMA` (default `{"type": "object", "properties": {}}`) and is exposed over REST only.
- REST: `/api/v1/controller/group/`; `/api/v1/controller/cert/<common_name>/group/` finds a group from a certificate.

Gotcha: `meta_data` never reaches a device's configuration; put a value the config needs in `context`.

Source: `$P/openwisp_controller/config/base/device_group.py:21-75`; `$P/openwisp_controller/config/settings.py:55-57`; `$P/openwisp_controller/config/api/urls.py`;
https://openwisp.io/docs/26.09/controller/user/device-groups.html.

## 8. VPN automation

Decision: model the management tunnel as a VPN server object plus a VPN-client template with automatic tunnel provisioning, so OpenWISP allocates keys and addresses per device.

| Backend (`OPENWISP_CONTROLLER_VPN_BACKENDS`)      | Server side                                                  | Per-client allocation                  |
| ------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------- |
| `openwisp_controller.vpn_backends.OpenVpn`        | CA and server certificate in PKI (create or import)          | x509 client certificate and key        |
| `openwisp_controller.vpn_backends.Wireguard`      | WireGuard host plus an updater reached by `webhook_endpoint` | Key pair and an IP from the VPN subnet |
| `openwisp_controller.vpn_backends.VxlanWireguard` | As WireGuard                                                 | As WireGuard plus a VNI                |
| `openwisp_controller.vpn_backends.ZeroTier`       | Self-hosted ZeroTier controller; `auth_token` is its token   | Identity secret, member ID and an IP   |

Steps (WireGuard, from the 26.09 guide): create the server at `/admin/config/vpn/add/` with host, backend, subnet, `webhook_endpoint` and `auth_token`; deploy the server (the docs recommend the
`ansible-wireguard-openwisp` role); create a template with `type` VPN-client, the VPN selected and "Automatic tunnel provisioning" (`auto_cert`) checked; assign it to devices or flag it default.

- Auto-generated variables are suffixed with the VPN's hex UUID, e.g. `vpn_host_<pk>`, `public_key_<pk>`, `pvt_key_<pk>`, `ip_address_<pk>`, `server_ip_address_<pk>`, `vni_<pk>`, `network_id_<pk>`.
- A change on a WireGuard or ZeroTier server triggers `trigger_vpn_server_endpoint`, which calls the webhook with the auth token.
- The agent's `management_interface` must name the tunnel interface so `management_ip` is the tunnel address.

Gotcha: in this install the docker `openvpn` service is not running (only `VPN_DOMAIN` is set), and no WireGuard updater exists: creating the objects allocates keys but builds no tunnel.

Source: `$P/openwisp_controller/config/settings.py:19-29`; `$P/openwisp_controller/config/base/vpn.py:58-142` (fields), `:613-680` (`_get_auto_context_keys`), `:682-700` (`auto_client`);
`$P/openwisp_controller/config/tasks.py:126-159`; https://openwisp.io/docs/26.09/controller/user/wireguard.html (snapshot `documents/openwisp-26.09-controller-wireguard.html`),
https://openwisp.io/docs/26.09/controller/user/zerotier.html, https://openwisp.io/docs/26.09/controller/user/openvpn.html, https://openwisp.io/docs/26.09/user/vpn.html.

## 9. Subnet division

Decision: let a subnet division rule carve per-device subnets and IPs from a master subnet in openwisp-ipam; reference them through system-defined variables. Installed and enabled here.

| Rule type | Class                                                                                | Fires when                                                                  |
| --------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| `Device`  | `openwisp_controller.subnet_division.rule_types.device.DeviceSubnetDivisionRuleType` | A `Config` is created in the rule's organisation (also back-fills existing) |
| `VPN`     | `openwisp_controller.subnet_division.rule_types.vpn.VpnSubnetDivisionRuleType`       | A VPN-client template whose VPN uses the rule's master subnet is assigned   |

```text
# rule fields: label, master_subnet, size, number_of_subnets, number_of_ips
# variables for label "OW":
OW_subnet1           -> 198.51.100.0/28
OW_subnet1_ip1       -> 198.51.100.1
OW_prefixlen         -> 28
```

- The rule always belongs to an organisation and fires only for devices of that organisation, even with a shared subnet or template.
- A reserved subnet is created automatically; do not create child subnets by hand inside the master subnet.

Gotcha: `size` and `number_of_subnets` cannot change on an existing rule, and `number_of_ips` can only grow; the documented remedy is to delete the rule and create a new one, which re-provisions.

Source: `$P/openwisp_controller/subnet_division/settings.py`; `$P/openwisp_controller/subnet_division/base/models.py:28-45`; `$P/openwisp_controller/subnet_division/rule_types/base.py:276`, `:316`;
`$P/openwisp_controller/subnet_division/utils.py:1-23`; https://openwisp.io/docs/26.09/controller/user/subnet-division-rules.html (snapshot
`documents/openwisp-26.09-controller-subnet-division-rules.html`).

## 10. Closed-firmware devices

Decision: for a device whose firmware is not OpenWrt (no netjsonconfig backend and no openwisp-config agent), use OpenWISP for inventory and monitoring only, and keep configuration intent elsewhere.

- Such a device can exist without a `Config` object; templates, variables, groups' templates, VPN-client templates and subnet division all act on `Config` and so do nothing for it.
- No agent means no checksum poll: `last_ip` and `management_ip` change only when written over REST, `Config.status` never moves, and `update-info` is never called.
- Push and commands still need an SSH-reachable shell and a `management_ip` (see [connections and firmware](connections-and-firmware.md)); the stock update strategy signals the agent, so "update
  config" is meaningless without it.
- Extending the matrix means a new backend class registered in `OPENWISP_CONTROLLER_BACKENDS` plus a delivery path; that is a product-level build, not a setting.

Gotcha: a device record that looks "configured" in the admin because a default template was attached at creation proves nothing; check whether it has a backend the firmware can apply.

Source: `$P/openwisp_controller/config/settings.py:11-17`; `$P/openwisp_controller/config/controller/views.py:440-443` (a device without a Config is handled at registration);
`$P/openwisp_controller/connection/connectors/openwrt/ssh.py:10-33`. The "no fetch without an agent" conclusion follows from the endpoints in section 4 and is not separately tested.
