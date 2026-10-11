from dataclasses import dataclass

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

    def process_order(self, order: Order) -> dict:
        # Validate that the order can be encoded before accepting it.
        order.pack()

        self.orders.append(order)
        self.stats.orders_processed += 1
        self.stats.total_quantity += order.quantity

        if order.side.upper() == "B":
            self.stats.buy_orders += 1
        else:
            self.stats.sell_orders += 1

        return {
            "order_id": order.order_id,
            "side": order.side.upper(),
            "price_paise": order.price_paise,
            "quantity": order.quantity,
            "status": "accepted",
        }

    def get_stats(self) -> dict:
        return {
            "orders_processed": self.stats.orders_processed,
            "buy_orders": self.stats.buy_orders,
            "sell_orders": self.stats.sell_orders,
            "total_quantity": self.stats.total_quantity,
        }
