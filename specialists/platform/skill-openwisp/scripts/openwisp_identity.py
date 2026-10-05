"""Pure identity and time conversions for integrating an inventory with OpenWISP 1.3 (images 26.09.0). Stdlib only, no I/O.

Promoted from the unified-network-controller collector (2026-10-05), where they key OpenWISP devices on an inventory UUID. Each rule is
checked against the installed 1.3 source, cited per function:

- `hardware_id` holds at most 32 characters, so a dashed UUID (36) does not fit; its 32-hex form is lossless.
- A device name must match OpenWISP's hostname or MAC regex (openwisp_controller/config/validators.py), so inventory names with
  underscores or spaces need translating for display.
- The monitoring `time` query parameter is `%d-%m-%Y_%H:%M:%S.%f` and is parsed as UTC (openwisp_monitoring/device/api/views.py), so a
  naive or local time must never be formatted directly.

Usage:
    from openwisp_identity import to_hardware_id, device_name, backfill_time
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

#: openwisp_controller/config/validators.py, 1.3: a hostname of dot-separated labels, each 1-63 of [A-Za-z0-9-], not starting or ending with '-'.
HOSTNAME_RE = re.compile(r"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$")
#: openwisp_monitoring/device/api/views.py, 1.3: the only accepted `time` format; microseconds are required.
BACKFILL_FORMAT = "%d-%m-%Y_%H:%M:%S.%f"
HARDWARE_ID_MAX = 32


def to_hardware_id(inventory_uuid: str) -> str:
    """An inventory UUID as an OpenWISP `hardware_id`: the same 128 bits as 32 lowercase hex characters. Raises ValueError for a non-UUID."""
    return uuid.UUID(str(inventory_uuid)).hex


def from_hardware_id(hardware_id: str) -> str:
    """The inverse of `to_hardware_id`: the dashed UUID. Raises ValueError when the value is not 32 hex characters."""
    if not isinstance(hardware_id, str) or not re.fullmatch(r"[0-9a-fA-F]{32}", hardware_id):
        raise ValueError(f"not a 32-hex hardware_id: {hardware_id!r}")
    return str(uuid.UUID(hex=hardware_id))


def normalise_mac(value: str | None) -> str | None:
    """A MAC in any common notation as `aa:bb:cc:dd:ee:ff`; None when it does not hold exactly 12 hex digits."""
    digits = "".join(c for c in (value or "") if c in "0123456789abcdefABCDEF").lower()
    return ":".join(digits[i:i + 2] for i in range(0, 12, 2)) if len(digits) == 12 else None


def device_name(inventory_name: str) -> str:
    """A display name OpenWISP 1.3 accepts: characters outside [A-Za-z0-9.-] become '-', runs of '-' collapse, labels are trimmed.

    Raises ValueError when the result still fails the hostname rule (an empty name, or a label over 63 characters), rather than
    letting the device save fail later. Names are display only: key devices on `hardware_id`, never on the name.
    """
    name = re.sub(r"-{2,}", "-", re.sub(r"[^A-Za-z0-9.-]", "-", inventory_name))
    name = ".".join(label.strip("-") for label in name.split("."))
    if not HOSTNAME_RE.match(name):
        raise ValueError(f"cannot make a valid OpenWISP device name from {inventory_name!r}")
    return name


def backfill_time(observed_at: datetime) -> str:
    """The `time` query parameter for a monitoring push of a reading taken at `observed_at`, converted to UTC.

    Raises ValueError for a naive datetime: OpenWISP reads the value as UTC, so a naive local time would be stored hours off.
    """
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("observed_at must be timezone-aware; OpenWISP parses the time as UTC")
    return observed_at.astimezone(timezone.utc).strftime(BACKFILL_FORMAT)
