"""Shared fixtures of the test suite: small corpora built once per process, child processes offline."""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from . import ROOT

import make_inputs as mk  # noqa: E402  (scenarios/make_inputs.py: builders of synthetic documents)
from corpus import generate  # noqa: E402
from dossier import rules_engine, run as runner  # noqa: E402
from dossier.lib import jsonio  # noqa: E402

DEV_SEED = generate.SUITES["dev"]["seed"]
AS_OF = "2026-09-30"


def tmp(prefix: str = "ezio-test-") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


def write_tree(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        jsonio.write_text(root / rel, text)
    return root


def run(input_dir, work, as_of=None, **kw) -> tuple[int, str, dict]:
    buf = io.StringIO()
    code, report = runner.run(input_dir, work, as_of, out=buf, **kw)
    return code, buf.getvalue(), report


@lru_cache(maxsize=None)
def rules():
    return rules_engine.load()


@lru_cache(maxsize=None)
def rules_report_unverified() -> Path:
    """A copy of the rule files with unverified_holders_table 'report' (the v2.0.0 behaviour): it lets a test
    look at the field-level abstention that the default 'block' keeps behind a blocked build."""
    dst = tmp("ezio-rules-") / "rules"
    shutil.copytree(ROOT / "rules", dst)
    path = dst / "ownership.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["parameters"]["unverified_holders_table"]["value"] = "report"
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return dst


@lru_cache(maxsize=None)
def rules_narrow_scope() -> Path:
    """A copy of the rule files with unread_document_scope 'fields_it_may_state' (the default of v2.0.3 only, OFF
    since v2.0.4): it lets a test show what that option does, and the risk that keeps it off."""
    dst = tmp("ezio-rules-") / "rules"
    shutil.copytree(ROOT / "rules", dst)
    path = dst / "discrepancy.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["parameters"]["unread_document_scope"]["value"] = "fields_it_may_state"
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return dst


@lru_cache(maxsize=None)
def corpus(entities: int = 24, seed: int = DEV_SEED, perturb: bool = False) -> Path:
    """A generated corpus on disk: <base>/input and <base>/gold.json. Only dev seeds are ever inspected."""
    base = tmp("ezio-corpus-")
    generate.write(generate.build_files(seed, entities=entities, perturb=perturb), base)
    return base


@lru_cache(maxsize=None)
def built(entities: int = 24, seed: int = DEV_SEED, perturb: bool = False) -> tuple[Path, Path, int]:
    """(corpus base, work folder, exit code) of one run of the pipeline on a generated corpus."""
    base = corpus(entities, seed, perturb)
    work = tmp("ezio-work-")
    code, _, _ = run(base / "input", work)
    return base, work, code


@lru_cache(maxsize=None)
def scenario_run(sid: str, sub: str = "") -> tuple[Path, Path, int, str]:
    """(input root, work folder, exit code, printed text) of one run on a scenario input."""
    inp = ROOT / "scenarios" / sid / "input"
    if sub:
        inp = inp / sub
    work = tmp(f"ezio-{sid}-")
    code, out, _ = run(inp, work)
    return inp, work, code, out


def tiny(docs: list[tuple[str, str]], as_of: str = "2026-06-30", persons=("P-001", "P-002", "P-003")) -> Path:
    """An input root with the given source documents (built with the helpers of scenarios/make_inputs.py)."""
    return write_tree(tmp("ezio-input-"), mk.root("T00", as_of, list(persons), docs))


def offline_env() -> dict[str, str]:
    """The environment of a child process: what the council executor passes, plus the socket block."""
    keep = ("PATH", "SYSTEMROOT", "SystemRoot", "TEMP", "TMP", "TMPDIR", "HOME", "USERPROFILE", "LANG")
    env = {k: v for k, v in os.environ.items() if k in keep}
    env["PYTHONPATH"] = str(ROOT / "tests" / "_offline")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def child(args: list[str], cwd: Path = ROOT, timeout: int = 600, **env_extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=str(cwd), env={**offline_env(), **env_extra},
                          capture_output=True, text=True, encoding="utf-8", timeout=timeout)


def nodes_of(tables: dict, whole: Fraction = Fraction(1)) -> dict[str, dict]:
    """Ownership nodes from plain holders' tables ``{entity: [(holder, Fraction), ...] | None}``."""
    nodes = {}
    for eid, table in tables.items():
        node = {"status": "TO_CONFIRM", "why": "unreadable", "table": [], "source": None, "checks": [],
                "violations": [], "unverified": []}
        if table is not None:
            total = sum((sh for _, sh in table), Fraction(0))
            src = {"source_doc": f"DOC-{eid}", "source_date": "2026-01-01", "edition": "T/1"}
            check = dict(src, sum=f"{total.numerator}/{total.denominator}", whole=total == whole)
            node.update(status="STATED", why="", table=list(table), checks=[check], source=src)
            if not check["whole"]:
                node.update(status="BLOCKED", table=[], violations=[check], why="sum")
        nodes[eid] = node
    return nodes


def tree_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): jsonio.sha256_file(p) for p in sorted(root.rglob("*")) if p.is_file()}
