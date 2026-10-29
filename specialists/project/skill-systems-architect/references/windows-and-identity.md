---
Title: Windows Server, Windows endpoints and identity
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Windows Server, Windows endpoints, AD DS and Entra ID decisions: lifecycle, Kerberos time dependency, LAPS, tiered admin, break-glass, recovery and validation.
---

# Windows Server, Windows endpoints and identity

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Lifecycle dates](#lifecycle-dates)
- [Identity topology](#identity-topology)
- [Login path, time and bootstrap](#login-path-time-and-bootstrap)
- [Privileged access, break-glass and recovery](#privileged-access-break-glass-and-recovery)
- [Operations and FOSS fit](#operations-and-foss-fit)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Windows Server, Windows endpoints, AD DS, Entra ID and hybrid identity: lifecycle, topology, privileged access, recovery and validation.
- Record per system: exact release, edition, build, installation option (Desktop Experience/Core), roles, join state (AD, Entra, hybrid, workgroup).
- Record licensing and entitlement as USER_STATED, plus support dates. A desktop image is not a server recovery plan.

## Decision rules

| Decision               | Rule and threshold                                                                                   | Evidence                                               |
| ---------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Windows Server 2016    | Plan replacement now: extended support ends 2027-01-12, under 3 months away                          | VERIFIED_SECONDARY; confirm in [W1]                    |
| Windows 10             | Support ended 2025-10-14. A device without a recorded ESU entitlement is unsupported                 | VERIFIED_SECONDARY                                     |
| Kerberos clock skew    | Default tolerance 5 minutes; keep 5. Alert on offset well under 5 minutes                            | VERIFIED_PRIMARY [W3]                                  |
| LAPS backup target     | Entra ID (Entra-joined), AD (domain-joined), either for hybrid, never both                           | VERIFIED_PRIMARY [W2]                                  |
| Legacy Microsoft LAPS  | Deprecated; installer blocked on Windows 11 23H2+. Legacy emulation mode only as a temporary step    | VERIFIED_SECONDARY; [W2]                               |
| Entra emergency access | 2+ cloud-only accounts, phishing-resistant auth unlike normal admins, alert on every sign-in         | VERIFIED_PRIMARY [W4]                                  |
| DC restore             | System-state backup inside the tombstone lifetime. Never hypervisor snapshot rollback (USN rollback) | Cited [W5]                                             |
| krbtgt reset           | After compromise or forest recovery, follow Microsoft's procedure; allow replication between resets  | [W5]; "twice" is common practice, UNVERIFIED as a rule |
| Delegation             | Any unconstrained delegation is a finding                                                            | Design rule                                            |

## Lifecycle dates

| Product                             | Mainstream end      | Extended end                    | Evidence                                                                          |
| ----------------------------------- | ------------------- | ------------------------------- | --------------------------------------------------------------------------------- |
| Windows Server 2016                 | 2022-01-11          | 2027-01-12                      | VERIFIED_SECONDARY                                                                |
| Windows Server 2019                 | 2024-01-09          | 2029-01-09                      | VERIFIED_SECONDARY                                                                |
| Windows Server 2022                 | 2026-10-13 (passed) | 2031-10-14                      | VERIFIED_SECONDARY                                                                |
| Windows Server 2025                 | 2029-11-13          | 2034-11-14                      | VERIFIED_SECONDARY (search extract of the Microsoft page; third parties conflict) |
| Windows 10 (Home/Pro/Ent/Edu, 22H2) | -                   | ended 2025-10-14; paid ESU only | VERIFIED_SECONDARY                                                                |

Microsoft lifecycle pages render client-side and could not be extracted on 2026-10-29. Open [W1] for the exact product before any plan.

## Identity topology

| Need                                       | Prefer                                                     | Why / caveat                                                                            |
| ------------------------------------------ | ---------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Cloud apps, M365, laptops, no legacy apps  | Entra ID join + Intune                                     | No line of sight to a DC needed; Kerberos-only apps need Cloud Kerberos trust or hybrid |
| On-prem Kerberos/LDAP/GPO apps and servers | AD DS (2+ DCs per domain, per site when WAN is unreliable) | DCs are Tier 0; DNS and time depend on them                                             |
| Both                                       | Hybrid: AD DS authoritative, Entra Connect Sync or         | Sync server is Tier 0; model what a sync outage stops for your auth method              |
|                                            | Cloud Sync                                                 | (UNVERIFIED, test)                                                                      |
| Linux hosts in an AD estate                | SSSD/realmd join or FreeIPA with trust                     | Prove ticket, group and sudo mapping per distro                                         |

- Separate authentication, authorization, provisioning, device trust and audit.
- Record forests, domains, trusts, sites, replication topology, DNS zones and the owner of each.

## Login path, time and bootstrap

```text
Kerberos login path: every arrow is a dependency of a successful logon

+--------+  1 SRV _ldap / _kerberos   +-------------------+
|        | -------------------------> | AD-integrated DNS |
|        |                            +-------------------+
|        |  2 AS / TGS request        +-------------------+     +--------------+     +-------------+
| client | -------------------------> | DC (KDC)          | <-- | PDC emulator | <-- | NTP, 3+     |
|        | <------------------------- | TGT, svc ticket   |     | forest root  |     | sources     |
|        |                            +-------------------+     +--------------+     +-------------+
|        |  3 service ticket          +-------------------+
|        | -------------------------> | application       |
+--------+                            +-------------------+

X client vs DC skew over 5 min (default): steps 2-3 fail for every user of that client
X client pointed at a public resolver: step 1 finds no DC
Legend: --> request or time flow   X failure and its effect
```

- A VM resumed from snapshot, a hypervisor time-sync override or a DC syncing to a bad source breaks authentication fleet-wide.
- Other DCs take time from the PDC emulator; members take it from DCs. DNS for AD is AD-integrated or correctly delegated.
- Cloud identity does not replace on-premises Kerberos/LDAP/SMB needs. Entra Connect or Cloud Sync feeds Entra ID; the sync server is Tier 0.

```text
Circular bootstrap: the recovery path must not need the thing it recovers

+-------+     +-----------------+     +--------------+     +-----------------------+
| admin | --> | hypervisor      | --> | AD DS auth   | --> | DC VM running on the  |
+-------+     | login           |     | (DNS, KDC)   |     | same hypervisor       |
              +-----------------+     +--------------+     +-----------------------+
                       ^                                               |
                       |    X hypervisor down: no DC, so no login      |
                       +-----------------------------------------------+

Fix: a local break-glass login on the hypervisor and one DC in a separate failure domain
```

## Privileged access, break-glass and recovery

- Use Microsoft's enterprise access model: control, management and data/workload planes. It replaces the older tier model [W6].
- Tier 0 includes DCs, AD CS, Entra Connect, ADFS, identity admins and their workstations [W6]. Tier 0 credentials never log on to lower tiers.
- Use privileged access workstations, or at least dedicated admin accounts. No email or browsing in admin sessions.
- Windows LAPS is built in since the 2023-04-11 Windows updates and can manage the DSRM password on DCs (VERIFIED_PRIMARY [W2], checked 2026-10-29).
- Service accounts: prefer gMSA/dMSA. Record owner, SPNs, rotation and delegation settings.
- Entra emergency accounts live on the `*.onmicrosoft.com` domain, not synced or federated, using passkey/FIDO2 (VERIFIED_PRIMARY [W4], checked 2026-10-29).
- Exclude them from blocking Conditional Access policies, store credentials separately, and validate them regularly [W4].
- AD: keep DSRM passwords LAPS-managed or sealed, one restorable system-state backup per domain, and a rehearsed forest recovery plan [W5].
- AD CS: back up the CA key and database. Document CRL publication and what an expired CRL does to smart-card, VPN and 802.1X authentication.

## Operations and FOSS fit

- Patch rings: pilot -> early -> broad -> critical servers, with application compatibility checks and reboot orchestration.
- Endpoints: Windows Update for Business or Intune rings. Servers: WSUS, Configuration Manager, or Azure Update Manager/Arc, as present.
- Remote management: PowerShell remoting over WinRM/HTTPS or SSH, with Kerberos or certificate server verification, and JEA for delegated tasks.
- Plan SMB permissions, inheritance, shares and restore independently. Clusters: quorum/witness, storage, network, isolation.
- A cluster witness supplies votes, not compute or data capacity.
- FreeIPA, Samba AD and Linux services may meet some requirements. Prove protocol, GPO, schema, trust and migration fit; never assert drop-in equivalence.
- FOSS-first does not remove existing Windows requirements. List proprietary dependencies; never fabricate licensing conclusions.

## Patterns and anti-patterns

| Pattern                              | Use when                     | Anti-pattern                                      | Why it fails                                           |
| ------------------------------------ | ---------------------------- | ------------------------------------------------- | ------------------------------------------------------ |
| Enterprise access model with PAWs    | Any AD or Entra estate       | Domain admin signs in to workstations and servers | Tier 0 credentials cached on lower tiers get harvested |
| Windows LAPS per device              | Local admin accounts         | One local admin password set by image or GPO      | One leak gives lateral movement across the fleet       |
| gMSA / dMSA                          | Windows services             | User account with a non-expiring password         | No rotation; owner and SPNs unknown                    |
| Cloud-only emergency accounts        | Every Entra tenant           | Break-glass synced from AD, or using admin MFA    | An AD or MFA outage locks out both paths               |
| System-state backup plus forest plan | DC recovery                  | Roll a DC back from a hypervisor snapshot         | USN rollback corrupts replication                      |
| Protocol-level FOSS fit test         | Samba AD or FreeIPA proposed | Assume drop-in equivalence                        | GPO, schema or trust gaps appear after cutover         |

## Failure modes and tests

| Failure                  | Symptom                                    | Blast radius                          | Proving test                                                       |
| ------------------------ | ------------------------------------------ | ------------------------------------- | ------------------------------------------------------------------ |
| Clock skew over 5 min    | Kerberos logon and ticket failures         | Every client of the skewed DC or host | Alert on offset; resume a lab DC VM from snapshot and watch logons |
| Clients on public DNS    | No DC found; GPO not applied               | Clients at that site                  | SRV lookup from a client at each site                              |
| Replication broken       | Stale passwords and groups on some DCs     | Domain                                | `repadmin /replsummary` shows no failures                          |
| LAPS readable too widely | Non-admin role reads local admin passwords | Lateral movement fleet-wide           | Retrieval by the intended role succeeds; by another role fails     |
| Break-glass blocked      | Emergency sign-in denied by policy         | Tenant administration                 | Scheduled break-glass sign-in; the alert fires                     |
| Expired CRL              | Smart-card, VPN or 802.1X logons fail      | All certificate authentication        | Monitor CRL next-update; let a lab CRL expire                      |
| Sync server down         | Changes stop reaching Entra ID             | Cloud apps, per auth method           | Stop sync in the lab; record what breaks (UNVERIFIED until tested) |
| Circular bootstrap       | No hypervisor login during an AD outage    | Whole estate                          | Power off lab DC VMs; log in to the hypervisor locally             |

## Worked example

Estate: 40 Windows Server 2016 VMs; 2 change windows a week; each migration needs 2 windows (build and cutover).

1. Runway: 2026-10-29 to extended end 2027-01-12 is 75 days, about 10.7 weeks (VERIFIED_SECONDARY dates).
2. Demand: 40 servers x 2 windows = 80 windows. Supply: 10.7 weeks x 2 = 21 windows.
3. Gap: 59 windows. The plan cannot finish in time. Record the gap as a risk with an owner and a dated decision.
4. Options: add parallel windows, retire servers with no traffic first, or isolate the remainder. Price extended support only from a primary source.
5. Kerberos check: a DC VM paused 7 minutes and resumed without time sync is 420 s behind, over the 300 s default, so its tickets fail.
   Illustrative alerts: 60 s warning, 120 s critical; keep both well under 300 s.

## Review checklist

- [ ] Every server and endpoint class has release, build, join state and support dates from [W1].
- [ ] Each identity topology choice states which apps need Kerberos, LDAP, GPO or SMB.
- [ ] Time hierarchy runs from 3+ NTP sources to the PDC emulator; offset alerts fire well under 5 minutes.
- [ ] No circular bootstrap: hypervisor and backup have local break-glass logins; one DC sits in a separate failure domain.
- [ ] Tier 0 assets are listed; Tier 0 credentials never touch lower tiers; LAPS covers every device with tested retrieval rights.
- [ ] Emergency access accounts exist, alert on use and were tested this cycle.
- [ ] DC system-state backup, forest recovery plan, krbtgt procedure and CA key backup exist.
- [ ] Tests cover wired, VPN and offline logons, GPO, SRV lookup, replication, patch/reboot, isolated restore; untested items are listed.

## Further reading

Lifecycle:
- [W1] [Microsoft lifecycle: Windows Server 2025](https://learn.microsoft.com/lifecycle/products/windows-server-2025) - read this for authoritative support dates; change the slug for other products.

Identity and time:
- [W3] [Kerberos clock skew policy][w3url] - read this for the Kerberos skew default (VERIFIED_PRIMARY, checked 2026-10-29).
- [AD DS overview][addsurl] - read this for directory concepts (VERIFIED_PRIMARY, checked 2026-10-29).

Privileged access:
- [W2] [Windows LAPS overview][w2url] - read this for backup targets, DSRM and legacy LAPS status (VERIFIED_PRIMARY, checked 2026-10-29).
- [W6] [Enterprise access model][w6url] - read this for control/management/data planes (VERIFIED_PRIMARY, checked 2026-10-29).
- [W4] [Manage emergency access accounts in Entra ID][w4url] - read this for break-glass design (VERIFIED_PRIMARY, checked 2026-10-29).

Recovery:
- [W5] [AD forest recovery guide][w5url] - read this before designing DC backup and restore.
- [Reset the krbtgt password (forest recovery)][krbtgturl] - read this for the krbtgt procedure.

Baselines:
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) - read this for Windows Server/11 hardening baselines to tailor (pointer).

[w3url]: https://learn.microsoft.com/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/maximum-tolerance-for-computer-clock-synchronization

[addsurl]: https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview

[w2url]: https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview

[w6url]: https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model

[w4url]: https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access

[w5url]: https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide

[krbtgturl]: https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
