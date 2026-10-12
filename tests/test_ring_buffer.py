import pytest

from chronosmatch.ring_buffer import RingBuffer


def test_buffer_stores_and_returns_items():
    buffer = RingBuffer(3)

    buffer.put(b"first")
    buffer.put(b"second")

    assert len(buffer) == 2
    assert buffer.get() == b"first"
    assert buffer.get() == b"second"
    assert buffer.is_empty()


def test_buffer_wraps_around():
    buffer = RingBuffer(2)

    buffer.put(b"A")
    buffer.put(b"B")

    assert buffer.get() == b"A"

    buffer.put(b"C")

    assert buffer.get() == b"B"
    assert buffer.get() == b"C"


def test_full_buffer_raises_error():
    buffer = RingBuffer(1)
    buffer.put(b"A")

    with pytest.raises(BufferError):
        buffer.put(b"B")


def test_empty_buffer_raises_error():
    buffer = RingBuffer(2)

    with pytest.raises(BufferError):
        buffer.get()


def test_zero_capacity_is_rejected():
    with pytest.raises(ValueError):
        RingBuffer(0)


def test_non_bytes_item_is_rejected():
    buffer = RingBuffer(2)

    with pytest.raises(TypeError):
        buffer.put("not bytes")
