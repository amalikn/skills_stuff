# Discovery and topology

## Evidence is not topology authority

Represent an observation with source, capture time, vantage point, endpoint identities, confidence, parser or collector version where material, conflict state, and freshness. The same link seen from
two ends is stronger evidence than a single assertion, but it is still observed state until a governed review promotes it.

| Source              | Useful for                                 | Cannot prove alone                                  |
| ------------------- | ------------------------------------------ | --------------------------------------------------- |
| LLDP/CDP            | A neighbour report from a specific vantage | An end-to-end physical path or both ends' agreement |
| FDB                 | A learned MAC on a port                    | Direct attachment or a stable cable                 |
| ARP/neighbour state | An IP/MAC sighting                         | A physical link or current ownership                |
| DHCP                | A recent lease association                 | Present topology or device identity                 |
| Device API or SSH   | A vendor-owned association                 | Cross-device physical truth                         |
| Inventory           | Approved intended arrangement              | Current observation                                 |

SNMP, DNS, and CLI evidence fit the same contract: state what was observed and from where, rather than turning a parser result into a permanent edge. Parallel links, asymmetric reports, and an
identity collision must remain explicit candidates, not collapsed into one attractive graph edge.

## Promotion and modelling

Keep physical topology, logical service topology, and monitoring association separate. A conflicting observation can indicate stale state, a one-sided report, a collector fault, a changed path, or a
real intent drift. Investigate those possibilities before changing accepted inventory. A custom Relationship is suitable for a durable relation between existing objects; the project's Wireless Link
object is a worked example where the native model was insufficient, not a product-wide prescription. Claim N-C15.

The project Step 9 correlator and rendering slice remain proposed architecture only. An installed model, a discovery feed, or a drawn graph does not prove reconciliation is implemented. Acceptance is
a traceable observation, conflict handling, reviewer decision, and separately recorded intended edge. Claim N-C07.

## Conflict and Wireless Link worked case

Synthetic observations at 10:00 UTC: switch `sw-a` reports LLDP peer `ap-1` on port 7; its FDB learns `ap-1` on port 8 at 09:52; an SMC ARP entry maps the
same IP to a different MAC at 09:40. Do not select port 7 by protocol prestige or rewrite a Cable. Verify endpoint identity and collection clocks; repeat
fresh observations from both ends; check whether port 8 is a trunk/bridge and whether ARP is stale. Store three candidate edges with source, vantage, timestamp
and conflict flag. Promotion to accepted intent requires a reviewed explanation and post-change consistency, not a majority vote.

UNC's implemented Wireless Link custom model represents a durable radio edge with A/Z Device endpoints, optional interfaces, band, planned channel, reported channel,
frequency, per-end and derived width, Status and source. Its validation rejects self-links, interfaces owned by the wrong Device, incompatible widths/channels and
duplicate endpoint pairs in the same band. These are **UNC model semantics**, not built-in Nautobot Wireless Link fields; read its model/design before copying them.
Native Cable/Interface models fit physical terminations, and a Relationship may suffice for a simple durable link between existing objects. A
Wireless Link-like model is justified only if the edge itself needs identity, status/lifecycle, endpoint relations and attributes that cannot be represented honestly by
those native objects. A live association-table sighting is **observation**, not an accepted Wireless Link. The UNC feed/reconciliation and Step 9 collector/rendering
remain proposed. A central collector unable to reach site protocols must use a justified site vantage; SNMP/ICMP and TCP forwarding are not interchangeable.
Vendor OIDs, commands and RF interpretation belong to equipment/transport expertise. For a graph consumer read OpenWISP
[topology and FOSS](../../skill-openwisp/references/topology-and-foss.md) only when the request crosses into presentation.
