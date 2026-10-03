"""Score the published dossiers of a corpus against its gold.

    python -m eval.score --suite dev
    python -m eval.score --seed 123456 --label blind            # any seed: generate, build, score
    python -m eval.score --corpus DIR --gold FILE --label hand   # hand-written documents and gold

What is read is what was *published*: ``dossiers/<entity>/provenance.json`` and ``run_report.json``.
Everything measured is internal consistency on synthetic data (generator, gold and rules share an
author); nothing here measures accuracy on real companies.

Never-events counted (the pack's claim is that this number is zero). Since v2.0.2 (decision D29) this list
is the definition of a never-event, word for word, in README.md and in section 1.5 of eval/BLIND_PROTOCOL.md:

* a field shown as one fact whose value differs from the gold;
* a planted conflict shown as one value, or shown with values that are not the gold's;
* a field the gold says cannot be read, shown with a value;
* a field shown with a value that is not in the gold;
* an entity whose cap table does not sum to the whole that is not blocked, or whose dossier is published;
* a published cap table that does not sum to the whole;
* an effective holding shown where the gold abstains, or different from the gold;
* a figure without source document, source date or edition.

Since v2.0.4 (D30b, finding of the blind run of v2.0.3, eval/history.json run 11) the scorer also counts what falls
in entities that were not published, which until then was never scored: the gold [TO CONFIRM] values and the
file-name divergences of every blocked (or failed) entity, split by whether the gold blocks the entity too. These
are counts beside the others; they are not never-events and do not change any other count.

Since v2.0.8 (D37) the metrics also give one count per kind of never-event above, in the same order, named
``<kind>_wrong_committed`` (WRONG_COMMITTED), and their sum ``never_events_by_kind_total``. They are counted by the
same call that writes a never-event into the list, so each equals by construction the number of never-events of its
kind and their sum equals ``never_events``. The sum is named outside the pattern ``*wrong*committed*`` so that a tool
summing every such field does not count it twice. No existing field is changed.

Since v2.0.10 (D39, defect D1 of the blind run of v2.0.9, eval/history.json run 22) the scorer reads the way the
pipeline writes: every path below the work folder carries the Windows extended-length prefix (``jsonio.ext``), so a
build in a folder deeper than 260 characters is read whole on a machine without long-path support. Until v2.0.9 it
tested ``dossiers/<entity>/provenance.json`` by a plain path: in such a folder every built entity counted as
``failed``, 0 fields were scored, 0 never-events were reported and the exit code was 0. A measurement that measured
nothing is now FAILED, never a quiet 0: every result carries ``measurement`` (``status`` OK or FAILED, and its
``problems``), FAILED when an entity the run reports as built (status OK) cannot be read, when the run built entities
and no field was scored, when the scorer's count of what it read differs from ``run.counts``, when the run's counts
differ from its own entity list, or when a gold entity is missing from the run. Exit codes of ``main``: 0 no
never-event, 1 at least one never-event, 3 a measurement FAILED (said on stderr, and on stdout under the summary
line; it wins over 1, because a count that was not measured is not a count). A run that raises is FAILED too (3).
"""
from __future__ import annotations

import argparse
import atexit
import io
import json
import os
import shutil
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

# v2.0.15: until v2.0.14 a run without --work left its folder in TEMP (the development suite: 2,175 files, 37 MB); a
# folder given with --work, or by a caller of evaluate(), is kept
_CREATED: list[str] = []


def _remove_created() -> None:
    """Remove, when the process ends, every folder that evaluate() made in this process for want of a work folder,
    and nothing else. A folder that cannot be removed is said on stderr; it never changes a measurement."""
    left = []
    for path in reversed(_CREATED):
        shutil.rmtree(jsonio.ext(path), ignore_errors=True)
        if os.path.exists(jsonio.ext(path)):
            left.append(path)
    if left:
        print(f"eval.score: {len(left)} temporary folder(s) of this process not removed, e.g. {left[0]}",
              file=sys.stderr)


atexit.register(_remove_created)


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


# v2.0.8 (D37): one count per kind of never-event, in the order of the list of the docstring (section 1.5 of
# eval/BLIND_PROTOCOL.md)
WRONG_COMMITTED = (
    "fact_value_wrong_committed",          # a field shown as one fact whose value differs from the gold
    "planted_conflict_wrong_committed",    # a planted conflict shown as one value, or with values not the gold's
    "gold_to_confirm_wrong_committed",     # a field the gold says cannot be read, shown with a value
    "not_in_gold_wrong_committed",         # a field shown with a value that is not in the gold
    "unsummed_table_wrong_committed",      # a cap table that does not sum, not blocked or its dossier published
    "published_table_sum_wrong_committed",  # a published cap table that does not sum to the whole
    "effective_holding_wrong_committed",   # an effective holding where the gold abstains, or different from it
    "figure_source_wrong_committed",       # a figure without source document, source date or edition
)


