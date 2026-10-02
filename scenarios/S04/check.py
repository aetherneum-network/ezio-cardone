"""S04 - after a capital increase the old amount is still in five outgoing documents among ten decoys."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402
from dossier import rules_engine, s7_audit  # noqa: E402

SID = "S04"


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    inp = c.scenario_dir(SID) / "input"
    work = c.workdir(SID)
    code, _, report = c.run(inp, work)
    problems: list[str] = []
    c.expect(problems, "exit code", code, exp["exit_code"])
    c.match_fields(problems, c.fields(work, eid), {"share_capital.resolved": exp["capital_now"]})

    view = c.view(work, eid)
    names = {e: c.view(work, e)["fields"]["name"]["value"].rsplit(" ", 1)[0] for e in sorted(report["entities"])}
    got = s7_audit.scan_outgoing(inp / "outgoing", view["superseded"], names, eid, rules_engine.load())
    c.expect(problems, "files scanned", got["files_scanned"], exp["files_scanned"])
    stale = {(s["file"], s["line"]) for s in exp["stale"]}
    flagged = {(h["file"], h["line"]) for h in got["findings"]}
    found = stale & flagged
    false_pos = sorted(flagged - stale)
    c.expect(problems, "stale mentions found", len(found), len(stale))
    if len(false_pos) > exp["max_false_positives"]:
        problems.append(f"{len(false_pos)} false positives: {false_pos}")
    for h in got["findings"]:
        if (h["file"], h["line"]) in stale:
            for key, val in exp["every_finding"].items():
                c.expect(problems, f"{h['file']}: {key}", h.get(key), val)
    unknown = sorted({f for f, _ in flagged} - {f for f, _ in stale} - set(exp["decoys"]))
    c.expect(problems, "flagged files that the scenario does not know", unknown, [])
    return c.report(SID, problems, f"{len(found)}/{len(stale)} stale mentions found, {len(false_pos)} false "
                                   f"positive(s) on {len(exp['decoys'])} decoys; each finding carries the new "
                                   f"value with its edition",
                    {"false_positives": [list(x) for x in false_pos],
                     "ignored_by_rule": sorted({(h["file"], h["rule"]) for h in got["ignored"]})})


if __name__ == "__main__":
    c.main(check)
