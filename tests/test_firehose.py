import socket
import threading

import pytest

from chronosmatch.firehose import receive_exact, handle_client
from chronosmatch.protocol import ORDER_SIZE, Order


def test_receive_exact_reads_requested_bytes():
    left, right = socket.socketpair()

    try:
        right.sendall(b"hello")
        assert receive_exact(left, 5) == b"hello"
    finally:
        left.close()
        right.close()


def test_receive_exact_returns_none_when_connection_closes():
    left, right = socket.socketpair()

    try:
        right.close()
        assert receive_exact(left, 5) is None
    finally:
        left.close()


def test_receive_exact_detects_incomplete_record():
    left, right = socket.socketpair()

    try:
        right.sendall(b"abc")
        right.close()

        with pytest.raises(ConnectionError):
            receive_exact(left, 5)
    finally:
        left.close()


def test_handle_client_processes_binary_order():
    server_sock, client_sock = socket.socketpair()
    received = []

    order = Order(101, 12550, 10, "B")

    def send_order():
        with client_sock:
            client_sock.sendall(order.pack())

    sender = threading.Thread(target=send_order)
    sender.start()

    try:
        count = handle_client(server_sock, received.append)
        assert count == 1
        assert received == [order]
    finally:
        sender.join(timeout=2)
        server_sock.close()


def test_handle_client_handles_multiple_orders():
    server_sock, client_sock = socket.socketpair()
    received = []

    orders = [
        Order(101, 12550, 10, "B"),
        Order(102, 12600, 5, "S"),
    ]

    def send_orders():
        with client_sock:
            client_sock.sendall(b"".join(order.pack() for order in orders))

    sender = threading.Thread(target=send_orders)
    sender.start()

    try:
        count = handle_client(server_sock, received.append)
        assert count == 2
        assert received == orders
    finally:
        sender.join(timeout=2)
        server_sock.close()
