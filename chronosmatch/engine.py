from dataclasses import dataclass
from time import perf_counter, perf_counter_ns
from collections import deque

from chronosmatch.latency import LatencyTracker
from chronosmatch.order_book import LimitOrderBook
from chronosmatch.protocol import Order


@dataclass
class EngineStats:
    orders_processed: int = 0
    buy_orders: int = 0
    sell_orders: int = 0
    total_quantity: int = 0
    trades_executed: int = 0
    traded_quantity: int = 0


class TradingEngine:
    """Educational order-processing and matching engine."""

    def __init__(self):
        self.stats = EngineStats()
        self.orders: list[Order] = []
        self.order_book = LimitOrderBook()
        self._start_time = perf_counter()
        self._order_timestamps = deque(maxlen=1000)
        self.processing_latency = LatencyTracker(max_samples=1000)
        self.trade_latency = LatencyTracker(max_samples=1000)

    def process_order(self, order: Order) -> dict:
        entry_ns = self.processing_latency.start()

        # Validate the order before modifying engine state.
        order.pack()
        normalized_side = order.side.upper()

        # Capture trade count before submitting the order.
        previous_trade_count = len(self.order_book.trades)

        # Matching and book updates happen here.
        executed_trades = self.order_book.add_order(order)

        exit_ns = perf_counter_ns()
        processing_ns = self.processing_latency.record(entry_ns, exit_ns)

        # Record only after successful order-book processing.
        self.orders.append(order)
        self.stats.orders_processed += 1
        self.stats.total_quantity += order.quantity

        if normalized_side == "B":
            self.stats.buy_orders += 1
        else:
            self.stats.sell_orders += 1

        self.stats.trades_executed += len(executed_trades)
        self.stats.traded_quantity += sum(
            trade["quantity"] for trade in executed_trades
        )

        self._order_timestamps.append(perf_counter())

        # Record execution timing for orders that generated trades.
        if executed_trades:
            self.trade_latency.record(entry_ns, exit_ns)

        return {
            "order_id": order.order_id,
            "side": normalized_side,
            "price_paise": order.price_paise,
            "quantity": order.quantity,
            "status": "accepted",
            "processing_latency_ns": processing_ns,
            "latency_unit": "ns",
            "executed_trades": executed_trades,
            "trades_count": len(executed_trades),
            "remaining_order_quantity": sum(
                item.quantity
                for levels in (
                    self.order_book.bids,
                    self.order_book.asks,
                )
                for queue in levels.values()
                for item in queue
                if item.order_id == order.order_id
            ),
            "total_trades_in_book": len(self.order_book.trades),
        }

    def get_stats(self) -> dict:
        # Preserve the original statistics response for existing clients.
        return {
            "orders_processed": self.stats.orders_processed,
            "buy_orders": self.stats.buy_orders,
            "sell_orders": self.stats.sell_orders,
            "total_quantity": self.stats.total_quantity,
        }

    def get_order_book(self, depth: int = 5) -> dict:
        return self.order_book.snapshot(depth=depth)

    def get_trades(self, limit: int = 100) -> list[dict]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        return list(reversed(self.order_book.trades[-limit:]))

    def get_performance_stats(self) -> dict:
        elapsed_seconds = perf_counter() - self._start_time

        if len(self._order_timestamps) >= 2:
            interval = (
                self._order_timestamps[-1] - self._order_timestamps[0]
            )
            recent_throughput = (
                (len(self._order_timestamps) - 1) / interval
                if interval > 0
                else 0.0
            )
        else:
            recent_throughput = 0.0

        processing = self.processing_latency.get_stats()
        trade = self.trade_latency.get_stats()

        return {
            "orders_per_second": (
                self.stats.orders_processed / elapsed_seconds
                if elapsed_seconds > 0
                else 0.0
            ),
            "recent_orders_per_second": recent_throughput,
            "average_latency_ns": processing["average_latency_ns"],
            "min_latency_ns": processing["min_latency_ns"],
            "max_latency_ns": processing["max_latency_ns"],
            "p50_latency_ns": processing["p50_latency_ns"],
            "p95_latency_ns": processing["p95_latency_ns"],
            "p99_latency_ns": processing["p99_latency_ns"],
            "latency_samples": processing["latency_samples"],
            "average_latency_ms": (
                processing["average_latency_ns"] / 1_000_000
                if processing["average_latency_ns"] is not None
                else None
            ),
            "latency_unit": "ns",
            "trade_latency": trade,
        }
