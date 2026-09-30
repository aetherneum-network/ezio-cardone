"""Stage 1 - assertions from source documents, with abstention.

A source document is a UTF-8 text file: a header block (``Key: value`` lines up to the first blank
line) and a body. Each rule of ``rules/extract.json`` turns one place of one document into one
assertion ``{field, value, source_doc, source_date, edition, ...}``. What a rule cannot read is an
assertion with status ``TO_CONFIRM`` and a reason - never a guess:

* an illegible figure, an amount in an unknown or ambiguous form;
* a holders' table or a directors' list with one line that cannot be read (the whole table abstains);
* an amount whose nature (resolved, subscribed, paid in) the text does not give;
* a field that the kind of document is expected to state and no rule found.

Facts come from the content. The file name is compared with the content and a divergence is
reported; it is never a source.
"""
from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import SYNTHETIC_MARKER
from .lib import jsonio
from .lib.numbers import frac_str, parse_amount, parse_share
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


def _pattern(rule: dict, rules: Rules) -> re.Pattern:
    return rx(rule["line_matches"].replace("{amount_token}", rules.extract["parameters"]["amount_token"]))


def _body(doc: Document) -> list[tuple[int, str]]:
    """(1-based line number, text) of every body line."""
    return [(i + 1, doc.lines[i]) for i in range(doc.body_start, len(doc.lines))]


def _extract_text(doc: Document, rule: dict, rules: Rules) -> list[dict] | None:
    pat = _pattern(rule, rules)
    for no, text in _body(doc):
        m = pat.search(text)
        if not m:
            continue
        out = []
        value = m.group("value").strip()
        fld = _field_name(rule["field"], doc)
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
        value, why = parse_amount(m.group("amt"))
        return [_assertion(doc, _field_name(rule["field"], doc), rule["nature"], rule["id"], value=value,
                           reason=why, line=no, quote=text)]
    return None


def amount_spans(clause: str, rules: Rules) -> list[tuple[int, int, str]]:
    """(start of the currency marker, end of the token, token) of every amount in a clause."""
    p = rules.extract["parameters"]
    pat = rx(p["currency_prefix"] + "(?P<amt>" + p["amount_token"] + ")")
    return [(m.start(), m.end(), m.group("amt")) for m in pat.finditer(clause)]


def classify_natures(clause: str, rules: Rules) -> list[dict]:
    """The nature of every amount of a capital clause, by the ordered rules of figure_nature.json."""
    spans = amount_spans(clause, rules)
    segs = []
    for i, (start, end, token) in enumerate(spans):
        pre = clause[spans[i - 1][1] if i else 0:start]
        post = clause[end:spans[i + 1][0] if i + 1 < len(spans) else len(clause)]
        segs.append({"token": token, "pre": pre, "post": post})
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
        out.append({"token": s["token"], "natures": natures, "rule": r["id"] if r else ""})
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
        value, why = parse_amount(amt["token"])
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


def _block(doc: Document, heading_no: int) -> list[tuple[int, str]]:
    """The non-empty lines that follow a heading, up to the first blank line."""
    out = []
    for no, text in _body(doc):
        if no <= heading_no:
            continue
        if not text.strip():
            break
        out.append((no, text))
    return out


