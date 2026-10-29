---
Title: Routing policy template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Prefix ownership, per-peer import and export policy, communities, filters, protection limits and measured failover expectations for one routing domain.
---

# <routing domain> routing policy

Based on:

- BGP operations and security: [RFC 7454](https://www.rfc-editor.org/rfc/rfc7454.html).
- Default eBGP deny without policy: [RFC 8212](https://www.rfc-editor.org/rfc/rfc8212.html).
- Communities [RFC 1997](https://www.rfc-editor.org/rfc/rfc1997.html) and large communities [RFC 8092](https://www.rfc-editor.org/rfc/rfc8092.html).

## How to use

- Write policy as intent per peer class first; render it per platform afterwards.
- Every session has an explicit import and export policy. Nothing is accepted or sent by default.
- Each prefix has one owning originator.
- State the expected path in normal and failed states, with measured convergence. "It fails over" is not a criterion.
- Label platform behaviour facts with version and source. Exact syntax belongs to the platform specialist and version-matched vendor docs.
- Rules, failure modes and a convergence worked example: [routing-and-switching](../references/routing-and-switching.md).

## 1. Domain summary

| Field                     | Value                                                               |
| ------------------------- | ------------------------------------------------------------------- |
| ASN(s) / private ASN plan | <asn> / <range and allocation rule>                                 |
| IGP / overlay / BGP roles | *e.g. underlay eBGP per leaf, EVPN overlay, iBGP to route reflectors* |
| VRFs in scope             | <list>                                                              |
| Policy owner / renderer   | <role> / <automation or template>                                   |

```text
Routing domain: who peers with whom (fill in ASNs and prefixes)
+------------+                                                          +------------------------+
| upstream 1 |--eBGP--+                                        +-iBGP-->| site A (<site prefix>) |
+------------+        |                                        |        +------------------------+
+------------+        |     +------+       +-----------+       |        +------------------------+
| upstream 2 |--eBGP--+---->| edge |<----->| core / RR |<----->+-iBGP-->| site B (<site prefix>) |
+------------+        |     +------+       +-----------+       |        +------------------------+
+------------+        |                                        |        +------------------------+
| partner    |--eBGP--+                                        +-iBGP-->| datacentre fabric      |
+------------+                                                          +------------------------+
every session: explicit import and export policy; each prefix has one originator
```

## 2. Prefix ownership

| Prefix (or set)  | Originator       | Origin method (network, redistribute, aggregate) | Advertised to | Max length accepted | RPKI ROA      | Label |
| ---------------- | ---------------- | ------------------------------------------------ | ------------- | ------------------- | ------------- | ----- |
| <site aggregate> | <site-code> edge | network statement                                | core only     | /<n>                | n/a (private) |       |

## 3. Peers and policy

| Peer / class     | Session (AFI/SAFI, auth, BFD)      | Import: accept    | Import: reject               | Import actions     | Export: send      | Export actions | Max-prefix warn / limit | Owner |
| ---------------- | ---------------------------------- | ----------------- | ---------------------------- | ------------------ | ----------------- | -------------- | ----------------------- | ----- |
| upstream transit | ipv4/ipv6 unicast, TCP-AO/MD5, BFD | default or        | bogons, own prefixes,        | lp <n>,            | own               | none           | <n> / <n>               |       |
|                  |   <n> ms                           |   full table      |   too-specific, RPKI invalid |   tag <community>  |   aggregates only |                |                         |       |
| site edge        |                                    | site prefix set   | everything else              |                    | default +         |                |                         |       |
|                  |                                    |                   |                              |                    |   shared services |                |                         |       |

Import actions: local-pref, communities. Export actions: prepend, MED, communities.

## 4. Communities

| Community (standard or large) | Meaning                 | Set by                | Acted on by     | Action                           |
| ----------------------------- | ----------------------- | --------------------- | --------------- | -------------------------------- |
| <asn>:<n>                     | learned from upstream 1 | edge import           | export to peers | do not export                    |
| <asn>:<n>:<n>                 | origin site <site-code> | site edge             | core            | informational                    |
| <asn>:<n>                     | blackhole request       | operator / automation | edges           | discard, limited to /32 and /128 |

## 5. Filters and protection

- Bogon and martian lists: *source and refresh method.* Own-prefix rejection on external import.
- Maximum prefix length and AS-path length per class; RPKI validation state handling.
- Control-plane protection: *TTL security, session limits, policing.*

## 6. Path selection and failover

| Scenario                             | Expected best path (by prefix) | Mechanism (local-pref, MED, IGP cost, BFD) | Convergence target | Measured | Test |
| ------------------------------------ | ------------------------------ | ------------------------------------------ | ------------------ | -------- | ---- |
| Normal                               |                                |                                            | n/a                |          |      |
| Upstream 1 lost                      |                                |                                            | <n> s              |          |      |
| Route reflector lost                 |                                |                                            |                    |          |      |
| Site edge reboot (graceful restart?) |                                |                                            |                    |          |      |

## 7. Review state

| Revision | State    | Date | Reviewer (role) | Evidence |
| -------- | -------- | ---- | --------------- | -------- |
| r1       | proposed |      |                 |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
