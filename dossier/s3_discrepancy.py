"""Stage 3 - from the assertions of a field to one status, without adjudicating.

For every field the assertions are ordered in time:

* the latest *event* document (deed, resolution, transfer, appointment, office transfer) is the
  baseline; earlier events and earlier state documents are history;
* of each series of *state* documents (registry extracts, holders' ledger, the financial summary of a
  year) only the latest edition counts, and only if it is not older than the baseline;
* the baseline and those witnesses are the *current* sources.

Then the ordered rules of ``rules/discrepancy.json`` decide: no current source -> ``TO_CONFIRM``;
two or more different current values -> ``DISCREPANCY`` (all shown, none chosen); current sources
that could not be read -> ``TO_CONFIRM``; one value -> ``STATED``.

An unreadable event document is still the baseline: an older value is never promoted back.
"""
from __future__ import annotations

import json

from .rules_engine import Rules, first_match

SOURCE_KEYS = ("source_doc", "source_file", "source_date", "edition", "line", "line_end", "quote", "nature", "rule")


def _key(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _src(a: dict) -> dict:
    return {k: a[k] for k in SOURCE_KEYS}


def _order(a: dict) -> tuple:
    return (a["source_date"], a["edition_no"] or 0, a["source_doc"])


def split_current(assertions: list[dict], rules: Rules) -> tuple[dict | None, list[dict], list[tuple[dict, dict]]]:
    """(baseline, witnesses, [(historical assertion, the assertion that superseded it)])."""
    same_day = rules.param("discrepancy", "same_day_state_is_current")
    events = sorted((a for a in assertions if a["role"] == "event"), key=_order)
    baseline = events[-1] if events else None
    history: list[tuple[dict, dict]] = [(e, baseline) for e in events[:-1]]
    witnesses: list[dict] = []
    series: dict[str, list[dict]] = {}
    for a in assertions:
        if a["role"] == "state":
            series.setdefault(a["series"], []).append(a)
    for name in sorted(series):
        editions = sorted(series[name], key=_order)
        latest = editions[-1]
        history.extend((e, latest) for e in editions[:-1])
        if baseline is None:
            witnesses.append(latest)
        elif latest["source_date"] > baseline["source_date"] or (
                same_day and latest["source_date"] == baseline["source_date"]):
            witnesses.append(latest)
        else:
            history.append((latest, baseline))
    return baseline, witnesses, history


def resolve_field(fld: str, assertions: list[dict], rules: Rules) -> dict:
    baseline, witnesses, history = split_current(assertions, rules)
    current = ([baseline] if baseline else []) + witnesses
    stated = [a for a in current if a["status"] == "STATED"]
    groups: dict[str, list[dict]] = {}
    for a in stated:
        groups.setdefault(_key(a["value"]), []).append(a)
    facts = {"no_current_assertion": not current,
             "two_or_more_current_values": len(groups) >= 2,
             "no_current_value": bool(current) and not groups,
             "one_current_value": len(groups) == 1}
    rule = first_match(rules.discrepancy["rules"], lambda r: facts.get(r["when"], False))
    if rule is None:
        raise RuntimeError(f"discrepancy.json has no rule for field {fld}: {facts}")
    res: dict = {"field": fld, "status": rule["status"], "rule": rule["id"],
                 "unreadable": [dict(_src(a), reason=a["reason"]) for a in sorted(current, key=_order)
                                if a["status"] != "STATED"]}
    if rule["status"] == "STATED":
        newest_first = sorted(stated, key=_order, reverse=True)
        res["value"] = newest_first[0]["value"]
        res["sources"] = [_src(a) for a in newest_first]
    elif rule["status"] == "DISCREPANCY":
        cands = []
        for k in sorted(groups, key=lambda k: (min(_order(a) for a in groups[k]), k)):
            members = sorted(groups[k], key=_order)
            cands.append({"value": members[0]["value"], "sources": [_src(a) for a in members]})
        res["candidates"] = cands
    else:
        reasons = sorted({a["reason"] for a in current if a["status"] != "STATED"})
        res["reason"] = rule["reason"] + (": " + "; ".join(reasons) if reasons else "")
    res["historical"] = []
    for old, by in sorted(history, key=lambda pair: _order(pair[0])):
        if old["status"] != "STATED":
            continue
        res["historical"].append(dict(_src(old), value=old["value"],
                                      superseded_by={"source_doc": by["source_doc"], "source_date": by["source_date"],
                                                     "edition": by["edition"]}))
    return res


def resolve_record(record: dict, rules: Rules) -> dict:
    """Resolution of every field of a record, plus the values documents state as 'previous'."""
    by_field: dict[str, list[dict]] = {}
    previous = []
    for a in record["assertions"]:
        if a["field"].endswith(".previous"):
            if a["status"] == "STATED":
                previous.append(dict(_src(a), field=a["field"], value=a["value"]))
        else:
            by_field.setdefault(a["field"], []).append(a)
    fields = {f: resolve_field(f, by_field[f], rules) for f in sorted(by_field)}
    return {"fields": fields, "previous_statements": sorted(previous, key=lambda p: (p["field"], p["source_date"],
                                                                                   p["source_doc"]))}


def superseded_register(resolution: dict) -> list[dict]:
    """Historical values that differ from the value now stated, each bound to the edition that replaced it."""
    out = []
    for fld, res in resolution["fields"].items():
        if res["status"] != "STATED":
            continue
        new = res["sources"][0]
        for h in res["historical"]:
            if _key(h["value"]) != _key(res["value"]):
                out.append({"field": fld, "old_value": h["value"], "old_source_doc": h["source_doc"],
                            "old_edition": h["edition"], "old_source_date": h["source_date"],
                            "new_value": res["value"], "new_source_doc": new["source_doc"],
                            "new_edition": new["edition"], "since": h["superseded_by"]["source_date"]})
    return out


def run_inline_tests(rules: Rules) -> tuple[int, list[str]]:
    n, bad = 0, []
    for r in rules.discrepancy["rules"]:
        for t in r.get("tests", []):
            n += 1
            assertions = []
            for i, a in enumerate(t["assertions"]):
                x = {"field": "f", "role": a["role"], "series": a["series"], "edition_no": i + 1,
                     "source_doc": a["doc"], "source_file": a["doc"], "source_date": a["date"],
                     "edition": f"{a['series']}/{i + 1}", "line": 1, "line_end": 1, "quote": "q",
                     "nature": "resolved", "rule": "T"}
                if a["value"] is None:
                    x["status"], x["reason"] = "TO_CONFIRM", "unreadable"
                else:
                    x["status"], x["value"] = "STATED", a["value"]
                assertions.append(x)
            got = resolve_field("f", assertions, rules)
            exp = t["expect"]
            ok = got["status"] == exp["status"] and got["rule"] == r["id"]
            if "value" in exp:
                ok = ok and got.get("value") == exp["value"]
            if "values" in exp:
                ok = ok and sorted(c["value"] for c in got.get("candidates", [])) == sorted(exp["values"])
            if "historical" in exp:
                ok = ok and sorted(h["value"] for h in got["historical"]) == sorted(exp["historical"])
            if got["status"] != "STATED" and "value" in got:
                ok = False
            if not ok:
                bad.append(f"{r['id']}: got {got['status']} by {got['rule']}, expected {exp}")
    return n, bad
