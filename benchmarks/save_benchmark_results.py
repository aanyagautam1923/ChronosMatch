import json
import platform
import statistics
import subprocess
import sys
import time

from pathlib import Path

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order


def run_benchmark(order_count=10000, repeats=3):
    throughputs = []
    latencies = []

    for run in range(1, repeats + 1):
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
        throughput = order_count / elapsed
        throughputs.append(throughput)

        print(
            f"Run {run}/{repeats}: "
            f"{throughput:,.0f} orders/sec"
        )

    return {
        "orders_per_run": order_count,
        "repetitions": repeats,
        "average_throughput_orders_per_second": round(
            statistics.mean(throughputs), 2
        ),
        "best_throughput_orders_per_second": round(max(throughputs), 2),
        "average_latency_ms": round(statistics.mean(latencies), 6),
        "median_latency_ms": round(statistics.median(latencies), 6),
    }


def main():
    result = run_benchmark()

    report = {
        "project": "ChronosMatch",
        "benchmark_type": "Python TradingEngine",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "results": result,
        "notes": [
            "Local educational simulation measurements.",
            "Not production exchange performance.",
            "Cython comparison pending native compilation.",
        ],
    }

    output = Path("data/benchmarks/week2_python_results.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=4), encoding="utf-8")

    print("\nBenchmark report saved to:", output)
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
