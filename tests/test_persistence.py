import sqlite3

import pytest

from chronosmatch.persistence import TradePersistence


@pytest.fixture
def persistence(tmp_path):
    database = tmp_path / "trades.db"
    store = TradePersistence(database_path=database)
    yield store

    if store._started:
        store.stop()


def sample_trade():
    return {
        "buy_order_id": 101,
        "sell_order_id": 102,
        "price_paise": 10500,
        "quantity": 5,
    }


def test_database_table_is_created(persistence):
    with sqlite3.connect(persistence.database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

    assert ("trades",) in tables


def test_trade_is_saved_in_background(persistence):
    persistence.start()

    assert persistence.enqueue_trade(sample_trade()) is True

    persistence.flush()

    trades = persistence.get_trades()

    assert len(trades) == 1
    assert trades[0]["buy_order_id"] == 101
    assert trades[0]["sell_order_id"] == 102
    assert trades[0]["price_paise"] == 10500
    assert trades[0]["quantity"] == 5
    assert trades[0]["timestamp"]

    persistence.stop()


def test_trade_history_survives_restart(tmp_path):
    database = tmp_path / "persistent.db"

    first = TradePersistence(database)
    first.start()
    first.enqueue_trade(sample_trade())
    first.stop()

    second = TradePersistence(database)

    trades = second.get_trades()

    assert len(trades) == 1
    assert trades[0]["quantity"] == 5


def test_invalid_trade_is_rejected(persistence):
    persistence.start()

    invalid_trade = sample_trade()
    invalid_trade["quantity"] = 0

    with pytest.raises(ValueError):
        persistence.enqueue_trade(invalid_trade)

    persistence.stop()


def test_get_trades_validates_limit(persistence):
    with pytest.raises(ValueError):
        persistence.get_trades(0)

    with pytest.raises(ValueError):
        persistence.get_trades(10001)


def test_start_and_stop_are_safe(persistence):
    persistence.start()
    persistence.start()

    assert persistence._started is True

    persistence.stop()
    persistence.stop()

    assert persistence._started is False
