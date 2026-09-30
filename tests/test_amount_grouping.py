"""Finding T16 (blind run of 2026-09-30, eval/history.json run 5): regression tests from the evaluator's documents.

1. ``EUR 150'000.00`` was read as ``150.00``: the amount token stopped at the apostrophe, the rest of the figure
   was dropped, and the independent audit - cutting the quote the same way - confirmed the wrong value.
2. Seven out-of-pool dossiers and one perturbed dossier whose holders' table does not sum to the whole were
   published, because that table could not be read (``per cent``, name before the identifier, ``Shareholders:``,
   a date in words, a document type not recognised).

The documents below are copied from the evaluator's synthetic corpora (fictitious entities, invented registry).
"""
import unittest

from . import support as s
from .support import mk

from dossier import s1_extract, s7_audit
from dossier.lib import jsonio
from dossier.lib.numbers import parse_amount

MARKER = "SYNTHETIC TEST DOCUMENT - fictitious entity, invented test registry, not an official record."
H = [("P-001", "60%"), ("P-002", "40%")]


def _doc(doc_id, doc_type, date, edition, entity, body):
    return "\n".join([MARKER, f"Document id: {doc_id}", f"Document type: {doc_type}", f"Document date: {date}",
                      f"Edition: {edition}", f"Entity: {entity}", "", *body]) + "\n"


# out-of-pool, clause of DOC-E0114-04 (rewrite B3: apostrophe grouping)
E0114 = ("The meeting resolved to increase the share capital from EUR 200'000.00 to EUR 280'000.00; after the "
         "increase the subscribed capital is EUR 260'000.00 and the paid-in capital is EUR 220'000.00.")
# out-of-pool, clauses of DOC-E0065-08 and DOC-E0112-03
E0065 = ("The meeting resolved to increase the share capital from EUR 100'000.00 to EUR 150'000.00. "
         "The whole increase has been subscribed and paid in.")
E0112 = ("The meeting resolved that the share capital go up from EUR 200'000.00 to EUR 220'000.00. "
         "The whole increase has been subscribed and paid in.")

