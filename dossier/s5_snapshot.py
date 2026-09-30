"""Stage 5 - dated snapshots in an append-only store.

Each material change of an entity gives a new snapshot file; no snapshot is ever overwritten.

* A snapshot is written with an exclusive create: writing over an existing file raises.
* ``index.jsonl`` has one line per snapshot with its SHA-256 and the hash of the previous line
  (a chain): changing or removing an old snapshot is detected by ``verify``.
* ``at(entity, date)`` answers "what did this entity look like on that date" from the snapshot with
  the latest ``as_of`` not after the date, and says which ``as_of`` the answer is.
* A run whose content equals the latest snapshot of the entity appends nothing.
"""
from __future__ import annotations

import json
from pathlib import Path

from .lib import jsonio

GENESIS = "0" * 64


class SnapshotError(RuntimeError):
    """The snapshot store is inconsistent or an overwrite was attempted."""


class SnapshotStore:
    def __init__(self, directory: Path | str):
        self.dir = Path(directory)
        self.index_path = self.dir / "index.jsonl"

    # -- reading -------------------------------------------------------------------------------
    def entries(self) -> list[dict]:
        if not self.index_path.exists():
            return []
        text = jsonio.read_text(self.index_path)
        return [jsonio.loads(line) for line in text.split("\n") if line.strip()]

    def of(self, entity: str) -> list[dict]:
        return [e for e in self.entries() if e["entity"] == entity]

    def at(self, entity: str, date: str) -> dict | None:
        """The snapshot in force on ``date``: latest ``as_of`` <= date, latest recorded on ties."""
        cands = [e for e in self.of(entity) if e["as_of"] <= date]
        if not cands:
            return None
        e = max(cands, key=lambda x: (x["as_of"], x["seq"]))
        return {"asked": date, "as_of": e["as_of"], "seq": e["seq"], "file": e["file"], "sha256": e["sha256"],
                "snapshot": jsonio.load(self.dir / e["file"])}

    # -- writing -------------------------------------------------------------------------------
    @staticmethod
    def _entry_hash(entry: dict) -> str:
        body = {k: entry[k] for k in sorted(entry) if k != "entry_hash"}
        return jsonio.sha256_bytes(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8"))

    def append(self, entity: str, as_of: str, payload: dict) -> tuple[dict, bool]:
        """Append a snapshot. Returns ``(index entry, created)``; ``created`` is False when nothing changed."""
        entries = self.entries()
        mine = [e for e in entries if e["entity"] == entity]
        content = {"entity": entity, "payload": payload}
        content_hash = jsonio.sha256_bytes(jsonio.dumps(content).encode("utf-8"))
        if mine and mine[-1]["content_sha256"] == content_hash:
            return mine[-1], False
        seq = len(mine) + 1
        rel = f"{entity}/{as_of}__{seq:04d}.json"
        body = {"entity": entity, "as_of": as_of, "seq": seq, "payload": payload}
        sha = jsonio.write(self.dir / rel, body, exclusive=True)
        entry = {"entity": entity, "as_of": as_of, "seq": seq, "file": rel, "sha256": sha,
                 "content_sha256": content_hash,
                 "prev_hash": entries[-1]["entry_hash"] if entries else GENESIS}
        entry["entry_hash"] = self._entry_hash(entry)
        line = json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n"
        old = jsonio.read_bytes(self.index_path) if self.index_path.exists() else b""
        jsonio.write_bytes(self.index_path, old + line.encode("utf-8"))
        return entry, True

    # -- verification --------------------------------------------------------------------------
    def verify(self) -> list[str]:
        """Problems found in the store (an empty list means every snapshot is intact)."""
        problems = []
        prev = GENESIS
        seen: dict[str, int] = {}
        for e in self.entries():
            if e["prev_hash"] != prev:
                problems.append(f"{e['file']}: chain broken")
            if self._entry_hash(e) != e["entry_hash"]:
                problems.append(f"{e['file']}: index line altered")
            prev = e["entry_hash"]
            seen[e["entity"]] = seen.get(e["entity"], 0) + 1
            if e["seq"] != seen[e["entity"]]:
                problems.append(f"{e['file']}: sequence gap")
            path = self.dir / e["file"]
            if not path.exists():
                problems.append(f"{e['file']}: snapshot file missing")
            elif jsonio.sha256_file(path) != e["sha256"]:
                problems.append(f"{e['file']}: snapshot content changed")
        return problems