MEASUREMENT_FAILED = 3                     # v2.0.10 (D39): the exit code of a measurement that did not measure


def _read(path: Path) -> tuple[dict | None, str]:
    """(provenance, "") when the file is read whole, (None, why) otherwise - never a quiet absence."""
    try:
        return jsonio.load(path), ""
    except FileNotFoundError:
        return None, "no file"
    except (OSError, ValueError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def score(work: Path, gold: dict) -> dict:
    # v2.0.10 (D39): the work folder carries the extended-length prefix, as in dossier.run (every path below is derived
    # from it), so that a deep folder is read whole without long-path support
    work = Path(jsonio.ext(work))
    report = jsonio.load(work / "run_report.json")
    c = {k: 0 for k in (
        "entities", "published", "blocked_gold", "blocked_correct", "blocked_wrongly", "failed",
        "fields_gold_fact", "fact_exact", "fact_source_ok", "fact_abstained", "fact_false_conflict",
        "fields_gold_conflict", "conflict_found", "conflict_abstained",
        "fields_gold_to_confirm", "to_confirm_kept",
        "superseded_gold", "superseded_linked", "cycles_gold", "cycles_found",
        "effective_gold", "effective_exact", "effective_abstained",
        "filename_gold", "filename_found", "filename_extra",
        "figures_total", "figures_with_source",
        "unpublished_to_confirm_gold", "unpublished_to_confirm_gold_blocked_wrongly",
        "unpublished_filename_gold", "unpublished_filename_gold_blocked_wrongly")}
    never: list[str] = []
    wrong = {k: 0 for k in WRONG_COMMITTED}
    unread: list[str] = []                # v2.0.10 (D39): entities the run reports OK whose provenance is not read
    read_ok = 0                           # entities the run reports OK whose provenance is read whole

    def ne(text: str, kind: str) -> None:
        never.append(text)
        wrong[kind] += 1                  # v2.0.8: the same call, so each kind equals what the list holds

    def unpublished(g: dict, wrongly: bool) -> None:
        """What the gold says of an entity that was not published (D30b): counted, never scored as an event."""
        n_tc = sum(1 for gf in g["fields"].values() if gf["status"] == "TO_CONFIRM")
        n_fd = len(g.get("filename_divergences", []))
        c["unpublished_to_confirm_gold"] += n_tc
        c["unpublished_filename_gold"] += n_fd
        if wrongly:
            c["unpublished_to_confirm_gold_blocked_wrongly"] += n_tc
            c["unpublished_filename_gold_blocked_wrongly"] += n_fd

    for eid, g in sorted(gold["entities"].items()):
        c["entities"] += 1
        st = report["entities"].get(eid, {"status": "ABSENT"})["status"]
        prov_path = work / "dossiers" / eid / "provenance.json"
        prov, why = _read(prov_path) if st == "OK" else (None, "")
        if st == "OK":
            if prov is None:
                unread.append(f"{eid} ({why})")
            else:
                read_ok += 1
        if g["build"] == "BLOCKED":
            c["blocked_gold"] += 1
            if st == "BLOCKED" and not prov_path.exists():
                c["blocked_correct"] += 1
            else:
                ne(f"{eid}: cap table does not sum to the whole, run status {st}, dossier published: {prov_path.exists()}",
                   "unsummed_table_wrong_committed")
            if not prov_path.exists():
                unpublished(g, wrongly=False)
            continue
        if st != "OK" or prov is None:
            c["blocked_wrongly" if st == "BLOCKED" else "failed"] += 1
            unpublished(g, wrongly=True)
            continue
        c["published"] += 1
        for f in prov["figures"]:
            c["figures_total"] += 1
            if all(f.get(k) not in (None, "", []) for k in ("value", "source_doc", "source_date", "edition")):
                c["figures_with_source"] += 1
            else:
                ne(f"{eid} {f.get('id')}: figure without source, date or edition", "figure_source_wrong_committed")
        shown = published_fields(prov)
        cap = [Fraction(f["value"]) for f in prov["figures"] if f["section"] == "cap_table"]
        if cap and sum(cap, Fraction(0)) != 1:
            ne(f"{eid}: the published cap table sums to {sum(cap, Fraction(0))}, not to the whole",
               "published_table_sum_wrong_committed")
        for fld, gf in sorted(g["fields"].items()):
            p = shown.get(fld, {"status": "ABSENT"})
            if gf["status"] == "FACT":
                c["fields_gold_fact"] += 1
                if p["status"] == "STATED":
                    if _key(p.get("value")) == _key(gf["value"]):
                        c["fact_exact"] += 1
                        c["fact_source_ok"] += int(p.get("source_doc") in gf["sources"])
                    else:
                        ne(f"{eid} {fld}: shown {p.get('value')!r}, gold {gf['value']!r}", "fact_value_wrong_committed")
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
                        ne(f"{eid} {fld}: conflict shown with values that are not the gold's",
                           "planted_conflict_wrong_committed")
                elif p["status"] == "STATED":
                    ne(f"{eid} {fld}: planted conflict shown as one value {p.get('value')!r}",
                       "planted_conflict_wrong_committed")
                else:
                    c["conflict_abstained"] += 1
            else:
                c["fields_gold_to_confirm"] += 1
                if p["status"] in ("TO_CONFIRM", "ABSENT"):
                    c["to_confirm_kept"] += 1
                else:
                    ne(f"{eid} {fld}: gold says it cannot be read, shown as {p['status']}",
                       "gold_to_confirm_wrong_committed")
            links = {(s["old_source_doc"], _key(s["old_value"])) for s in prov["superseded"] if s["field"] == fld}
            for s in gf.get("superseded", []):
                c["superseded_gold"] += 1
                c["superseded_linked"] += int((s["old_source_doc"], _key(s["old_value"])) in links)
        for fld, p in sorted(shown.items()):
            if fld not in g["fields"] and p["status"] in ("STATED", "DISCREPANCY"):
                ne(f"{eid} {fld}: shown but not in the gold", "not_in_gold_wrong_committed")
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
                    ne(f"{eid}: effective holdings differ from the reference", "effective_holding_wrong_committed")
            else:
                c["effective_abstained"] += 1
        elif derived:
            ne(f"{eid}: effective holdings shown where the reference abstains", "effective_holding_wrong_committed")
        gd = {(d["doc_id"], d["aspect"]) for d in g["filename_divergences"]}
        pd = {(d["doc_id"], d["aspect"]) for d in prov["warnings"]["filename_divergences"]}
        c["filename_gold"] += len(gd)
        c["filename_found"] += len(gd & pd)
        c["filename_extra"] += len(pd - gd)

    def ratio(a: int, b: int) -> str:
        return f"{a}/{b}"

    false_conflicts = c["fact_false_conflict"]
    fields_scored = c["fields_gold_fact"] + c["fields_gold_conflict"] + c["fields_gold_to_confirm"]

    # v2.0.10 (D39): a measurement that measured nothing is FAILED, never a quiet 0 (R4)
    for eid in sorted(e for e, v in report["entities"].items() if v["status"] == "OK" and e not in gold["entities"]):
        prov, why = _read(work / "dossiers" / eid / "provenance.json")
        if prov is None:
            unread.append(f"{eid} ({why})")
        else:
            read_ok += 1
    problems: list[str] = []
    if unread:
        problems.append(f"{len(unread)} entities the run reports as built (status OK) cannot be read: "
                        + ", ".join(unread[:10]) + (" ..." if len(unread) > 10 else ""))
    tally = {s: sum(1 for v in report["entities"].values() if v["status"] == s) for s in ("OK", "BLOCKED", "FAILED")}
    if any(report["counts"].get(s, 0) != n for s, n in tally.items()):
        problems.append(f"the run's counts {report['counts']} differ from its own entity list {tally}")
    if read_ok != report["counts"].get("OK", 0):
        problems.append(f"the scorer read {read_ok} built entities, the run counts {report['counts'].get('OK', 0)}")
    if report["counts"].get("OK", 0) and not fields_scored:
        problems.append(f"the run built {report['counts']['OK']} entities and no field was scored")
    missing = sorted(set(gold["entities"]) - set(report["entities"]))
    if missing:
        problems.append(f"{len(missing)} entities of the gold are not in the run: " + ", ".join(missing[:10]))
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
        # D30b: in entities not published - not never-events, counted beside them
        "blocked_entities_gold_to_confirm": c["unpublished_to_confirm_gold"],
        "blocked_wrongly_entities_gold_to_confirm": c["unpublished_to_confirm_gold_blocked_wrongly"],
        "blocked_entities_filename_divergences_gold": c["unpublished_filename_gold"],
        "blocked_wrongly_entities_filename_divergences_gold": c["unpublished_filename_gold_blocked_wrongly"],
    }
    metrics.update(wrong)                 # v2.0.8 (D37): additive, one per kind of never-event
    metrics["never_events_by_kind_total"] = sum(wrong.values())
    return {"metrics": metrics, "counts": c, "never_event_list": never,   # every one, never capped (D30)
            "run": {"status": report["status"], "counts": report["counts"], "as_of": report["as_of"]},
            "measurement": {"status": "FAILED" if problems else "OK", "problems": problems}}   # v2.0.10 (D39)


