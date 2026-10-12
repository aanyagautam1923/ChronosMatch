import pytest

from chronosmatch.protocol import ORDER_SIZE, Order


def test_buy_order_pack_unpack():
    order = Order(101, 12550, 10, "B")

    packed = order.pack()

    assert len(packed) == ORDER_SIZE
    assert Order.unpack(packed) == order


def test_sell_order_pack_unpack():
    order = Order(102, 12600, 5, "S")

    assert Order.unpack(order.pack()) == order


def test_invalid_side_is_rejected():
    order = Order(103, 12500, 2, "X")

    with pytest.raises(ValueError):
        order.pack()


def test_invalid_record_size_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Order.unpack(b"short")


def test_order_record_size():
    assert ORDER_SIZE == 20
