from types import SimpleNamespace

from chronosmatch.risk_engine import OrderRiskEngine, RiskLimits


def make_order(side="B", quantity=100, price_paise=10000):
    return SimpleNamespace(
        side=side,
        quantity=quantity,
        price_paise=price_paise,
    )


def test_valid_order_is_accepted():
    result = OrderRiskEngine().validate(make_order())
    assert result.accepted is True
    assert result.reasons == ()


def test_invalid_side_is_rejected():
    result = OrderRiskEngine().validate(make_order(side="X"))
    assert result.accepted is False
    assert any("Side" in reason for reason in result.reasons)


def test_zero_quantity_is_rejected():
    result = OrderRiskEngine().validate(make_order(quantity=0))
    assert result.accepted is False


def test_quantity_over_limit_is_rejected():
    engine = OrderRiskEngine(RiskLimits(max_quantity=100))
    result = engine.validate(make_order(quantity=101))
    assert result.accepted is False


def test_large_order_is_flagged():
    engine = OrderRiskEngine(
        RiskLimits(max_quantity=1000, large_order_quantity=500)
    )
    result = engine.validate(make_order(quantity=500))
    assert result.accepted is True
    assert result.warnings


def test_price_below_minimum_is_rejected():
    result = OrderRiskEngine().validate(make_order(price_paise=0))
    assert result.accepted is False


def test_price_above_limit_is_rejected():
    engine = OrderRiskEngine(RiskLimits(max_price_paise=20000))
    result = engine.validate(make_order(price_paise=20001))
    assert result.accepted is False


def test_invalid_quantity_type_is_rejected():
    result = OrderRiskEngine().validate(make_order(quantity=True))
    assert result.accepted is False


def test_invalid_limits_raise_error():
    try:
        OrderRiskEngine(RiskLimits(max_quantity=0))
    except ValueError:
        return
    raise AssertionError("Expected invalid limits to raise ValueError.")
