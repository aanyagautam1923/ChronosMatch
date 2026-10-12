import pytest

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order


def test_process_buy_order():
    engine = TradingEngine()
    order = Order(1, 12550, 10, "B")

    result = engine.process_order(order)

    assert result["order_id"] == 1
    assert result["side"] == "B"
    assert result["status"] == "accepted"


def test_process_sell_order():
    engine = TradingEngine()
    order = Order(2, 12600, 5, "S")

    result = engine.process_order(order)

    assert result["side"] == "S"
    assert result["quantity"] == 5


def test_engine_statistics():
    engine = TradingEngine()

    engine.process_order(Order(1, 12550, 10, "B"))
    engine.process_order(Order(2, 12600, 5, "S"))
    engine.process_order(Order(3, 12400, 8, "B"))

    assert engine.get_stats() == {
        "orders_processed": 3,
        "buy_orders": 2,
        "sell_orders": 1,
        "total_quantity": 23,
    }


def test_empty_engine_statistics():
    engine = TradingEngine()

    assert engine.get_stats() == {
        "orders_processed": 0,
        "buy_orders": 0,
        "sell_orders": 0,
        "total_quantity": 0,
    }


def test_invalid_order_is_not_processed():
    engine = TradingEngine()
    invalid_order = Order(4, 12500, 5, "X")

    with pytest.raises(ValueError):
        engine.process_order(invalid_order)

    assert engine.get_stats()["orders_processed"] == 0
