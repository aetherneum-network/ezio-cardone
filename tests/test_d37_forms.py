"""D37 (v2.0.8): the never-event route of the blind run of v2.0.7 (eval/history.json run 18, hand corpus
eval/blind/hand-18, entity E-0015), closed by corroboration and equality, not by a longer word list or a tighter form.

E-0015: the deed states the registered office as a street, a number and a town; the registry extract states the same
address with words of the form of a place name inside the town. Every word passed the form test of v2.0.7 (each ends in
a vowel, none is of a class of slot_not_name_word), so v2.0.7 read the two as two addresses: the office was shown as a
DISCREPANCY and the share capital, whose change those words stated, as a fact. The gold keeps both [TO CONFIRM].

v2.0.8 (rules/extract.json address_corroboration, rules/discrepancy.json DISC-038):
- an address is a fact only when corroborated: stated equal, token for token, by two different documents of the
  entity, or stated by a recognised office transfer and repeated equal by a later source (ADR-020);
- an address equal to another of the entity plus words is not two addresses: its line is one that no rule explains
  (ADR-010: CLS-999, DISC-006 keeps every field [TO CONFIRM], OWN-015 blocks when it may state a holding), not a
  DISCREPANCY;
- an address that no second document states alike (ADR-999) cannot be checked: the document may change every other
  field (DISC-006), and the office stays [TO CONFIRM] when it is the only current statement of it (DISC-038);
- a genuine difference (two addresses neither of which is the other plus words) stays a DISCREPANCY side by side (A2).

The siblings are built by class (R6), never from the literal strings of hand-18: words of the form of a place name that
state a change of the capital, of the holders, of the directors or of the office, or that are a person's name of the
identity layer; in each position (in the town: after it, before it, between its words; in the street: before the
number, inside it, before it; inside the province's parentheses); in each place where the pack reads an address (deed,
registry extract, a label line of an extract, an office transfer's new and previous address, a label line of a share
transfer notice and of an appointment); with a second source that states the address without the words, and with one
source only. A case is unsafe when a field the words may change is published as fact, the office is published as fact
or shown as a DISCREPANCY with the words in it, or a holding is derived from a table the words may contradict. Every
wording passes the form test of v2.0.7 (each word ends in a vowel; none is in a word class). The same file was run on
the code of v2.0.6 and v2.0.7 (CHANGELOG 2.0.8 gives the count, by class).

D37_DeclaredForms: goals (b) and (d), the forms of hand-18 E-0020, E-0025, E-0026 (block) and E-0012 (the capital keeps
[TO CONFIRM]), by class; they behave the same on the code of v2.0.6 and v2.0.7 and are now declared limits.

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import sys
import unittest

from . import support as s
from .support import mk

from dossier.lib import jsonio

E = "E-0001"
NAME, FORM = mk.ENT[E]
H = [("P-001", "60%"), ("P-002", "40%")]
CAPITAL_FIELDS = ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")
OTHER = ("name", "legal_form", "directors", "shareholders", *CAPITAL_FIELDS)

# words of the form of an Italian place name (each ends in a vowel, none is of a class of slot_not_name_word) that state
# a change of another field, or that are the name of a person of the identity layer (P-003 of these inputs)
WORDS = (
    ("capital", "Capitale Raddoppiato", CAPITAL_FIELDS),
    ("holders", "Soci Cambiati", ("shareholders",)),
    ("holders", "Quote Cedute", ("shareholders",)),
    ("directors", "Ugo Presiede", ("directors",)),
    ("office", "Sede Trasferita", ()),
    ("identity-layer name", "Carlo Inventati", ("directors", "shareholders")),
)

# (position, the address without the words, the address with the words w)
POSITIONS = (
    ("town, after it", "Via Nuova 1, Montefinto (ZZ)", "Via Nuova 1, Montefinto {w} (ZZ)"),
    ("town, before it", "Via Nuova 1, Montefinto (ZZ)", "Via Nuova 1, {w} Montefinto (ZZ)"),
    ("town, between its words", "Via Nuova 1, San Fittizio (ZZ)", "Via Nuova 1, San {w} Fittizio (ZZ)"),
    ("street, before the number", "Via Nuova 1, Montefinto (ZZ)", "Via Nuova {w} 1, Montefinto (ZZ)"),
    ("street, inside it", "Via Nuova 1, Montefinto (ZZ)", "Via {w} Nuova 1, Montefinto (ZZ)"),
    ("street, before it", "Via Nuova 1, Montefinto (ZZ)", "{w} Via Nuova 1, Montefinto (ZZ)"),
    ("province, inside the parentheses", "Via Nuova 1, Montefinto (ZZ)", "Via Nuova 1, Montefinto (ZZ {w})"),
)
ROWS, DIRS = mk._holders(H), mk._directors(["P-001"])


def deed(office: str | None = mk.OFFICE_A):
    return mk._file(E, "2024-03-10_deed.txt", mk._head(E, 1, "Deed of incorporation", "2024-03-10", "DEED/1") + [
        f"1. Name and form. The company is named {NAME}; its legal form is {FORM}",
        f"2. Registered office. The registered office is at {office}.",
        "3. Share capital. " + mk.FULL.format(a="50.000,00"),
        "4. Holders.", *ROWS, "",
        "5. Directors.", *DIRS])


def extract(office: str = mk.OFFICE_A, extra=(), n: int = 2, date: str = "2025-02-01", ed: str = "EXTRACT/1"):
    return mk._file(E, f"{date}_registry-extract.txt", mk._head(E, n, "Test registry extract", date, ed) + [
        f"Name: {NAME}", f"Legal form: {FORM}", f"Registered office: {office}",
        "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00", *extra,
        "Holders:", *ROWS, "", "Directors:", *DIRS])


def later(kind: str, body: list[str], n: int = 3, date: str = "2026-08-20"):
    label, title, edition, slug = {
        "OFFICE": ("Transfer of registered office", None, "OFFICE/1", "office-transfer"),
        "TRANSFER": ("Share transfer notice", "Notice of a transfer of shares (synthetic).", "TRANSFER/1",
                     "share-transfer"),
        "APPOINTMENT": ("Appointment of directors", "Minutes of the holders' meeting (synthetic).", "APPOINTMENT/1",
                        "appointment_P-001"),
    }[kind]
    return mk._file(E, f"{date}_{slug}.txt", mk._head(E, n, label, date, edition) + ([title] if title else []) + body)


def moved(frm: str, to: str, n: int = 3, date: str = "2026-08-20"):
    return later("OFFICE", [f"The registered office is transferred from {frm} to {to}."], n, date)


def _places(plain: str, w_addr: str):
    """(place, sources, documents). 'two' = a second document states the address without the words; 'one' = no other
    document states the address the words are in."""
    yield "deed", "two", [deed(w_addr), extract(plain)]
    yield "deed", "one", [deed(w_addr)]
    yield "extract", "two", [deed(plain), extract(w_addr)]
    yield "extract", "one", [extract(w_addr)]
    yield "extract, label line", "two", [deed(plain), extract(plain, [f"Registered address: {w_addr}"])]
    yield "office transfer, new address", "one", [deed(), extract(), moved(mk.OFFICE_A, w_addr)]
    yield "office transfer, new address", "two", [deed(), extract(), moved(mk.OFFICE_A, w_addr),
                                                  extract(plain, n=4, date="2026-09-01", ed="EXTRACT/2")]
    yield "office transfer, previous address", "two", [deed(plain), extract(plain), moved(w_addr, mk.OFFICE_B)]
    yield "share transfer notice, label line", "two", [deed(plain), extract(plain), later(
        "TRANSFER", [f"Registered office: {w_addr}", "Holders after the transfer:", *ROWS])]
    yield "appointment, label line", "two", [deed(plain), extract(plain), later(
        "APPOINTMENT", [f"Registered office: {w_addr}", "Directors in office after this appointment:", *DIRS])]


def cases():
    for wname, w, changes in WORDS:
        for pos, plain, shape in POSITIONS:
            w_addr = shape.format(w=w)
            for place, sources, docs in _places(plain, w_addr):
                yield (wname, pos, place, sources), docs, changes, w


def genuine_cases():
    """A genuine difference (A2): the deed states one address, the extract a wholly different one with the words in it.
    v2.0.8 shows the office side by side as a DISCREPANCY and keeps every other field [TO CONFIRM] (neither address
    is stated by a second document)."""
    for wname, w, changes in WORDS:
        for pos, plain, shape in POSITIONS[:3]:
            yield (wname, pos, "deed vs extract", "genuine"), [deed(mk.OFFICE_A), extract(shape.format(w=w))], \
                changes, w


def _run(docs):
    work = s.tmp()
    code, _, report = s.run(s.tiny(docs, "2026-09-30"), work)
    status = report["entities"][E]["status"]
    view = jsonio.load(work / "views" / f"{E}.json") if (work / "views" / f"{E}.json").exists() else None
    prov_path = work / "dossiers" / E / "provenance.json"
    prov = jsonio.load(prov_path) if prov_path.exists() else None
    return status, view, prov


def unsafe(status: str, view: dict | None, prov: dict | None, changes, w: str, genuine: bool = False) -> str:
    """'' when the case is safe, else what was published wrongly. A FAILED entity is reported as such."""
    if status == "BLOCKED" and prov is None:
        return ""
    if status != "OK":
        return f"status {status}"
    fields = view["fields"]
    wrong = [f for f in changes if f in fields and fields[f]["status"] == "STATED"]
    office = fields.get("registered_office", {})
    if office.get("status") == "STATED":
        wrong.append("registered_office as fact")
    elif office.get("status") == "DISCREPANCY" and not genuine:
        wrong.append("registered_office as DISCREPANCY")
    if "shareholders" in changes and (prov["derived"] or [f for f in prov["figures"] if f["section"] == "cap_table"]):
        wrong.append("holdings derived")
    return ", ".join(wrong)


def tally(include_genuine: bool = True) -> dict:
    """{class: [cases, unsafe]} by words, position, place and sources, and the list of unsafe cases."""
    out: dict[str, dict[str, list[int]]] = {"words": {}, "position": {}, "place": {}, "sources": {}}
    bad = []
    every = [(k, d, c, w, False) for k, d, c, w in cases()]
    if include_genuine:
        every += [(k, d, c, w, True) for k, d, c, w in genuine_cases()]
    for key, docs, changes, w, genuine in every:
        why = unsafe(*_run(docs), changes, w, genuine)
        for axis, value in zip(("words", "position", "place", "sources"), key):
            row = out[axis].setdefault(value, [0, 0])
            row[0] += 1
            row[1] += bool(why)
        if why:
            bad.append((" | ".join(key), why))
    return {"by_class": out, "cases": len(every), "unsafe": len(bad), "unsafe_cases": bad}


N_CASES = sum(1 for _ in cases())
N_GENUINE = sum(1 for _ in genuine_cases())


class D37_AddressSiblings(unittest.TestCase):
    def test_every_sibling_is_safe(self):
        n = 0
        outcomes = s.sweep(_run, [(docs,) for _, docs, _, _ in cases()])
        for (key, docs, changes, w), outcome in zip(cases(), outcomes):
            with self.subTest(case=" | ".join(key)):
                n += 1
                self.assertEqual(unsafe(*outcome.result(), changes, w), "")
        self.assertEqual(n, N_CASES)

    def test_genuine_difference_side_by_side(self):
        """A2: the office side by side, every other field [TO CONFIRM] (each address has a single source)."""
        for key, docs, changes, w in genuine_cases():
            with self.subTest(case=" | ".join(key)):
                status, view, prov = _run(docs)
                self.assertEqual(unsafe(status, view, prov, changes, w, genuine=True), "")
                if status == "OK":
                    # a known person's or company's name inside an address leaves its line open (since v2.0.7, D36):
                    # that address is not read, there is no second value to show, and the office stays [TO CONFIRM].
                    # Since v2.0.9 (D38) the same holds for every second address of these cases: its words are not of
                    # the gazetteer (IDN-999). Two identified addresses are still side by side:
                    # tests/test_d38_identification.py D38_PlainStillPublishes.
                    want = "TO_CONFIRM"
                    self.assertEqual(view["fields"]["registered_office"]["status"], want)
                    self.assertTrue(all(view["fields"][f]["status"] == "TO_CONFIRM" for f in OTHER
                                        if f in view["fields"]), view["fields"])


class D37_CorroboratedAddresses(unittest.TestCase):
    """The cost side, and what corroboration still publishes."""

    def test_two_documents_alike_publish(self):
        # since v2.0.9 (D38) only addresses whose every word is of the gazetteer; the three others of v2.0.8 are in
        # tests/test_d36_forms.py D36_PlainAddressesStillRead.test_addresses_outside_the_gazetteer
        for addr in (mk.OFFICE_A, "Corso della Prova 12/B, Montefinto (ZZ)",
                     "Piazza Inventata 3, Valcollaudo (ZZ) - interno 4"):
            with self.subTest(addr=addr):
                status, view, prov = _run([deed(addr), extract(addr)])
                self.assertEqual(status, "OK")
                f = view["fields"]
                self.assertEqual((f["registered_office"]["status"], f["registered_office"].get("value")), ("STATED", addr))
                for fld in OTHER:
                    self.assertEqual(f[fld]["status"], "STATED", fld)

    def test_transfer_repeated_by_a_later_source(self):
        status, view, prov = _run([deed(), extract(), moved(mk.OFFICE_A, mk.OFFICE_B),
                                   extract(mk.OFFICE_B, n=4, date="2026-09-01", ed="EXTRACT/2")])
        self.assertEqual(status, "OK")
        self.assertEqual((view["fields"]["registered_office"]["status"], view["fields"]["registered_office"]["value"]),
                         ("STATED", mk.OFFICE_B))
        self.assertTrue(all(view["fields"][f]["status"] == "STATED" for f in OTHER))

    def test_transfer_as_the_last_document_keeps_the_office_to_confirm(self):
        """The price, declared in CHANGELOG 2.0.8: a new address that a transfer states and no later source repeats is
        not corroborated (DISC-038); its words cannot be checked, so the fields whose latest event is not newer than
        the transfer stay [TO CONFIRM] too (DISC-006). v2.0.7 published the new address (tests/test_d36_forms.py)."""
        status, view, prov = _run([deed(), extract(), moved(mk.OFFICE_A, mk.OFFICE_B)])
        self.assertEqual(status, "OK")
        self.assertEqual(view["fields"]["registered_office"]["status"], "TO_CONFIRM")
        self.assertTrue(all(view["fields"][f]["status"] == "TO_CONFIRM" for f in OTHER), view["fields"])

    def test_one_document_only_keeps_every_field_to_confirm(self):
        """The price, declared in CHANGELOG 2.0.8: an entity whose office only one document states."""
        status, view, prov = _run([deed()])
        self.assertEqual(status, "OK")
        self.assertTrue(all(f["status"] == "TO_CONFIRM" for f in view["fields"].values()), view["fields"])

    def test_record_says_why(self):
        """The record names the rule that decided each address and the mentions it rests on."""
        work = s.tmp()
        s.run(s.tiny([deed(), extract(mk.OFFICE_A + " - interno 2")], "2026-09-30"), work)
        rec = jsonio.load(work / "records" / f"{E}.json")
        why = " ".join(c["fields_check"]["why"] for c in rec["classified_checks"])
        self.assertIn("ADR-010", why)
        office = [a for a in rec["assertions"] if a["field"] == "registered_office"]
        self.assertTrue(office and all("value" not in a for a in office if a["source_doc"].endswith("-02")), office)


class D37_EqualityPremise(unittest.TestCase):
    """The premise of corroboration, stated in CHANGELOG 2.0.8 section 4: two documents of the entity that state the
    same address, words and all, were taken to state an address (hand-20 E-0009, eval/history.json run 20). Closed in
    v2.0.9 (D38): the agreement of the documents no longer accounts for any word; an address is taken as written only
    when every word is identified (rules/extract.json free_text_identification), so the case below keeps every field
    [TO CONFIRM]. The test keeps its name, and now states the opposite of v2.0.8."""

    def test_same_words_in_two_documents_are_corroborated(self):
        addr = "Via Nuova 1, Montefinto Capitale Raddoppiato (ZZ)"
        status, view, prov = _run([deed(addr), extract(addr)])
        self.assertEqual((status, view["fields"]["registered_office"]["status"]), ("OK", "TO_CONFIRM"))
        self.assertTrue(all(f["status"] == "TO_CONFIRM" for f in view["fields"].values()), view["fields"])


def _deed_with(holders_block: list[str], capital: str = mk.FULL.format(a="50.000,00")):
    return mk._file(E, "2024-03-10_deed.txt", mk._head(E, 1, "Deed of incorporation", "2024-03-10", "DEED/1") + [
        f"1. Name and form. The company is named {NAME}; its legal form is {FORM}",
        f"2. Registered office. The registered office is at {mk.OFFICE_A}.",
        "3. Share capital. " + capital,
        *holders_block, "",
        "5. Directors.", *DIRS])


def _extract_with(holders_block: list[str]):
    return mk._file(E, "2025-02-01_registry-extract.txt", mk._head(E, 2, "Test registry extract", "2025-02-01",
                                                                   "EXTRACT/1") + [
        f"Name: {NAME}", f"Legal form: {FORM}", f"Registered office: {mk.OFFICE_A}",
        "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00",
        *holders_block, "", "Directors:", *DIRS])


class D37_DeclaredForms(unittest.TestCase):
    """Goals (b) and (d) of D37: the forms of hand-18 that were neither read nor declared, by class, with fixtures of
    this file (never the literal lines of hand-18). Each is a known limit of CHANGELOG 2.0.8 with its class."""

    BLOCKS = {
        # E-0020: holder rows that name the holder by a person's name alone, no identifier, under a numbered heading
        # of another noun; and each of the two apart
        "rows by name alone, heading of another noun": [_deed_with(["4. Members of the company.", "- Aldo Finti: 60%",
                                                                    "- Bice Provetti: 40%"]), extract()],
        "rows by name alone, holders' heading": [_deed_with(["4. Holders.", "- Aldo Finti: 60%",
                                                             "- Bice Provetti: 40%"]), extract()],
        "rows with identifiers, heading of another noun": [_deed_with(["4. Members of the company.", *ROWS]),
                                                           extract()],
        # E-0025: a lettered item with the share before the holder, separated by a vertical bar
        "lettered item, share | holder": [deed(), _extract_with(["Quotaholders of the company:",
                                                                 "a) 60% | P-001 (Aldo Finti)",
                                                                 "b) 40% | P-002 (Bice Provetti)"])],
        # E-0026: an ordinal word before the holders' heading, shares in words or in figures
        "ordinal word before the heading, shares in words": [_deed_with(["Fourth. Holders:",
                                                                         "- P-001 (Aldo Finti): sixty per cent",
                                                                         "- P-002 (Bice Provetti): forty per cent"]),
                                                             extract()],
        "ordinal word before the heading, shares in figures": [_deed_with(["Fourth. Holders:", *ROWS]), extract()],
    }
    # E-0012: the capital in a sentence of a shape the pack does not have (CLS-999 -> DISC-006)
    KEEPS = {
        "capital brought in by the founders": [_deed_with(["4. Holders.", *ROWS], "The founders bring in EUR "
                                               "50.000,00, all of it paid on signing."), extract()],
        "capital brought in by the founders, deed alone": [_deed_with(["4. Holders.", *ROWS], "The founders bring in "
                                                           "EUR 50.000,00, all of it paid on signing.")],
    }
    # controls: the nearest forms that are read (their values agree with the deed's)
    READ = {
        "lettered item, holder: share": [deed(), _extract_with(["Holders:", "a) P-001 (Aldo Finti): 60%",
                                                                "b) P-002 (Bice Provetti): 40%"])],
        "dash item, share | holder": [deed(), _extract_with(["Holders:", "- 60% | P-001 (Aldo Finti)",
                                                             "- 40% | P-002 (Bice Provetti)"])],
    }

    def test_blocks(self):
        for k, docs in self.BLOCKS.items():
            with self.subTest(form=k):
                status, view, prov = _run(docs)
                self.assertEqual(status, "BLOCKED")
                self.assertFalse(view and [f for f, v in view["fields"].items() if v["status"] == "STATED"])

    def test_keeps_to_confirm(self):
        for k, docs in self.KEEPS.items():
            with self.subTest(form=k):
                status, view, prov = _run(docs)
                self.assertEqual(status, "OK")
                for f in CAPITAL_FIELDS:
                    self.assertEqual(view["fields"][f]["status"], "TO_CONFIRM", f)

    def test_controls_read(self):
        for k, docs in self.READ.items():
            with self.subTest(form=k):
                status, view, prov = _run(docs)
                self.assertEqual(status, "OK")
                self.assertEqual(view["fields"]["shareholders"]["status"], "STATED")


if __name__ == "__main__":
    import json
    json.dump(tally(), sys.stdout, indent=1, ensure_ascii=False)
    print()
