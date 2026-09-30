"""D26 follow-up (owner decision of 2026-09-30: OWN-015 stays 'block'): more holders'-table forms are read.

On the stress suite and on the perturbed corpora of the recorded seeds, entities were blocked for two form
classes (eval/history.json, run 7 and the v2.0.2 entry):

A. a holders' heading in another wording ("Members:", "4. Members.", "Members at the document date:",
   "After the transfer the members are:", "Shareholders:"): the heading is now a grammar (rules/extract.json,
   parameter holders_heading); a qualifier not known to mean "current" is still not a heading, and two
   headings in one document abstain;
B. a document whose type is not recognised: its body is now checked (rules/extract.json holders_evidence).
   No table and no line that may state a holding: it no longer blocks. Tables read whole: they are summed.
   Anything else - a table not read whole, a line that may state a holding, two tables, a header that
   cannot be read - blocks the entity as before.

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import unittest

from . import support as s
from .support import mk

from dossier import s1_extract
from dossier.lib import jsonio

H = [("P-001", "60%"), ("P-002", "40%")]
DEED = mk.deed("E-0001", 1, "2024-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"), H, ["P-001"])
AFTER = [("P-001", "50%"), ("P-002", "30%"), ("P-003", "20%")]


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


def _ledger(n, date, heading, rows):
    return mk._file("E-0001", f"{date}_holders-ledger.txt",
                    mk._head("E-0001", n, "Holders' ledger", date, f"LEDGER/{n}") + [heading, *mk._holders(rows)])


def _run(docs):
    work = s.tmp()
    code, _, report = s.run(s.tiny(docs, "2026-06-30"), work)
    view = jsonio.load(work / "views" / "E-0001.json")
    return report["entities"]["E-0001"]["status"], view, work


class A_RewordedHeadingsAreRead(unittest.TestCase):
    """Class A: the holders' heading in another wording."""

    def assertPublished(self, docs, table=None):
        status, view, work = _run(docs)
        self.assertEqual(status, "OK", view["ownership"])
        self.assertTrue((work / "dossiers" / "E-0001").exists())
        if table is not None:
            fld = view["fields"]["shareholders"]
            self.assertEqual(fld["status"], "STATED", fld)
            self.assertEqual({r["holder"]: r["share"] for r in fld["value"]}, table)

    def test_members_numbered_clause_of_a_deed(self):
        self.assertPublished([_reword(DEED, "4. Holders.", "4. Members.")], {"P-001": "3/5", "P-002": "2/5"})

    def test_shareholders_heading(self):
        self.assertPublished([_reword(DEED, "4. Holders.", "4. Shareholders:")], {"P-001": "3/5", "P-002": "2/5"})

    def test_members_heading_of_an_extract(self):
        ext = mk.extract("E-0001", 2, "2025-02-01", 1, mk.OFFICE_A,
                         "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00",
                         H, ["P-001"])
        self.assertPublished([DEED, _reword(ext, "Holders:", "Members:")])

    def test_members_at_the_document_date_of_a_ledger(self):
        self.assertPublished([DEED, _ledger(2, "2025-02-01", "Members at the document date:", H)])

    def test_after_the_transfer_the_members_are(self):
        tr = _reword(mk.transfer("E-0001", 2, "2025-05-05", AFTER), "Holders after the transfer:",
                     "After the transfer the members are:")
        self.assertPublished([DEED, tr], {"P-001": "1/2", "P-002": "3/10", "P-003": "1/5"})

    def test_a_reworded_table_that_does_not_sum_is_blocked_by_its_sum(self):
        doc = _reword(_reword(DEED, "4. Holders.", "4. Members."), "- P-002 (Bice Provetti): 40%",
                      "- P-002 (Bice Provetti): 30%")
        status, view, _ = _run([doc])
        self.assertEqual(status, "BLOCKED")
        self.assertEqual(view["ownership"]["rule"], "OWN-010", view["ownership"])


