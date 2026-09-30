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
from . import rules_engine
from .rules_engine import Rules, first_match, rx
from . import s6_build as b

_ORPHAN = re.compile(r"(EUR\s*[\d#\[])|(\d\s*%)|(\b\d+/\d+\b)")
# The audit's own reading of an amount in a quote (not the extraction rules): the whole run of digits and of
# any character that may group digits, so that a figure is never cut short at a separator (finding T16).
_GROUPING = r"(?:[.,'’‘ʼ′´`]|[^\S\n])"
_DIGIT_RUN = rf"\d(?:\d|{_GROUPING}(?=\d))*"
_AMOUNT_IN_QUOTE = re.compile(
    rf"(?<![A-Za-z])EUR\s+({_DIGIT_RUN})"
    rf"(?!{_GROUPING}+[\d#]|[\dA-Za-z#]|\s*(?:thousand|million|billion|k|m|bn|mn|mln|mio|mrd)(?![A-Za-z]))", re.I)
# The audit's own reading of a list line (v2.0.3, D30): a list marker (dash, bullet, number, letter, roman
# numeral) or none; the identifier first with an optional label in parentheses, or a name first with the
# identifier in parentheses; then a colon, tab, bar, spaced dash or space, and the share.
_MARK = r"(?:[-*•–—·]|\(?\d{1,3}[.)]|\(\d{1,3}\)|\(?[a-z][.)]|\([a-z]\)|\(?[ivx]{1,5}[.)]|\([ivx]{1,5}\))"
_HOLDER = r"(?:(P-\d{3}|E-\d{4})(?:\s*\([^()]*\))?|[^()|:\t]+?\s*\((P-\d{3}|E-\d{4})\))"
_SHARE_IN_LINE = re.compile(rf"^\s*(?:{_MARK}\s+)?{_HOLDER}\s*(?::|\t|\||\s[-–—]\s|\s)\s*(\S.*?)\s*$", re.I)
_PERSON_LINE = re.compile(rf"^\s*(?:{_MARK}\s+)?(?:(P-\d{{3}})(?:\s*\([^()]*\))?|[^()|:\t]+?\s*\((P-\d{{3}})\))\s*$",
                          re.I)
_COUNT_IN_LINE = re.compile(r"^(\d{1,3}(?:[.,'’ ]\d{3})+|\d+)\s+(?:(?:ordinary|registered)\s+)?(?:quotas?|shares?)$",
                            re.I)
_TOTAL_IN_LINE = re.compile(r"(?<![\d.,'’])(\d{1,3}(?:[.,'’ ]\d{3})+|\d+)\s+(?:(?:ordinary|registered|equal)\s+)?"
                            r"(?:quotas|shares)\b", re.I)
FIGURE_SECTIONS = {"facts": b.H_FACTS, "discrepancies": b.H_DISC, "unconfirmed": b.H_UNCONF,
                   "cap_table": b.H_CAP, "chain": b.H_CHAIN, "history": b.H_HIST}
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


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
        ids = [m.group(1) or m.group(2) for m in map(_PERSON_LINE.match, quote.split("\n")[1:]) if m]
        return sorted(ids) == sorted(value)
    if isinstance(value, str) and re.fullmatch(r"\d+\.\d{2}", value) and (
            fld.startswith(("share_capital", "fin."))):
        return any(parse_amount(t)[0] == value and _same_digits(t, value) for t in _AMOUNT_IN_QUOTE.findall(quote))
    return isinstance(value, str) and value in quote


def _same_digits(token: str, value: str) -> bool:
    """Every digit of the quoted figure is in the value, in order: no group was dropped or added."""
    written = re.sub(r"\D", "", token)
    return value.replace(".", "") in (written, written + "00")


