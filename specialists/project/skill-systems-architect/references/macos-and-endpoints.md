---
Title: macOS, MacBook and endpoint lifecycle
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  macOS, MacBook and endpoint lifecycle decisions: enrollment, FileVault and bootstrap-token custody, update rings, Platform SSO, admin-endpoint hygiene, Intel end of road and validation.
---

# macOS, MacBook and endpoint lifecycle

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Lifecycle and enrollment](#lifecycle-and-enrollment)
- [Recovery custody](#recovery-custody)
- [Updates and identity](#updates-and-identity)
- [Developer, admin and FOSS boundaries](#developer-admin-and-foss-boundaries)
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
- osquery and other FOSS tools cover inventory, configuration and security checks. MDM enrollment still needs an MDM server with Apple push certificates.
- No FOSS tool replaces Apple Business or a commercial MDM. This pack requires no paid endpoint add-on.

## Patterns and anti-patterns

| Pattern                                 | Use when                 | Anti-pattern                           | Why it fails                                                |
| --------------------------------------- | ------------------------ | -------------------------------------- | ----------------------------------------------------------- |
| ADE with supervision                    | Organisation-owned Macs  | Manual or user-approved enrollment     | Not fully supervised; weaker lost-device and update control |
| PRK escrow gated in Setup Assistant     | Every FileVault Mac      | Let users enable FileVault later       | Keys never reach escrow; data unrecoverable                 |
| DDM target version plus deadline        | Update enforcement       | Rely on user prompts and deferrals     | Fleet drifts; security fixes wait on users                  |
| Platform SSO plus MDM local admin       | IdP-backed fleets        | AD bind on roaming laptops             | Logins break off-network                                    |
| Hardware-backed, short-lived admin keys | Admin and developer Macs | Long-lived SSH keys in the home folder | One stolen laptop opens every host                          |
| Retire Intel on a plan                  | Mixed fleet              | Buy or redeploy Intel Macs             | Security updates end; Rosetta goes after macOS 27           |

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

Baselines:
- [macOS Security Compliance Project](https://github.com/usnistgov/macos_security) - read this for NIST/CIS-mapped macOS baselines (pointer).

[a3url]: https://support.apple.com/guide/deployment/install-and-enforce-software-updates-depd30715cbb/web

[ddmurl]: https://support.apple.com/guide/deployment/intro-to-declarative-device-management-depb1bab77f8/web

[alurl]: https://support.apple.com/guide/deployment/activation-lock-on-mac-dep4e1ae6f2c/web

[a1url]: https://support.apple.com/guide/deployment/manage-filevault-with-device-management-dep0a2cb7686/web

[a2url]: https://support.apple.com/guide/deployment/use-secure-and-bootstrap-tokens-dep24dbdcf9e/web

[a4url]: https://support.apple.com/guide/deployment/platform-sso-for-macos-dep7bbb05313/web
