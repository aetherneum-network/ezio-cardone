"""S03 - a figure without its source never reaches a dossier: the run FAILS and publishes nothing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402
from dossier.lib import jsonio  # noqa: E402

SID = "S03"


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    inp = c.scenario_dir(SID) / "input"
    problems: list[str] = []

    # valid run: every figure carries source document, source date and edition
    want = exp["valid"]
    work = c.workdir(SID)
    code, _, _ = c.run(inp, work)
    c.expect(problems, "valid: exit code", code, want["exit_code"])
    figures = c.provenance(work, eid)["figures"]
    unsourced = [f["id"] for f in figures
                 if not all(f.get(k) for k in ("source_doc", "source_date", "edition"))]
    c.expect(problems, "valid: figures without source, date or edition", unsourced, [])
    if len(figures) < want["minimum_figures"]:
        problems.append(f"valid: only {len(figures)} figures, expected at least {want['minimum_figures']}")
    c.match_fields(problems, c.fields(work, eid), want["fields"], "valid: ")
    docx = work / "dossiers" / eid / "dossier.docx"
    blank = [r for col in ("Field", "Field in discrepancy", "Share (exact)", "Historical value")
             for r in c.docx_rows(docx, col)
             if r.get("Fig.") and not all(r[k] for k in ("Source document", "Source date", "Edition"))]
    c.expect(problems, "valid: DOCX figure rows without a source", len(blank), 0)

    # negative: the same record with one figure stripped of its source, or with a value its source does not say
    want = exp["every_tamper"]
    record = jsonio.load(work / "records" / f"{eid}.json")
    outcomes = {}
    for t in jsonio.load(inp / "tamper.json")["tampers"]:
        rec = jsonio.loads(jsonio.dumps(record))
        hits = [a for a in rec["assertions"] if a["field"] == t["field"] and a["source_doc"] == t["doc"]]
        if len(hits) != 1:
            problems.append(f"{t['name']}: the figure to tamper was not found once")
            continue
        if t["op"] == "drop":
            del hits[0][t["key"]]
        else:
            hits[0][t["key"]] = t["to"]
        bad = c.workdir(SID)
        jsonio.write(bad / "records_in" / f"{eid}.json", rec)
        code, out, report = c.run(inp, bad / "work", records_dir=bad / "records_in")
        status = report["entities"].get(eid, {}).get("status")
        outcomes[t["name"]] = {"exit_code": code, "status": status,
                               "reason": report["entities"].get(eid, {}).get("reason", "")[:200]}
        c.expect(problems, f"{t['name']}: exit code", code, want["exit_code"])
        c.expect(problems, f"{t['name']}: status", status, want["status"])
        if t["reason_contains"] not in outcomes[t["name"]]["reason"]:
            problems.append(f"{t['name']}: failed for another reason: {outcomes[t['name']]['reason']}")
        c.expect(problems, f"{t['name']}: dossier published", c.published(bad / "work", eid), want["published"])
        c.expect(problems, f"{t['name']}: 'RUN OK' printed", "RUN OK" in out, False)
    return c.report(SID, problems, f"{len(figures)}/{len(figures)} figures of the valid run carry source, date "
                                   f"and edition; {len(outcomes)}/{len(outcomes)} tampered records FAILED "
                                   f"with exit 3 and published nothing", {"tampers": outcomes})


if __name__ == "__main__":
    c.main(check)
