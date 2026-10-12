import argparse
import statistics
import time

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order


def run_benchmark(order_count: int, repeats: int = 3) -> None:
    if order_count <= 0:
        raise ValueError("Order count must be greater than zero")

    if repeats <= 0:
        raise ValueError("Repeats must be greater than zero")

    durations = []

    for run in range(repeats):
        engine = TradingEngine()

        start = time.perf_counter()

        for index in range(order_count):
            side = "B" if index % 2 == 0 else "S"
            order = Order(
                order_id=index + 1,
                price_paise=12500 + (index % 100),
                quantity=1 + (index % 10),
                side=side,
            )
            engine.process_order(order)

        elapsed = time.perf_counter() - start
        durations.append(elapsed)

        print(
            f"Run {run + 1}: {order_count:,} orders "
            f"in {elapsed:.6f} seconds"
        )

        assert engine.stats.orders_processed == order_count

    average_seconds = statistics.mean(durations)
    throughput = order_count / average_seconds

    print("\n--- Benchmark Summary ---")
    print(f"Orders per run: {order_count:,}")
    print(f"Runs: {repeats}")
    print(f"Average time: {average_seconds:.6f} seconds")
    print(f"Average throughput: {throughput:,.0f} orders/second")
    print("Note: Educational benchmark; results depend on hardware and workload.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark the ChronosMatch educational trading engine"
    )
    parser.add_argument("--orders", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    run_benchmark(args.orders, args.repeats)
