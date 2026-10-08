---
Title: Raspberry Pi 4 Model B vendor sources
Category: vendor-sources
Status: current
Authority: >-
  Verbatim copies of Raspberry Pi Ltd documents, documentation sources and rpi-eeprom release notes, plus read-only captures from four SMC boxes; the vendor
  originals stay authoritative.
Scope: Raspberry Pi 4 Model B (revision d03115) used as SMC site controllers (Ubuntu 22.04.1, kernel 5.15.0-1078-raspi, overlayroot)
Last reviewed: 2026-10-08
Summary: >-
  Product brief, datasheet, mechanical drawing, BCM2711 peripherals, revision-code, bootloader EEPROM and OTP documentation, EEPROM release notes, firmware
  manifest and per-box firmware captures for the Raspberry Pi SMC flavour.
---

# Raspberry Pi 4 Model B vendor sources

Collected 2026-10-08 under the operator rule that every device keeps its product documents, MIB details, firmware details and firmware files. PDFs are kept as downloaded with a `pdftotext -layout`
copy beside them; documentation pages are kept as their official AsciiDoc source text. Firmware binaries are committed in [firmware-files/raspberry-pi/](../../firmware-files/raspberry-pi/) and
described in [firmware-manifest.yaml](firmware-manifest.yaml).

## Documents

| File | What it is | Source URL | Retrieved |
|---|---|---|---|
| [raspberry-pi-4-product-brief.pdf](raspberry-pi-4-product-brief.pdf) / [.txt](raspberry-pi-4-product-brief.txt) | Raspberry Pi 4 Model B | https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-product-brief.pdf | 2026-10-08 |
|  |   product brief |  |  |
| [raspberry-pi-4-datasheet.pdf](raspberry-pi-4-datasheet.pdf) / [.txt](raspberry-pi-4-datasheet.txt) | Raspberry Pi 4 Model B datasheet, | https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-datasheet.pdf | 2026-10-08 |
|  |   Release 1.1 |  |  |
| [raspberry-pi-4-mechanical-drawing.pdf](raspberry-pi-4-mechanical-drawing.pdf) | Mechanical drawing (vector only, no | https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf | 2026-10-08 |
|  |   extractable text) |  |  |
| [bcm2711-peripherals.pdf](bcm2711-peripherals.pdf) / [.txt](bcm2711-peripherals.txt) | BCM2711 ARM peripherals datasheet | https://datasheets.raspberrypi.com/bcm2711/bcm2711-peripherals.pdf | 2026-10-08 |
| [rpi-docs-revision-codes.adoc.txt](rpi-docs-revision-codes.adoc.txt) | Revision codes page | https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-revision-codes | 2026-10-08 |
|  |   (decodes `d03115`) |   (source: github.com/raspberrypi/documentation, master |  |
|  |  |   2f403648, `documentation/asciidoc/computers/raspberry-pi/revision-codes.adoc`) |  |
| [rpi-docs-eeprom-bootloader.adoc.txt](rpi-docs-eeprom-bootloader.adoc.txt) | Bootloader EEPROM | https://www.raspberrypi.com/documentation/computers/raspberry-pi.html (source: same | 2026-10-08 |
|  |   configuration page |   repo, `eeprom-bootloader.adoc`) |  |
| [rpi-docs-boot-eeprom.adoc.txt](rpi-docs-boot-eeprom.adoc.txt) | Boot EEPROM page (release | https://www.raspberrypi.com/documentation/computers/raspberry-pi.html (source: same | 2026-10-08 |
|  |   channels, `rpi-eeprom-update`) |   repo, `boot-eeprom.adoc`) |  |
| [rpi-docs-otp-bits.adoc.txt](rpi-docs-otp-bits.adoc.txt) | OTP register page; states the | https://www.raspberrypi.com/documentation/computers/raspberry-pi.html (source: same | 2026-10-08 |
|  |   64-bit serial is in |   repo, `otp-bits.adoc`) |  |
|  |   `/proc/device-tree/serial-number` |  |  |
| [rpi-eeprom-firmware-2711-release-notes.md.txt](rpi-eeprom-firmware-2711-release-notes.md.txt) | rpi-eeprom firmware-2711 | https://github.com/raspberrypi/rpi-eeprom/blob/master/firmware-2711/release-notes.md | 2026-10-08 |
|  |   release notes |  |  |
| [firmware-manifest.yaml](firmware-manifest.yaml) | Firmware files kept, versions, | Built from the rpi-eeprom repo and the captures below | 2026-10-08 |
|  |   sha256, which boxes run them |  |  |

## Captures

Read-only, 2026-10-08 10:44 AEDT, over `ssh root@<node>.teleport.apn.au`: `vcgencmd bootloader_version`, `vcgencmd version`, `rpi-eeprom-update`, device-tree model, cpuinfo revision and the firmware
packages. Nothing was written to the boxes.

| File                                    | What it is                                   | Source                           | Retrieved  |
| --------------------------------------- | -------------------------------------------- | -------------------------------- | ---------- |
| [captures/20-mile-smc01-20261008.txt](captures/20-mile-smc01-20261008.txt) | Firmware and model read of 20-mile-smc01     | 20-mile-smc01 (APN Teleport)     | 2026-10-08 |
| [captures/adjamarragu-smc01-20261008.txt](captures/adjamarragu-smc01-20261008.txt) | Firmware and model read of adjamarragu-smc01 | adjamarragu-smc01 (APN Teleport) | 2026-10-08 |
| [captures/areyonga-smc01-20261008.txt](captures/areyonga-smc01-20261008.txt) | Firmware and model read of areyonga-smc01    | areyonga-smc01 (APN Teleport)    | 2026-10-08 |
| [captures/glen-hill-smc01-20261008.txt](captures/glen-hill-smc01-20261008.txt) | Firmware and model read of glen-hill-smc01   | glen-hill-smc01 (APN Teleport)   | 2026-10-08 |

## MIBs

Raspberry Pi Ltd publishes no SNMP MIB for the Raspberry Pi 4. SNMP on these boxes, if enabled, would be net-snmp serving the standard MIBs (MIB-II, HOST-RESOURCES-MIB, UCD-SNMP-MIB and the like), so
no MIB file is kept here.

## Findings

- `d03115` decodes, per the official revision-codes table, to Model 4B, Revision 1.5, 8 GB, manufacturer Sony UK (new-style code: memory 5 = 8 GB, processor 3 = BCM2711, type 0x11 = 4B, revision 5).
- All four boxes run bootloader EEPROM 2023-01-11 (git `8ba17717`, timestamp 1673458852) and VL805 `000138c0`. The image `pieeprom-2023-01-11.bin` carries the same version and timestamp strings.
- Ubuntu's `rpi-eeprom` 13.12 package only ships the 2022-01-25 image, which is older than what the boxes run, so `rpi-eeprom-update` reports "up to date". Upstream's default channel is 2026-09-23
  (promoted 2026-09-27), so the boxes are behind upstream.
- The 2026-09-23 release notes add an MFG-version check on updates; read them before any EEPROM update.
