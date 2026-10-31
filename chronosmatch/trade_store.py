import sqlite3
from contextlib import closing
from pathlib import Path
from threading import Lock
from typing import Any


class TradeStore:
    """Persistent SQLite storage for executed trades."""

    def __init__(self, db_path: str = "data/trades.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        buy_order_id INTEGER NOT NULL,
                        sell_order_id INTEGER NOT NULL,
                        price_paise INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        executed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)

    def save_trades(self, trades: list[dict[str, Any]]) -> int:
        if not trades:
            return 0

        required = (
            "buy_order_id",
            "sell_order_id",
            "price_paise",
            "quantity",
        )

        rows = []
        for trade in trades:
            missing = [key for key in required if key not in trade]
            if missing:
                raise ValueError(f"Missing trade fields: {missing}")

            rows.append(tuple(trade[key] for key in required))

        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.executemany("""
                    INSERT INTO trades (
                        buy_order_id, sell_order_id, price_paise, quantity
                    )
                    VALUES (?, ?, ?, ?)
                """, rows)

        return len(rows)

    def save_trade(self, trade: dict[str, Any]) -> None:
        self.save_trades([trade])

    def get_trades(self, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 10000:
            raise ValueError("limit must be between 1 and 10000")

        with self._lock, closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM trades ORDER BY trade_id DESC LIMIT ?",
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def count_trades(self) -> int:
        with self._lock, closing(self._connect()) as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM trades"
            ).fetchone()[0]
