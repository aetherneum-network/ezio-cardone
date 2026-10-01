"""Stage 7 - audit of what was built, read back from disk.

The audit does not trust the builder. It re-opens ``provenance.json`` and the DOCX and checks that

1. every figure has a value, a source document, a source date and an edition;
2. the cited document exists in the input, has the recorded SHA-256, and carries the quoted lines at
   the recorded line numbers; and the value is supported by the quote (re-read with a small parser
   of its own, not with the extraction rules);
3. a field shown as one value has no current source that says otherwise (a second, independent
   implementation of the rule declared in ``rules/discrepancy.json``), and no document - of unrecognised type, or
   (since v2.0.5, D34) of a recognised type with a line that no rule of its kind reads, every body line read again
   by the audit - that may change it;
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
# v2.0.4 (D30b): dot leaders as a separator ('P-014 (Pia Mendaci) ...... 50%'), a share before the holder
# ('- 60% P-002 (Bruno Simulanti)', per cent or n/d only), and a last line 'Total' that must equal the exact sum.
_SEP = r"(?::|\t|\||\s[-–—]\s|\s*\.{3,}\s*|\s)"
_SHARE_IN_LINE = re.compile(rf"^\s*(?:{_MARK}\s+)?{_HOLDER}\s*{_SEP}\s*([^\s.].*?)\s*$", re.I)
_SHARE_FIRST_LINE = re.compile(rf"^\s*(?:{_MARK}\s+)?(\d{{1,3}}(?:[.,]\d+)?\s*(?:%|per\s*-?\s*cent|percent|pct)"
                               rf"|\d+\s*/\s*[1-9]\d*)\s*{_SEP}\s*{_HOLDER}\s*$", re.I)
_TOTAL_LINE = re.compile(rf"^\s*(?:{_MARK}\s+)?(?:the\s+)?total\s*{_SEP}\s*([^\s.].*?)\s*$", re.I)
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
    lines = [x for x in quote.split("\n") if x.strip()]
    stated = None
    if lines and _TOTAL_LINE.match(lines[-1]):
        stated = _TOTAL_LINE.match(lines[-1]).group(1)
        lines = lines[:-1]
    for line in lines:
        m = _SHARE_IN_LINE.match(line)
        hid = (m.group(1) or m.group(2)) if m else None
        share = parse_share(m.group(3))[0] if m else None
        count = _COUNT_IN_LINE.match(m.group(3).strip()) if m and share is None else None
        f = _SHARE_FIRST_LINE.match(line) if share is None and not count else None
        if f:
            hid, share = f.group(2) or f.group(3), parse_share(f.group(1))[0]
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
        if stated is not None:
            c = _COUNT_IN_LINE.match(stated.strip())
            if not c or Fraction(int(re.sub(r"\D", "", c.group(1))), total) != sum(out.values(), Fraction(0)):
                return {"": Fraction(-1)}
    elif stated is not None and parse_share(stated)[0] != sum(out.values(), Fraction(0)):
        return {"": Fraction(-1)}                      # a Total that is not the exact sum of the rows
    return out


def _is_holder_row(line: str) -> bool:
    return bool(_SHARE_IN_LINE.match(line) or _SHARE_FIRST_LINE.match(line) or _TOTAL_LINE.match(line))


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
    for _ in range(8):
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
        if t["line"] > start and rows and all(_is_holder_row(x) for x in rows) and got == want:
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
# 3b. documents of a recognised type, every body line read again (v2.0.5, D34)

# The audit's own reading of the name beside an identifier in a list line.
_LABEL_AFTER = re.compile(r"(?:P-\d{3}|E-\d{4})\s*\(([^()]*)\)")
_LABEL_BEFORE = re.compile(rf"^\s*(?:{_MARK}\s+)?([^()|:\t]+?)\s*\((?:P-\d{{3}}|E-\d{{4}})\)")
_FY_HEADER = re.compile(r"^Financial year:\s*(\d{4})\s*$")


def _topic_of(fld: str) -> str:
    return "share_capital.*" if fld.startswith("share_capital.") else "fin.*" if fld.startswith("fin.") else fld


class _Words:
    """The audit's own test of free words: the fields they may name, by the rules that judge a document of
    unrecognised type (the topic rules of unread_fields, and holders_evidence for a holding). Figures are
    removed first: a slot's figures are typed by its grammar."""

    def __init__(self, rules: Rules):
        p = rules.extract["parameters"]
        self.topics = [(rx(_expand_all(r["pattern"], p)), r["fields"]) for r in rules.extract["unread_fields"]["rules"]
                       if r["when"] == "topic"]
        hev = rules.extract["holders_evidence"]
        self.neutral = rx(_expand_all(hev["parameters"]["neutral_phrases"], p))
        self.hev = [(None if r["when"] == "always" else rx(_expand_all(r["pattern"], p)), r["outcome"])
                    for r in hev["rules"]]

    def holding(self, text: str) -> bool:
        plain = self.neutral.sub(" ", text)
        return next(out for pat, out in self.hev if pat is None or pat.search(plain)) != "none"

    def name(self, text: str) -> set[str]:
        words = re.sub(r"[0-9]", " ", text)
        out = {f for pat, fields in self.topics if pat.search(words) for f in fields}
        if self.holding(words):
            out.add("shareholders")
        return out


