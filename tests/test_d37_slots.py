"""D37 (v2.0.8), the other free-text slots: the principle of tests/test_d37_forms.py (corroboration and equality, not
a longer word list or a tighter form) applied to every slot whose words were decided by form or by a word list.

The census of the slots of rules/extract.json classified_lines (CHANGELOG 2.0.8, section 4): the addresses
(w_office, w_previous: tests/test_d37_forms.py); the company's name (the header line 'Entity:', and the slots of the
entity's own name w_name, which since v2.0.6 must be the name of their header); the title of CLS-900 (w_title); the
label of CLS-250 (w_label). The person's name beside an identifier (w_person, CLS-005, CLS-240) was already decided by
equality with the identity layer (v2.0.6, v2.0.7); the document type by equality with doc_kinds (KIND-010..080).

Until v2.0.7 a company's name in a header could hold any words (nothing compared the header with another one); a title
or a label passed when its words named no field of another kind by the topic words (slot_topics) - words of another
language, or of no list, passed. v2.0.8 (rules/extract.json name_corroboration, text_corroboration, rules/discrepancy.json
DISC-038):
- a header name equal to another header name of the entity plus words makes its document one that no rule explains
  (NAM-010: DISC-006 keeps every field [TO CONFIRM], OWN-015 blocks when the name may state a holding), and no name of
  that document is read; a header name that no second document states alike (NAM-999) leaves every other field of its
  document [TO CONFIRM], and the name [TO CONFIRM] when it is its only current source (DISC-038);
- a title or a label closes its line only when another document of the input states it alike or the pack's own
  builders write it (TXT-020); otherwise (TXT-010 plus words, TXT-999 alone) the line is read by no rule (CLS-999).

The siblings are built by class (R6), with the words of tests/test_d37_forms.py (of the form of a place name, stating a
change of another field, or a person's name of the identity layer), in each position of a name (before its legal form,
inside it, before it), in each place where the pack reads a header, a name slot, a title, a label or a heading; with a
second source that states the text without the words, and with one source only. A case is published wrongly when a
field the words may change is published as fact, the name is published as fact with the words in it or shown as a
DISCREPANCY with them, or a holding is derived from a table the words may contradict. A case that ends FAILED publishes
nothing and is counted apart, with its reason: the one FAILED that v2.0.8 keeps is fail-closed by design - a company's
name that holds a person's name of the identity layer and that no second document refuses is listed beside its
[TO CONFIRM] field, and the leak check of the shareable layer (A6) refuses the entity (CHANGELOG 2.0.8, known limits:
blocks). The same file was run on the code of v2.0.6 and v2.0.7 (CHANGELOG 2.0.8 gives the counts, by class).

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import sys
import unittest

from . import support as s
from .support import mk
from .test_d37_forms import (CAPITAL_FIELDS, DIRS, E, NAME, OTHER, ROWS, WORDS, deed, extract, later)

from dossier.lib import jsonio

CHANGES = {"capital": CAPITAL_FIELDS, "holders": ("shareholders",), "directors": ("directors",),
           "office": ("registered_office",), "identity-layer name": ("directors", "shareholders")}
BARE, LEGAL = NAME.rsplit(" ", 1)              # the name without its legal form, and the form
FIRST, REST = BARE.split(" ", 1)
NAME_POSITIONS = (
    ("before the legal form", f"{BARE} {{w}} {LEGAL}"),
    ("inside the name", f"{FIRST} {{w}} {REST} {LEGAL}"),
    ("before the name", f"{{w}} {BARE} {LEGAL}"),
)
TR_ROWS = ["Holders after the transfer:", *ROWS]
AP_ROWS = ["Directors in office after this appointment:", *DIRS]


def _head(doc, wn):
    """The header line 'Entity:' of a document with the name ``wn``."""
    rel, text = doc
    old = f"Entity: {NAME} ("
    assert old in text
    return rel, text.replace(old, f"Entity: {wn} (")


def _all(doc, wn):
    """The header and every slot of the entity's own name with the name ``wn``."""
    rel, text = doc
    assert text.count(NAME) >= 2
    return rel, text.replace(NAME, wn)


def _slot(doc, old_line, new_line):
    rel, text = doc
    assert old_line in text
    return rel, text.replace(old_line, new_line)


