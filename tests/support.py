"""Shared fixtures of the test suite: small corpora built once per process, child processes offline."""
from __future__ import annotations

import atexit
import concurrent.futures
import datetime
import io
import json
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
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


_CREATED: list[str] = []


def _remove_created() -> None:
    """v2.0.10 (D39 d): remove, when the process ends, every folder that tmp() created in it, and nothing else. Until
    v2.0.9 none was removed (39,109 entries piled up in one scratch TEMP). The fixtures built once per process (corpus,
    built, scenario_run) are shared by many tests, so the folders go at the end of the process, not of each test. A
    folder that cannot be removed is said on stderr; it never changes a test's outcome."""
    left = []
    for path in reversed(_CREATED):
        shutil.rmtree(jsonio.ext(path), ignore_errors=True)
        if os.path.exists(jsonio.ext(path)):
            left.append(path)
    if left:
        print(f"tests/support.py: {len(left)} temporary folder(s) of this process not removed, e.g. {left[0]}",
              file=sys.stderr)


atexit.register(_remove_created)


def tmp(prefix: str = "ezio-test-") -> Path:
    """A new temporary folder (under tempfile's folder, so a test may move it), removed when the process ends."""
    path = tempfile.mkdtemp(prefix=prefix)
    _CREATED.append(path)
    return Path(path)


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


_DEED_DATE = re.compile(r"^Document date: (\d{4}-\d{2}-\d{2})$", re.M)
_DEED_OFFICE = re.compile(r"^\d+\. Registered office\. The registered office is at (.+)\.$", re.M)


