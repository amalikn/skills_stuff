"""Pure IPAM rules for Nautobot 3.x data. Stdlib only, no I/O.

The mask an address carries should be its subnet's: the narrowest Prefix of type `network` that holds it, never `/32` by default.
Container and pool Prefixes are not subnets. Writing every device address as `/32` hides the routing fact and makes later
interface/subnet checks impossible; this rule came from a deployment that had to convert its imported addresses afterwards.

Usage:
    from nautobot_ipam import network_mask, with_mask
    with_mask(prefixes, "192.0.2.10")   # "192.0.2.10/27" when 192.0.2.0/27 is the narrowest network Prefix
"""

from __future__ import annotations

import ipaddress


def _prefix_type(prefix: dict) -> str | None:
    kind = prefix.get("type")
    return kind.get("value") if isinstance(kind, dict) else kind


def network_mask(prefixes: list[dict], ip: str) -> int | None:
    """The prefix length of the narrowest `network` Prefix in `prefixes` (REST dicts with `prefix` and `type`) holding `ip`; None if none does.

    Pass the Prefixes of the address's own Namespace only: overlapping address space is legitimate across Namespaces.
    """
    host = ipaddress.ip_address(ip)
    lengths = [ipaddress.ip_network(p["prefix"], strict=False).prefixlen for p in prefixes
               if _prefix_type(p) == "network" and host in ipaddress.ip_network(p["prefix"], strict=False)]
    return max(lengths, default=None)


def with_mask(prefixes: list[dict], ip: str) -> str | None:
    """`ip/len` using `network_mask`; None when no network Prefix holds the address (create the subnet first; do not fall back to /32)."""
    length = network_mask(prefixes, ip)
    return None if length is None else f"{ip}/{length}"
