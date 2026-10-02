"""D30b (v2.0.4): what the blind run of v2.0.3 found (eval/history.json, run 11; hand documents in
eval/blind/hand-11/), by class (R6).

S  DISC-005 scope (2 never-events on hand entity E-0015). v2.0.3 let a document of unrecognised type change only the
   fields its words name (unread_document_scope fields_it_may_state). A sentence that changes a field without naming
   it - a capital raised by a contribution in kind, a merger, a transfer worded without the word "holder", a capital
   change worded without the word "capital" - kept only the named fields, and a title noun of FEV-920 ("Notice",
   "Memorandum", "Letter"...) could narrow a whole document. Since v2.0.4 the default is every_field again. The
   adversarial siblings below are E-0009 / E-0010 / E-0015 in other words, each tried with every title noun of
   FEV-920, with the hand's own title, and with no title line: every field must stay [TO CONFIRM] and no effective
   holding may be derived. The narrow scope stays available but OFF: no test shows it safe, one shows it is not.

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import re
import unittest

from . import support as s
from .support import mk

from dossier.lib import jsonio

H = [("P-001", "60%"), ("P-002", "40%")]
CAPITAL = mk.FULL.format(a="50.000,00")
DEED = mk.deed("E-0001", 1, "2024-03-10", mk.OFFICE_A, CAPITAL, H, ["P-001"])
EXTRACT_CAPITAL = "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00"
EXTRACT = mk.extract("E-0001", 2, "2025-02-01", 1, mk.OFFICE_A, EXTRACT_CAPITAL, H, ["P-001"])
EVERY_FIELD = ("name", "legal_form", "registered_office", "share_capital.resolved", "share_capital.subscribed",
               "share_capital.paid_in", "directors", "shareholders")

# FEV-920's title nouns (rules/extract.json unread_fields); test_the_title_nouns_are_those_of_the_rule keeps the
# two lists equal, so a noun added to the rule is tried here too
FEV920_NOUNS = ("minutes", "notice", "entries", "entry", "register", "ledger", "statement", "certificate",
                "memorandum", "summary", "record", "report", "letter", "declaration")

# (class, the hand's own title, sentence, fields the sentence changes without naming all of them)
SIBLINGS = (
    ("E-0009 as written: an office sentence beside a capital doubled, the word capital absent", "Circular",
     f"To whom it may concern: the registered office remains at {mk.OFFICE_A}. On the fifteenth of July the two "
     "founders doubled what they had put into the company, all of it handed over on the same day, in equal parts as "
     "before.", ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")),
    ("E-0009 capital doubled, the word capital absent", "Circular",
     "On the fifteenth of July the two founders doubled what they had put into the company, all of it handed over "
     "on the same day, in equal parts as before.", ("share_capital.resolved", "share_capital.subscribed",
                                                   "share_capital.paid_in")),
    ("E-0010 transfer, the word holder absent", "Note for the file",
     "On the second of August Ms Bice Provetti (P-002) sold everything she had in the company to Mr Aldo Finti "
     "(P-001), who is since then the only one left in it.", ("shareholders",)),
    ("E-0015 contribution in kind and a new seat", "Notice to creditors",
     "The company informs its creditors that its equity has been raised to EUR 300.000,00 by a contribution in "
     f"kind, and that its seat moves to {mk.OFFICE_B} with effect from the first of September.",
     ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in", "shareholders",
      "registered_office")),
    ("contribution in kind, holders not named", "Notice",
     "A plant was contributed in kind by Mr Carlo Inventati (P-003) against new quotas.",
     ("share_capital.resolved", "share_capital.subscribed", "shareholders")),
    ("merger, the word merger present", "Notice",
     "Gamma S.r.l. has been merged into the company; its members received quotas of the company in exchange.",
     ("share_capital.resolved", "share_capital.subscribed", "shareholders")),
    ("merger, no topic word", "Letter",
     "Gamma S.r.l. has been folded into the company, and the people who owned Gamma now own part of it.",
     ("share_capital.resolved", "shareholders")),
    ("transfer worded as a gift", "Memorandum",
     "P-002 (Bice Provetti) gave her whole stake to P-001 (Aldo Finti) on the tenth of June.", ("shareholders",)),
    ("capital cut, the word capital absent", "Statement",
     "The amount the members committed to the company was cut by half on the tenth of June.",
     ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")),
    ("capital raised in figures, the word capital absent", "Report",
     "The members put in a further EUR 25.000,00 each, in the same proportions as before.",
     ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")),
)


def _sibling(title: str | None, sentence: str, label: str) -> tuple[str, str]:
    body = ([f"{title} (synthetic)."] if title else []) + [sentence]
    return mk._file("E-0001", "2026-08-20_doc-3.txt", mk._head("E-0001", 3, label, "2026-08-20", "DOC/1") + body)


def _titles(own: str):
    yield None, own                                     # no title line; type label = the hand's own
    yield own, own                                      # the hand's own title
    for noun in FEV920_NOUNS:                           # every title noun of FEV-920, as title and as type label
        yield noun.capitalize(), noun.capitalize()


def _run(docs, rules_dir=None):
    work = s.tmp()
    code, _, report = s.run(s.tiny(s.office_witness(docs), "2026-09-30"), work, rules_dir=rules_dir)
    status = report["entities"]["E-0001"]["status"]
    view = jsonio.load(work / "views" / "E-0001.json")
    prov_path = work / "dossiers" / "E-0001" / "provenance.json"
    prov = jsonio.load(prov_path) if prov_path.exists() else None
    return status, view, prov


class S_UnreadScopeAdversarialSiblings(unittest.TestCase):
    """Every sibling x every title: published with every field [TO CONFIRM], or blocked; never a fact."""

    def test_the_title_nouns_are_those_of_the_rule(self):
        rule = next(r for r in s.rules().extract["unread_fields"]["rules"] if r["id"] == "FEV-920")
        self.assertIn("{title_nouns}", rule["pattern"])         # since v2.0.5 a parameter shared with CLS-900
        nouns = re.search(r"\(\?:((?:[a-z]+\|)+[a-z]+)\)",
                          s.rules().extract["parameters"]["title_nouns"]).group(1).split("|")
        self.assertEqual(tuple(nouns), FEV920_NOUNS)

    def test_default_scope_is_every_field(self):
        self.assertEqual(s.rules().param("discrepancy", "unread_document_scope"), "every_field")

    def _assert_safe(self, status, view, prov, changes):
        self.assertIn(status, ("OK", "BLOCKED"))
        if status != "OK":
            self.assertIsNone(prov)
            return
        for f in EVERY_FIELD:
            self.assertEqual(view["fields"][f]["status"], "TO_CONFIRM", (f, view["fields"][f]))
            self.assertNotIn("value", view["fields"][f])
        for f in changes:
            self.assertEqual(view["fields"][f]["rule"], "DISC-005", f)
        self.assertEqual(prov["derived"], [])
        self.assertEqual([f for f in prov["figures"] if f["section"] in ("facts", "cap_table")], [])

    def test_every_sibling_with_every_title_keeps_every_field(self):
        n = 0
        for cls, own, sentence, changes in SIBLINGS:
            for title, label in _titles(own):
                with self.subTest(cls=cls, title=title):
                    n += 1
                    self._assert_safe(*_run([DEED, EXTRACT, _sibling(title, sentence, label)]), changes)
        self.assertEqual(n, len(SIBLINGS) * (2 + len(FEV920_NOUNS)))

    def test_a_sibling_with_a_holders_table_of_the_same_holders_keeps_the_holders(self):
        # a table that equals the current one does not prove that the sentence beside it changed nothing
        for cls, own, sentence, changes in SIBLINGS[:3]:
            with self.subTest(cls=cls):
                rel, text = _sibling("Notice", sentence, own)
                text += "Holders:\n" + "\n".join(mk._holders(H)) + "\n"
                self._assert_safe(*_run([DEED, EXTRACT, (rel, text)]), changes)

    def test_the_narrow_scope_is_not_safe_and_stays_off(self):
        # Evidence of the risk that keeps fields_it_may_state OFF (rules/discrepancy.json unread_document_scope):
        # with it on, the E-0010 sibling (a transfer worded without the word holder) under a FEV-920 title publishes
        # the holders it changes, as E-0015 did in run 11.
        status, view, prov = _run([DEED, EXTRACT, _sibling("Notice", SIBLINGS[2][2], "Notice to creditors")],
                                  rules_dir=s.rules_narrow_scope())
        self.assertEqual(status, "OK")
        self.assertEqual(view["fields"]["shareholders"]["status"], "STATED")
        self.assertNotEqual(prov["derived"], [])


def _reword(doc, old, new):
    rel, text = doc
    assert old in text, old
    return rel, text.replace(old, new)


def _deed(heading="4. Holders.", rows=None, directors_heading="5. Directors.", capital=CAPITAL):
    rel, text = mk.deed("E-0001", 1, "2024-03-10", mk.OFFICE_A, capital, H, ["P-001"])
    text = text.replace("4. Holders.\n", heading + "\n").replace("5. Directors.\n", directors_heading + "\n")
    if rows is not None:
        text = text.replace("- P-001 (Aldo Finti): 60%\n- P-002 (Bice Provetti): 40%\n", "".join(r + "\n" for r in rows))
    return rel, text


def _memo(line, label="Memorandum"):
    return mk._file("E-0001", "2026-07-03_doc-3.txt", mk._head("E-0001", 3, label, "2026-07-03", "MEMO/1")
                    + [f"{label} (synthetic).", line])


class _Built(unittest.TestCase):
    def assertPublished(self, docs, table=None, stated=(), to_confirm=()):
        status, view, prov = _run(docs)
        self.assertEqual(status, "OK", view["ownership"])
        self.assertIsNotNone(prov)
        if table is not None:
            fld = view["fields"]["shareholders"]
            self.assertEqual(fld["status"], "STATED", fld)
            self.assertEqual({r["holder"]: r["share"] for r in fld["value"]}, table)
        for f in stated:
            self.assertEqual(view["fields"][f]["status"], "STATED", (f, view["fields"][f]))
        for f in to_confirm:
            self.assertEqual(view["fields"][f]["status"], "TO_CONFIRM", (f, view["fields"][f]))
        return view

    def assertBlocked(self, docs, rule="OWN-015", why=None):
        status, view, prov = _run(docs)
        self.assertEqual(status, "BLOCKED", view["ownership"])
        self.assertEqual(view["ownership"]["rule"], rule, view["ownership"])
        if why:
            self.assertIn(why, view["ownership"]["reason"])
        self.assertIsNone(prov)


TABLE = {"P-001": "3/5", "P-002": "2/5"}
OTHERS = ("name", "legal_form", "registered_office", "share_capital.resolved", "share_capital.subscribed",
          "share_capital.paid_in", "directors")


class F1_HeadingWithoutTerminalPunctuation(_Built):
    """Class 1 of run 11 (7 of 15 hand deeds): the heading is read without '.' or ':' only when it is the whole line
    and the next line is an item of the list (rules/extract.json holders_heading_bare, directors_heading_bare)."""

    def test_bare_holders_headings(self):           # hand-11 E-0001, E-0002, E-0003, E-0005, E-0006, E-0011, E-0012
        for heading in ("4. Shareholders", "Article 4. Stockholders", "iv. Quotaholdings", "§ 4 Holders",
                        "4. Holders", "(4) Members", "Section 4 - Quotaholders"):
            with self.subTest(heading=heading):
                self.assertPublished([_deed(heading)], table=TABLE, stated=OTHERS)

    def test_bare_directors_headings(self):         # hand-11 E-0001, E-0003, E-0012; with E-0013's '(5) Directors:'
        for heading in ("5. Directors", "Article 5. Directors", "v. Directors", "§ 5 Directors", "(5) Directors:",
                        "§ 5 Directors:", "Article 5. Directors."):
            with self.subTest(heading=heading):
                self.assertPublished([_deed(directors_heading=heading)], table=TABLE, stated=OTHERS)

    def test_a_bare_heading_not_followed_by_an_item_is_not_a_heading(self):
        rel, text = _deed("4. Holders")
        self.assertBlocked([(rel, text.replace("4. Holders\n", "4. Holders\n\n"))])
        self.assertBlocked([_deed("4. Holders", rows=["as listed in the annex"])])

    def test_two_holders_headings_abstain(self):
        rel, text = _deed("4. Holders")
        text = text.replace("\n5. Directors.", "4.1 Holders\n- P-001 (Aldo Finti): 50%\n- P-002 (Bice Provetti): 50%"
                                               "\n\n5. Directors.")
        self.assertBlocked([(rel, text)])

    def test_two_directors_headings_abstain(self):
        rel, text = _deed()
        text = text.rstrip("\n") + "\n\n6. Directors\n- P-002 (Bice Provetti)\n"
        self.assertPublished([(rel, text)], table=TABLE, to_confirm=["directors"])


class F2_DateOrdinalIsNotAShare(_Built):
    """Class 2 (hand-11 E-0008): a day ordinal in words with a month name, and 'third parties', are not a share in
    words (rules/extract.json holders_evidence neutral_phrases). The document is still of unrecognised type: every
    field is [TO CONFIRM] (DISC-005 every_field), but the entity is no longer blocked for nothing (OWN-015)."""

    def test_dates_in_words(self):
        for line in ("For the file: Mr Aldo Finti stepped back on the third of July; from that day Ms Bice Provetti "
                     "alone signs for the company and answers for it towards third parties.",
                     "Signed on July the fifth.", "Signed on the twenty-first day of March.",
                     "Signed on March 3rd by the director."):
            with self.subTest(line=line):
                self.assertPublished([DEED, EXTRACT, _memo(line)], to_confirm=EVERY_FIELD)

    def test_a_share_in_words_beside_a_date_still_blocks(self):
        for line in ("On the third of July Mr Carlo Inventati received a third of the company.",
                     "In May a third of it went to Mr Carlo Inventati.",
                     "Two thirds of June's quotas went to P-003."):
            with self.subTest(line=line):
                self.assertBlocked([DEED, EXTRACT, _memo(line)])


class F3_DotLeadersAndTotal(_Built):
    """Class 4 (hand-11 E-0006): dot leaders as a separator; a last line 'Total' must equal the exact sum of the rows,
    and a Total that differs blocks by OWN-010 (dossier/s4_ownership.py table_check)."""

    ROWS = ["- P-001 (Aldo Finti) .......... 60%", "- P-002 (Bice Provetti) ........ 40%"]

    def test_dot_leaders_with_a_total_equal_to_the_sum(self):
        self.assertPublished([_deed("4. Holders", rows=self.ROWS + ["  Total .......................... 100%"])],
                             table=TABLE, stated=OTHERS)
        self.assertPublished([_deed(rows=self.ROWS)], table=TABLE, stated=OTHERS)

    def test_a_total_that_differs_blocks_by_own_010(self):
        for total in ("  Total .......... 90%", "Total: 110%", "Total | 9/10"):
            with self.subTest(total=total):
                self.assertBlocked([_deed(rows=self.ROWS + [total])], rule="OWN-010", why="Total line")

    def test_a_total_that_is_not_the_last_line_or_not_read_blocks(self):
        self.assertBlocked([_deed(rows=[self.ROWS[0], "Total: 100%", self.ROWS[1]])])
        self.assertBlocked([_deed(rows=self.ROWS + ["Total: all of it"])])
        self.assertBlocked([_deed(rows=self.ROWS + ["Total: 500 quotas"])])

    def test_counts_with_a_total(self):
        cap = "The share capital is EUR 50.000,00, divided into 500 quotas, fully subscribed and fully paid in."
        rows = ["- P-001 (Aldo Finti) ...... 300 quotas", "- P-002 (Bice Provetti) .... 200 quotas"]
        self.assertPublished([_deed(rows=rows + ["Total ...... 500 quotas"], capital=cap)], table=TABLE)
        self.assertBlocked([_deed(rows=rows + ["Total ...... 450 quotas"], capital=cap)], rule="OWN-010",
                           why="Total line")


class F4_ShareBeforeHolder(_Built):
    """Class 5 (hand-11 E-0012): a share with its per cent sign or word, or a fraction n/d, before the holder."""

    def test_share_first(self):
        for rows in (["- 60% P-001 (Aldo Finti)", "- 40% P-002 (Bice Provetti)"],
                     ["1. 3/5 - Aldo Finti (P-001)", "2. 2/5 - Bice Provetti (P-002)"],
                     ["(a) 60 per cent | P-001 (Aldo Finti)", "(b) 40 per cent | P-002 (Bice Provetti)"]):
            with self.subTest(rows=rows):
                self.assertPublished([_deed("§ 4 Holders", rows=rows)], table=TABLE, stated=OTHERS)

    def test_share_first_in_words_or_counts_still_blocks(self):
        self.assertBlocked([_deed(rows=["- three fifths P-001 (Aldo Finti)", "- two fifths P-002 (Bice Provetti)"])])
        self.assertBlocked([_deed(rows=["- 300 quotas P-001 (Aldo Finti)", "- 200 quotas P-002 (Bice Provetti)"])])

    def test_share_first_that_does_not_sum_blocks_by_own_010(self):
        self.assertBlocked([_deed(rows=["- 60% P-001 (Aldo Finti)", "- 30% P-002 (Bice Provetti)"])], rule="OWN-010")


class F5_StillNotRead(_Built):
    """Known limits of v2.0.4 found or re-examined on run 11 (CHANGELOG 2.0.4): each still blocks the entity."""

    def test_current_qualifier_in_free_words(self):          # hand-11 E-0002
        tr = mk.transfer("E-0001", 2, "2025-05-05", [("P-001", "50%"), ("P-002", "50%")])
        self.assertBlocked([DEED, _reword(tr, "Holders after the transfer:",
                                          "Shareholders once the transfer has taken effect:")])

    def test_header_row(self):                                # hand-11 E-0011
        self.assertBlocked([_deed("4. Holders", rows=["| Identifier | Holder | Share |", "| P-001 | Aldo Finti | 3/5 |",
                                                      "| P-002 | Bice Provetti | 2/5 |"])])

    def test_per_mille(self):                                 # hand-11 E-0014
        self.assertBlocked([_deed(rows=["- P-001 (Aldo Finti): 600‰", "- P-002 (Bice Provetti): 400‰"])])

    def test_holders_in_prose(self):                          # hand-9 E-0007: owner's risk decision, not read
        self.assertBlocked([_deed("4. Capital allocation. The share capital is held by P-001 (Aldo Finti) as to 60% "
                                  "and by P-002 (Bice Provetti) as to 40%.", rows=[])])


class G_HandCorpora(unittest.TestCase):
    """The hand corpora already seen, end to end through the scorer: 0 never-events (hand-11: 2 on v2.0.3)."""

    def _score(self, sub):
        from eval import score
        d = s.ROOT / "eval" / "blind" / sub
        return score.evaluate(sub, corpus=d / "input", gold_path=d / "gold.json", work=s.tmp())

    def test_hand_11(self):
        got = self._score("hand-11")
        self.assertEqual(got["metrics"]["never_events"], 0, got["never_event_list"])
        # v2.0.8: [TO CONFIRM] kept 12/12, blocked wrongly at most 3; v2.0.9 (D38) every entity of this corpus is
        # blocked: the persons of its holders' rows are not of the gazetteer (free_text_identification), the rows are
        # read by no rule and may state a holding (OWN-015); the price of CHANGELOG 2.0.9 section 3
        self.assertEqual(got["metrics"]["to_confirm_kept"], "0/0")
        self.assertEqual((got["counts"]["published"], got["counts"]["blocked_wrongly"]), (0, 13))

    def test_hand_9_and_hand(self):
        for sub in ("hand-9", "hand"):
            with self.subTest(sub=sub):
                got = self._score(sub)
                self.assertEqual(got["metrics"]["never_events"], 0, got["never_event_list"])


class H_ScorerCountsWhatIsNotPublished(unittest.TestCase):
    """Goal 3 (eval/score.py): gold [TO CONFIRM] values and file-name divergences of entities that were not published
    are counted beside the other counts; the never-event definition and counts do not change."""

    def test_unpublished_entities_are_counted_not_scored(self):
        from eval import score
        base, work, _ = s.built(24)
        gold = jsonio.load(base / "gold.json")
        before = score.score(work, gold)
        eid = next(e for e, g in sorted(gold["entities"].items())
                   if g["build"] == "OK" and (work / "dossiers" / e / "provenance.json").exists())
        # the same build with one published entity blocked, and its gold given two [TO CONFIRM] fields and a
        # file-name divergence
        copy = s.tmp()
        report = jsonio.load(work / "run_report.json")
        report["entities"][eid]["status"] = "BLOCKED"
        jsonio.write(copy / "run_report.json", report)
        for p in (work / "dossiers").rglob("provenance.json"):
            if p.parent.name != eid:
                jsonio.write_bytes(copy / p.relative_to(work), p.read_bytes())
        g = gold["entities"][eid]
        for f in ("name", "legal_form"):
            g["fields"][f] = {"status": "TO_CONFIRM", "superseded": []}
        g["filename_divergences"] = g.get("filename_divergences", []) + [
            {"doc_id": "DOC-X", "aspect": "date"}]
        n_tc = sum(1 for gf in g["fields"].values() if gf["status"] == "TO_CONFIRM")
        got = score.score(copy, gold)
        m, m0 = got["metrics"], before["metrics"]
        self.assertEqual(m["never_events"], m0["never_events"])
        self.assertEqual(got["never_event_list"], before["never_event_list"])
        self.assertEqual(got["counts"]["blocked_wrongly"], before["counts"]["blocked_wrongly"] + 1)
        self.assertEqual(m["blocked_wrongly_entities_gold_to_confirm"],
                         m0["blocked_wrongly_entities_gold_to_confirm"] + n_tc)
        self.assertEqual(m["blocked_wrongly_entities_filename_divergences_gold"],
                         m0["blocked_wrongly_entities_filename_divergences_gold"] + len(g["filename_divergences"]))
        self.assertGreaterEqual(m["blocked_entities_gold_to_confirm"], m["blocked_wrongly_entities_gold_to_confirm"])
        # the entities the gold blocks are counted too, and not as blocked wrongly
        gb = sum(1 for e, x in gold["entities"].items() if x["build"] == "BLOCKED"
                 and not (copy / "dossiers" / e / "provenance.json").exists()
                 for f in x["fields"].values() if f["status"] == "TO_CONFIRM")
        self.assertEqual(m["blocked_entities_gold_to_confirm"] - m["blocked_wrongly_entities_gold_to_confirm"], gb)


if __name__ == "__main__":
    unittest.main()
