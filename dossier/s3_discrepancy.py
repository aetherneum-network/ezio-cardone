"""Stage 3 - from the assertions of a field to one status, without adjudicating.

For every field the assertions are ordered in time:

* the latest *event* document (deed, resolution, transfer, appointment, office transfer) is the
  baseline; earlier events and earlier state documents are history;
* of each series of *state* documents (registry extracts, holders' ledger, the financial summary of a
  year) only the latest edition counts, and only if it is not older than the baseline;
* the baseline and those witnesses are the *current* sources.

Then the ordered rules of ``rules/discrepancy.json`` decide: an unread document that may change the
field -> ``TO_CONFIRM``; a document of a recognised type with text that no rule of its kind reads (since v2.0.5,
``classified_checks`` of the record) that may change the field -> ``TO_CONFIRM``; no current source -> ``TO_CONFIRM``; two or more different current values
-> ``DISCREPANCY`` (all shown, none chosen); a current source that could not be read ->
``TO_CONFIRM``; a name whose legal form differs from the legal form stated (since v2.0.6, DISC-035) -> ``TO_CONFIRM``
for the name and the legal form, both readings listed with their sources; every current source readable and agreeing
-> ``STATED``.

An unreadable event document is still the baseline: an older value is never promoted back. What
could be read of a field that is ``TO_CONFIRM`` is kept as ``readable`` statements, never as a fact.
"""
from __future__ import annotations

import datetime as _dt
import json
import re

from . import rules_engine
from .rules_engine import Rules, first_match, rx

SOURCE_KEYS = ("source_doc", "source_file", "source_date", "edition", "line", "line_end", "quote", "nature", "rule")


