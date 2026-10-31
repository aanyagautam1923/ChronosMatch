import sqlite3
import threading
import queue
from datetime import datetime, timezone
from pathlib import Path


class TradePersistence:
    """Background SQLite persistence for executed trades."""

    def __init__(self, database_path="data/trades.db", queue_size=10000):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self._queue = queue.Queue(maxsize=queue_size)
        self._thread = None
        self._sentinel = object()
        self._lock = threading.Lock()
        self._started = False
        self.last_error = None

        self._initialize_database()

    def _connect(self):
        return sqlite3.connect(str(self.database_path), timeout=10)

    def _initialize_database(self):
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    buy_order_id INTEGER NOT NULL,
                    sell_order_id INTEGER NOT NULL,
                    price_paise INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_trades_timestamp
                ON trades(timestamp)
            """)

    def start(self):
        with self._lock:
            if self._started:
                return

            self._thread = threading.Thread(
                target=self._worker,
                name="ChronosMatch-TradeWriter",
                daemon=True,
            )
            self._started = True
            self._thread.start()

    def enqueue_trade(self, trade):
        if not self._started:
            raise RuntimeError("Trade persistence worker is not running")

        record = {
            "buy_order_id": int(trade["buy_order_id"]),
            "sell_order_id": int(trade["sell_order_id"]),
            "price_paise": int(trade["price_paise"]),
            "quantity": int(trade["quantity"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if min(
            record["buy_order_id"],
            record["sell_order_id"],
            record["price_paise"],
            record["quantity"],
        ) <= 0:
            raise ValueError("Trade values must be positive")

        try:
            self._queue.put_nowait(record)
            return True
        except queue.Full:
            self.last_error = "Trade persistence queue is full"
            return False

    def _worker(self):
        with self._connect() as connection:
            while True:
                item = self._queue.get()

                try:
                    if item is self._sentinel:
                        return

                    connection.execute(
                        """
                        INSERT INTO trades (
                            buy_order_id,
                            sell_order_id,
                            price_paise,
                            quantity,
                            timestamp
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            item["buy_order_id"],
                            item["sell_order_id"],
                            item["price_paise"],
                            item["quantity"],
                            item["timestamp"],
                        ),
                    )
                    connection.commit()

                except Exception as exc:
                    self.last_error = str(exc)

                finally:
                    self._queue.task_done()

    def flush(self):
        self._queue.join()

        if self.last_error:
            raise RuntimeError(
                f"Trade persistence error: {self.last_error}"
            )

    def get_trades(self, limit=100):
        if limit < 1 or limit > 10000:
            raise ValueError("limit must be between 1 and 10000")

        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT
                    id,
                    buy_order_id,
                    sell_order_id,
                    price_paise,
                    quantity,
                    timestamp
                FROM trades
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def stop(self):
        with self._lock:
            if not self._started:
                return

            thread = self._thread

        self.flush()
        self._queue.put(self._sentinel)
        self._queue.join()
        thread.join(timeout=10)

        if thread.is_alive():
            raise RuntimeError("Trade persistence worker did not stop")

        with self._lock:
            self._started = False
            self._thread = None
