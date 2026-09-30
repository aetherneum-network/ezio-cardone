"""Reading the source documents: the content decides, the file name never does, the unreadable is not guessed."""
import unittest

from . import support as s
from .support import mk

from dossier import s1_extract
from dossier.lib import jsonio

H = [("P-001", "60%"), ("P-002", "40%")]


def _deed(capital=None, office=mk.OFFICE_A, holders=H):
    return mk.deed("E-0001", 1, "2025-03-10", office, capital or mk.FULL.format(a="50.000,00"), holders, ["P-001"])


def _run(docs, as_of="2026-06-30", crlf=False, **kw):
    inp = s.tiny(docs, as_of)
    if crlf:
        for p in (inp / "entities").rglob("*.txt"):
            p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    work = s.tmp()
    code, out, report = s.run(inp, work, **kw)
    record = jsonio.load(work / "records" / "E-0001.json") if (work / "records" / "E-0001.json").exists() else None
    view = jsonio.load(work / "views" / "E-0001.json") if (work / "views" / "E-0001.json").exists() else None
    return code, report, record, view, work


def _status(view):
    return {k: (r["status"], r.get("value")) for k, r in view["fields"].items()}


class ContentDecides(unittest.TestCase):
    def test_plain_deed(self):
        code, _, record, view, _ = _run([_deed()])
        got = _status(view)
        self.assertEqual(code, 0)
        self.assertEqual(got["name"], ("STATED", "Fornace Aurelia S.r.l."))
        self.assertEqual(got["registered_office"], ("STATED", mk.OFFICE_A))
        for nature in ("resolved", "subscribed", "paid_in"):
            self.assertEqual(got[f"share_capital.{nature}"], ("STATED", "50000.00"))
        self.assertEqual(view["fields"]["shareholders"]["value"],
                         [{"holder": "P-001", "share": "3/5"}, {"holder": "P-002", "share": "2/5"}])
        self.assertEqual(record["entity"], {"id": "E-0001", "registry_no": "TEST-REG-000001"})

    def test_windows_line_endings_change_nothing(self):
        _, _, _, lf, _ = _run([_deed()])
        _, _, _, crlf, _ = _run([_deed()], crlf=True)
        self.assertEqual(_status(lf), _status(crlf))

    def test_file_name_is_never_a_source(self):
        rel, text = _deed()
        cases = {"kind": (rel.replace("_deed", "_registry-extract"), "EXTRACT", "DEED"),
                 "date": (rel.replace("2025-03-10", "2026-01-01"), "2026-01-01", "2025-03-10"),
                 "folder": (rel.replace("E-0001", "E-0004"), "E-0004", "E-0001")}
        _, _, _, plain, _ = _run([(rel, text)])
        for aspect, (name, says, content) in cases.items():
            with self.subTest(aspect=aspect):
                code, report, record, view, _ = _run([(name, text)])
                self.assertEqual(list(report["entities"]), ["E-0001"])
                self.assertEqual(_status(view), _status(plain))
                div = record["filename_divergences"]
                self.assertEqual([(d["aspect"], d["filename_says"], d["content_says"]) for d in div],
                                 [(aspect, says, content)])
                src = view["fields"]["name"]["sources"][0]
                self.assertEqual((src["source_date"], src["edition"]), ("2025-03-10", "DEED/1"))

    def test_document_after_as_of_is_not_read(self):
        res = mk.resolution("E-0001", 2, "2026-08-15",
                            "The meeting resolved to increase the share capital from EUR 50.000,00 to "
                            "EUR 80.000,00. The increase has been fully subscribed and fully paid in.")
        _, _, record, view, _ = _run([_deed(), res], as_of="2026-06-30")
        self.assertEqual(_status(view)["share_capital.resolved"], ("STATED", "50000.00"))
        self.assertEqual(record["ignored_after_as_of"], ["DOC-E0001-02"])
        _, _, _, later, _ = _run([_deed(), res], as_of="2026-08-15")
        self.assertEqual(_status(later)["share_capital.resolved"], ("STATED", "80000.00"))
        self.assertEqual([h["value"] for h in later["fields"]["share_capital.resolved"]["historical"]], ["50000.00"])


