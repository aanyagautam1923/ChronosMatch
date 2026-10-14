# ChronosMatch
### Educational High-Frequency Trading Engine Simulation

ChronosMatch is a Python-based project that simulates important components of a high-frequency trading system. It focuses on efficient order processing, binary data serialization, backend API development, testing, and performance benchmarking.

This project is developed as part of a Python Development Internship.

> **Disclaimer:** ChronosMatch is an educational simulation. It is not connected to a real stock exchange or brokerage and does not execute real trades.

---

## Project Objectives

- Understand the basic architecture of a trading engine.
- Implement a compact binary order protocol.
- Process orders using an in-memory engine.
- Develop REST APIs using FastAPI.
- Explore ring buffers and TCP-based order streaming.
- Write automated tests using pytest.
- Measure order-processing performance through benchmarking.
- Maintain project code using Git and GitHub.

---

## Key Features

### 1. Binary Order Protocol
Provides functionality for packing and unpacking structured order records in binary format.

### 2. Trading Engine
Implements an in-memory order-processing component and tracks basic engine statistics.

### 3. Ring Buffer
Demonstrates fixed-capacity buffer operations and FIFO processing concepts.

### 4. TCP Firehose
Explores sending and receiving binary order records over a TCP connection.

### 5. FastAPI Backend
Provides HTTP endpoints for health checks, order submission, and engine statistics.

### 6. Performance Benchmarking
Measures the time required to process a configurable number of orders.

### 7. Automated Testing
Uses pytest to validate application components and reduce regressions.

---

## Technology Stack

- Python 3.12+
- FastAPI
- Uvicorn
- pytest
- HTTPX
- HTML
- CSS
- JavaScript
- Git and GitHub

---

## Project Structure

```text
ChronosMatch/
├── app/
│   ├── main.py
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── script.js
├── benchmarks/
│   └── benchmark_engine.py
├── chronosmatch/
│   ├── __init__.py
│   ├── protocol.py
│   ├── engine.py
│   ├── ring_buffer.py
│   └── firehose.py
├── data/
│   └── sample_orders.csv
├── tests/
│   ├── test_api.py
│   ├── test_engine.py
│   ├── test_firehose.py
│   ├── test_protocol.py
│   └── test_ring_buffer.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/aanyagautam1923/ChronosMatch.git
cd ChronosMatch
```

### Step 2: Create a virtual environment

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## Run the Application

Start the FastAPI server:

```powershell
python -m uvicorn app.main:app --reload
```

Once the server starts, open the following addresses in your browser.

| Resource | Address |
|---|---|
| Application | http://127.0.0.1:8000/ |
| Health Check | http://127.0.0.1:8000/health |
| Interactive API Documentation | http://127.0.0.1:8000/docs |

The API documentation can be used to inspect and test the available endpoints.

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Returns the application home response |
| GET | `/health` | Checks API availability |
| POST | `/orders` | Submits an order |
| GET | `/stats` | Retrieves engine statistics |

The exact request and response formats can be inspected through the interactive API documentation.

---

## Running Tests

Run the complete test suite:

```powershell
python -m pytest -v
```

Run protocol tests separately:

```powershell
python -m pytest tests/test_protocol.py -v
```

Run ring buffer tests separately:

```powershell
python -m pytest tests/test_ring_buffer.py -v
```

### Current Testing Status

An earlier test run completed successfully with **21 tests passed**.

Run the tests again after making changes to confirm the current project status.

---

## Performance Benchmark

Run the benchmark using:

```powershell
python -m benchmarks.benchmark_engine --orders 10000 --repeats 3
```

An earlier local benchmark reported approximately 492,015 orders per second.

This result depends on the machine, implementation, and benchmark workload. It should not be interpreted as guaranteed real-world exchange performance.

---

## Sample Data

The `data/` directory is intended to contain sample order records for development and testing.

Sample records may include:

- Order ID
- Order side (Buy or Sell)
- Price
- Quantity
- Order status

The sample dataset is fictional and is not real stock-market data.

---

## Future Improvements

- Complete and refine the interactive web dashboard.
- Improve order validation and error handling.
- Display engine statistics dynamically.
- Expand automated test coverage.
- Improve benchmark reporting.
- Add structured logging and monitoring.
- Improve project documentation and demonstration materials.

---

## Learning Outcomes

This project provides practical experience with:

- Python application development
- Binary data serialization
- Data structures and buffering
- REST API development
- TCP networking concepts
- Automated testing
- Performance measurement
- Git and GitHub workflows

---

## Author

Developed as a Python Development Internship Project.

**Repository:** [ChronosMatch on GitHub](https://github.com/aanyagautam1923/ChronosMatch)

---

## License and Usage

This project is intended for educational and demonstration purposes.

It is not a production trading system and must not be used to execute real financial transactions.
