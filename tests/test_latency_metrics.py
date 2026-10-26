import pytest

from chronosmatch.latency import LatencyTracker


def test_record_uses_nanoseconds():
    tracker = LatencyTracker()
    latency = tracker.record(100, 175)

    assert latency == 75
    assert tracker.get_stats()["average_latency_ns"] == 75


def test_empty_tracker_returns_none_for_latency_metrics():
    stats = LatencyTracker().get_stats()

    assert stats["latency_samples"] == 0
    assert stats["average_latency_ns"] is None
    assert stats["min_latency_ns"] is None
    assert stats["max_latency_ns"] is None
    assert stats["p95_latency_ns"] is None


def test_percentiles_and_average():
    tracker = LatencyTracker()

    for value in (10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        tracker.record(0, value)

    stats = tracker.get_stats()

    assert stats["average_latency_ns"] == 55
    assert stats["min_latency_ns"] == 10
    assert stats["max_latency_ns"] == 100
    assert stats["p50_latency_ns"] == 50
    assert stats["p95_latency_ns"] == 100
    assert stats["p99_latency_ns"] == 100


def test_sample_history_is_bounded():
    tracker = LatencyTracker(max_samples=3)

    for value in (10, 20, 30, 40):
        tracker.record(0, value)

    stats = tracker.get_stats()

    assert stats["latency_samples"] == 3
    assert stats["total_timed_operations"] == 4
    assert stats["average_latency_ns"] == 30


def test_invalid_max_samples():
    with pytest.raises(ValueError):
        LatencyTracker(max_samples=0)


def test_invalid_timestamp_order():
    tracker = LatencyTracker()

    with pytest.raises(ValueError):
        tracker.record(200, 100)


def test_invalid_timestamp_type():
    tracker = LatencyTracker()

    with pytest.raises(TypeError):
        tracker.record("100", 200)


def test_start_returns_integer_timestamp():
    timestamp = LatencyTracker().start()

    assert isinstance(timestamp, int)
    assert timestamp >= 0
