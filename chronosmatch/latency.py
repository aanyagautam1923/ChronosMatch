from collections import deque
from math import ceil
from threading import Lock
from time import perf_counter_ns


class LatencyTracker:
    """Thread-safe nanosecond latency tracker with bounded history."""

    def __init__(self, max_samples: int = 1000):
        if not isinstance(max_samples, int) or isinstance(max_samples, bool):
            raise TypeError("max_samples must be an integer")
        if max_samples < 1:
            raise ValueError("max_samples must be at least 1")

        self.max_samples = max_samples
        self._samples = deque(maxlen=max_samples)
        self._lock = Lock()
        self._total_operations = 0

    def start(self) -> int:
        """Return an operation entry timestamp in nanoseconds."""
        return perf_counter_ns()

    def record(self, start_ns: int, end_ns: int | None = None) -> int:
        """Record an operation duration and return its latency in nanoseconds."""
        if not isinstance(start_ns, int) or isinstance(start_ns, bool):
            raise TypeError("start_ns must be an integer")

        if end_ns is None:
            end_ns = perf_counter_ns()

        if not isinstance(end_ns, int) or isinstance(end_ns, bool):
            raise TypeError("end_ns must be an integer")

        if start_ns < 0 or end_ns < start_ns:
            raise ValueError("timestamps must be non-negative and end_ns >= start_ns")

        latency_ns = end_ns - start_ns

        with self._lock:
            self._samples.append(latency_ns)
            self._total_operations += 1

        return latency_ns

    def get_stats(self) -> dict:
        """Return latency statistics for the retained sample window."""
        with self._lock:
            samples = sorted(self._samples)
            total_operations = self._total_operations

        count = len(samples)

        def percentile(percent: float):
            if not samples:
                return None
            index = max(0, ceil(percent * count) - 1)
            return samples[min(index, count - 1)]

        average_ns = sum(samples) / count if count else None

        return {
            "latency_unit": "ns",
            "latency_samples": count,
            "total_timed_operations": total_operations,
            "average_latency_ns": average_ns,
            "min_latency_ns": min(samples) if samples else None,
            "max_latency_ns": max(samples) if samples else None,
            "p50_latency_ns": percentile(0.50),
            "p95_latency_ns": percentile(0.95),
            "p99_latency_ns": percentile(0.99),
        }
