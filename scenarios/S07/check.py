"""S07 - a cross-holding in the chain: the cycle is reported, the effective holding follows the declared rule."""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402
from dossier.lib import jsonio  # noqa: E402

SID = "S07"


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    inp = c.scenario_dir(SID) / "input"
    problems: list[str] = []

    # declared policy: abstain
    want = exp["abstain"]
    work = c.workdir(SID)
    code, _, _ = c.run(inp, work)
    c.expect(problems, "abstain: exit code", code, want["exit_code"])
    own = c.view(work, eid)["ownership"]
    c.expect(problems, "abstain: cycles", own["cycles"], exp["cycles"])
    c.expect(problems, "abstain: outcome", own["outcome"], want["outcome"])
    c.expect(problems, "abstain: effective", own["effective"], want["effective"])
    for other in want["also_to_confirm"]:
        o = c.view(work, other)["ownership"]
        c.expect(problems, f"abstain: {other} outcome", (o["outcome"], o["effective"]), ("TO_CONFIRM", None))
    prov = c.provenance(work, eid)
    c.expect(problems, "abstain: derived figures published", prov["derived"], [])
    docx = work / "dossiers" / eid / "dossier.docx"
    rows = [r for r in c.docx_rows(docx, "Field to confirm") if r["Field to confirm"] == "effective_holdings"]
    c.expect(problems, "abstain: effective holdings in the DOCX", [r["Value"] for r in rows], ["[TO CONFIRM]"])
    c.expect(problems, "abstain: effective-share table in the DOCX", c.docx_rows(docx, "Natural person"), [])
    from dossier.s7_audit import read_docx
    if not any("Cross-holding found: E-0002 <-> E-0003" in p for p in read_docx(docx)["paragraphs"]):
        problems.append("abstain: the DOCX does not report the cross-holding")

    # the other declared policy: closure (exact limit of the look-through)
    want = exp["closure"]
    override = jsonio.load(inp / "policy_override.json")

    def change(rules: dict) -> None:
        rules[override["file"]]["parameters"][override["parameter"]]["value"] = override["value"]

    base = c.workdir(SID)
    code, _, _ = c.run(inp, base / "work", rules_dir=c.rules_copy(base / "rules", change))
    c.expect(problems, "closure: exit code", code, want["exit_code"])
    for e, eff in want["effective"].items():
        o = c.view(base / "work", e)["ownership"]
        c.expect(problems, f"closure: {e} outcome", o["outcome"], want["outcome"])
        c.expect(problems, f"closure: {e} method", o["method"], want["method"])
        c.expect(problems, f"closure: {e} effective", o["effective"], eff)
        c.expect(problems, f"closure: {e} cycles", o["cycles"], exp["cycles"])
        if o["effective"]:
            total = sum((Fraction(v) for v in o["effective"].values()), Fraction(0))
            c.expect(problems, f"closure: {e} sum of effective holdings", total, Fraction(1))
    return c.report(SID, problems, "cycle E-0002 <-> E-0003 reported; effective holding [TO CONFIRM] under "
                                   "'abstain', exact under 'closure' (E-0002: P-002 45/49, P-003 4/49)")


if __name__ == "__main__":
    c.main(check)