class NotGuessed(unittest.TestCase):
    def test_ambiguous_separator(self):
        _, _, _, view, _ = _run([_deed("The share capital is EUR 50.000, fully subscribed and fully paid in.")])
        got = _status(view)
        for nature in ("resolved", "subscribed", "paid_in"):
            self.assertEqual(got[f"share_capital.{nature}"], ("TO_CONFIRM", None))
        self.assertEqual(got["name"][0], "STATED")

    def test_illegible_share(self):
        # v2.0.1: a holders' table that cannot be summed blocks the build (OWN-015, unverified_holders_table 'block')
        code, report, _, view, work = _run([_deed(holders=[("P-001", "6#%"), ("P-002", "40%")])])
        self.assertEqual(_status(view)["shareholders"], ("TO_CONFIRM", None))
        self.assertEqual((view["ownership"]["outcome"], view["ownership"]["rule"]), ("BLOCKED", "OWN-015"))
        self.assertIsNone(view["ownership"]["effective"])
        self.assertEqual((code, report["entities"]["E-0001"]["status"]), (2, "BLOCKED"))
        self.assertFalse((work / "dossiers" / "E-0001").exists())
        # under 'report' (the v2.0.0 behaviour) the dossier is published with the holders [TO CONFIRM]
        _, _, _, view, _ = _run([_deed(holders=[("P-001", "6#%"), ("P-002", "40%")])],
                                rules_dir=s.rules_report_unverified())
        self.assertEqual(view["ownership"]["outcome"], "TO_CONFIRM")
        self.assertIsNone(view["ownership"]["effective"])

    def test_header_problems_leave_the_document_unread(self):
        rel, text = _deed()
        for label, bad in (("date", text.replace("Document date: 2025-03-10", "Document date: 2025-13-40")),
                           ("edition", text.replace("Edition: DEED/1\n", "")),
                           ("type", text.replace("Deed of incorporation", "Some paper"))):
            with self.subTest(problem=label):
                code, report, record, view, work = _run([(rel, bad)])
                self.assertEqual(len(record["unclassified_documents"]), 1)
                self.assertEqual(record["documents"], [])
                self.assertEqual(view["fields"], {})
                # v2.0.1: the unread deed may hold a table that does not sum: the build is blocked (OWN-015)
                self.assertEqual((code, view["ownership"]["rule"]), (2, "OWN-015"))
                self.assertFalse((work / "dossiers" / "E-0001").exists())
                code, report, record, view, work = _run([(rel, bad)], rules_dir=s.rules_report_unverified())
                prov = jsonio.load(work / "dossiers" / "E-0001" / "provenance.json")
                self.assertEqual(prov["figures"], [])

    def test_document_that_names_no_registered_entity_fails_the_run(self):
        rel, text = _deed()
        code, report, record, view, work = _run([(rel, text.replace(" (test registry no. TEST-REG-000001)", ""))])
        self.assertEqual((code, report["entities"]["E-0001"]["status"]), (3, "FAILED"))
        self.assertIsNone(record)
        self.assertFalse((work / "dossiers").exists())

    def test_not_utf8(self):
        inp = s.tiny([_deed()])
        path = next((inp / "entities").rglob("*.txt"))
        path.write_bytes(path.read_bytes().replace(b"Borgoprova", b"Borgopr\xf2va"))
        work = s.tmp()
        code, _, report = s.run(inp, work)
        self.assertEqual((code, report["entities"]["E-0001"]["status"]), (3, "FAILED"))
        self.assertIn("not UTF-8", report["entities"]["E-0001"]["reason"])

    def test_nature_of_a_figure_is_classified_before_it_is_counted(self):
        rules = s.rules()
        clause = "resolved EUR 500.000,00, subscribed EUR 400.000,00, paid in EUR 250.000,00"
        got = [(n["token"], n["natures"]) for n in s1_extract.classify_natures(clause, rules)]
        self.assertEqual(got, [("500.000,00", ["resolved"]), ("400.000,00", ["subscribed"]),
                               ("250.000,00", ["paid_in"])])
        both = s1_extract.classify_natures("resolved EUR 80.000,00; subscribed and paid in EUR 60.000,00", rules)
        self.assertEqual([(n["token"], n["natures"]) for n in both],
                         [("80.000,00", ["resolved"]), ("60.000,00", ["subscribed", "paid_in"])])
        vague = s1_extract.classify_natures("resolved EUR 500.000,00, of which EUR 400.000,00 and EUR 250.000,00",
                                            rules)
        self.assertEqual(vague[0]["natures"], ["resolved"])
        for n in vague[1:]:
            self.assertEqual(n["natures"], [], n)
        old = s1_extract.classify_natures("to increase the share capital from EUR 300.000,00 to EUR 500.000,00",
                                          rules)
        self.assertEqual([n["natures"] for n in old], [["historical"], ["resolved"]])


class KindsAreRules(unittest.TestCase):
    def test_every_known_type_label(self):
        rules = s.rules()
        for label, kind in (("Deed of incorporation", "DEED"), ("Test registry extract", "EXTRACT"),
                            ("Resolution on share capital", "RESOLUTION"), ("Share transfer notice", "TRANSFER"),
                            ("Appointment of directors", "APPOINTMENT"), ("Transfer of registered office", "OFFICE"),
                            ("Financial statements summary", "FIN")):
            self.assertEqual(s1_extract.classify_kind(label, rules)[0], kind, label)
        self.assertEqual(s1_extract.classify_kind("Letter to the holders", rules), ("UNKNOWN", "KIND-999"))


if __name__ == "__main__":
    unittest.main()
