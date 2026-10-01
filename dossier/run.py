"""One chained run: documents -> record -> resolution -> ownership -> snapshot -> dossier -> audit -> shareable.

    python -m dossier.run --input corpus/out --work build/work --as-of 2026-09-30

Exit codes: ``0`` every dossier published; ``2`` BLOCKED (at least one cap table does not sum to the
whole, or a holders' table that could not be read leaves the sum unverified: that dossier is not
published); ``3`` FAILED (a figure without a source, an invalid record, an
unmarked source document, an audit problem, a failed write). ``RUN OK`` is printed only on exit 0.

``as_of`` is never implicit: ``--as-of``, else ``as_of`` in ``<input>/config.json``; never the clock.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys
from pathlib import Path

from . import __version__, rules_engine, s1_extract, s2_record, s3_discrepancy, s4_ownership, s5_snapshot
from . import s6_build, s7_audit, s8_shareable
from .lib import jsonio

OK, BLOCKED, FAILED = "OK", "BLOCKED", "FAILED"
EXIT = {OK: 0, BLOCKED: 2, FAILED: 3}


class RunError(RuntimeError):
    """The run cannot start (bad arguments, missing as_of, broken rules)."""


def make_view(eid: str, records: dict, resolutions: dict, ownership: dict) -> dict:
    record, res, own = records[eid], resolutions[eid], ownership[eid]
    upstream = {}
    for edge in own["chain"]:
        if edge["held"] != eid:
            meta = next(d for d in records[edge["held"]]["documents"] if d["doc_id"] == edge["source_doc"])
            upstream[meta["doc_id"]] = meta
    return {"entity": record["entity"], "fields": res["fields"], "previous_statements": res["previous_statements"],
            "ownership": own, "documents": record["documents"], "upstream_documents": upstream,
            "superseded": s3_discrepancy.superseded_register(res),
            "warnings": {"filename_divergences": record["filename_divergences"],
                         "unclassified_documents": record["unclassified_documents"],
                         "classified_checks": record["classified_checks"],
                         "ignored_after_as_of": record["ignored_after_as_of"]}}


def _replace_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(jsonio.ext(dst))
    os.makedirs(jsonio.ext(dst.parent), exist_ok=True)
    os.replace(jsonio.ext(src), jsonio.ext(dst))


def run(input_dir: Path | str | None, work_dir: Path | str, as_of: str | None = None, *,
        rules_dir: Path | str | None = None, entities: list[str] | None = None,
        records_dir: Path | str | None = None, store_dir: Path | str | None = None,
        salt: str | None = None, out=sys.stdout) -> tuple[int, dict]:
    work = Path(work_dir)
    inp = Path(input_dir) if input_dir else None
    config = {}
    if inp and (inp / "config.json").exists():
        config = jsonio.load(inp / "config.json")
    as_of = as_of or config.get("as_of")
    if not as_of:
        raise RunError("as_of is required (--as-of or as_of in <input>/config.json); the clock is never used")
    _dt.date.fromisoformat(as_of)
    salt = salt or config.get("shareable_salt")
    rules = rules_engine.load(rules_dir)
    failures = rules_engine.self_test(rules)
    if failures:
        raise RunError("rule inline tests failed: " + "; ".join(failures[:5]))
    identity = {}
    if inp and (inp / "identity" / "persons.json").exists():
        identity = jsonio.load(inp / "identity" / "persons.json")

    status: dict[str, dict] = {}
    records: dict[str, dict] = {}

    def fail(eid: str, why: str) -> None:
        status[eid] = {"status": FAILED, "reason": why}

    if records_dir:
        for path in sorted(Path(records_dir).glob("E-*.json")):
            try:
                records[path.stem] = s2_record.load_record(path)
            except (s2_record.RecordInvalid, jsonio.FloatRefused, json.JSONDecodeError) as exc:
                fail(path.stem, str(exc))
    else:
        if inp is None:
            raise RunError("--input or --records is required")
        for eid, raw in sorted(s1_extract.extract_corpus(inp, rules, as_of).items()):
            try:
                records[eid] = s2_record.build_record(raw, as_of)
            except s2_record.RecordInvalid as exc:
                rejected = "; ".join(f"{d['file'].rsplit('/', 1)[-1]}: {d['reason']}"
                                     for d in raw["rejected_documents"])
                fail(eid, f"{rejected}; {exc}" if rejected else str(exc))
    if not records and not status:
        raise RunError("nothing to build: no source document and no entity record was found")
    for eid, record in records.items():
        jsonio.write(work / "records" / f"{eid}.json", record)
        if record["rejected_documents"]:
            fail(eid, "; ".join(f"{d['file'].rsplit('/', 1)[-1]}: {d['reason']}" for d in record["rejected_documents"]))

    # an entity that FAILED is not looked through by the others: for them it is outside the dossier set
    records = {eid: r for eid, r in records.items() if eid not in status}
    resolutions = {eid: s3_discrepancy.resolve_record(records[eid], rules) for eid in records}
    ownership = s4_ownership.analyse_all(records, resolutions, rules)
    store = s5_snapshot.SnapshotStore(Path(store_dir) if store_dir else work / "snapshots")
    assumptions = rules.legal_assumptions()
    targets = sorted(entities) if entities else sorted(set(records) | set(status))
    staging_root = work / "_staging"

    for eid in targets:
        if eid in status:
            continue
        if eid not in records:
            fail(eid, "no document of this entity in the input")
            continue
        view = make_view(eid, records, resolutions, ownership)
        jsonio.write(work / "views" / f"{eid}.json", view)
        if view["ownership"]["outcome"] == "BLOCKED":
            status[eid] = {"status": BLOCKED, "reason": view["ownership"]["reason"]}
            continue
        staging = staging_root / eid
        if staging.exists():
            shutil.rmtree(jsonio.ext(staging))
        try:
            built = s6_build.build(view, staging / "dossier", as_of, assumptions, identity=identity)
            audit = s7_audit.audit_dossier(staging / "dossier", inp, records[eid], rules=rules) if inp else {
                "ok": False, "problems": ["no input folder: the sources cannot be re-read"], "figures_total": 0,
                "figures_with_source": 0, "derived_total": 0, "to_confirm_total": 0}
            jsonio.write(staging / "dossier" / "audit.json", audit)
            if not audit["ok"]:
                _replace_dir(staging, work / "_rejected" / eid)
                fail(eid, "audit: " + "; ".join(audit["problems"][:3]))
                continue
            share = {"status": "SKIPPED", "reason": "no salt given"}
            if salt:
                sb = s8_shareable.build_shareable(view, staging / "shareable", as_of, assumptions, salt)
                found = s8_shareable.leaks(staging / "shareable", identity)
                if found:
                    _replace_dir(staging, work / "_rejected" / eid)
                    fail(eid, f"shareable layer leaks {len(found)} identity string(s)")
                    continue
                share = {"status": OK, "docx_sha256": sb["docx_sha256"]}
            entry, created = store.append(eid, as_of, view)
            _replace_dir(staging / "dossier", work / "dossiers" / eid)
            if salt:
                _replace_dir(staging / "shareable", work / "shareable" / eid)
            status[eid] = {"status": OK, "docx_sha256": built["docx_sha256"],
                           "provenance_sha256": built["provenance_sha256"],
                           "figures": audit["figures_total"], "figures_with_source": audit["figures_with_source"],
                           "to_confirm": audit["to_confirm_total"], "shareable": share,
                           "snapshot": {"file": entry["file"], "sha256": entry["sha256"], "created": created}}
        except s6_build.BuildBlocked as exc:
            status[eid] = {"status": BLOCKED, "reason": str(exc)}
        except (s6_build.BuildRefused, s5_snapshot.SnapshotError, jsonio.WriteFailed, OSError, ValueError) as exc:
            fail(eid, f"{type(exc).__name__}: {exc}")
    if staging_root.exists():
        shutil.rmtree(jsonio.ext(staging_root))

    counts = {s: sum(1 for v in status.values() if v["status"] == s) for s in (OK, BLOCKED, FAILED)}
    overall = FAILED if counts[FAILED] else BLOCKED if counts[BLOCKED] else OK
    problems = store.verify()
    if problems:
        overall = FAILED
    report = {"generator": f"dossier {__version__}", "as_of": as_of, "status": overall, "counts": counts,
              "rules_version": {f[:-5]: getattr(rules, f[:-5])["version"] for f in rules_engine.FILES},
              "snapshot_store_problems": problems, "entities": {e: status[e] for e in sorted(status)}}
    jsonio.write(work / "run_report.json", report)
    for eid in sorted(status):
        s = status[eid]
        if s["status"] != OK:
            print(f"{eid} {s['status']} - {s['reason']}", file=out)
    print(f"dossiers: {counts[OK]} published, {counts[BLOCKED]} BLOCKED, {counts[FAILED]} FAILED (as of {as_of})",
          file=out)
    print("RUN OK" if overall == OK else f"RUN {overall} - not everything was published", file=out)
    return EXIT[overall], report


def diff_runs(before: Path | str, after: Path | str) -> list[dict]:
    """What moved between two work folders: one line per (entity, field) whose status or value changed."""
    out = []
    a_dir, b_dir = Path(before) / "views", Path(after) / "views"
    for eid in sorted({p.stem for p in a_dir.glob("E-*.json")} | {p.stem for p in b_dir.glob("E-*.json")}):
        a = jsonio.load(a_dir / f"{eid}.json")["fields"] if (a_dir / f"{eid}.json").exists() else {}
        b = jsonio.load(b_dir / f"{eid}.json")["fields"] if (b_dir / f"{eid}.json").exists() else {}
        for fld in sorted(set(a) | set(b)):
            x, y = _shape(a.get(fld)), _shape(b.get(fld))
            if x != y:
                out.append({"entity": eid, "field": fld, "before": x, "after": y})
    return out


def _shape(res: dict | None) -> dict | None:
    if res is None:
        return None
    out = {"status": res["status"]}
    if res["status"] == "STATED":
        out["value"] = res["value"]
        out["source_doc"] = res["sources"][0]["source_doc"]
    elif res["status"] == "DISCREPANCY":
        out["values"] = [c["value"] for c in res["candidates"]]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="dossier.run", description=__doc__.split("\n\n")[0])
    ap.add_argument("--input", help="folder with entities/<id>/*.txt, optional identity/ and config.json")
    ap.add_argument("--records", help="start from entity records (JSON) instead of extracting")
    ap.add_argument("--work", required=True, help="output folder (build artefacts)")
    ap.add_argument("--as-of", dest="as_of", help="YYYY-MM-DD; never taken from the clock")
    ap.add_argument("--rules", help="folder with the four rule files (default: rules/)")
    ap.add_argument("--store", help="snapshot store (default: <work>/snapshots)")
    ap.add_argument("--entity", action="append", help="build only this entity (repeatable)")
    ap.add_argument("--salt", help="salt of the opaque identifiers of the shareable layer")
    a = ap.parse_args(argv)
    try:
        code, _ = run(a.input, a.work, a.as_of, rules_dir=a.rules, entities=a.entity, records_dir=a.records,
                      store_dir=a.store, salt=a.salt)
    except (RunError, rules_engine.RuleError, ValueError) as exc:
        print(f"RUN FAILED - {exc}")
        return EXIT[FAILED]
    return code


if __name__ == "__main__":
    sys.exit(main())