def _key(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _src(a: dict) -> dict:
    return {k: a[k] for k in SOURCE_KEYS}


def _order(a: dict) -> tuple:
    return (a["source_date"], a["edition_no"] or 0, a["source_doc"])


def split_current(assertions: list[dict], rules: Rules) -> tuple[dict | None, list[dict], list[tuple[dict, dict]]]:
    """(baseline, witnesses, [(historical assertion, the assertion that superseded it)]).

    A tie is never broken by a guess: event documents of the same day are all current (their order within
    the day is not known), and so are two documents that carry the same edition of the same series.
    """
    same_day = rules.param("discrepancy", "same_day_state_is_current")
    events = sorted((a for a in assertions if a["role"] == "event"), key=_order)
    baseline = events[-1] if events else None
    witnesses: list[dict] = [e for e in events[:-1] if e["source_date"] == baseline["source_date"]]
    history: list[tuple[dict, dict]] = [(e, baseline) for e in events[:-1]
                                        if e["source_date"] != baseline["source_date"]]
    series: dict[str, list[dict]] = {}
    for a in assertions:
        if a["role"] == "state":
            series.setdefault(a["series"], []).append(a)
    for name in sorted(series):
        editions = sorted(series[name], key=_order)
        top = _order(editions[-1])[:2]
        latest = [e for e in editions if _order(e)[:2] == top]
        history.extend((e, latest[-1]) for e in editions if _order(e)[:2] != top)
        if baseline is None:
            witnesses.extend(latest)
        elif top[0] > baseline["source_date"] or (same_day and top[0] == baseline["source_date"]):
            witnesses.extend(latest)
        else:
            history.extend((e, baseline) for e in latest)
    return baseline, witnesses, history


def _valid_date(text: str) -> bool:
    try:
        _dt.date.fromisoformat(text)
        return True
    except (TypeError, ValueError):
        return False


def may_change(u: dict, fld: str, rules: Rules) -> bool:
    """Whether an unread document may change the field (rules/discrepancy.json unread_document_scope). A document
    without a fields check - or any scope other than fields_it_may_state - may change every field."""
    fc = u.get("fields_check")
    if rules.param("discrepancy", "unread_document_scope") != "fields_it_may_state" or not fc:
        return True
    for m in fc.get("may_change") or ["*"]:
        if m == "*" or m == fld or (m.endswith(".*") and fld.startswith(m[:-1])):
            return True
    return False


def agrees_with_current(u: dict, fld: str, current: list[dict], rules: Rules) -> bool:
    """A holders' table read whole in an unread document that equals the one current table: it says nothing the
    recognised sources do not already say, so it does not make the shareholders [TO CONFIRM]."""
    hc = u.get("holders_check") or {}
    if (fld != "shareholders" or rules.param("discrepancy", "unread_document_scope") != "fields_it_may_state"
            or hc.get("status") != "read" or len(hc.get("tables") or []) != 1 or not current
            or any(a["status"] != "STATED" for a in current)):
        return False
    values = {_key(a["value"]) for a in current}
    return values == {_key(hc["tables"][0]["value"])}


def unread_that_matter(unread: list[dict], baseline: dict | None, rules: Rules, fld: str | None = None,
                       current: list[dict] | None = None) -> tuple[list[dict], list[dict]]:
    """(unread documents that may change the field, unread documents whose holders' table agrees with the current
    one). A document matters when it may change the field and is undated or not older than the latest event
    document of the field."""
    if not rules.param("discrepancy", "unread_document_blocks_fact"):
        return [], []
    dated = [u for u in unread if baseline is None or not _valid_date(u.get("date") or "")
             or u["date"] >= baseline["source_date"]]
    if fld is None:
        return dated, []
    scoped = [u for u in dated if may_change(u, fld, rules)]
    agreeing = [u for u in scoped if agrees_with_current(u, fld, current or [], rules)]
    return [u for u in scoped if u not in agreeing], agreeing


def classified_that_matter(classified: list[dict], baseline: dict | None, fld: str) -> list[dict]:
    """Documents of a recognised type that may change the field beyond their kind (``classified_checks`` of the record,
    since v2.0.5) and are not older than the latest event document of the field - the criterion of DISC-005. Their
    scope is structural (a line no rule of the kind explains: every field; a holders' table of another kind: the
    shareholders) and does not depend on unread_document_scope."""
    out = []
    for c in classified:
        if baseline is not None and c["date"] < baseline["source_date"]:
            continue
        for m in c["fields_check"]["may_change"]:
            if m == "*" or m == fld or (m.endswith(".*") and fld.startswith(m[:-1])):
                out.append(c)
                break
    return out


def _stated_current(assertions: list[dict], rules: Rules) -> list[dict]:
    if not assertions:
        return []
    baseline, witnesses, _ = split_current(assertions, rules)
    return [a for a in ([baseline] if baseline else []) + witnesses if a["status"] == "STATED"]


def _form_code(text, rules: Rules, whole: bool) -> str | None:
    """The letters, lower case, of the legal form a text ends with (parameter legal_form_in_name); with ``whole``,
    only when the text is nothing but that legal form."""
    if not isinstance(text, str):
        return None
    m = rx(rules.param("discrepancy", "legal_form_in_name")).search(text)
    if not m or (whole and text[:m.start("form")].strip()):
        return None
    return re.sub(r"[^a-z]", "", m.group("form").lower())


def legal_form_clash(by_field: dict[str, list[dict]], rules: Rules) -> list[dict]:
    """Every pair (a current name, a current legal form) both read as stated, where the name ends with a legal form
    that is not the legal form stated (DISC-035, since v2.0.6). Nothing is reconciled: each pair is listed with the
    source of each reading."""
    if not rules.param("discrepancy", "legal_form_in_name"):
        return []
    out, seen = [], set()
    for n in sorted(_stated_current(by_field.get("name", []), rules), key=_order):
        code_n = _form_code(n["value"], rules, whole=False)
        if code_n is None:
            continue
        for f in sorted(_stated_current(by_field.get("legal_form", []), rules), key=_order):
            code_f = _form_code(f["value"], rules, whole=True)
            key = (n["source_doc"], n["line"], f["source_doc"], f["line"])
            if code_f is not None and code_f != code_n and key not in seen:
                seen.add(key)
                out.append({"name": n["value"], "name_source": _src(n),
                            "legal_form": f["value"], "legal_form_source": _src(f)})
    return out


def _clash_text(c: dict) -> str:
    n, f = c["name_source"], c["legal_form_source"]
    return (f"name {c['name']!r} ({n['source_doc']}, {n['edition']}, {n['source_date']}, line {n['line']}) against "
            f"legal form {c['legal_form']!r} ({f['source_doc']}, {f['edition']}, {f['source_date']}, line {f['line']})")


def resolve_field(fld: str, assertions: list[dict], rules: Rules, unread: list[dict] | None = None,
                  classified: list[dict] | None = None, clash: list[dict] | None = None) -> dict:
    baseline, witnesses, history = split_current(assertions, rules)
    current = ([baseline] if baseline else []) + witnesses
    stated = [a for a in current if a["status"] == "STATED"]
    groups: dict[str, list[dict]] = {}
    for a in stated:
        groups.setdefault(_key(a["value"]), []).append(a)
    blocking, agreeing = unread_that_matter(unread or [], baseline, rules, fld, current)
    open_docs = classified_that_matter(classified or [], baseline, fld)
    strict = rules.param("discrepancy", "unreadable_current_source_blocks_fact")
    facts = {"unread_document_may_change_field": bool(blocking),
             "classified_document_may_change_field": bool(open_docs),
             "no_current_assertion": not current,
             "two_or_more_current_values": len(groups) >= 2,
             "current_source_unreadable": len(stated) < len(current) and bool(strict or not groups),
             "legal_form_in_name_differs": bool(clash),
             "one_current_value": len(groups) == 1}
    rule = first_match(rules.discrepancy["rules"], lambda r: facts.get(r["when"], False)
                       and (not r.get("fields") or fld in r["fields"]))
    if rule is None:
        raise RuntimeError(f"discrepancy.json has no rule for field {fld}: {facts}")
    res: dict = {"field": fld, "status": rule["status"], "rule": rule["id"],
                 "unreadable": [dict(_src(a), reason=a["reason"]) for a in sorted(current, key=_order)
                                if a["status"] != "STATED"]}
    if agreeing:
        res["unread_agreeing"] = sorted(u.get("doc_id") or u["file"] for u in agreeing)
    if rule["status"] == "STATED":
        newest_first = sorted(stated, key=_order, reverse=True)
        res["value"] = newest_first[0]["value"]
        res["sources"] = [_src(a) for a in newest_first]
    else:
        cands = []
        for k in sorted(groups, key=lambda k: (min(_order(a) for a in groups[k]), k)):
            members = sorted(groups[k], key=_order)
            cands.append({"value": members[0]["value"], "sources": [_src(a) for a in members]})
        if rule["status"] == "DISCREPANCY":
            res["candidates"] = cands
        else:
            if rule["when"] == "unread_document_may_change_field":
                reasons = sorted(f"{u.get('doc_id') or 'a document without id'} dated "
                                 f"{u.get('date') or 'without a valid date'}" for u in blocking)
            elif rule["when"] == "classified_document_may_change_field":
                reasons = sorted(f"{c['doc_id']} dated {c['date']}" for c in open_docs)
            elif rule["when"] == "legal_form_in_name_differs":
                reasons = sorted(_clash_text(c) for c in clash or [])
                res["legal_form_clash"] = clash
            else:
                reasons = sorted({a["reason"] for a in current if a["status"] != "STATED"})
            res["reason"] = rule["reason"] + (": " + "; ".join(reasons) if reasons else "")
            res["readable"] = cands          # statements that could be read; not facts of the dossier
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
    unread = record.get("unclassified_documents", [])
    classified = record.get("classified_checks", [])
    clash = legal_form_clash(by_field, rules)
    fields = {f: resolve_field(f, by_field[f], rules, unread, classified, clash) for f in sorted(by_field)}
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
                            "new_edition": new["edition"], "since": h["superseded_by"]["source_date"],
                            "changed_by_doc": h["superseded_by"]["source_doc"],
                            "changed_by_edition": h["superseded_by"]["edition"]})
    return out


