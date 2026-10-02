"""Gold labels, computed from the document plan of ``world.py`` - never from the rendered text.

For every document the plan says what it states (``stated_fields``): a value, or ``None`` when the
plan made that place unreadable (illegible figure, amounts without a stated nature). The status of a
field is then the declared semantics of ``rules/discrepancy.json``, written here a second time and
independently of ``dossier/``:

* the latest event document that carries the field is the baseline;
* of each series of state documents only the latest edition counts, if not older than the baseline;
* two different readable current values -> DISCREPANCY; a current source that cannot be read ->
  TO_CONFIRM (the others are not promoted to fact); every current source readable and agreeing -> FACT.

Effective holdings come from ``reference_ownership.py`` (path enumeration).

Honest limit: generator, gold and extraction rules share an author; gold measures internal
consistency on synthetic data, not accuracy on real companies.
"""
from __future__ import annotations

import re
from fractions import Fraction

from . import reference_ownership as ref
from .world import ROLE, SLUGS, Doc, Entity, World

NATURES = ("resolved", "subscribed", "paid_in")
_SLUG_KIND = {v: k for k, v in SLUGS.items()}
_FILENAME = re.compile(r"^(\d{4}-\d{2}-\d{2})_([a-z-]+)(?:_([A-Za-z0-9-]+))?\.txt$")