def _holder_lines(quote: str) -> dict[str, Fraction]:
    """Every holder line of the quote with its share. Numbers of quotas or shares are shares only through the one
    total the other lines of the quote state; a quote that mixes them with shares, or states no single total, gives
    a table that cannot match (the audit then fails the dossier)."""
    out: dict[str, Fraction] = {}
    counts: dict[str, int] = {}
    others: list[str] = []
    for line in quote.split("\n"):
        m = _SHARE_IN_LINE.match(line)
        hid = (m.group(1) or m.group(2)) if m else None
        share = parse_share(m.group(3))[0] if m else None
        count = _COUNT_IN_LINE.match(m.group(3).strip()) if m and share is None else None
        if share is not None:
            out[hid] = share
        elif count:
            counts[hid] = int(re.sub(r"\D", "", count.group(1)))
        else:
            others.append(line)
    if counts:
        totals = {int(re.sub(r"\D", "", t)) for line in others for t in _TOTAL_IN_LINE.findall(line)}
        if out or len(totals) != 1 or 0 in totals:
            return {"": Fraction(-1)}
        total = totals.pop()
        out = {h: Fraction(n, total) for h, n in counts.items()}
    return out


# ----------------------------------------------------------------------------------------------
# 3. independent re-derivation of the current values of a field

def current_values(assertions: list[dict]) -> tuple[set[str], bool, bool, str]:
    """(distinct readable current values, any current source?, any unreadable current source?, date of
    the latest event document) for one field."""
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
    return ({_key(a["value"]) for a in current if a["status"] == "STATED"}, bool(current),
            any(a["status"] != "STATED" for a in current), cutoff)


def _expand_all(pattern: str, params: dict) -> str:
    """Substitute every ``{name}`` of the rule parameters, until none is left (the audit's own expansion)."""
    for _ in range(5):
        new = re.sub(r"\{([a-z_]+)\}", lambda m: params[m.group(1)] if isinstance(params.get(m.group(1)), str)
                     else m.group(0), pattern)
        if new == pattern:
            break
        pattern = new
    return pattern


def unread_scope(u: dict, input_dir: Path | str, rules: Rules | None) -> tuple[set[str], list[dict]]:
    """(fields an unread document may change, holders' tables of it re-read by the audit), read again from the
    source by the audit: a second implementation of rules/discrepancy.json unread_document_scope over
    rules/extract.json unread_fields and holders_evidence. ``{"*"}`` is every field."""
    every = ({"*"}, [])
    if rules is None or rules.param("discrepancy", "unread_document_scope") != "fields_it_may_state":
        return every
    reason = u.get("reason") or ""
    if not reason.startswith("document type not recognised") or "; " in reason:
        return every                      # another problem of the header: any field
    path = Path(input_dir) / u["file"]
    if not path.exists():
        return every
    lines = jsonio.read_bytes(path).decode("utf-8").replace("\r\n", "\n").split("\n")
    start = next((i for i in range(1, len(lines)) if not lines[i].strip()), len(lines))
    skip: set[int] = set()
    tables = []
    hc = u.get("holders_check") or {}
    for t in hc.get("tables") or [] if hc.get("status") == "read" else []:
        rows = lines[t["line"]:t["line_end"]]          # the lines after the heading, 0-based t["line"] is next
        got = _holder_lines("\n".join(lines[t["line"] - 1:t["line_end"]]))
        want = {r["holder"]: parse_frac(r["share"]) for r in t["value"]}
        if t["line"] > start and rows and all(_SHARE_IN_LINE.match(x) for x in rows) and got == want:
            skip.update(range(t["line"], t["line_end"] + 1))
            tables.append(t["value"])
    p = rules.extract["parameters"]
    fev = rules.extract["unread_fields"]["rules"]
    hev = rules.extract["holders_evidence"]
    neutral = rx(_expand_all(hev["parameters"]["neutral_phrases"], p))
    fields: set[str] = set()
    holders = False
    for no in range(start + 1, len(lines) + 1):
        text = lines[no - 1]
        if no in skip or not text.strip():
            continue
        topics = [r for r in fev if r["when"] == "topic" and rx(_expand_all(r["pattern"], p)).search(text)]
        if not topics:
            topics = [next(r for r in fev if r["when"] != "topic" and (
                r["when"] == "always" or rx(_expand_all(r["pattern"], p)).search(text)))]
        for r in topics:
            fields.update(r["fields"])
        plain = neutral.sub(" ", text)
        hit = next(r for r in hev["rules"] if r["when"] == "always" or rx(_expand_all(r["pattern"], p)).search(plain))
        holders = holders or hit["outcome"] != "none"
    if holders or tables or hc.get("status") != "no_table":
        fields.add("shareholders")
    return ({"*"} if "*" in fields else fields), tables