def _list_row(line: str, fld: str, words: _Words, unread_share: re.Pattern) -> bool:
    """A line of a list by the audit's own grammar: a director, or a holder (or the Total) whose share is read as a
    share or a number, or is a figure without words; the name beside the identifier has no figure and names
    nothing but a name, a legal form or the field of the list."""
    if fld == "directors":
        if not _PERSON_LINE.match(line):
            return False
        rest = line
    else:
        m, f, t = _SHARE_IN_LINE.match(line), _SHARE_FIRST_LINE.match(line), _TOTAL_LINE.match(line)
        if m:
            share, rest = m.group(3), line[:m.start(3)]
        elif f:
            share, rest = f.group(1), re.sub(r"^[\s:|\-–—.]+", "", line[f.end(1):])
        elif t:
            share, rest = t.group(1), ""
        else:
            return False
        share = share.strip()
        if not share or (parse_share(share)[0] is None and not _COUNT_IN_LINE.match(share)
                         and not unread_share.fullmatch(share)):
            return False
    labels = [x.group(1) for x in _LABEL_AFTER.finditer(rest)]
    before = _LABEL_BEFORE.match(rest)
    if before:
        labels.append(before.group(1))
    return all(not re.search(r"[0-9]", x) and words.name(x) <= {"name", "legal_form", _topic_of(fld)} for x in labels)


