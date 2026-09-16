from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def decimal(value: Decimal | int | str | float) -> Decimal:
    if isinstance(value, bool):
        raise TypeError("boolean is not a financial amount")
    return Decimal(str(value))


def money(value: Decimal | int | str | float) -> Decimal:
    return decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)
