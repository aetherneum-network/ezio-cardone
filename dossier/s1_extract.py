"""Stage 1 - assertions from source documents, with abstention.

A source document is a UTF-8 text file: a header block (``Key: value`` lines up to the first blank
line) and a body. Each rule of ``rules/extract.json`` turns one place of one document into one
assertion ``{field, value, source_doc, source_date, edition, ...}``. What a rule cannot read is an
assertion with status ``TO_CONFIRM`` and a reason - never a guess:

* an illegible figure, an amount in an unknown or ambiguous form, an amount whose reading is not certain
  (the figure goes on past the token, a magnitude word next to it, a document that states a scale);
* a holders' table or a directors' list with one line that cannot be read (the whole table abstains);
* an amount whose nature (resolved, subscribed, paid in) the text does not give;
* a field that the kind of document is expected to state and no rule found.

Facts come from the content. The file name is compared with the content and a divergence is
reported; it is never a source.

A document whose type is not recognised gives no assertion. Since v2.0.2 its body is still checked for
holders' tables (``holders_check``, rules/extract.json ``holders_evidence``), so that stage 4 can tell a
document with no table, or with tables read whole, from one that may hide a table it could not read.

A document whose type is recognised is read for the fields of its kind only. Since v2.0.5 (D34) every body line of
it is decided by rules/extract.json ``classified_lines`` (``classified_check``): a line that no rule of its kind
explains makes the document one that may change every field (stage 3, DISC-006) and is checked for holdings as an
unread document is; a holders' table in a document of another kind is read whole and summed, or OWN-015 blocks.
"""
from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

from . import SYNTHETIC_MARKER
from .lib import jsonio
from .lib.numbers import frac_str, parse_amount, parse_count, parse_share
from .rules_engine import Rules, first_match, rx

NATURES = ("resolved", "subscribed", "paid_in")


@dataclass
class Document:
    file: str                 # posix path relative to the input root
    sha256: str
    lines: list[str]
    header: dict[str, str] = field(default_factory=dict)
    header_lines: dict[str, int] = field(default_factory=dict)
    body_start: int = 0       # index (0-based) of the first body line
    marker_ok: bool = False
    doc_id: str = ""
    type_label: str = ""
    date: str = ""
    edition: str = ""
    series: str = ""
    edition_no: int | None = None
    entity_id: str = ""
    entity_name: str = ""
    registry_no: str = ""
    kind: str = "UNKNOWN"
    kind_rule: str = ""
    role: str = ""
    fy: str = ""
    scale: str = ""           # a scale statement of the document ("in thousands of EUR"): no amount is read
    problems: list[str] = field(default_factory=list)

    def summary(self) -> dict:
        return {"doc_id": self.doc_id, "file": self.file, "kind": self.kind, "type_label": self.type_label,
                "date": self.date, "edition": self.edition, "series": self.series,
                "edition_no": self.edition_no, "role": self.role, "sha256": self.sha256}


def _valid_date(s: str) -> bool:
    try:
        _dt.date.fromisoformat(s)
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s))
    except ValueError:
        return False


def classify_kind(type_label: str, rules: Rules) -> tuple[str, str]:
    r = first_match(rules.extract["doc_kinds"], lambda k: rx(k["type_matches"]).search(type_label.strip()) is not None)
    return (r["kind"], r["id"]) if r else ("UNKNOWN", "")


def parse_document(text: str, file: str, rules: Rules, sha256: str = "") -> Document:
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    doc = Document(file=file, sha256=sha256 or jsonio.sha256_bytes(text.encode("utf-8")), lines=lines)
    doc.marker_ok = bool(lines) and lines[0].strip() == SYNTHETIC_MARKER
    keys = set(rules.extract["parameters"]["header_keys"])
    i = 1 if doc.marker_ok else 0
    while i < len(lines) and lines[i].strip():
        k, sep, v = lines[i].partition(":")
        if sep and k.strip() in keys and k.strip() not in doc.header:
            doc.header[k.strip()] = v.strip()
            doc.header_lines[k.strip()] = i + 1
        i += 1
    doc.body_start = i
    h = doc.header
    doc.doc_id = h.get("Document id", "")
    doc.type_label = h.get("Document type", "")
    doc.date = h.get("Document date", "")
    doc.edition = h.get("Edition", "")
    doc.fy = h.get("Financial year", "")
    if not doc.doc_id:
        doc.problems.append("no document id in the header")
    if not _valid_date(doc.date):
        doc.problems.append("no valid document date in the header")
    m = rx(rules.extract["parameters"]["entity_pattern"]).match(h.get("Entity", ""))
    if m:
        doc.entity_name = m.group("name")
        doc.registry_no = f"TEST-REG-{m.group('num')}"
        doc.entity_id = f"E-{m.group('num')[-4:]}"
    else:
        doc.problems.append("no entity with a test registry number in the header")
    doc.kind, doc.kind_rule = classify_kind(doc.type_label, rules)
    if doc.kind == "UNKNOWN":
        doc.problems.append(f"document type not recognised: {doc.type_label!r}")
    else:
        doc.role = rules.extract["roles"][doc.kind]
    if doc.kind == "FIN" and not re.fullmatch(r"\d{4}", doc.fy):
        doc.problems.append("financial summary without a financial year")
    m = re.match(rules.extract["parameters"]["edition_pattern"], doc.edition)
    if m:
        doc.series, doc.edition_no = m.group("series"), int(m.group("no"))
    else:
        doc.series = f"FIN-FY{doc.fy}" if doc.kind == "FIN" else doc.kind
        if not doc.edition:
            doc.problems.append("no edition in the header")
    scale = _param_rx(rules, "scale_statement")
    doc.scale = next((m.group(0) for line in lines[doc.body_start:] for m in [scale.search(line)] if m), "")
    return doc


# ----------------------------------------------------------------------------------------------
# assertions

def _assertion(doc: Document, fld: str, nature: str, rule: str, *, value=None, reason: str | None = None,
               line: int | None = None, line_end: int | None = None, quote: str = "") -> dict:
    a = {"field": fld, "nature": nature, "role": doc.role, "series": doc.series, "edition_no": doc.edition_no,
         "source_doc": doc.doc_id, "source_file": doc.file, "source_date": doc.date, "edition": doc.edition,
         "rule": rule, "line": line, "line_end": line_end if line_end is not None else line, "quote": quote}
    if value is not None:
        a["status"], a["value"] = "STATED", value
    else:
        a["status"], a["reason"] = "TO_CONFIRM", reason or "could not be read"
    return a


def _field_name(template: str, doc: Document) -> str:
    return template.replace("{fy}", doc.fy)


def _expand(text: str, rules: Rules) -> str:
    """Substitute the shared pieces of rules/extract.json parameters into a pattern, until none is left (since
    v2.0.5 every string parameter may be a piece: the slots of classified_lines nest three deep)."""
    p = rules.extract["parameters"]
    for _ in range(8):
        new = re.sub(r"\{([a-z_]+)\}", lambda m: p[m.group(1)] if isinstance(p.get(m.group(1)), str)
                     else m.group(0), text)
        if new == text:
            break
        text = new
    return text


class _Items:
    """The item grammars of one list rule, tried in order: item_matches, then (since v2.0.4) item_matches_share_first
    for a share that stands before the holder. Every grammar names the same groups (id, id_last, share)."""

    def __init__(self, patterns: list[re.Pattern]):
        self.patterns = patterns

    def match(self, line: str) -> re.Match | None:
        for pat in self.patterns:
            m = pat.match(line)
            if m:
                return m
        return None


