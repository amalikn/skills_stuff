from collections.abc import Mapping
from typing import Protocol


class DraftingProvider(Protocol):
    """Draft text only; callers must independently validate claims and calculations."""

    def draft(self, instruction: str, context: Mapping[str, object]) -> str: ...


class ProviderPolicy(Protocol):
    """Allow an integration to decide whether data may leave the local environment."""

    def permits_external_data(self, classification: str) -> bool: ...
