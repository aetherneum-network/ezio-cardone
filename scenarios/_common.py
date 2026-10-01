"""Shared helpers of scenarios S01-S10 (synthetic, offline, deterministic).

A check reads ``input/`` and ``expected/`` of its scenario, runs the pipeline into a fresh temporary
folder, and returns ``(ok, one line, details)``. Nothing is read from the environment: ``as_of`` and
the salt of the shareable layer live in ``input/.../config.json``.
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dossier import run as runner  # noqa: E402
from dossier.lib import jsonio  # noqa: E402

HERE = Path(__file__).resolve().parent


def scenario_dir(sid: str) -> Path:
    return HERE / sid


def expected(sid: str) -> dict:
    return jsonio.load(HERE / sid / "expected" / "expected.json")


def workdir(sid: str) -> Path:
    """A fresh temporary folder for the outputs of one check. Since v2.0.10 (D39) it carries the extended-length prefix,
    as the pipeline's work folder does, so that every check reads a build under a deep TEMP whole: a plain path there
    made 'no DOCX written' and 'not published' true by not reading (scenario S02)."""
    return Path(jsonio.ext(tempfile.mkdtemp(prefix=f"ezio-{sid}-")))


def run(input_dir: Path, work: Path, as_of: str | None = None, **kw) -> tuple[int, str, dict]:
    """Run the pipeline; returns (exit code, what it printed, the run report)."""
    buf = io.StringIO()
    code, report = runner.run(input_dir, work, as_of, out=buf, **kw)
    return code, buf.getvalue(), report


def view(work: Path, eid: str) -> dict:
    return jsonio.load(work / "views" / f"{eid}.json")


def provenance(work: Path, eid: str) -> dict:
    return jsonio.load(work / "dossiers" / eid / "provenance.json")


def fields(work: Path, eid: str) -> dict:
    """field -> compact status as the view has it: status, value or values, first source."""
    out = {}
    for fld, res in view(work, eid)["fields"].items():
        item = {"status": res["status"]}
        if res["status"] == "STATED":
            item["value"] = res["value"]
            item["source"] = [res["sources"][0][k] for k in ("source_doc", "source_date", "edition")]
            item["sources"] = sorted([s[k] for k in ("source_doc", "source_date", "edition")] for s in res["sources"])
        elif res["status"] == "DISCREPANCY":
            item["values"] = [{"value": c["value"],
                               "sources": [[s[k] for k in ("source_doc", "source_date", "edition")]
                                           for s in c["sources"]]} for c in res["candidates"]]
        else:
            item["readable"] = sorted(c["value"] for c in res.get("readable", []) if isinstance(c["value"], str))
        out[fld] = item
    return out


def match_fields(problems: list[str], got: dict, want: dict, where: str = "") -> None:
    """Compare only the keys the expected file gives for each field."""
    for fld, exp in want.items():
        g = got.get(fld)
        if g is None:
            problems.append(f"{where}{fld}: not in the view")
            continue
        for key, val in exp.items():
            have = g.get(key)
            if key == "values" and have is not None:
                have = sorted(have, key=lambda c: json.dumps(c["value"], sort_keys=True))
            expect(problems, f"{where}{fld}.{key}", have, val)


def docx_rows(path: Path, column: str) -> list[dict]:
    """Rows (as header -> cell) of every table of the DOCX that has the given column."""
    out = []
    for header, rows in docx_tables(path).items():
        cols = header.split("|")
        if column in cols:
            out.extend(dict(zip(cols, r)) for r in rows)
    return out


def docx_tables(path: Path) -> dict[str, list[list[str]]]:
    from dossier.s7_audit import read_docx
    return read_docx(path)["tables"]


def docx_text(path: Path) -> str:
    """Every XML part of a DOCX, concatenated: what a recipient could find by searching the file."""
    with zipfile.ZipFile(path) as z:
        return "\n".join(z.read(n).decode("utf-8", "replace") for n in sorted(z.namelist()) if n.endswith(".xml"))


def published(work: Path, eid: str) -> bool:
    return (work / "dossiers" / eid / "dossier.docx").exists()


def rules_copy(dst: Path, change) -> Path:
    """A copy of rules/ in ``dst`` after ``change(rules: dict[file name -> object])`` edited it."""
    src = ROOT / "rules"
    data = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted(src.glob("*.json"))}
    change(data)
    for name, obj in data.items():
        jsonio.write_text(dst / name, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    return dst


def report(sid: str, problems: list[str], summary: str, details: dict | None = None) -> tuple[bool, str, dict]:
    ok = not problems
    line = f"{sid} {'PASS' if ok else 'FAIL'} - {summary if ok else '; '.join(problems[:3])}"
    return ok, line, {"scenario": sid, "pass": ok, "summary": summary, "problems": problems,
                      "details": details or {}}


def expect(problems: list[str], what: str, got, want) -> None:
    if got != want:
        problems.append(f"{what}: got {got!r}, expected {want!r}")


def main(check) -> None:
    ok, line, _ = check()
    print(line)
    sys.exit(0 if ok else 1)
