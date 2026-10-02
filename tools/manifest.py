"""SHA-256 of every file of the frozen part of the pack: code, rules, schema, corpus generator, scenarios, tests.

    python tools/manifest.py --check     # the files are exactly what MANIFEST.sha256 says
    python tools/manifest.py --write     # rewrite MANIFEST.sha256

Documents that are appended to after the freeze (README, CLAIMS, CHANGELOG, eval/history.json,
eval/BLIND_PROTOCOL.md, eval/results.json) are outside the manifest on purpose. Offline; standard library only (plus the
path helper of the pack, dossier/lib/jsonio.py, itself standard library only).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dossier.lib import jsonio  # noqa: E402

# v2.0.10 (D39): the tree is read with the extended-length prefix, as the pipeline writes, so that a clone in a deep
# folder is hashed whole (a plain is_file() there is False and --write would drop the file without a word)
ROOT = Path(jsonio.ext(ROOT))
MANIFEST = ROOT / "MANIFEST.sha256"
FROZEN_DIRS = ("corpus", "dossier", "rules", "schema", "scenarios", "tests", "tools")
FROZEN_FILES = ("eval/__init__.py", "eval/score.py", "requirements.txt", "docs/ASSUMPTIONS.md")
SKIP_DIRS = {"__pycache__", "out"}


def frozen_files() -> list[Path]:
    found = [ROOT / f for f in FROZEN_FILES if (ROOT / f).exists()]
    for d in FROZEN_DIRS:
        for p in (ROOT / d).rglob("*"):
            if p.is_file() and not (set(p.relative_to(ROOT).parts[:-1]) & SKIP_DIRS) and p.suffix != ".pyc":
                found.append(p)
    return sorted(found, key=lambda p: p.relative_to(ROOT).as_posix())


def lines() -> list[str]:
    return [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}" for p in frozen_files()]


def check() -> list[str]:
    """Differences between the files and the manifest (an empty list means they agree)."""
    if not MANIFEST.exists():
        return ["MANIFEST.sha256 is missing"]
    want = dict(reversed(line.split("  ", 1)) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line)
    have = dict(reversed(line.split("  ", 1)) for line in lines())
    problems = [f"not in the manifest: {f}" for f in sorted(set(have) - set(want))]
    problems += [f"in the manifest but missing: {f}" for f in sorted(set(want) - set(have))]
    problems += [f"changed: {f}" for f in sorted(set(have) & set(want)) if have[f] != want[f]]
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.write:
        MANIFEST.write_bytes(("\n".join(lines()) + "\n").encode("utf-8"))
        print(f"MANIFEST.sha256 written: {len(lines())} files")
        return 0
    problems = check()
    for p in problems:
        print(p)
    print("manifest OK" if not problems else f"manifest: {len(problems)} difference(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
