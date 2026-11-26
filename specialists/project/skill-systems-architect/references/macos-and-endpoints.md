---
Title: macOS, MacBook and endpoint lifecycle
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  macOS, MacBook and endpoint lifecycle decisions: enrollment, FileVault and bootstrap-token custody, update rings, Platform SSO, admin-endpoint hygiene,
  free Apple services and FOSS or low-cost MDM options, Intel end of road and validation.
---

# macOS, MacBook and endpoint lifecycle

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Lifecycle and enrollment](#lifecycle-and-enrollment)
- [Recovery custody](#recovery-custody)
- [Updates and identity](#updates-and-identity)
- [Developer, admin and FOSS boundaries](#developer-admin-and-foss-boundaries)
- [FOSS and low-cost MDM](#foss-and-low-cost-mdm)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Mac-specific endpoint questions: enrollment, FileVault and token custody, updates, identity, admin and developer use. Linux and Windows endpoints use their own references.
- Inventory ownership (organisation vs personal), Apple silicon or Intel, macOS version, applications, local data, mobility, identity, network access, privacy, support, replacement.
- Track per device: model identifier, chip, macOS build, enrollment type, FileVault status, bootstrap token escrow status, last check-in.
- A MacBook may be a developer workstation, an admin endpoint or local compute. Sleep, battery, thermals and mobility decide suitability, not specifications alone.

## Decision rules

| Decision           | Rule and threshold                                                                                                    | Evidence                                |
| ------------------ | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Patch window       | Apple publishes no fixed lifecycle. Assume the current major release and the previous two                             | UNVERIFIED assumption; record it        |
| Intel Macs         | macOS Tahoe 26 is the last Intel release; about 3 years of security updates; Rosetta 2 through macOS 27. Buy no Intel | VERIFIED_SECONDARY (WWDC 2025 coverage) |
| Enrollment         | Automated Device Enrollment for every organisation-owned Mac. Manual enrollment cannot be fully supervised            | Design rule; [A1] context               |
| FileVault key      | Escrow the PRK to MDM; hold the Mac in Setup Assistant until FileVault is on and the key is escrowed                  | VERIFIED_PRIMARY [A1]                   |
| Bootstrap token    | macOS 26+: created at enrollment when the MDM supports it. Older: at first secure-token user login                    | VERIFIED_PRIMARY [A2]                   |
| Update enforcement | Declarative device management: target version plus deadline. Legacy commands and deferrals are fallbacks              | Cited [A3] (pointer)                    |
| Update rings       | Canary day 0, early ~10% day 3-7, broad day 14, exceptions with dated waiver                                          | UNVERIFIED as universal                 |
| Identity           | Platform SSO when both IdP and MDM support it; keep one MDM-managed local admin for recovery                          | VERIFIED_PRIMARY [A4]                   |
| Custody            | Log every PRK retrieval and rotate the PRK after use                                                                  | Design rule                             |
| MDM cost           | Apple Business built-in MDM is free since 2026-04-14; price a paid or FOSS MDM only for a gap it leaves               | VERIFIED_PRIMARY [A5]                   |

## Lifecycle and enrollment

```text
Org-owned Mac lifecycle (supervised from first boot to reassignment)

+----------------+     +--------------------+     +--------------------+     +--------------------+
| buy via Apple  | --> | ADE: MDM enrol in  | --> | FileVault on, PRK  | --> | Platform SSO or    |
| Business       |     | Setup Assistant    |     | escrowed; boot-    |     | local account;     |
| (org serial)   |     | (supervised)       |     | strap token to MDM |     | certs, VPN, Wi-Fi  |
+----------------+     +--------------------+     +--------------------+     +--------------------+
                                                                                       |
                                                                                       v
+----------------+     +--------------------+     +--------------------+     +--------------------+
| reassign       | <-- | Activation Lock    | <-- | wipe / return      | <-- | operate: DDM       |
|                |     | cleared            |     |                    |     | updates, inventory |
+----------------+     +--------------------+     +--------------------+     +--------------------+

Legend: --> next lifecycle stage
```

- Certificates arrive by SCEP or ACME profiles. Manually enrolled or user-approved devices are weaker for lost-device and update enforcement.

## Recovery custody

```text
Recovery custody: what the MDM holds, who reads it, and what is lost with it

                 +--------------------------------------+
                 | MDM escrow store                     |
                 |  - FileVault PRK (CMS, MDM cert)     |
                 |  - bootstrap token                   |
                 |  - Activation Lock bypass            |
                 +--------------------------------------+
                     ^             |              |
          escrow at  |   retrieval |              | X MDM lost
          enrolment  |    (logged) v              v
                 +--------+  +-------------+  +-----------------------------+
                 | Mac    |  | named IT    |  | escrow lost: no PRK, no     |
                 +--------+  | role; PRK   |  | bypass. Need MDM backup or  |
                             | rotated     |  | an alternate recovery route |
                             +-------------+  +-----------------------------+

Legend: ^ v escrow or retrieval   X failure and its effect
```

- The Mac encrypts the PRK to a certificate from the MDM in CMS format. Choose: show the PRK to the user, escrow it, or both (VERIFIED_PRIMARY [A1], checked 2026-10-29).
- The bootstrap token grants secure tokens to new accounts and volume ownership (VERIFIED_PRIMARY [A2], checked 2026-10-29).
- On Apple silicon the bootstrap token can also authorise software update installation [A2]. Check with `sudo profiles status -type bootstraptoken`.
- Do not copy Intel-era recovery steps onto Apple silicon: recoveryOS, LocalPolicy and volume ownership differ.
- Do not promise remote unlock after every restart.

> **Learned 2026-11-21** · Secure Enclave keys for unattended agents (age-plugin-se v0.2.1) · VERIFIED_PRIMARY · Source: age-plugin-se `Sources/Plugin.swift:44` (v0.2.1, commit a229872), keygen on a
> locked Mac returned OSStatus -25308 (errSecInteractionNotAllowed) inside and outside the tool sandbox in an Aqua session; continuum DL-117, DL-118 · Falsifier: an enclave key from this plugin used
> while the Mac is locked.
> The plugin creates keys with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`, so even with `--access-control none` a key cannot be made or used while the Mac is locked. An agent that must act
> unattended on a locked Mac cannot unseal with it: design for it (continuum pins the verified public half of the account key so a locked Mac still encrypts captures, and anything that decrypts
> waits for an unlock), or choose an after-first-unlock key and accept a fork. Its `--recipient-type tag` recipients (`age1tag1`) are encryptable by any age 0.12 client without the plugin.

> **Learned 2026-11-22** · Secure Enclave keys: binary independence and locked-screen behaviour (age-plugin-se v0.2.1, macOS) · VERIFIED_PRIMARY (live runs on the operator's Mac) ·
> Source: continuum TASK-321; continuum-app `apps/coordinator/tests/agent_e2e/p4_cases.rs` (e3d865b) · Falsifier: a second build that cannot decrypt, or a locked-screen capture that needs the enclave.
> A key made by one build of age-plugin-se (keygen `--access-control none --recipient-type tag`) was opened by a separately built copy of the same commit (different SHA-256): the identity file is
> a reference to the enclave key, not bound to one binary. A capture that only encrypts (to pinned `age1tag1` and X25519 recipients) completes with the screen locked; only unsealing waits for an
> unlock. A test can wait for the lock state the way macOS reports it:

```rust
// continuum-app apps/coordinator/tests/agent_e2e/p4_cases.rs (e3d865b)
fn console_locked() -> Result<bool, Error> {
  let out = Command::new("ioreg").args(["-n", "Root", "-d1", "-a"]).output()?;
  let text = String::from_utf8_lossy(&out.stdout);
  let after = text.split("<key>IOConsoleLocked</key>").nth(1).ok_or("ioreg reports no IOConsoleLocked")?;
  Ok(after.trim_start().starts_with("<true/>"))
}
```

## Updates and identity

| Ring           | Size                   | Start       | Rule                                               |
| -------------- | ---------------------- | ----------- | -------------------------------------------------- |
| IT canary      | 2-5 Macs               | day 0       | Security agents, VPN and system extensions checked |
| Early adopters | ~10%                   | day 3-7     | App compatibility confirmed before broad           |
| Broad          | Remainder              | day 14      | Deadline enforced                                  |
| Exceptions     | Audio/video, regulated | Waiver date | Dated waiver, owner, re-test                       |

- Ring timings are a starting design (UNVERIFIED as universal).
- Out-of-band security fixes follow the security ring, not the feature ring. Check the mechanism the target macOS uses in [A3].
- Major upgrades need an app compatibility check (security agents, VPN, kernel/system extensions) before ring 1.

| Option                                | Use when                                                 | Caveat                                               |
| ------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------- |
| Local accounts + MDM                  | Small fleet, no IdP                                      | Password drift; offboarding manual                   |
| Platform SSO (minimum macOS per [A4]) | Entra/Okta-type IdP, Secure Enclave key or password sync | IdP and MDM must both support it; test offline login |
| AD bind                               | Legacy only                                              | Fragile off-network; avoid for new designs           |

- Platform SSO registers a Secure Enclave-backed key with the IdP during user registration (VERIFIED_PRIMARY [A4], checked 2026-10-29).
- Keep one local admin managed by MDM (rotated, escrowed) for recovery when the IdP is unreachable.

## Developer, admin and FOSS boundaries

- Separate privileged access from ordinary browsing.
- Keep SSH and signing keys in the Secure Enclave or a hardware key where tools allow.
- Prefer short-lived SSH certificates (Teleport, OpenSSH CA) to long-lived keys.
- Account for arm64 VM and container compatibility and virtualisation limits.
- Local LLM work: benchmark memory pressure, thermal throttling and concurrency. Unified memory is not unlimited.
- Never promise continuous server availability from a laptop without power, sleep and network evidence.
- osquery and other FOSS tools cover inventory, configuration and security checks. MDM enrollment still needs an MDM server with an APNs certificate.
- No FOSS tool replaces Apple Business itself (device ownership, ADE assignment, apps). The MDM server is replaceable; see below.

> **Learned 2026-11-26** · macOS application firewall under a default-deny manifest · VERIFIED_PRIMARY (Apple Platform Security, Firewall security
> in macOS; Apple Support, Change Firewall settings on Mac; socketfilterfw(8); codesign on the Command Line Tools Python) · Source: tools_stuff
> host-firewall (6ab4309, 8c4d19d, 21000b4); continuum DL-276 · Falsifier: a bundle-id firewall entry changed by `socketfilterfw --blockapp`.
> Keep "automatically allow built-in software" on (Apple's default): turned off, macOS asks about its own daemons (replicatord, rapportd) and a
> default-deny tool blocks them. Govern only third-party listeners in the manifest. Entries macOS stores by bundle id (com.github.Electron.helper)
> cannot be changed by `socketfilterfw` on macOS 15 (paths only); `--add <bundle-id>` makes a bogus path entry. `/usr/bin/python3` is a small
> xcrun launcher: the executable that accepts connections is the Command Line Tools Python.app, Apple-signed, so it is auto-allowed unless the
> manifest blocks that path explicitly. Docker on the Mac (OrbStack) exposes each network on a bridge; its default 192.168.x pool can shadow a
> VPN's routes (here the office DNS server): set `default-address-pools` (~/.orbstack/config/docker.json, `orb restart docker`) to a block clear
> of every VPN, the LAN and CGNAT; networks move when recreated.

## FOSS and low-cost MDM

Free Apple services (VERIFIED_PRIMARY unless marked, checked 2026-10-29):

- Apple Business replaced Apple Business Manager, Apple Business Essentials and Apple Business Connect on 2026-04-14. It is a free service in the U.S.
  and 200+ countries and regions, and includes built-in MDM with Blueprints, Managed Apple Accounts and an Admin API [A5].
- Apple Business still assigns devices to an external MDM service when the built-in one is not used [A6]. ADE assignment itself costs nothing.
- The MDM push (APNs) certificate is issued at the Apple Push Certificates Portal (identity.apple.com) [A7], with any Apple Account and no fee
  (VERIFIED_SECONDARY: Fleet's setup guide [F2]; Apple's pages name the portal but list no price).
  Apple requires annual renewal; renew with the same Apple Account, or every Apple device must re-enroll (VERIFIED_SECONDARY, Fleet guide [F2]).
- The catch for a self-built server: the push certificate request must be signed by an MDM Vendor CSR signing certificate. Only an Account
  Holder of the Apple Developer Program ($99 a year) or Enterprise Program ($299 a year) can request one, by contacting Apple [A7] [A8].
  A commercial or Fleet server signs the request for you. mdmcert.download is for testing and development only (its own MicroMDM docs [M2]).

| Option                      | Licence (checked 2026-10-29)                   | Status                                           |
| --------------------------- | ---------------------------------------------- | ------------------------------------------------ |
| Apple Business built-in MDM | Free Apple service, not FOSS                   | Available since 2026-04-14 [A5]                  |
| Fleet Free (self-hosted)    | MIT core; `ee/` commercial; docs CC BY-SA [F1] | v4.94.0, 2026-10-28; active                      |
| Fleet Premium               | Commercial, $7 per host per month (list) [F3]  | same release                                     |
| NanoMDM                     | MIT [N1]                                       | v0.9.0, 2025-12-25; commits in 2026-10           |
| MicroMDM v1                 | Not assessed for new use                       | Maintenance mode; support ended end of 2025 [M1] |
| osquery (agent, not an MDM) | Apache-2.0 OR GPL-2.0-only, user choice [O1]   | 5.24.0, 2026-10-09                               |

| Option                      | What it gives                                                                       | What it leaves out                                           |
| --------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Apple Business built-in MDM | Blueprints, ADE, apps, Managed Apple Accounts, Admin API                            | FileVault escrow and DDM update depth: UNVERIFIED, pilot it  |
| Fleet Free                  | MDM, BYOD, DDM profiles, OS settings, scripts, inventory, osquery, GitOps, SSO [F3] | zero-touch ADE, encryption and update enforcement, lock/wipe |
| Fleet Premium               | adds the items Fleet Free leaves out, plus app deployment, RBAC, audit log [F3]     | -                                                            |
| NanoMDM                     | MDM protocol core, MySQL/PostgreSQL storage, horizontal scaling [N1]                | SCEP, TLS, ADE API, profiles, VPP, inventory API             |
| MicroMDM v1                 | an existing install only                                                            | support; maintainers point to NanoMDM                        |
| osquery                     | SQL inventory and compliance queries [O1]                                           | enrollment, FileVault escrow, lock or wipe                   |

- Fleet Free does not include zero-touch setup, disk-encryption enforcement, recovery lock, OS update enforcement or lock/wipe commands [F3].
  Those are the controls the decision rules above require for organisation-owned Macs.
- NanoMDM is a library and server core. A working service also needs SCEP, TLS termination, NanoDEP for the ADE API, enrollment profiles and
  your own command tooling (raw plist commands) [N1]. Budget engineering time, not licences.

```text
Self-hosted NanoMDM: the parts you build and run yourself

+-------------+   HTTPS   +-----------+     +-----------+     +------------------+
| Mac (ADE or | --------> | TLS proxy | --> | NanoMDM   | --> | MySQL/PostgreSQL |
| profile)    |           | (yours)   |     | core      |     | storage          |
+-------------+           +-----------+     +-----------+     +------------------+
     ^   |                                     |     ^
     |   +----- SCEP (yours) ------------------+     | webhook / raw plist commands
     |                                               |
  APNs push <-- push cert (Apple Developer acct) <-- your automation; NanoDEP for ADE

X push cert expires or is renewed under another Apple Account: every device must re-enroll
Legend: --> request or data flow   X failure and its effect
```

| Situation                                      | Viable choice                          | Why                                                             |
| ---------------------------------------------- | -------------------------------------- | --------------------------------------------------------------- |
| Small or mid Apple-only fleet, no IT engineers | Apple Business built-in MDM            | Free, supervised ADE; pilot FileVault escrow and DDM updates    |
| Mixed OS, inventory and compliance as code     | Fleet Free plus Apple Business for ADE | Free MDM, profiles, osquery; enforcement gaps above             |
| Org-owned Macs needing escrow, deadlines, wipe | Fleet Premium or a commercial MDM      | Free tiers omit the enforcement controls; price per host        |
| Engineering team building its own platform     | NanoMDM + NanoDEP + SCEP               | MIT, scalable; needs a developer account and in-house operation |
| Existing MicroMDM v1                           | Migrate (NanoMDM, Fleet or Apple)      | Out of support since the end of 2025                            |
| Inventory and security queries only            | osquery (Fleet as manager)             | No enrollment; pair it with an MDM                              |

- Whatever the server, the recovery custody rules above still apply: PRK escrow, bootstrap token, MDM backup and the annual APNs renewal owner.

## Patterns and anti-patterns

| Pattern                                 | Use when                 | Anti-pattern                           | Why it fails                                                |
| --------------------------------------- | ------------------------ | -------------------------------------- | ----------------------------------------------------------- |
| ADE with supervision                    | Organisation-owned Macs  | Manual or user-approved enrollment     | Not fully supervised; weaker lost-device and update control |
| PRK escrow gated in Setup Assistant     | Every FileVault Mac      | Let users enable FileVault later       | Keys never reach escrow; data unrecoverable                 |
| DDM target version plus deadline        | Update enforcement       | Rely on user prompts and deferrals     | Fleet drifts; security fixes wait on users                  |
| Platform SSO plus MDM local admin       | IdP-backed fleets        | AD bind on roaming laptops             | Logins break off-network                                    |
| Hardware-backed, short-lived admin keys | Admin and developer Macs | Long-lived SSH keys in the home folder | One stolen laptop opens every host                          |
| Retire Intel on a plan                  | Mixed fleet              | Buy or redeploy Intel Macs             | Security updates end; Rosetta goes after macOS 27           |
| Free tier checked against the controls  | Choosing a FOSS MDM      | "Fleet is free, so we are covered"     | ADE, escrow, update and wipe enforcement are Premium [F3]   |

## Failure modes and tests

| Failure                      | Symptom                                                     | Blast radius                       | Proving test                                                   |
| ---------------------------- | ----------------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------- |
| PRK not escrowed             | Locked Mac with no recovery key                             | User data on that Mac              | Inventory shows escrow per device; retrieve and rotate one PRK |
| Bootstrap token missing      | New accounts lack secure token; Apple silicon updates stall | That Mac                           | `profiles status -type bootstraptoken` on a sample             |
| MDM lost or tenant deleted   | No PRK, no Activation Lock bypass                           | Whole fleet's recovery             | Restore MDM export or backup in a test tenant                  |
| Update deadline not enforced | Fleet spread across many builds                             | Exposure window fleet-wide         | Deadline test on canary; build count after day 14              |
| IdP unreachable              | Platform SSO login fails                                    | Users offline or during IdP outage | Offline login and MDM local admin login drill                  |
| Activation Lock not cleared  | Returned Mac cannot be reassigned                           | Hardware stock                     | Offboard a test Mac; reassign through ADE                      |
| Intel Mac past updates       | No security fixes                                           | Every Intel device                 | Intel count per quarter against the retirement plan            |
| APNs certificate lapses      | Devices stop answering commands; renewal under new account  | Whole fleet must re-enroll         | Calendar the renewal owner; renew a lab certificate early      |

## Worked example

Fleet: 200 Macs, 30 of them Intel. A security fix ships on day 0.

1. Canary 4 Macs on day 0. Early ring 10% = 20 Macs from day 3. Broad 170 Macs at day 14. Exceptions: 6 Macs on dated waivers.
2. Exposure: unpatched count falls 200 -> 196 (day 0) -> 176 (day 3-7) -> 6 (day 14 deadline). The 6 waivers are named, owned, re-tested.
3. Intel plan: 30 Macs at 10 per quarter take 3 quarters. That finishes well inside the roughly 3-year update window (VERIFIED_SECONDARY).
4. Custody check: 1 PRK retrieval per month means 12 logged reads and 12 rotations a year. A read with no rotation is a finding.
5. Counts in steps 1-4 are illustrative; use the fleet's own inventory and ring sizes.

## Review checklist

- [ ] Every organisation-owned Mac uses ADE, is supervised and reports chip, build and last check-in.
- [ ] FileVault is on and the PRK escrowed on every Mac; retrievals are logged and followed by rotation.
- [ ] Bootstrap token escrow is confirmed; MDM backup or an alternate recovery route is tested.
- [ ] Update rings use DDM deadlines; exceptions have dated waivers and owners.
- [ ] Platform SSO, offline login and the MDM-managed local admin are tested.
- [ ] Admin keys are hardware-backed or short-lived; Intel retirement has dates.
- [ ] Acceptance: zero-touch build, standard-user use, lost-device lock/wipe, Activation Lock offboarding, data restore to a replacement.
- [ ] Privacy and recovery ownership are documented.
- [ ] MDM choice names the controls it lacks (from the free/paid table) and how each is covered; APNs renewal has an owner and the Apple Account.

## Further reading

Deployment and management:
- [Apple Platform Deployment](https://support.apple.com/guide/deployment/welcome/web) - read this as the entry point for enrollment, MDM and DDM.
- [A3] [Install and enforce software updates][a3url] - read this for DDM update enforcement (pointer).
- [Intro to declarative device management][ddmurl] - read this for the DDM model.
- [Activation Lock on Mac][alurl] - read this for bypass and organisation-owned behaviour.

Encryption and tokens:
- [A1] [Manage FileVault with device management][a1url] - read this for PRK escrow (VERIFIED_PRIMARY, checked 2026-10-29).
- [A2] [Use secure and bootstrap tokens][a2url] - read this for token behaviour by OS and chip (VERIFIED_PRIMARY, checked 2026-10-29).
- [Apple Platform Security](https://support.apple.com/guide/security/welcome/web) - read this for Secure Enclave, boot and LocalPolicy internals.

Identity:
- [A4] [Platform SSO for macOS][a4url] - read this for IdP integration (VERIFIED_PRIMARY, checked 2026-10-29).

Free Apple services and low-cost MDM:
- [A5] [Introducing Apple Business (Apple Newsroom, 2026-03-24)][a5url] - read this for the free service and built-in MDM (VERIFIED_PRIMARY, checked 2026-10-29).
- [A6] [Manage the built-in device management service in Apple Business][a6url] - read this for built-in vs external MDM (VERIFIED_PRIMARY, checked 2026-10-29).
- [A7] [Requesting an MDM Vendor CSR signing certificate][a7url] - read this before self-hosting an MDM (VERIFIED_PRIMARY, checked 2026-10-29).
- [A8] [Apple Developer Program](https://developer.apple.com/programs/) - read this for membership fees (VERIFIED_PRIMARY, checked 2026-10-29).
- [F1] [Fleet LICENSE](https://github.com/fleetdm/fleet/blob/main/LICENSE) - read this for the MIT and `ee/` split (VERIFIED_PRIMARY, checked 2026-10-29).
- [F2] [Fleet: macOS MDM setup](https://fleetdm.com/guides/macos-mdm-setup) - read this for the APNs flow and renewal (VERIFIED_SECONDARY, checked 2026-10-29).
- [F3] [Fleet pricing](https://fleetdm.com/pricing) - read this for the Free vs Premium feature table (VERIFIED_PRIMARY, checked 2026-10-29).
- [N1] [NanoMDM](https://github.com/micromdm/nanomdm) - read this for what the core includes and leaves out (VERIFIED_PRIMARY, checked 2026-10-29).
- [M1] [MicroMDM v1](https://github.com/micromdm/micromdm) and [M2] [its quickstart][m2url] - read these for the maintenance notice and APNs steps (VERIFIED_PRIMARY, checked 2026-10-29).
- [O1] [osquery LICENSE](https://github.com/osquery/osquery/blob/master/LICENSE) - read this for the dual licence (VERIFIED_PRIMARY, checked 2026-10-29).

Baselines:
- [macOS Security Compliance Project](https://github.com/usnistgov/macos_security) - read this for NIST/CIS-mapped macOS baselines (pointer).

[a3url]: https://support.apple.com/guide/deployment/install-and-enforce-software-updates-depd30715cbb/web

[ddmurl]: https://support.apple.com/guide/deployment/intro-to-declarative-device-management-depb1bab77f8/web

[alurl]: https://support.apple.com/guide/deployment/activation-lock-on-mac-dep4e1ae6f2c/web

[a1url]: https://support.apple.com/guide/deployment/manage-filevault-with-device-management-dep0a2cb7686/web

[a2url]: https://support.apple.com/guide/deployment/use-secure-and-bootstrap-tokens-dep24dbdcf9e/web

[a4url]: https://support.apple.com/guide/deployment/platform-sso-for-macos-dep7bbb05313/web

[a5url]: https://www.apple.com/newsroom/2026/03/introducing-apple-business-a-new-all-in-one-platform-for-businesses-of-all-sizes/

[a6url]: https://support.apple.com/guide/business/manage-the-built-in-device-management-service-axmc7864dd73/web

[a7url]: https://developer.apple.com/help/account/certificates/mdm-vendor-csr-signing-certificate

[m2url]: https://github.com/micromdm/micromdm/blob/main/docs/user-guide/quickstart.md

> **Learned 2026-11-19** · writing SD cards from macOS · VERIFIED_PRIMARY (bench card writes on the operator's Mac)
> Source: smc-resiliency lab/media.toml and malik1tb lab-evidence/20261119/flash-c2 ·
> Falsifier: a root shell from `osascript ... with administrator privileges` that opens /dev/rdiskN for writing on the same macOS.
> - A root process started through `osascript ... with administrator privileges` could neither read an image on an external volume nor open /dev/rdiskN ("Operation not permitted"): privacy
>   controls (TCC) need Full Disk Access, which the user's Terminal has; `sudo dd` in that Terminal worked.
> - Right after a raw write macOS mounts the card's new FAT partition and adds `.Spotlight-V100` and `.fseventsd`, so a whole-card read-back hash differs from a correct write. Read back only
>   regions macOS cannot mount (or unmount before reading and compare the FAT partition file by file).
> - A Mac's USB card reader does not expose an SD card's CID; read it on the box (`/sys/block/mmcblk0/device/cid`).

> **Learned 2026-11-25** · Time Machine to an SMB share (macOS client, Samba 4.22 vfs_fruit server) · VERIFIED_PRIMARY (live reads on the operator's Mac and the
> NAS container) · Source: me/nas scripts/nas_tm_status.sh and scripts/ct/tm_progress.sh (commit after 1524716), docs/operator-steps/home-network.md ·
> Falsifier: a wedged mount that `diskutil unmount force` clears, or one freed by closing the server session alone.
> - When a Mac leaves the LAN mid-backup (cause inferred from timing, UNVERIFIED) its SMB client can wedge: `diskutil unmount force`, Finder's NetAuthSysAgent (the "Connecting to smb://..."
>   dialog), `backupd-helper`, `df`, `ls` on the mount all sat in uninterruptible wait (`ps` state `U`); a draw.io export started then also hung, stuck exiting in state `E`
>   (link to the mount not proven). `timeout` and kill cannot end them. Closing the session on the server (`smbcontrol smbd close-share <share>`) dropped it there but did not free
>   the Mac, so a restart is the remaining fix. Count `U`-state SMB processes before trying to unmount anything.
> - Progress is readable server-side without touching the Mac. In the sparsebundle, the size of `bands/` and its newest file time show whether data still
>   arrives, and `com.apple.TimeMachine.SnapshotHistory.plist` lists completed backups (an empty `<array/>` means none). Here 31 GB were written, then
>   nothing for over 2 h, with no snapshot: the first backup had stalled although `tmutil status` showed only `Running = 0`.
> - Two caps apply, and both can be set: the dataset's `refquota` and Samba's `fruit:time machine max size`. Read `refquota` as well as `quota`: checking only
>   `quota` showed "none" and led to a wrong claim, corrected the same hour.
>
> ```sh
> # me/nas scripts/ct/tm_progress.sh (inside the Samba container)
> path="$(testparm -s --parameter-name=path --section-name="$share" 2>/dev/null || true)"
> for b in "$path"/*.sparsebundle; do
>   kib="$(du -sk "$b/bands" | cut -f1)"
>   newest="$(find "$b/bands" -type f -printf '%T@\n' | sort -n | tail -1 | cut -d. -f1)"
>   dicts="$(grep -c '<dict>' "$b/com.apple.TimeMachine.SnapshotHistory.plist" 2>/dev/null || true)"
>   echo "bundle $kib ${newest:-0} $((dicts - 1))"
> done
> # me/nas scripts/nas_tm_status.sh (on the Mac): wedged-client count
> ps -axo stat=,comm= | awk '$1 ~ /^U/ && $2 ~ /(diskutil|NetAuthSysAgent|backupd-helper|mount_smbfs)/ {n++} END {print n+0}'
> ```

> **Learned 2026-11-25 (b)** · iPhone (iOS 27.2.1) and iPad (iPadOS 26.7.3) backed up headless with pymobiledevice3 11.63.1 from a Linux VM on a NAS ·
> VERIFIED_PRIMARY (installed pymobiledevice3 source: osu/posix_util.py, pair_records.py, cli backup2; live runs) · Source: home NAS project
> scripts/nas_ios_vm.sh, scripts/ios/ios_backup_job.sh at 6df2786 · Falsifier: an iOS release that backs up over Wi-Fi without a passcode prompt on
> the device, or that keeps advertising mobdev2 on Wi-Fi while cabled
> Local (Finder-style) iOS backups to a Linux host over Wi-Fi work without iCloud, with these facts:
> (1) Pairing needs the device once on USB, unlocked (else PasswordProtectedError), with Trust tapped; it can be done on a Mac and the pymobiledevice3
> pair record (`~/.pymobiledevice3/<UDID>.plist`, or `~/.local/share/pymobiledevice3`) copied to the backup host, which then connects over Wi-Fi only.
> The record is a key to the device: keep it on encrypted storage only, delete other copies; untrusting the computer on the device revokes it.
> (2) `lockdown wifi-connections on` enables Wi-Fi access; while cabled the device advertises `_apple-mobdev2._tcp` only on the USB link; unplugged it
> advertises on the LAN (IPv6 link-local). A bonjour browse shows `UniqueDeviceID: null` until a paired session, so test presence with
> `lockdown info --mobdev2 --udid <UDID>`. (3) Backup encryption is a device setting: `backup2 encryption on <password>` (positional). If it is already
> on, the password set earlier (Finder) applies and cannot be read; Settings > General > Transfer or Reset > Reset > Reset All Settings clears it, and
> also clears Wi-Fi connections and the Trust, so the device is paired again. (4) iOS asks for the device passcode to start a backup to a new host;
> unattended nightly runs depend on whether it asks again (to be measured). (5) Under `sudo`, pymobiledevice3 reads `~$SUDO_USER` (get_homedir), so a
> record linked only under /root is missed by `sudo pymobiledevice3` but found by a systemd unit running as root.
> ```bash
> pymobiledevice3 lockdown info --mobdev2 --udid "$UDID" >/dev/null && \
>   timeout 14400 pymobiledevice3 backup2 backup --mobdev2 --udid "$UDID" /srv/ios-backups   # then check Status.plist SnapshotState finished
> ```

> **Learned 2026-11-25 (c)** · iPhone (iOS 27.2.1), iPad (iPadOS 26.7.3), pymobiledevice3 11.63.1 over Wi-Fi · VERIFIED_PRIMARY (Apple iPhone User Guide
> "Back up iPhone" and support 108366, read 2026-11-25; live lockdown reads) · Source: home NAS scripts/ios/ios_backup_job.sh at 8f7e4e8 · Falsifier: a
> PasswordProtected reading of true on a locked device with a backup session open
> Apple's automatic iCloud Backup rule is only: on power, screen locked, on Wi-Fi; no battery minimum or lock duration is documented. A local Wi-Fi job can
> read the power state and charge over mobdev2 (`lockdown get com.apple.mobile.battery`: ExternalConnected, BatteryIsCharging, BatteryCurrentCapacity).
> Lock state is not reliable that way: `PasswordProtected` read false on both devices while locked, each with a backup running, so a "locked for N
> minutes" gate built on it ships off until verified with no session open. Two first backups over Wi-Fi each dropped with "Connection was terminated
> abruptly" (iPad, once mid-transfer, once while asleep); an iPhone at 29% off power backed up 60 GB without a drop, so power is a policy, not a need.