class A_HeadingsThatStayUnread(unittest.TestCase):
    """Class A, limits: a heading that does not say the table is current, or two headings, still block."""

    def assertBlocked(self, docs):
        status, view, work = _run(docs)
        self.assertEqual(status, "BLOCKED", view["ownership"])
        self.assertEqual(view["ownership"]["rule"], "OWN-015", view["ownership"])
        self.assertFalse((work / "dossiers" / "E-0001").exists())

    def test_holders_before_the_transfer_is_not_the_current_table(self):
        self.assertBlocked([DEED, _reword(mk.transfer("E-0001", 2, "2025-05-05", AFTER),
                                          "Holders after the transfer:", "Holders before the transfer:")])

    def test_members_of_the_board_is_not_a_holders_heading(self):
        self.assertBlocked([_reword(DEED, "4. Holders.", "Members of the board:")])

    def test_owners_is_not_a_holders_heading(self):
        self.assertBlocked([_reword(DEED, "4. Holders.", "Owners:")])

    def test_two_holders_tables_in_one_document_abstain(self):
        second = "\n\nMembers:\n- P-003 (Carlo Inventati): 100%"
        rel, text = DEED
        self.assertBlocked([(rel, text.rstrip("\n") + second + "\n")])


class B_UnclassifiedDocumentsAreChecked(unittest.TestCase):
    """Class B: a document whose type is not recognised no longer blocks when its body has no table, or when
    every table in it is read whole and sums to the whole."""

    def assertPublished(self, docs, to_confirm=()):
        status, view, work = _run(docs)
        self.assertEqual(status, "OK", view["ownership"])
        self.assertTrue((work / "dossiers" / "E-0001").exists())
        for fld in to_confirm:
            self.assertEqual(view["fields"][fld]["status"], "TO_CONFIRM", fld)
        return view

    def test_minutes_of_a_change_of_seat(self):
        doc = _retype(mk.office_transfer("E-0001", 2, "2025-05-05", "The registered office is transferred from "
                                         f"{mk.OFFICE_A} to {mk.OFFICE_B}."), "Minutes - change of seat")
        self.assertPublished([DEED, doc], to_confirm=["registered_office"])

    def test_minutes_of_a_change_of_the_board(self):
        doc = _retype(mk.appointment("E-0001", 2, "2025-05-05", ["P-002"], "P-002"), "Minutes - change of the board")
        self.assertPublished([DEED, doc], to_confirm=["directors"])

    def test_summary_of_the_annual_accounts(self):
        doc = _retype(mk.fin("E-0001", 2, "2025-05-05", "2024", "80.000,00", "1.000.000,00", "750.000,00"),
                      "Summary of the annual accounts")
        self.assertPublished([DEED, doc])

    def test_notice_of_assignment_with_a_table_that_sums(self):
        doc = _retype(mk.transfer("E-0001", 2, "2025-05-05", AFTER), "Notice of assignment of shares")
        view = self.assertPublished([DEED, doc], to_confirm=["shareholders"])
        checks = {c["source_doc"]: c for c in view["ownership"]["sum_checks"]}
        self.assertEqual(checks["DOC-E0001-02"]["sum"], "1/1")
        self.assertEqual(checks["DOC-E0001-02"]["source_date"], "2025-05-05")

    def test_register_of_members_with_a_reworded_heading(self):
        doc = _retype(_ledger(2, "2025-02-01", "Members at the document date:", H), "Register of members")
        self.assertPublished([DEED, doc], to_confirm=["shareholders"])


