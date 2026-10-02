"""Offline test suite. Importing this package blocks every socket of the process.

    python -m unittest discover -s tests -t .

Child processes started by the tests get the same block through ``tests/_offline/sitecustomize.py``.
"""
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "scenarios"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


class NetworkBlocked(RuntimeError):
    """A test tried to open a socket."""


def _refuse(*args, **kwargs):
    raise NetworkBlocked("network access is blocked in the test suite")


class _NoSocket(socket.socket):
    def __init__(self, *args, **kwargs):
        _refuse()


socket.socket = _NoSocket
socket.create_connection = _refuse
socket.getaddrinfo = _refuse
socket.socketpair = _refuse
