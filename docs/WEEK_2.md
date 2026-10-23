# ChronosMatch - Week 2 Technical Documentation

## 1. Overview

Week 2 focuses on improving the order management and matching
capabilities of ChronosMatch, an educational high-frequency trading
(HFT) engine simulation.

The main objectives are:
- Implement a Limit Order Book.
- Support price-time priority.
- Match incoming buy and sell orders.
- Handle partial order execution.
- Prepare a Cython-based engine for performance optimization.
- Test correctness and prepare performance benchmarks.

## 2. Limit Order Book

A Limit Order Book maintains outstanding buy and sell orders.

It contains two sides:

- Bids: Buy orders.
- Asks: Sell orders.

The best bid is the highest available buy price.
The best ask is the lowest available sell price.

When compatible buy and sell orders arrive, the engine attempts
to match them.

## 3. Price-Time Priority

The matching system follows price-time priority.

For buy orders:
- A higher price has priority.
- At the same price, the earlier order has priority.

For sell orders:
- A lower price has priority.
- At the same price, the earlier order has priority.

This approach provides deterministic ordering when multiple
orders compete for execution.

## 4. Order Matching

An incoming order is compared with compatible orders on the
opposite side of the book.

If the prices are compatible, the engine matches the smaller
remaining quantity.

Possible outcomes:

- Full execution: The incoming order is completely filled.
- Partial execution: Only part of the incoming order is filled.
- Resting order: The unfilled quantity remains in the book.

The implementation must preserve the remaining quantity
correctly after partial execution.

## 5. Cython Optimization

The project includes a Cython source file:

`chronosmatch/engine_cython.pyx`

The purpose is to compile performance-sensitive engine logic
into a native extension.

The source code has been prepared, but successful native
compilation and performance comparison must be verified after
the required C++ build tools are available.

Python and Cython benchmark results should be measured using
the same workload and comparable conditions.

## 6. Testing Strategy

The order book test suite covers important behaviours:

- Adding buy orders.
- Adding sell orders.
- Matching compatible orders.
- Price priority.
- Time priority.
- Partial fills.
- Remaining quantities.
- Invalid order handling.
- Snapshot depth validation.
- Empty order book behaviour.

Run the order book tests with:

`python -m pytest tests/test_order_book.py -v`

Run the complete test suite with:

`python -m pytest -v`

## 7. Performance Measurement

Performance evaluation should consider:

- Orders processed per second.
- Average processing latency.
- Number of processed orders.
- Buy and sell order counts.
- Total processed quantity.

A fair comparison should use the same input workload and
multiple benchmark repetitions.

Benchmark results should be recorded rather than assumed.

## 8. Complexity Considerations

The theoretical complexity depends on the data structures
and matching implementation.

Typical considerations include:

- Inspecting the best bid or ask: O(1) when directly accessible.
- Finding a matching order: depends on the book structure.
- Matching multiple orders: depends on the number of orders filled.
- Generating a snapshot of depth k: at least O(k) to return k entries.

These are general expectations, not guaranteed performance
measurements of the current implementation.

## 9. Week 2 Completion Checklist

- [x] Implement the Limit Order Book.
- [x] Add price-time priority behaviour.
- [x] Add order book unit tests.
- [x] Prepare the Cython engine source.
- [ ] Complete native Cython compilation.
- [ ] Verify the compiled extension.
- [ ] Implement and validate benchmark comparisons.
- [ ] Record measured performance results.
- [ ] Run the complete test suite.
- [ ] Commit and push the verified Week 2 changes.

## 10. Project Scope

ChronosMatch is an educational trading engine simulation.
It is not a production exchange and does not connect to a
real stock market or execute real financial transactions.
