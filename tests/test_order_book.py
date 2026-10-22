import pytest

from chronosmatch.order_book import LimitOrderBook
from chronosmatch.protocol import Order


def test_add_buy_order():
    book = LimitOrderBook()

    trades = book.add_order(Order(1, 10000, 10, "B"))

    assert trades == []
    assert book.best_bid() == {
        "price_paise": 10000,
        "quantity": 10,
    }


def test_add_sell_order():
    book = LimitOrderBook()

    book.add_order(Order(1, 10500, 5, "S"))

    assert book.best_ask() == {
        "price_paise": 10500,
        "quantity": 5,
    }


def test_buy_order_matches_sell_order():
    book = LimitOrderBook()

    book.add_order(Order(1, 10000, 10, "S"))
    trades = book.add_order(Order(2, 10000, 6, "B"))

    assert len(trades) == 1
    assert trades[0]["buy_order_id"] == 2
    assert trades[0]["sell_order_id"] == 1
    assert trades[0]["quantity"] == 6
    assert book.best_ask()["quantity"] == 4


def test_price_priority():
    book = LimitOrderBook()

    book.add_order(Order(1, 10200, 5, "S"))
    book.add_order(Order(2, 10100, 5, "S"))

    trades = book.add_order(Order(3, 10200, 5, "B"))

    assert trades[0]["sell_order_id"] == 2
    assert trades[0]["price_paise"] == 10100


def test_time_priority_at_same_price():
    book = LimitOrderBook()

    book.add_order(Order(1, 10000, 5, "S"))
    book.add_order(Order(2, 10000, 5, "S"))

    trades = book.add_order(Order(3, 10000, 5, "B"))

    assert trades[0]["sell_order_id"] == 1


def test_partial_fill():
    book = LimitOrderBook()

    book.add_order(Order(1, 10000, 10, "S"))
    book.add_order(Order(2, 10000, 4, "B"))

    assert book.best_ask()["quantity"] == 6


def test_remaining_buy_quantity_is_added_to_book():
    book = LimitOrderBook()

    book.add_order(Order(1, 9900, 10, "B"))
    trades = book.add_order(Order(2, 10000, 5, "B"))

    assert trades == []
    assert book.best_bid() == {
        "price_paise": 10000,
        "quantity": 5,
    }


def test_invalid_order_does_not_change_book():
    book = LimitOrderBook()

    with pytest.raises(ValueError):
        book.add_order(Order(1, 10000, 5, "X"))

    assert book.snapshot()["bids"] == []
    assert book.snapshot()["asks"] == []


def test_snapshot_depth_validation():
    book = LimitOrderBook()

    with pytest.raises(ValueError):
        book.snapshot(depth=0)


def test_empty_book():
    book = LimitOrderBook()

    assert book.best_bid() is None
    assert book.best_ask() is None
    assert book.snapshot()["trades_count"] == 0
