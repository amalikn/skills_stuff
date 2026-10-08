---
Title: Dallas Delta Corp VoIP vendor sources
Category: vendor-sources-index
Status: current
Authority: reference-capture
Scope: Dallas Delta Corporation (DDC) VoIP help-point and door-station documents kept for the DDC_VoIP-m unit found at community Wi-Fi sites
Last reviewed: 2026-10-08
Summary: >-
  Verbatim DDC manuals, datasheets and web pages (PDF plus .txt extraction) retrieved 2026-10-08, with the SNMP, firmware, default-credential and model-naming facts they
  support and the live SNMP test result for the DDC_VoIP-m. No firmware image or MIB file is publicly downloadable.
---

# Dallas Delta Corp VoIP vendor sources

Collected 2026-10-08 for the DDC VoIP ATA/help point seen at community Wi-Fi sites: web title "DDC_VoIP Login", HTML comment "Dallas Delta Corp VoIP telephone Feb 2009 ver2.0", settings page "Model:
DDC_VoIP-m", "Version No.: 042112", MAC OUI 00:18:1F. Files are kept verbatim. Each PDF has a `.txt` beside it from `pdftotext -layout`; the six image-only datasheets (CST, Guard, Hygienic, Sentinel,
Sentry, Weathertough) were OCR'd with tesseract instead, so their text may hold OCR errors. Web pages are kept as text only. Firmware: see [firmware-manifest.yaml](firmware-manifest.yaml); no image
could be downloaded.

## Contents

