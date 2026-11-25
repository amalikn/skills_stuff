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

> **Learned 2026-11-22** · testing passkey-only flows without a person · VERIFIED_PRIMARY (built and run: registration, device grant, portal step-up and CLI, all accepted by
> Keycloak 26.8.2) · Source: continuum-app `scripts/soft_passkey.py`, `scripts/devbot.py` (cddb5cd); Red Hat KB 6988073 · Falsifier: a Keycloak release that puts the real
> `auth_time` in password-grant tokens.
> A password grant (direct access grant) does not stand in for a person in a step-up design: Keycloak's password-grant tokens carry no real `auth_time`, so any "signed in within
> N minutes" check fails, and enabling it is an exception to a passkey-only rule. A software WebAuthn authenticator does: an ES256 key (signed with `openssl`, key on stdin),
> attestation "none", flags UP+UV, answering the IdP's own registration and sign-in pages, so the test user passes the real browser flow, device grant and step-up. Keep it to
> dev and test realms (refuse elsewhere), its key in the operator's vault, and a guard that fails if product code ever names the test user.
>
> ```python
> auth_data = sha256(rp_id) + bytes([0x05]) + (0).to_bytes(4, "big")          # UP+UV, no counter
> cd = json.dumps({"type": "webauthn.get", "challenge": challenge, "origin": origin, "crossOrigin": False})
> sig = openssl(["dgst", "-sha256", "-sign", "/dev/stdin", data_file], key_pem)  # DER ES256
> ```

> **Learned 2026-11-22** · signing in on an untrusted, managed browser with a phone passkey · VERIFIED_PRIMARY (CTAP 2.2 section 11.5; Windows passkeys docs; Chrome and Edge
> policy files, read 2026-11-22) · Source: continuum `docs/research/guest-pc-20261122/browser-constraints.md` · Falsifier: a browser or OS adding a Bluetooth-free hybrid transport.
> WebAuthn hybrid (QR on the PC, passkey on the phone) needs Bluetooth on the PC (a proximity advert) and the CTAP relay domains (`cable.ua5v.com`, `cable.auth.com`); IT can
> block Bluetooth by policy (Windows Bluetooth CSP) although no browser policy turns hybrid off. Design a Bluetooth-free path that always works: the guest page shows a short-lived
> code and QR, the phone (already signed in with its passkey) approves it after a step-up while showing the guest's browser and address, and the guest gets a first-party session
> cookie. It has the device-code phishing exposure, so: one use, two minutes, the code and requester shown on the phone.

> **Learned 2026-11-23** · Keycloak: a sub-flow shared by two top-level flows breaks sign-in on a fresh import · VERIFIED_PRIMARY (Keycloak 26.8.2 debug log; fresh import
> FAIL before, PASS after) · Source: continuum BUG-464; continuum-app `keycloak/realm/continuum.json` (300a38d) · Falsifier: a fresh import where two top-level flows share one
> sub-flow and the username step still moves on. When the browser flow and another top-level flow (here device approval) both reference the same sub-flow, the form post after
> the username resolves through the wrong parent ("Cannot find execution in the authentication flow, reseting flow") and the username page simply returns, with no error and no
> login event. A live realm built by scripts can work while the realm file does not: give each top-level flow its own copies in the file, and compare a fresh import with the live
> realm (continuum-app `scripts/keycloak_realm_diff.py`, a partial export of each, flattened).

> **Learned 2026-11-23** · Keycloak RP-initiated logout from a backend-for-frontend portal · VERIFIED_PRIMARY (keycloak/keycloak main: server_admin sso-protocols, LogoutEndpoint.java;
> live probe) · Source: continuum BUG-463; continuum-app `apps/coordinator/src/portal/login.rs` (07e6a89) · Falsifier: a sign-out that clears only the portal cookie and still ends the
> session. Clearing the portal's own session is not a sign-out: the Keycloak SSO session signs the person straight back in (one token exchange per click in the log). Keep the ID
> token from the code exchange, redirect to `/protocol/openid-connect/logout` with `client_id`, `id_token_hint` (no confirmation page) and `post_logout_redirect_uri`, which must be
> listed in the client attribute `post.logout.redirect.uris`; several values join with `##` (live: listed 302, unlisted 400). Ending the SSO session also ends tokens other clients
> got through it (a device-grant CLI approved in the same browser asked to sign in again).

