"""S05 - "as at 31 March": the answer comes from the snapshot of that date; no snapshot is ever overwritten."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402
from dossier.lib import jsonio  # noqa: E402
from dossier.s5_snapshot import SnapshotStore  # noqa: E402

SID = "S05"


def check():
    exp = c.expected(SID)
    inp = c.scenario_dir(SID) / "input"
    plan = jsonio.load(inp / "plan.json")
    eid = plan["entity"]
    base = c.workdir(SID)
    store_dir = base / "store"
    problems: list[str] = []

    hashes_after_run: list[dict[str, str]] = []
    for n, as_of in enumerate(plan["runs_as_of"], 1):
        code, _, _ = c.run(inp, base / f"work{n}", as_of, store_dir=store_dir)
        c.expect(problems, f"run as of {as_of}: exit code", code, 0)
        hashes_after_run.append({p.relative_to(store_dir).as_posix(): jsonio.sha256_file(p)
                                 for p in sorted(store_dir.rglob("*.json"))})
    store = SnapshotStore(store_dir)
    c.expect(problems, "snapshots of the entity", len(store.of(eid)), exp["snapshots"])
    for earlier, later in zip(hashes_after_run, hashes_after_run[1:]):
        changed = sorted(f for f, h in earlier.items() if later.get(f) != h)
        c.expect(problems, "earlier snapshot files changed by a later run", changed, [])

    answers = {}
    for asked in plan["asked"]:
        got = store.at(eid, asked)
        want = exp["answers"][asked]
        if want is None:
            c.expect(problems, f"asked {asked}", got, None)
            answers[asked] = None
            continue
        if got is None:
            problems.append(f"asked {asked}: no snapshot answered")
            continue
        f = got["snapshot"]["payload"]["fields"]
        mine = {"as_of": got["as_of"], "shareholders": f["shareholders"].get("value"),
                "directors": f["directors"].get("value")}
        answers[asked] = got["as_of"]
        c.expect(problems, f"asked {asked}", mine, want)

    # a second run on the same date and content appends nothing
    code, _, _ = c.run(inp, base / "work_again", plan["runs_as_of"][-1], store_dir=store_dir)
    c.expect(problems, "snapshots after an identical run", len(store.of(eid)), exp["snapshots"])

    # overwriting is refused; an alteration made behind the store's back is detected
    first = store.of(eid)[0]
    try:
        jsonio.write(store_dir / first["file"], {"overwritten": True}, exclusive=True)
        problems.append("an existing snapshot could be overwritten")
    except FileExistsError:
        pass
    c.expect(problems, "store problems before tampering", store.verify(), [])
    path = store_dir / first["file"]
    path.write_bytes(path.read_bytes().replace(b'"3/5"', b'"4/5"'))
    if not any("content changed" in p for p in store.verify()):
        problems.append("an altered snapshot was not detected")
    return c.report(SID, problems, "asked 2026-03-31 -> snapshot as of 2026-03-31 (holders after the transfer, "
                                   "directors before the appointment); 3 snapshots, earlier files unchanged, "
                                   "overwrite refused, alteration detected", {"answered_as_of": answers})


if __name__ == "__main__":
    c.main(check)
