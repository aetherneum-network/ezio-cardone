"""D30 (v2.0.3): the forms found by the blind run of v2.0.2 (eval/history.json, run 9), the over-reach of DISC-005,
and what is still not read.

Run 9 (hand-9, an independent hand) blocked 4 of 9 entities wrongly and, on the perturbed corpus of seed 20261013,
published 54 of 144 dossiers with the holders [TO CONFIRM] (780 fields [TO CONFIRM]). By form class (R6):

C1 a holders' heading in another wording: "Shareholders of record:", "Holders (as at the document date):",
   "IV. Quotaholders.", "Shareholding structure at the document date (synthetic):" - now read;
C2 a list line in another form: numbered "1) P-002 (...) - 20%", name first "Elmo Ipotetici (P-010): ...",
   letters, bar or tab separators - now read;
C3 a share in words or with a space: "thirty per cent", "two fifths", "60 %" - now read;
C4 numbers of quotas or shares - read only with the one total the same document states;
C5 a directors' list in the same forms - now read;
C6 DISC-005 over-reach: a document of unrecognised type left every field [TO CONFIRM]; now only the fields its body
   may state (rules/extract.json unread_fields; rules/discrepancy.json unread_document_scope), and not the holders
   when its table read whole equals the one current table;
C7 what is still not read, and still blocks (OWN-015 stays 'block', D26): holders stated in prose, nominal
   amounts, a table with a header row, a heading with an explicit date, counts without a total or mixed with
   shares, counts in a document of unrecognised type, shares in words beyond whole per cent or simple fractions.

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import unittest

from . import support as s
from .support import mk

from dossier import s1_extract, s7_audit
from dossier.lib import jsonio

H = [("P-001", "60%"), ("P-002", "40%")]
CAPITAL = mk.FULL.format(a="50.000,00")
DEED = mk.deed("E-0001", 1, "2024-03-10", mk.OFFICE_A, CAPITAL, H, ["P-001"])
EXTRACT_CAPITAL = "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00"
EXTRACT = mk.extract("E-0001", 2, "2025-02-01", 1, mk.OFFICE_A, EXTRACT_CAPITAL, H, ["P-001"])
TABLE = {"P-001": "3/5", "P-002": "2/5"}
OTHER_FIELDS = ("name", "legal_form", "registered_office", "share_capital.resolved", "share_capital.subscribed",
                "share_capital.paid_in", "directors")


def _reword(doc, old, new):
    rel, text = doc
    assert old in text, old
    return rel, text.replace(old, new)


def _retype(doc, label):
    rel, text = doc
    lines = text.split("\n")
    i = next(i for i, line in enumerate(lines) if line.startswith("Document type: "))
    lines[i] = f"Document type: {label}"
    return rel, "\n".join(lines)


def _doc(n, date, label, edition, body):
    return mk._file("E-0001", f"{date}_doc-{n}.txt", mk._head("E-0001", n, label, date, edition) + body)


def _run(docs):
    work = s.tmp()
    code, _, report = s.run(s.tiny(docs, "2026-06-30"), work)
    view = jsonio.load(work / "views" / "E-0001.json")
    return report["entities"]["E-0001"]["status"], view, work


class _Published(unittest.TestCase):
    def assertPublished(self, docs, table=TABLE, stated=(), to_confirm=()):
        status, view, work = _run(docs)
        self.assertEqual(status, "OK", view["ownership"])
        self.assertTrue((work / "dossiers" / "E-0001").exists())
        if table is not None:
            fld = view["fields"]["shareholders"]
            self.assertEqual(fld["status"], "STATED", fld)
            self.assertEqual({r["holder"]: r["share"] for r in fld["value"]}, table)
        for f in stated:
            self.assertEqual(view["fields"][f]["status"], "STATED", (f, view["fields"][f]))
        for f in to_confirm:
            self.assertEqual(view["fields"][f]["status"], "TO_CONFIRM", (f, view["fields"][f]))
        return view

    def assertBlocked(self, docs, rule="OWN-015"):
        status, view, work = _run(docs)
        self.assertEqual(status, "BLOCKED", view["ownership"])
        self.assertEqual(view["ownership"]["rule"], rule, view["ownership"])
        self.assertFalse((work / "dossiers" / "E-0001").exists())


class C1_HeadingForms(_Published):
    def test_shareholders_of_record(self):                       # hand-9 E-0007, extract
        self.assertPublished([DEED, _reword(EXTRACT, "Holders:", "Shareholders of record:")])

    def test_holders_as_at_the_document_date_in_parentheses(self):  # hand-9 E-0009, extract
        self.assertPublished([DEED, _reword(EXTRACT, "Holders:", "Holders (as at the document date):")])

    def test_roman_clause_number_and_quotaholders(self):
        self.assertPublished([_reword(DEED, "4. Holders.", "IV. Quotaholders.")])

    def test_shareholding_structure_at_the_document_date(self):   # hand-9 E-0007, statement (type not recognised)
        stmt = _doc(2, "2025-02-01", "Statement of shareholdings", "STATEMENT/1",
                    ["Shareholding structure at the document date (synthetic):", *mk._holders(H)])
        # the heading is read (the table is checked and sums to the whole); the type is not recognised, so since
        # v2.0.4 (D30b, unread_document_scope every_field) every field is [TO CONFIRM] - v2.0.3 stated the others
        doc = s1_extract.parse_document(stmt[1], stmt[0], s.rules())
        hc = s1_extract.holders_check(doc, s.rules())
        self.assertEqual(hc["status"], "read", hc)
        self.assertEqual({r["holder"]: r["share"] for r in hc["tables"][0]["value"]}, TABLE)
        self.assertPublished([DEED, stmt], table=None, to_confirm=OTHER_FIELDS + ("shareholders",))


class C2_ItemForms(_Published):
    def test_numbered_items_with_a_spaced_dash(self):             # hand-9 E-0009, deed
        doc = _reword(_reword(DEED, "- P-001 (Aldo Finti): 60%", "1) P-001 (Aldo Finti) - 60%"),
                      "- P-002 (Bice Provetti): 40%", "2) P-002 (Bice Provetti) - 40%")
        self.assertPublished([doc])

    def test_name_first(self):                                     # hand-9 E-0008, deed
        doc = _reword(_reword(DEED, "- P-001 (Aldo Finti): 60%", "- Aldo Finti (P-001): 60%"),
                      "- P-002 (Bice Provetti): 40%", "- Bice Provetti (P-002): 40%")
        self.assertPublished([doc])

    def test_letters_bar_and_tab(self):
        for a, b in (("(a) P-001 (Aldo Finti): 60%", "(b) P-002 (Bice Provetti): 40%"),
                     ("P-001 (Aldo Finti) | 60%", "P-002 (Bice Provetti) | 40%"),
                     ("P-001 (Aldo Finti)\t60%", "P-002 (Bice Provetti)\t40%")):
            with self.subTest(line=a):
                doc = _reword(_reword(DEED, "- P-001 (Aldo Finti): 60%", a), "- P-002 (Bice Provetti): 40%", b)
                self.assertPublished([doc])

    def test_name_first_in_a_document_of_unrecognised_type_is_read(self):
        # until v2.0.2 this line blocked the entity (tests/test_holders_forms.py, class B limits)
        doc = _retype(_reword(mk.transfer("E-0001", 2, "2025-05-05", [("P-001", "50%"), ("P-002", "30%"),
                                                                       ("P-003", "20%")]),
                              "- P-003 (Carlo Inventati): 20%", "- Carlo Inventati (P-003): 20%"),
                      "Notice of assignment of shares")
        self.assertPublished([DEED, doc], table=None, to_confirm=["shareholders"])


class C3_SharesInWords(_Published):
    def test_per_cent_in_words(self):                              # hand-9 E-0007, statement
        doc = _reword(_reword(DEED, ": 60%", ": sixty per cent"), ": 40%", ": forty per cent")
        self.assertPublished([doc])

    def test_fractions_in_words_and_a_spaced_percent(self):
        doc = _reword(_reword(DEED, ": 60%", ": three fifths"), ": 40%", ": 40 %")
        self.assertPublished([doc])


class C4_CountsWithATotal(_Published):
    COUNTED = _reword(_reword(_reword(DEED, CAPITAL, "The share capital is EUR 50.000,00, divided into 500 quotas "
                                                     "of EUR 100,00 each, fully subscribed and fully paid in."),
                              "- P-001 (Aldo Finti): 60%", "- Aldo Finti (P-001): 300 quotas"),
                      "- P-002 (Bice Provetti): 40%", "- Bice Provetti (P-002): 200 quotas")

    def test_counts_divided_by_the_total_of_the_same_document(self):   # hand-9 E-0008, deed
        self.assertPublished([self.COUNTED])

    def test_counts_without_a_total_are_not_read(self):
        self.assertBlocked([_reword(self.COUNTED, ", divided into 500 quotas of EUR 100,00 each", "")])

    def test_two_totals_are_not_read(self):
        self.assertBlocked([_reword(self.COUNTED, "fully paid in.", "fully paid in. The capital consists of 50 quotas.")])

    def test_counts_that_do_not_add_up_to_the_total_do_not_sum(self):
        self.assertBlocked([_reword(self.COUNTED, "300 quotas", "250 quotas")], rule="OWN-010")

    def test_audit_rederives_the_shares_from_the_quote(self):
        quote = ("3. Share capital. The share capital is EUR 50.000,00, divided into 500 quotas.\n4. Holders.\n"
                 "- Aldo Finti (P-001): 300 quotas\n- Bice Provetti (P-002): 200 quotas")
        fig = {"section": "cap_table", "field": "shareholders", "holder": "P-001", "value": "3/5", "quote": quote}
        self.assertTrue(s7_audit.supported_by_quote(fig))
        self.assertFalse(s7_audit.supported_by_quote(dict(fig, quote=quote.replace("500 quotas", "600 quotas"))))
        self.assertFalse(s7_audit.supported_by_quote(dict(fig, quote=quote.replace("divided into 500 quotas", "paid"))))


class C5_DirectorsForms(_Published):
    def test_name_first_and_numbered_directors(self):
        doc = _reword(mk.deed("E-0001", 1, "2024-03-10", mk.OFFICE_A, CAPITAL, H, ["P-001", "P-002"]),
                      "- P-001 (Aldo Finti)\n- P-002 (Bice Provetti)", "- Aldo Finti (P-001)\n2) P-002 (Bice Provetti)")
        view = self.assertPublished([doc], stated=["directors"])
        self.assertEqual(view["fields"]["directors"]["value"], ["P-001", "P-002"])


class C6_UnreadDocumentScope(_Published):
    """DISC-005. v2.0.3 scoped it to the fields the unread document may state (fields_it_may_state); the blind run
    of v2.0.3 (eval/history.json run 11, E-0015) showed a sentence that changes a field without naming it, so since
    v2.0.4 (D30b) the default is every_field again: the three documents below keep every field [TO CONFIRM]. With
    the narrow scope (OFF, rules/discrepancy.json unread_document_scope) they keep only the fields named."""

    LEDGER = _doc(3, "2026-06-10", "Ledger of quotaholders", "LEDGER/1",
                  ["Entries of the ledger as at the document date (synthetic).", "Quotaholders:", *mk._holders(H)])

    def test_ledger_of_unrecognised_type_that_agrees_keeps_every_field(self):   # hand-9 E-0006
        view = self.assertPublished([DEED, EXTRACT, self.LEDGER], table=None,
                                    to_confirm=OTHER_FIELDS + ("shareholders",))
        self.assertNotIn("unread_agreeing", view["fields"]["shareholders"])

    def test_register_with_another_table_keeps_every_field(self):
        reg = _retype(_doc(3, "2026-06-10", "Holders' ledger", "LEDGER/1",
                           ["Members at the document date:", *mk._holders([("P-001", "1/2"), ("P-002", "1/2")])]),
                      "Register of members")
        self.assertPublished([DEED, EXTRACT, reg], table=None, to_confirm=OTHER_FIELDS + ("shareholders",))

    def test_minutes_of_a_change_of_seat_keep_every_field(self):
        doc = _retype(mk.office_transfer("E-0001", 3, "2025-05-05", "The registered office is transferred from "
                                         f"{mk.OFFICE_A} to {mk.OFFICE_B}."), "Minutes - change of seat")
        self.assertPublished([DEED, doc], table=None, to_confirm=OTHER_FIELDS + ("shareholders",))

    def test_the_narrow_scope_is_an_option_that_is_off(self):
        self.assertEqual(s.rules().param("discrepancy", "unread_document_scope"), "every_field")
        # with the option on (v2.0.3's default) the agreeing ledger changes nothing - the behaviour it was made for
        work = s.tmp()
        code, _, report = s.run(s.tiny([DEED, EXTRACT, self.LEDGER], "2026-06-30"), work,
                                rules_dir=s.rules_narrow_scope())
        view = jsonio.load(work / "views" / "E-0001.json")
        self.assertEqual(view["fields"]["shareholders"]["status"], "STATED")
        self.assertEqual(view["fields"]["shareholders"].get("unread_agreeing"), ["DOC-E0001-03"])

    def test_a_line_no_topic_explains_keeps_every_field(self):
        doc = _doc(3, "2025-05-05", "Memorandum", "MEMO/1", ["Reference: ABC-17"])
        self.assertPublished([DEED, doc], table=None, to_confirm=OTHER_FIELDS + ("shareholders",))

    def test_a_correction_keeps_every_field(self):
        doc = _doc(3, "2025-05-05", "Memorandum", "MEMO/1", ["The resolution of 3 March is annulled."])
        self.assertPublished([DEED, doc], table=None, to_confirm=OTHER_FIELDS + ("shareholders",))

    def test_a_sentence_no_rule_explains_keeps_every_field(self):
        # FEV-999: no topic word, no figure, no identifier - a person named without identifier. The word lists
        # never close, so what they do not know keeps every field [TO CONFIRM].
        for line in ("Ugo Apparenti now runs the company.", "Lia Inesistente sold everything to Ugo Apparenti."):
            with self.subTest(line=line):
                doc = _doc(3, "2025-05-05", "Memorandum", "MEMO/1", [line])
                self.assertPublished([DEED, doc], table=None, to_confirm=OTHER_FIELDS + ("shareholders",))

    def test_fields_check_of_a_header_problem_is_every_field(self):
        rel, text = _reword(_doc(3, "2025-05-05", "Memorandum", "MEMO/1", ["Nothing."]),
                            "Document date: 2025-05-05", "Document date: fifth of May 2025")
        doc = s1_extract.parse_document(text, rel, s.rules())
        got = s1_extract.fields_check(doc, s.rules(), s1_extract.holders_check(doc, s.rules()))
        self.assertEqual(got["may_change"], ["*"])


class C7_StillNotRead(_Published):
    """Known limits of v2.0.3 (CHANGELOG, README, eval/BLIND_PROTOCOL.md): each still blocks the entity."""

    def test_holders_in_prose(self):                               # hand-9 E-0007, deed
        doc = mk._file("E-0001", "2024-03-10_deed.txt", mk._head("E-0001", 1, "Deed of incorporation", "2024-03-10",
                                                                  "DEED/1") + [
            "1. Name and form. The company is named Fornace Aurelia S.r.l.; its legal form is S.r.l.",
            f"2. Registered office. The registered office is at {mk.OFFICE_A}.", f"3. Share capital. {CAPITAL}",
            "4. Capital allocation. The share capital is held by P-001 (Aldo Finti) as to 60% and by P-002 "
            "(Bice Provetti) as to 40%.", "", "5. Directors.", "- P-001 (Aldo Finti)"])
        self.assertBlocked([doc])

    def test_nominal_amounts(self):                                # hand-9 E-0003, deed
        doc = _reword(_reword(DEED, ": 60%", ": nominal EUR 30.000,00"), ": 40%", ": nominal EUR 20.000,00")
        self.assertBlocked([doc])

    def test_table_with_a_header_row(self):                        # hand-9 E-0003, extract
        ext = _reword(EXTRACT, "Holders:\n- P-001 (Aldo Finti): 60%\n- P-002 (Bice Provetti): 40%",
                      "Quotaholders:\n| Holder | Nominal quota | Share |\n| P-001 (Aldo Finti) | EUR 30'000.00 | 60 % |\n"
                      "| P-002 (Bice Provetti) | EUR 20'000.00 | 40 % |")
        self.assertBlocked([DEED, ext])

    def test_heading_with_an_explicit_date(self):
        self.assertBlocked([DEED, _reword(EXTRACT, "Holders:", "Holders at 16 February 2026:")])

    def test_counts_mixed_with_shares(self):
        doc = _reword(_reword(DEED, CAPITAL, "The share capital is EUR 50.000,00, divided into 500 quotas, fully "
                                             "subscribed and fully paid in."), ": 60%", ": 300 quotas")
        self.assertBlocked([doc])

    def test_counts_in_a_document_of_unrecognised_type(self):
        doc = _doc(2, "2025-02-01", "Register of members", "LEDGER/1",
                   ["The capital is divided into 500 quotas.", "Members:", "- P-001 (Aldo Finti): 300 quotas",
                    "- P-002 (Bice Provetti): 200 quotas"])
        self.assertBlocked([DEED, doc])

    def test_shares_in_words_that_are_not_read(self):
        for a, b in ((": half", ": half"), (": thirty point five per cent", ": sixty-nine point five per cent"),
                     (": two third", ": one third")):
            with self.subTest(share=a):
                self.assertBlocked([_reword(_reword(DEED, ": 60%", a), ": 40%", b)])

    def test_nested_parentheses(self):
        self.assertBlocked([_reword(DEED, "- P-001 (Aldo Finti): 60%", "- P-001 (Aldo (Al) Finti): 60%")])


if __name__ == "__main__":
    unittest.main()