def canon(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def parse_share_text(text: str) -> Fraction | None:
    """The exact share a plan entry states; None when the plan made it illegible."""
    t = text.strip()
    if "#" in t or "illegible" in t:
        return None
    if t.endswith("%"):
        return Fraction(t[:-1].replace(",", ".")) / 100
    return Fraction(t)


def _fin_value(text: str) -> str | None:
    if "#" in text or "illegible" in text:
        return None
    whole, frac = text.replace(".", "").split(",")
    return f"{int(whole)}.{frac}"


def stated_fields(doc: Doc) -> dict:
    """field -> canonical value, or None when the document carries the field but it cannot be read."""
    r = doc.render
    out: dict = {}
    if doc.kind in ("DEED", "EXTRACT"):
        out["name"], out["legal_form"] = r["name"], r["form"]
    if "office" in r:
        out["registered_office"] = r["office"]
    if "cap" in r:
        res, sub, paid = (canon(c) for c in r["cap"])
        style = r["cap_style"]
        bad = r.get("cap_illegible")
        if style in ("full", "res_full"):          # one amount stands for the three natures
            vals = (None, None, None) if bad else (res, res, res)
        elif style == "bare":                      # bare capital: read as resolved only [TO CONFIRM with legal]
            vals = (None if bad else res, None, None)
        elif style == "combined":
            vals = (res, sub, sub)
        elif style in ("split", "res_partial"):
            vals = (res, sub, paid)
        elif style == "ambiguous":                 # three amounts, no nature given
            vals = (None, None, None)
        elif style in ("partial_cues", "res_ambiguous"):
            vals = (res, None, None)
        else:
            raise ValueError(style)
        for nature, v in zip(NATURES, vals):
            out[f"share_capital.{nature}"] = None if bad == nature else v
    if "holders" in r:
        shares = [(h, parse_share_text(s)) for h, s in r["holders"]]
        if any(s is None for _, s in shares):
            out["shareholders"] = None             # one unreadable line: the whole table abstains
        else:
            out["shareholders"] = sorted(({"holder": h, "share": f"{s.numerator}/{s.denominator}"}
                                          for h, s in shares), key=lambda x: x["holder"])
    if "directors" in r:
        out["directors"] = sorted(r["directors"])
    if "fin" in r:
        for key, text in r["fin"].items():
            out[f"fin.FY{doc.fy}.{key}"] = _fin_value(text)
    return out


def resolve(entries: list[tuple[Doc, object]]) -> dict:
    """Status of one field from (document, stated value) pairs."""
    events = [e for e in entries if ROLE[e[0].kind] == "event"]
    baseline = max(events, key=lambda e: e[0].date) if events else None
    current = [baseline] if baseline else []
    for series in sorted({d.series for d, _ in entries if ROLE[d.kind] == "state"}):
        latest = max((e for e in entries if e[0].series == series), key=lambda e: (e[0].date, e[0].edition_no))
        if baseline is None or latest[0].date >= baseline[0].date:
            current.append(latest)
    values: list = []
    for _, v in current:
        if v is not None and v not in values:
            values.append(v)
    current_ids = {d.doc_id for d, _ in current}
    if len(values) >= 2:
        res = {"status": "DISCREPANCY", "values": values,
               "sources": sorted(d.doc_id for d, v in current if v is not None)}
    elif len(values) == 1 and all(v is not None for _, v in current):
        res = {"status": "FACT", "value": values[0],
               "sources": sorted(d.doc_id for d, v in current if v == values[0])}
    else:
        res = {"status": "TO_CONFIRM"}
    res["superseded"] = sorted(
        ({"old_value": v, "old_source_doc": d.doc_id} for d, v in entries
         if d.doc_id not in current_ids and v is not None and res["status"] == "FACT" and v != values[0]),
        key=lambda x: x["old_source_doc"])
    return res


def filename_divergences(doc: Doc) -> list[str]:
    """Aspects on which the file name (or folder) of a planned document contradicts its content."""
    out = []
    if doc.folder != doc.entity:
        out.append("folder")
    m = _FILENAME.match(doc.filename)
    if m:
        if m.group(1) != doc.date:
            out.append("date")
        if _SLUG_KIND.get(m.group(2)) not in (None, doc.kind):
            out.append("kind")
        detail = m.group(3) or ""
        if doc.kind == "APPOINTMENT" and re.fullmatch(r"P-\d{3}", detail) and detail not in doc.render["directors"]:
            out.append("appointee")
    return out


def entity_gold(ent: Entity, as_of: str) -> dict:
    docs = [d for d in ent.docs if d.date <= as_of]
    by_field: dict[str, list] = {}
    blocked = []
    for d in docs:
        for fld, value in stated_fields(d).items():
            by_field.setdefault(fld, []).append((d, value))
            if fld == "shareholders" and value is not None:
                total = sum((Fraction(r["share"]) for r in value), Fraction(0))
                if total != 1:
                    blocked.append({"source_doc": d.doc_id, "sum": f"{total.numerator}/{total.denominator}"})
    fields = {f: resolve(by_field[f]) for f in sorted(by_field)}
    return {"entity": ent.eid, "build": "BLOCKED" if blocked else "OK", "blocked_by": blocked,
            "fault": ent.fault + (f":{ent.variant}" if ent.variant else ""),
            "documents": len(docs), "fields": fields,
            "filename_divergences": sorted(({"doc_id": d.doc_id, "aspect": a} for d in docs
                                            for a in filename_divergences(d)),
                                           key=lambda x: (x["doc_id"], x["aspect"]))}


def world_gold(world: World) -> dict:
    ents = {eid: entity_gold(world.entities[eid], world.as_of) for eid in sorted(world.entities)}
    tables: dict[str, list | None] = {}
    for eid, g in ents.items():
        sh = g["fields"].get("shareholders", {"status": "TO_CONFIRM"})
        ok = g["build"] == "OK" and sh["status"] == "FACT"
        tables[eid] = [(r["holder"], Fraction(r["share"])) for r in sh["value"]] if ok else None
    for eid, g in ents.items():
        if g["build"] == "BLOCKED":
            g["ownership"] = {"outcome": "BLOCKED", "cycles": [], "effective": None}
            continue
        if tables[eid] is None:
            g["ownership"] = {"outcome": "TO_CONFIRM", "cycles": [], "effective": None}
            continue
        got = ref.effective_holdings(tables, eid)
        eff = got["effective"]
        g["ownership"] = {"outcome": got["outcome"], "cycles": ref.merged_cycles(got["cycles"]),
                          "effective": None if eff is None else {p: f"{s.numerator}/{s.denominator}"
                                                                 for p, s in eff.items()}}
    faults: dict[str, int] = {}
    for g in ents.values():
        faults[g["fault"].split(":")[0]] = faults.get(g["fault"].split(":")[0], 0) + 1
    return {"schema": "gold/2.0.0", "seed": world.seed, "as_of": world.as_of,
            "cycle_policy": "abstain", "entities": ents,
            "summary": {"entities": len(ents), "faults": dict(sorted(faults.items())),
                        "cross_holding_groups": len(world.cross_groups),
                        "blocked": sum(1 for g in ents.values() if g["build"] == "BLOCKED")}}