def _item_rx(rule: dict, rules: Rules) -> _Items:
    keys = ("item_matches", "item_matches_share_first")
    return _Items([rx(_expand(_expand(rule[k], rules), rules)) for k in keys if rule.get(k)])


def _total_rx(rule: dict, rules: Rules) -> re.Pattern | None:
    """The Total line of a holders' table (rules/extract.json item_total, since v2.0.4), or None."""
    return rx(_expand(_expand(rule["total_matches"], rules), rules)) if rule.get("total_matches") else None


def _item_id(m: re.Match) -> str:
    """The identifier of a list line, whether it stands first or after the name."""
    return m.group("id") or m.group("id_last")


def _param_rx(rules: Rules, name: str) -> re.Pattern:
    return rx(_expand(_expand(rules.extract["parameters"][name], rules), rules))


def _pattern(rule: dict, rules: Rules) -> re.Pattern:
    return rx(_expand(_expand(rule["line_matches"], rules), rules))


def read_amount(doc: Document, line: str, start: int, end: int, token: str,
                rules: Rules) -> tuple[str | None, str | None]:
    """The canonical value of the amount ``token`` that ends at ``line[end]`` (``line[:start]`` is the text
    before it and its currency marker), or ``(None, reason)`` when the reading is not certain. Nothing
    uncertain is ever returned as a value."""
    if doc.scale:
        return None, f"the document states a scale ({doc.scale!r}): its amounts are not read as units"
    if _param_rx(rules, "amount_uncertain_before").search(line[:start]):
        return None, "a magnitude word stands before the amount"
    if _param_rx(rules, "amount_uncertain_after").search(line[end:]):
        return None, ("the figure goes on past what can be read as one amount "
                      "(a further separator, an attached character or a magnitude word)")
    return parse_amount(token)


def _body(doc: Document) -> list[tuple[int, str]]:
    """(1-based line number, text) of every body line."""
    return [(i + 1, doc.lines[i]) for i in range(doc.body_start, len(doc.lines))]


def _extract_text(doc: Document, rule: dict, rules: Rules, known: dict[str, set[str]] | None = None
                  ) -> list[dict] | None:
    pat = _pattern(rule, rules)
    for no, text in _body(doc):
        m = pat.search(text)
        if not m:
            continue
        out = []
        value = m.group("value").strip()
        fld = _field_name(rule["field"], doc)
        if rule.get("value_slot"):
            # since v2.0.7 (D36): each value is judged as the slot of classified_lines the rule names (w_office, an
            # address): words that are not part of it, and the line gives no value
            slots = [v.strip() for k, v in m.groupdict().items() if k in ("value", "previous") and v]
            if not all(_slot_closes(doc, rule["value_slot"], v, text.strip(), {_topic(fld)}, known, rules)
                       for v in slots):
                return [_assertion(doc, fld, rule["nature"], rule["id"], line=no, quote=text,
                                   reason="the address holds words that are not part of an address (rules/extract.json "
                                          "slot_address_word, slot_not_name_word, or a name known to the corpus): "
                                          "not read")]
        if value:
            out.append(_assertion(doc, fld, rule["nature"], rule["id"], value=value, line=no, quote=text))
        else:
            out.append(_assertion(doc, fld, rule["nature"], rule["id"], reason="empty value", line=no, quote=text))
        if "previous" in pat.groupindex and m.group("previous").strip():
            out.append(_assertion(doc, fld + ".previous", "historical", rule["id"],
                                  value=m.group("previous").strip(), line=no, quote=text))
        return out
    return None


def _extract_amount(doc: Document, rule: dict, rules: Rules) -> list[dict] | None:
    pat = _pattern(rule, rules)
    for no, text in _body(doc):
        m = pat.search(text)
        if not m:
            continue
        value, why = read_amount(doc, text, m.start("amt"), m.end("amt"), m.group("amt"), rules)
        return [_assertion(doc, _field_name(rule["field"], doc), rule["nature"], rule["id"], value=value,
                           reason=why, line=no, quote=text)]
    return None


def amount_spans(clause: str, rules: Rules) -> list[tuple[int, int, str]]:
    """(start of the currency marker, end of the token, token) of every amount in a clause."""
    p = rules.extract["parameters"]
    pat = rx(_expand(p["currency_prefix"] + "(?P<amt>" + p["amount_token"] + ")", rules))
    return [(m.start(), m.end(), m.group("amt")) for m in pat.finditer(clause)]


def classify_natures(clause: str, rules: Rules) -> list[dict]:
    """The nature of every amount of a capital clause, by the ordered rules of figure_nature.json."""
    spans = amount_spans(clause, rules)
    segs = []
    for i, (start, end, token) in enumerate(spans):
        pre = clause[spans[i - 1][1] if i else 0:start]
        post = clause[end:spans[i + 1][0] if i + 1 < len(spans) else len(clause)]
        segs.append({"token": token, "pre": pre, "post": post, "start": start, "end": end})
    group = rules.figure_nature["rules"]

    def applies(r: dict, s: dict, current: int | None) -> bool:
        w = r["when"]
        if "pre_matches" in w and not rx(w["pre_matches"]).search(s["pre"]):
            return False
        if "post_matches" in w and not rx(w["post_matches"]).search(s["post"]):
            return False
        if w.get("single_current_amount") and current != 1:
            return False
        return True

    # first pass: which amounts are historical (needed by rules that ask for a single current amount)
    first = [first_match(group, lambda r, s=s: applies(r, s, None)) for s in segs]
    current = sum(1 for r in first if not (r and r["natures"] == ["historical"]))
    out = []
    for s in segs:
        r = first_match(group, lambda r, s=s: applies(r, s, current))
        natures = [n.replace("{bare_capital_nature}", rules.param("figure_nature", "bare_capital_nature"))
                   for n in (r["natures"] if r else [])]
        out.append({"token": s["token"], "natures": natures, "rule": r["id"] if r else "",
                    "start": s["start"], "end": s["end"]})
    return out


def _extract_capital(doc: Document, rule: dict, rules: Rules) -> list[dict] | None:
    pat = _pattern(rule, rules)
    clauses = [(no, text) for no, text in _body(doc) if pat.search(text) and amount_spans(text, rules)]
    if not clauses:
        return None
    base = "share_capital."
    if len(clauses) > 1:
        no, text = clauses[0]
        return [_assertion(doc, base + n, n, rule["id"], reason="more than one capital clause in the document",
                           line=no, line_end=clauses[-1][0], quote="\n".join(t for _, t in clauses))
                for n in NATURES]
    no, text = clauses[0]
    found: dict[str, list[tuple[str | None, str | None, str]]] = {n: [] for n in NATURES}
    unknown = 0
    out: list[dict] = []
    for amt in classify_natures(text, rules):
        value, why = read_amount(doc, text, amt["start"], amt["end"], amt["token"], rules)
        if not amt["natures"]:
            unknown += 1
            continue
        for n in amt["natures"]:
            if n == "historical":
                if value is not None:
                    out.append(_assertion(doc, base + "previous", "historical", amt["rule"], value=value,
                                          line=no, quote=text))
            else:
                found[n].append((value, why, amt["rule"]))
    for n in NATURES:
        hits = found[n]
        values = {v for v, _, _ in hits}
        if len(hits) == 1 or (hits and len(values) == 1):
            value, why, rid = hits[0]
            out.append(_assertion(doc, base + n, n, rid, value=value, reason=why, line=no, quote=text))
        elif hits:
            out.append(_assertion(doc, base + n, n, rule["id"], reason=f"the clause gives more than one {n} amount",
                                  line=no, quote=text))
        elif unknown:
            out.append(_assertion(doc, base + n, n, rule["id"],
                                  reason="the clause has an amount whose nature the text does not give",
                                  line=no, quote=text))
        else:
            out.append(_assertion(doc, base + n, n, rule["id"], reason=f"the clause gives no {n} amount",
                                  line=no, quote=text))
    return out


