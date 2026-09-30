"""Score the published dossiers of a corpus against its gold.

    python -m eval.score --suite dev
    python -m eval.score --seed 123456 --label blind            # any seed: generate, build, score
    python -m eval.score --corpus DIR --gold FILE --label hand   # hand-written documents and gold

What is read is what was *published*: ``dossiers/<entity>/provenance.json`` and ``run_report.json``.
Everything measured is internal consistency on synthetic data (generator, gold and rules share an
author); nothing here measures accuracy on real companies.

Never-events counted (the pack's claim is that this number is zero):

* a field shown as one fact whose value differs from the gold;
* a planted conflict shown as one value, or shown with values that are not the gold's;
* a field the gold says cannot be read, shown with a value;
* a dossier published for an entity whose cap table does not sum to the whole;
* an effective holding shown where the gold abstains, or different from the gold;
* a figure without source document, source date or edition.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from corpus import generate  # noqa: E402
from dossier import run as dossier_run  # noqa: E402
from dossier.lib import jsonio  # noqa: E402

SUITES = generate.SUITES


def _key(v) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def published_fields(prov: dict) -> dict[str, dict]:
    """field -> {status, value | values, source_doc} as the published dossier shows it."""
    out: dict[str, dict] = {f: {"status": s} for f, s in prov["field_status"].items()}
    table = []
    for f in prov["figures"]:
        slot = out.setdefault(f["field"], {"status": "ABSENT"})
        if f["section"] == "facts":
            slot["value"], slot["source_doc"] = f["value"], f["source_doc"]
        elif f["section"] == "cap_table":
            table.append({"holder": f["holder"], "share": f["value"]})
            slot["source_doc"] = f["source_doc"]
        elif f["section"] == "discrepancies":
            slot.setdefault("values", [])
            if _key(f["value"]) not in [_key(v) for v in slot["values"]]:
                slot["values"].append(f["value"])
    if table:
        out["shareholders"]["value"] = sorted(table, key=lambda r: r["holder"])
    return out


def score(work: Path, gold: dict) -> dict:
    report = jsonio.load(work / "run_report.json")
    c = {k: 0 for k in (
        "entities", "published", "blocked_gold", "blocked_correct", "blocked_wrongly", "failed",
        "fields_gold_fact", "fact_exact", "fact_source_ok", "fact_abstained", "fact_false_conflict",
        "fields_gold_conflict", "conflict_found", "conflict_abstained",
        "fields_gold_to_confirm", "to_confirm_kept",
        "superseded_gold", "superseded_linked", "cycles_gold", "cycles_found",
        "effective_gold", "effective_exact", "effective_abstained",
        "filename_gold", "filename_found", "filename_extra",
        "figures_total", "figures_with_source")}
    never: list[str] = []

    def ne(text: str) -> None:
        never.append(text)

    for eid, g in sorted(gold["entities"].items()):
        c["entities"] += 1
        st = report["entities"].get(eid, {"status": "ABSENT"})["status"]
        prov_path = work / "dossiers" / eid / "provenance.json"
        if g["build"] == "BLOCKED":
            c["blocked_gold"] += 1
            if st == "BLOCKED" and not prov_path.exists():
                c["blocked_correct"] += 1
            else:
                ne(f"{eid}: cap table does not sum to the whole, run status {st}, dossier published: {prov_path.exists()}")
            continue
        if st != "OK" or not prov_path.exists():
            c["blocked_wrongly" if st == "BLOCKED" else "failed"] += 1
            continue
        c["published"] += 1
        prov = jsonio.load(prov_path)
        for f in prov["figures"]:
            c["figures_total"] += 1
            if all(f.get(k) not in (None, "", []) for k in ("value", "source_doc", "source_date", "edition")):
                c["figures_with_source"] += 1
            else:
                ne(f"{eid} {f.get('id')}: figure without source, date or edition")
        shown = published_fields(prov)
        cap = [Fraction(f["value"]) for f in prov["figures"] if f["section"] == "cap_table"]
        if cap and sum(cap, Fraction(0)) != 1:
            ne(f"{eid}: the published cap table sums to {sum(cap, Fraction(0))}, not to the whole")
        for fld, gf in sorted(g["fields"].items()):
            p = shown.get(fld, {"status": "ABSENT"})
            if gf["status"] == "FACT":
                c["fields_gold_fact"] += 1
                if p["status"] == "STATED":
                    if _key(p.get("value")) == _key(gf["value"]):
                        c["fact_exact"] += 1
                        c["fact_source_ok"] += int(p.get("source_doc") in gf["sources"])
                    else:
                        ne(f"{eid} {fld}: shown {p.get('value')!r}, gold {gf['value']!r}")
                elif p["status"] == "DISCREPANCY":
                    c["fact_false_conflict"] += 1
                else:
                    c["fact_abstained"] += 1
            elif gf["status"] == "DISCREPANCY":
                c["fields_gold_conflict"] += 1
                if p["status"] == "DISCREPANCY":
                    if sorted(_key(v) for v in p.get("values", [])) == sorted(_key(v) for v in gf["values"]):
                        c["conflict_found"] += 1
                    else:
                        ne(f"{eid} {fld}: conflict shown with values that are not the gold's")
                elif p["status"] == "STATED":
                    ne(f"{eid} {fld}: planted conflict shown as one value {p.get('value')!r}")
                else:
                    c["conflict_abstained"] += 1
            else:
                c["fields_gold_to_confirm"] += 1
                if p["status"] in ("TO_CONFIRM", "ABSENT"):
                    c["to_confirm_kept"] += 1
                else:
                    ne(f"{eid} {fld}: gold says it cannot be read, shown as {p['status']}")
            links = {(s["old_source_doc"], _key(s["old_value"])) for s in prov["superseded"] if s["field"] == fld}
            for s in gf.get("superseded", []):
                c["superseded_gold"] += 1
                c["superseded_linked"] += int((s["old_source_doc"], _key(s["old_value"])) in links)
        for fld, p in sorted(shown.items()):
            if fld not in g["fields"] and p["status"] in ("STATED", "DISCREPANCY"):
                ne(f"{eid} {fld}: shown but not in the gold")
        go, po = g["ownership"], prov["ownership"]
        derived = {d["person"]: d["value"] for d in prov["derived"]}
        if go["cycles"]:
            c["cycles_gold"] += 1
            c["cycles_found"] += int(po["cycles"] == go["cycles"])
        if go["outcome"] == "RESOLVED":
            c["effective_gold"] += 1
            if derived:
                if derived == go["effective"]:
                    c["effective_exact"] += 1
                else:
                    ne(f"{eid}: effective holdings differ from the reference")
            else:
                c["effective_abstained"] += 1
        elif derived:
            ne(f"{eid}: effective holdings shown where the reference abstains")
        gd = {(d["doc_id"], d["aspect"]) for d in g["filename_divergences"]}
        pd = {(d["doc_id"], d["aspect"]) for d in prov["warnings"]["filename_divergences"]}
        c["filename_gold"] += len(gd)
        c["filename_found"] += len(gd & pd)
        c["filename_extra"] += len(pd - gd)

    def ratio(a: int, b: int) -> str:
        return f"{a}/{b}"

    false_conflicts = c["fact_false_conflict"]
    fields_scored = c["fields_gold_fact"] + c["fields_gold_conflict"] + c["fields_gold_to_confirm"]
    metrics = {
        "never_events": len(never),
        "conflicts_recall": ratio(c["conflict_found"], c["fields_gold_conflict"]),
        "conflicts_precision": ratio(c["conflict_found"], c["conflict_found"] + false_conflicts),
        "fields_exact": ratio(c["fact_exact"], c["fields_gold_fact"]),
        "fields_abstained": ratio(c["fact_abstained"] + c["conflict_abstained"], fields_scored),
        "fact_source_among_gold_sources": ratio(c["fact_source_ok"], c["fact_exact"]),
        "to_confirm_kept": ratio(c["to_confirm_kept"], c["fields_gold_to_confirm"]),
        "blocked_correct": ratio(c["blocked_correct"], c["blocked_gold"]),
        "superseded_linked": ratio(c["superseded_linked"], c["superseded_gold"]),
        "cycles_found": ratio(c["cycles_found"], c["cycles_gold"]),
        "effective_holdings_exact": ratio(c["effective_exact"], c["effective_gold"]),
        "filename_divergences_found": ratio(c["filename_found"], c["filename_gold"]),
        "figures_with_source": ratio(c["figures_with_source"], c["figures_total"]),
    }
    return {"metrics": metrics, "counts": c, "never_event_list": never[:50],
            "run": {"status": report["status"], "counts": report["counts"], "as_of": report["as_of"]}}


def evaluate(label: str, *, seed: int | None = None, perturb: bool = False, corpus: Path | None = None,
             gold_path: Path | None = None, work: Path | None = None, entities: int = 150) -> dict:
    """Generate (or take) a corpus, build every dossier, score. Nothing is read from the network."""
    base = Path(work) if work else Path(tempfile.mkdtemp(prefix=f"eval-{label}-"))
    if corpus is None:
        files = generate.build_files(seed, entities=entities, perturb=perturb)
        generate.write(files, base / "corpus")
        corpus, gold_path = base / "corpus" / "input", base / "corpus" / "gold.json"
    gold = json.loads(Path(gold_path).read_text(encoding="utf-8"))
    sink = io.StringIO()
    code, _ = dossier_run.run(corpus, base / "work", out=sink)
    result = score(base / "work", gold)
    result.update({"label": label, "seed": seed, "perturbed": perturb, "exit_code": code,
                   "source_documents": sum(g["documents"] for g in gold["entities"].values()),
                   "as_of": gold["as_of"], "scope": "internal consistency on synthetic data"})
    return result


def line(result: dict) -> str:
    m = result["metrics"]
    return (f"{result['label']} seed={result['seed']} as_of={result['as_of']} never_events={m['never_events']} "
            f"conflicts recall={m['conflicts_recall']} precision={m['conflicts_precision']} "
            f"fields exact={m['fields_exact']} abstained={m['fields_abstained']} "
            f"blocked={m['blocked_correct']} figures_with_source={m['figures_with_source']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="eval.score", description=__doc__.split("\n\n")[0])
    ap.add_argument("--suite", choices=sorted(SUITES), action="append")
    ap.add_argument("--seed", type=int, help="any seed (used for the blind run)")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--corpus", help="input folder with hand-written documents")
    ap.add_argument("--gold", help="gold file of the hand-written documents")
    ap.add_argument("--label", default="run")
    ap.add_argument("--work", help="new or empty folder for the corpus and the build (default: a temp folder)")
    ap.add_argument("--json", help="write the results to this file")
    a = ap.parse_args(argv)
    results = []
    if a.corpus:
        if not a.gold:
            ap.error("--corpus needs --gold")
        results.append(evaluate(a.label, corpus=Path(a.corpus), gold_path=Path(a.gold),
                                work=Path(a.work) if a.work else None))
    elif a.seed is not None:
        results.append(evaluate(a.label, seed=a.seed, perturb=a.perturb, work=Path(a.work) if a.work else None))
    else:
        for name in a.suite or ["dev"]:
            s = SUITES[name]
            r = evaluate(name, seed=s["seed"], perturb=s["perturb"],
                         work=Path(a.work) / name if a.work else None)
            r["role"] = s["role"]
            results.append(r)
    for r in results:
        print(line(r))
        for text in r["never_event_list"][:10]:
            print("  NEVER-EVENT:", text)
    if a.json:
        jsonio.write(Path(a.json), {"schema": "eval-results/2.0.0", "results": results})
    return 1 if any(r["metrics"]["never_events"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
