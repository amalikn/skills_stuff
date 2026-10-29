---
Title: BGP peer policy template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: >-
  One row per BGP peer covering role, import and export policy, default deny, prefix limits, RPKI origin validation, GTSM, TCP-AO, BFD, communities,
  graceful shutdown and the test that proves each.
---

# <routing domain> BGP peer policy

Based on (each checked 2026-10-29 against the RFC text, VERIFIED_PRIMARY):

- BGP roles and the Only to Customer (OTC) attribute, roles Provider, Customer, RS, RS-Client, Peer: [RFC 9234](https://www.rfc-editor.org/rfc/rfc9234.html).
- eBGP routes are neither accepted nor advertised without an explicit import or export policy: [RFC 8212](https://www.rfc-editor.org/rfc/rfc8212.html).
- Route origin validation states Valid, Invalid, NotFound: [RFC 6811](https://www.rfc-editor.org/rfc/rfc6811.html).
- GTSM (send TTL 255, accept only the expected TTL from configured peers): [RFC 5082](https://www.rfc-editor.org/rfc/rfc5082.html).
- TCP-AO, which obsoletes TCP MD5 ([RFC 2385](https://www.rfc-editor.org/rfc/rfc2385.html)): [RFC 5925](https://www.rfc-editor.org/rfc/rfc5925.html).
- BFD: [RFC 5880](https://www.rfc-editor.org/rfc/rfc5880.html), single hop [RFC 5881](https://www.rfc-editor.org/rfc/rfc5881.html), multihop [RFC 5883](https://www.rfc-editor.org/rfc/rfc5883.html).
- GRACEFUL_SHUTDOWN community 65535:0; receiver sets LOCAL_PREF low (RECOMMENDED 0): [RFC 8326](https://www.rfc-editor.org/rfc/rfc8326.html).
- Maximum-prefix Cease subcode 1 "Maximum Number of Prefixes Reached": [RFC 4486](https://www.rfc-editor.org/rfc/rfc4486.html).
- BLACKHOLE community 65535:666: [RFC 7999](https://www.rfc-editor.org/rfc/rfc7999.html). Operations and security baseline: [RFC 7454](https://www.rfc-editor.org/rfc/rfc7454.html).

## Contents

- [How to use](#how-to-use)
- [1. Peers](#1-peers)
- [2. Policy per peer](#2-policy-per-peer)
- [3. Session protection](#3-session-protection)
- [4. Communities](#4-communities)
- [5. Tests that prove each control](#5-tests-that-prove-each-control)
- [6. Review state](#6-review-state)

## How to use

- One row per eBGP or iBGP session (or per peer class where sessions are identical; list the members).
- Complements [routing-policy](routing-policy.md), which holds prefix ownership and path selection for the whole domain. This sheet is per session.
- Write intent first; render per platform afterwards. Every platform default named here needs version-matched vendor docs and a label.
- Role (RFC 9234) drives the import and export intent: from a Customer accept its cone and send everything; from a Provider or Peer accept routes, send only own and customer routes.
- RFC 8212 behaviour is a default on compliant implementations; record whether the platform has it and do not rely on it in place of a written policy.
- RPKI: decide per role what Invalid does (drop is the usual intent for external peers); NotFound is accepted. Say who runs the validators.
- Every control has a test in section 5 and a result. "Configured" is not "proved".
- Rules and failure modes: [routing-and-switching](../references/routing-and-switching.md). Red flags: [red-flags](../references/red-flags.md).

```text
Peer roles (RFC 9234) and where routes may go
                +------------+
                |  provider  |   routes from here: to customers only
                +------------+
                      |
+----------+    +------------+    +----------+
|   peer   |----|   local AS |----| RS (IXP) |   routes from peer / RS: to customers only
+----------+    +------------+    +----------+
                      |
                +------------+
                |  customer  |   routes from here: to everyone
                +------------+
OTC marks routes that may go only to customers; OTC on a route sent up or sideways = leak
```

## 1. Peers

| Peer ID | Peer name / AS | Local AS | Role (local / remote) | AFI/SAFI            | Addresses (local / remote) | Single or multihop | Owner | Label |
| ------- | -------------- | -------- | --------------------- | ------------------- | -------------------------- | ------------------ | ----- | ----- |
| P1      | <name> / <asn> | <asn>    | Customer / Provider   | ipv4 / ipv6 unicast | <ip> / <ip>                | single             |       |       |
| P2      | <name> / <asn> | <asn>    | Peer / Peer           |                     |                            |                    |       |       |

Role strict mode (session refused without a matching role capability): *yes / no per peer, and why.*

## 2. Policy per peer

| Peer ID | Import accepts        | Import rejects                   | Import actions   | Export sends       | Export actions | RFC 8212 default on platform | ROV action (Valid / Invalid / NotFound) |
| ------- | --------------------- | -------------------------------- | ---------------- | ------------------ | -------------- | ---------------------------- | --------------------------------------- |
| P1      | default or full table | bogons, own space, too-specific, | local-pref       | own + customer     | none / prepend | yes (version, source) / no   | accept / drop / accept                  |
|         |                       |   AS-path too long               |   <n>, tag       |   aggregates       |                |                              |                                         |
| P2      | peer cone (IRR or     | as P1, plus anything with a      | local-pref       | own + customer     |                |                              |                                         |
|         |   ASPA list)          |   provider in the path           |   <n>, tag       |   aggregates       |                |                              |                                         |

Prefix limits:

| Peer ID | Expected prefixes v4 / v6 | Warning threshold | Hard limit | Action at limit (warn only, Cease, restart after <n> min) | Who is alerted |
| ------- | ------------------------- | ----------------- | ---------- | --------------------------------------------------------- | -------------- |
| P1      | <n> / <n>                 | <n>%              | <n> / <n>  | Cease (RFC 4486 subcode 1), restart after <n> min         |                |

## 3. Session protection

| Peer ID | GTSM (TTL 255) | Auth (TCP-AO key ID; MD5 only if no AO) | Key custody and rotation | BFD (interval x mult, hop type) | Graceful restart | Max AS-path length | Label |
| ------- | -------------- | --------------------------------------- | ------------------------ | ------------------------------- | ---------------- | ------------------ | ----- |
| P1      | on             | TCP-AO, key ID <n>                      | *where, who; no secrets* | <n> ms x <n>, single            | yes / no         | <n>                |       |

- GTSM fits directly connected peers; a multihop session needs an agreed hop count or GTSM off (RFC 5082). Record which.
- Never put key material in this document; record only where it lives and who rotates it.

## 4. Communities

| Community | Meaning                                      | Set on             | Acted on         | Action                                                     |
| --------- | -------------------------------------------- | ------------------ | ---------------- | ---------------------------------------------------------- |
| <asn>:<n> | learned from customer P1                     | import P1          | all exports      | export to everyone                                         |
| <asn>:<n> | learned from provider or peer                | import P1/P2       | exports to P1/P2 | do not export                                              |
| 65535:0   | GRACEFUL_SHUTDOWN (RFC 8326)                 | before maintenance | every import     | set LOCAL_PREF 0 so traffic moves before the session drops |
| 65535:666 | BLACKHOLE (RFC 7999), only if peer offers it | operator           | peer             | discard at peer; /32 and /128 only                         |

## 5. Tests that prove each control

| Control           | Test (lab or maintenance window)                               | Expected result                                                 | Measured | Date / by |
| ----------------- | -------------------------------------------------------------- | --------------------------------------------------------------- | -------- | --------- |
| Default deny      | Remove the import policy in lab; check Adj-RIB-In to Loc-RIB   | Nothing accepted or sent (RFC 8212) or documented gap           |          |           |
| Import filter     | Peer announces a bogon, own prefix, too-specific               | Rejected; counter increments                                    |          |           |
| Export filter     | Inject a provider route; check what P2 receives                | Not exported                                                    |          |           |
| Role / OTC        | Peer with mismatched role; send a route with OTC to a provider | Role Mismatch (code 2, subcode 11) in strict mode; leak blocked |          |           |
| ROV               | Announce a test prefix with a ROA for another AS               | Invalid; dropped or tagged as designed                          |          |           |
| Prefix limit      | Announce limit + 1 prefixes                                    | Warning at threshold; Cease subcode 1 at limit                  |          |           |
| GTSM              | Send BGP from a host two hops away                             | Dropped before TCP                                              |          |           |
| TCP-AO            | Wrong key ID or key                                            | Session does not establish                                      |          |           |
| BFD               | Drop the link silently (no carrier loss)                       | Session down within interval x multiplier                       |          |           |
| Graceful shutdown | Tag 65535:0 on export; watch traffic                           | Traffic moves before the session is shut                        |          |           |

## 6. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
