from dataclasses import dataclass
from collections import deque
from typing import Deque

from chronosmatch.protocol import Order


@dataclass
class BookOrder:
    order_id: int
    price_paise: int
    quantity: int
    side: str


class LimitOrderBook:
    """Limit order book implementing price-time priority."""

    def __init__(self):
        self.bids: dict[int, Deque[BookOrder]] = {}
        self.asks: dict[int, Deque[BookOrder]] = {}
        self.trades: list[dict] = []

    def add_order(self, order: Order) -> list[dict]:
        order.pack()

        side = order.side.upper()
        remaining = order.quantity
        executed_trades = []

        opposite_book = self.asks if side == "B" else self.bids

        while remaining > 0 and opposite_book:
            best_price = (
                min(opposite_book)
                if side == "B"
                else max(opposite_book)
            )

            if side == "B" and best_price > order.price_paise:
                break

            if side == "S" and best_price < order.price_paise:
                break

            queue = opposite_book[best_price]
            resting_order = queue[0]

            quantity = min(remaining, resting_order.quantity)

            trade = {
                "buy_order_id": (
                    order.order_id
                    if side == "B"
                    else resting_order.order_id
                ),
                "sell_order_id": (
                    resting_order.order_id
                    if side == "B"
                    else order.order_id
                ),
                "price_paise": resting_order.price_paise,
                "quantity": quantity,
            }

            executed_trades.append(trade)
            self.trades.append(trade)

            remaining -= quantity
            resting_order.quantity -= quantity

            if resting_order.quantity == 0:
                queue.popleft()

                if not queue:
                    del opposite_book[best_price]

        if remaining > 0:
            own_book = self.bids if side == "B" else self.asks

            own_book.setdefault(order.price_paise, deque()).append(
                BookOrder(
                    order_id=order.order_id,
                    price_paise=order.price_paise,
                    quantity=remaining,
                    side=side,
                )
            )

        return executed_trades

    def best_bid(self):
        if not self.bids:
            return None

        price = max(self.bids)

        return {
            "price_paise": price,
            "quantity": sum(
                item.quantity for item in self.bids[price]
            ),
        }

    def best_ask(self):
        if not self.asks:
            return None

        price = min(self.asks)

        return {
            "price_paise": price,
            "quantity": sum(
                item.quantity for item in self.asks[price]
            ),
        }

    def snapshot(self, depth: int = 5) -> dict:
        if depth < 1:
            raise ValueError("Depth must be at least 1")

        bids = [
            {
                "price_paise": price,
                "quantity": sum(
                    item.quantity for item in self.bids[price]
                ),
            }
            for price in sorted(self.bids, reverse=True)[:depth]
        ]

        asks = [
            {
                "price_paise": price,
                "quantity": sum(
                    item.quantity for item in self.asks[price]
                ),
            }
            for price in sorted(self.asks)[:depth]
        ]

        return {
            "bids": bids,
            "asks": asks,
            "best_bid": self.best_bid(),
            "best_ask": self.best_ask(),
            "trades_count": len(self.trades),
        }