def _in_scope(scope: set[str], fld: str) -> bool:
    return any(m == "*" or m == fld or (m.endswith(".*") and fld.startswith(m[:-1])) for m in scope)


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
                  names: tuple[str, str] = ("dossier.docx", "provenance.json"), rules: Rules | None = None) -> dict:
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
        if rules is None:
            rules = rules_engine.load()
        scopes = [(u, *unread_scope(u, input_dir, rules)) for u in record.get("unclassified_documents", [])]
        for fld, assertions in sorted(by_field.items()):
            values, any_current, unreadable, cutoff = current_values(assertions)
            shown = [f for f in figures if f["field"] == fld and f["section"] in ("facts", "cap_table")]
            disc = {_key(f["value"]) for f in figures if f["field"] == fld and f["section"] == "discrepancies"}
            unread = []
            for u, scope, tables in scopes:
                if cutoff and _ISO_DATE.fullmatch(u.get("date") or "") and u["date"] < cutoff:
                    continue
                if not _in_scope(scope, fld):
                    continue
                if (fld == "shareholders" and len(tables) == 1 and len(values) == 1 and not unreadable
                        and _key(sorted(tables[0], key=lambda r: r["holder"])) in values):
                    continue                  # its table, re-read by the audit, is the one current table
                unread.append(u)
            if unread:
                if shown or disc:
                    problems.append(f"{fld}: shown as fact or as a conflict although an unread document may change it")
            elif len(values) >= 2:
                if shown:
                    problems.append(f"{fld}: sources disagree but one value is shown as fact")
                if disc != values:
                    problems.append(f"{fld}: not every conflicting value is shown side by side")
            elif unreadable:
                if shown:
                    problems.append(f"{fld}: a value is shown as fact although a current source could not be read")
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
    num = _DIGIT_RUN
    for m in re.finditer(rf"(?<![A-Za-z])(?:{currency})\s*({num})|({num})\s*(?:{currency})", line, flags=re.I):
        token = (m.group(1) or m.group(2)).strip(" .,")
        value, _ = parse_amount(token)
        if value is None and re.fullmatch(r"\d{1,3}(\.\d{3})+", token):   # 50.000 next to a currency marker
            value = f"{int(token.replace('.', ''))}.00"
        if value is not None:
            out.append((m.start(), value))
    return out


def _has_cue(line: str, field_root: str, params: dict) -> bool:
    """The cue of the field is in the line, outside the expressions that only look like it."""
    excluded = params.get("field_cue_exclusions", {}).get(field_root)
    if excluded:
        line = rx(excluded).sub(" ", line)
    return rx(params["field_cues"][field_root]).search(line) is not None


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
                        "no_field_cue_in_line": not _has_cue(line, field_root, p),
                        "historical_marker_before_amount": False,
                        "line_is_about_another_entity": nearest is not None and nearest != target,
                        "line_is_not_about_the_entity": nearest is None,
                        "always": True,
                    }
                    rule = first_match(cfg["rules"], lambda r: _scan_fact(r, facts, line[:pos]))
                    hit = {"file": rel, "line": no, "text": line.strip(), "field": field_root,
                           "old_value": entry["old_value"], "new_value": entry["new_value"],
                           "new_edition": entry["new_edition"], "new_source_doc": entry["new_source_doc"],
                           "changed_on": entry["since"], "changed_by_doc": entry.get("changed_by_doc", ""),
                           "changed_by_edition": entry.get("changed_by_edition", ""), "rule": rule["id"]}
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
                             "no_field_cue_in_line": not _has_cue(line, "share_capital", cfg["parameters"]),
                             "historical_marker_before_amount": False,
                             "line_is_about_another_entity": nearest is not None and nearest != "E-0001",
                             "line_is_not_about_the_entity": nearest is None, "always": True}
                    got = first_match(cfg["rules"], lambda x: _scan_fact(x, facts, line[:pos]))["id"]
            if got != r["id"]:
                bad.append(f"{r['id']}: test text decided by {got}")
    return n, bad
