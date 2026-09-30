"""Stage 7 - audit of what was built, read back from disk.

The audit does not trust the builder. It re-opens ``provenance.json`` and the DOCX and checks that

1. every figure has a value, a source document, a source date and an edition;
2. the cited document exists in the input, has the recorded SHA-256, and carries the quoted lines at
   the recorded line numbers; and the value is supported by the quote (re-read with a small parser
   of its own, not with the extraction rules);
3. a field shown as one value has no current source that says otherwise (a second, independent
   implementation of the rule declared in ``rules/discrepancy.json``);
4. every figure row of the DOCX matches its provenance entry, no row lacks a source, nothing marked
   ``[TO CONFIRM]`` carries a value, and no amount, percentage or fraction appears outside a table;
5. the cap table in the DOCX sums to exactly the whole.

Any problem makes the run FAILED and the dossier is not published.

``scan_outgoing`` is the scanner for outgoing documents that still carry a superseded value.
"""
from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

from docx import Document

from . import TO_CONFIRM
from .lib import jsonio
from .lib.numbers import parse_amount, parse_frac, parse_share
from .rules_engine import Rules, first_match, rx
from . import s6_build as b

_ORPHAN = re.compile(r"(EUR\s*[\d#\[])|(\d\s*%)|(\b\d+/\d+\b)")
_AMOUNT_IN_QUOTE = re.compile(r"EUR\s+((?:\d[\d., ]*\d)|\d)")
_SHARE_IN_LINE = re.compile(r"^\s*- (\S+) \(.*\): (.+)$")
FIGURE_SECTIONS = {"facts": b.H_FACTS, "discrepancies": b.H_DISC, "cap_table": b.H_CAP, "chain": b.H_CHAIN,
                   "history": b.H_HIST}


def _key(v) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


# ----------------------------------------------------------------------------------------------
# 2. value supported by the quoted source lines

def supported_by_quote(fig: dict) -> bool:
    quote, value, fld = fig.get("quote") or "", fig["value"], fig["field"]
    if fig["section"] in ("cap_table", "chain"):
        return _holder_lines(quote).get(fig["holder"]) == parse_frac(value)
    if fld == "shareholders":
        return _holder_lines(quote) == {r["holder"]: parse_frac(r["share"]) for r in value}
    if fld == "directors":
        ids = re.findall(r"^\s*- (P-\d{3}) ", quote, flags=re.M)
        return sorted(ids) == sorted(value)
    if isinstance(value, str) and re.fullmatch(r"\d+\.\d{2}", value) and (
            fld.startswith(("share_capital", "fin."))):
        return value in {parse_amount(t)[0] for t in _AMOUNT_IN_QUOTE.findall(quote)}
    return isinstance(value, str) and value in quote


def _holder_lines(quote: str) -> dict[str, Fraction]:
    out: dict[str, Fraction] = {}
    for line in quote.split("\n"):
        m = _SHARE_IN_LINE.match(line)
        if m:
            share, _ = parse_share(m.group(2))
            if share is not None:
                out[m.group(1)] = share
    return out


# ----------------------------------------------------------------------------------------------
# 3. independent re-derivation of the current values of a field

def current_values(assertions: list[dict]) -> tuple[set[str], bool]:
    """(distinct readable current values, whether any current source exists) for one field."""
    events = [a for a in assertions if a["role"] == "event"]
    cutoff = max((a["source_date"] for a in events), default="")
    current = []
    if events:
        current.append(max(events, key=lambda a: (a["source_date"], a["edition_no"] or 0, a["source_doc"])))
    for series in {a["series"] for a in assertions if a["role"] == "state"}:
        latest = max((a for a in assertions if a["role"] == "state" and a["series"] == series),
                     key=lambda a: (a["source_date"], a["edition_no"] or 0, a["source_doc"]))
        if latest["source_date"] >= cutoff:
            current.append(latest)
    return {_key(a["value"]) for a in current if a["status"] == "STATED"}, bool(current)


# ----------------------------------------------------------------------------------------------
# 4. the DOCX, read back

