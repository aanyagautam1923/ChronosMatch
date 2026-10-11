import socket
from collections.abc import Callable

from chronosmatch.protocol import ORDER_SIZE, Order


def receive_exact(sock: socket.socket, size: int) -> bytes | None:
    """Receive exactly size bytes, or return None on a clean disconnect."""
    chunks = bytearray()

    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))

        if not chunk:
            if not chunks:
                return None
            raise ConnectionError("Connection closed during a record")

        chunks.extend(chunk)

    return bytes(chunks)


def handle_client(
    conn: socket.socket,
    on_order: Callable[[Order], object],
) -> int:
    """Receive and process fixed-size binary orders from one client."""
    processed = 0

    with conn:
        while True:
            record = receive_exact(conn, ORDER_SIZE)

            if record is None:
                break

            order = Order.unpack(record)
            on_order(order)
            processed += 1

    return processed


def serve(
    host: str = "127.0.0.1",
    port: int = 9000,
    on_order: Callable[[Order], object] | None = None,
) -> None:
    """Run a simple TCP order receiver until interrupted."""
    if on_order is None:
        on_order = lambda order: print(
            f"Received order: {order.order_id} {order.side} "
            f"price={order.price_paise} quantity={order.quantity}"
        )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()

        print(f"ChronosMatch firehose listening on {host}:{port}")

        while True:
            conn, _address = server.accept()
            try:
                handle_client(conn, on_order)
            except (ConnectionError, ValueError) as exc:
                print(f"Client record error: {exc}")
