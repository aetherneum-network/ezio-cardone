"""S09 - a rule is added, the dossiers are rebuilt: only the expected field moves, and the diff says so."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402
from dossier import run as runner  # noqa: E402
from dossier.lib import jsonio  # noqa: E402

SID = "S09"


def check():
    exp = c.expected(SID)
    eid, control = exp["entity"], exp["control_entity"]
    inp = c.scenario_dir(SID) / "input"
    problems: list[str] = []

    before = c.workdir(SID)
    code, _, _ = c.run(inp, before)
    c.expect(problems, "before: exit code", code, exp["before"]["exit_code"])
    c.match_fields(problems, c.fields(before, eid), {"registered_office": exp["before"]["registered_office"]},
                   "before: ")
    facts = [f for f in c.provenance(before, eid)["figures"]
             if f["field"] == "registered_office" and f["section"] == "facts"]
    c.expect(problems, "before: office shown as fact", facts, [])

    patch = jsonio.load(inp / "rule_patch.json")

    def change(rules: dict) -> None:
        group = rules[patch["file"]]["field_rules"]
        at = next(i for i, r in enumerate(group) if r["id"] == patch["insert_before"])
        group.insert(at, patch["rule"])
        rules[patch["file"]]["version"] = patch["new_version"]

    base = c.workdir(SID)
    after = base / "work"
    code, _, report = c.run(inp, after, rules_dir=c.rules_copy(base / "rules", change))
    c.expect(problems, "after: exit code", code, exp["after"]["exit_code"])
    c.expect(problems, "after: version of the rule file in the run report",
             report["rules_version"]["extract"], patch["new_version"])
    c.match_fields(problems, c.fields(after, eid), {"registered_office": exp["after"]["registered_office"]},
                   "after: ")

    diff = runner.diff_runs(before, after)
    c.expect(problems, "diff between the two builds", diff, exp["diff"])
    same = jsonio.read_text(before / "views" / f"{control}.json") == jsonio.read_text(after / "views" / f"{control}.json")
    c.expect(problems, f"view of the control entity {control} unchanged", same, True)
    same_docx = (jsonio.sha256_file(before / "dossiers" / control / "dossier.docx")
                 == jsonio.sha256_file(after / "dossiers" / control / "dossier.docx"))
    c.expect(problems, f"dossier of the control entity {control} byte-identical", same_docx, True)
    return c.report(SID, problems, "one rule added on top: registered_office of E-0001 goes from [TO CONFIRM] "
                                   "to the new office with its source; the diff lists that field only; "
                                   "the control entity is byte-identical", {"diff": diff})


if __name__ == "__main__":
    c.main(check)
