"""Give every /32 address its subnet's mask: plan the changes from address and Prefix records, then optionally apply them. Stdlib only.

Why: importers that write device addresses as `/32` and importers that write the subnet's mask disagree, so which one runs first
at a site decides the mask, and a site can end up holding both. One deployment found exactly that after its onboarding, discovery
and DNS-zone importers had each run. The rule (see `nautobot_ipam`) is that an address carries the mask of the narrowest `network`
Prefix holding it in its own Namespace. Changing the mask in place (PATCH `address` with the same host) keeps the object, so its
interface assignments, primary_ip4 and relationships stay as they are (seen on Nautobot 3.2.3).

What the plan does, per Namespace:
    fix       a /32 whose narrowest network Prefix is found and no wider than `min_subnet`: the new `host/len`.
    report    a /32 with no network Prefix, or whose narrowest network Prefix is wider than `min_subnet` (a placeholder such as a
              seeded /16, not a real subnet); and any non-/32 address whose mask differs from its subnet's. Nothing is changed.
A second plan over the fixed records finds nothing to fix.

Usage:
    from nautobot_masks import plan, apply
    fix, report = plan(addresses, prefixes)          # REST dicts of ONE Namespace: addresses need id/host/mask_length/address
    apply(lambda method, path, body: session.request(method, base + path, json=body).json(), fix)   # bulk PATCH, 200 per call
"""

from __future__ import annotations

from typing import Callable

from nautobot_ipam import network_mask

#: A network Prefix wider than this is treated as a placeholder, not the subnet a device is configured on.
MIN_SUBNET = 17

#: The report wording; a caller may pass its own (same keys, same format fields) to keep an established output.
MESSAGES = {
    "none": "no network Prefix holds it",
    "wide": "narrowest network Prefix is /{mask}, wider than /{min_subnet}: the subnet is not recorded",
    "differs": "mask /{have} differs from its subnet's /{mask}",
}


def plan(addresses: list[dict], prefixes: list[dict], *, min_subnet: int = MIN_SUBNET,
         messages: dict[str, str] | None = None) -> tuple[list[tuple[dict, str]], list[tuple[dict, str]]]:
    """(to fix: [(address, "host/len")], to report: [(address, why)]) for one Namespace's addresses and Prefixes, in input order."""
    text = {**MESSAGES, **(messages or {})}
    fix: list[tuple[dict, str]] = []
    report: list[tuple[dict, str]] = []
    for a in addresses:
        mask = network_mask(prefixes, a["host"])
        if a["mask_length"] == 32:
            if mask is None:
                report.append((a, text["none"].format(mask=mask, min_subnet=min_subnet, have=32)))
            elif mask < min_subnet:
                report.append((a, text["wide"].format(mask=mask, min_subnet=min_subnet, have=32)))
            elif mask != 32:
                fix.append((a, f"{a['host']}/{mask}"))
        elif mask is not None and a["mask_length"] != mask:
            report.append((a, text["differs"].format(mask=mask, min_subnet=min_subnet, have=a["mask_length"])))
    return fix, report


def apply(call: Callable[[str, str, list], object], fix: list[tuple[dict, str]], *, batch: int = 200,
          path: str = "/ipam/ip-addresses/") -> int:
    """Bulk-PATCH each planned `address` through `call(method, path, body)`, `batch` objects per request. Returns how many were sent.

    The caller owns authentication, the base URL, retries and which account writes; this only shapes the requests.
    """
    if batch < 1:
        raise ValueError("batch must be at least 1")
    for i in range(0, len(fix), batch):
        call("PATCH", path, [{"id": a["id"], "address": new} for a, new in fix[i : i + batch]])
    return len(fix)