def read_docx(path: Path) -> dict:
    doc = Document(str(path))
    tables: dict[str, list[list[str]]] = {}
    for t in doc.tables:
        rows = [[c.text for c in r.cells] for r in t.rows]
        tables.setdefault("|".join(rows[0]), []).extend(rows[1:])
    paragraphs = [p.text for p in doc.paragraphs]
    for s in doc.sections:
        paragraphs.extend(p.text for p in s.header.paragraphs)
        paragraphs.extend(p.text for p in s.footer.paragraphs)
    return {"tables": tables, "paragraphs": paragraphs}


def audit_dossier(dossier_dir: Path | str, input_dir: Path | str, record: dict | None = None,
                  names: tuple[str, str] = ("dossier.docx", "provenance.json")) -> dict:
    d = Path(dossier_dir)
    problems: list[str] = []
    prov = jsonio.load(d / names[1])
    figures = prov["figures"]
    docs = {x["doc_id"]: x for x in prov["documents"]}
    docs.update(prov.get("upstream_documents", {}))
    sourced = 0
    cache: dict[str, tuple[str, list[str]]] = {}
    for f in figures:
        if any(f.get(k) in (None, "", []) for k in ("value", "source_doc", "source_date", "edition")):
            problems.append(f"{f.get('id')}: figure without value, source document, date or edition")
            continue
        sourced += 1
        meta = docs.get(f["source_doc"])
        if meta is None:
            problems.append(f"{f['id']}: source {f['source_doc']} is not a document of the record")
            continue
        if f["source_date"] != meta["date"] or f["edition"] != meta["edition"]:
            problems.append(f"{f['id']}: date or edition differs from the source document's own")
        if f["source_file"] not in cache:
            path = Path(input_dir) / f["source_file"]
            if not path.exists():
                problems.append(f"{f['id']}: source file of {f['source_doc']} not found")
                continue
            data = jsonio.read_bytes(path)
            cache[f["source_file"]] = (jsonio.sha256_bytes(data), data.decode("utf-8").replace("\r\n", "\n").split("\n"))
        sha, lines = cache[f["source_file"]]
        if sha != meta["sha256"]:
            problems.append(f"{f['id']}: source {f['source_doc']} changed since the record was built")
        if "\n".join(lines[f["line"] - 1:f["line_end"]]) != f["quote"]:
            problems.append(f"{f['id']}: quoted lines are not in {f['source_doc']} at lines {f['line']}-{f['line_end']}")
        elif not supported_by_quote(f):
            problems.append(f"{f['id']}: value {f['display']} is not supported by the quoted source lines")
        if f["display"] != b.display("share" if f["section"] in ("cap_table", "chain") else _display_field(f), f["value"]):
            problems.append(f"{f['id']}: displayed text does not match the value")

    for t in prov["to_confirm"]:
        if "value" in t or t.get("marker") != TO_CONFIRM:
            problems.append(f"{t['field']}: a field to confirm carries a value")
        if any(f["field"] == t["field"] and f["section"] in ("facts", "cap_table") for f in figures):
            problems.append(f"{t['field']}: shown both as a fact and as to confirm")

    if record is not None:
        by_field: dict[str, list[dict]] = {}
        for a in record["assertions"]:
            if not a["field"].endswith(".previous"):
                by_field.setdefault(a["field"], []).append(a)
        for fld, assertions in sorted(by_field.items()):
            values, any_current = current_values(assertions)
            shown = [f for f in figures if f["field"] == fld and f["section"] in ("facts", "cap_table")]
            disc = {_key(f["value"]) for f in figures if f["field"] == fld and f["section"] == "discrepancies"}
            if len(values) >= 2:
                if shown:
                    problems.append(f"{fld}: sources disagree but one value is shown as fact")
                if disc != values:
                    problems.append(f"{fld}: not every conflicting value is shown side by side")
            elif len(values) == 1:
                if fld == "shareholders" and shown:
                    table = sorted(({"holder": f["holder"], "share": f["value"]} for f in shown),
                                   key=lambda r: r["holder"])
                    if _key(table) not in values:
                        problems.append("shareholders: the table shown is not the one the current sources state")
                elif shown and _key(shown[0]["value"]) not in values:
                    problems.append(f"{fld}: the value shown is not the one the current sources state")
                if not shown:
                    problems.append(f"{fld}: a readable current value is not shown")
            elif shown:
                problems.append(f"{fld}: a value is shown but no current source could be read")

    # the DOCX
    got = read_docx(d / names[0])
    by_id = {f["id"]: f for f in figures}
    seen_ids: set[str] = set()
    for section, header in FIGURE_SECTIONS.items():
        for row in got["tables"].get("|".join(header), []):
            if section == "cap_table" and row[0] == "" and row[1] == "Sum":
                continue
            f = by_id.get(row[0])
            if f is None or f["section"] != section:
                problems.append(f"DOCX row {row[0]!r} in {section} has no provenance entry")
                continue
            seen_ids.add(row[0])
            if row[-3:] != [f["source_doc"], f["source_date"], f["edition"]] or not all(row[-3:]):
                problems.append(f"{f['id']}: DOCX row lacks or alters the source, date or edition")
            if f["display"] not in row:
                problems.append(f"{f['id']}: DOCX value differs from provenance")
    missing = sorted(set(by_id) - seen_ids)
    if missing:
        problems.append(f"{len(missing)} provenance figure(s) are not in the DOCX: {missing[:5]}")
    for row in got["tables"].get("|".join(b.H_TOCONFIRM), []):
        if row[1] != TO_CONFIRM:
            problems.append(f"{row[0]}: the to-confirm row does not carry the marker")
    cap_rows = [r for r in got["tables"].get("|".join(b.H_CAP), []) if r[0]]
    if cap_rows:
        total = sum((parse_frac(r[2].split(" ")[0]) for r in cap_rows), Fraction(0))
        if total != 1:
            problems.append(f"the cap table in the DOCX sums to {total}, not to the whole")
    for p in got["paragraphs"]:
        if _ORPHAN.search(p):
            problems.append(f"figure outside a sourced table: {p[:80]!r}")
    return {"ok": not problems, "figures_total": len(figures), "figures_with_source": sourced,
            "derived_total": len(prov["derived"]), "to_confirm_total": len(prov["to_confirm"]),
            "problems": problems}