def ends_list(text: str, rules: Rules) -> bool:
    """A line that ends a list without being part of it (since v2.0.7, D36; rules/extract.json list_end_note): a
    heading of a list, or a full sentence (list_end_sentence), with no identifier in it."""
    line = text.strip()
    if re.search(r"P-\d{3}|E-\d{4}", line):
        return False
    for r in rules.extract["field_rules"]:
        if r["extractor"] in ("holders", "directors") and (
                _pattern(r, rules).search(line) or (r.get("line_matches_bare") and rx(
                    _expand(_expand(r["line_matches_bare"], rules), rules)).search(line))):
            return True
    return _param_rx(rules, "list_end_sentence").search(line) is not None


def _block(doc: Document, heading_no: int, rules: Rules) -> list[tuple[int, str]]:
    """The non-empty lines that follow a heading, up to the first blank line or (since v2.0.7) the first line that
    ends the list without being part of it (ends_list): that line is classified on its own."""
    out = []
    for no, text in _body(doc):
        if no <= heading_no:
            continue
        if not text.strip() or ends_list(text, rules):
            break
        out.append((no, text))
    return out


def count_total(doc: Document, rules: Rules) -> tuple[int | None, int | None, str]:
    """(total number of quotas or shares, line of the statement, "") when the body of the document states one
    total (rules/extract.json, count_total); (None, None, why) otherwise."""
    found: dict[int, int] = {}
    for no, text in _body(doc):
        for pattern in rules.extract["parameters"]["count_total"]:
            for m in rx(pattern).finditer(text):
                found.setdefault(int(re.sub(r"\D", "", m.group("total"))), no)
    if not found:
        return None, None, "the document does not state the total number of quotas or shares"
    if len(found) > 1:
        return None, None, ("the document states more than one total number of quotas or shares ("
                            + ", ".join(str(t) for t in sorted(found)) + ")")
    (total, no), = found.items()
    if total <= 0:
        return None, None, "the total number of quotas or shares is not positive"
    return total, no, ""


def _read_items(block: list[tuple[int, str]], item: _Items, extractor: str, doc: Document | None = None,
                rules: Rules | None = None, total_rx: re.Pattern | None = None
                ) -> tuple[list | None, str, int | None, Fraction | None]:
    """(value, "", line of the total number of quotas or None, the Total line's value or None) of a list read whole,
    or (None, why, None, None) at the first line that cannot be read. A table of counts is read only with the total
    its document states (count_total). A Total line (total_rx) is read only as the last line of a holders' table;
    its value is returned beside the rows, never in place of them (stage 4 compares it with the exact sum)."""
    if not block:
        return None, "the list is empty", None, None
    stated = None
    if extractor == "holders" and total_rx is not None and len(block) > 1:
        m = total_rx.match(block[-1][1])
        if m and not item.match(block[-1][1]):
            stated, block = m.group("share"), block[:-1]
    ids: list[str] = []
    rows: list[dict] = []
    counts: dict[str, int] = {}
    for _, line in block:
        m = item.match(line)
        if not m:
            return None, "a line of the list could not be read", None, None
        hid = _item_id(m)
        if hid in ids:
            return None, f"{hid} is listed twice", None, None
        ids.append(hid)
        if extractor == "holders":
            share, why = parse_share(m.group("share"))
            if share is None:
                n, _ = parse_count(m.group("share"))
                if n is None:
                    return None, f"share of {hid}: {why}", None, None
                counts[hid] = n
                continue
            if share <= 0:
                return None, f"share of {hid} is not positive", None, None
            rows.append({"holder": hid, "share": frac_str(share)})
    if extractor != "holders":
        return sorted(ids), "", None, None
    total_line = None
    if counts:
        if rows:
            return None, "the table mixes numbers of quotas or shares with shares", None, None
        if doc is None or rules is None:
            return None, "a number of quotas or shares without the total of its document", None, None
        total, total_line, why = count_total(doc, rules)
        if total is None:
            return None, f"numbers of quotas or shares: {why}", None, None
        for hid, n in counts.items():
            if n <= 0:
                return None, f"share of {hid} is not positive", None, None
            rows.append({"holder": hid, "share": frac_str(Fraction(n, total))})
    stated_total = None
    if stated is not None:
        share, _ = parse_share(stated)
        if share is not None and not counts:
            stated_total = share
        elif share is None and counts:
            n, _ = parse_count(stated)
            if n is None:
                return None, "the Total line could not be read", None, None
            stated_total = Fraction(n, total)
        elif share is None:
            return None, ("the Total line could not be read" if parse_count(stated)[0] is None else
                          "the Total line states a number of quotas or shares, the rows state shares"), None, None
        else:
            return None, "the Total line states a share, the rows state numbers of quotas or shares", None, None
    return sorted(rows, key=lambda r: r["holder"]), "", total_line, stated_total


def _span(doc: Document, first: int, last: int) -> str:
    """The source lines ``first`` to ``last`` (1-based, inclusive), as the audit reads them back."""
    return "\n".join(doc.lines[first - 1:last])


def _list_headings(doc: Document, rule: dict, rules: Rules) -> list[tuple[int, str]]:
    """The body lines that head the list of the rule: the heading grammar with its terminal '.' or ':'
    (line_matches), or - since v2.0.4 - the same grammar without it (line_matches_bare) when the heading is the
    whole line and the next line is an item of the list. Nothing is guessed: a bare line followed by anything else
    is not a heading."""
    heading = _pattern(rule, rules)
    bare = rx(_expand(_expand(rule["line_matches_bare"], rules), rules)) if rule.get("line_matches_bare") else None
    item = _item_rx(rule, rules)
    out = []
    for no, text in _body(doc):
        line = text.strip()
        if heading.search(line):
            out.append((no, text))
        elif bare is not None and bare.search(line):
            block = _block(doc, no, rules)
            if block and block[0][0] == no + 1 and item.match(block[0][1]):
                out.append((no, text))
    return out


