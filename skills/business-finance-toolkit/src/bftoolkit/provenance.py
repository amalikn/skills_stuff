import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .models import Claim, RunManifest


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def create_run_manifest(payload: Mapping[str, Any], claims: list[Claim], *, calculator_version: str, artifacts: list[str] | None = None) -> RunManifest:
    payload_hash = canonical_sha256(payload)
    return RunManifest(
        run_id=payload_hash[:16],
        calculator_version=calculator_version,
        input_sha256=payload_hash,
        claim_ids=[claim.id for claim in claims],
        artifacts=artifacts or [],
    )
