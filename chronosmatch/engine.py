from dataclasses import dataclass
from time import perf_counter
from collections import deque

from chronosmatch.protocol import Order


@dataclass
class EngineStats:
    orders_processed: int = 0
    buy_orders: int = 0
    sell_orders: int = 0
    total_quantity: int = 0


class TradingEngine:
    """Educational order-processing engine; not connected to a real exchange."""

    def __init__(self):
        self.stats = EngineStats()
        self.orders: list[Order] = []
        self._start_time = perf_counter()
        self._latencies_ms = deque(maxlen=1000)

    def process_order(self, order: Order) -> dict:
        start = perf_counter()

        # Validate before modifying engine state.
        order.pack()

        self.orders.append(order)
        self.stats.orders_processed += 1
        self.stats.total_quantity += order.quantity

        if order.side.upper() == "B":
            self.stats.buy_orders += 1
        else:
            self.stats.sell_orders += 1

        self._latencies_ms.append((perf_counter() - start) * 1000)

        return {
            "order_id": order.order_id,
            "side": order.side.upper(),
            "price_paise": order.price_paise,
            "quantity": order.quantity,
            "status": "accepted",
        }

    def get_stats(self) -> dict:
        # Preserve the exact original response for existing tests.
        return {
            "orders_processed": self.stats.orders_processed,
            "buy_orders": self.stats.buy_orders,
            "sell_orders": self.stats.sell_orders,
            "total_quantity": self.stats.total_quantity,
        }

    def get_performance_stats(self) -> dict:
        elapsed_seconds = perf_counter() - self._start_time

        return {
            "orders_per_second": (
                self.stats.orders_processed / elapsed_seconds
                if elapsed_seconds > 0
                else 0.0
            ),
            "average_latency_ms": (
                sum(self._latencies_ms) / len(self._latencies_ms)
                if self._latencies_ms
                else None
            ),
            "latency_unit": "ms",
        }