def _extract_list(doc: Document, rule: dict, rules: Rules) -> list[dict] | None:
    item = _item_rx(rule, rules)
    fld = _field_name(rule["field"], doc)
    found = _list_headings(doc, rule, rules)
    if not found:
        return None
    no, text = found[0]
    block = _block(doc, no, rules)
    quote = "\n".join([text] + [t for _, t in block])
    end = block[-1][0] if block else no

    def abstain(why: str) -> list[dict]:
        return [_assertion(doc, fld, rule["nature"], rule["id"], reason=why, line=no, line_end=end, quote=quote)]

    if len(found) > 1:
        lines = ", ".join(str(n) for n, _ in found)
        what = "holders' tables" if rule["extractor"] == "holders" else "directors' lists"
        return abstain(f"{len(found)} {what} in one document (lines {lines}): which one is current "
                       "is not ours to choose")
    value, why, total_line, stated_total = _read_items(block, item, rule["extractor"], doc, rules,
                                                       _total_rx(rule, rules))
    if value is None:
        return abstain(why)
    if total_line is not None:
        # counts: the quote runs from the statement of the total to the end of the table, so that the audit can
        # re-derive every share from the source lines it cites
        no, end = min(no, total_line), max(end, total_line)
        quote = _span(doc, no, end)
    a = _assertion(doc, fld, rule["nature"], rule["id"], value=value, line=no, line_end=end, quote=quote)
    if stated_total is not None:
        a["stated_total"] = frac_str(stated_total)      # the Total line, compared with the sum by stage 4 (OWN-010)
    return [a]


def holders_evidence(line: str, rules: Rules) -> dict:
    """The rule of rules/extract.json holders_evidence that decides one body line (first match wins)."""
    cfg = rules.extract["holders_evidence"]
    text = rx(_expand(cfg["parameters"]["neutral_phrases"], rules)).sub(" ", line)
    return first_match(cfg["rules"], lambda r: r["when"] == "always"
                       or rx(_expand(r["pattern"], rules)).search(text) is not None)


def holders_check(doc: Document, rules: Rules) -> dict:
    """What a document that was not classified says about its holders, without reading any other fact.

    ``read``: every holders' table in it was read whole (they are summed by stage 4, OWN-010);
    ``no_table``: no heading, no table and no line of rules/extract.json holders_evidence;
    ``not_read``: anything else - the document blocks the entity as an unread table would (OWN-015).
    """
    other = [p for p in doc.problems if not p.startswith("document type not recognised")]
    if other:
        return {"status": "not_read", "why": "the header of the document could not be read (" + "; ".join(other)
                + "): a table in it could not carry its source and date"}
    rule = next(r for r in rules.extract["field_rules"] if r["extractor"] == "holders")
    item = _item_rx(rule, rules)
    covered: set[int] = set()
    tables = []
    for no, _text in _list_headings(doc, rule, rules):
        block = _block(doc, no, rules)
        # the line of a total stated for counts is not covered: it is still checked for evidence below, so a
        # table of counts in a document of unrecognised type is not read (known limit of v2.0.3)
        value, why, _, stated_total = _read_items(block, item, "holders", doc, rules, _total_rx(rule, rules))
        if value is None:
            return {"status": "not_read", "why": f"the holders' table at line {no} could not be read ({why})"}
        covered.update([no] + [n for n, _ in block])
        table = {"line": no, "line_end": block[-1][0], "value": value}
        if stated_total is not None:
            table["stated_total"] = frac_str(stated_total)
        tables.append(table)
    if len(tables) > 1:
        return {"status": "not_read", "why": f"{len(tables)} holders' tables in one document: which one is current "
                                             "is not ours to choose"}
    for no, text in _body(doc):
        if no in covered or not text.strip():
            continue
        hit = holders_evidence(text, rules)
        if hit["outcome"] != "none":
            return {"status": "not_read", "why": f"line {no} may state a holding outside a table that could be read "
                                                 f"(rule {hit['id']})"}
    if tables:
        return {"status": "read", "why": "", "edition": doc.edition, "tables": tables}
    return {"status": "no_table", "why": "no holders' table and no line that may state a holding"}


EVERY_FIELD = "*"


def line_fields(line: str, rules: Rules) -> tuple[list[str], list[str]]:
    """(fields one body line of an unclassified document may state, ids of the rules that decided), by
    rules/extract.json unread_fields: every 'topic' rule that applies adds its fields; only when none applies,
    the first other rule that applies decides. ``["*"]`` is every field."""
    group = rules.extract["unread_fields"]["rules"]
    fields: set[str] = set()
    ids: list[str] = []
    for r in group:
        if r["when"] == "topic" and rx(_expand(r["pattern"], rules)).search(line):
            fields.update(r["fields"])
            ids.append(r["id"])
    if not ids:
        r = first_match([r for r in group if r["when"] != "topic"],
                        lambda r: r["when"] == "always" or rx(_expand(r["pattern"], rules)).search(line) is not None)
        fields.update(r["fields"])
        ids.append(r["id"])
    return ([EVERY_FIELD] if EVERY_FIELD in fields else sorted(fields)), ids


def fields_check(doc: Document, rules: Rules, holders: dict) -> dict:
    """Which fields a document that was not classified may change (DISC-005, rules/discrepancy.json
    unread_document_scope). Only a document whose one problem is its type is looked into; the lines of a
    holders' table read whole are left to the holders' check, which alone decides the shareholders."""
    other = [p for p in doc.problems if not p.startswith("document type not recognised")]
    if other:
        return {"may_change": [EVERY_FIELD], "why": "the header of the document could not be read"}
    covered: set[int] = set()
    for t in holders.get("tables", []) if holders.get("status") == "read" else []:
        covered.update(range(t["line"], t["line_end"] + 1))
    may: set[str] = set() if holders.get("status") == "no_table" else {"shareholders"}
    lines: dict[str, list[int]] = {}
    for no, text in _body(doc):
        if no in covered or not text.strip():
            continue
        got, _ = line_fields(text, rules)
        for f in got:
            lines.setdefault(f, []).append(no)
        may.update(got)
    if EVERY_FIELD in may:
        return {"may_change": [EVERY_FIELD],
                "why": f"line {lines[EVERY_FIELD][0]} may state any field (rules/extract.json unread_fields)"}
    judged = "; ".join(f"{f}: line {', '.join(str(n) for n in lines[f])}" for f in sorted(lines)) \
        or "no line states a field"
    if rules.param("discrepancy", "unread_document_scope") != "fields_it_may_state":
        # since v2.0.6 (D35, hand-14 E-0013): the record says what DISC-005 applies - every field under the default
        # every_field - and keeps the judgement of the lines, which decides nothing under that scope, as a note
        return {"may_change": [EVERY_FIELD],
                "why": "every field: rules/discrepancy.json unread_document_scope is every_field (DISC-005); the "
                       f"lines alone (rules/extract.json unread_fields, not applied) would name {judged}"}
    return {"may_change": sorted(may), "why": judged}


_EXTRACTORS = {"text": _extract_text, "amount": _extract_amount, "capital": _extract_capital,
               "holders": _extract_list, "directors": _extract_list}


# ----------------------------------------------------------------------------------------------
# classified documents: every body line explained, or the document may change every field (v2.0.5, D34)

def _topic(fld: str) -> str:
    """The topic of a field, as the rules of unread_fields name it."""
    if fld.startswith("share_capital."):
        return "share_capital.*"
    if fld.startswith("fin."):
        return "fin.*"
    return fld


def not_name_words(text: str, rules: Rules) -> list[str]:
    """The words of a name slot that cannot be part of a name (rules/extract.json slot_not_name_word, since v2.0.6):
    every run of letters is tested, case ignored."""
    pat = _param_rx(rules, "slot_not_name_word")
    return [w for w in re.findall(r"[^\W\d_]+", text) if pat.search(w)]


