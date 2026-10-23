import json
import platform
import statistics
import sys
import time
from pathlib import Path

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order
from chronosmatch.engine_cython import CythonEngine


def benchmark_python(order_count, repeats):
    throughputs = []
    latencies = []

    for run in range(repeats):
        engine = TradingEngine()
        start = time.perf_counter()

        for order_id in range(1, order_count + 1):
            order = Order(
                order_id=order_id,
                price_paise=10000,
                quantity=1,
                side="B" if order_id % 2 else "S",
            )
            order_start = time.perf_counter()
            engine.process_order(order)
            latencies.append((time.perf_counter() - order_start) * 1000)

        elapsed = time.perf_counter() - start
        throughputs.append(order_count / elapsed)

    return {
        "average_throughput_orders_per_second": round(statistics.mean(throughputs), 2),
        "best_throughput_orders_per_second": round(max(throughputs), 2),
        "average_latency_ms": round(statistics.mean(latencies), 6),
        "median_latency_ms": round(statistics.median(latencies), 6),
    }


def benchmark_cython(order_count, repeats):
    throughputs = []
    latencies = []

    for run in range(repeats):
        engine = CythonEngine()
        start = time.perf_counter()

        for order_id in range(1, order_count + 1):
            side = "B" if order_id % 2 else "S"
            order_start = time.perf_counter()
            engine.process_order(order_id, 10000, 1, side)
            latencies.append((time.perf_counter() - order_start) * 1000)

        elapsed = time.perf_counter() - start
        throughputs.append(order_count / elapsed)

    return {
        "average_throughput_orders_per_second": round(statistics.mean(throughputs), 2),
        "best_throughput_orders_per_second": round(max(throughputs), 2),
        "average_latency_ms": round(statistics.mean(latencies), 6),
        "median_latency_ms": round(statistics.median(latencies), 6),
    }


orders = 10000
repeats = 3

report = {
    "project": "ChronosMatch",
    "benchmark_type": "Python vs compiled Cython",
    "environment": {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
    },
    "configuration": {
        "orders_per_run": orders,
        "repetitions": repeats,
    },
    "python_engine": benchmark_python(orders, repeats),
    "cython_engine": benchmark_cython(orders, repeats),
    "notes": [
        "Local educational simulation measurements.",
        "Not production exchange performance.",
        "Results may vary with system load and runtime conditions.",
    ],
}

python_rate = report["python_engine"]["average_throughput_orders_per_second"]
cython_rate = report["cython_engine"]["average_throughput_orders_per_second"]

report["cython_speedup_ratio"] = round(cython_rate / python_rate, 2) if python_rate else None

output = Path("data/benchmarks/week2_comparison_results.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=4), encoding="utf-8")

print("Comparison report saved:", output)
print(json.dumps(report, indent=4))
