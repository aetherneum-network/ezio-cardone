"""docs/ASSUMPTIONS.md is written from the rule files, never by hand.

    python tools/assumptions.py --check
    python tools/assumptions.py --write

Every legal assumption of the pack is a parameter of a rule file with the status [TO CONFIRM with legal].
Offline; standard library only (plus the rule loader of the pack).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dossier import rules_engine  # noqa: E402

TARGET = ROOT / "docs" / "ASSUMPTIONS.md"


def render() -> str:
    rules = rules_engine.load()
    items = rules.legal_assumptions()
    out = ["# Legal assumptions of the pack", "",
           "SYNTHETIC - written from the rule files by `tools/assumptions.py`; do not edit by hand.", "",
           f"The pack makes {len(items)} assumptions that only a qualified professional can confirm. The author is a",
           "synthetic AI agent: not a lawyer, a notary, an accountant or an auditor. None of these assumptions is",
           "legal advice and none has been reviewed by a legal professional. Each one is a parameter of a rule file,",
           "is printed in every dossier, and carries the status `[TO CONFIRM with legal]` until someone qualified",
           "changes it. Changing a value is a change of a rule file (with its inline tests), never of an output.", ""]
    for n, a in enumerate(items, 1):
        value = str(a["value"]).lower() if isinstance(a["value"], bool) else str(a["value"])
        out += [f"## {n}. `{a['parameter']}`", "",
                f"- File: `{a['file']}`", f"- Value in v2.0: `{value}`", "- Status: [TO CONFIRM with legal]", "",
                a["note"], ""]
    out += ["## Not modelled at all", "",
            "Statutory deadlines and obligation calendars, treasury shares, usufruct and pledge over shares, voting",
            "rights that differ from capital rights, beneficial-ownership thresholds, foreign registries. v2.0 says",
            "nothing about them."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    text = render()
    if a.write:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(text.encode("utf-8"))
        print("docs/ASSUMPTIONS.md written")
        return 0
    ok = TARGET.exists() and TARGET.read_bytes() == text.encode("utf-8")
    print("assumptions OK" if ok else "docs/ASSUMPTIONS.md differs from the rule files: run --write")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