def slot_topics(text: str, rules: Rules, names: bool = False) -> set[str]:
    """The fields the free words of a closed line may name, by the same test as a document of unrecognised type:
    every 'topic' rule of unread_fields that applies (FEV-010, a word of cancellation or correction, gives every field
    "*"), and the shareholders when a rule of holders_evidence finds a holding. The figures a slot may hold are typed
    by its grammar (a house number, the mark of an 'interno'): the test reads its words. A slot that holds a name
    (``names``, since v2.0.6) with a word that cannot be part of a name may name every field ("*")."""
    words = re.sub(r"\d+", " ", text)
    out: set[str] = set()
    for r in rules.extract["unread_fields"]["rules"]:
        if r["when"] == "topic" and rx(_expand(r["pattern"], rules)).search(words):
            out.update(r["fields"])
    if holders_evidence(words, rules)["outcome"] != "none":
        out.add("shareholders")
    if names and not_name_words(text, rules):
        out.add(EVERY_FIELD)
    return out


def _label_ok(label: str | None, fld: str, rules: Rules, own: bool = False) -> bool:
    """The name beside an identifier in a list line: a person's or a company's name (parameter slot_label) whose
    words name nothing but a name, a legal form or the field of the list, and (since v2.0.6) are all words that can
    be part of a name. ``own`` (since v2.0.7): the label is its identifier's own known name, a name whatever its
    words."""
    if not label or not label.strip() or own:
        return True
    if not rx("^" + _expand("{slot_label}", rules) + "$").search(label.strip()):
        return False
    return slot_topics(label, rules, names=True) <= {"name", "legal_form", _topic(fld)}


_LABEL_AFTER_ID = re.compile(r"(P-\d{3}|E-\d{4})\s*\(([^()]*)\)")


def own_name_differs(doc: Document, value: str, rules: Rules) -> bool:
    """A slot of the entity's own name (parameter slot_own_name_groups, since v2.0.6) that is not the name of the
    document's own header, spaces collapsed and the legal form at the end of each set aside. A document whose header
    names no entity has nothing to compare: False."""
    if not doc.entity_name.strip():
        return False
    pat = rx(rules.param("discrepancy", "legal_form_in_name"))

    def bare(text: str) -> str:
        m = pat.search(text)
        return " ".join((text[:m.start("form")] if m else text).split())
    return bare(value) != bare(doc.entity_name)


def labelled_identifiers(line: str, rules: Rules) -> list[tuple[str, str]]:
    """(identifier, the name beside it) of a line: every 'ID (name)', and the name before '(ID)' at the start of the
    line after an optional list marker and an optional share that stands first (the item grammar of EXT-HOLD-010)."""
    out = [(m.group(1), m.group(2)) for m in _LABEL_AFTER_ID.finditer(line)]
    first = rx(_expand(r"^\s*(?:{list_marker}\s+)?(?:(?:{share_token_first})\s*{item_separator}\s*)?"
                       r"(?P<label>[^()|:\t]+?)\s*\((?P<id>P-\d{3}|E-\d{4})\)", rules)).match(line)
    if first:
        out.append((first.group("id"), first.group("label")))
    return out


def label_not_its_own(line: str, known: dict[str, set[str]] | None, rules: Rules) -> list[str]:
    """The identifiers of a line whose name beside them is not their own known name (CLS-005, since v2.0.6), and
    (since v2.0.7, D36) the identifiers whose own name is known nowhere in the corpus: such a name cannot be checked.
    ``known`` None (an inline test that gives no names) checks nothing."""
    if not known:
        return []
    return [ident for ident, label in labelled_identifiers(line, rules)
            if " ".join(label.split()) not in known.get(ident, ())]


def own_label(ident: str | None, label: str | None, known: dict[str, set[str]] | None) -> bool:
    """The name beside an identifier is that identifier's own known name (since v2.0.7): a name whatever its words."""
    return bool(known and ident and label is not None and " ".join(label.split()) in known.get(ident, ()))


def _bare_company(name: str, rules: Rules) -> str:
    m = rx(rules.param("discrepancy", "legal_form_in_name")).search(name)
    return " ".join((name[:m.start("form")] if m else name).split())


def known_name_inside(text: str, known: dict[str, set[str]] | None, rules: Rules) -> list[str]:
    """The names known to the corpus (a person's of the identity layer, a company's of an Entity: header, its legal
    form set aside) that stand, as whole words, inside ``text`` (an address slot, since v2.0.7, D36)."""
    if not known:
        return []
    plain = " ".join(text.split())
    out = []
    for ident, names in known.items():
        for name in names:
            bare = _bare_company(name, rules) if ident.startswith("E-") else name
            if bare and re.search(r"(?<![^\W_])" + re.escape(bare) + r"(?![^\W_])", plain, re.I):
                out.append(bare)
    return sorted(set(out))


def _own_value(doc: Document, group: str, value: str, line: str, known: dict[str, set[str]] | None,
               rules: Rules) -> bool:
    """A slot that holds its own known value (since v2.0.7): the entity's own name of the document's header (the
    groups of slot_own_name_groups), or the own name of an identifier of the line (a person's slot beside it). Its
    words are a name whatever their class: the word test of slot_not_name_word is not applied to it."""
    p = rules.extract["parameters"]
    if group in p["slot_own_name_groups"]:
        return bool(doc.entity_name.strip()) and not own_name_differs(doc, value, rules)
    return any(own_label(ident, value, known) for ident, _ in labelled_identifiers(line, rules))


def address_form_ok(value: str, rules: Rules) -> bool:
    """The street and the town of an address are words of the form of an Italian place name (rules/extract.json
    slot_address_part, slot_address_word; since v2.0.7, D36)."""
    m = _param_rx(rules, "slot_address_part").match(" ".join(value.split()))
    if not m:
        return False
    word = _param_rx(rules, "slot_address_word")
    return all(word.match(w) for w in re.findall(r"[^\W\d_]+", m.group("street") + " " + m.group("town")))


def _slot_closes(doc: Document, group: str, value: str, line: str, allowed: set[str],
                 known: dict[str, set[str]] | None, rules: Rules) -> bool:
    """The free words of one slot name only the ``allowed`` fields: the topic test (slot_topics), the word test of a
    name slot unless it holds its own known value (v2.0.6, v2.0.7); an address (slot_address_groups, v2.0.7) has
    the form of an Italian place name (address_form_ok) and no name known to the corpus inside it."""
    p = rules.extract["parameters"]
    names = group in p["slot_name_groups"] and not _own_value(doc, group, value, line, known, rules)
    if group in p["slot_address_groups"] and (not address_form_ok(value, rules)
                                              or known_name_inside(value, known, rules)):
        return False
    return slot_topics(value, rules, names=names) <= allowed


def _share_typed(share: str | None, rules: Rules) -> bool:
    """The share of a list line is typed: read as a share or as a number of quotas or shares, or a figure that is
    not read (parameter slot_share_unread: no letter but those of per cent, quotas or shares). A share in other
    words is free text: the line is not a line of the list."""
    if share is None:
        return True
    s = share.strip()
    return (parse_share(s)[0] is not None or parse_count(s)[0] is not None
            or rx("^" + _expand("{slot_share_unread}", rules) + "$").search(s) is not None)