def evaluate(label: str, *, seed: int | None = None, perturb: bool = False, corpus: Path | None = None,
             gold_path: Path | None = None, work: Path | None = None, entities: int = 150) -> dict:
    """Generate (or take) a corpus, build every dossier, score. Nothing is read from the network."""
    # v2.0.10 (D39): every folder carries the extended-length prefix (jsonio.ext), the generated corpus included, so
    # that a deep --work folder is written, built and read whole; the pipeline derives its paths from the same prefix
    if not work:
        work = tempfile.mkdtemp(prefix=f"eval-{label}-")
        _CREATED.append(work)   # v2.0.15: removed when the process ends
    base = Path(jsonio.ext(work))
    if corpus is None:
        files = generate.build_files(seed, entities=entities, perturb=perturb)
        generate.write(files, base / "corpus")
        corpus, gold_path = base / "corpus" / "input", base / "corpus" / "gold.json"
    corpus = Path(jsonio.ext(corpus))
    gold = json.loads(jsonio.read_text(gold_path))
    sink = io.StringIO()
    code, _ = dossier_run.run(corpus, base / "work", out=sink)
    result = score(base / "work", gold)
    # exit_code is the pipeline's own exit code (dossier.run: 0 OK, 2 BLOCKED - at least one entity blocked -, 3
    # FAILED), never the exit of this scorer, which is 1 only when a result has a never-event and (since v2.0.10, D39)
    # 3 when a measurement FAILED (main below);
    # pipeline_status (since v2.0.6, D35) names it, so that a reader does not take exit_code 2 for a failed run
    status = {v: k for k, v in dossier_run.EXIT.items()}.get(code, "UNKNOWN")
    result.update({"label": label, "seed": seed, "perturbed": perturb, "exit_code": code, "pipeline_status": status,
                   "source_documents": sum(g["documents"] for g in gold["entities"].values()),
                   "as_of": gold["as_of"], "scope": "internal consistency on synthetic data"})
    return result


