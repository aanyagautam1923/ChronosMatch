"""Standalone project health audit for ChronosMatch Week 2.

This utility does not modify the application, frontend, backend,
order book, benchmark reports, or project configuration.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "app/main.py",
    "app/static/index.html",
    "app/static/style.css",
    "app/static/script.js",
    "chronosmatch/engine.py",
    "chronosmatch/order_book.py",
    "chronosmatch/protocol.py",
    "chronosmatch/ring_buffer.py",
    "chronosmatch/firehose.py",
    "chronosmatch/engine_cython.pyx",
    "tests/test_api.py",
    "tests/test_engine.py",
    "tests/test_order_book.py",
    "tests/test_protocol.py",
    "tests/test_ring_buffer.py",
    "docs/WEEK_2.md",
    "setup.py",
    "requirements.txt",
]

BENCHMARK_FILES = [
    "data/benchmarks/week2_python_results.json",
    "data/benchmarks/week2_comparison_results.json",
]


def check_file(relative_path):
    path = ROOT / relative_path
    passed = path.is_file() and path.stat().st_size > 0
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] Required file: {relative_path}")
    return passed


def check_json(relative_path):
    path = ROOT / relative_path

    if not path.is_file():
        print(f"[WARN] Benchmark report missing: {relative_path}")
        return None

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"[FAIL] Invalid JSON: {relative_path} ({error})")
        return False

    print(f"[PASS] Valid JSON: {relative_path}")
    return True


def main():
    print("=" * 58)
    print("CHRONOSMATCH - WEEK 2 PROJECT HEALTH AUDIT")
    print("=" * 58)

    results = [check_file(path) for path in REQUIRED_FILES]
    benchmark_results = [
        check_json(path) for path in BENCHMARK_FILES
    ]

    passed = sum(results)
    failed = len(results) - passed
    valid_reports = sum(result is True for result in benchmark_results)
    invalid_reports = sum(result is False for result in benchmark_results)
    missing_reports = sum(result is None for result in benchmark_results)

    print("\n" + "-" * 58)
    print(f"Required files: {passed}/{len(REQUIRED_FILES)} passed")
    print(f"Valid benchmark reports: {valid_reports}/{len(BENCHMARK_FILES)}")
    print(f"Invalid reports: {invalid_reports}")
    print(f"Missing reports: {missing_reports}")

    if failed or invalid_reports:
        print("\nAudit result: ISSUES FOUND")
        return 1

    print("\nAudit result: STRUCTURE CHECK PASSED")
    print("Note: This audit does not replace automated tests or")
    print("manual verification of the dashboard and API.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