def _list_lines(doc: Document, rules: Rules, known: dict[str, set[str]] | None = None) -> dict[int, str]:
    """line -> field, for every line of a list under a heading of a list rule: the heading, an item line of the rule's
    grammar whose name passes _label_ok and whose share is typed (_share_typed), and the last line 'Total' of a
    holders' table with a typed share. Holders' tables are looked for in documents of every kind; directors' lists in
    the kinds of their rule. ``known``: a name that is its identifier's own known name passes _label_ok (v2.0.7)."""
    out: dict[int, str] = {}
    for rule in rules.extract["field_rules"]:
        if rule["extractor"] not in ("holders", "directors"):
            continue
        if rule["extractor"] == "directors" and doc.kind not in rule["kinds"]:
            continue
        item, total = _item_rx(rule, rules), _total_rx(rule, rules)
        for no, _text in _list_headings(doc, rule, rules):
            out[no] = rule["field"]
            block = _block(doc, no, rules)
            for i, (n, t) in enumerate(block):
                m = item.match(t)
                if m:
                    groups = m.groupdict()
                    label = groups.get("label") or groups.get("label_first")
                    if (_label_ok(label, rule["field"], rules, own_label(_item_id(m), label, known))
                            and _share_typed(groups.get("share"), rules)):
                        out[n] = rule["field"]
                elif (total is not None and i == len(block) - 1 and len(block) > 1 and total.match(t)
                      and _share_typed(total.match(t).group("share"), rules)):
                    out[n] = rule["field"]
    return out


def classify_line(doc: Document, no: int, text: str, lists: dict[int, str], rules: Rules,
                  known: dict[str, set[str]] | None = None) -> tuple[dict, list[str]]:
    """(the rule of rules/extract.json classified_lines that decides one body line of a classified document, the
    fields the line states). First match wins; ``["*"]`` is every field. ``known``: identifier -> its own names (the
    identity layer for persons, the entity's own headers for companies; CLS-005, since v2.0.6)."""
    kind_topics = {_topic(_field_name(t, doc)) for t in rules.extract["expected_fields"].get(doc.kind, [])}
    own_groups = set(rules.extract["parameters"]["slot_own_name_groups"])
    line = text.strip()
    for r in rules.extract["classified_lines"]["rules"]:
        if r.get("kinds") and doc.kind not in r["kinds"]:
            continue
        w = r["when"]
        if w == "always":
            return r, list(r["fields"])
        if w == "label_not_its_own":
            if label_not_its_own(line, known, rules):
                return r, list(r["fields"])
            continue
        if w == "no_letter_or_digit":
            if not re.search(r"[^\W_]", line):
                return r, []
            continue
        if w == "list_line":
            if no in lists:
                return r, [lists[no]]
            continue
        m = rx(_expand(r["pattern"], rules)).search(line)
        if not m:
            continue
        if any(v and own_name_differs(doc, v, rules) for k, v in m.groupdict().items() if k in own_groups):
            continue              # the entity's own name slot holds more, or other, than the entity's name (v2.0.6)
        if w == "label":
            fields = _label_line_fields(doc, m, r, kind_topics, rules, line, known)
            if fields:
                return r, fields
            continue
        may = r.get("slots_may_name", r["fields"])
        allowed = kind_topics if may == "kind" else {_topic(f) for f in may}
        if all(_slot_closes(doc, k, v, line, allowed, known, rules)
               for k, v in m.groupdict().items() if k.startswith("w_") and v):
            return r, [_field_name(f, doc) for f in r["fields"]]
        # free words that name another field do not close the line: the next rule decides
    raise RuntimeError("rules/extract.json classified_lines has no default rule")


def _label_line_fields(doc: Document, m: re.Match, rule: dict, kind_topics: set[str], rules: Rules,
                       line: str = "", known: dict[str, set[str]] | None = None) -> list[str]:
    """The fields a label line states (rule CLS-250): the fields of the kind whose topic both the label and the type of
    the value name (value_topics); [] when there is none, when the label names a field outside its kind, or when the
    free words of the value name anything but the fields of the line."""
    groups = m.groupdict()
    label = slot_topics(groups["w_label"], rules)
    if not label <= kind_topics:
        return []
    value = next((k for k in rule["value_topics"] if k and groups.get(k)), "")
    topics = label & set(rule["value_topics"][value])
    if not topics:
        return []
    for k, v in groups.items():
        if k.startswith("w_") and k != "w_label" and v and not _slot_closes(doc, k, v, line, topics, known, rules):
            return []
    return sorted(f for f in (_field_name(t, doc) for t in rules.extract["expected_fields"][doc.kind])
                  if _topic(f) in topics)


def _classified_holders(doc: Document, open_lines: list[int], rules: Rules) -> dict:
    """The holders' check of a classified document, as for a document of unrecognised type: in a document whose
    kind is not read for holders, every holders' table is read whole (summed by stage 4) or the document is
    'not_read'; in a document of any kind, a line that no rule explains and that may state a holding
    (holders_evidence) makes it 'not_read' (OWN-015 blocks)."""
    rule = next(r for r in rules.extract["field_rules"] if r["extractor"] == "holders")
    tables = []
    if doc.kind not in rule["kinds"]:
        found = _list_headings(doc, rule, rules)
        if len(found) > 1:
            return {"status": "not_read", "why": f"{len(found)} holders' tables in a document of kind {doc.kind}: "
                                                 "which one is current is not ours to choose"}
        item = _item_rx(rule, rules)
        for no, _text in found:
            block = _block(doc, no, rules)
            value, why, _, stated_total = _read_items(block, item, "holders", doc, rules, _total_rx(rule, rules))
            if value is None:
                return {"status": "not_read", "why": f"the holders' table at line {no} of a document of kind "
                                                     f"{doc.kind} could not be read ({why})"}
            table = {"line": no, "line_end": block[-1][0], "value": value}
            if stated_total is not None:
                table["stated_total"] = frac_str(stated_total)
            tables.append(table)
    for no in open_lines:
        hit = holders_evidence(doc.lines[no - 1], rules)
        if hit["outcome"] != "none":
            return {"status": "not_read", "why": f"line {no}, read by no rule of its kind, may state a holding "
                                                 f"(rule {hit['id']})"}
    if tables:
        return {"status": "read", "why": "", "edition": doc.edition, "tables": tables}
    return {"status": "no_table", "why": "no holders' table outside the lists of its kind and no line that may "
                                         "state a holding"}


_LIST_NOUN = {"shareholders": "holders' table", "directors": "directors' list"}


def _list_region(doc: Document, rules: Rules) -> dict[int, tuple[str, int]]:
    """line -> (field of the list, line of its heading), for every line of the block of a list heading (the lists
    of _list_lines: holders' tables in every kind, directors' lists in the kinds of their rule), rows or not."""
    out: dict[int, tuple[str, int]] = {}
    for rule in rules.extract["field_rules"]:
        if rule["extractor"] not in ("holders", "directors"):
            continue
        if rule["extractor"] == "directors" and doc.kind not in rule["kinds"]:
            continue
        for no, _text in _list_headings(doc, rule, rules):
            for n, _t in _block(doc, no, rules):
                out.setdefault(n, (rule["field"], no))
    return out


def _lines_text(numbers: list[int]) -> str:
    return ("line " if len(numbers) == 1 else "lines ") + ", ".join(str(n) for n in numbers)


