"""Make an OOXML container (DOCX) byte-deterministic.

python-docx stamps every zip entry with the wall clock and the host system. The container is rewritten
with a fixed timestamp, a fixed ``create_system``, no external attributes, the same entry order and a
fixed compression level; the core-property dates are pinned to the ``as_of`` of the build.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import zipfile
from pathlib import Path

from .jsonio import ext

_CORE_DATE = re.compile(rb"(<dcterms:(created|modified)\b[^>]*>)[^<]*(</dcterms:\2>)")


def normalize(path: os.PathLike | str, when: _dt.datetime) -> None:
    p = Path(path)
    iso = when.strftime("%Y-%m-%dT%H:%M:%SZ").encode()
    stamp = (max(when.year, 1980), when.month, when.day, when.hour, when.minute, when.second // 2 * 2)
    with zipfile.ZipFile(ext(p), "r") as src:
        entries = [(i.filename, src.read(i.filename)) for i in src.infolist()]
    tmp = p.with_name(p.name + ".norm")
    with zipfile.ZipFile(ext(tmp), "w") as dst:
        for name, data in entries:
            if name == "docProps/core.xml":
                data = _CORE_DATE.sub(lambda m: m.group(1) + iso + m.group(3), data)
            zi = zipfile.ZipInfo(name, date_time=stamp)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 0
            zi.external_attr = 0
            dst.writestr(zi, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    os.replace(ext(tmp), ext(p))