def run_inline_tests(rules: Rules) -> tuple[int, list[str]]:
    n, bad = 0, []

    def build(items: list[dict], fld: str) -> list[dict]:
        out = []
        for i, a in enumerate(items):
            no = a.get("edition_no", i + 1)
            x = {"field": fld, "role": a["role"], "series": a["series"], "edition_no": no,
                 "source_doc": a["doc"], "source_file": a["doc"], "source_date": a["date"],
                 "edition": f"{a['series']}/{no}", "line": a.get("line", 1), "line_end": a.get("line", 1),
                 "quote": "q", "nature": "resolved", "rule": "T"}
            if a["value"] is None:
                x["status"], x["reason"] = "TO_CONFIRM", "unreadable"
            else:
                x["status"], x["value"] = "STATED", a["value"]
            out.append(x)
        return out

    for r in rules.discrepancy["rules"]:
        for t in r.get("tests", []):
            n += 1
            fld = t.get("field", "f")
            assertions = build(t["assertions"], fld)
            # a test of the name and the legal form together names the assertions of the other field (DISC-035)
            by_field = {fld: assertions, **{k: build(v, k) for k, v in t.get("other_fields", {}).items()}}
            # a test of an option that is off by default names the parameter value it holds for
            local = rules_engine.with_params(rules, "discrepancy", t["params"]) if t.get("params") else rules
            got = resolve_field(fld, assertions, local, t.get("unread"), t.get("classified"),
                                legal_form_clash(by_field, local))
            exp = t["expect"]
            ok = got["status"] == exp["status"] and got["rule"] == r["id"]
            if "value" in exp:
                ok = ok and got.get("value") == exp["value"]
            if "values" in exp:
                ok = ok and sorted(c["value"] for c in got.get("candidates", [])) == sorted(exp["values"])
            if "historical" in exp:
                ok = ok and sorted(h["value"] for h in got["historical"]) == sorted(exp["historical"])
            if "sources" in exp:
                ok = ok and len(got.get("sources", [])) == exp["sources"]
            if "readable" in exp:
                ok = ok and sorted(c["value"] for c in got.get("readable", [])) == sorted(exp["readable"])
            if got["status"] != "STATED" and "value" in got:
                ok = False
            if not ok:
                bad.append(f"{r['id']}: got {got['status']} by {got['rule']}, expected {exp}")
    return n, bad
