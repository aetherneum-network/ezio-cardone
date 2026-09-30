"""S01 - the deed and the registry extract disagree on the share capital: both are shown, none is chosen."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402

SID = "S01"


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    work = c.workdir(SID)
    code, _, _ = c.run(c.scenario_dir(SID) / "input", work)
    problems: list[str] = []
    c.expect(problems, "exit code", code, exp["exit_code"])
    c.match_fields(problems, c.fields(work, eid), exp["fields"])

    never = set(exp["fields_never_shown_as_fact"])
    prov = c.provenance(work, eid)
    as_fact = sorted({f["field"] for f in prov["figures"] if f["section"] == "facts" and f["field"] in never})
    c.expect(problems, "fields in discrepancy shown as fact (provenance)", as_fact, [])

    docx = work / "dossiers" / eid / "dossier.docx"
    fact_rows = sorted({r["Field"] for r in c.docx_rows(docx, "Field") if r["Field"] in never})
    c.expect(problems, "fields in discrepancy shown as fact (DOCX)", fact_rows, [])
    rows = [[r["Field in discrepancy"], r["Value"], r["Source document"], r["Source date"], r["Edition"]]
            for r in c.docx_rows(docx, "Field in discrepancy")]
    for want in exp["docx_discrepancy_rows"]:
        if want not in rows:
            problems.append(f"DOCX discrepancy table lacks the row {want}")
    return c.report(SID, problems, "capital 50000.00 (deed) and 80000.00 (extract) shown side by side with "
                                   "their sources; no capital figure among the facts",
                    {"discrepancy_rows_in_docx": len(rows)})


if __name__ == "__main__":
    c.main(check)
