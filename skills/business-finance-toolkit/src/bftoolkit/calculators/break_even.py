from decimal import Decimal, ROUND_CEILING

from ._money import decimal


def break_even_units(*, fixed_cost: Decimal | int | str | float, unit_contribution: Decimal | int | str | float) -> Decimal:
    """Return whole units needed to cover fixed cost; reject a non-positive contribution."""

    contribution = decimal(unit_contribution)
    if contribution <= 0:
        raise ValueError("unit contribution must be greater than zero")
    return (decimal(fixed_cost) / contribution).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
