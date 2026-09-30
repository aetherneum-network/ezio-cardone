"""Canonical JSON in and out.

* Output is sorted, two-space indented, UTF-8, LF, with a trailing newline: the same data gives the
  same bytes on every operating system.
* Input refuses floats: a share or an amount is a string (``"1/3"``, ``"50000.00"``), never a float.
* A write is verified by reading the file back; a failed write raises (a failed write is a failed run).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


class FloatRefused(ValueError):
    """A JSON document contained a floating-point number."""


class WriteFailed(OSError):
    """A file was not written as requested."""


def _no_float(token: str) -> Any:
    raise FloatRefused(f"floating-point literal {token!r} refused: use a decimal or fraction string")


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def loads(text: str) -> Any:
    return json.loads(text, parse_float=_no_float, parse_constant=_no_float)


def load(path: os.PathLike | str) -> Any:
    return loads(read_text(path))


def ext(path: os.PathLike | str) -> str:
    """Absolute path that survives the Windows 260-character limit."""
    s = os.path.abspath(str(path))
    if os.name == "nt" and not s.startswith("\\\\?\\"):
        return "\\\\?\\" + s
    return s


def read_bytes(path: os.PathLike | str) -> bytes:
    with open(ext(path), "rb") as fh:
        return fh.read()


def read_text(path: os.PathLike | str) -> str:
    return read_bytes(path).decode("utf-8")


def write_bytes(path: os.PathLike | str, data: bytes, *, exclusive: bool = False) -> str:
    """Write ``data`` and verify it. ``exclusive`` refuses to replace an existing file. Returns SHA-256."""
    p = Path(path)
    os.makedirs(ext(p.parent), exist_ok=True)
    target = ext(p)
    if exclusive:
        with open(target, "xb") as fh:  # FileExistsError if the file is already there
            fh.write(data)
    else:
        tmp = target + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, target)
    if read_bytes(p) != data:
        raise WriteFailed(f"write verification failed for {p.name}")
    return hashlib.sha256(data).hexdigest()


def write_text(path: os.PathLike | str, text: str, *, exclusive: bool = False) -> str:
    return write_bytes(path, text.replace("\r\n", "\n").encode("utf-8"), exclusive=exclusive)


def write(path: os.PathLike | str, obj: Any, *, exclusive: bool = False) -> str:
    return write_text(path, dumps(obj), exclusive=exclusive)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: os.PathLike | str) -> str:
    return hashlib.sha256(read_bytes(path)).hexdigest()
