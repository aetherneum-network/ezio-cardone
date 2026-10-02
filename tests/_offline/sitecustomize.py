"""Put on PYTHONPATH by the tests: every child process starts with its sockets blocked."""
import socket


class NetworkBlocked(RuntimeError):
    """A child process of the test suite tried to open a socket."""


def _refuse(*args, **kwargs):
    raise NetworkBlocked("network access is blocked in the test suite")


class _NoSocket(socket.socket):
    def __init__(self, *args, **kwargs):
        _refuse()


socket.socket = _NoSocket
socket.create_connection = _refuse
socket.getaddrinfo = _refuse
socket.socketpair = _refuse
