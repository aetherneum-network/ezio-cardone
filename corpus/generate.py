"""Generate one synthetic corpus and its gold from a seed.

    python -m corpus.generate --suite dev --out build/corpus/dev     # dev = seed 20260930
    python -m corpus.generate --seed 123456 --out build/corpus/any   # any other seed
    python -m corpus.generate --check                                # regenerate, compare with MANIFEST.sha256

``--out`` must be a new or empty folder (nothing is overwritten). It receives

    input/entities/<entity>/<date>_<kind>.txt    source documents (SYNTHETIC marker on line 1)
    input/identity/persons.json                  the identity layer (invented persons)
    input/config.json                            as_of and the salt of the shareable layer
    gold.json                                    gold labels, computed from the plan, not from the text
    perturbations.json                           only with --perturb: what was changed in which document

Same seed, same bytes: no clock, no environment, no network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

from . import gold as gold_mod
from . import perturb as perturb_mod
from . import templates
from .world import AS_OF, build_world


def dumps(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_files(seed: int, entities: int = 150, as_of: str = AS_OF, perturb: bool = False) -> dict[str, bytes]:
    """Every file of the corpus, keyed by its posix path relative to the output folder."""
    world = build_world(seed, entities, as_of)
    files: dict[str, bytes] = {}
    changed: dict[str, list[str]] = {}
    for eid in sorted(world.entities):
        for doc in world.entities[eid].docs:
            text = templates.render(doc, world)
            if perturb:
                text, done = perturb_mod.perturb(text, random.Random(f"{seed}:{doc.doc_id}"))
                if done:
                    changed[doc.doc_id] = done
            rel = f"input/entities/{doc.folder}/{doc.filename}"
            if rel in files:
                raise RuntimeError(f"two planned documents share the path {rel}")
            files[rel] = text.encode("utf-8")
    files["input/identity/persons.json"] = dumps(world.persons)
    files["input/config.json"] = dumps({"as_of": as_of, "shareable_salt": f"synthetic-salt-{seed}",
                                        "seed": seed, "synthetic": True})
    gold = gold_mod.world_gold(world)
    gold["perturbed"] = perturb
    files["gold.json"] = dumps(gold)
    if perturb:
        files["perturbations.json"] = dumps(changed)
    return files


def manifest_lines(files: dict[str, bytes], suite: str) -> list[str]:
    return [f"{hashlib.sha256(files[rel]).hexdigest()}  {suite}/{rel}" for rel in sorted(files)]


def check(files: dict[str, bytes], manifest: Path, suite: str) -> list[str]:
    """Differences between the generated files and the lines of the manifest for this suite."""
    want = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            digest, rel = line.split("  ", 1)
            if rel.startswith(suite + "/"):
                want[rel] = digest
    got = {line.split("  ", 1)[1]: line.split("  ", 1)[0] for line in manifest_lines(files, suite)}
    problems = [f"missing from the manifest: {r}" for r in sorted(set(got) - set(want))]
    problems += [f"not generated: {r}" for r in sorted(set(want) - set(got))]
    problems += [f"differs: {r}" for r in sorted(set(got) & set(want)) if got[r] != want[r]]
    return problems


def write(files: dict[str, bytes], out: Path) -> None:
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"{out} is not empty: choose a new folder (nothing is overwritten)")
    for rel, data in files.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if path.read_bytes() != data:
            raise OSError(f"write not verified: {rel}")


SUITES = {
    "dev": {"seed": 20260930, "perturb": False, "role": "development: inspected while the rules were written"},
    "holdout": {"seed": 20261001, "perturb": False, "role": "holdout: generated and scored, never inspected"},
    "stress": {"seed": 20261002, "perturb": True,
               "role": "stress: perturbed wording, used for diagnosis and declared as such"},
}
MANIFEST = Path(__file__).resolve().parent / "MANIFEST.sha256"
MANIFEST_HEAD = [
    "# sha256 of every generated file of the three suites (as_of 2026-09-30):",
    "#   dev seed 20260930 - holdout seed 20261001 - stress seed 20261002 (perturbed)",
    "# check: python -m corpus.generate --check",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="corpus.generate", description=__doc__.split("\n\n")[0])
    ap.add_argument("--seed", type=int, help="any seed; optional when --suite names dev, holdout or stress")
    ap.add_argument("--suite", help="dev, holdout or stress: takes the seed (and the perturbation) of that suite")
    ap.add_argument("--out", help="new or empty output folder")
    ap.add_argument("--entities", type=int, default=150)
    ap.add_argument("--as-of", dest="as_of", default=AS_OF)
    ap.add_argument("--perturb", action="store_true", help="same content, said otherwise (stress)")
    ap.add_argument("--check", action="store_true",
                    help="regenerate the suites in memory and compare with corpus/MANIFEST.sha256")
    ap.add_argument("--write-manifest", action="store_true", help="rewrite corpus/MANIFEST.sha256 for the suites")
    a = ap.parse_args(argv)
    if a.check or a.write_manifest:
        names = [a.suite] if a.suite else sorted(SUITES)
        built = {n: build_files(SUITES[n]["seed"], perturb=SUITES[n]["perturb"]) for n in names}
        if a.write_manifest:
            lines = MANIFEST_HEAD + [x for n in sorted(SUITES) for x in manifest_lines(
                built.get(n) or build_files(SUITES[n]["seed"], perturb=SUITES[n]["perturb"]), n)]
            MANIFEST.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
            print(f"manifest written: {len(lines) - len(MANIFEST_HEAD)} files")
            return 0
        bad = 0
        for n in names:
            problems = check(built[n], MANIFEST, n)
            bad += len(problems)
            for p in problems[:20]:
                print(p)
            print(f"corpus {n} seed {SUITES[n]['seed']}: {len(built[n])} files, "
                  + ("MANIFEST OK" if not problems else f"{len(problems)} DIFFERENCE(S)"))
        return 1 if bad else 0
    seed, perturb = a.seed, a.perturb
    if seed is None:
        if a.suite not in SUITES:
            ap.error("--seed is required unless --suite names dev, holdout or stress")
        seed, perturb = SUITES[a.suite]["seed"], SUITES[a.suite]["perturb"]
    if not a.out:
        ap.error("--out is required (or use --check)")
    files = build_files(seed, a.entities, a.as_of, perturb)
    docs = sum(1 for r in files if r.startswith("input/entities/"))
    try:
        write(files, Path(a.out))
    except OSError as exc:
        print(f"GENERATION FAILED - {exc}")
        return 1
    print(f"corpus seed {seed}: {a.entities} entities, {docs} source documents, as of {a.as_of}"
          + (", perturbed" if perturb else "") + f" -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
