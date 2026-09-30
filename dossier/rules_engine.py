"""Ordered rule files: the first match wins, exceptions go on top.

The code extracts and applies; it does not interpret. Every rule carries an ``id``, a ``rationale``
and its own ``tests``. When an output is wrong the rule is fixed, never the output; the next build
realigns everything and ``diff_views`` (``dossier.run``) reports exactly what moved.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable

from .lib import jsonio

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"
FILES = ("extract.json", "figure_nature.json", "discrepancy.json", "ownership.json")

_FLAGS = re.IGNORECASE


class RuleError(ValueError):
    """A rule file is malformed."""


@lru_cache(maxsize=4096)
def rx(pattern: str) -> re.Pattern:
    return re.compile(pattern, _FLAGS)


@dataclass(frozen=True)
class Rules:
    """The four rule files, loaded once for a run."""

    directory: str
    extract: dict
    figure_nature: dict
    discrepancy: dict
    ownership: dict

    def param(self, file: str, name: str) -> Any:
        """A parameter value; parameters that carry a status are stored as ``{"value": ...}``."""
        p = getattr(self, file)["parameters"][name]
        return p["value"] if isinstance(p, dict) and "value" in p else p

    def legal_assumptions(self) -> list[dict]:
        """Every parameter marked [TO CONFIRM with legal], in file order."""
        out = []
        for file in ("figure_nature", "discrepancy", "ownership"):
            for name, p in getattr(self, file)["parameters"].items():
                if isinstance(p, dict) and "with legal" in str(p.get("status", "")):
                    out.append({"file": f"rules/{file}.json", "parameter": name, "value": p["value"],
                                "status": p["status"], "note": p["note"]})
        return out


def load(directory: Path | str | None = None) -> Rules:
    d = Path(directory) if directory else RULES_DIR
    data = {}
    for name in FILES:
        obj = jsonio.load(d / name)
        if obj.get("file") != name:
            raise RuleError(f"{name}: 'file' must be {name!r}")
        data[name[:-5]] = obj
    rules = Rules(directory=str(d), **data)
    _validate(rules)
    return rules


def _validate(rules: Rules) -> None:
    seen: set[str] = set()
    for group in rule_groups(rules):
        if not group:
            raise RuleError("an empty rule list has no default")
        for r in group:
            for key in ("id", "rationale"):
                if not r.get(key):
                    raise RuleError(f"rule without {key}: {r}")
            if r["id"] in seen:
                raise RuleError(f"duplicate rule id {r['id']}")
            seen.add(r["id"])


def rule_groups(rules: Rules) -> list[list[dict]]:
    return [rules.extract["doc_kinds"], rules.extract["field_rules"], rules.extract["holders_evidence"]["rules"],
            rules.figure_nature["rules"],
            rules.discrepancy["rules"], rules.discrepancy["outgoing_scan"]["rules"], rules.ownership["rules"]]


def first_match(group: Iterable[dict], predicate: Callable[[dict], bool]) -> dict | None:
    for r in group:
        if predicate(r):
            return r
    return None


def self_test(rules: Rules) -> list[str]:
    """Run the inline tests of every rule. Returns the list of failures (empty when all pass)."""
    from . import s1_extract, s3_discrepancy, s4_ownership, s7_audit

    failures: list[str] = []
    counted = 0
    for run in (s1_extract.run_inline_tests, s3_discrepancy.run_inline_tests, s4_ownership.run_inline_tests,
                s7_audit.run_scan_tests):
        n, bad = run(rules)
        counted += n
        failures.extend(bad)
    untested = [r["id"] for g in rule_groups(rules) for r in g if not r.get("tests")]
    failures.extend(f"{rid}: rule has no inline test" for rid in untested)
    if counted == 0:
        failures.append("no inline test was run")
    return failures