def _extract_list(doc: Document, rule: dict, rules: Rules) -> list[dict] | None:
    heading = _pattern(rule, rules)
    item = rx(rule["item_matches"])
    fld = _field_name(rule["field"], doc)
    for no, text in _body(doc):
        if not heading.search(text.strip()):
            continue
        block = _block(doc, no)
        quote = "\n".join([text] + [t for _, t in block])
        end = block[-1][0] if block else no

        def abstain(why: str) -> list[dict]:
            return [_assertion(doc, fld, rule["nature"], rule["id"], reason=why, line=no, line_end=end, quote=quote)]

        if not block:
            return abstain("the list is empty")
        ids: list[str] = []
        rows: list[dict] = []
        for _, line in block:
            m = item.match(line)
            if not m:
                return abstain("a line of the list could not be read")
            if m.group("id") in ids:
                return abstain(f"{m.group('id')} is listed twice")
            ids.append(m.group("id"))
            if rule["extractor"] == "holders":
                share, why = parse_share(m.group("share"))
                if share is None:
                    return abstain(f"share of {m.group('id')}: {why}")
                if share <= 0:
                    return abstain(f"share of {m.group('id')} is not positive")
                rows.append({"holder": m.group("id"), "share": frac_str(share)})
        value = sorted(rows, key=lambda r: r["holder"]) if rule["extractor"] == "holders" else sorted(ids)
        return [_assertion(doc, fld, rule["nature"], rule["id"], value=value, line=no, line_end=end, quote=quote)]
    return None


_EXTRACTORS = {"text": _extract_text, "amount": _extract_amount, "capital": _extract_capital,
               "holders": _extract_list, "directors": _extract_list}


def extract_document(doc: Document, rules: Rules) -> list[dict]:
    """Every assertion of one classified document, abstentions included."""
    if doc.kind == "UNKNOWN":
        return []
    out: list[dict] = []
    done: set[str] = set()
    for rule in rules.extract["field_rules"]:
        if doc.kind not in rule["kinds"] or rule["field"] in done:
            continue
        got = _EXTRACTORS[rule["extractor"]](doc, rule, rules)
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


def extract_corpus(input_dir: Path | str, rules: Rules, as_of: str) -> dict[str, dict]:
    """Raw extraction of a whole input folder, keyed by the entity each document names in its content."""
    raw: dict[str, dict] = {}

    def bucket(eid: str) -> dict:
        return raw.setdefault(eid, {"entity_id": eid, "registry_no": "", "documents": [], "assertions": [],
                                    "filename_divergences": [], "unclassified_documents": [],
                                    "rejected_documents": [], "ignored_after_as_of": []})

    for folder, rel, path in list_source_files(Path(input_dir)):
        data = jsonio.read_bytes(path)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            bucket(folder)["rejected_documents"].append({"file": rel, "reason": "not UTF-8 text"})
            continue
        doc = parse_document(text, rel, rules, jsonio.sha256_bytes(data))
        eid = doc.entity_id or folder
        b = bucket(eid)
        if doc.registry_no and not b["registry_no"]:
            b["registry_no"] = doc.registry_no
        if rules.extract["parameters"]["synthetic_marker_required"] and not doc.marker_ok:
            b["rejected_documents"].append({"file": rel, "reason": "source document without the SYNTHETIC marker line"})
            continue
        if doc.problems:
            b["unclassified_documents"].append({"file": rel, "reason": "; ".join(doc.problems),
                                                "doc_id": doc.doc_id, "date": doc.date})
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
        assertions = extract_document(doc, rules)
        b["documents"].append(doc.summary())
        b["assertions"].extend(assertions)
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
            if r["extractor"] == "capital":
                seen = {a["field"].rsplit(".", 1)[-1]: a.get("value") for a in got if a["nature"] != "historical"}
                ok = seen == t["expect"]
            else:
                main = [a for a in got if not a["field"].endswith(".previous")]
                ok = len(main) == 1 and main[0].get("value") == t["expect"]
                if ok and "expect_previous" in t:
                    prev = [a for a in got if a["field"].endswith(".previous")]
                    ok = len(prev) == 1 and prev[0]["value"] == t["expect_previous"]
                seen = [a.get("value") for a in got]
            if not ok:
                bad.append(f"{r['id']}: got {seen}, expected {t['expect']}")
    for r in rules.figure_nature["rules"]:
        for t in r.get("tests", []):
            n += 1
            got = classify_natures(t["clause"], rules)[t["amount_index"]]
            if got["natures"] != t["expect"] or got["rule"] != r["id"]:
                bad.append(f"{r['id']}: amount {t['amount_index']} -> {got}, expected {t['expect']}")
    return n, bad
