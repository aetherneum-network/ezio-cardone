"""D36 (v2.0.7): the residual risk of section 4 of CHANGELOG 2.0.6, probed by class. The blind run of v2.0.6
(eval/history.json run 16, hand corpus eval/blind/hand-16) probed it with five hand entities, two of them masked: the
office-transfer wording of E-0014 is the unknown wording of scenario S09, and the total line of E-0017 stood outside
the capital clause that count_total reads.

A typed slot states only its own value. An ADDRESS slot is a street, a house number, a town and the province in
parentheses, and nothing after it but the end of the line or the sentence's own full stop; an AMOUNT slot is a currency
and a figure (and the words the rules already read: the nature of the amount, 'each'); a COUNT slot is a figure and the
unit noun. Anything else in the slot makes the line one that no rule explains (CLS-999: DISC-006 keeps every field
[TO CONFIRM], or OWN-015 blocks when the line may state a holding), and the readers of the registered office read only
such an address (value_slot). The words a slot of names may hold are told from a statement (v2.0.7):
- a name beside an identifier, and the entity's own name, by equality only: the identifier's own known name (identity
  layer, Entity: header), or the line is open - an identifier whose own name the corpus does not know cannot be checked;
- a street and a town by form: every word of the form of an Italian place name (rules/extract.json slot_address_word:
  it ends in a vowel, or is a particle, a truncated form or a Roman numeral), no name known to the corpus inside, and
  none of the word classes of slot_not_name_word (v2.0.6, since v2.0.7 also English verb forms in -ing and -s, common
  irregular past forms, nouns in -ee, Italian nouns and verbs of role and holding). What still rests on that word list
  is a street or a town word of the form of a place name that states something ([TO CONFIRM], CHANGELOG 2.0.7).

The siblings are built by class (R6), never from the literal strings of hand-16: for each kind of slot, each place
where the pack reads it (deed, registry extract, office transfer, capital resolution, financial summary, label line,
list row), each position of the extra words (after the slot, inside it, in place of a part of it), and words that state
another field (the directors, the holders, the capital) with a person the corpus knows, a person it does not know,
and no person at all. A case is unsafe when a field the extra words may change is published as fact, the slot's own
field is published with the extra words in it, or a holding is derived from a table the extra words may contradict.
The same file was run on the code of v2.0.6 (CHANGELOG 2.0.7 gives the count, by class).

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import sys
import unittest

from . import support as s
from .support import mk

from dossier.lib import jsonio

E = "E-0001"
NAME, FORM = mk.ENT[E]                      # Fornace Aurelia S.r.l., S.r.l.
H = [("P-001", "60%"), ("P-002", "40%")]
CAPITAL_FIELDS = ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")
NEW = ("Via Nuova", "1", "Montefinto")      # the address an office transfer moves to

# extra words that state another field, by the field they state and by whom they name (a person of the identity layer
# of the input, a person nobody in the corpus knows, nobody); each wording is capitalised words only, so that it fits
# a slot of names, and none is a literal string of hand-16
WORDS = (
    ("directors, a known person", "Carlo Inventati Presiding", ("directors",)),
    ("directors, an unknown person", "Ugo Nessuno Presiding", ("directors",)),
    ("directors, no person", "Chairing Changes", ("directors",)),
    ("holders, a known person", "Carlo Inventati Buys", ("shareholders",)),
    ("holders, an unknown person", "Ugo Nessuno Buys", ("shareholders",)),
    ("capital, no person", "Means Doubling", CAPITAL_FIELDS),
    ("directors, an unknown person, a noun of role in no list", "Ugo Nessuno Leader", ("directors",)),
    ("holders, an unknown person, an Italian verb", "Ugo Nessuno Subentra", ("shareholders",)),
)


def deed(**o):
    return mk._file(E, "2024-03-10_deed.txt", mk._head(E, 1, "Deed of incorporation", "2024-03-10", "DEED/1") + [
        o.get("name_line", f"1. Name and form. The company is named {NAME}; its legal form is {FORM}"),
        o.get("office_line", f"2. Registered office. The registered office is at {mk.OFFICE_A}."),
        o.get("capital_line", "3. Share capital. " + mk.FULL.format(a="50.000,00")),
        "4. Holders.", *o.get("holders", mk._holders(H)), "",
        "5. Directors.", *o.get("directors", mk._directors(["P-001"]))])


def extract(**o):
    return mk._file(E, "2025-02-01_registry-extract.txt",
                    mk._head(E, 2, "Test registry extract", "2025-02-01", "EXTRACT/1") + [
                        f"Name: {NAME}", f"Legal form: {FORM}",
                        o.get("office_line", f"Registered office: {mk.OFFICE_A}"),
                        o.get("capital_line", "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; "
                                              "paid in EUR 50.000,00"),
                        *o.get("extra", []),
                        "Holders:", *o.get("holders", mk._holders(H)), "",
                        "Directors:", *o.get("directors", mk._directors(["P-001"]))])


def later(kind: str, body: list[str], fy: str = ""):
    label, title, edition, slug = {
        "APPOINTMENT": ("Appointment of directors", "Minutes of the holders' meeting (synthetic).", "APPOINTMENT/1",
                        "appointment_P-001"),
        "TRANSFER": ("Share transfer notice", "Notice of a transfer of shares (synthetic).", "TRANSFER/1",
                     "share-transfer"),
        "LEDGER": ("Holders' ledger", None, "LEDGER/1", "holders-ledger"),
        "OFFICE": ("Transfer of registered office", None, "OFFICE/1", "office-transfer"),
        "RESOLUTION": ("Resolution on share capital", "Minutes of the holders' meeting (synthetic).", "RESOLUTION/1",
                       "capital-resolution"),
        "FIN": ("Financial statements summary", None, f"FIN-FY{fy}/1", "financial-summary"),
    }[kind]
    return mk._file(E, f"2026-08-20_{slug}.txt", mk._head(E, 3, label, "2026-08-20", edition, fy)
                    + ([title] if title else []) + body)


# ----------------------------------------------------------------------------------------------
# ADDRESS slots

def addresses(w: str):
    """(position, address) for the extra words w: after the slot, inside it, in place of a part of it."""
    street, no, town = NEW
    return (("after the province", f"{street} {no}, {town} (ZZ) {w}"),
            ("after the house number", f"{street} {no} {w}, {town} (ZZ)"),
            ("in place of the house number", f"{street} {w}, {town} (ZZ)"),
            ("inside the town", f"{street} {no}, {town} {w} (ZZ)"),
            ("inside the street", f"Via {w} {no}, {town} (ZZ)"),
            ("after the mark of the interno", f"{street} {no}, {town} (ZZ) - interno 2 {w}"),
            ("as the town", f"{street} {no}, {w} (ZZ)"))


def _address_cases():
    for wname, w, changes in WORDS:
        for pos, addr in addresses(w):
            ch = (*changes, "registered_office")
            yield "deed", wname, pos, [deed(office_line=f"2. Registered office. The registered office is at {addr}."),
                                       extract(office_line=f"Registered office: {addr}")], ch
            yield "extract", wname, pos, [deed(), extract(office_line=f"Registered office: {addr}")], ch
            yield "office transfer, new address", wname, pos, [deed(), extract(), later(
                "OFFICE", [f"The registered office is transferred from {mk.OFFICE_A} to {addr}."])], ch
            yield "office transfer, previous address", wname, pos, [deed(), extract(), later(
                "OFFICE", [f"The registered office is transferred from {addr} to {mk.OFFICE_B}."])], ch
            yield "extract, label line", wname, pos, [deed(), extract(extra=[f"Registered address: {addr}"])], ch


# ----------------------------------------------------------------------------------------------
# AMOUNT slots

def _amount_cases():
    for wname, w, changes in WORDS:
        ch = (*changes, *CAPITAL_FIELDS)
        for pos, line in (
                ("after the amount", f"3. Share capital. The share capital is EUR 50.000,00 {w}, fully subscribed and "
                                     "fully paid in."),
                ("after the clause", f"3. Share capital. The share capital is EUR 50.000,00, fully subscribed and "
                                     f"fully paid in {w}."),
                ("after an amount in words", f"3. Share capital. The share capital is fifty thousand euro {w}, fully "
                                             "subscribed and fully paid in.")):
            yield "deed", wname, pos, [deed(capital_line=line), extract()], ch
        for pos, line in (
                ("after the first amount", f"Share capital: resolved EUR 50.000,00 {w}; subscribed EUR 50.000,00; "
                                           "paid in EUR 50.000,00"),
                ("after the last amount", f"Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in "
                                          f"EUR 50.000,00 {w}"),
                ("before the currency", f"Share capital: resolved EUR 50.000,00; subscribed {w} EUR 50.000,00; "
                                        "paid in EUR 50.000,00")):
            yield "extract", wname, pos, [deed(), extract(capital_line=line)], ch
        yield "extract, label line", wname, "after the amount", \
            [deed(), extract(extra=[f"Subscribed capital: EUR 50.000,00 {w}"])], ch
        for pos, line in (
                ("after the new amount", f"The meeting resolved to increase the share capital from EUR 50.000,00 to "
                                         f"EUR 80.000,00 {w}."),
                ("after the old amount", f"The meeting resolved to increase the share capital from EUR 50.000,00 {w} "
                                         "to EUR 80.000,00.")):
            yield "capital resolution", wname, pos, [deed(), extract(), later("RESOLUTION", [line])], ch
        yield "financial summary", wname, "after the amount", [deed(), extract(), later("FIN", [
            f"Net equity: EUR 80.000,00 {w}", "Total assets: EUR 200.000,00", "Revenue: EUR 150.000,00"], "2025")], \
            (*changes, "fin.FY2025.net_equity")


# ----------------------------------------------------------------------------------------------
# COUNT slots

COUNTED = "3. Share capital. The share capital is EUR 50.000,00, divided into 500 quotas, fully subscribed and fully paid in."


def _count_cases():
    for wname, w, changes in WORDS:
        ch = (*changes, "shareholders", *CAPITAL_FIELDS)
        for pos, line in (
                ("after the unit of the total", f"3. Share capital. The share capital is EUR 50.000,00, divided into "
                                                f"500 quotas {w}, fully subscribed and fully paid in."),
                ("after the nominal amount of each", f"3. Share capital. The share capital is EUR 50.000,00, divided "
                                                     f"into 500 quotas of EUR 100,00 each {w}.")):
            yield "deed, total", wname, pos, [deed(capital_line=line, holders=[
                "- P-001 (Aldo Finti): 300 quotas", "- P-002 (Bice Provetti): 200 quotas"]), extract()], ch
        for pos, row in (("after the unit of a row", f"- P-002 (Bice Provetti): 200 quotas {w}"),
                         ("between the figure and the unit", f"- P-002 (Bice Provetti): 200 {w} quotas")):
            yield "deed, row", wname, pos, [deed(capital_line=COUNTED, holders=[
                "- P-001 (Aldo Finti): 300 quotas", row]), extract()], ch


# ----------------------------------------------------------------------------------------------
# a name beside an identifier that nobody in the corpus knows (P-004 is not in the identity layer of these inputs,
# E-0077 has no document), and another company's name in a label

def _unknown_label_cases():
    plain = {"P-004": "Dora Campione", "E-0077": "Argentiere Riofittizio S.r.l."}
    for wname, w, changes in WORDS:
        for ident, label in (("P-004", f"Dora Campione {w}"), ("E-0077", f"Argentiere Riofittizio {w} S.r.l.")):
            other = [f"- P-001 (Aldo Finti): 60%", f"- {ident} ({plain[ident]}): 40%"]
            for form, row in (("ID (name)", f"- {ident} ({label}): 40%"), ("name (ID)", f"- {label} ({ident}): 40%")):
                rows = ["- P-001 (Aldo Finti): 60%", row]
                ch = (*changes, "shareholders")
                yield f"holder row, {ident[0]}", wname, f"{form}, deed", [deed(holders=rows), extract(holders=other)], ch
                yield f"holder row, {ident[0]}", wname, f"{form}, extract", [deed(holders=other),
                                                                            extract(holders=rows)], ch
                yield f"holder row, {ident[0]}", wname, f"{form}, transfer", [deed(), extract(), later(
                    "TRANSFER", ["Holders after the transfer:", *rows])], ch
                yield f"holder row, {ident[0]}", wname, f"{form}, ledger", [deed(), extract(), later(
                    "LEDGER", ["Holders:", *rows])], ch
        for form, row in (("ID (name)", f"- P-004 (Dora Campione {w})"), ("name (ID)", f"- Dora Campione {w} (P-004)")):
            ch = (*changes, "directors")
            plain_dir = ["- P-004 (Dora Campione)"]
            yield "director row, P", wname, f"{form}, deed", [deed(directors=[row]), extract(directors=plain_dir)], ch
            yield "director row, P", wname, f"{form}, extract", [deed(directors=plain_dir), extract(directors=[row])], ch
            yield "director row, P", wname, f"{form}, appointment", [deed(), extract(), later(
                "APPOINTMENT", ["Directors in office after this appointment:", row])], ch


def other_company():
    """A second entity of the corpus, so that its name is known from its own header."""
    return mk._file("E-0002", "2024-01-10_deed.txt", mk._head("E-0002", 1, "Deed of incorporation", "2024-01-10",
                                                            "DEED/1") + [
        f"1. Name and form. The company is named {mk.ENT['E-0002'][0]}; its legal form is S.r.l.",
        f"2. Registered office. The registered office is at {mk.OFFICE_C}.",
        "3. Share capital. " + mk.FULL.format(a="20.000,00"),
        "4. Holders.", *mk._holders([("P-003", "100%")]), "",
        "5. Directors.", *mk._directors(["P-003"])])


def _company_label_cases():
    known = mk.ENT["E-0002"][0][: -len(" S.r.l.")]          # Holding Aurelia Partecipazioni
    for wname, w, changes in WORDS:
        row = f"- E-0002 ({known} {w} S.r.l.): 40%"
        rows = ["- P-001 (Aldo Finti): 60%", row]
        plain = ["- P-001 (Aldo Finti): 60%", f"- E-0002 ({mk.ENT['E-0002'][0]}): 40%"]
        ch = (*changes, "shareholders")
        yield "holder row, a company of the corpus", wname, "deed", [deed(holders=rows), extract(holders=plain),
                                                                     other_company()], ch
        yield "holder row, a company of the corpus", wname, "transfer", [deed(), extract(), other_company(), later(
            "TRANSFER", ["Holders after the transfer:", *rows])], ch
        yield "label line, another company's name", wname, "extract", [deed(), extract(extra=[
            f"Name of the company: {known} {w} S.r.l."]), other_company()], (*changes, "name", "legal_form")
        yield "label line, another company's name", wname, "extract, the other company's own name", [deed(), extract(
            extra=[f"Company name: {mk.ENT['E-0002'][0]} {w}"]), other_company()], (*changes, "name", "legal_form")


GROUPS = (("ADDRESS slot", _address_cases), ("AMOUNT slot", _amount_cases), ("COUNT slot", _count_cases),
          ("name beside an identifier nobody knows", _unknown_label_cases),
          ("another company's name in a label", _company_label_cases))


def cases():
    for group, gen in GROUPS:
        for place, wname, pos, docs, changes in gen():
            yield group, f"{place} | {wname} | {pos}", docs, changes


def _run(docs):
    work = s.tmp()
    code, _, report = s.run(s.tiny(docs, "2026-09-30"), work)
    status = report["entities"][E]["status"]
    view = jsonio.load(work / "views" / f"{E}.json") if (work / "views" / f"{E}.json").exists() else None
    prov_path = work / "dossiers" / E / "provenance.json"
    prov = jsonio.load(prov_path) if prov_path.exists() else None
    return status, view, prov


def unsafe(status: str, view: dict | None, prov: dict | None, changes) -> str:
    """'' when the case is safe (blocked, or no field it may change published as fact and no holding derived from a
    table the extra words may contradict), else what was published wrongly. A FAILED entity is not published, but a
    case that fails is reported as such: the reader should have refused the slot before."""
    if status == "BLOCKED" and prov is None:
        return ""
    if status != "OK":
        return f"status {status}"
    wrong = [f for f in changes if f in view["fields"] and view["fields"][f]["status"] == "STATED"]
    if "shareholders" in changes and (prov["derived"] or [f for f in prov["figures"] if f["section"] == "cap_table"]):
        wrong.append("holdings derived")
    return ", ".join(wrong)


def tally() -> dict:
    """{group: [cases, unsafe, failed]} and the list of unsafe cases, on the code this file runs on."""
    out: dict[str, list[int]] = {}
    bad = []
    for group, wording, docs, changes in cases():
        status, view, prov = _run(docs)
        why = unsafe(status, view, prov, changes)
        row = out.setdefault(group, [0, 0, 0])
        row[0] += 1
        if why:
            row[1] += 1
            bad.append((group, wording, why))
        if status == "FAILED":
            row[2] += 1
    return {"by_group": out, "unsafe": bad}


class D36_TypedSlotSiblings(unittest.TestCase):
    def test_every_sibling_is_safe(self):
        n = 0
        for group, wording, docs, changes in cases():
            with self.subTest(group=group, wording=wording):
                n += 1
                self.assertEqual(unsafe(*_run(docs), changes), "")
        self.assertEqual(n, N_CASES)


N_CASES = sum(1 for _ in cases())


def hand_16_variant(work) -> tuple:
    """A fixture of this test, built at run time from the seen corpus eval/blind/hand-16 (which is not changed): the
    two typed-slot probes of run 16 that were masked, unmasked. E-0014: the office change in the form EXT-OFFICE-010
    reads ('The registered office is transferred from ... to ...'), the extra words after the new address kept. E-0017:
    the total of quotas inside the deed's capital clause that count_total reads, the deed's table in quotas with the
    probe's extra words on a row, the extract's table in the shares those quotas give and its total line (outside any
    clause) removed. (input, gold)"""
    import json
    hand = s.ROOT / "eval" / "blind" / "hand-16"
    inp = work / "input"

    def edit(eid: str, name: str, text: str) -> str:
        if eid == "E-0014":
            return text.replace("The seat of the company is moved from", "The registered office is transferred from")
        if name.endswith("_deed.txt"):
            text = text.replace("The share capital is EUR 10.000,00, fully subscribed and fully paid in.",
                                "The share capital is EUR 10.000,00, divided into 1.000 quotas, fully subscribed and "
                                "fully paid in.")
            text = text.replace("- P-003 (Teo Congetturi): 70%", "- P-003 (Teo Congetturi): 700 quotas")
            return text.replace("- P-005 (Ivo Apparenti): 30%", "- P-005 (Ivo Apparenti): 300 quotas Twenty Euro Apiece")
        text = text.replace("The capital is divided into 1.000 quotas.\n", "")
        return text.replace(": 700 quotas", ": 70%").replace(": 300 quotas Twenty Euro Apiece", ": 30%")

    for eid in ("E-0014", "E-0017"):
        for f in sorted((hand / "input" / "entities" / eid).glob("*.txt")):
            changed = edit(eid, f.name, f.read_text(encoding="utf-8"))
            jsonio.write_bytes(inp / "entities" / eid / f.name, changed.encode("utf-8"))
    jsonio.write_bytes(inp / "identity" / "persons.json", (hand / "input" / "identity" / "persons.json").read_bytes())
    jsonio.write_bytes(inp / "config.json", (hand / "input" / "config.json").read_bytes())
    gold = json.loads((hand / "gold.json").read_text(encoding="utf-8"))
    gold["entities"] = {k: v for k, v in gold["entities"].items() if k in ("E-0014", "E-0017")}
    jsonio.write(work / "gold.json", gold)
    return inp, work / "gold.json"


class D36_HandSixteenUnmasked(unittest.TestCase):
    """Goal (a) on seen data: hand-16 E-0014 (ADDRESS slot) and E-0017 (COUNT slot) with the masking removed. v2.0.6
    publishes nothing as fact on this variant either: E-0014 FAILED (the reader took the words after the new address
    into the office, and the names in them reached the shareable layer; every field [TO CONFIRM]), E-0017 BLOCKED (a
    row whose count is followed by words is not typed: CLS-999, and it may state a holding: OWN-015). v2.0.7: E-0014
    OK with every field [TO CONFIRM] and the office not read from the line (value_slot), E-0017 BLOCKED."""

    def test_unmasked_probes_publish_nothing_wrong(self):
        from eval import score
        work = s.tmp()
        inp, gold = hand_16_variant(work)
        got = score.evaluate("hand-16-unmasked", corpus=inp, gold_path=gold, work=work / "run")
        self.assertEqual(got["metrics"]["never_events"], 0, got["never_event_list"])
        report = jsonio.load(work / "run" / "work" / "run_report.json")
        self.assertEqual(report["entities"]["E-0014"]["status"], "OK")
        self.assertEqual(report["entities"]["E-0017"]["status"], "BLOCKED")
        v14 = jsonio.load(work / "run" / "work" / "views" / "E-0014.json")
        self.assertTrue(all(f["status"] == "TO_CONFIRM" for f in v14["fields"].values()), v14["fields"])
        office = [a for a in jsonio.load(work / "run" / "work" / "records" / "E-0014.json")["assertions"]
                  if a["field"] == "registered_office" and a["source_doc"] == "DOC-E0014-03"]
        self.assertTrue(office and all("value" not in a for a in office), office)


class D36_PlainAddressesStillRead(unittest.TestCase):
    """The cost side: the addresses of the generator's forms, a street with a particle and a Roman numeral, an
    'interno', are still read and published; a street named after nobody the corpus knows is a street."""

    def test_plain_addresses(self):
        for addr in (mk.OFFICE_A, "Via XX Settembre 4, Borgoprova (ZZ)", "Corso dell'Arsenale 12/B, Montefinto (ZZ)",
                     "Via Giuseppe Collaudi 3, San Fittizio (ZZ) - interno 4", "Via Nuova 1, Montefinto (ZZ)"):
            with self.subTest(addr=addr):
                status, view, prov = _run([deed(office_line=f"2. Registered office. The registered office is at {addr}."),
                                           extract(office_line=f"Registered office: {addr}")])
                self.assertEqual(status, "OK")
                self.assertEqual((view["fields"]["registered_office"]["status"],
                                  view["fields"]["registered_office"].get("value")), ("STATED", addr))
                for f in ("directors", "shareholders", *CAPITAL_FIELDS):
                    self.assertEqual(view["fields"][f]["status"], "STATED", f)

    def test_no_house_number_is_a_declared_limit(self):
        """The price, declared in CHANGELOG 2.0.7: an address without a house number is no longer an address (v2.0.6
        read it), so its line is open and every field stays [TO CONFIRM] (DISC-006). One address of the recorded
        corpora has this form (hand-11 E-0009), whose fields were [TO CONFIRM] already."""
        addr = "Piazza Grande, Montefinto (ZZ)"
        status, view, prov = _run([deed(office_line=f"2. Registered office. The registered office is at {addr}."),
                                   extract(office_line=f"Registered office: {addr}")])
        self.assertEqual(status, "OK")
        self.assertTrue(all(f["status"] == "TO_CONFIRM" for f in view["fields"].values()), view["fields"])

    def test_plain_transfer(self):
        """Changed in v2.0.8 (D37, recorded in CHANGELOG 2.0.8): the new address of a transfer is a fact only when a
        later source repeats it (rules/extract.json ADR-020); the transfer as the last document keeps the office
        [TO CONFIRM] (DISC-038, tests/test_d37_forms.py). Until v2.0.7 this case had no later extract."""
        repeat = mk._file(E, "2026-09-01_registry-extract.txt",
                          mk._head(E, 4, "Test registry extract", "2026-09-01", "EXTRACT/2") + [
                              f"Name: {NAME}", f"Legal form: {FORM}", f"Registered office: {mk.OFFICE_B}",
                              "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00",
                              "Holders:", *mk._holders(H), "", "Directors:", *mk._directors(["P-001"])])
        status, view, prov = _run([deed(), extract(), later("OFFICE", [
            f"The registered office is transferred from {mk.OFFICE_A} to {mk.OFFICE_B}."]), repeat])
        self.assertEqual(status, "OK")
        self.assertEqual((view["fields"]["registered_office"]["status"], view["fields"]["registered_office"]["value"]),
                         ("STATED", mk.OFFICE_B))


class D36_ReaderRefusesTheSlot(unittest.TestCase):
    """The readers of the registered office give no value from an address that holds more than an address."""

    def test_readers(self):
        from dossier import rules_engine, s1_extract as x
        rules = rules_engine.load(s.ROOT / "rules")
        for kind, text in (("EXTRACT", "Registered office: Via Nuova 1, Montefinto (ZZ) Carlo Inventati Presiding"),
                           ("EXTRACT", "Registered office: Via Carlo Inventati 1, Montefinto (ZZ)"),
                           ("EXTRACT", "Registered office: Via Nuova Leader 1, Montefinto (ZZ)"),
                           ("DEED", "2. Registered office. The registered office is at Via Nuova, Montefinto Buys (ZZ)."),
                           ("OFFICE", f"The registered office is transferred from {mk.OFFICE_A} to Via Nuova 1, "
                                      "Montefinto (ZZ) Teo Nessuno Replacing Ugo Nessuno.")):
            with self.subTest(text=text):
                doc = x._test_doc(kind, text, rules)
                got = [a for a in x.extract_document(doc, rules, {"P-003": {"Carlo Inventati"}})
                       if a["field"].startswith("registered_office")]
                self.assertTrue(got and all("value" not in a for a in got), got)


# ----------------------------------------------------------------------------------------------
# goals (b)-(e): the end of a list, a possessive with 'own', an illegible amount, the message of a list line


def _deed_raw(body: list[str]):
    return mk._file(E, "2024-03-10_deed.txt", mk._head(E, 1, "Deed of incorporation", "2024-03-10", "DEED/1") + [
        f"1. Name and form. The company is named {NAME}; its legal form is {FORM}",
        f"2. Registered office. The registered office is at {mk.OFFICE_A}.",
        "3. Share capital. " + mk.FULL.format(a="50.000,00")] + body)


def _extract_raw(body: list[str]):
    return mk._file(E, "2025-02-01_registry-extract.txt",
                    mk._head(E, 2, "Test registry extract", "2025-02-01", "EXTRACT/1") + [
                        f"Name: {NAME}", f"Legal form: {FORM}", f"Registered office: {mk.OFFICE_A}",
                        "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00"] + body)


def _odd(label: str, body: list[str], fy: str = ""):
    """A document of a type the pack does not recognise (no rule of doc_kinds reads its 'Document type')."""
    return mk._file(E, "2026-08-20_odd-note.txt", mk._head(E, 3, label, "2026-08-20", "ODD/1", fy) + body)


ROWS, DIRS = mk._holders(H), mk._directors(["P-001"])


class D36_ListEnd(unittest.TestCase):
    """Goal (b): a list ends at the first line that is not an item and is a full sentence or a heading (no identifier;
    a capital first, three words or more, the sentence's own stop after a word; no share, fraction or figure followed
    by a unit noun), and that line is classified on its own. A broken item stays a row and blocks; a sentence with a share or a count is not an
    end. v2.0.6 took every line to the next blank line as a row: the four cases marked v2.0.6 BLOCKED were blocked
    there (a holders' list) or kept the directors [TO CONFIRM] (a directors' list)."""

    # Since v2.0.8 (D37, rules/extract.json text_corroboration): a short sentence of the form of CLS-250 ('The holders
    # sign this deed in person.', 'Bice Provetti also joins the board.') is a label that no second document states
    # (TXT-999); the list still ends at it and its rows are read, but its own line is read by no rule: in the deed its
    # holder noun may state a holding and the entity blocks (OWN-015, the reason names that line, not the list); in the
    # appointment, the latest document, every field stays [TO CONFIRM] (DISC-006). v2.0.7: OK, the fields below STATED.
    CASES = (  # (place, docs, expected status, fields expected STATED, v2.0.6 status)
        ("deed, holders + a sentence", lambda: [_deed_raw(["4. Holders.", *ROWS, "The holders sign this deed in person.",
                                                           "", "5. Directors.", *DIRS]), extract()],
         "BLOCKED", (), "BLOCKED"),
        ("deed, holders + a heading, no blank line", lambda: [_deed_raw(["4. Holders.", *ROWS, "5. Directors.", *DIRS]),
                                                              extract()],
         "OK", ("shareholders", "directors"), "BLOCKED"),
        ("extract, directors + a heading, no blank line", lambda: [deed(), _extract_raw(["Directors:", *DIRS, "Holders:",
                                                                                         *ROWS])],
         "OK", ("shareholders", "directors"), "OK, directors [TO CONFIRM]"),
        ("extract, holders + a sentence", lambda: [deed(), _extract_raw(["Holders:", *ROWS, "Nothing else is certified.",
                                                                         "", "Directors:", *DIRS])],
         "OK", ("shareholders", "directors"), "BLOCKED"),
        ("transfer notice, holders + a sentence", lambda: [deed(), extract(), later(
            "TRANSFER", ["Holders after the transfer:", *ROWS, "The price was paid in full."])], "OK", (), "BLOCKED"),
        ("appointment, directors + a sentence that adds a director", lambda: [deed(), extract(), later(
            "APPOINTMENT", ["Directors in office after this appointment:", "- P-001 (Aldo Finti)",
                            "Bice Provetti also joins the board."])], "OK", (), "OK"),
    )
    STILL_BLOCKED = (  # a broken item, and sentences that state a share or a count, stay rows and block
        ("deed, a wrapped row", lambda: [_deed_raw(["4. Holders.", "- P-001 (Aldo", "Finti): 60%", ROWS[1], "",
                                                    "5. Directors.", *DIRS]), extract()]),
        ("deed, holders + a sentence with a count", lambda: [_deed_raw(["4. Holders.", *ROWS,
                                                                        "Aldo Finti holds 300 quotas.", "",
                                                                        "5. Directors.", *DIRS]), extract()]),
        ("transfer notice, holders + a sentence with a share", lambda: [deed(), extract(), later(
            "TRANSFER", ["Holders after the transfer:", *ROWS, "Bice Provetti keeps her 40%."])]),
        ("deed, holders + a sentence of the total (it ends the list; read on its own, OWN-015)", lambda: [_deed_raw(
            ["4. Holders.", *ROWS, "The quotas are 1000 in total.", "", "5. Directors.", *DIRS]), extract()]),
    )

    def test_a_sentence_or_a_heading_ends_the_list(self):
        for place, docs, want, stated, _ in self.CASES:
            with self.subTest(place=place):
                status, view, prov = _run(docs())
                self.assertEqual(status, want)
                if place == "deed, holders + a sentence":      # v2.0.8: the sentence blocks, the list is read
                    work = s.tmp()
                    _, _, report = s.run(s.tiny(docs(), "2026-09-30"), work)
                    self.assertIn("line 14, read by no rule of its kind", report["entities"][E]["reason"])
                for f in stated:
                    self.assertEqual(view["fields"][f]["status"], "STATED", f)
                if "directors" in stated:
                    self.assertEqual(view["fields"]["directors"]["value"], ["P-001"])

    def test_a_broken_row_or_a_share_sentence_still_blocks(self):
        for place, docs in self.STILL_BLOCKED:
            with self.subTest(place=place):
                self.assertEqual(_run(docs())[0], "BLOCKED")

    def test_ends_list(self):
        from dossier import rules_engine, s1_extract as x
        rules = rules_engine.load(s.ROOT / "rules")
        for text, want in (("Holders:", True), ("5. Directors.", True), ("Holders after the transfer:", True),
                           ("Bice Provetti also joins the board.", True), ("Nothing else is certified.", True),
                           ("  Finti): 60%", False), ("Total: 100%", False), ("Aldo Finti holds 300 quotas.", False),
                           ("The quotas are 1000 in total.", True), ("Aldo Finti (P-001) also joins the board.", False),
                           ("Aldo Finti.", False), ("two thirds", False)):
            with self.subTest(text=text):
                self.assertEqual(x.ends_list(text, rules), want)


class D36_PossessiveOwn(unittest.TestCase):
    """Goal (c): a possessive followed by the adjective 'own' (its own, their own, the company's own) is not a word of
    holding (rules/extract.json neutral_phrases); the verb 'own', and 'own' followed by an article, a determiner or a
    figure, still are (HEV-040). On v2.0.6 the first two cases blocked (a line that may state a holding outside a
    table, in a document of a type the pack does not recognise)."""

    def test_possessive_own(self):
        for text, want in (("The company's own resources are unchanged since the deed.", "OK"),
                           ("The company covers the cost from its own funds.", "OK"),
                           ("Aldo Finti and Bice Provetti own the company in equal parts.", "BLOCKED"),
                           ("Since July they own the whole of it.", "BLOCKED"),
                           ("Aldo Finti's own 60% passes to Bice Provetti.", "BLOCKED")):
            with self.subTest(text=text):
                status, view, prov = _run([deed(), extract(), _odd("Note of the auditor", [text])])
                self.assertEqual(status, want)
                if status == "OK":   # an unread document after the baseline keeps every field [TO CONFIRM] (DISC-005)
                    self.assertTrue(all(f["status"] == "TO_CONFIRM" for f in view["fields"].values()))


class D36_IllegibleAmount(unittest.TestCase):
    """Goal (d): an amount with a currency whose figure cannot be read ('EUR 2#.###,00') is not a bare figure that may
    state a holding (HEV-080). A name and a bare figure still are. On v2.0.6 the first two cases blocked."""

    def test_illegible_amount(self):
        for body, want in ((["Net equity: EUR 2#.###,00", "Total assets: EUR 310.000,00"], "OK"),
                           (["Total assets: € 4##.000", "Revenue: EUR 90.000,00"], "OK"),
                           (["Net equity: EUR 20.000,00", "Bice Provetti 400"], "BLOCKED")):
            with self.subTest(body=body):
                self.assertEqual(_run([deed(), extract(), _odd("Summary of the yearly figures", body, "2025")])[0], want)


class D36_ListLineMessage(unittest.TestCase):
    """Goal (e): lines inside the holders' table that read as lines of another field are named as such (the message
    says they stand in the holders' table and are not rows it reads), not as 'lines that state the directors'."""

    def test_message_names_the_table(self):
        work = s.tmp()
        docs = [_deed_raw(["4. Holders.", "- P-001 (Aldo Finti)", "  three fifths", "- P-002 (Bice Provetti)",
                           "  two fifths", "", "5. Directors.", *DIRS]), extract()]
        s.run(s.tiny(docs, "2026-09-30"), work)
        view = jsonio.load(work / "views" / f"{E}.json")
        why = " ".join(c["fields_check"]["why"] for c in view["warnings"].get("classified_checks", []))
        self.assertIn("stand in the holders' table of line", why)
        self.assertNotIn("state the directors", why)


class D36_UnknownIdentifierIsOpen(unittest.TestCase):
    """Equality only (CLS-005, v2.0.7): a name beside a person identifier is checked against that person's name in the
    identity layer. A corpus whose identity layer names no person cannot check any of them: every holder row and
    director line is open, so the holders block (OWN-015). The price, declared in CHANGELOG 2.0.7; v2.0.6 judged such a
    name by the word list and published."""

    def test_no_person_in_the_identity_layer(self):
        work = s.tmp()
        code, _, report = s.run(s.tiny([deed(), extract()], "2026-09-30", persons=()), work)
        self.assertEqual(report["entities"][E]["status"], "BLOCKED")


class D36_ResidualWordList(unittest.TestCase):
    """The residual risk of CHANGELOG 2.0.7 section 4, [TO CONFIRM], written as a test that is EXPECTED TO FAIL: words of
    the form of an Italian place name (each ends in a vowel), inside a street or a town, that name a person nobody in
    the corpus knows and state something with a verb of no class of slot_not_name_word ('governa', 'presiede'). The
    address passes every check of the slot, the line closes, and every field is published - the directors included,
    whatever those words were meant to say. No grammar tells such a street from 'Via Giuseppe Garibaldi 1'. When this
    test passes, the residual is closed and section 4 must say so."""

    @unittest.expectedFailure
    def test_vowel_words_of_no_class_inside_an_address(self):
        published = []
        for addr in ("Via Ugo Nessuno Governa 1, Montefinto (ZZ)", "Via Nuova 1, Montefinto Ugo Nessuno Presiede (ZZ)"):
            status, view, prov = _run([deed(office_line=f"2. Registered office. The registered office is at {addr}."),
                                       extract(office_line=f"Registered office: {addr}")])
            if status == "OK" and view["fields"]["directors"]["status"] == "STATED":
                published.append(addr)
        self.assertEqual(published, [])


if __name__ == "__main__":
    import json
    got = tally()
    json.dump(got, sys.stdout, indent=1, ensure_ascii=False)
    print()
