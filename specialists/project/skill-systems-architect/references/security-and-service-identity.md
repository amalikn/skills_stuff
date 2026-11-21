---
Title: Systems security and service identity
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Systems security and service identity: zero-trust framing, trust-boundary pass, SSH certificates vs keys, workload identity, secrets lifecycle and rotation, break-glass, supply chain and
  acceptance tests.
---

# Systems security and service identity

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Trust-boundary pass](#trust-boundary-pass)
- [Identity trust chain](#identity-trust-chain)
- [Human and workload access](#human-and-workload-access)
- [Secrets and break-glass](#secrets-and-break-glass)
- [Platform, recovery and shared review](#platform-recovery-and-shared-review)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Privileged identities, workloads, data, endpoints, management surfaces, supply chain and recovery assets.
- Human and machine authentication, authorization, secret issuance, rotation, audit and revocation.
- Physical/OOB access, hypervisor admin, storage deletion and backup encryption keys. A private subnet or encrypted disk alone is not a control design.

## Decision rules

| Decision                   | Rule and threshold                                                                                            | Evidence                                 |
| -------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Access decisions           | Per request, per identity and device posture, at a policy enforcement point. Network location grants no trust | NIST SP 800-207 [N3]                     |
| Fleet SSH                  | Prefer certificates (CA, principals, KRL) to static `authorized_keys`                                         | VERIFIED_PRIMARY [O1][O2]                |
| Access proxy TTL           | Short-lived certs per login; default TTLs are configuration-specific, read version-matched docs               | VERIFIED_PRIMARY [T1]                    |
| Human passwords            | No periodic change and no composition rules; change on compromise evidence or user request                    | VERIFIED_PRIMARY [N1]                    |
| Workload identity          | Prefer short-lived platform identities (X.509-SVID, JWT-SVID, cloud identity, service account token, gMSA)    | VERIFIED_PRIMARY [N4]                    |
| Static secrets             | Only when unavoidable: scoped per service and site, in the vault of record, rotated on schedule and exit      | Design rule                              |
| Certificate expiry         | Alert at 30/14/7 days; renew automatically (ACME)                                                             | Common pattern, UNVERIFIED as a standard |
| Issuer outage              | Decide in advance: fail closed, plus a named break-glass path                                                 | Design rule                              |
| Break-glass                | Must not depend on the IdP, CA, proxy, DNS or hypervisor it replaces                                          | Design rule                              |
| CA or signing key rotation | Publish new trust before retiring the old; overlap                                                            | Design rule                              |
| Backup admin               | Credentials in a separate trust domain from production admin                                                  | Design rule                              |
| Control catalogues         | Tailor NIST SP 800-53 or CIS per OS; never paste across Windows, Linux and macOS                              | Cited [N2]                               |

## Trust-boundary pass

Run this pass on every design that crosses a zone, tenant or credential domain.

1. List each boundary as an edge: from, to, protocol, authentication, encryption, filtering.
2. List the assets behind each boundary.
3. State attacker capabilities assumed (for example: any host on the user VLAN, one stolen laptop).
4. State explicit non-capabilities: what the attacker cannot do with those capabilities. This stops severity inflation.
5. Rank abuse paths by likelihood x impact, adjusted for controls already in place.
6. Ask 1-3 targeted questions before finalising.
7. Coverage check: every boundary has at least one threat, or an explicit "none found".

```text
Admin access trust boundaries (each ==== line is one row in the boundary table)

  user zone          +-------------------+
                     | admin laptop      |   X stolen: cert TTL bounds the damage
                     +-------------------+
                               | 1  HTTPS, IdP SSO + MFA
 ==== boundary 1 ==============|================================================
  access zone        +-------------------+
                     | access proxy + CA |   X CA key exposed: every host trusts it
                     +-------------------+
                               | 2  SSH, user cert, host cert, management ACL
 ==== boundary 2 ==============|================================================
  management zone    +-------------------+
                     | host sshd         |   X root on host: retained backups still safe
                     +-------------------+
                               | 3  backup protocol, separate credentials
 ==== boundary 3 ==============|================================================
  backup domain      +-------------------+
                     | backup repository |
                     +-------------------+

Legend: | flow crossing a boundary   ==== trust boundary   X compromise and its limit
```

| Edge              | Attacker can                               | Attacker cannot                                              | Top abuse path                                        |
| ----------------- | ------------------------------------------ | ------------------------------------------------------------ | ----------------------------------------------------- |
| 1 laptop -> proxy | Reach the proxy login; phish a user        | Reach host sshd directly                                     | Stolen session yields a cert, bounded by TTL          |
| 2 proxy -> sshd   | Use a valid cert for its listed principals | Log in as a principal not in the cert                        | Over-broad principals map to root                     |
| 3 host -> backup  | Write new backups                          | Delete or alter retained backups (when the repo enforces it) | Backup admin credentials kept in the production vault |

The table is illustrative; build the real one from the design's own edges.

## Identity trust chain

```text
Identity trust chain: every arrow needs an owner, a rotation interval and a tested failure mode

+------------------------------+  signs   +-------------------+  presents  +-------------------+
| root of trust: offline CA    | -------> | issuing CA or IdP | ---------> | short-lived cred: |
| key, IdP tenant, or vault    |          | policy: who, TTL, |            | SSH cert, X.509,  |
| master + hardware key        |          | principal, device |            | OIDC token, SVID  |
+------------------------------+          +-------------------+            +-------------------+
                                                   |                                |
                                                   | revoke: CA rotation,           v
                                                   | KRL/CRL, session revoke   +-------------------+
                                                   +-------------------------> | PEP: sshd, proxy, |
                                                                               | API; authz + UTC  |
                                                                               | audit off-host    |
                                                                               +-------------------+

Legend: --> issue, present or revoke   PEP = policy enforcement point
```

## Human and workload access

| Property           | Static `authorized_keys` | OpenSSH CA certificates                                         | Access proxy (e.g. Teleport)            |
| ------------------ | ------------------------ | --------------------------------------------------------------- | --------------------------------------- |
| Trust distribution | Every key on every host  | One CA public key per host (`TrustedUserCAKeys`)                | Agent/CA trust per node, central policy |
| Expiry             | None unless managed      | Validity interval set at signing (`ssh-keygen -V`)              | Short-lived certs issued per login      |
| Identity mapping   | Implicit per key         | Principals in cert; `AuthorizedPrincipalsFile` maps to accounts | Roles map users to logins and resources |
| Revocation         | Remove from every host   | KRL via `RevokedKeys`; short TTL limits exposure                | Central lock/session revoke             |
| Host authenticity  | TOFU `known_hosts`       | Host certificates + `@cert-authority`                           | Proxy-validated host certs              |

- OpenSSH certificate, principal and KRL behaviour: VERIFIED_PRIMARY [O1][O2], checked 2026-10-29.
- Teleport authentication is built on its certificate authorities and short-lived certificates (VERIFIED_PRIMARY [T1], checked 2026-10-29).
- Keep a static-key or console break-glass path that does not depend on the CA or proxy. Protect the CA key offline, or in an HSM or agent with audit.
- SPIFFE/SPIRE delivers SVIDs through the Workload API (VERIFIED_PRIMARY [N4], checked 2026-10-29).
- Certificates: record issuer hierarchy, trust distribution, expiry monitoring, automated renewal, revocation and CA disaster recovery.

> **Learned 2026-11-19** · Client-certificate trust anchors at a TLS edge · VERIFIED_PRIMARY (built and tested) · Source: continuum-app `caddy/Caddyfile`, `scripts/dev_pki.py`
> (b25dbf8); Caddy client_auth docs (caddyserver.com, read 2026-11-19) · Falsifier: an edge that checks the leaf's issuer or EKU beyond the chain.
> When devices and servers share one root, the edge's client-certificate pool must hold only the **device intermediate**, not the root: with the root as anchor, any
> certificate under it (the edge's own server certificate, another service's) verifies as a device. Give devices and servers separate intermediates, mark device roles client-only
> and server roles server-only, and have the backend match the forwarded certificate fingerprint against the one recorded at enrolment, trusting that header only from the edge.
>
> ```caddy
> client_auth {
> 	mode require_and_verify
> 	trust_pool file /edge/device-ca.pem   # the device intermediate only
> }
> ```

> **Learned 2026-11-19** · Keycloak issuer for clients on different networks · VERIFIED_PRIMARY (Keycloak 26.8 docs, hostname v2; live test) · Source: continuum-app `compose.yaml`
> (b25dbf8) · Falsifier: a Keycloak version where the issuer follows the request host with a full-URL `hostname`.
> Keycloak puts its frontend URL in every token's `iss`. Clients that reach it by different names (a VM by `host.orb.internal`, the Mac by `localhost`) get different issuers unless
> `hostname` is a fixed full URL; then `hostname-backchannel-dynamic=true` lets back-channel calls (device authorization, token) arrive by any name while the issuer and the
> approval link stay on the one URL a browser can open. Pick that URL by where the person approves, not where the agent runs.

## Secrets and break-glass

Lifecycle: create -> store (vault of record) -> distribute (runtime fetch, never git) -> use -> rotate -> revoke -> destroy.
Rotate at once on compromise or staff exit. Log access and name an owner.

| Secret class                  | Rotation trigger                                   | Notes                                                                                           |
| ----------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Human passwords               | Compromise evidence or user request only           | NIST SP 800-63B-4: verifiers SHALL NOT require periodic change and SHALL NOT impose composition |
|                               |                                                    | rules [N1]                                                                                      |
| Shared device/admin passwords | Staff exit, exposure, after break-glass use, and a | Per-device unique (LAPS-style) beats a fleet-wide value                                         |
|                               | set schedule                                       |                                                                                                 |
| API tokens / service creds    | Schedule + exit + exposure                         | Prefer short-lived tokens issued by an identity                                                 |
| CA and signing keys           | Planned ceremony; compromise                       | Rotation needs overlap: publish new trust before retiring old                                   |

- KeePassXC-style file vaults suit a small team when database, key file/hardware key and backups are controlled. Record the limit: no per-secret audit, no auto-rotation.
- Never place secrets in inventory systems, diagrams, logs or tickets.
- Break-glass per identity system: accounts, storage (split or sealed, offline copy), who may use it, trigger, alert on use, rotation and review after use.
- Test break-glass on a schedule and after identity-system changes.

> **Learned 2026-11-21** · device-side encryption with a shared per-user key · VERIFIED_PRIMARY (design and gate) · Source: Keybase per-user keys, https://book.keybase.io/docs/teams/puk
> (read 2026-11-21); continuum DL-109, DL-111, DL-112, DL-114 and continuum-app `apps/agent/src/keys.rs` (P4 gate 2026-11-21) · Falsifier: a design where the server can add a recipient without a
> device or person noticing.
> When devices share one user key sealed to each device, "the server never holds the key" holds only if the server cannot choose who the key is sealed to. A draft that asked the server for the
> recipient list (at enrolment, revocation and recovery-key change) let a compromised server seal the key to itself. Fixes: (1) the device set is written only by devices and authenticated with a key
> the server lacks (an HMAC keyed from the user key, or a signature chain as Keybase does); (2) a new device is approved by comparing a code derived from its public key on both screens, at least
> about 100 bits when the server relays the key, because a server that sees the real key first can grind a 6-digit code in seconds; (3) adding a device seals the current key and lets the chain open
> history; only removal rolls a generation. The server still checks shape and sequence (version + 1, exactly one device added, removal only) since it cannot check the MAC.
>
> ```rust
> let roster = keys::roster(&uk.identity, v, uk.generation, &devices, rec)?;      // HMAC keyed by HKDF(user identity); the server cannot forge it
> keys::verify_roster(&identity, &v["roster"], seen_version(state))?;            // every device refuses a bad MAC or a lower version
> ```

## Platform, recovery and shared review

- Plan privilege separation, Secure Boot where supported, patch and vulnerability management, application isolation, host policy, encryption, off-host logging.
- Check package, image and dependency provenance: signed repos, pinned digests, SBOM where available.
- Patch in rings with canaries; sequence reboots, firmware and dependencies. A snapshot rollback can revert credentials or certificates: assess first.
- Protect logs from tampering and overcollection; record retention and access owners.
- Ransomware or compromise: preserve evidence and follow incident scope. Never wipe hosts or delete logs as an unapproved diagnostic action.
- Network architect reviews exposure, segmentation, management paths, denied flows. Systems architect reviews host permissions, identity dependencies, recovery credentials.
- Use skill-coder for secret-safe implementation.
- Record exceptions, compensating controls and risk owners. A checklist does not make a design "compliant" or "secure".

## Patterns and anti-patterns

| Pattern                             | Use when                  | Anti-pattern                                   | Why it fails                                    |
| ----------------------------------- | ------------------------- | ---------------------------------------------- | ----------------------------------------------- |
| SSH CA with short-lived certs       | Fleets of hosts           | Static keys copied to every host               | No expiry; revocation means touching every host |
| Platform-issued workload identity   | Services calling services | Long-lived API token in a config file          | Leaks persist until someone notices             |
| Overlapping CA rotation             | CA or signing key change  | Retire old trust and publish new at once       | Every client fails during the gap               |
| Independent break-glass             | Any IdP, CA or proxy      | Emergency account behind the same IdP or proxy | The outage locks out the recovery path          |
| Separate backup trust domain        | Ransomware scope          | Backup admin in the production directory       | One compromise deletes production and backups   |
| Boundary pass with non-capabilities | Threat review             | List every theoretical attack as high          | Severity inflation hides the real paths         |
| Client-authenticated recipient set  | End-to-end encryption     | Server hands out the list of keys to seal to   | A compromised server seals the key to itself    |

## Failure modes and tests

| Failure                                | Symptom                         | Blast radius                | Proving test                                           |
| -------------------------------------- | ------------------------------- | --------------------------- | ------------------------------------------------------ |
| Credential not revoked                 | Old key or token still works    | Everything it reached       | Rotate, then prove the old credential fails            |
| Certificate expiry                     | TLS or SSH handshakes fail      | Every client of the service | Expiry alert test; renew a lab cert past its date      |
| CA or proxy outage                     | No new logins                   | All managed hosts           | Stop the CA/proxy in the lab; use break-glass          |
| CA key exposed                         | Attacker mints valid certs      | Every host trusting the CA  | Rotation ceremony drill with overlap                   |
| Over-broad privilege                   | Role can do denied actions      | Data and hosts in scope     | Least-privilege test: denied actions are refused       |
| Backup reachable from production admin | Backups deleted with production | All recovery points         | Attempt deletion with production credentials; it fails |
| Secret in git, logs or tickets         | Scanner hit or leaked value     | Systems using that secret   | Secret scan of repos and log samples                   |

> **Learned 2026-11-10** · SSH host-key trust for unattended tunnels · VERIFIED-OBSERVED (one site box, 22 days) · Source: ansible-wifi
> `roles/smc_autossh/templates/autossh-teleport-openssh.service.j2:15` · Falsifier: a reverse tunnel that stays up while known_hosts holds a
> **different** key for the server
> `StrictHostKeyChecking=no` only accepts **unknown** hosts. When known_hosts holds a **different** key for the server, OpenSSH still connects
> for key auth but disables port forwarding ("forwarding disabled due to host key check failure"), so a reverse tunnel with
> `ExitOnForwardFailure=yes` fails and autossh restarts it forever while the unit reads `active`, `NRestarts=0`. Ordinary commands over the
> same trust (rsync by name) keep working, which hides it. Monitor the tunnel by its **listener on the server**, not the client unit. Fix by
> installing the server's keys read on the server itself over another trusted path and compared by fingerprint with a healthy client; never
> trust whatever answers (`ssh-keyscan`).
>
> ```ini
> # autossh-teleport-openssh.service.j2:15 (ansible-wifi rise 0fc086ca)
> ExecStart=/usr/bin/autossh -M 0 -i <key> -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes \
>   -o ServerAliveInterval=20 -o ServerAliveCountMax=3 -N -4 -R {{ openssh_remoteport }}:127.0.0.1:22 <user>@{{ teleport_address }}
> ```

## Worked example

Fleet: 400 Linux hosts. Compare a leaked static SSH key with a leaked short-lived certificate.

1. Static key: exposure lasts until removal from every host. At 2 minutes per host by hand, 400 hosts take 800 minutes, about 13.3 hours after detection.
2. Certificate with an 8 hour TTL: exposure ends at expiry with no action. A KRL push shortens it further.
3. With config management at 50 hosts in parallel and 1 minute per batch, a KRL reaches 400 hosts in 8 minutes.
4. Boundary pass result: edge 2 ranks highest when principals map to root, so the fix is narrower principals, not more MFA.
5. TTL and timings are illustrative; read the deployed version's TTL settings [T1].

## Review checklist

- [ ] Every trust boundary is an edge with protocol, auth, encryption and filtering, and has a threat or an explicit "none found".
- [ ] Attacker capabilities and non-capabilities are written down; abuse paths are ranked; every credential arrow has an owner and a rotation interval.
- [ ] Fleet SSH uses certificates; the CA key is offline or in an HSM; a CA-independent break-glass exists.
- [ ] Workloads use short-lived identities; remaining static secrets are scoped and in the vault of record.
- [ ] Human password policy follows [N1]; rotation tests prove the old credential fails.
- [ ] Backup credentials sit in a separate trust domain; deletion from production fails; exceptions have compensating controls and owners.

## Further reading

Identity and zero trust:
- [N1] [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html) - read this for authenticator and password rules (VERIFIED_PRIMARY, checked 2026-10-29).
- [N3] [NIST SP 800-207 Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final) - read this for PEP/PDP framing.
- [N2] [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) - read this as the control catalogue to tailor.

SSH and access:
- [O1] [ssh-keygen(1) CERTIFICATES and KRL](https://man.openbsd.org/ssh-keygen.1) - read this for signing, validity, principals and KRLs (VERIFIED_PRIMARY, checked 2026-10-29).
- [O2] [sshd_config(5)](https://man.openbsd.org/sshd_config.5) - read this for TrustedUserCAKeys, AuthorizedPrincipalsFile, RevokedKeys (VERIFIED_PRIMARY, checked 2026-10-29).
- [T1] [Teleport authentication architecture][t1url] - read this for CA and short-lived cert design (VERIFIED_PRIMARY, checked 2026-10-29).

Workload identity:
- [N4] [SPIFFE concepts](https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/) - read this for SVIDs, trust bundles and the Workload API (VERIFIED_PRIMARY, checked 2026-10-29).

Baselines:
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) - read this for per-OS hardening baselines (pointer).

[t1url]: https://goteleport.com/docs/reference/architecture/authentication/