def classified_scope(d: dict, record: dict, input_dir: Path | str, rules: Rules,
                     words: _Words | None = None) -> dict:
    """What one document of a recognised type may change beyond the fields its rules read, read again from the
    source by the audit: a second implementation of rules/extract.json classified_lines over the assertions of the
    record. A body line is closed when it has no letter or digit; when it is a line of a list (a heading of a list
    rule - holders in every kind, directors in the kinds of their rule - or a row of the audit's own grammar after
    it); when it is the whole of a shape of its kind whose free words name only the fields of the shape; or when it is
    a label and a typed value (CLS-250) whose label names fields of its kind only, and the fields both the label and
    the type of the value name. A closed line whose field is not read from it (no assertion of the record covers it,
    or its kind does not read the field) may change that field; any other line, every field ("*")."""
    path = Path(input_dir) / d["file"]
    out = {"scope": set(), "open": [], "restated": set(), "holding": False, "problems": []}
    if not path.exists():
        out["scope"], out["problems"] = {"*"}, [f"{d['doc_id']}: source file not found"]
        return out
    words = words or _Words(rules)
    p = rules.extract["parameters"]
    lines = jsonio.read_bytes(path).decode("utf-8").replace("\r\n", "\n").split("\n")
    start = next((i for i in range(1, len(lines)) if not lines[i].strip()), len(lines))
    fy = next((m.group(1) for x in lines[1:start] for m in [_FY_HEADER.match(x.strip())] if m), "")
    kind = d["kind"]
    expected = {t.replace("{fy}", fy) for t in rules.extract["expected_fields"][kind]}
    spans: dict[str, list[tuple[int, int]]] = {}
    for a in record["assertions"]:
        if (a["source_doc"] == d["doc_id"] and a["source_file"] == d["file"] and a["line"] is not None
                and not a["field"].endswith(".previous")):
            spans.setdefault(a["field"], []).append((a["line"], a["line_end"]))
    check = next((c for c in record.get("classified_checks", []) if c["doc_id"] == d["doc_id"]
                  and c["file"] == d["file"]), None)
    hc = (check or {}).get("holders_check") or {}
    for t in hc.get("tables") or [] if hc.get("status") == "read" else []:
        if _holder_lines("\n".join(lines[t["line"] - 1:t["line_end"]])) != {
                r["holder"]: parse_frac(r["share"]) for r in t["value"]}:
            out["problems"].append(f"{d['doc_id']}: the holders' table at line {t['line']} is not the one its "
                                   "source states")
    unread_share = re.compile(_expand_all(p["slot_share_unread"], p), re.I)
    rows_of: dict[int, str] = {}
    for r in rules.extract["field_rules"]:
        if r["extractor"] != "holders" and not (r["extractor"] == "directors" and kind in r["kinds"]):
            continue
        heads = [rx(_expand_all(r[k], p)) for k in ("line_matches", "line_matches_bare") if r.get(k)]
        for no in range(start + 1, len(lines) + 1):
            if not any(h.search(lines[no - 1].strip()) for h in heads):
                continue
            rows_of[no] = r["field"]
            nxt = no + 1
            while nxt <= len(lines) and lines[nxt - 1].strip():
                if _list_row(lines[nxt - 1], r["field"], words, unread_share):
                    rows_of[nxt] = r["field"]
                nxt += 1
    kind_topics = {_topic_of(f) for f in expected}
    shapes = [r for r in rules.extract["classified_lines"]["rules"]
              if r.get("pattern") and (not r.get("kinds") or kind in r["kinds"])]
    for no in range(start + 1, len(lines) + 1):
        line = lines[no - 1].strip()
        if not any(ch.isalnum() for ch in line):
            continue
        fields = [rows_of[no]] if no in rows_of else None
        for r in shapes if fields is None else []:
            m = rx(_expand_all(r["pattern"], p)).search(line)
            if not m:
                continue
            if r["when"] == "label":      # a label and a typed value: the fields both name, by the audit's words
                g = m.groupdict()
                label = words.name(g["w_label"])
                typed = next((k for k in r["value_topics"] if k and g.get(k)), "")
                both = label & set(r["value_topics"][typed]) if label <= kind_topics else set()
                if not both or any(v and not words.name(v) <= both for k, v in g.items()
                                   if k.startswith("w_") and k != "w_label"):
                    continue
                fields = sorted(f for f in expected if _topic_of(f) in both)
                break
            may = r.get("slots_may_name", r["fields"])
            allowed = kind_topics if may == "kind" else {_topic_of(f) for f in may}
            if any(v and not words.name(v) <= allowed for k, v in m.groupdict().items() if k.startswith("w_")):
                continue
            fields = [f.replace("{fy}", fy) for f in r["fields"]]
            break
        if fields is None:
            out["open"].append(no)
            out["holding"] = out["holding"] or words.holding(line)
            continue
        for f in fields:          # a field its kind does not read, not read at all, or read from another line
            if f not in expected or not spans.get(f) or any(not first <= no <= last for first, last in spans[f]):
                out["restated"].add(f)
    out["scope"] = {"*"} if out["open"] else set(out["restated"])
    return out


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
        words = _Words(rules)
        for meta in record["documents"]:
            got = classified_scope(meta, record, input_dir, rules, words)
            problems.extend(got["problems"])
            check = next((c for c in record.get("classified_checks", []) if c["doc_id"] == meta["doc_id"]
                          and c["file"] == meta["file"]), None)
            said = set(check["fields_check"]["may_change"]) if check else set()
            if got["open"] and "*" not in said:
                problems.append(f"{meta['doc_id']}: line(s) {got['open'][:5]} read by no rule of its kind, and the record "
                                "does not say the document may change every field")
            elif got["restated"] - said and "*" not in said:
                problems.append(f"{meta['doc_id']}: it states {sorted(got['restated'] - said)} on lines that no rule "
                                "read, and the record does not say the document may change them")
            if got["holding"] and (check is None or check["holders_check"]["status"] != "not_read"):
                problems.append(f"{meta['doc_id']}: a line read by no rule of its kind may state a holding, and its "
                                "holders are not marked unread")
            if got["scope"] | said:
                scopes.append(({"date": meta["date"], "doc_id": meta["doc_id"]}, got["scope"] | said, []))
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