def _display_field(f: dict) -> str:
    if f["section"] == "history" and f["field"] == "share_capital":
        return "share_capital."
    return f["field"]


# ----------------------------------------------------------------------------------------------
# outgoing documents that still carry a superseded value

_DOC_DATE = re.compile(r"^(?:Document date|Date):\s*(\d{4}-\d{2}-\d{2})\s*$", re.M)


def _amounts_in(line: str, currency: str) -> list[tuple[int, str]]:
    """(position, canonical amount) of every currency amount in a line, whatever its format."""
    out = []
    num = r"\d[\d., ]*\d|\d"
    for m in re.finditer(rf"(?:{currency})\s*({num})|({num})\s*(?:{currency})", line, flags=re.I):
        token = (m.group(1) or m.group(2)).strip(" .,")
        value, _ = parse_amount(token)
        if value is None and re.fullmatch(r"\d{1,3}(\.\d{3})+", token):   # 50.000 next to a currency marker
            value = f"{int(token.replace('.', ''))}.00"
        if value is not None:
            out.append((m.start(), value))
    return out


def scan_outgoing(outgoing_dir: Path | str, superseded: list[dict], entity_names: dict[str, str],
                  target: str, rules: Rules) -> dict:
    """Find, in outgoing text documents, amounts of the target entity that were superseded.

    ``superseded`` is the register of stage 3; ``entity_names`` maps entity id -> name without legal form.
    """
    cfg = rules.discrepancy["outgoing_scan"]
    p = cfg["parameters"]
    lookback = int(p["entity_lookback_lines"])
    findings, ignored = [], []
    root = Path(outgoing_dir)
    files = sorted(f for f in root.rglob("*") if f.is_file() and f.suffix.lower() in (".txt", ".md"))
    for f in files:
        rel = f.relative_to(root).as_posix()
        text = jsonio.read_text(f).replace("\r\n", "\n")
        lines = text.split("\n")
        m = _DOC_DATE.search(text)
        doc_date = m.group(1) if m else ""
        for entry in superseded:
            field_root = entry["field"].split(".")[0]
            cue = p["field_cues"].get(field_root)
            if cue is None or not isinstance(entry["old_value"], str):
                continue
            for no, line in enumerate(lines, 1):
                for pos, value in _amounts_in(line, p["currency_markers"]):
                    if value != entry["old_value"]:
                        continue
                    nearest = _nearest_entity(lines, no, pos, entity_names, lookback)
                    facts = {
                        "document_dated_before_change": bool(doc_date) and doc_date < entry["since"],
                        "no_field_cue_in_line": not rx(cue).search(line),
                        "historical_marker_before_amount": False,
                        "line_is_about_another_entity": nearest is not None and nearest != target,
                        "line_is_not_about_the_entity": nearest is None,
                        "always": True,
                    }
                    rule = first_match(cfg["rules"], lambda r: _scan_fact(r, facts, line[:pos]))
                    hit = {"file": rel, "line": no, "text": line.strip(), "field": field_root,
                           "old_value": entry["old_value"], "new_value": entry["new_value"],
                           "new_edition": entry["new_edition"], "new_source_doc": entry["new_source_doc"],
                           "rule": rule["id"]}
                    (findings if rule["action"] == "flag" else ignored).append(hit)
    uniq = {(h["file"], h["line"]): h for h in findings}
    return {"files_scanned": len(files), "findings": [uniq[k] for k in sorted(uniq)],
            "ignored": sorted(ignored, key=lambda h: (h["file"], h["line"], h["rule"]))}


