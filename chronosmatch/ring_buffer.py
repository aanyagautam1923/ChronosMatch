from typing import Optional


class RingBuffer:
    """A fixed-capacity FIFO ring buffer for byte records."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero")

        self.capacity = capacity
        self._items: list[Optional[bytes]] = [None] * capacity
        self._read_index = 0
        self._write_index = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        return self._size == self.capacity

    def put(self, item: bytes) -> None:
        if not isinstance(item, bytes):
            raise TypeError("Item must be bytes")

        if self.is_full():
            raise BufferError("Ring buffer is full")

        self._items[self._write_index] = item
        self._write_index = (self._write_index + 1) % self.capacity
        self._size += 1

    def get(self) -> bytes:
        if self.is_empty():
            raise BufferError("Ring buffer is empty")

        item = self._items[self._read_index]
        self._items[self._read_index] = None
        self._read_index = (self._read_index + 1) % self.capacity
        self._size -= 1

        if item is None:
            raise RuntimeError("Unexpected empty slot in ring buffer")

        return item
