import socket
import threading
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


class FirehoseReceiver:
    """Manage a background TCP receiver for binary orders."""

    def __init__(
        self,
        on_order: Callable[[Order], object],
        host: str = "127.0.0.1",
        port: int = 9000,
    ):
        self.host = host
        self.port = port
        self.on_order = on_order
        self._server: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.last_error: str | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        """Bind the TCP port and start the receiver thread."""
        with self._lock:
            if self.is_running:
                return

            self._stop_event.clear()
            self.last_error = None

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                server.bind((self.host, self.port))
                server.listen()
                server.settimeout(0.5)
            except OSError:
                server.close()
                raise

            self._server = server
            self._thread = threading.Thread(
                target=self._run,
                name="ChronosMatch-Firehose",
                daemon=True,
            )
            self._thread.start()

        print(f"ChronosMatch firehose listening on {self.host}:{self.port}")

    def _run(self) -> None:
        """Accept TCP clients until the receiver is stopped."""
        while not self._stop_event.is_set():
            server = self._server
            if server is None:
                break

            try:
                conn, _address = server.accept()
            except socket.timeout:
                continue
            except OSError:
                if not self._stop_event.is_set():
                    self.last_error = "Firehose socket stopped unexpectedly"
                break

            try:
                handle_client(conn, self.on_order)
            except (ConnectionError, ValueError, OSError) as exc:
                self.last_error = str(exc)
                print(f"Firehose client error: {exc}")

    def stop(self) -> None:
        """Stop the receiver and release its TCP port."""
        self._stop_event.set()

        server = self._server
        self._server = None

        if server is not None:
            server.close()

        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2)

        self._thread = None


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
