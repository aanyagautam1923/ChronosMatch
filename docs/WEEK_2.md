# ChronosMatch - Week 2 Technical Documentation

## 1. Overview

Week 2 improves the order management and matching capabilities of ChronosMatch, an educational high-frequency trading (HFT) engine simulation. It introduces a Limit Order Book, price-time priority, order matching, partial fills, Cython-based performance experimentation, and benchmark reporting.

This project is an educational simulation and is not connected to a real exchange.

## 2. Limit Order Book

The Limit Order Book maintains outstanding buy and sell orders.

- Bids: Buy orders.
- Asks: Sell orders.
- Best bid: Highest outstanding buy price.
- Best ask: Lowest outstanding sell price.

The implementation is available in `chronosmatch/order_book.py`.

## 3. Price-Time Priority

Orders are prioritised by price and then by arrival time.

- Buy orders with higher prices receive priority.
- Sell orders with lower prices receive priority.
- Orders at the same price are processed in arrival order.

## 4. Order Matching and Partial Fills

When a new order crosses the opposite side of the book, the order book attempts to match it against eligible resting orders.

The matching process supports:
- Trade execution when buy and sell prices cross.
- Partial fills when the available quantity is smaller than the incoming order quantity.
- Remaining quantities staying in the book when they cannot be fully matched.
- Best bid and best ask inspection.
- Book snapshots with configurable depth.

## 5. Cython Performance Experiment

The Cython implementation is provided in `chronosmatch/engine_cython.pyx`.

To build the extension in the development environment, activate the virtual environment and run:

`python setup.py build_ext --inplace`

A successful build creates native build artifacts locally. Generated C and platform-specific extension files are build outputs and are not intended to be committed as source files.

## 6. Benchmark Results

The saved Python-versus-Cython comparison report is located at `data/benchmarks/week2_comparison_results.json`.

Recorded results from that comparison run:

| Metric | Python | Cython |
|---|---:|---:|
| Average throughput | 192,752.09 orders/sec | 246,440.17 orders/sec |
| Best throughput | 241,969.63 orders/sec | 309,371.48 orders/sec |
| Average latency | 0.004285 ms | 0.003606 ms |
| Median latency | 0.0023 ms | 0.0011 ms |

The recorded comparison reports approximately 1.28x Cython speedup for that run. Results depend on hardware, system load, and benchmark conditions; they should not be treated as production performance guarantees.

Python benchmark results are also saved in `data/benchmarks/week2_python_results.json`.

## 7. Running Tests

Activate the project's virtual environment, then run:

`python -m pytest -q`

The tests cover the API, engine, order book, protocol, ring buffer, and firehose components.

## 8. Project Limitations

- This project is an educational trading-engine simulation.
- It does not connect to an exchange or execute real financial transactions.
- Benchmark measurements are local experimental results.
- Performance can vary between machines and runs.

## 9. Week 2 Completion Checklist

- [x] Limit Order Book implementation
- [x] Price-time priority
- [x] Matching and partial-fill test coverage
- [x] Cython source and build configuration
- [x] Python/Cython benchmark comparison report
- [x] Week 2 technical documentation
- [x] Automated test suite
