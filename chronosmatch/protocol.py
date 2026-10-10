import struct
from dataclasses import dataclass

ORDER_STRUCT = struct.Struct("<QIIB3x")
ORDER_SIZE = ORDER_STRUCT.size


@dataclass(slots=True)
class Order:
    order_id: int
    price_paise: int
    quantity: int
    side: str

    def pack(self) -> bytes:
        side = self.side.upper()

        if side not in ("B", "S"):
            raise ValueError("Side must be B (buy) or S (sell)")

        if not 0 <= self.order_id <= 2**64 - 1:
            raise ValueError("Invalid order ID")

        if not 0 <= self.price_paise <= 2**32 - 1:
            raise ValueError("Invalid price")

        if not 0 <= self.quantity <= 2**32 - 1:
            raise ValueError("Invalid quantity")

        side_code = 1 if side == "B" else 2

        return ORDER_STRUCT.pack(
            self.order_id,
            self.price_paise,
            self.quantity,
            side_code,
        )

    @classmethod
    def unpack(cls, data: bytes) -> "Order":
        if len(data) != ORDER_SIZE:
            raise ValueError(
                f"Expected {ORDER_SIZE} bytes, received {len(data)}"
            )

        order_id, price, quantity, side_code = ORDER_STRUCT.unpack(data)

        if side_code not in (1, 2):
            raise ValueError("Invalid side code")

        return cls(
            order_id=order_id,
            price_paise=price,
            quantity=quantity,
            side="B" if side_code == 1 else "S",
        )