# holders' tables that do not sum to the whole and that v2.0.0 could not read (gold: BLOCKED)
UNREAD_TABLES = {
    "E-0061 per cent": ("entities/E-0061/2020-02-02_deed.txt", _doc(
        "DOC-E0061-01", "Deed of incorporation", "2020-02-02", "DEED/1",
        "Fornaci Pontecollaudo S.p.A. (test registry no. TEST-REG-000061)", [
            "1. Name and form. The company is named Fornaci Pontecollaudo S.p.A.; its legal form is S.p.A.",
            "2. Registered office. The registered office is at Largo Simulato 6, Selvaprototipo (ZZ).",
            "3. Share capital. The share capital is EUR 100.000,00, fully subscribed and fully paid in.",
            "4. Holders.", "- E-0060 (Holding Rivaprova Partecipazioni S.p.A.): 69,99%",
            "- P-053 (Dora Sintetici): 30 per cent", "", "5. Directors.", "- P-053 (Dora Sintetici)",
            "- P-054 (Ida Fasulli)"])),
    "E-0001 name first": ("entities/E-0001/2021-06-25_deed.txt", _doc(
        "DOC-E0001-01", "Deed of incorporation", "2021-06-25", "DEED/1",
        "Holding Villasimulata Partecipazioni S.r.l. (test registry no. TEST-REG-000001)", [
            "1. Name and form. The company is named Holding Villasimulata Partecipazioni S.r.l.; it takes the "
            "legal form of S.r.l.",
            "2. Registered office. The registered office is at Via del Collaudo 70, Lagosintetico (ZZ).",
            "3. Share capital. The share capital is 10.000,00 EUR, fully subscribed and fully paid in.",
            "4. Holders.", "- Livio Esempi (P-002): 59,99%", "- Dino Sintetici (P-001): 40%", "",
            "5. Directors.", "- Dino Sintetici (P-001)", "- Livio Esempi (P-002)"])),
    "E-0035 Shareholders heading": ("entities/E-0035/2023-09-30_registry-extract.txt", _doc(
        "DOC-E0035-05", "Test registry extract", "2023-09-30", "EXTRACT/1",
        "Fornaci Montefinto S.r.l. (test registry no. TEST-REG-000035)", [
            "Name: Fornaci Montefinto S.r.l.", "Legal form: S.r.l.",
            "Registered office: Via dei Prototipi 76, Monteprototipo (ZZ)",
            "Share capital: resolved EUR 20'000.00; subscribed EUR 20'000.00; paid in EUR 20'000.00",
            "Shareholders:", "- E-0034 (Holding Selvaprototipo Partecipazioni S.r.l.): 25,01%",
            "- P-034 (Elio Fantasmi): 25%", "- P-031 (Franca Campioni): 25%", "- P-032 (Aldo Fittizi): 25%", "",
            "Directors:", "- P-033 (Mara Modelli)", "- P-032 (Aldo Fittizi)", "- P-034 (Elio Fantasmi)"])),
    "E-0115 date in words": ("entities/E-0115/2023-10-08_registry-extract.txt", _doc(
        "DOC-E0115-04", "Test registry extract", "8 October 2023", "EXTRACT/1",
        "Fonderie Rivaprova S.r.l. (test registry no. TEST-REG-000115)", [
            "Name: Fonderie Rivaprova S.r.l.", "Legal form: S.r.l.",
            "Registered office: Piazza Inventata 73, Montefinto (ZZ)",
            "Share capital: resolved EUR 120.000,00; subscribed EUR 120.000,00; paid in EUR 120.000,00",
            "Holders:", "- E-0112 (Cantieri Campomodello S.r.l.): 33,33%",
            "- E-0114 (Fonderie Valfittizia S.r.l.): 33,33%", "- P-101 (Bice Sintetici): 33,33%", "",
            "Directors:", "- P-101 (Bice Sintetici)"])),
    "E-0123 type not recognised (perturbed)": ("entities/E-0123/2019-10-15_deed.txt", _doc(
        "DOC-E0123-01", "Articles of incorporation", "2019-10-15", "DEED/1",
        "Tipografie Valfittizia S.r.l. (test registry no. TEST-REG-000123)", [
            "1. Name and form. The company is named Tipografie Valfittizia S.r.l.; its legal form is S.r.l.",
            "2. Registered office. The registered office is at Viale degli Esempi 75, Portoinventato (ZZ).",
            "3. Share capital. The share capital is € 500.000, fully subscribed and fully paid in.",
            "4. Holders.", "- E-0122 (Saline Portoinventato S.r.l.): 69,99%", "- P-105 (Piero Provetti): 30%", "",
            "5. Directors.", "- P-105 (Piero Provetti)", "- P-106 (Carlo Inventati)"])),
}


def _capital(kind, clause):
    rules = s.rules()
    rule = next(r for r in rules.extract["field_rules"] if r["id"] == "EXT-CAP-010")
    got = s1_extract._extract_capital(s1_extract._test_doc(kind, clause, rules), rule, rules) or []
    return {a["field"].rsplit(".", 1)[-1]: a.get("value") for a in got}