- [Files](#files)
- [Facts for the DDC_VoIP-m](#facts-for-the-ddc_voip-m)
- [Not found](#not-found)

## Files

| File | What it is | Source URL | Retrieved | Covers |
|---|---|---|---|---|
| wayback-DDC_VoIP_m_v4_2015_12_15.pdf (+ .txt) | DDC VoIP V2 help point / Sentry / | https://web.archive.org/web/20230630224841id_/https://dallasdelta.com/wp-content/uploads/2018/08/DDC_VoIP_m_v4_2015_12_15.pdf | 2026-10-08 | DDC_VoIP-m |
|  |   Guard user manual, |  |  |   generation |
|  |   `DDC_VoIP_m_v4.cdr 15/12/2015`; no |  |  |   (closest |
|  |   SNMP section |  |  |   match) |
| VoIP-S11-Manual.pdf (+ .txt) | VoIP Doorstation S-11 user manual, | https://dallasdelta.com/api/resources/manuals/VoIP-S11-Manual.pdf | 2026-10-08 | S11 |
|  |   release note 21/10/2021 PCB S_11 |  |  |   (successor) |
| seadan-DDLSENTRYVOIPKPV_SENTRYVOIPKPV_user-manual_1.pdf (+ .txt) | Sentry VoIP keypad manual hosted by | https://resources.seadan.com.au/resources/products/DDLSENTRYVOIPKPV/attachments/DDLSENTRYVOIPKPV_SENTRYVOIPKPV_user-manual_1.pdf | 2026-10-08 | S11 |
|  |   Seadan, |  |  |   Sentry |
|  |   `Manual-VoIP-s11 r1.cdr 08-03-2019`, |  |  |   keypad |
|  |   pcb s11 Apr19; source of the |  |  |  |
|  |   45255 claim |  |  |  |
| seadan-DDLSENTRYVOIPCAM1BV_SENTRYVOIP1BVCAM_installation-manual_1.pdf | Sentry VoIP 1-button camera | https://resources.seadan.com.au/resources/products/DDLSENTRYVOIPCAM1BV/attachments/DDLSENTRYVOIPCAM1BV_SENTRYVOIP1BVCAM_installation-manual_1.pdf | 2026-10-08 | VoIP camera |
|   (+ .txt) |   installation manual, v1.3 02-02-2018 |  |  |   door station |
| Sentinel-VoIP-Manual.pdf (+ .txt) | Sentinel VoIP manual, | https://dallasdelta.com/api/resources/manuals/Sentinel-VoIP-Manual.pdf | 2026-10-08 | S11 Sentinel |
|  |   `Manual-VoIP-s11_S r1 28-05-2020` |  |  |  |
| VoIP-Hygienic.pdf (+ .txt) | Hygienic VoIP manual, | https://dallasdelta.com/api/resources/manuals/VoIP-Hygienic.pdf | 2026-10-08 | S11 Hygienic |
|  |   `Manual-VoIP-HYG-S11 15-11-2022` |  |  |  |
| VoIPCam-Manual.pdf (+ .txt) | VoIP camera Mk2 manual v4, 1/9/2024, | https://dallasdelta.com/api/resources/manuals/VoIPCam-Manual.pdf | 2026-10-08 | VoIP Cam Mk2 |
|  |   pcb iX60 rev2 |  |  |  |
| wayback-VoIP-Camera-UserManual.pdf (+ .txt) | Older VoIP camera door station manual | https://web.archive.org/web/20230630194807id_/https://dallasdelta.com/wp-content/uploads/2021/03/VoIP-Camera-UserManual.pdf | 2026-10-08 | VoIP |
|  |  |  |  |   Cam (older) |
| wayback-sentry.web_.pdf (+ .txt) | Sentry series datasheet, 2016 | https://web.archive.org/web/20180921164310id_/http://dallasdelta.com:80/wp-content/uploads/2016/11/sentry.web_.pdf | 2026-10-08 | Sentry family |
|  |   web edition |  |  |  |
| wayback-PIN-Reset-Request-form.pdf (+ .txt) | DDC PIN reset request form | https://web.archive.org/web/20190407064843id_/http://dallasdelta.com/wp-content/uploads/2016/07/PIN-Reset-Request-form.pdf | 2026-10-08 | All DDC (PIN |
|  |  |  |  |   reset |
|  |  |  |  |   process) |
| Sentry-datasheet.pdf (+ OCR .txt) | Current Sentry datasheet | https://dallasdelta.com/api/resources/datasheets/Sentry-datasheet.pdf | 2026-10-08 | Sentry family |
| Sentry-Camera-datasheet.pdf (+ .txt) | Current Sentry camera datasheet | https://dallasdelta.com/api/resources/datasheets/Sentry-Camera-datasheet.pdf | 2026-10-08 | Sentry camera |
| Sentinel-datasheet.pdf (+ OCR .txt) | Current Sentinel datasheet | https://dallasdelta.com/api/resources/datasheets/Sentinel-datasheet.pdf | 2026-10-08 | Sentinel |
|  |  |  |  |   family |
| CST-datasheet.pdf (+ OCR .txt) | Customer service / help-point | https://dallasdelta.com/api/resources/datasheets/CST-datasheet.pdf | 2026-10-08 | CST family |
|  |   telephone datasheet |  |  |  |
| Guard-datasheet.pdf (+ OCR .txt) | Guard door station datasheet | https://dallasdelta.com/api/resources/datasheets/Guard-datasheet.pdf | 2026-10-08 | Guard family |
| Hygienic-datasheet.pdf (+ OCR .txt) | Hygienic telephone datasheet | https://dallasdelta.com/api/resources/datasheets/Hygienic-datasheet.pdf | 2026-10-08 | Hygienic |
|  |  |  |  |   family |
| Weathertough-datasheet.pdf (+ OCR .txt) | Weathertough telephone datasheet | https://dallasdelta.com/api/resources/datasheets/Weathertough-datasheet.pdf | 2026-10-08 | Weathertough |
|  |  |  |  |   family |
| dallasdelta-brochure.pdf (+ .txt) | Current product brochure | https://dallasdelta.com/api/resources/datasheets/dallasdelta-brochure.pdf | 2026-10-08 | All |
|  |  |  |  |   DDC products |
| TeamsSetUp.pdf (+ .txt) | MS Teams SIP Gateway setup for DDC | https://dallasdelta.com/api/resources/miscellaneous/TeamsSetUp.pdf | 2026-10-08 | DDC |
|  |   VoIP phones |  |  |   VoIP |
|  |  |  |  |   (current) |
| web-dallasdelta-support-downloads.txt | Downloads page; firmware section has | https://dallasdelta.com/support/downloads | 2026-10-08 | All DDC |
|  |   no public file |  |  |  |
| web-dallasdelta-support-compliance.txt | ACMA compliance page: firmware release | https://dallasdelta.com/support/compliance | 2026-10-08 | S11, S11 |
|  |   notes and support periods |  |  |   Sentinel, |
|  |  |  |  |   VoIP Cam |
| web-dallasdelta-support-compliance-security-details.txt | Firmware remediation and | https://dallasdelta.com/support/compliance/security-details | 2026-10-08 | Current |
|  |   lifecycle policy |  |  |   DDC VoIP/4G |
| web-dallasdelta-support-faq.txt | Support FAQ (SIP registration, Teams) | https://dallasdelta.com/support/faq | 2026-10-08 | All DDC |
| web-dallasdelta-support.txt | Support landing page | https://dallasdelta.com/support | 2026-10-08 | All DDC |
| web-dallasdelta-products-sentry.txt | Sentry product page | https://dallasdelta.com/products/sentry | 2026-10-08 | Sentry |
| web-dallasdelta-products-sentry-sentry-keypad-voip.txt | Sentry keypad (VoIP) product page | https://dallasdelta.com/products/sentry/sentry-keypad-voip/ | 2026-10-08 | Sentry |
|  |  |  |  |   keypad VoIP |
| web-dallasdelta-products-sentinel.txt | Sentinel product page | https://dallasdelta.com/products/sentinel | 2026-10-08 | Sentinel |
| web-dallasdelta-products-polephone.txt | Pole phone (roadside help point) page | https://dallasdelta.com/products/polephone | 2026-10-08 | Pole phone |
| web-dallasdelta-products-guard.txt | Guard product page | https://dallasdelta.com/products/guard | 2026-10-08 | Guard |
| web-dallasdelta-products-weathertough.txt | Weathertough product page | https://dallasdelta.com/products/weathertough | 2026-10-08 | Weathertough |
| iana-enterprise-numbers-45255-excerpt.txt | IANA Private Enterprise Number | https://www.iana.org/assignments/enterprise-numbers.txt | 2026-10-08 | Enterprise |
|  |   entry 45255 |  |  |   45255 |
| ieee-oui-00-18-1F-excerpt.txt | IEEE OUI registry entry 00-18-1F | https://standards-oui.ieee.org/oui/oui.txt | 2026-10-08 | MAC OUI |

Listed on the downloads page but not kept, as they are analogue, 4G or PABX products rather than VoIP help points: 4G-Series datasheet, 4GS manual, SimFone 4G manual, LP8 manual, DoorCom manual,
Sentinel Analogue manual, Enclosures datasheet, DDConnect datasheet, warranty terms, and the Windows tools `SentPro8_9.exe` and `DDC-Client-4GS-Configurator.exe` (all under
`https://dallasdelta.com/api/resources/`).

## Facts for the DDC_VoIP-m

- **SNMP.** S11-generation manuals (2019 to 2022) say the unit "can send SNMP traps to a server", v2c, community and one or two server IPs configured, enterprise `1.3.6.1.4.1.45255.1.1.1.0` to `.10`,
  example `snmpget -v2c -c DDC_VoIP ...` (Sentinel VoIP manual prints the community as `DDCVoIP`). VERIFIED_PRIMARY for S11 only. The 2015 DDC_VoIP_m manual has no SNMP section and lists Syslog as its
  only event output. **Live test 2026-10-08 on the DDC_VoIP-m (version 042112): no answer to SNMP v2c community `DDC_VoIP` or `public`, and its settings page has no SNMP field.** Do not assume SNMP on
  this model.
- **Enterprise 45255** is registered to Dallas Delta Corp (IANA PEN, VERIFIED_PRIMARY). No MIB file is published.
- **OUI 00:18:1F** is Palmmicro Communications, Beijing (IEEE registry, VERIFIED_PRIMARY); consistent with the manual's "Dedicated VoIP chip set". The chip itself is UNVERIFIED.
- **Model naming.** The 2015 manual's file name is `DDC_VoIP_m_v4` and its cover reads "DDC VoIP V2 ... Help Point Telephone", "Model DDC VoIP"; the unit's "ver2.0" comment matches. That `-m` names
  this manual's generation is inferred (UNVERIFIED).
- **Credentials.** DDC_VoIP_m and S11 manuals: shipped with no admin password; rear keypad `*#*#7*1` sets static 192.168.1.100 (mask 255.255.0.0 in the 2015 manual, 255.255.255.0 in S11) and clears
  the admin password, `*#*#7*2` sets DHCP and clears it, S11 `*#*#7*9` factory reset. S11 relay code factory default `123`. The VoIP camera manuals use `admin`/`admin`. The 2026 compliance page says
  products now ship with unique per-unit credentials; that applies to current firmware, not a 2009-era unit.
- **Firmware.** The 2015 manual says "Firmware up-gradable" but its Upgrade page only loads ring-tone `.DAT` files. Version `042112` appears in no vendor source (UNVERIFIED; it may be a date code).
  Current published lines: S11 `s11.2604.09`, S11 Sentinel `s11.2606.09`, VoIP Cam `v2605.14`.
- **Management protocols (2015 manual).** HTTP web UI for all settings, SIP (port 5060, PRACK, STUN), Syslog, rear keypad. S11 adds SNMP traps and an auto-provisioning server.

## Not found

- Any firmware image (none public; downloads page section is empty, files likely via customertools.dallasdelta.com or the vendor).
- Any MIB for enterprise 45255 (vendor, Seadan, observium, oidview searches).
- Any vendor document naming `DDC_VoIP-m` or version `042112` as such.
- Whirlpool forum thread https://forums.whirlpool.net.au/archive/995799 (VoIP door station on Asterisk) returned HTTP 403; not kept.