class B_UnclassifiedDocumentsThatStillBlock(unittest.TestCase):
    """Class B, limits: what cannot be read and verified still blocks (D26)."""

    def assertBlocked(self, docs, rule="OWN-015"):
        status, view, work = _run(docs)
        self.assertEqual(status, "BLOCKED", view["ownership"])
        self.assertEqual(view["ownership"]["rule"], rule, view["ownership"])
        self.assertFalse((work / "dossiers" / "E-0001").exists())

    def test_a_table_that_does_not_sum(self):
        doc = _retype(mk.transfer("E-0001", 2, "2025-05-05", [("P-001", "50%"), ("P-003", "20%")]),
                      "Notice of assignment of shares")
        self.assertBlocked([DEED, doc], rule="OWN-010")

    def test_a_sentence_that_states_a_holding(self):
        doc = _retype(mk.resolution("E-0001", 2, "2025-05-05", "The new shares were taken up by P-003 (Carlo "
                                    "Inventati), who now holds 20% of the capital."), "Minutes - capital increase")
        self.assertBlocked([DEED, doc])

    def test_a_table_with_a_line_in_another_form(self):
        doc = _retype(_reword(mk.transfer("E-0001", 2, "2025-05-05", AFTER), "- P-003 (Carlo Inventati): 20%",
                              "- Carlo Inventati (P-003): 20%"), "Notice of assignment of shares")
        self.assertBlocked([DEED, doc])

    def test_a_table_under_a_heading_in_another_form(self):
        doc = _retype(_reword(mk.transfer("E-0001", 2, "2025-05-05", AFTER), "Holders after the transfer:",
                              "Allocation of the capital:"), "Notice of assignment of shares")
        self.assertBlocked([DEED, doc])

    def test_shares_counted_not_fractioned(self):
        doc = _retype(mk.resolution("E-0001", 2, "2025-05-05", "Aldo Finti: 600 shares; Bice Provetti: 400 shares."),
                      "Minutes - capital increase")
        self.assertBlocked([DEED, doc])

    def test_a_header_that_cannot_be_read(self):
        doc = _retype(_reword(mk.office_transfer("E-0001", 2, "2025-05-05", f"The registered office is at {mk.OFFICE_B}."),
                              "Document date: 2025-05-05", "Document date: fifth of May 2025"), "Minutes - change of seat")
        self.assertBlocked([DEED, doc])

    def test_two_tables(self):
        rel, text = _retype(mk.transfer("E-0001", 2, "2025-05-05", AFTER), "Notice of assignment of shares")
        self.assertBlocked([DEED, (rel, text.rstrip("\n") + "\n\nMembers:\n- P-001 (Aldo Finti): 100%\n")])


class HoldersCheckUnit(unittest.TestCase):
    """The status of the check, document by document (the rules decide; see rules/extract.json)."""

    def _check(self, doc):
        rel, text = doc
        return s1_extract.holders_check(s1_extract.parse_document(text, rel, s.rules()), s.rules())

    def test_statuses(self):
        seat = _retype(mk.office_transfer("E-0001", 2, "2025-05-05", "The seat is moved."), "Minutes - change of seat")
        self.assertEqual(self._check(seat)["status"], "no_table")
        notice = _retype(mk.transfer("E-0001", 2, "2025-05-05", AFTER), "Notice of assignment of shares")
        got = self._check(notice)
        self.assertEqual(got["status"], "read")
        self.assertEqual(got["edition"], "TRANSFER/1")
        self.assertEqual([r["share"] for r in got["tables"][0]["value"]], ["1/2", "3/10", "1/5"])
        said = _retype(mk.resolution("E-0001", 2, "2025-05-05", "P-001 (Aldo Finti) now owns the whole capital."),
                       "Minutes - capital increase")
        self.assertEqual(self._check(said)["status"], "not_read")

    def test_the_meeting_of_the_holders_is_not_a_holding(self):
        for line in ("Minutes of the holders' meeting (synthetic).", "Minutes of the shareholders’ general meeting.",
                     "Minutes of the meeting of the members."):
            with self.subTest(line=line):
                self.assertEqual(s1_extract.holders_evidence(line, s.rules())["outcome"], "none")

    def test_evidence_rules_err_on_the_side_of_evidence(self):
        for line in ("Carlo Inventati - 20 per cent", "E-0002 (Holding Aurelia Partecipazioni S.r.l.)",
                     "The shareholders are the founders.", "Aldo Finti owns the company.", "Aldo Finti: 600 shares",
                     "P-001 600", "- Aldo Finti 3", "Aldo Finti | 3", "Aldo Finti 600", "Bice Provetti: a half"):
            with self.subTest(line=line):
                self.assertEqual(s1_extract.holders_evidence(line, s.rules())["outcome"], "evidence")


if __name__ == "__main__":
    unittest.main()