class ApostropheGrouping(unittest.TestCase):
    def test_parse_amount_groupings(self):
        for token, canon in (("150'000.00", "150000.00"), ("150’000.00", "150000.00"),
                             ("150'000,00", "150000.00"), ("1'234'567.89", "1234567.89"), ("150'000", "150000.00"),
                             ("150 000.00", "150000.00"), ("150\u00a0000,00", "150000.00"),
                             ("150\u202f000,00", "150000.00"), ("150\u2009000,00", "150000.00"),
                             ("1.500.000,00", "1500000.00"), ("1,500,000.00", "1500000.00")):
            self.assertEqual(parse_amount(token), (canon, None), token)

    def test_look_alike_or_mixed_grouping_is_not_guessed(self):
        for token in ("150‘000,00", "150ʼ000", "150′000", "150´000", "150`000", "150·000,00",
                      "150\u200a000,00", "1'500.000,00", "1 500\u00a0000,00", "15'00.00", "150'000.000"):
            value, reason = parse_amount(token)
            self.assertIsNone(value, token)
            self.assertTrue(reason, token)

    def test_the_token_is_never_cut_at_a_separator(self):
        spans = s1_extract.amount_spans(E0065, s.rules())
        self.assertEqual([t for _, _, t in spans], ["100'000.00", "150'000.00"])

    def test_evaluator_clauses(self):
        self.assertEqual(_capital("RESOLUTION", E0114),
                         {"previous": "200000.00", "resolved": "280000.00", "subscribed": "260000.00",
                          "paid_in": "220000.00"})
        self.assertEqual(_capital("RESOLUTION", E0065)["resolved"], "150000.00")
        self.assertEqual(_capital("RESOLUTION", E0065)["previous"], "100000.00")
        self.assertEqual(_capital("RESOLUTION", E0112)["resolved"], "220000.00")

    def test_uncertain_readings_abstain(self):
        for clause in ("The share capital is EUR 150 thousand, fully subscribed and fully paid in.",
                       "The share capital is Mio. EUR 1, fully subscribed and fully paid in.",
                       "The share capital is EUR 150  000,00, fully subscribed and fully paid in.",
                       "The share capital is EUR 150·000,00, fully subscribed and fully paid in.",
                       "The share capital is EUR 150k, fully subscribed and fully paid in.",
                       "Amounts in thousands of EUR.\nThe share capital is EUR 150,00, fully subscribed and fully paid in."):
            got = _capital("DEED", clause)
            self.assertEqual({k: v for k, v in got.items() if k != "previous"},
                             {"resolved": None, "subscribed": None, "paid_in": None}, clause)
        self.assertEqual(s1_extract.amount_spans("The share capital is TEUR 150.", s.rules()), [])

    def test_end_to_end_the_dossier_shows_the_whole_figure(self):
        deed = mk.deed("E-0001", 1, "2024-03-10", mk.OFFICE_A, mk.FULL.format(a="200.000,00"), H, ["P-001"])
        work = s.tmp()
        code, _, _ = s.run(s.tiny([deed, mk.resolution("E-0001", 2, "2025-10-09", E0114)], "2026-06-30"), work)
        self.assertEqual(code, 0)
        fields = jsonio.load(work / "views" / "E-0001.json")["fields"]
        got = {k: fields[f"share_capital.{k}"].get("value") for k in ("resolved", "subscribed", "paid_in")}
        self.assertEqual(got, {"resolved": "280000.00", "subscribed": "260000.00", "paid_in": "220000.00"})
        prov = jsonio.load(work / "dossiers" / "E-0001" / "provenance.json")
        shown = {f["display"] for f in prov["figures"] if f["field"].startswith("share_capital.")}
        self.assertTrue({"EUR 280.000,00", "EUR 260.000,00", "EUR 220.000,00"} <= shown, shown)
        self.assertFalse({"EUR 280,00", "EUR 260,00", "EUR 220,00"} & shown, shown)


class TheAuditReadsTheWholeFigure(unittest.TestCase):
    def _fig(self, value):
        return {"section": "facts", "field": "share_capital.resolved", "value": value, "quote": E0065}

    def test_a_figure_cut_short_is_not_supported_by_its_quote(self):
        self.assertFalse(s7_audit.supported_by_quote(self._fig("150.00")))
        self.assertFalse(s7_audit.supported_by_quote(self._fig("100.00")))
        self.assertTrue(s7_audit.supported_by_quote(self._fig("150000.00")))

    def test_the_outgoing_scanner_reads_the_whole_figure(self):
        got = [v for _, v in s7_audit._amounts_in("capital of EUR 150'000.00 as resolved", "(?:EUR|€|euro)")]
        self.assertEqual(got, ["150000.00"])


class AnUnreadTableThatMayNotSumIsBlocked(unittest.TestCase):
    def test_each_evaluator_document(self):
        for label, (rel, text) in UNREAD_TABLES.items():
            with self.subTest(case=label):
                eid = rel.split("/")[1]
                work = s.tmp()
                code, _, report = s.run(s.tiny([(rel, text)], "2026-06-30"), work)
                self.assertEqual(report["entities"][eid]["status"], "BLOCKED", report["entities"][eid])
                self.assertEqual(code, 2)
                self.assertFalse((work / "dossiers" / eid).exists())


if __name__ == "__main__":
    unittest.main()
