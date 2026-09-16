from decimal import Decimal

from pydantic import BaseModel

from ._money import money


class CapitalRequirement(BaseModel):
    inventory: Decimal
    operating_buffer: Decimal
    setup_cost: Decimal
    total: Decimal


def required_capital(
    *, inventory: Decimal | int | str | float, operating_buffer: Decimal | int | str | float, setup_cost: Decimal | int | str | float = 0
) -> CapitalRequirement:
    values = (money(inventory), money(operating_buffer), money(setup_cost))
    return CapitalRequirement(inventory=values[0], operating_buffer=values[1], setup_cost=values[2], total=money(sum(values)))