def classified_check(doc: Document, assertions: list[dict], rules: Rules,
                     known: dict[str, set[str]] | None = None) -> dict | None:
    """What a document of a recognised type may change beyond the fields its rules read (since v2.0.5, D34).

    Every non-empty body line is decided by rules/extract.json classified_lines. A line that no rule explains makes the
    document one that may change every field (DISC-006). A closed line states nothing but the fields of its rule: when
    one of them is a field of the kind that no rule read from this line (a second clause, a second list), or a field
    that its kind does not read (a holders' table in a document of another kind), the document may change that
    field. ``None`` when the document says nothing beyond what its rules read."""
    if doc.kind == "UNKNOWN":
        return None
    expected = {_field_name(t, doc) for t in rules.extract["expected_fields"][doc.kind]}
    spans: dict[str, list[tuple[int, int]]] = {}
    for a in assertions:
        if a["line"] is not None and not a["field"].endswith(".previous"):
            spans.setdefault(a["field"], []).append((a["line"], a["line_end"]))
    lists = _list_lines(doc, rules, known)
    region = _list_region(doc, rules)
    unexplained: list[int] = []
    again: dict[str, list[int]] = {}
    foreign: dict[str, list[int]] = {}
    inside: dict[tuple[str, int, str, str], list[int]] = {}
    for no, text in _body(doc):
        if not text.strip():
            continue
        rule, fields = classify_line(doc, no, text, lists, rules, known)
        if "*" in fields:
            unexplained.append(no)
            continue
        for f in fields:
            if no in region and region[no][0] != f:
                # a line inside the list of another field that reads as a line of this one (v2.0.7, D36 (e): a holder
                # without a share reads as a director's line, CLS-240): the document may change both fields
                inside.setdefault((region[no][0], region[no][1], f, rule["id"]), []).append(no)
            elif f not in expected:
                foreign.setdefault(f, []).append(no)
            elif not spans.get(f) or any(not (first <= no <= last) for first, last in spans[f]):
                again.setdefault(f, []).append(no)      # no rule of the kind read the field from this line
    holders = _classified_holders(doc, unexplained, rules)
    if not unexplained and not again and not foreign and not inside and holders["status"] == "no_table":
        return None
    why = []
    if unexplained:
        why.append(f"{_lines_text(unexplained)} read by no rule of its kind (rules/extract.json classified_lines)")
    for f in sorted(again):
        why.append(f"{_lines_text(again[f])} state the {f} and no rule of its kind read them")
    for (lf, head, f, rid), nos in sorted(inside.items()):
        why.append(f"{_lines_text(nos)} stand in the {_LIST_NOUN.get(lf, lf)} of line {head} and are not rows it reads "
                   f"(each reads as a line of the {f}, {rid}); no rule of its kind read them")
    for f in sorted(foreign):
        why.append(f"{_lines_text(foreign[f])}: a list of the {f} in a document of kind {doc.kind}")
    may = [EVERY_FIELD] if unexplained else sorted(set(again) | set(foreign)
                                                   | {x for lf, _, f, _ in inside for x in (lf, f)})
    return {"doc_id": doc.doc_id, "file": doc.file, "date": doc.date, "kind": doc.kind,
            "fields_check": {"may_change": may, "why": "; ".join(why)}, "holders_check": holders}


def extract_document(doc: Document, rules: Rules, known: dict[str, set[str]] | None = None) -> list[dict]:
    """Every assertion of one classified document, abstentions included. ``known`` (since v2.0.7): the names known to
    the corpus, refused inside a value that is a slot of names (value_slot_names)."""
    if doc.kind == "UNKNOWN":
        return []
    out: list[dict] = []
    done: set[str] = set()
    for rule in rules.extract["field_rules"]:
        if doc.kind not in rule["kinds"] or rule["field"] in done:
            continue
        got = (_extract_text(doc, rule, rules, known) if rule["extractor"] == "text"
               else _EXTRACTORS[rule["extractor"]](doc, rule, rules))
        if got is None:
            continue
        done.add(rule["field"])      # first match wins: no later rule is tried for this field
        out.extend(got)
    have = {a["field"] for a in out}
    for template in rules.extract["expected_fields"][doc.kind]:
        fld = _field_name(template, doc)
        if fld not in have:
            nature = fld.rsplit(".", 1)[-1] if fld.startswith("share_capital.") else _nature_of(fld)
            out.append(_assertion(doc, fld, nature, "EXPECTED-FIELD",
                                  reason="this kind of document is expected to state the field and no rule found it"))
    return out


def _nature_of(fld: str) -> str:
    if fld == "shareholders":
        return "share"
    if fld == "directors":
        return "person"
    return "financial" if fld.startswith("fin.") else "text"


def filename_divergences(doc: Document, assertions: list[dict], rules: Rules, folder_entity: str = "") -> list[dict]:
    """Compare what the file name suggests with what the content says. The content always wins."""
    p = rules.extract["parameters"]
    out = []

    def add(aspect: str, name_says: str, content_says: str) -> None:
        out.append({"doc_id": doc.doc_id, "file": doc.file, "aspect": aspect,
                    "filename_says": name_says, "content_says": content_says})

    if folder_entity and doc.entity_id and folder_entity != doc.entity_id:
        add("folder", folder_entity, doc.entity_id)
    m = re.match(p["filename_pattern"], doc.file.rsplit("/", 1)[-1])
    if not m:
        return out
    if m.group("date") != doc.date:
        add("date", m.group("date"), doc.date)
    kind = p["filename_slugs"].get(m.group("slug"))
    if kind and doc.kind != "UNKNOWN" and kind != doc.kind:
        add("kind", kind, doc.kind)
    detail = m.group("detail") or ""
    if re.fullmatch(r"P-\d{3}", detail) and doc.kind == "APPOINTMENT":
        stated = [a for a in assertions if a["field"] == "directors" and a["status"] == "STATED"]
        if stated and detail not in stated[0]["value"]:
            add("appointee", detail, ", ".join(stated[0]["value"]))
    return out


# ----------------------------------------------------------------------------------------------
# corpus level

def list_source_files(input_dir: Path) -> list[tuple[str, str, Path]]:
    """(entity folder, posix path relative to the input root, path) of every source file, sorted."""
    root = Path(input_dir) / "entities"
    out = []
    if root.is_dir():
        for folder in sorted(p for p in root.iterdir() if p.is_dir()):
            for f in sorted(folder.glob("*.txt")):
                out.append((folder.name, f"entities/{folder.name}/{f.name}", f))
    return out


def known_names(input_dir: Path, docs: list[Document], rules: Rules) -> dict[str, set[str]]:
    """identifier -> the names that are its own (CLS-005, since v2.0.6): a person's name in the identity layer of the
    input (identity/persons.json, when present), a company's name in the header (Entity:) of its own documents that
    carry the SYNTHETIC marker. Spaces are collapsed; nothing else is normalised."""
    out: dict[str, set[str]] = {}
    path = Path(input_dir) / "identity" / "persons.json"
    if path.exists():
        for pid, person in (jsonio.load(path) or {}).items():
            if isinstance(person, dict) and isinstance(person.get("name"), str) and person["name"].strip():
                out.setdefault(pid, set()).add(" ".join(person["name"].split()))
    for doc in docs:
        if doc.marker_ok and doc.entity_id and doc.entity_name.strip():
            out.setdefault(doc.entity_id, set()).add(" ".join(doc.entity_name.split()))
    return out


