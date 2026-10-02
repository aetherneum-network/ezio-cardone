"""S08 - the shareable layer: no identity string survives, the ownership graph keeps its shape."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _common as c  # noqa: E402
from dossier.lib import jsonio  # noqa: E402

SID = "S08"


def check():
    exp = c.expected(SID)
    eid = exp["entity"]
    inp = c.scenario_dir(SID) / "input"
    work = c.workdir(SID)
    code, _, _ = c.run(inp, work)
    problems: list[str] = []
    c.expect(problems, "exit code", code, exp["exit_code"])

    # every string of the identity layer, computed here (not by the pipeline)
    identity = jsonio.load(inp / "identity" / "persons.json")
    strings = sorted(set(identity) | {v for p in identity.values() for v in p.values()})
    c.expect(problems, "identity strings to look for", len(strings), exp["identity_strings_that_must_not_appear"])
    share = work / "shareable" / eid
    haystack = (jsonio.read_text(share / "provenance_shareable.json") + jsonio.read_text(share / "graph.json")
                + c.docx_text(share / "dossier_shareable.docx"))
    leaked = [s for s in strings if s in haystack]
    c.expect(problems, "identity strings in the shareable files", leaked, [])
    internal = c.docx_text(work / "dossiers" / eid / "dossier.docx")
    if not any(identity[p]["name"] in internal for p in identity):
        problems.append("the internal dossier carries no name: the comparison proves nothing")

    # the graph keeps its shape: same edges and exact shares, persons under opaque ids
    def opaque(node: str) -> str:
        if not node.startswith("P-"):
            return node
        return "N-" + hashlib.sha256(f"{exp['salt']}:{node}".encode("utf-8")).hexdigest()[:12]

    key = lambda e: (e["held"], e["holder"])  # noqa: E731
    want_edges = sorted(({"holder": opaque(e["holder"]), "held": e["held"], "share": e["share"]}
                         for e in exp["edges"]), key=key)
    graph = jsonio.load(share / "graph.json")
    got_edges = sorted(({k: e[k] for k in ("holder", "held", "share")} for e in graph["edges"]), key=key)
    c.expect(problems, "edges of the shareable graph", got_edges, want_edges)
    c.expect(problems, "effective holdings of the shareable graph", graph["effective"],
             {opaque(p): s for p, s in exp["effective"].items()})
    unsourced = [e for e in graph["edges"] if not all(e.get(k) for k in ("source_doc", "source_date", "edition"))]
    c.expect(problems, "edges without source", unsourced, [])
    inner = c.view(work, eid)["ownership"]
    c.expect(problems, "effective holdings of the internal layer", inner["effective"], exp["effective"])
    return c.report(SID, problems, f"0/{len(strings)} identity strings in the shareable DOCX and JSON; "
                                   f"{len(got_edges)} edges and the effective holdings unchanged under opaque ids")


if __name__ == "__main__":
    c.main(check)
