import argparse
import statistics
import time

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order


def benchmark_python_engine(order_count: int, repeats: int) -> dict:
    """Measure Python TradingEngine throughput and latency."""
    throughputs = []
    latencies = []

    for run_number in range(1, repeats + 1):
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
        throughput = order_count / elapsed if elapsed > 0 else 0
        throughputs.append(throughput)

        print(
            f"Run {run_number}/{repeats}: "
            f"{order_count:,} orders in {elapsed:.4f}s "
            f"({throughput:,.0f} orders/sec)"
        )

    return {
        "orders": order_count,
        "repeats": repeats,
        "average_throughput": statistics.mean(throughputs),
        "best_throughput": max(throughputs),
        "average_latency_ms": statistics.mean(latencies),
        "median_latency_ms": statistics.median(latencies),
    }


def benchmark_cython_engine(order_count: int, repeats: int) -> dict | None:
    """Measure the compiled Cython engine when available."""
    try:
        from chronosmatch.engine_cython import CythonEngine
    except ImportError as exc:
        print(f"\nCython extension unavailable: {exc}")
        print("Python benchmark completed; Cython comparison is pending.")
        return None

    throughputs = []
    latencies = []

    for run_number in range(1, repeats + 1):
        engine = CythonEngine()
        start = time.perf_counter()

        for order_id in range(1, order_count + 1):
            side = "B" if order_id % 2 else "S"
            order_start = time.perf_counter()

            engine.process_order(
                order_id=order_id,
                price_paise=10000,
                quantity=1,
                side=side,
            )

            latencies.append((time.perf_counter() - order_start) * 1000)

        elapsed = time.perf_counter() - start
        throughput = order_count / elapsed if elapsed > 0 else 0
        throughputs.append(throughput)

        print(
            f"Run {run_number}/{repeats}: "
            f"{order_count:,} orders in {elapsed:.4f}s "
            f"({throughput:,.0f} orders/sec)"
        )

    return {
        "orders": order_count,
        "repeats": repeats,
        "average_throughput": statistics.mean(throughputs),
        "best_throughput": max(throughputs),
        "average_latency_ms": statistics.mean(latencies),
        "median_latency_ms": statistics.median(latencies),
    }


def print_results(name: str, result: dict) -> None:
    print(f"\n{name}")
    print("-" * len(name))
    print(f"Orders per run       : {result['orders']:,}")
    print(f"Repetitions          : {result['repeats']}")
    print(f"Average throughput   : {result['average_throughput']:,.0f} orders/sec")
    print(f"Best throughput      : {result['best_throughput']:,.0f} orders/sec")
    print(f"Average latency      : {result['average_latency_ms']:.6f} ms")
    print(f"Median latency       : {result['median_latency_ms']:.6f} ms")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark ChronosMatch Python and Cython engines."
    )
    parser.add_argument("--orders", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    if args.orders < 1:
        parser.error("--orders must be at least 1")
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    print("ChronosMatch Engine Benchmark")
    print("=============================")
    print(f"Orders per run: {args.orders:,}")
    print(f"Repetitions: {args.repeats}")

    python_result = benchmark_python_engine(args.orders, args.repeats)
    print_results("Python Engine Results", python_result)

    cython_result = benchmark_cython_engine(args.orders, args.repeats)

    if cython_result is not None:
        print_results("Cython Engine Results", cython_result)

        python_rate = python_result["average_throughput"]
        cython_rate = cython_result["average_throughput"]

        if python_rate > 0:
            print(
                f"\nCython/Python throughput ratio: "
                f"{cython_rate / python_rate:.2f}x"
            )

    print(
        "\nNote: Results are local measurements for an educational simulation, "
        "not production exchange performance."
    )


if __name__ == "__main__":
    main()
