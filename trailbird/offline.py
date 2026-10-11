"""Runtime guarantee that inference makes no outbound network connections.

`block_network()` patches socket connects so any non-loopback connection raises
NetworkBlockedError. It is a safety net and a testable claim, not a sandbox.
"""
from __future__ import annotations

import socket
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from .errors import NetworkBlockedError

_LOOPBACK = {"127.0.0.1", "::1", "localhost"}
_lock = threading.Lock()
_depth = 0
_orig_connect = socket.socket.connect
_orig_connect_ex = socket.socket.connect_ex


def _is_allowed(sock: socket.socket, address: Any) -> bool:
    if sock.family == getattr(socket, "AF_UNIX", None):
        return True
    host = address[0] if isinstance(address, tuple) and address else address
    return isinstance(host, str) and host in _LOOPBACK


def _guarded_connect(self: socket.socket, address: Any) -> None:
    if not _is_allowed(self, address):
        raise NetworkBlockedError(f"Offline mode: blocked connection to {address!r}.")
    return _orig_connect(self, address)


def _guarded_connect_ex(self: socket.socket, address: Any) -> int:
    if not _is_allowed(self, address):
        raise NetworkBlockedError(f"Offline mode: blocked connection to {address!r}.")
    return _orig_connect_ex(self, address)


@contextmanager
def block_network() -> Iterator[None]:
    """Reentrant, thread-safe (reference counted) outbound network block."""
    global _depth
    with _lock:
        if _depth == 0:
            socket.socket.connect = _guarded_connect  # type: ignore[method-assign]
            socket.socket.connect_ex = _guarded_connect_ex  # type: ignore[method-assign]
        _depth += 1
    try:
        yield
    finally:
        with _lock:
            _depth -= 1
            if _depth == 0:
                socket.socket.connect = _orig_connect  # type: ignore[method-assign]
                socket.socket.connect_ex = _orig_connect_ex  # type: ignore[method-assign]
