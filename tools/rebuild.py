"""Two independent rebuilds in two different folders, compared byte by byte (DOCX included).

    python tools/rebuild.py            # scenario S03 and the development corpus, each built twice
    python tools/rebuild.py --quick    # scenario S03 only

Prints the SHA-256 of what was built; exit code 1 if the two builds differ in any file. The hashes are
comparable between machines: what is verified, and on which operating system, is said in the README.
Offline; no clock, no environment variable.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from corpus import generate  # noqa: E402
from dossier import run as runner  # noqa: E402


def tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def digest(hashes: dict[str, str]) -> str:
    lines = "".join(f"{h}  {rel}\n" for rel, h in sorted(hashes.items()))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def build_twice(input_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    out = []
    for name in ("first build", "second build in another folder"):
        work = Path(tempfile.mkdtemp(prefix="ezio-rebuild-")) / name
        runner.run(input_dir, work, out=io.StringIO())
        out.append(tree(work))
    return out[0], out[1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--quick", action="store_true", help="scenario S03 only")
    a = ap.parse_args(argv)
    same = True

    first, second = build_twice(ROOT / "scenarios" / "S03" / "input")
    same &= first == second
    for rel in ("dossiers/E-0004/dossier.docx", "dossiers/E-0004/provenance.json",
                "shareable/E-0004/dossier_shareable.docx"):
        print(f"S03 {rel}  sha256 {first[rel]}  {'identical' if first[rel] == second.get(rel) else 'DIFFERENT'}")
    print(f"S03 whole build: {len(first)} files, tree sha256 {digest(first)}, "
          f"{'identical in 2 builds' if first == second else 'DIFFERENT'}")

    if not a.quick:
        suite = generate.SUITES["dev"]
        base = Path(tempfile.mkdtemp(prefix="ezio-rebuild-corpus-"))
        generate.write(generate.build_files(suite["seed"]), base)
        first, second = build_twice(base / "input")
        same &= first == second
        docx = sum(1 for f in first if f.endswith(".docx"))
        print(f"dev corpus (seed {suite['seed']}, 150 entities, as of {generate.AS_OF}): {len(first)} files, "
              f"{docx} DOCX, tree sha256 {digest(first)}, "
              f"{'identical in 2 builds' if first == second else 'DIFFERENT'}")
    print("REBUILD OK" if same else "REBUILD DIFFERS")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
