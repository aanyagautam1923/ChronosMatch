# ChronosMatch — Week 3 Technical Documentation

## Overview

Week 3 connects the earlier protocol, matching engine, and dashboard through a
fixed-capacity ring buffer, a TCP order firehose, latency tracking, and HTTP
endpoints for the live order book and recent trades. ChronosMatch remains an
educational simulation and does not connect to an exchange or execute real
financial transactions.

## Ring Buffer and Engine Flow

`TradingEngine.process_order` validates an order by packing it into the binary
protocol format, enqueues that record in a 1,024-slot FIFO `RingBuffer`, reads
the record back, and submits the reconstructed order to the limit order book.
The engine lock keeps this buffer and matching sequence safe when HTTP and TCP
clients submit orders concurrently. The buffer is currently used synchronously
as an integration stage; it is not a separate worker queue.

## TCP Firehose

The FastAPI application starts a background receiver on `127.0.0.1:9000` during
its lifespan and stops it during shutdown. Clients send fixed-size binary
records using the format documented in `chronosmatch/protocol.py`. The receiver
handles partial socket reads and multiple records per connection. If the port
cannot be bound, the HTTP application still starts and reports the firehose as
offline in `/stats`.

## Latency and Statistics

The engine tracks processing and trade-generating operation latency in
nanoseconds, with bounded sample history. `/stats` reports total and recent
throughput, latency percentiles, and component states. The dashboard refreshes
these statistics alongside the order history, book depth, and recent trades.

## HTTP API

| Method | Endpoint | Result |
|---|---|---|
| GET | `/health` | API health |
| POST | `/orders` | Validate and process a buy (`B`) or sell (`S`) order |
| GET | `/orders` | Accepted order history |
| GET | `/orderbook?depth=5` | Aggregated bid and ask levels |
| GET | `/trades?limit=100` | Most recent executions |
| GET | `/stats` | Engine, performance, and component statistics |

Prices in API order book and trade records use integer paise (`price_paise`);
the dashboard displays these values in rupees. Limits are validated by the API:
book depth is 1–100 and trade limit is 1–1,000.

## Verification

Run the complete suite from the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Start the application with `python -m uvicorn app.main:app --reload`, then
verify `/`, `/health`, `/stats`, `/orders`, `/orderbook`, and `/trades` through
the browser or the interactive API documentation at `/docs`.