def _name_places(wn):
    """(place, sources, documents): 'two' = another document states the name without the words; 'one' = none."""
    yield "deed, header and name", "two", [_all(deed(), wn), extract()]
    yield "deed, header only", "two", [_head(deed(), wn), extract()]
    yield "extract, header and name", "two", [deed(), _all(extract(), wn)]
    yield "extract, header only", "two", [deed(), _head(extract(), wn)]
    yield "extract, name slot only", "two", [deed(), _slot(extract(), f"Name: {NAME}", f"Name: {wn}")]
    yield "extract, company label line", "two", [deed(), _slot(_head(extract(), wn), f"Name: {NAME}",
                                                               f"Company name: {wn}")]
    yield "share transfer notice, header", "two", [deed(), extract(), _head(later("TRANSFER", TR_ROWS), wn)]
    yield "appointment, header", "two", [deed(), extract(), _head(later("APPOINTMENT", AP_ROWS), wn)]
    yield "later extract, header and name", "two", [deed(), extract(), _all(extract(n=3, date="2026-08-20",
                                                                                    ed="EXTRACT/2"), wn)]
    yield "later extract, header only", "two", [deed(), extract(), _head(extract(n=3, date="2026-08-20",
                                                                                 ed="EXTRACT/2"), wn)]
    yield "deed, header and name", "one", [_all(deed(), wn)]
    yield "extract, header and name", "one", [_all(extract(), wn)]
    yield "share transfer notice, header", "one", [_head(later("TRANSFER", TR_ROWS), wn)]


def _titled(kind, title, lines):
    rel, text = later(kind, lines)
    std = {"TRANSFER": "Notice of a transfer of shares (synthetic).",
           "APPOINTMENT": "Minutes of the holders' meeting (synthetic)."}[kind]
    return rel, text.replace(std + "\n", title + "\n")


def _text_places(w):
    """(place, sources, documents) of a title, a label or a heading with the words ``w``. 'two' = the documents of
    the input state the text without the words (the builders' own titles and headings); 'one' = a text of the hand's
    own, stated once."""
    yield "transfer title, end", "two", [deed(), extract(), _titled(
        "TRANSFER", f"Notice of a transfer of shares {w} (synthetic).", TR_ROWS)]
    yield "transfer title, inside", "two", [deed(), extract(), _titled(
        "TRANSFER", f"Notice of a {w} transfer of shares (synthetic).", TR_ROWS)]
    yield "appointment title, end", "two", [deed(), extract(), _titled(
        "APPOINTMENT", f"Minutes of the holders' meeting {w} (synthetic).", AP_ROWS)]
    yield "appointment title of the hand's own", "one", [deed(), extract(), _titled(
        "APPOINTMENT", f"Minutes - change of the board {w} (synthetic).", AP_ROWS)]
    yield "extract label line (office)", "one", [deed(), extract(extra=[f"Office {w}: {mk.OFFICE_A}"])]
    yield "extract label line (office), label stated plain elsewhere", "two", [
        deed(), extract(extra=[f"Office: {mk.OFFICE_A}"]),
        extract(extra=[f"Office {w}: {mk.OFFICE_A}"], n=3, date="2026-08-20", ed="EXTRACT/2")]
    yield "transfer label line (office)", "one", [deed(), extract(), later(
        "TRANSFER", [f"Registered office {w}: {mk.OFFICE_A}", *TR_ROWS])]
    yield "appointment label line (seat)", "one", [deed(), extract(), later(
        "APPOINTMENT", [f"Seat {w}: {mk.OFFICE_A}", *AP_ROWS])]
    yield "transfer label line (company)", "one", [deed(), extract(), later(
        "TRANSFER", [f"Company {w}: {NAME}", *TR_ROWS])]
    yield "transfer heading", "two", [deed(), extract(), later("TRANSFER", [f"Holders after the transfer {w}:", *ROWS])]
    yield "appointment heading", "two", [deed(), extract(), later(
        "APPOINTMENT", [f"Directors in office after this appointment {w}:", *DIRS])]


def cases():
    for wname, w, _ in WORDS:
        for pos, shape in NAME_POSITIONS:
            for place, sources, docs in _name_places(shape.format(w=w)):
                yield ("name", wname, pos, place, sources), docs, CHANGES[wname], w
        for place, sources, docs in _text_places(w):
            yield ("title or label", wname, "-", place, sources), docs, CHANGES[wname], w


LEAK = "shareable layer leaks"


def _run(docs):
    """(status, reason, view, provenance) of the one entity of a tiny input, as of 2026-09-30."""
    work = s.tmp()
    code, _, report = s.run(s.tiny(docs, "2026-09-30"), work)
    ent = report["entities"][E]
    view = jsonio.load(work / "views" / f"{E}.json") if (work / "views" / f"{E}.json").exists() else None
    prov_path = work / "dossiers" / E / "provenance.json"
    prov = jsonio.load(prov_path) if prov_path.exists() else None
    return ent["status"], ent.get("reason", ""), view, prov