> **Learned 2026-11-23** · Keycloak levels of authentication (ACR) for a fresh-passkey step-up · VERIFIED_PRIMARY (throwaway Keycloak 26.8.2, software passkey) · Source: continuum
> `spikes/p5-acr` (2d2a654), DL-174 · Falsifier: a device-grant token carrying the requested acr. With `acr.loa.map` and 'Condition - Level of Authentication' sub-flows, the code
> flow honours `acr_values` and essential `claims` (token `acr` names the level, max-age 0 prompts every time), but the device authorization grant ignores both (token keeps the
> base level), so a CLI or agent step-up cannot be checked by name; keep `auth_time` for that path. The username step must sit outside the level sub-flows (inside one, Keycloak
> restarts the flow after the username), and a browser with no session asking for the higher level is prompted twice.

### Test identities with software authenticators

> **Learned 2026-11-23** · identity design, any IdP with WebAuthn and TOTP · VERIFIED_PRIMARY (Keycloak 26, continuum dev stack: 57
> end-to-end checks; wrong second factor refused; token azp/aud checked) · Source: continuum-app `scripts/devbot/`, `scripts/dev-stack/keycloak_sensitive.py`;
> skill-coder design-patterns P-85 · Falsifier: a flow the test identity passes that a person with the same factors cannot

- Give the test suite its own identity in the real IdP with software authenticators (a WebAuthn key pair, a TOTP secret) kept in the
  vault, so step-up, device-grant and second-factor flows are proven end to end without a person. Scope it: its own devices and
  workspaces only, never a person's; never recreate the realm (people's passkeys are bound to it).
- Second factor for sensitive actions without ACR: a dedicated client whose browser flow is passkey then OTP (both REQUIRED; password
  bootstrap disabled; the passkey sub-flow REQUIRED, not "if configured"); the resource server accepts those actions only with
  `azp` = that client and a fresh `auth_time`. The same flow covers the device grant (its verification re-enters the client's browser flow).
- Traps seen: the OTP required action may be unregistered in an imported realm ("credential setup required"); a client enforcing PKCE
  needs the challenge on the device grant too; TOTP replays are refused and count towards brute-force lockout; an in-memory
  authorisation store loses grants on restart while the database still marks them written (resync on start).

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

> **Learned 2026-11-21** · break-glass keys and vault custody · USER_STATED (operator decision after review) · Source: continuum DL-116 · Falsifier: a recovery key stored where an
> enrolled device can read it with no prompt.
> A vault that unlocks with no prompt (master password in the OS keychain, a CLI wrapper reading it) is readable by every process on that machine; if the machine is one of the devices a recovery
> key recovers, the key falls with it. Keep break-glass keys in a separate vault whose password is typed, kept in two places (a synced copy that survives losing the machine, an offline copy),
> and generate the key straight into the vault so it is never printed or passed as an argument.

> **Learned 2026-11-22** · a second copy of a private key on an encrypted removable drive · VERIFIED_PRIMARY (built and self-tested) · Source: continuum-app
> `scripts/devbot_copies.py`, `apps/cli/src/keystore.rs` (00c1f1f; DL-155) · Falsifier: a platform where an unmounted volume path cannot be written. On macOS an unplugged
> drive leaves its path under `/Volumes`, and a write there can land on the internal disk. Write the copy only when the drive is mounted (`os.path.ismount(<mount point>)`) or
> when the target folder already exists, force 0600 on every write (an existing file keeps its old mode), restore a missing copy from the other on read, and treat an
> absent drive as a warning so automation continues. Throwaway test credentials must be kept off the mirror (they would overwrite or, at logout, delete the real copy).

```python
def _usable(path, drive):  # drive None: always-present disk
  return drive is None or os.path.ismount(drive)
```

> **Learned 2026-11-22** · moving an owner check into a relationship-based authoriser · VERIFIED_PRIMARY (OpenFGA v1.22.1 measured) · Source: continuum
> `spikes/p5-openfga/README.md` (73b7280) · Falsifier: a model whose relation equals the SQL rule exactly. A check costs about 0.4 ms median (0.6 ms p95) over a kept-alive
> connection on a quiet host, under 6 ms p95 under CPU load: affordable per request. The risk is semantic: a relation computed from organisation membership widens "only the
> creator" to every member. Compare the relation's reach with the rule it replaces before moving it, and add the dependency's failure mode (authoriser down = 503 on every
> checked route) to the design.

