"""Run scenarios S01-S10 and print one PASS/FAIL line each.

    python scenarios/run_all.py
    python scenarios/run_all.py --json reports/scenarios.json

Offline: no network, no clock, no environment variable. Exit code 1 if any scenario fails.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SCENARIOS = [f"S{n:02d}" for n in range(1, 11)]


def load_check(sid: str):
    spec = importlib.util.spec_from_file_location(f"scenario_{sid}", HERE / sid / "check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check


def run_all() -> tuple[int, list[dict]]:
    results = []
    for sid in SCENARIOS:
        try:
            ok, line, details = load_check(sid)()
        except Exception as exc:  # a crash is a failure, said in the line
            ok, line, details = False, f"{sid} FAIL - {type(exc).__name__}: {exc}", {"scenario": sid, "pass": False}
        print(line, flush=True)
        results.append({"scenario": sid, "pass": ok, "line": line, "details": details.get("details", {})})
    passed = sum(1 for r in results if r["pass"])
    print(f"Scenarios: {passed}/{len(results)} PASS")
    return passed, results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--json", help="write the results to this file")
    a = ap.parse_args(argv)
    passed, results = run_all()
    if a.json:
        from dossier.lib import jsonio
        jsonio.write(Path(a.json), {"schema": "scenarios/2.0.0", "passed": passed, "total": len(results),
                                    "results": results})
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