def fail_closed(key) -> bool:
    """The class whose FAILED is fail-closed by design (A6): a person's name of the identity layer in the company's
    name of a header, with no second document whose header refuses it."""
    return key[0] == "name" and key[1] == "identity-layer name" and key[4] == "one"


def unsafe(status: str, reason: str, view: dict | None, prov: dict | None, changes, w: str) -> str:
    """'' when nothing is published wrongly, 'FAILED: <reason>' when the entity fails (nothing is published), else
    what was published wrongly."""
    if status == "BLOCKED" and prov is None:
        return ""
    if status == "FAILED":
        return f"FAILED: {reason}"
    if status != "OK":
        return f"status {status}"
    fields = view["fields"]
    wrong = [f for f in changes if f in fields and fields[f]["status"] == "STATED"]
    name = fields.get("name", {})
    if name.get("status") == "STATED" and w in str(name.get("value")):
        wrong.append("name with the words as fact")
    elif name.get("status") == "DISCREPANCY":
        wrong.append("name as DISCREPANCY")
    if "shareholders" in changes and (prov["derived"] or [f for f in prov["figures"] if f["section"] == "cap_table"]):
        wrong.append("holdings derived")
    return ", ".join(wrong)


def tally() -> dict:
    """{class: [cases, published wrongly, FAILED]} by slot, words, position, place and sources, and the cases."""
    axes = ("slot", "words", "position", "place", "sources")
    out: dict[str, dict[str, list[int]]] = {a: {} for a in axes}
    wrong, failed = [], []
    n = 0
    for key, docs, changes, w in cases():
        n += 1
        why = unsafe(*_run(docs), changes, w)
        for axis, value in zip(axes, key):
            row = out[axis].setdefault(value if axis != "place" else f"{key[0]}: {value}", [0, 0, 0])
            row[0] += 1
            row[1] += bool(why) and not why.startswith("FAILED")
            row[2] += why.startswith("FAILED")
        if why:
            (failed if why.startswith("FAILED") else wrong).append((" | ".join(key), why))
    return {"by_class": out, "cases": n, "published_wrongly": len(wrong), "failed": len(failed),
            "failed_fail_closed_class": sum(fail_closed(tuple(k.split(" | "))) and LEAK in why for k, why in failed),
            "published_wrongly_cases": wrong, "failed_cases": failed}


N_CASES = sum(1 for _ in cases())


class D37_SlotSiblings(unittest.TestCase):
    def test_no_sibling_is_published_wrongly(self):
        """No sibling publishes wrongly; the only FAILED is the fail-closed class, refused by the leak check."""
        n = n_failed = 0
        outcomes = s.sweep(_run, [(docs,) for _, docs, _, _ in cases()])
        for (key, docs, changes, w), outcome in zip(cases(), outcomes):
            with self.subTest(case=" | ".join(key)):
                n += 1
                why = unsafe(*outcome.result(), changes, w)
                if why.startswith("FAILED"):
                    n_failed += 1
                    self.assertTrue(fail_closed(key) and LEAK in why, why)
                else:
                    self.assertEqual(why, "")
        self.assertEqual(n, N_CASES)
        self.assertLessEqual(n_failed, sum(1 for key, *_ in cases() if fail_closed(key)))


