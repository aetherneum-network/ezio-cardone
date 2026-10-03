"""D38 (v2.0.9): the never-event route of hand-20 (eval/history.json run 20, hand corpus eval/blind/hand-20), closed by
POSITIVE identification of every word of a free-text slot, not by a longer word list or a tighter form.

E-0009: the deed and the registry extract state the registered office alike, with words that state a capital inside the
town ('... Dotazione Novantamila'); E-0010: every header and the name clauses state the company's name alike, with the
same words before the legal form. v2.0.8 took two documents that agree to account for the words (address_corroboration
ADR-020, name_corroboration NAM-020): the office and the name were shown as facts, and the share capital too. The gold
keeps them [TO CONFIRM].

v2.0.9 (rules/extract.json free_text_identification, the gazetteer parameters): a slot of an address, a company's name,
a person's name, a title or a label closes its line only when every word of it is identified - the street a type of a
closed list and a name of the gazetteer, the house number of the slot grammar, the town and the province of the
gazetteer; a company's name a trade and a town of the gazetteer before its legal form; a person's name a first name and a
surname of the gazetteer; a title or a label a recognised text -, whatever the other documents say. A numeral anywhere but
the house number makes the slot one that may state a quantity (IDN-010). Anything not identified makes the line one that no
rule explains: every field [TO CONFIRM] (DISC-006), and a block when it may state a holding (OWN-015).

The siblings are built by class (R6), never from the literal strings of hand-20: words that state a change of the capital,
of the holders, of the directors or of the office; with and without a numeral; of the form of an Italian place name and of
another form; in the town, the street, the province, the company's name (before the legal form, after its first word,
before it, after the legal form, inside the legal form), a title and a label; stated alike by 2 and by 3 documents (the
run-20 class), and by one document beside a second that states the slot without them (the run-18 class). A case is unsafe
when a field the words may change is published as fact, when the slot that holds the words (the office, the name) is
published as fact or shown as a DISCREPANCY, or when a holding is derived from a table the words may contradict. The same
file was run on the code of v2.0.7 and v2.0.8 (``python -m tests.test_d38_identification``, CHANGELOG 2.0.9 gives the
count by class).

D38_OwnNameStreetWord: goal (b), both ways - an own name that holds a street word ('Borgo', 'Corso', 'Largo', 'Viale') is
decided by identification, never by the topic words of the office (hand-20 E-0007, E-0020).

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import json
import shutil
import sys
import unittest
from functools import lru_cache

from . import ROOT
from . import support as s
from .support import mk

from dossier.lib import jsonio

E = "E-0001"
NAME, FORM = mk.ENT[E]                       # a name of the gazetteer: trade and town, then the legal form
BARE = NAME[:-len(FORM)].strip()
FIRST, REST = BARE.split(" ", 1)
H = [("P-001", "60%"), ("P-002", "40%")]
ROWS, DIRS = mk._holders(H), mk._directors(["P-001"])
OFFICE = mk.OFFICE_A                         # "Via del Collaudo 7, Borgoprova (ZZ)": every word of the gazetteer
CAPITAL_FIELDS = ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")
OTHER = ("name", "legal_form", "registered_office", "directors", "shareholders", *CAPITAL_FIELDS)

# (field the words change, the words, their form, whether they hold a numeral, the fields they may change)
WORDS = (
    ("capital", "Dotazione Novantamila", "place-name", True, CAPITAL_FIELDS),
    ("capital", "Capitale Raddoppiato", "place-name", False, CAPITAL_FIELDS),
    ("capital", "Capital Ninety Thousand", "other", True, CAPITAL_FIELDS),
    ("capital", "Capital Doubled", "other", False, CAPITAL_FIELDS),
    ("holders", "Quote Sessanta", "place-name", True, ("shareholders",)),
    ("holders", "Soci Cambiati", "place-name", False, ("shareholders",)),
    ("holders", "Holder Sixty", "other", True, ("shareholders",)),
    ("holders", "Shares Sold", "other", False, ("shareholders",)),
    ("directors", "Consiglieri Tre", "place-name", True, ("directors",)),
    ("directors", "Ugo Presiede", "place-name", False, ("directors",)),
    ("directors", "Two Directors", "other", True, ("directors",)),
    ("directors", "Board Changed", "other", False, ("directors",)),
    ("office", "Sede Numero Due", "place-name", True, ("registered_office",)),
    ("office", "Sede Trasferita", "place-name", False, ("registered_office",)),
    ("office", "Seat Number Two", "other", True, ("registered_office",)),
    ("office", "Seat Moved", "other", False, ("registered_office",)),
)

# (slot, position, the slot's text with the words w); the address slots are the registered office, the name slots the
# company's name of every header and of the name clauses
SLOTS = (
    ("town", "after it", "Via del Collaudo 7, Borgoprova {w} (ZZ)"),
    ("town", "before it", "Via del Collaudo 7, {w} Borgoprova (ZZ)"),
    ("street", "before the number", "Via del Collaudo {w} 7, Borgoprova (ZZ)"),
    ("street", "inside it", "Via {w} del Collaudo 7, Borgoprova (ZZ)"),
    ("province", "inside the parentheses", "Via del Collaudo 7, Borgoprova (ZZ {w})"),
    ("name", "before the legal form", BARE + " {w} " + FORM),
    ("name", "after its first word", FIRST + " {w} " + REST + " " + FORM),
    ("name", "before it", "{w} " + NAME),
    ("name", "after the legal form", NAME + " {w}"),
    ("name", "inside the legal form", BARE + " S. {w} " + FORM[3:] if FORM.startswith("S.") else NAME + " {w}"),
    ("title", "before the closing mark", "Notice of a transfer of shares {w} (synthetic)."),
    ("label", "after its words", "Registered address {w}: " + OFFICE),
    ("label", "before its words", "{w} Registered address: " + OFFICE),
)
SOURCES = ("2 documents alike", "3 documents alike", "1 document, a second without the words")


def _head(n: int, label: str, date: str, ed: str, name: str) -> list[str]:
    return [mk.MARKER, f"Document id: {mk._doc_id(E, n)}", f"Document type: {label}", f"Document date: {date}",
            f"Edition: {ed}", f"Entity: {name} (test registry no. TEST-REG-00{E[2:]})", ""]


def deed(office: str = OFFICE, name: str = NAME):
    return mk._file(E, "2024-03-10_deed.txt", _head(1, "Deed of incorporation", "2024-03-10", "DEED/1", name) + [
        f"1. Name and form. The company is named {name}; its legal form is {FORM}",
        f"2. Registered office. The registered office is at {office}.",
        "3. Share capital. " + mk.FULL.format(a="50.000,00"),
        "4. Holders.", *ROWS, "",
        "5. Directors.", *DIRS])


def extract(office: str = OFFICE, name: str = NAME, extra=(), n: int = 2, date: str = "2025-02-01",
            ed: str = "EXTRACT/1"):
    return mk._file(E, f"{date}_registry-extract.txt", _head(n, "Test registry extract", date, ed, name) + [
        f"Name: {name}", f"Legal form: {FORM}", f"Registered office: {office}",
        "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00", *extra,
        "Holders:", *ROWS, "", "Directors:", *DIRS])


def notice(title: str, n: int, date: str):
    return mk._file(E, f"{date}_share-transfer.txt", _head(n, "Share transfer notice", date, "TRANSFER/1", NAME) + [
        title, "Holders after the transfer:", *ROWS])


PLAIN_TITLE = "Notice of a transfer of shares (synthetic)."
PLAIN_LABEL = "Registered address: " + OFFICE


def documents(slot: str, text: str, plain: str, sources: str) -> list:
    """The documents of one case: ``text`` (the slot with the words) in 2 or 3 documents alike, or in one document beside
    a second that states ``plain`` (the slot without the words)."""
    k = {"2 documents alike": 2, "3 documents alike": 3}.get(sources, 1)
    texts = [text] * k + ([plain] if k == 1 else [])
    if k == 1 and slot in ("title", "label"):
        # the words in the later document, so that the date criterion (DISC-005/006: an older document cannot
        # change a field a later event states) does not decide the case in place of the identification
        texts = [plain, text]
    if slot in ("town", "street", "province"):
        docs = [deed(office=texts[0])] + [extract(office=t, n=2 + i, date=f"2025-0{2 + i}-01", ed=f"EXTRACT/{1 + i}")
                                          for i, t in enumerate(texts[1:])]
        return docs if len(docs) > 1 else docs + [extract()]
    if slot == "name":
        docs = [deed(name=texts[0])] + [extract(name=t, n=2 + i, date=f"2025-0{2 + i}-01", ed=f"EXTRACT/{1 + i}")
                                        for i, t in enumerate(texts[1:])]
        return docs
    if slot == "title":
        return [deed(), extract()] + [notice(t, 3 + i, f"2026-0{3 + i}-01") for i, t in enumerate(texts)]
    return [deed()] + [extract(extra=[t], n=2 + i, date=f"2025-0{2 + i}-01", ed=f"EXTRACT/{1 + i}")
                       for i, t in enumerate(texts)]


def cases():
    for field, w, form, numeral, changes in WORDS:
        for slot, pos, shape in SLOTS:
            plain = {"title": PLAIN_TITLE, "label": PLAIN_LABEL}.get(slot) or (
                OFFICE if slot in ("town", "street", "province") else NAME)
            for sources in SOURCES:
                key = (field, "numeral" if numeral else "no numeral", form, f"{slot}, {pos}", slot, sources)
                yield key, documents(slot, shape.format(w=w), plain, sources), changes


def _run(docs, rules_dir=None):
    work = s.tmp()
    kw = {"rules_dir": rules_dir} if rules_dir else {}
    code, _, report = s.run(s.tiny(docs, "2026-09-30"), work, **kw)
    status = report["entities"][E]["status"]
    view = jsonio.load(work / "views" / f"{E}.json") if (work / "views" / f"{E}.json").exists() else None
    prov_path = work / "dossiers" / E / "provenance.json"
    prov = jsonio.load(prov_path) if prov_path.exists() else None
    return status, view, prov


def unsafe(status: str, view: dict | None, prov: dict | None, changes, slot: str) -> str:
    """'' when the case is safe, else what was published wrongly. A FAILED entity is reported as such."""
    if status == "BLOCKED" and prov is None:
        return ""
    if status != "OK":
        return f"status {status}"
    fields = view["fields"]
    wrong = [f for f in changes if f in fields and fields[f]["status"] == "STATED"]
    held = ("registered_office" if slot in ("town", "street", "province") else "name" if slot == "name" else None)
    if held and fields.get(held, {}).get("status") in ("STATED", "DISCREPANCY") and held not in wrong:
        wrong.append(f"{held} as {fields[held]['status']}")
    if "shareholders" in changes and (prov["derived"] or [f for f in prov["figures"] if f["section"] == "cap_table"]):
        wrong.append("holdings derived")
    return ", ".join(wrong)


AXES = ("words", "numeral", "form", "slot and position", "slot", "sources")


def tally() -> dict:
    """{axis: {class: [cases, unsafe]}}, and the list of unsafe cases."""
    out: dict[str, dict[str, list[int]]] = {a: {} for a in AXES}
    bad = []
    n = 0
    for key, docs, changes in cases():
        n += 1
        why = unsafe(*_run(docs), changes, key[4])
        for axis, value in zip(AXES, key):
            row = out[axis].setdefault(value, [0, 0])
            row[0] += 1
            row[1] += bool(why)
        if why:
            bad.append((" | ".join(key), why))
    return {"by_class": out, "cases": n, "unsafe": len(bad), "unsafe_cases": bad}


N_CASES = len(WORDS) * len(SLOTS) * len(SOURCES)


class D38_IdentificationSiblings(unittest.TestCase):
    def test_no_sibling_is_published_wrongly(self):
        n = 0
        outcomes = s.sweep(_run, [(docs,) for _, docs, _ in cases()])
        for (key, docs, changes), outcome in zip(cases(), outcomes):
            with self.subTest(case=" | ".join(key)):
                n += 1
                self.assertEqual(unsafe(*outcome.result(), changes, key[4]), "")
        self.assertEqual(n, N_CASES)


class D38_Hand20Classes(unittest.TestCase):
    """The two classes of hand-20, by their shape (never its strings): the record says why."""

    def test_town_with_a_numeral_in_two_documents(self):
        w_addr = "Via del Collaudo 7, Borgoprova Dotazione Novantamila (ZZ)"
        work = s.tmp()
        code, _, report = s.run(s.tiny([deed(office=w_addr), extract(office=w_addr)], "2026-09-30"), work)
        self.assertEqual(report["entities"][E]["status"], "BLOCKED")
        rec = jsonio.load(work / "records" / f"{E}.json")
        why = " ".join(c["holders_check"]["why"] + " " + c["fields_check"]["why"] for c in rec["classified_checks"])
        self.assertIn("IDN-010", why)
        offices = [a for a in rec["assertions"] if a["field"] == "registered_office"]
        self.assertTrue(offices and all("value" not in a for a in offices), offices)

    def test_name_with_a_numeral_in_every_header(self):
        wn = f"{BARE} Dotazione Novantamila {FORM}"
        work = s.tmp()
        code, _, report = s.run(s.tiny([deed(name=wn), extract(name=wn)], "2026-09-30"), work)
        self.assertEqual(report["entities"][E]["status"], "BLOCKED")
        rec = jsonio.load(work / "records" / f"{E}.json")
        why = " ".join(c["holders_check"]["why"] + " " + c["fields_check"]["why"] for c in rec["classified_checks"])
        self.assertIn("NAM-005", why)
        names = [a for a in rec["assertions"] if a["field"] == "name"]
        self.assertTrue(names and all("value" not in a for a in names), names)

    def test_words_without_a_numeral_keep_every_field_to_confirm(self):
        wn = f"{BARE} Capitale Raddoppiato {FORM}"
        status, view, prov = _run([deed(name=wn), extract(name=wn)])
        self.assertEqual(status, "OK")
        self.assertTrue(all(view["fields"][f]["status"] == "TO_CONFIRM" for f in OTHER), view["fields"])


class D38_PlainStillPublishes(unittest.TestCase):
    """The cost side: documents whose every free word is of the gazetteer still publish every field."""

    def test_plain_documents_publish(self):
        for docs in ([deed(), extract()],
                     [deed(), extract(), notice(PLAIN_TITLE, 3, "2026-03-01")]):
            with self.subTest(docs=[d[0] for d in docs]):
                status, view, prov = _run(docs)
                self.assertEqual(status, "OK")
                self.assertTrue(all(view["fields"][f]["status"] == "STATED" for f in OTHER), view["fields"])

    def test_a_word_outside_the_gazetteer_is_not_identified(self):
        """A town, a trade or a surname that the gazetteer does not hold: the slot is not identified (IDN-999), and
        every field stays [TO CONFIRM], however many documents agree. The price, declared in CHANGELOG 2.0.9."""
        for docs in ([deed(office="Via del Collaudo 7, Borgonuovo (ZZ)"),
                      extract(office="Via del Collaudo 7, Borgonuovo (ZZ)")],
                     [deed(name=f"Sartoria Aurelia {FORM}"), extract(name=f"Sartoria Aurelia {FORM}")]):
            with self.subTest(docs=docs[0][1].split("\n")[5]):
                status, view, prov = _run(docs)
                self.assertEqual(status, "OK")
                self.assertTrue(all(view["fields"][f]["status"] != "STATED" for f in OTHER), view["fields"])

    def test_a_genuine_difference_of_two_identified_addresses_side_by_side(self):
        """A2 still holds where every word is identified: two whole different addresses, each stated once, are a
        DISCREPANCY side by side (DISC-020), and the other fields stay [TO CONFIRM] (ADR-999)."""
        status, view, prov = _run([deed(office=mk.OFFICE_A), extract(office=mk.OFFICE_B)])
        self.assertEqual(status, "OK")
        office = view["fields"]["registered_office"]
        self.assertEqual(office["status"], "DISCREPANCY")
        self.assertEqual(sorted(c["value"] for c in office["candidates"]), sorted([mk.OFFICE_A, mk.OFFICE_B]))

    def test_a_label_two_documents_state_alike_is_read_by_no_rule(self):
        """Since v2.0.9 the agreement of two documents on a label accounts for none of its words (TXT-020)."""
        work = s.tmp()
        s.run(s.tiny([deed(), extract(extra=[PLAIN_LABEL]),
                      extract(extra=[PLAIN_LABEL], n=3, date="2026-08-20", ed="EXTRACT/2")], "2026-09-30"), work)
        rec = jsonio.load(work / "records" / f"{E}.json")
        why = " ".join(c["fields_check"]["why"] for c in rec["classified_checks"])
        self.assertIn("TXT-020", why)


# goal (b): the own name holding a street word, decided by identification both ways
STREET_WORD_NAMES = ("Conceria Borgo Lontano", "Sartoria Corso Fittizio", "Vivaio Largo Inventato",
                     "Conceria Viale Remoto")   # none is a value of an inline test of the rule files


@lru_cache(maxsize=None)
def rules_wider_gazetteer():
    """A copy of the rule files whose gazetteer also holds the trades and the towns of STREET_WORD_NAMES (each town
    opens with a street word): it shows that such a name, once identified, is a name - no topic word masks it."""
    dst = s.tmp("ezio-rules-") / "rules"
    shutil.copytree(ROOT / "rules", dst)
    path = dst / "extract.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    p = obj["parameters"]
    p["gazetteer_trade"] = p["gazetteer_trade"] + ["Conceria", "Sartoria", "Vivaio"]
    p["gazetteer_town"] = p["gazetteer_town"] + ["Borgo Lontano", "Corso Fittizio", "Largo Inventato", "Viale Remoto"]
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return dst


class D38_OwnNameStreetWord(unittest.TestCase):
    def test_identified_own_name_with_a_street_word_is_a_name(self):
        for bare in STREET_WORD_NAMES:
            name = f"{bare} {FORM}"
            with self.subTest(name=name):
                status, view, prov = _run([deed(name=name), extract(name=name)], rules_wider_gazetteer())
                self.assertEqual(status, "OK")
                self.assertEqual(view["fields"]["name"]["status"], "STATED", view["fields"])
                self.assertTrue(all(view["fields"][f]["status"] == "STATED" for f in OTHER), view["fields"])

    def test_unidentified_own_name_with_a_street_word_is_not_read(self):
        for bare in STREET_WORD_NAMES:
            name = f"{bare} {FORM}"
            with self.subTest(name=name):
                status, view, prov = _run([deed(name=name), extract(name=name)])
                self.assertEqual(status, "OK")
                self.assertTrue(all(view["fields"][f]["status"] != "STATED" for f in OTHER), view["fields"])


@lru_cache(maxsize=None)
def rules_multiword_gazetteer():
    """A copy of the rule files whose gazetteer holds entries of more than one word: a trade, a town, a first name."""
    dst = s.tmp("ezio-rules-") / "rules"
    shutil.copytree(ROOT / "rules", dst)
    path = dst / "extract.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    p = obj["parameters"]
    p["gazetteer_trade"] = p["gazetteer_trade"] + ["Cooperativa Agricola"]
    p["gazetteer_town"] = p["gazetteer_town"] + ["Borgo Lontano"]
    p["gazetteer_first_name"] = p["gazetteer_first_name"] + ["Gian Maria"]
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return dst


class D38_AuditAgrees(unittest.TestCase):
    """The audit's own identification (dossier/s7_audit.py _Ident) and the extractor's (rules/extract.json
    free_text_identification) give the same outcome, with the pack's gazetteer and with one whose entries hold more than
    one word. Found while v2.0.9 was built: with a trade of two words the extractor identified a name and the audit did
    not, and the run of the entity ended FAILED (fail-closed: nothing published) - tests/test_d37_score.py."""

    VALUES = (("address", OFFICE), ("address", "Via Del Collaudo 7, Borgoprova (ZZ)"),
              ("address", "Via del Collaudo 7, Borgo Lontano (ZZ)"),
              ("address", "Via del Collaudo 7, Borgoprova Dotazione Novantamila (ZZ)"),
              ("address", "Piazza Inventata 3, Valcollaudo (ZZ) - interno 4"),
              ("company", NAME), ("company", "Cooperativa Agricola Borgoprova S.r.l."),
              ("company", "Cooperativa Agricola Borgo Lontano S.r.l."), ("company", "Cooperativa Borgoprova S.r.l."),
              ("company", "Holding Borgoprova Partecipazioni S.p.A."), ("company", "Officine Borgoprova Tremila S.r.l."),
              ("company", "Officine Borgo Lontano Quote Cedute S.r.l."),
              ("person", "Aldo Finti"), ("person", "Gian Maria Finti"), ("person", "Gian Finti"),
              ("person", "Finti Aldo"), ("person", "Aldo Finti Trenta"),
              ("title", "Minutes of the holders' meeting (synthetic)"), ("title", "Minutes of the board (synthetic)"),
              ("label", "Registered address"))

    def test_same_outcome(self):
        from dossier import rules_engine, s1_extract, s7_audit
        for name, rules in (("pack", rules_engine.load()), ("multi-word", rules_engine.load(rules_multiword_gazetteer()))):
            ident = s7_audit._Ident(rules)
            for cls, value in self.VALUES:
                with self.subTest(rules=name, value=value):
                    self.assertEqual(ident.ok(value, cls),
                                     s1_extract.identify(value, cls, rules)["outcome"] == "identified")


OTHER_ENTITY = "E-0003"


def misfiled():
    """A registry extract filed with the documents of E-0001 whose header names E-0003 (its registry number)."""
    lines = [mk.MARKER, f"Document id: {mk._doc_id(OTHER_ENTITY, 1)}", "Document type: Test registry extract",
             "Document date: 2025-06-01", "Edition: EXTRACT/1",
             f"Entity: {NAME} (test registry no. TEST-REG-00{OTHER_ENTITY[2:]})", "",
             f"Name: {NAME}", f"Legal form: {FORM}", f"Registered office: {OFFICE}",
             "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00",
             "Holders:", *ROWS, "", "Directors:", *DIRS]
    return f"entities/{E}/2025-06-01_registry-extract.txt", "\n".join(lines) + "\n"


class D38_DeclaredLimits(unittest.TestCase):
    """Goal (c) of D38: the limits run 20 found, declared by class with fixtures of this file (never the lines of
    hand-20), each with the class CHANGELOG 2.0.9 gives it."""

    def test_rows_framed_by_vertical_bars_without_a_header_row_block(self):
        """hand-20 E-0030, by class: holder rows framed by vertical bars, no header row - not read, blocks."""
        bars = [f"| {h} ({mk.LABEL[h]}) | {share} |" for h, share in H]
        d = deed()
        d = (d[0], d[1].replace("\n".join(ROWS), "\n".join(bars)))
        e = extract()
        e = (e[0], e[1].replace("\n".join(ROWS), "\n".join(bars)))
        status, view, prov = _run([d, e])
        self.assertEqual(status, "BLOCKED")
        self.assertIsNone(prov)

    def test_a_capitalised_particle_keeps_every_field_to_confirm(self):
        """hand-20 E-0025, by class: 'Via Del ...' - the gazetteer holds 'del Collaudo', not 'Del Collaudo' (each entry
        is matched whole, case included): the address is not identified (IDN-999), every field keeps [TO CONFIRM]."""
        addr = "Via Del Collaudo 7, Borgoprova (ZZ)"
        status, view, prov = _run([deed(office=addr), extract(office=addr)])
        self.assertEqual(status, "OK")
        self.assertTrue(all(f["status"] == "TO_CONFIRM" for f in view["fields"].values()), view["fields"])

    def test_a_misfiled_extract_of_an_entity_with_no_folder(self):
        """hand-20 E-0062, by class: a registry extract filed with the documents of E-0001 whose content names another
        entity (another registry number) that has no folder of its own. It is built for the entity its content names,
        as ever, and it is also an unclassified document of E-0001 (DISC-005, every_field): no field of E-0001 is
        published as a fact (every field [TO CONFIRM], or the entity blocks when its holders are not read whole)."""
        other = OTHER_ENTITY
        work = s.tmp()
        code, _, report = s.run(s.tiny([deed(), extract(), misfiled()], "2026-09-30"), work)
        rec = jsonio.load(work / "records" / f"{E}.json")
        self.assertTrue(any("no folder of its own" in u["reason"] for u in rec["unclassified_documents"]),
                        rec["unclassified_documents"])
        status = report["entities"][E]["status"]
        self.assertIn(status, ("OK", "BLOCKED"))
        view = jsonio.load(work / "views" / f"{E}.json")
        self.assertTrue(all(f["status"] != "STATED" for f in view["fields"].values()), view["fields"])
        self.assertIn(other, report["entities"])

    def test_the_same_extract_when_that_entity_has_a_folder(self):
        """Control: when the entity the content names has a folder of its own, the document is not an unclassified
        document of E-0001 (the generator's 'folder' fault, decided as before v2.0.9)."""
        own = (f"entities/{OTHER_ENTITY}/2024-03-10_deed.txt",
               deed()[1].replace(mk._doc_id(E, 1), mk._doc_id(OTHER_ENTITY, 2))
                        .replace(f"TEST-REG-00{E[2:]}", f"TEST-REG-00{OTHER_ENTITY[2:]}"))
        work = s.tmp()
        code, _, report = s.run(s.tiny([deed(), extract(), misfiled(), own], "2026-09-30"), work)
        rec = jsonio.load(work / "records" / f"{E}.json")
        self.assertFalse([u for u in rec["unclassified_documents"] if "no folder of its own" in u["reason"]])
        self.assertEqual(report["entities"][E]["status"], "OK")
        view = jsonio.load(work / "views" / f"{E}.json")
        self.assertTrue(all(view["fields"][f]["status"] == "STATED" for f in OTHER), view["fields"])


def load_tests(loader, tests, pattern):
    """v2.0.14: the sweep's cases go to the workers now, while the other tests run (tests/support.py ahead())."""
    s.ahead(tests, "D38_IdentificationSiblings.test_no_sibling_is_published_wrongly", _run,
            [(docs,) for _, docs, _ in cases()])
    return tests


if __name__ == "__main__":
    json.dump(tally(), sys.stdout, indent=1, ensure_ascii=False)
    print()
