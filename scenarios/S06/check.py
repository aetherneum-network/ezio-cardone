"""S06 - the file is named "appointment of P-005", the text appoints P-006: the content wins, the name is flagged."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402

SID = "S06"


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    work = c.workdir(SID)
    code, _, _ = c.run(c.scenario_dir(SID) / "input", work)
    problems: list[str] = []
    c.expect(problems, "exit code", code, exp["exit_code"])
    c.match_fields(problems, c.fields(work, eid), {"directors": exp["directors"]})

    view = c.view(work, eid)
    got = [{k: d[k] for k in ("doc_id", "aspect", "filename_says", "content_says")}
           for d in view["warnings"]["filename_divergences"]]
    c.expect(problems, "file name divergences", got, exp["filename_divergences"])

    wrong = exp["never_a_director"]
    prov = c.provenance(work, eid)
    as_director = [f["id"] for f in prov["figures"]
                   if f["field"] == "directors" and f["section"] == "facts" and wrong in f["value"]]
    c.expect(problems, f"{wrong} shown as a director in office", as_director, [])
    docx = work / "dossiers" / eid / "dossier.docx"
    shown = [r["Value"] for r in c.docx_rows(docx, "Field") if r["Field"] == "directors"]
    c.expect(problems, "directors in the DOCX", shown, [", ".join(exp["directors"]["value"])])
    from dossier.s7_audit import read_docx
    notes = [p for p in read_docx(docx)["paragraphs"] if "DOC-E0003-02" in p and wrong in p]
    if not notes:
        problems.append("the DOCX does not report the divergence between file name and content")
    return c.report(SID, problems, "director in office P-006 from the text (APPOINTMENT/1); the file name "
                                   "saying P-005 is reported as a divergence and never used as a source")


if __name__ == "__main__":
    c.main(check)
