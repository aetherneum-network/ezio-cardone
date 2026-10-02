"""D39 (c): four declarations of CHANGELOG 2.0.10 made true by tests (each a known limit with its class, or the
intended behaviour of a case that the 2.0.9 list described wrongly).

- D4, the holder row with the identifier in square brackets ("- Name [P-015]: 60%", E-0006 of hand-22): it is in
  neither the C2 grammar nor any rule; the row is not read, the holders' table cannot be summed and the entity
  BLOCKS (OWN-015). Declared, not read: reading it would need its own verification and sibling suite.
- E-0005 of hand-22, a blank line inside a list of holders: the blank line ends the list, the rows after it are not
  part of the table, the table sums to less than the whole and the entity BLOCKS.
- the numeral case of IDN-010 (E-0025, E-0028 of hand-22): a line that no rule of its kind reads and that holds a
  numeral BLOCKS when it may state a holding - by design, not a leftover.
- D3, an address that holds a known name inside a WHOLE gazetteer street entry (E-0033 of hand-22, 'Via del
  Segnaposto 5', the surname of P-007): the address is identified word by word and, when another document states it
  alike, it is read - the known name does not open the line. A known name that is not part of a gazetteer entry
  ('Via Gino Segnaposto 5') leaves the address unidentified and the office [TO CONFIRM]."""
import json
import re
import unittest

from . import ROOT
from . import support as s
from .support import mk

from dossier.lib import jsonio

E = "E-0001"
PCT = [("P-001", "60%"), ("P-002", "40%")]
HAND = ROOT / "eval" / "blind" / "hand-22"
_ROW = re.compile(r"^- (P-\d{3}) \(([^()]*)\): (.*)$", re.M)


def _bracket(text: str, form: str) -> str:
    return _ROW.sub({"name [id]": r"- \2 [\1]: \3", "id [name]": r"- \1 [\2]: \3",
                     "[id] name": r"- [\1] \2: \3"}[form], text)


def _status(docs) -> tuple[int, str, bool, dict]:
    inp = s.tiny(list(docs))
    work = s.tmp("ezio-d39-lim-")
    code, out, report = s.run(inp, work)
    published = (work / "dossiers" / E).exists()
    view = jsonio.load(work / "views" / f"{E}.json")["fields"] if (work / "views" / f"{E}.json").exists() else {}
    return code, report["entities"][E]["status"], published, view


class D39_DeclaredLimits(unittest.TestCase):
    def test_D4_holder_rows_with_the_identifier_in_brackets_block(self):
        clause = mk.FULL.format(a="20.000,00")
        for form in ("name [id]", "id [name]", "[id] name"):
            deed = mk.deed(E, 1, "2025-03-10", mk.OFFICE_A, clause, PCT, ["P-001"])
            later = mk.extract(E, 2, "2025-12-01", 1, mk.OFFICE_A, "Share capital: resolved EUR 20.000,00; subscribed "
                               "and paid in EUR 20.000,00", PCT, ["P-001"])
            for setup, docs in (("deed alone", s.office_witness([(deed[0], _bracket(deed[1], form))])),
                                ("deed and extract", [(deed[0], _bracket(deed[1], form)),
                                                      (later[0], _bracket(later[1], form))])):
                with self.subTest(form=form, setup=setup):
                    code, status, published, view = _status(docs)
                    self.assertNotEqual(_bracket(deed[1], form), deed[1])
                    self.assertEqual((code, status, published), (2, "BLOCKED", False))
                    self.assertNotEqual(view.get("shareholders", {}).get("status"), "STATED")

    def test_E0005_a_blank_line_inside_a_list_ends_it_and_blocks(self):
        deed = mk.deed(E, 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="20.000,00"),
                       [("P-001", "1/2"), ("P-002", "1/2")], ["P-001"])
        rows = _ROW.findall(deed[1])
        first = f"- {rows[0][0]} ({rows[0][1]}): {rows[0][2]}"
        gap = (deed[0], deed[1].replace(first + "\n", first + "\n\n", 1))
        self.assertIn(first + "\n\n- P-002", gap[1])
        code, status, published, view = _status(s.office_witness([gap]))
        self.assertEqual((code, status, published), (2, "BLOCKED", False))


class D39_Hand22Limits(unittest.TestCase):
    """The same, on the hand documents of run 22 (now seen data)."""

    @classmethod
    def setUpClass(cls):
        cls.gold = json.loads((HAND / "gold.json").read_text(encoding="utf-8"))
        cls.work = s.tmp("ezio-d39-h22-")
        cls.code, _, cls.report = s.run(HAND / "input", cls.work)

    def test_the_declared_blocks(self):
        for eid, words in (("E-0005", "sums to 1/2"), ("E-0006", "a line of the list could not be read"),
                           ("E-0025", "holds a numeral"), ("E-0028", "holds a numeral")):
            with self.subTest(eid=eid):
                v = self.report["entities"][eid]
                self.assertEqual(v["status"], "BLOCKED")
                self.assertIn(words, v["reason"])
                self.assertFalse((self.work / "dossiers" / eid).exists())

    def test_D3_a_known_surname_inside_a_whole_street_entry_is_read(self):
        self.assertEqual(self.report["entities"]["E-0033"]["status"], "OK")
        view = jsonio.load(self.work / "views" / "E-0033.json")["fields"]["registered_office"]
        self.assertEqual((view["status"], view["value"]),
                         ("STATED", self.gold["entities"]["E-0033"]["fields"]["registered_office"]["value"]))
        self.assertEqual(len(view["sources"]), 2)

    def test_D3_a_known_full_name_inside_an_address_is_not_read(self):
        inp = s.tmp("ezio-d39-e33-")
        for rel in ("config.json", "identity/persons.json"):
            jsonio.write_bytes(inp / rel, (HAND / "input" / rel).read_bytes())
        for f in sorted((HAND / "input" / "entities" / "E-0033").glob("*.txt")):
            text = f.read_text(encoding="utf-8").replace("Via del Segnaposto 5", "Via Gino Segnaposto 5")
            jsonio.write_bytes(inp / "entities" / "E-0033" / f.name, text.encode("utf-8"))
        work = s.tmp("ezio-d39-e33w-")
        code, _, report = s.run(inp, work)
        self.assertNotEqual(report["entities"]["E-0033"]["status"], "FAILED")
        views = work / "views" / "E-0033.json"
        if views.exists():
            office = jsonio.load(views)["fields"]["registered_office"]
            self.assertNotEqual(office["status"], "STATED", office)
            self.assertNotIn("Gino", str(office.get("value")))


if __name__ == "__main__":
    unittest.main()
