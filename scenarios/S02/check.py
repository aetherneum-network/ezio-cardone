"""S02 - three holders at 33,33% do not make the whole: the build is BLOCKED and nothing is published."""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402

SID = "S02"


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    problems: list[str] = []

    # negative: 33,33% x 3 = 9999/10000
    want = exp["percent"]
    work = c.workdir(SID)
    code, out, report = c.run(c.scenario_dir(SID) / "input" / "percent", work)
    c.expect(problems, "percent: exit code", code, want["exit_code"])
    c.expect(problems, "percent: status", report["entities"][eid]["status"], want["status"])
    c.expect(problems, "percent: last line", out.strip().split("\n")[-1], want["last_line"])
    if want["sum"] not in report["entities"][eid].get("reason", ""):
        problems.append(f"percent: the reason does not give the exact sum {want['sum']}")
    written = sorted(p.relative_to(work).as_posix() for p in work.rglob("*")
                     if p.is_file() and p.suffix == ".docx")
    c.expect(problems, "percent: DOCX files written", written, [])
    c.expect(problems, "percent: dossier published", c.published(work, eid), want["published"])
    c.expect(problems, "percent: snapshot recorded", (work / "snapshots" / "index.jsonl").exists(), False)
    c.expect(problems, "percent: 'RUN OK' printed", "RUN OK" in out, False)

    # the same table written exactly builds
    want = exp["exact"]
    work2 = c.workdir(SID)
    code, out, report = c.run(c.scenario_dir(SID) / "input" / "exact", work2)
    c.expect(problems, "exact: exit code", code, want["exit_code"])
    c.expect(problems, "exact: status", report["entities"][eid]["status"], want["status"])
    c.expect(problems, "exact: dossier published", c.published(work2, eid), want["published"])
    total = None
    if c.published(work2, eid):
        table = sorted(({"holder": f["holder"], "share": f["value"]}
                        for f in c.provenance(work2, eid)["figures"] if f["section"] == "cap_table"),
                       key=lambda r: r["holder"])
        c.expect(problems, "exact: cap table", table, want["cap_table"])
        total = sum((Fraction(r["share"]) for r in table), Fraction(0))
        c.expect(problems, "exact: sum", f"{total.numerator}/{total.denominator}", want["sum"])
    return c.report(SID, problems, "33,33% x 3 = 9999/10000: BLOCKED with exit 2, no dossier written; "
                                   "1/3 x 3 builds and sums to exactly 1/1")


if __name__ == "__main__":
    c.main(check)
