"""S10 - resolved, subscribed and paid-in in one clause: each amount keeps its nature, or is [TO CONFIRM]."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402

SID = "S10"
NATURES = ("resolved", "subscribed", "paid_in")


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    problems: list[str] = []

    # the clause gives a nature to each of its four amounts
    want = exp["clear"]
    work = c.workdir(SID)
    code, _, _ = c.run(c.scenario_dir(SID) / "input" / "clear", work)
    c.expect(problems, "clear: exit code", code, want["exit_code"])
    c.match_fields(problems, c.fields(work, eid), want["fields"], "clear: ")
    record = __import__("json").loads((work / "records" / f"{eid}.json").read_text(encoding="utf-8"))
    natures = {a["value"]: a["nature"] for a in record["assertions"]
               if a["source_doc"] == "DOC-E0003-02" and a["status"] == "STATED"}
    c.expect(problems, "clear: nature of each amount of the clause", natures, want["natures_of_the_clause"])
    docx = work / "dossiers" / eid / "dossier.docx"
    shown = {r["Field"]: (r["Value"], r["Nature"]) for r in c.docx_rows(docx, "Field")
             if r["Field"].startswith("share_capital.")}
    c.expect(problems, "clear: capital rows of the DOCX", shown,
             {"share_capital.resolved": ("EUR 500.000,00", "resolved"),
              "share_capital.subscribed": ("EUR 400.000,00", "subscribed"),
              "share_capital.paid_in": ("EUR 250.000,00", "paid_in")})

    # a later extract lists the same three amounts without saying what two of them are
    want = exp["insufficient"]
    work2 = c.workdir(SID)
    code, _, _ = c.run(c.scenario_dir(SID) / "input" / "insufficient", work2)
    c.expect(problems, "insufficient: exit code", code, want["exit_code"])
    got = c.fields(work2, eid)
    c.match_fields(problems, got, want["fields"], "insufficient: ")
    for fld, readable in want["readable_not_fact"].items():
        c.expect(problems, f"insufficient: readable statements of {fld}", got[fld].get("readable"), readable)
    prov = c.provenance(work2, eid)
    as_fact = sorted(f["field"] for f in prov["figures"]
                     if f["section"] == "facts" and f["field"] in want["readable_not_fact"])
    c.expect(problems, "insufficient: fields to confirm shown as fact", as_fact, [])
    docx2 = work2 / "dossiers" / eid / "dossier.docx"
    marks = {r["Field to confirm"]: r["Value"] for r in c.docx_rows(docx2, "Why")}
    c.expect(problems, "insufficient: [TO CONFIRM] rows of the DOCX", marks,
             {f: "[TO CONFIRM]" for f in want["readable_not_fact"]})
    fact_rows = [r["Field"] for r in c.docx_rows(docx2, "Field") if r["Field"] in want["readable_not_fact"]]
    c.expect(problems, "insufficient: fields to confirm among the DOCX facts", fact_rows, [])
    return c.report(SID, problems, "one clause, four amounts: historical 300000.00, resolved 500000.00, "
                                   "subscribed 400000.00, paid-in 250000.00; when a later extract does not say "
                                   "what two amounts are, subscribed and paid-in are [TO CONFIRM]")


if __name__ == "__main__":
    c.main(check)
