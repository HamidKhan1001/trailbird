import socket

import pytest

from trailbird.errors import NetworkBlockedError
from trailbird.offline import block_network


def test_blocks_external_connect():
    with block_network(), pytest.raises(NetworkBlockedError):
        socket.socket().connect(("8.8.8.8", 53))


def test_connect_ex_also_blocked():
    with block_network(), pytest.raises(NetworkBlockedError):
        socket.socket().connect_ex(("8.8.8.8", 53))


def test_loopback_allowed():
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    try:
        with block_network():
            cli = socket.socket()
            cli.connect(srv.getsockname())
            cli.close()
    finally:
        srv.close()


def test_patch_removed_after_exit_and_reentrant():
    original = socket.socket.connect
    with block_network():
        with block_network():
            assert socket.socket.connect is not original
        assert socket.socket.connect is not original  # outer still active
    assert socket.socket.connect is original
