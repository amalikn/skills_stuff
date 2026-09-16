from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel

from ._money import decimal, money


class UnitEconomicsResult(BaseModel):
    selling_price: Decimal
    variable_cost: Decimal
    selling_cost: Decimal
    contribution: Decimal
    contribution_margin_pct: Decimal


def unit_economics(
    *, selling_price: Decimal | int | str | float, variable_cost: Decimal | int | str | float, selling_cost: Decimal | int | str | float = 0
) -> UnitEconomicsResult:
    price = money(selling_price)
    variable = money(variable_cost)
    selling = money(selling_cost)
    contribution = money(price - variable - selling)
    margin = Decimal("0") if price == 0 else (contribution / price * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return UnitEconomicsResult(
        selling_price=price,
        variable_cost=variable,
        selling_cost=selling,
        contribution=contribution,
        contribution_margin_pct=margin,
    )