def office_witness(docs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """The documents, plus one registry extract per deed of incorporation, dated the day before that deed, that states
    the deed's registered office alike (and the builder's plain values for the other fields).

    Since v2.0.8 (D37, rules/extract.json address_corroboration) an address that one document alone states is not
    corroborated: words added to it cannot be told from the address, so every field of that document stays
    [TO CONFIRM] (ADR-999, DISC-006) and its office too (DISC-038). The tests of how a deed's forms are read are
    about those forms, so they add this witness: it corroborates the deed's office (the same tokens, another
    document; no date condition binds a mention that is not the new address of an office transfer) and, older than
    the deed, it is a current source of no field (its values are a past edition, superseded by the deed). A deed
    whose office clause is not the builder's own gets no witness."""
    out = list(docs)
    for rel, text in docs:
        if "Document type: Deed of incorporation" not in text:
            continue
        date, office = _DEED_DATE.search(text), _DEED_OFFICE.search(text)
        if not (date and office):
            continue
        eid = "E-" + re.search(r"TEST-REG-(\d+)", text).group(1)[-4:]      # the content's entity, never the folder
        day = (datetime.date.fromisoformat(date.group(1)) - datetime.timedelta(days=1)).isoformat()
        out.append(mk.extract(eid, 0, day, 1, office.group(1),
                              "Share capital: resolved EUR 50.000,00; subscribed and paid in EUR 50.000,00",
                              [("P-001", "60%"), ("P-002", "40%")], ["P-001"]))
    return out


def offline_env() -> dict[str, str]:
    """The environment of a child process: what the council executor passes, plus the socket block."""
    keep = ("PATH", "SYSTEMROOT", "SystemRoot", "TEMP", "TMP", "TMPDIR", "HOME", "USERPROFILE", "LANG")
    env = {k: v for k, v in os.environ.items() if k in keep}
    env["PYTHONPATH"] = str(ROOT / "tests" / "_offline")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def child(args: list[str], cwd: Path = ROOT, timeout: int = 600, **env_extra: str) -> subprocess.CompletedProcess:
    # v2.0.10 (D39 d): a child process gets a TEMP of its own, made by tmp(), so that what it leaves there (the work
    # folders of the scenario checks, of a rebuild) is removed with it when this process ends
    own = str(tmp("ezio-child-"))
    env = {**offline_env(), "TEMP": own, "TMP": own, "TMPDIR": own, **env_extra}
    return subprocess.run([sys.executable, *args], cwd=str(cwd), env=env,
                          capture_output=True, text=True, encoding="utf-8", timeout=timeout)


# v2.0.12: the seven sweeps of siblings (one whole pipeline run per constructed case, up to 624 cases per test) took
# 600 of the 791 s of the v2.0.11 suite on Windows 11, every case in one process. Their cases are independent, so they
# run in worker processes and the test reads each outcome inside the case's own subTest, with the same assertions, in
# the same order.
_POOL: concurrent.futures.ProcessPoolExecutor | None = None


def jobs() -> int:
    """Worker processes of a sweep: EZIO_TEST_JOBS when it is set, else the CPU count, at most 8. With 1 every case
    runs in this process when the test reads it, as until v2.0.11."""
    value = os.environ.get("EZIO_TEST_JOBS", "").strip()
    return max(1, int(value)) if value else max(1, min(8, os.cpu_count() or 1))


class _HereWhenRead:
    """The outcome of one case run in this process, at the moment the test reads it (jobs() == 1)."""

    def __init__(self, fn, args):
        self._fn, self._args = fn, args

    def result(self):
        return self._fn(*self._args)


def _submit(fn, cases: list) -> list:
    global _POOL
    if _POOL is None:
        # spawn on every system: a worker starts clean and removes its own tmp() folders when it ends (atexit)
        _POOL = concurrent.futures.ProcessPoolExecutor(jobs(), mp_context=multiprocessing.get_context("spawn"))
        atexit.register(_end_pool)  # before _remove_created (atexit runs last-registered first)
    return [_POOL.submit(fn, *args) for args in cases]


def sweep(fn, cases) -> list:
    """One future per case, in the order given: ``fn(*args)`` for every ``args`` of ``cases``, run in worker processes.
    ``fn`` is a module-level function of a test module (the workers import it by name, and with it the socket block of
    this package). ``future.result()`` returns the outcome, or raises the case's exception, where the test reads it:
    inside that case's subTest, as a call of ``fn`` there would. Since v2.0.14, when ahead() already submitted ``fn``
    with equal cases, those futures are returned (once) instead of new ones."""
    cases = list(cases)
    if jobs() == 1 or len(cases) < 2:
        return [_HereWhenRead(fn, args) for args in cases]
    early = _AHEAD.get((fn.__module__, fn.__qualname__), [])
    for i, (submitted, futures) in enumerate(early):
        if submitted == cases:
            del early[i]
            return futures
    return _submit(fn, cases)


# v2.0.14: with the sweeps in workers, the rest of the suite runs in one process (about 175 s of a run with 4 workers
# on Windows 11: of 322 s on 4 cores, of 399 s on 2 cores of two threads each), and the workers waited for it. A module
# with a sweep now submits its cases when the loader reads the whole module (load_tests, before the first test runs),
# so the workers compute them while this process runs the other tests. The test still builds its cases, calls sweep()
# and reads each outcome inside the case's own subTest, with the same assertions, in the same order; only the moment
# of the computation moves.
_AHEAD: dict[tuple[str, str], list[tuple[list, list]]] = {}


def _ids(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _ids(test)
        else:
            yield test.id()


def ahead(tests, reader: str, fn, cases) -> None:
    """Submit ``fn(*args)`` for every ``args`` of ``cases`` now, when the sweep runs in workers and the loaded ``tests``
    hold the test that reads it (an id that contains ``reader``: a test, or a class whose set-up reads the sweep). The
    reader's own sweep() gets these futures if its cases are equal; if not, it submits its own, as without ahead(), and
    the ones submitted here are said at the end of the process."""
    cases = list(cases)
    if jobs() == 1 or len(cases) < 2 or not any(reader in tid for tid in _ids(tests)):
        return
    _AHEAD.setdefault((fn.__module__, fn.__qualname__), []).append((cases, _submit(fn, cases)))


def _end_pool() -> None:
    """At the end of the process: what ahead() submitted and no test read is said on stderr, and its cases not yet
    started are cancelled instead of computed (a run of some tests of a module, or an interrupted run). It never
    changes a test's outcome."""
    unread = sum(len(early) for early in _AHEAD.values())
    if unread:
        print(f"tests/support.py: {unread} sweep(s) submitted ahead and not read by a test; their cases not yet "
              f"started are cancelled", file=sys.stderr)
    _POOL.shutdown(wait=True, cancel_futures=True)


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
    root = Path(jsonio.ext(root))  # since v2.0.9 (D38): a deep folder is walked without long-path support
    return {p.relative_to(root).as_posix(): jsonio.sha256_file(p) for p in sorted(root.rglob("*")) if p.is_file()}