def extract_corpus(input_dir: Path | str, rules: Rules, as_of: str) -> dict[str, dict]:
    """Raw extraction of a whole input folder, keyed by the entity each document names in its content."""
    raw: dict[str, dict] = {}

    def bucket(eid: str) -> dict:
        return raw.setdefault(eid, {"entity_id": eid, "registry_no": "", "documents": [], "assertions": [],
                                    "filename_divergences": [], "unclassified_documents": [],
                                    "classified_checks": [], "rejected_documents": [], "ignored_after_as_of": []})

    parsed: list[tuple[str, str, Document | None]] = []
    for folder, rel, path in list_source_files(Path(input_dir)):
        data = jsonio.read_bytes(path)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            parsed.append((folder, rel, None))
            continue
        parsed.append((folder, rel, parse_document(text, rel, rules, jsonio.sha256_bytes(data))))
    known = known_names(Path(input_dir), [d for _, _, d in parsed if d is not None], rules)
    for folder, rel, doc in parsed:
        if doc is None:
            bucket(folder)["rejected_documents"].append({"file": rel, "reason": "not UTF-8 text"})
            continue
        eid = doc.entity_id or folder
        b = bucket(eid)
        if doc.registry_no and not b["registry_no"]:
            b["registry_no"] = doc.registry_no
        if rules.extract["parameters"]["synthetic_marker_required"] and not doc.marker_ok:
            b["rejected_documents"].append({"file": rel, "reason": "source document without the SYNTHETIC marker line"})
            continue
        if doc.problems:
            hc = holders_check(doc, rules)
            b["unclassified_documents"].append({"file": rel, "reason": "; ".join(doc.problems),
                                                "doc_id": doc.doc_id, "date": doc.date,
                                                "holders_check": hc, "fields_check": fields_check(doc, rules, hc)})
            continue
        if doc.date > as_of:
            b["ignored_after_as_of"].append(doc.doc_id)
            continue
        twin = next((d for d in b["documents"] if d["doc_id"] == doc.doc_id), None)
        if twin is not None:
            # two files under one document id: which one is "the" document is not ours to choose
            b["rejected_documents"].append({"file": rel, "reason": f"document id {doc.doc_id} is already used by "
                                                                   f"{twin['file'].rsplit('/', 1)[-1]}"})
            continue
        assertions = extract_document(doc, rules, known)
        b["documents"].append(doc.summary())
        b["assertions"].extend(assertions)
        check = classified_check(doc, assertions, rules, known)
        if check is not None:
            b["classified_checks"].append(check)
        b["filename_divergences"].extend(filename_divergences(doc, assertions, rules, folder))
    return raw


# ----------------------------------------------------------------------------------------------
# inline tests of the rules

_TEST_HEADER = ("{marker}\nDocument id: DOC-TEST\nDocument type: {type}\nDocument date: 2026-01-15\n"
                "Edition: TEST/1\nEntity: Test Entity S.r.l. (test registry no. TEST-REG-000001)\n{fy}\n")


def _test_doc(kind: str, body: str, rules: Rules, fy: str = "") -> Document:
    label = next(t["type"] for k in rules.extract["doc_kinds"] if k["kind"] == kind for t in k["tests"])
    head = _TEST_HEADER.format(marker=SYNTHETIC_MARKER, type=label, fy=f"Financial year: {fy}\n" if fy else "")
    return parse_document(head + body + "\n", "entities/E-0001/2026-01-15_test.txt", rules)


def run_inline_tests(rules: Rules) -> tuple[int, list[str]]:
    n, bad = 0, []
    for k in rules.extract["doc_kinds"]:
        for t in k.get("tests", []):
            n += 1
            got = classify_kind(t["type"], rules)
            if got != (t["expect"], k["id"]):
                bad.append(f"{k['id']}: {t['type']!r} -> {got}, expected {t['expect']}")
    for r in rules.extract["field_rules"]:
        for t in r.get("tests", []):
            n += 1
            doc = _test_doc(t["kind"], t["text"], rules, t.get("fy", ""))
            got = _EXTRACTORS[r["extractor"]](doc, r, rules) or []
            if t.get("expect_no_list"):            # the text holds no heading of the list at all (v2.0.4)
                if got:
                    bad.append(f"{r['id']}: a heading was found in {t['text']!r}, expected none")
                continue
            if r["extractor"] == "capital":
                seen = {a["field"].rsplit(".", 1)[-1]: a.get("value") for a in got if a["nature"] != "historical"}
                ok = seen == t["expect"]
            else:
                main = [a for a in got if not a["field"].endswith(".previous")]
                ok = len(main) == 1 and main[0].get("value") == t["expect"]
                if ok:
                    ok = main[0].get("stated_total") == t.get("expect_stated_total")
                if ok and "expect_previous" in t:
                    prev = [a for a in got if a["field"].endswith(".previous")]
                    ok = len(prev) == 1 and prev[0]["value"] == t["expect_previous"]
                seen = [a.get("value") for a in got]
            if not ok:
                bad.append(f"{r['id']}: got {seen}, expected {t['expect']}")
    for r in rules.extract["holders_evidence"]["rules"]:
        for t in r.get("tests", []):
            n += 1
            got = holders_evidence(t["text"], rules)["id"]
            if got != t["expect"] or got != r["id"]:
                bad.append(f"{r['id']}: line {t['text']!r} decided by {got}, expected {t['expect']}")
    for r in rules.extract["unread_fields"]["rules"]:
        for t in r.get("tests", []):
            n += 1
            got, ids = line_fields(t["text"], rules)
            if got != t["expect"] or r["id"] not in ids:
                bad.append(f"{r['id']}: line {t['text']!r} -> {got} by {ids}, expected {t['expect']}")
    for r in rules.extract["classified_lines"]["rules"]:
        for t in r.get("tests", []):
            n += 1
            doc = _test_doc(t["kind"], t["text"], rules, t.get("fy", ""))
            doc.entity_name = t.get("entity", "")            # a test without 'entity' has no own name to compare
            no = doc.body_start + 1 + t.get("line", 1)       # the line-th line of the test body
            known = {k: set(v) for k, v in t.get("known", {}).items()} or None
            got_rule, got = classify_line(doc, no, doc.lines[no - 1], _list_lines(doc, rules, known), rules, known)
            want = sorted(_field_name(f, doc) for f in t["expect"])
            if got_rule["id"] != r["id"] or sorted(got) != want:
                bad.append(f"{r['id']}: line {t.get('line', 1)} of {t['text']!r} -> {got} by {got_rule['id']}, "
                           f"expected {want}")
            if "expect_may_change" in t or "expect_may_change_unless_read" in t:
                found = extract_document(doc, rules, known)
                check = classified_check(doc, found, rules, known)
                may = check["fields_check"]["may_change"] if check else []
                want_may = t.get("expect_may_change")
                if want_may is None:     # (v2.0.7) what the line may change when no field rule of its kind reads it, and
                    #                      nothing when one does (scenario S09 adds such a rule for this wording)
                    want_may = [] if any("value" in a for a in found) else t["expect_may_change_unless_read"]
                if may != want_may:
                    bad.append(f"{r['id']}: {t['text']!r} may change {may}, expected {want_may}")
    for r in rules.figure_nature["rules"]:
        for t in r.get("tests", []):
            n += 1
            got = classify_natures(t["clause"], rules)[t["amount_index"]]
            if got["natures"] != t["expect"] or got["rule"] != r["id"]:
                bad.append(f"{r['id']}: amount {t['amount_index']} -> {got}, expected {t['expect']}")
    return n, bad