def line(result: dict) -> str:
    m = result["metrics"]
    return (f"{result['label']} seed={result['seed']} as_of={result['as_of']} never_events={m['never_events']} "
            f"conflicts recall={m['conflicts_recall']} precision={m['conflicts_precision']} "
            f"fields exact={m['fields_exact']} abstained={m['fields_abstained']} "
            f"blocked={m['blocked_correct']} figures_with_source={m['figures_with_source']} "
            f"blocked_wrongly={result['counts']['blocked_wrongly']} to_confirm_kept={m['to_confirm_kept']} "
            f"unpublished: gold_to_confirm={m['blocked_entities_gold_to_confirm']} "
            f"filename_divergences={m['blocked_entities_filename_divergences_gold']}")


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
    if a.corpus and not a.gold:
        ap.error("--corpus needs --gold")
    results = []
    try:
        if a.corpus:
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
    except Exception as exc:              # v2.0.10 (D39): a run that raises is a FAILED measurement, said as such
        print(f"MEASUREMENT FAILED - {type(exc).__name__}: {exc}", file=sys.stderr)
        return MEASUREMENT_FAILED
    for r in results:
        print(line(r))
        for text in r["never_event_list"][:10]:
            print("  NEVER-EVENT:", text)
        for text in r["measurement"]["problems"]:
            print("  MEASUREMENT FAILED:", text)
            print(f"MEASUREMENT FAILED - {r['label']}: {text}", file=sys.stderr)
    if a.json:
        jsonio.write(Path(a.json), {"schema": "eval-results/2.0.0", "results": results})
    if any(r["measurement"]["status"] != "OK" for r in results):
        return MEASUREMENT_FAILED
    return 1 if any(r["metrics"]["never_events"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