def _scan_fact(rule: dict, facts: dict, before_amount: str) -> bool:
    if rule["when"] == "historical_marker_before_amount":
        return rx(rule["pattern"]).search(before_amount) is not None
    return facts[rule["when"]]


def _nearest_entity(lines: list[str], no: int, pos: int, names: dict[str, str], lookback: int) -> str | None:
    """The entity named closest before the amount: in the line itself, else in the lines just above."""
    best: tuple[int, str] | None = None
    line = lines[no - 1]
    for eid, name in names.items():
        for m in re.finditer(re.escape(name), line, flags=re.I):
            dist = abs(pos - m.start())
            if best is None or dist < best[0]:
                best = (dist, eid)
    if best:
        return best[1]
    for back in range(1, lookback + 1):
        if no - 1 - back < 0:
            break
        found = [eid for eid, name in names.items() if re.search(re.escape(name), lines[no - 1 - back], flags=re.I)]
        if len(found) == 1:
            return found[0]
        if found:
            return None
    return None


def run_scan_tests(rules: Rules) -> tuple[int, list[str]]:
    """Inline tests of the outgoing-scan guards."""
    n, bad = 0, []
    cfg = rules.discrepancy["outgoing_scan"]
    entry = {"field": "share_capital.resolved", "old_value": "50000.00", "new_value": "80000.00",
             "new_edition": "RESOLUTION/1", "new_source_doc": "DOC-T", "since": "2026-01-15"}
    names = {"E-0001": "Fornace Aurelia", "E-0002": "Holding Aurelia Partecipazioni"}
    for r in cfg["rules"]:
        for t in r.get("tests", []):
            n += 1
            lines = t["text"].split("\n")
            doc_date = t.get("doc_date", "")
            got = None
            for no, line in enumerate(lines, 1):
                for pos, value in _amounts_in(line, cfg["parameters"]["currency_markers"]):
                    if value != entry["old_value"]:
                        continue
                    nearest = _nearest_entity(lines, no, pos, names, int(cfg["parameters"]["entity_lookback_lines"]))
                    facts = {"document_dated_before_change": bool(doc_date) and doc_date < entry["since"],
                             "no_field_cue_in_line": not rx(cfg["parameters"]["field_cues"]["share_capital"]).search(line),
                             "historical_marker_before_amount": False,
                             "line_is_about_another_entity": nearest is not None and nearest != "E-0001",
                             "line_is_not_about_the_entity": nearest is None, "always": True}
                    got = first_match(cfg["rules"], lambda x: _scan_fact(x, facts, line[:pos]))["id"]
            if got != r["id"]:
                bad.append(f"{r['id']}: test text decided by {got}")
    return n, bad
