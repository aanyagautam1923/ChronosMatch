# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

from libc.stdint cimport uint64_t, uint32_t
from time import perf_counter


cdef class CythonEngine:
    cdef public uint64_t orders_processed
    cdef public uint64_t buy_orders
    cdef public uint64_t sell_orders
    cdef public uint64_t total_quantity
    cdef object latencies_ms
    cdef double start_time

    def __cinit__(self):
        self.orders_processed = 0
        self.buy_orders = 0
        self.sell_orders = 0
        self.total_quantity = 0
        self.latencies_ms = []
        self.start_time = perf_counter()

    cpdef dict process_order(
        self,
        uint64_t order_id,
        uint32_t price_paise,
        uint32_t quantity,
        str side
    ):
        cdef double start = perf_counter()
        cdef str normalized_side = side.upper()

        if normalized_side not in ("B", "S"):
            raise ValueError("Side must be 'B' or 'S'")

        self.orders_processed += 1
        self.total_quantity += quantity

        if normalized_side == "B":
            self.buy_orders += 1
        else:
            self.sell_orders += 1

        self.latencies_ms.append((perf_counter() - start) * 1000.0)

        if len(self.latencies_ms) > 1000:
            del self.latencies_ms[0]

        return {
            "order_id": order_id,
            "side": normalized_side,
            "price_paise": price_paise,
            "quantity": quantity,
            "status": "accepted",
        }

    cpdef dict get_stats(self):
        return {
            "orders_processed": self.orders_processed,
            "buy_orders": self.buy_orders,
            "sell_orders": self.sell_orders,
            "total_quantity": self.total_quantity,
        }

    cpdef dict get_performance_stats(self):
        cdef double elapsed = perf_counter() - self.start_time
        cdef double average_latency = 0.0

        if self.latencies_ms:
            average_latency = sum(self.latencies_ms) / len(self.latencies_ms)

        return {
            "orders_per_second": (
                self.orders_processed / elapsed if elapsed > 0 else 0.0
            ),
            "average_latency_ms": (
                average_latency if self.latencies_ms else None
            ),
            "latency_unit": "ms",
        }
