from collections.abc import Mapping
from decimal import Decimal

from pydantic import BaseModel

from ._money import money


class LandedCostResult(BaseModel):
    components: dict[str, Decimal]
    total: Decimal


def landed_cost(components: Mapping[str, Decimal | int | str | float]) -> LandedCostResult:
    normalized = {name: money(amount) for name, amount in components.items()}
    return LandedCostResult(components=normalized, total=money(sum(normalized.values(), Decimal("0"))))
