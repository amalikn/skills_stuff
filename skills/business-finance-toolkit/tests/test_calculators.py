from decimal import Decimal, ROUND_DOWN, localcontext

from bftoolkit.calculators.cash_flow import monthly_closing_cash
from bftoolkit.calculators.capital import required_capital
from bftoolkit.calculators.break_even import break_even_units
from bftoolkit.calculators.landed_cost import landed_cost
from bftoolkit.calculators.scenarios import apply_percentage_change
from bftoolkit.calculators.unit_economics import unit_economics


def test_landed_cost_includes_all_components() -> None:
    result = landed_cost({"purchase": "10000", "freight": "1500", "duty": "500"})

    assert result.total == Decimal("12000.00")


def test_unit_economics_calculates_margin() -> None:
    result = unit_economics(selling_price="15000", variable_cost="12000", selling_cost="500")

    assert result.contribution == Decimal("2500.00")
    assert result.contribution_margin_pct == Decimal("16.67")


def test_unit_economics_uses_explicit_rounding_not_process_context() -> None:
    with localcontext() as context:
        context.rounding = ROUND_DOWN
        result = unit_economics(selling_price="200", variable_cost="175.31")

    assert result.contribution_margin_pct == Decimal("12.35")


def test_monthly_closing_cash_applies_inflows_and_outflows() -> None:
    assert monthly_closing_cash("1000", ["250", "100"], ["900", "50"]) == Decimal("400.00")


def test_scenario_change_is_quantized() -> None:
    assert apply_percentage_change("1000", "12.5") == Decimal("1125.00")


def test_required_capital_combines_inventory_and_buffer() -> None:
    result = required_capital(inventory="12000", operating_buffer="2000", setup_cost="500")

    assert result.total == Decimal("14500.00")


def test_break_even_units_uses_positive_unit_contribution() -> None:
    assert break_even_units(fixed_cost="5000", unit_contribution="2500") == Decimal("2.00")