> **Learned 2026-11-22** · a phone as the passkey for a dev portal · UNVERIFIED (from the WebAuthn rules as known; confirm against the W3C WebAuthn Level 3 RP ID and
> secure-context sections, https://www.w3.org/TR/webauthn-3/) · Source: continuum TASK-413, TASK-455 · Falsifier: a phone passkey prompt on a plain-HTTP LAN IP page.
> A dev portal on `127.0.0.1` cannot be opened from a phone, and moving it to `http://<LAN IP>` does not help: passkeys need a secure context (HTTPS, or `localhost`)
> and an RP ID that is a domain, never an IP, and a passkey made for `localhost` is unusable under any other name. On a dev stack the page stays on the computer and
> the phone can only be the authenticator through the browser's hybrid QR flow, and only if it holds a passkey for that RP ID; when the account's only passkey was made
> on the computer, the browser offered no phone option at all (observed; cause inferred, not confirmed). A phone that opens the page itself needs HTTPS under a hostname
> it trusts and a passkey registered for that hostname: a deployment or network design step, not a dev setting.

> **Learned 2026-11-22** · an authorisation model with no source for its relations · VERIFIED_PRIMARY (code read; fixed by migration and consumer) · Source: continuum-app
> `migrations/0013_organisation_member.sql`, `src/authorise.rs` (cbffb5a; DL-166) · Falsifier: none. The OpenFGA model derived `can_plan` from organisation membership,
> but no table recorded members and only tests wrote the member and owner tuples, so every real person would have been refused once a route relied on it. Before moving
> a check into a relationship authoriser, trace each relation back to the stored fact and the code that writes its tuple; write tuples from that fact by the same
> consumer that writes the others, and backfill existing rows.

> **Learned 2026-11-25** · a hypervisor vTPM as a key store (Proxmox VE swtpm) · VERIFIED_SECONDARY (reasoning from Proxmox storing the vTPM state as a VM disk volume,
> `tpmstate0`; no extraction tried) · Source: continuum TD-606, DL-232 · Falsifier: a restored or cloned VM whose vTPM refuses to unseal keys sealed in the original.
> A software vTPM's state is a file (a disk volume) on the host. Host root, VM backups and snapshots, and restores or clones all copy it, so a key sealed in a vTPM
> is held by whoever holds the host or any backup of the VM. A vTPM proves the code path (seal, unseal, attestation calls) and not key custody. Treat VM backups that
> include vTPM state as secrets, and prove custody on real TPM hardware before trusting real workloads to it.

## Platform, recovery and shared review

- Plan privilege separation, Secure Boot where supported, patch and vulnerability management, application isolation, host policy, encryption, off-host logging.
- Check package, image and dependency provenance: signed repos, pinned digests, SBOM where available.
- Patch in rings with canaries; sequence reboots, firmware and dependencies. A snapshot rollback can revert credentials or certificates: assess first.
- Protect logs from tampering and overcollection; record retention and access owners.
- Ransomware or compromise: preserve evidence and follow incident scope. Never wipe hosts or delete logs as an unapproved diagnostic action.
- Network architect reviews exposure, segmentation, management paths, denied flows. Systems architect reviews host permissions, identity dependencies, recovery credentials.
- Use skill-coder for secret-safe implementation.
- Record exceptions, compensating controls and risk owners. A checklist does not make a design "compliant" or "secure".

> **Learned 2026-11-22** · Keycloak passkey-only sign-in: what the flow conditions mean, and the bootstrap password · VERIFIED_PRIMARY (Keycloak 26.8.2 admin API and a browser-flow probe)
> · Source: continuum TASK-190, TD-331; continuum-app `keycloak/realm/continuum.json`, `scripts/keycloak_finish_user.py` (62e5ea1) · Falsifier: a password accepted for a user holding a passkey.
> `Condition - credential` with `included: false` is true when that credential was NOT USED in the current authentication, not when the user lacks it; paired with a passkey subflow gated by
> `Condition - user configured`, a user with a passkey is only ever offered WebAuthn (a probe without a passkey saw no password field and no "try another way"). The bootstrap password stays stored
> (`temporary: false`) after the passkey is registered; if the passkey is later removed the password signs in again. Delete it once a passkey exists, and prove it with a throwaway user:

```python
# continuum-app scripts/keycloak_finish_user.py (62e5ea1): finish refuses without a passkey, then
for c in admin(token, "GET", f"/users/{uid}/credentials") or []:
  if c["type"] == "password":
    admin(token, "DELETE", f"/users/{uid}/credentials/{c['id']}")
```

> **Learned 2026-11-22** · BFF login with a SameSite=Strict cookie loops after a sign-in on the identity provider's page · VERIFIED_PRIMARY (Chrome, live loop: five sessions a second) ·
> Source: continuum BUG-333; continuum-app `apps/coordinator/src/portal/login.rs` (2091a4e) · Falsifier: a browser that sends Strict cookies on a redirect chain started on another site.
> When the person signs in on the IdP's page (another site: `localhost:18080` vs `127.0.0.1:8080`, or another registrable domain), the navigation chain is cross-site, so the browser withholds the
> Strict session cookie on the 303 that follows the callback; the page sees no session, sends the browser to the IdP, whose SSO session bounces back, and it loops. A silent SSO sign-in (no IdP page)
> hides the bug until a step-up (`prompt=login`) forces one. Keep Strict and answer the callback with a page of your own that moves on, so the next request starts same-site:

```rust
// continuum-app apps/coordinator/src/portal/login.rs callback (2091a4e)
let body = format!("<!doctype html><meta charset=\"utf-8\"><meta http-equiv=\"refresh\" content=\"0;url={to}\"><title>Continuum</title><p>Signed in. <a href=\"{to}\">Continue</a></p>");
(StatusCode::OK, [(header::SET_COOKIE, set), (header::CACHE_CONTROL, "no-store".to_string())], Html(body)).into_response()
```

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

> **Learned 2026-11-24** · a step-up sign-in that returns to an existing session through a cross-site redirect · VERIFIED_PRIMARY (portal tests and live devbot check) ·
> Source: continuum TASK-535; continuum-app `apps/coordinator/src/portal/sensitive.rs` (5ba11ac) · Falsifier: a browser that sends a SameSite=Strict cookie on the IdP's redirect back.
> The callback of a second sign-in (e.g. passkey plus TOTP through a dedicated client) cannot read the session cookie, for the same cross-site reason as the
> 2026-11-22 entry above, so it cannot tell which session to mark. Bind it in the single-use login state instead: the start, a same-site request that carries the
> cookie, stores the session's digest with the state; the callback accepts only a state that names a session, checks the token's `azp` is the step-up client and
> its subject is the session's own, and updates that session. Keep the two logins' states apart (a normal callback refuses a step-up state and the reverse).

```rust
// continuum-app apps/coordinator/src/portal/sensitive.rs (5ba11ac): consume the state that names the session, then mark it
let row = sqlx::query("DELETE FROM portal_login WHERE state = $1 AND session_sha256 IS NOT NULL AND created_at > now() - interval '10 minutes' RETURNING verifier, return_to, session_sha256")
// ... exchange as the public step-up client, require azp == continuum-sensitive, then:
"UPDATE portal_session SET sensitive_auth_time = to_timestamp($3), auth_time = GREATEST(auth_time, to_timestamp($3))
   WHERE session_sha256 = $1 AND subject = $2 AND expires_at > now()"
```

> **Learned 2026-11-24** · secrets on a command line, and where a short-lived token may rest · VERIFIED_PRIMARY (macOS 27.2: `ps -axo user,args` shows another
> account's full arguments; continuum-app `apps/cli/src/keystore.rs` 16fa9e0) · Source: continuum BUG-548, FR-546 options record
> docs/architecture-review/options/fr-546-agent-sensitive-window-options-20261124_1319.md, DL-210 · Falsifier: a host where another user cannot list arguments.
> A token passed as an argument (`security add-generic-password ... -w <token>`) is readable by every local user while the process runs; send it on stdin
> (`security -i` with the command on stdin, `secret-tool store` reads stdin) and refuse values that could change the parsed command. For a token the server
> refuses after a short window (auth_time + 300 s), backup, sync and swap exposure are moot; what decides the place is same-user access, which every reuse
> option grants equally: a 0600 file in the per-user runtime folder (macOS `getconf DARWIN_USER_TEMP_DIR`, 0700 and outside Time Machine; Linux
> `$XDG_RUNTIME_DIR`) was chosen over the OS keystore and an agent socket, used only while `now < min(exp, auth_time + 300) - 15 s`.

> **Learned 2026-11-24** · Keycloak device authorization grant on a client that enforces PKCE · VERIFIED_PRIMARY (Keycloak 26.8.2, dev realm) ·
> Source: continuum TASK-536; continuum-app `apps/agent/src/enrol.rs` (80a65ce) · Falsifier: the same client accepting a device-grant start without `code_challenge`.
> A public client with `pkce.code.challenge.method = S256` refuses the device-grant start (`/protocol/openid-connect/auth/device`) with 400 unless it carries
> `code_challenge` and `code_challenge_method`, and the token poll then needs `code_verifier`; a wrong verifier gets `invalid_grant`. Send PKCE on every device
> grant: a client without enforcement accepts it too.

> **Learned 2026-11-25 (b)** · break-glass copy into a typed-password recovery vault (KeePassXC CLI 2.8) · VERIFIED_PRIMARY (tested on a throwaway
> vault: create, copy, exact value read back, rerun skip, wrong password refused) · Source: home NAS project `scripts/nas_recovery_copy.sh`
> (commit 98ab4a7), DL-039 · Falsifier: a copied entry whose value differs from the source, or a run that stores the recovery password anywhere
> Applying the 2026-11-21 custody rule takes one operator command: the script prompts for the recovery vault password (`read -s`), creates the vault
> when missing, copies only the listed break-glass entries that are missing, and proves each copy by reading it back (length, and in the test the
> exact value). The secret moves only through pipes (`keepassxc-cli add -p` reads the master then the value from stdin); the agent never sees the
> recovery password, so the step is handed to the operator and recorded in the project's operator steps. Test it with a stub of the main-vault reader.
> ```bash
> value="$(kp show -s -a Password "$e" | tr -d '\n')"
> printf '%s\n%s\n%s\n' "$RPW" "$value" "$value" | keepassxc-cli add -q -p "$VAULT" "$e" >/dev/null
> got="$(printf '%s\n' "$RPW" | keepassxc-cli show -q -s -a Password "$VAULT" "$e" | tr -d '\n' | wc -c)"
> ```