class D37_CorroboratedNamesAndTexts(unittest.TestCase):
    """The cost side, and what corroboration still publishes."""

    def test_plain_documents_still_publish(self):
        """Two documents whose headers name the company alike, the builders' own titles and headings: every field."""
        for docs in ([deed(), extract()],
                     [deed(), extract(), later("TRANSFER", TR_ROWS)],
                     [deed(), extract(), later("APPOINTMENT", AP_ROWS)]):
            with self.subTest(docs=[d[0] for d in docs]):
                status, _, view, prov = _run(docs)
                self.assertEqual(status, "OK")
                self.assertTrue(all(view["fields"][f]["status"] == "STATED" for f in OTHER), view["fields"])

    def test_a_legal_form_that_differs_is_not_words(self):
        """The legal form at the end of a name is set aside (it is DISC-035's): the header names stay corroborated."""
        other = "S.p.A." if LEGAL != "S.p.A." else "S.r.l."
        status, _, view, prov = _run([deed(), _head(extract(), f"{BARE} {other}")])
        self.assertEqual(status, "OK")
        self.assertEqual(view["fields"]["registered_office"]["status"], "STATED")

    def test_a_label_two_documents_state_alike_no_longer_closes(self):
        """v2.0.8: a label of the hand's own, stated alike by a second document of the input, closed its line (TXT-020).
        Since v2.0.9 (D38) the agreement of two documents accounts for none of its words: TXT-020 leaves the line read
        by no rule, and the documents that carry it may change every field (DISC-006)."""
        docs = [deed(), extract(extra=[f"Registered address: {mk.OFFICE_A}"]),
                extract(extra=[f"Registered address: {mk.OFFICE_A}"], n=3, date="2026-08-20", ed="EXTRACT/2")]
        work = s.tmp()
        s.run(s.tiny(docs, "2026-09-30"), work)
        rec = jsonio.load(work / "records" / f"{E}.json")
        why = " ".join(c["fields_check"]["why"] for c in rec["classified_checks"])
        self.assertIn("TXT-020", why)
        labelled = [c for c in rec["classified_checks"] if not c["doc_id"].endswith("-01")]
        self.assertTrue(labelled and all(c["fields_check"]["may_change"] == ["*"] for c in labelled), why)

    def test_a_label_stated_once_is_read_by_no_rule(self):
        """The price, declared in CHANGELOG 2.0.8: a label of the hand's own that no second document states (TXT-999)."""
        work = s.tmp()
        s.run(s.tiny([deed(), extract(extra=[f"Registered address: {mk.OFFICE_A}"])], "2026-09-30"), work)
        rec = jsonio.load(work / "records" / f"{E}.json")
        check = next(c for c in rec["classified_checks"] if c["doc_id"].endswith("-02"))
        self.assertEqual(check["fields_check"]["may_change"], ["*"])
        self.assertIn("TXT-999", check["fields_check"]["why"])

    def test_a_genuine_rename_side_by_side(self):
        """Two whole different names (neither is the other plus words): a DISCREPANCY side by side (DISC-020), and
        every other field [TO CONFIRM] (neither name is stated by a second document, NAM-999)."""
        # since v2.0.9 (D38) the second name is of the gazetteer, so that it is identified (v2.0.8: Officine Boreali)
        status, _, view, prov = _run([deed(), _all(extract(), f"Officine Valfittizia {LEGAL}")])
        self.assertEqual(status, "OK")
        self.assertEqual(view["fields"]["name"]["status"], "DISCREPANCY")
        self.assertTrue(all(view["fields"][f]["status"] == "TO_CONFIRM" for f in OTHER if f != "name"), view["fields"])

    def test_record_says_why(self):
        work = s.tmp()
        s.run(s.tiny([deed(), _all(extract(), f"{BARE} Soci Cambiati {LEGAL}")], "2026-09-30"), work)
        rec = jsonio.load(work / "records" / f"{E}.json")
        why = " ".join(c["fields_check"]["why"] for c in rec["classified_checks"])
        self.assertIn("NAM-010", why)
        self.assertIn("NAM-999", why)
        names = [a for a in rec["assertions"] if a["field"] == "name"]
        self.assertTrue(all("value" not in a for a in names if a["source_doc"].endswith("-02")), names)
        self.assertTrue(all(a.get("corroboration", {}).get("rule") == "NAM-999" for a in names
                            if a["source_doc"].endswith("-01")), names)


class D37_NameEqualityPremise(unittest.TestCase):
    """The premise of corroboration, as for addresses (tests/test_d37_forms.py D37_EqualityPremise): in v2.0.8 two
    documents of the entity whose headers state the same name, words and all, were taken to name the company (hand-20
    E-0010, eval/history.json run 20). Closed in v2.0.9 (D38): a header name is a fact only when it is identified word
    by word (NAM-005 before NAM-020), so the name and every field stay [TO CONFIRM]. The test keeps its name, and now
    states the opposite of v2.0.8."""

    def test_same_words_in_two_headers_are_corroborated(self):
        wn = f"{BARE} Capitale Raddoppiato {LEGAL}"
        status, _, view, prov = _run([_all(deed(), wn), _all(extract(), wn)])
        self.assertEqual((status, view["fields"]["name"]["status"]), ("OK", "TO_CONFIRM"))
        self.assertTrue(all(f["status"] != "STATED" for f in view["fields"].values()), view["fields"])


if __name__ == "__main__":
    import json
    json.dump(tally(), sys.stdout, indent=1, ensure_ascii=False)
    print()
