---
Title: rct site ATA (Dallas Delta DDC_VoIP-m)
Category: reference
Status: current
Authority: >-
  Read-only observations of live units over Teleport apn, 2026-10-08; vendor documents in vendor-sources-dallas-delta-20261008_1043/ stay authoritative for
  vendor claims.
Scope: The Dallas Delta Corp VoIP ATA behind the MikroTik switch at rct sites, reached from the SMC on 192.168.5.0/24
Last reviewed: 2026-10-08
Summary: >-
  Identity, address, management surface (web UI only, no SNMP, no SSH), SIP registration readout, which settings are site-unique, and the quirks seen when
  reading the rct site ATA.
---

# rct Site ATA — Dallas Delta DDC_VoIP-m

## Contents

- [Identity and placement](#identity-and-placement)
- [Management surface](#management-surface)
- [Settings and SIP registration](#settings-and-sip-registration)
- [Reading quirks and unreachable units](#reading-quirks-and-unreachable-units)
- [Vendor sources](#vendor-sources)

All facts VERIFIED-OBSERVED 2026-10-08, read-only from the site's SMC over Teleport apn, unless labelled otherwise. No PIN, password or SIP secret is recorded here.

## Identity and placement

- Dallas Delta Corp `DDC_VoIP-m`, firmware `042112`. Web page title `DDC_VoIP Login`; the page source carries the comment `Dallas Delta Corp VoIP telephone Feb 2009 ver2.0`.
- Address `192.168.5.253/24`, gateway `192.168.5.100` (the second address on the SMC's `bridge_500`, kept for this unit; `03_communication-flows.md`, rct Site Addressing).
- Cabled to the MikroTik switch's `ether4` (skill-mikrotik reads it from the bridge host table). 20-mile's unit is MAC `38:B1:9E:D0:02:14`.

## Management surface

- **Web UI only.** The login is a password-only form. The PIN was empty on every unit read (adjamarragu, alamirra, akwalirrumanja, alice-well, alkngarrija); treat that as a finding to fix, not a
  credential to rely on.
- **No SSH.** Telnet is closed on adjamarragu; on 20-mile the port is open but silent and drops the connection on the first keystroke.
- **No SNMP.** No answer to SNMP v2c with community `DDC_VoIP` or `public`, and the settings page has no SNMP setting. Only the later S11 generation sends SNMP traps (enterprise 45255; vendor manuals,
  VERIFIED_PRIMARY for S11 only). Monitor it by its web page or by SIP registration, not SNMP.

## Settings and SIP registration

- The settings page shows `Registered : Yes` or `Registered : No`: that is the unit's SIP registration state, readable without changing anything.
- Across five units (adjamarragu, alamirra, akwalirrumanja, alice-well, alkngarrija), 83 of 93 settings fields are identical. The site-unique ones are `user_number` and `auth_id` (the SIP number, for
  example `09990455`), `sip_proxy` (`125.213.160.7` at four sites, `sip00.mvp.symbionetworks.com` at alice-well), `syslog_ip`, `user_name` (set at alice-well only), and the volume settings. The
  phonebook is identical everywhere (button 1 = Emergency 000).
- A per-site template therefore needs only those few fields; the rest is a fleet-wide constant.
- Read and compare units with [`scripts/ata_settings_read.py`](../scripts/ata_settings_read.py) (`just ata_settings_read <proxy> <node>...`): read-only, empty PIN,
  secret-named fields dropped on the SMC, `Registered` shown per unit. A rerun on 2026-10-08 (adjamarragu, akwalirrumanja, alamirra) counted 92 named settings
  fields, 86 identical across the three, and found the digitmap differs too: entry `m003` is `1800xxxxxx` at akwalirrumanja and `1800xxxxxxxx` at the other two.

## Reading quirks and unreachable units

- The settings page declares 43 bytes more `Content-Length` than it sends. Python's `http.client` raises `IncompleteRead`; `curl` tolerates it. Catch the exception and keep the partial body.
- 20-mile's unit never answers HTTP. **Superseded 2026-10-20:** it answers; see "The S11 generation" below.
- aeroplane-1's unit drops the HTTP connection.
- kintore-smc01 is not registered in Teleport (`subsystem request failed`, twice), so its ATA could not be reached.

## The S11 generation (20-mile, 2026-10-20)

VERIFIED-OBSERVED 2026-10-20, read-only from 20-mile-smc01 over Teleport apn, one login with the empty PIN.

- 20-mile's ATA is a **DDC_VoIP-BIA** on firmware **s11.0920.04** (the vendor's S11 generation), MAC `38:b1:9e:d0:02:14`, at 192.168.5.253. It is not
  silent: its replies start with a blank line before the status line, so `curl` refuses them ("Received HTTP/0.9 when not allowed") unless given
  `--http0.9`, and Python's `http.client` refuses them too (read with a plain socket). That is why it looked as if it never answered HTTP.
- Its page (`DDC_VoIP Settings`, footer "Dallas Delta Corp Web Page") has no login form and fills its fields by script. The script's reads:
  `GET /auth=<PIN>,<ms>` logs in (200, body `OK`, with the empty PIN), then `GET /SYS` gives `model,mac,firmware,...`
  (`DDC_VoIP-BIA,38:b1:9e:d0:02:14,s11.0920.04,show`), `GET /_REG` the registration (`Yes > Server 1,27,0`), and `GET /webdata` the settings as JSON
  `{"i": {checkboxes}, "n": {field: value}}` with the same field names as DDC_VoIP-m's form (`user_number`, `sip_proxy`; the SIP password is in there,
  so parse it on the box). Before `/auth` they return 404. `/dotest`, `/getrst` and `POST /settings` also exist; they test, reset or write, so a
  reader never calls them.
- A marker matching both generations' pages is "Dallas Delta Corp" (DDC_VoIP-m's comment and the S11 footer).
- adjamarragu's DDC_VoIP-m now reports MAC `00:18:1F:01:F1:6A`, not the `00-18-1F-01-E6-16` read on 2026-10-08: the unit may have been replaced
  (UNVERIFIED; same model and firmware 042112, registered).

UNC reads both generations (`identify_candidates.identify_ddc`, `s11_identity`); its catalog has the DDC_VoIP-BIA type.

Excerpt (unified-network-controller `wc-local/scripts/site_onboarding/identify_candidates.py` `DDC_AGENT`, commit 04c3a7f), run on the SMC:

```python
def raw_get(path):                       # the S11 reply starts with a blank line: http.client and curl refuse it
    s = socket.create_connection((ip, 80), timeout=20)
    s.sendall(("GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, ip)).encode())
    ...                                  # read to EOF, cut at the first "HTTP/", split head and body at the blank line
if raw_get("/auth=,%d" % int(time.time() * 1000))[0] == "200":   # empty PIN
    facts = s11_identity(raw_get("/SYS")[1], raw_get("/_REG")[1], raw_get("/webdata")[1])
# s11_identity: /SYS "model,mac,firmware,..." split on ","; /_REG starts "Yes"; /webdata JSON n.user_number, n.sip_proxy only
```

Screenshot pending: the ATA's `DDC_VoIP Settings` page, taken from the SMC through a port forward with its SIP number and server redacted.

## Vendor sources

Manuals, datasheets, web pages, the IANA and IEEE excerpts and a firmware note are in [vendor-sources-dallas-delta-20261008_1043/](vendor-sources-dallas-delta-20261008_1043/readme.md). No firmware
image or MIB is publicly downloadable. The ATA's switch port and the switch itself belong to skill-mikrotik.
