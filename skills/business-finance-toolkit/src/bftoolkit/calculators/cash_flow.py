from collections.abc import Iterable
from decimal import Decimal

from ._money import decimal, money


def monthly_closing_cash(
    opening_cash: Decimal | int | str | float,
    inflows: Iterable[Decimal | int | str | float],
    outflows: Iterable[Decimal | int | str | float],
) -> Decimal:
    return money(decimal(opening_cash) + sum((decimal(x) for x in inflows), Decimal("0")) - sum((decimal(x) for x in outflows), Decimal("0")))
