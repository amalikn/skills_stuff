# Topology and complementary FOSS

## Graph evidence model

Treat topology input as an observation with source, time, vantage, endpoint identity, confidence, conflict state, and freshness. NetJSON NetworkGraph and RECEIVE-style ingestion concepts can carry
observed edges, but an observed graph is not intended inventory. Preserve parallel, disputed, and stale edges rather than normalizing them into a single asserted path.

When a task crosses the seam, make provenance visible in the graph or its review record: which collector asserted the edge, what it could observe, and why an operator accepted or rejected it.
Rendering is a consumer of graph data, not evidence that discovery, reconciliation, or intent promotion works.

## Capability boundary

OpenWISP Network Topology and complementary FOSS can be evaluated for collection, diffing, correlation, or rendering through supported seams. An installed module does not create a working pipeline;
verify its version, effective settings, ingestion path, worker reachability, persistence, and consumer view. The project NetworkGraph integration is proposed architecture, not deployed capability.
Claim O-C07.

## Capability and status map

| Capability                                     | Supported source/seam                                            | UNC status and proof still needed                                                |
| ---------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| NetJSON NetworkGraph receive and topology view | [OpenWISP 26.09 Network Topology strategies](https://openwisp.io/docs/26.09/network-topology/user/strategies.html) and [REST reference](https://openwisp.io/docs/26.09/network-topology/user/rest-api.html) | Module observed installed; UNC RECEIVE pipeline and operator view **not deployed** |
| Edge observations                              | Site-side LLDP/FDB/ARP, radio association or [Netdisco](https://github.com/netdisco/netdisco) | UNC Step 9 collector/correlator **proposed**; protocol-specific evidence differs |
|                                                |   where reachable                                                |                                                                                  |
| Intended links                                 | Nautobot native Cable/Interface or reviewed relationship/model   | Separate accepted inventory, not graph ingestion                                 |
| Graph rendering                                | OpenWISP UI or another FOSS consumer                             | Requires proven ingestion, retained provenance, freshness/conflict display and   |
|                                                |                                                                  |   user access                                                                    |

Synthetic conflict: LLDP says `A→B`, FDB suggests `A→C`, with different collection times. Keep both candidates and their vantage/time; do not send a single
asserted edge to RECEIVE merely to make a clean graph. An ingestion design needs stable node/link identifiers, source, observed-at, expiry and conflict semantics;
confirm the chosen NetworkGraph schema and extension fields in the deployed version. A valid POST proves neither stored topology nor an operator view. For the
inventory side read Nautobot [discovery and topology](../../skill-nautobot/references/discovery-and-topology.md) only when intent changes.
