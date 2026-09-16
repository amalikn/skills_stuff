from decimal import Decimal

from ._money import decimal, money


def apply_percentage_change(value: Decimal | int | str | float, percentage: Decimal | int | str | float) -> Decimal:
    return money(decimal(value) * (Decimal("1") + decimal(percentage) / Decimal("100")))
