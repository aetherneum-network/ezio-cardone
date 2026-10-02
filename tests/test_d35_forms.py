"""D35 (v2.0.6): typed slots that admit more than their own value. The blind run of v2.0.5 (eval/history.json run 14)
probed the residual risk of section 4 of CHANGELOG 2.0.5 with two hand entities that a one-character cliff of the
deed masked: a person slot 'Hilde Simulanti Sole Proprietress Henceforth' in a director line (E-0011) and an extract
whose 'Name:' ends in S.p.A. while its 'Legal form:' says S.r.l. (E-0012).

Since v2.0.6 a slot that holds a name (parameter slot_name_groups of rules/extract.json) carrying a word that cannot
be part of a name (parameter slot_not_name_word: role, holding, time and function words, and English suffix classes)
does not pass: the line falls to CLS-999 and the document may change every field (DISC-006). A name beside an
identifier that is not the identifier's own name (the identity layer for a person, the header of the entity's own
documents for a company) does the same, by CLS-005. A name whose legal form differs from the legal form stated is a
discrepancy of its own (DISC-035 of rules/discrepancy.json): both readings listed with their sources, nothing
reconciled, the name and the legal form [TO CONFIRM].

A slot of the entity's own name (parameter slot_own_name_groups) closes its line only when it is the name of the
document's own header 'Entity:', legal form aside: a word of no class of the lexicon is told from a name by that
equality (for a person, by CLS-005 against the identity layer), not by the lexicon.

The siblings are tested by class, never by literal strings (R6): person slots with trailing words in director lines
(deed, extract, appointment) and in holder rows (deed, extract, transfer, ledger), each in the form 'ID (name)' and
'name (ID)'; company names whose legal form differs from the one stated; company names with words that are not part
of a name; the same slots with words of no class of the lexicon; address slots and amount slots with a trailing
clause. The base is a deed and a registry extract that agree;
a later document is dated after both. Every case must end with the fields it may change not published as fact, or
blocked. tests/test_d35_forms.py was also run on the code of v2.0.5 (CHANGELOG 2.0.6 gives the count, by class).

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import unittest

from . import support as s
from .support import mk

from dossier import rules_engine, s1_extract
from dossier.lib import jsonio

E = "E-0001"
NAME, FORM = mk.ENT[E]                      # Fornace Aurelia S.r.l., S.r.l.
BARE = NAME[: -len(FORM)].strip()           # Fornace Aurelia
H = [("P-001", "60%"), ("P-002", "40%")]
CAPITAL = mk.FULL.format(a="50.000,00")
EXTRACT_CAPITAL = "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00"
CAPITAL_FIELDS = ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")
ALL = ("name", "legal_form", "registered_office", "directors", "shareholders", *CAPITAL_FIELDS)

# words that are not part of a name, by class of the lexicon (role, holding, time, function, Italian, suffix class)
TRAILING = (
    ("holding and time", "Sole Proprietress Henceforth"),
    ("holding", "Sole Owner"),
    ("role", "Managing Director"),
    ("time", "Henceforth"),
    ("suffix -ly", "Solely"),
    ("suffix -ship", "Partnership"),
    ("function words", "Who Holds It All"),
    ("Italian holding", "Socio Unico"),
    ("Italian time", "Ora Titolare"),
)
# words of no class of the lexicon: only equality with the identity layer (a person) or with the document's own header
# 'Entity:' (the company) can tell them from a name
NO_CLASS = (
    ("one word of no class", "Padrona"),
    ("two words of no class", "Vecchie Zeta"),
)


def deed(**o):
    """The deed of scenarios/make_inputs.py (the generator's form), with lines replaced."""
    return mk._file(E, "2024-03-10_deed.txt", mk._head(E, 1, "Deed of incorporation", "2024-03-10", "DEED/1") + [
        o.get("name_line", f"1. Name and form. The company is named {NAME}; its legal form is {FORM}"),
        o.get("office_line", f"2. Registered office. The registered office is at {mk.OFFICE_A}."),
        o.get("capital_line", f"3. Share capital. {CAPITAL}"),
        "4. Holders.", *o.get("holders", mk._holders(H)), "",
        "5. Directors.", *o.get("directors", mk._directors(["P-001"]))])


def extract(**o):
    return mk._file(E, "2025-02-01_registry-extract.txt",
                    mk._head(E, 2, "Test registry extract", "2025-02-01", "EXTRACT/1") + [
                        o.get("name_line", f"Name: {NAME}"), o.get("form_line", f"Legal form: {FORM}"),
                        o.get("office_line", f"Registered office: {mk.OFFICE_A}"),
                        o.get("capital_line", EXTRACT_CAPITAL),
                        "Holders:", *o.get("holders", mk._holders(H)), "",
                        "Directors:", *o.get("directors", mk._directors(["P-001"]))])


def later(kind: str, body: list[str]):
    label, title, edition, slug = {
        "APPOINTMENT": ("Appointment of directors", "Minutes of the holders' meeting (synthetic).", "APPOINTMENT/1",
                        "appointment_P-001"),
        "TRANSFER": ("Share transfer notice", "Notice of a transfer of shares (synthetic).", "TRANSFER/1",
                     "share-transfer"),
        "LEDGER": ("Holders' ledger", None, "LEDGER/1", "holders-ledger"),
        "OFFICE": ("Transfer of registered office", None, "OFFICE/1", "office-transfer"),
        "RESOLUTION": ("Resolution on share capital", "Minutes of the holders' meeting (synthetic).", "RESOLUTION/1",
                       "capital-resolution"),
    }[kind]
    return mk._file(E, f"2026-08-20_{slug}.txt", mk._head(E, 3, label, "2026-08-20", edition)
                    + ([title] if title else []) + body)


def person_rows(t: str, share: str | None):
    """A row of P-001 whose name slot carries the trailing words, in both forms of the item grammar."""
    tail = f": {share}" if share else ""
    return (("ID (name)", f"- P-001 (Aldo Finti {t}){tail}"), ("name (ID)", f"- Aldo Finti {t} (P-001){tail}"))


def _director_cases(words=TRAILING):
    for wname, t in words:
        for form, row in person_rows(t, None):
            yield wname, form, "deed", [deed(directors=[row]), extract()]
            yield wname, form, "extract", [deed(), extract(directors=[row])]
            yield wname, form, "appointment", [deed(), extract(),
                                               later("APPOINTMENT", ["Directors in office after this appointment:",
                                                                     row])]


def _holder_cases(words=TRAILING):
    for wname, t in words:
        for form, row in person_rows(t, "60%"):
            other = mk._holders([("P-002", "40%")])
            yield wname, form, "deed", [deed(holders=[row, *other]), extract()]
            yield wname, form, "extract", [deed(), extract(holders=[row, *other])]
            yield wname, form, "transfer", [deed(), extract(), later("TRANSFER", ["Holders after the transfer:", row,
                                                                                 *other])]
            yield wname, form, "ledger", [deed(), extract(), later("LEDGER", ["Holders:", row, *other])]


# (class, wording, documents, fields that must not be published as fact)
def cases():
    for wname, form, place, docs in _director_cases():
        yield "A person slot with trailing words in a director line", f"{wname}, {form}, {place}", docs, \
            ("directors", "shareholders")
    for wname, form, place, docs in _holder_cases():
        yield "A person slot with trailing words in a holder row", f"{wname}, {form}, {place}", docs, ("shareholders",)
    other = "S.p.A."
    for wording, docs in (
            ("extract name, dotted", [deed(), extract(name_line=f"Name: {BARE} {other}")]),
            ("extract name, undotted", [deed(), extract(name_line=f"Name: {BARE} SpA")]),
            ("extract name, lower case", [deed(), extract(name_line=f"Name: {BARE} s.p.a.")]),
            ("deed name", [deed(name_line=f"1. Name and form. The company is named {BARE} {other}; its legal form is "
                                          f"{FORM}"), extract()]),
            ("both names, one form", [deed(name_line=f"1. Name and form. The company is named {BARE} {other}; its "
                                                     f"legal form is {FORM}"),
                                      extract(name_line=f"Name: {BARE} {other}")]),
            ("extract form", [deed(), extract(form_line=f"Legal form: {other}")]),
            ("S.r.l.s. against S.r.l.", [deed(), extract(name_line=f"Name: {BARE} S.r.l.s.")])):
        yield "A company name whose legal form differs from the one stated", wording, docs, ("name", "legal_form")
    for wname, t in TRAILING:
        yield "A company name slot with words that are not part of a name", f"{wname}, extract", \
            [deed(), extract(name_line=f"Name: {BARE} {t} {FORM}")], ALL
        yield "A company name slot with words that are not part of a name", f"{wname}, deed", \
            [deed(name_line=f"1. Name and form. The company is named {BARE} {t} {FORM}; its legal form is {FORM}"),
             extract()], ALL
    for wname, form, place, docs in _director_cases(NO_CLASS):
        yield "A person slot with words of no class (director line)", f"{wname}, {form}, {place}", docs, \
            ("directors", "shareholders")
    for wname, form, place, docs in _holder_cases(NO_CLASS):
        yield "A person slot with words of no class (holder row)", f"{wname}, {form}, {place}", docs, ("shareholders",)
    for wname, t in NO_CLASS:
        yield "A company name slot with words of no class", f"{wname}, extract", \
            [deed(), extract(name_line=f"Name: {BARE} {t} {FORM}")], ALL
        yield "A company name slot with words of no class", f"{wname}, deed", \
            [deed(name_line=f"1. Name and form. The company is named {BARE} {t} {FORM}; its legal form is {FORM}"),
             extract()], ALL
    for wording, docs, changes in (
            ("extract, a word in the town", [deed(), extract(office_line="Registered office: Via del Collaudo 7, "
                                                                         "Borgoprova Henceforth (ZZ)")],
             ("registered_office",)),
            ("extract, a holding after the town", [deed(), extract(office_line=f"Registered office: {mk.OFFICE_A}, "
                                                                               "where P-003 now holds every quota")],
             ("registered_office", "shareholders")),
            ("deed, a holding after the address", [deed(office_line=f"2. Registered office. The registered office is "
                                                                    f"at {mk.OFFICE_A}, held by the sole member."),
                                                   extract()], ("registered_office", "shareholders")),
            ("office transfer, a holding after the address", [deed(), extract(), later(
                "OFFICE", [f"The registered office is transferred from {mk.OFFICE_A} to {mk.OFFICE_B}, together with "
                           f"every quota of P-002."])], ("registered_office", "shareholders")),
            ("office transfer, a word in the town", [deed(), extract(), later(
                "OFFICE", [f"The registered office is transferred from {mk.OFFICE_A} to Piazza del Campione 3, "
                           f"Montefinto Solely (ZZ)."])], ("registered_office",))):
        yield "An address slot with a trailing clause", wording, docs, changes
    for wording, docs, changes in (
            ("deed, paid in by one holder", [deed(capital_line="3. Share capital. The share capital is EUR 50.000,00, "
                                                               "fully subscribed and fully paid in by P-002 alone."),
                                             extract()], ("shareholders",)),
            ("extract, subscribed by the sole member", [deed(), extract(
                capital_line="Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00 by the sole member; "
                             "paid in EUR 50.000,00")], ("shareholders", *CAPITAL_FIELDS)),
            ("extract, a clause after the last amount", [deed(), extract(
                capital_line="Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00 "
                             "henceforth all by P-003")], ("shareholders", *CAPITAL_FIELDS)),
            ("resolution, taken up by a new holder", [deed(), extract(), later(
                "RESOLUTION", ["The meeting resolved to increase the share capital from EUR 50.000,00 to EUR "
                               "80.000,00, wholly taken up by Carlo Inventati."])], ("shareholders",))):
        yield "An amount slot with a trailing clause", wording, docs, changes


def _run(docs):
    work = s.tmp()
    code, _, report = s.run(s.tiny(docs, "2026-09-30"), work)
    status = report["entities"][E]["status"]
    view = jsonio.load(work / "views" / f"{E}.json")
    prov_path = work / "dossiers" / E / "provenance.json"
    prov = jsonio.load(prov_path) if prov_path.exists() else None
    return status, view, prov


def unsafe(status: str, view: dict, prov: dict | None, changes) -> str:
    """'' when the case is safe (blocked, or no field it may change published as fact and no holding derived from a
    table the slot may contradict), else what was published wrongly."""
    if status == "BLOCKED" and prov is None:
        return ""
    if status != "OK":
        return f"status {status}"
    wrong = [f for f in changes if f in view["fields"] and view["fields"][f]["status"] == "STATED"]
    if "shareholders" in changes and (prov["derived"] or [f for f in prov["figures"] if f["section"] == "cap_table"]):
        wrong.append("holdings derived")
    return ", ".join(wrong)


class D35_TypedSlotSiblings(unittest.TestCase):
    def test_every_sibling_is_safe(self):
        n = 0
        outcomes = s.sweep(_run, [(docs,) for _, _, docs, _ in cases()])
        for (cls, wording, docs, changes), outcome in zip(cases(), outcomes):
            with self.subTest(cls=cls, wording=wording):
                n += 1
                self.assertEqual(unsafe(*outcome.result(), changes), "")
        self.assertEqual(n, (len(TRAILING) + len(NO_CLASS)) * (2 * 3 + 2 * 4 + 2) + 7 + 5 + 4)


class D35_ExactFormProbes(unittest.TestCase):
    """The two probes of hand-14 in the exact form the deed of v2.0.5 reads, on entities of this test (not the hand
    corpus): nothing is published wrongly."""

    def test_person_slot_probe(self):
        status, view, prov = _run([deed(), extract(), later("APPOINTMENT", [
            "Directors in office after this appointment:", "- P-003 (Carlo Inventati Sole Proprietress Henceforth)"])])
        self.assertIn(status, ("OK", "BLOCKED"))
        if prov is not None:
            self.assertNotEqual(view["fields"]["shareholders"]["status"], "STATED")
            self.assertEqual(prov["derived"], [])
            self.assertEqual([f for f in prov["figures"] if f["section"] == "cap_table"], [])
            d = view["fields"]["directors"]
            self.assertTrue(d["status"] == "TO_CONFIRM" or d.get("value") == ["P-003"], d)
        self.assertIn("*", next(c for c in view["warnings"]["classified_checks"]
                                if c["doc_id"] == "DOC-E0001-03")["fields_check"]["may_change"])

    def test_name_and_legal_form_probe(self):
        status, view, prov = _run([deed(), extract(name_line=f"Name: {BARE} S.p.A.")])
        self.assertEqual(status, "OK", view["ownership"])
        self.assertEqual(view["fields"]["name"]["status"], "DISCREPANCY")
        self.assertEqual(sorted(c["value"] for c in view["fields"]["name"]["candidates"]),
                         [f"{BARE} S.p.A.", NAME])
        lf = view["fields"]["legal_form"]
        self.assertEqual((lf["status"], lf["rule"]), ("TO_CONFIRM", "DISC-035"))
        self.assertNotIn("value", lf)
        self.assertIn(f"{BARE} S.p.A.", lf["reason"])
        self.assertEqual(sorted(c["value"] for c in lf["readable"]), [FORM])
        for f in ("registered_office", "directors", "shareholders", *CAPITAL_FIELDS):
            self.assertEqual(view["fields"][f]["status"], "STATED", f)


def hand_14_variant(work) -> tuple:
    """A fixture of this test, built at run time from the seen corpus eval/blind/hand-14 (which is not changed):
    entities E-0011 and E-0012 with the deed's legal-form clause in the exact form v2.0.5 reads ('S.r.l.' then the
    end of the line, not 'S.r.l..'), so that nothing else in the entity makes it abstain. (input, gold)"""
    import json
    hand = s.ROOT / "eval" / "blind" / "hand-14"
    inp = work / "input"
    for eid in ("E-0011", "E-0012"):
        for f in sorted((hand / "input" / "entities" / eid).glob("*.txt")):
            text = f.read_text(encoding="utf-8").replace("; its legal form is S.r.l..\n", "; its legal form is S.r.l.\n")
            jsonio.write_bytes(inp / "entities" / eid / f.name, text.encode("utf-8"))
    persons = jsonio.load(hand / "input" / "identity" / "persons.json")
    jsonio.write(inp / "identity" / "persons.json", {k: persons[k] for k in ("P-002", "P-003", "P-015", "P-016")})
    jsonio.write_bytes(inp / "config.json", (hand / "input" / "config.json").read_bytes())
    gold = json.loads((hand / "gold.json").read_text(encoding="utf-8"))
    gold["entities"] = {k: v for k, v in gold["entities"].items() if k in ("E-0011", "E-0012")}
    jsonio.write(work / "gold.json", gold)
    return inp, work / "gold.json"


class D35_HandFourteenExactForm(unittest.TestCase):
    """Goal (a) on seen data: hand-14 E-0011 and E-0012 unmasked (the deed in the exact form). v2.0.5 publishes 3
    never-events on this variant (E-0011 holders and effective holdings, E-0012 legal form); v2.0.6 none."""

    def test_unmasked_probes_publish_nothing_wrong(self):
        from eval import score
        work = s.tmp()
        inp, gold = hand_14_variant(work)
        got = score.evaluate("hand-14-exact-form", corpus=inp, gold_path=gold, work=work / "run")
        self.assertEqual(got["metrics"]["never_events"], 0, got["never_event_list"])
        # v2.0.8: [TO CONFIRM] kept 2/2, E-0012's legal form [TO CONFIRM] by DISC-035 and its name a DISCREPANCY;
        # since v2.0.9 (D38) every entity of this corpus is blocked: the persons of its holders' rows are not of the
        # gazetteer (free_text_identification), the rows are read by no rule and may state a holding (OWN-015); the
        # price of CHANGELOG 2.0.9 section 3. The legal-form
        # rule DISC-035 is still tested on fixtures of the gazetteer (tests/test_d35_forms.py, tests/test_d37_slots.py)
        self.assertEqual(got["metrics"]["to_confirm_kept"], "0/0")
        v11 = jsonio.load(work / "run" / "work" / "views" / "E-0011.json")
        self.assertTrue(all(f["status"] != "STATED" for f in v11["fields"].values()), v11["fields"])
        v12 = jsonio.load(work / "run" / "work" / "views" / "E-0012.json")
        self.assertTrue(all(f["status"] != "STATED" for f in v12["fields"].values()), v12["fields"])
        report = jsonio.load(work / "run" / "work" / "run_report.json")["entities"]
        self.assertEqual((report["E-0011"]["status"], report["E-0012"]["status"]), ("BLOCKED", "BLOCKED"))


class D35_PlainNamesStillPublish(unittest.TestCase):
    """The cost side: the documents of the generator's own forms are still read."""

    def test_plain_documents(self):
        status, view, prov = _run([deed(), extract(), later("APPOINTMENT", [
            "Directors in office after this appointment:", *mk._directors(["P-001", "P-002"])])])
        self.assertEqual(status, "OK", view["ownership"])
        for f in ALL:
            self.assertEqual(view["fields"][f]["status"], "STATED", (f, view["fields"][f]))
        self.assertEqual(view["warnings"]["classified_checks"], [])


def memo(body: list[str]):
    """A document of a type the rules do not know, dated after the deed and the extract."""
    return mk._file(E, "2026-08-20_memorandum.txt", mk._head(E, 3, "Memorandum", "2026-08-20", "MEMO/1") + body)


class D35_UnreadScopeReported(unittest.TestCase):
    """Goal (b), hand-14 E-0013: the fields check of an unread document reports what DISC-005 applies. Under the
    default scope every_field it reports every field, and keeps the judgement of the lines as a note; under the
    narrow scope (OFF) it reports the fields its lines may state, as before."""

    LINES = ["The share capital is EUR 90.000,00."]

    def _check(self, rules):
        rel, text = memo(self.LINES)
        doc = s1_extract.parse_document(text, rel, rules)
        return s1_extract.fields_check(doc, rules, s1_extract.holders_check(doc, rules))

    def test_default_scope_reports_every_field(self):
        got = self._check(s.rules())
        self.assertEqual(got["may_change"], ["*"])
        self.assertIn("every_field", got["why"])
        self.assertIn("DISC-005", got["why"])
        self.assertIn("share_capital", got["why"])           # the judgement of the lines, kept as a note

    def test_narrow_scope_reports_the_fields_named(self):
        got = self._check(rules_engine.load(s.rules_narrow_scope()))
        self.assertNotIn("*", got["may_change"])
        self.assertIn("share_capital.*", got["may_change"])

    def test_the_record_says_every_field_end_to_end(self):
        status, view, _ = _run([deed(), extract(), memo(self.LINES)])
        fc = [u["fields_check"] for u in view["warnings"]["unclassified_documents"] if u.get("fields_check")]
        self.assertTrue(fc, view["warnings"])
        self.assertEqual(fc[0]["may_change"], ["*"])
        for f in ALL:
            self.assertNotEqual(view["fields"][f]["status"], "STATED", f)


class D35_HeadingWithParticipialClause(unittest.TestCase):
    """Goal (d), hand-14 E-0007: a holders' heading whose qualifier of the class 'registered' follows the noun after a
    comma is the same heading as without the comma. A participle of another class after a comma is not a heading."""

    def test_comma_qualifier_reads_like_the_plain_one(self):
        for heading in ("4. Shareholdings, entered in the register:",
                        "4. Members, as recorded in the book of members:"):
            with self.subTest(heading=heading):
                status, view, prov = _run([(deed()[0], deed()[1].replace("4. Holders.", heading)), extract()])
                self.assertEqual(status, "OK", view["ownership"])
                self.assertEqual(view["fields"]["shareholders"]["status"], "STATED")
                self.assertEqual(view["warnings"]["classified_checks"], [])

    def test_other_participle_is_not_a_heading(self):
        heading = "4. Shareholdings, transferred on 1 May:"
        status, view, prov = _run([(deed()[0], deed()[1].replace("4. Holders.", heading)), extract()])
        self.assertTrue(status == "BLOCKED" or view["fields"]["shareholders"]["status"] != "STATED", status)


class D35_HandCorpus14(unittest.TestCase):
    """Goal (c) and (f), through the scorer: hand-14 (eval/history.json run 14) with the one-character cliff read,
    0 never-events, every gold [TO CONFIRM] kept; the result names the pipeline's exit code (pipeline_status)."""

    def test_hand_14(self):
        from eval import score
        from dossier import run as dossier_run
        d = s.ROOT / "eval" / "blind" / "hand-14"
        got = score.evaluate("hand-14", corpus=d / "input", gold_path=d / "gold.json", work=s.tmp())
        self.assertEqual(got["metrics"]["never_events"], 0, got["never_event_list"])
        # v2.0.5: facts exact 2/64 (run 14); v2.0.7: 27/64; v2.0.8 (D37): 14/64, the measured cost of corroboration
        # (CHANGELOG 2.0.8), [TO CONFIRM] kept 7/7; since v2.0.9 (D38) every entity of this corpus is blocked: the
        # persons of its holders' rows are not of the gazetteer (free_text_identification), the rows are read by no rule
        # and may state a holding (OWN-015); the price of CHANGELOG 2.0.9 section 3
        self.assertEqual(got["metrics"]["to_confirm_kept"], "0/0")
        self.assertEqual((got["counts"]["published"], got["counts"]["fact_exact"]), (0, 0))
        self.assertIn("exit_code", got)
        self.assertEqual(dossier_run.EXIT[got["pipeline_status"]], got["exit_code"])


if __name__ == "__main__":
    unittest.main()
