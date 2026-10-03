"""D34 (v2.0.5): the limit "may publish" of v2.0.4 closed. A document of a recognised type is read only for the fields
of its own kind; when its text also changes another field, that field must not be published from an older document
as fact.

Since v2.0.5 every non-empty body line of a document of a recognised type is decided by rules/extract.json
classified_lines: a line that no rule of its kind explains makes the document one that may change every field
(DISC-006 keeps each field [TO CONFIRM] when the document is not older than the latest event of the field, the
criterion of DISC-005), and the line is checked for holdings as a line of an unread document is (OWN-015 blocks).
A holders' table in a document of a kind that is not read for holders is read whole and summed, or OWN-015 blocks.

The siblings below are tested by class, never by literal strings (R6): five classes, each in several wordings (a
separate line, the same line, words of the pack's own lists, a sentence that changes the field without naming it),
each wording with the kind's own title line, with every title noun of FEV-920 and with no title line. The base is a
deed and a registry extract that agree; the sibling is dated after both. Every case must end with the fields it
changes [TO CONFIRM], or blocked; never a fact. tests/test_d34_forms.py was also run on the code of v2.0.4 (CHANGELOG
2.0.5 gives the count of the cases v2.0.4 publishes wrongly, by class).

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import unittest

from . import support as s
from .support import mk

from dossier.lib import jsonio

H = [("P-001", "60%"), ("P-002", "40%")]
CAPITAL = mk.FULL.format(a="50.000,00")
DEED = mk.deed("E-0001", 1, "2024-03-10", mk.OFFICE_A, CAPITAL, H, ["P-001"])
EXTRACT = mk.extract("E-0001", 2, "2025-02-01", 1, mk.OFFICE_A,
                     "Share capital: resolved EUR 50.000,00; subscribed EUR 50.000,00; paid in EUR 50.000,00", H,
                     ["P-001"])
CAPITAL_FIELDS = ("share_capital.resolved", "share_capital.subscribed", "share_capital.paid_in")
RAISE = "The meeting resolved to increase the share capital from EUR 50.000,00 to EUR 80.000,00."
RAISE_FULL = RAISE + " The increase has been fully subscribed and fully paid in."      # the generator's form res_full
MOVE = f"The registered office is transferred from {mk.OFFICE_A} to {mk.OFFICE_B}."

# the title nouns of FEV-920 (rules/extract.json parameter title_nouns, shared with CLS-900)
TITLE_NOUNS = ("minutes", "notice", "entries", "entry", "register", "ledger", "statement", "certificate",
               "memorandum", "summary", "record", "report", "letter", "declaration")

# kind -> (type label, the generator's own title line or None, edition)
KINDS = {
    "RESOLUTION": ("Resolution on share capital", "Minutes of the holders' meeting (synthetic).", "RESOLUTION/1"),
    "TRANSFER": ("Share transfer notice", "Notice of a transfer of shares (synthetic).", "TRANSFER/1"),
    "APPOINTMENT": ("Appointment of directors", "Minutes of the holders' meeting (synthetic).", "APPOINTMENT/1"),
    "OFFICE": ("Transfer of registered office", None, "OFFICE/1"),
}

# (class, kind, [(wording, body lines after the title)], fields the text changes beyond its kind)
CLASSES = (
    ("A capital resolution whose new quotas go to a new holder", "RESOLUTION", [
        ("separate line", [RAISE, "The new quotas are subscribed by P-003 (Carlo Inventati)."]),
        ("same line", ["The meeting resolved to increase the share capital from EUR 50.000,00 to EUR 80.000,00, the "
                       "new quotas being subscribed by P-003 (Carlo Inventati)."]),
        ("pack words: taken up", [RAISE, "The increase was taken up in full by Carlo Inventati."]),
        ("unnamed: who put in the money", [RAISE, "Mr Carlo Inventati put in the whole of the increase and joins "
                                                  "the company."]),
        ("unnamed: name only", [RAISE, "Welcome to Carlo Inventati."]),
    ], ("shareholders",)),
    ("A transfer notice that also moves the seat", "TRANSFER", [
        ("separate line", ["Holders after the transfer:", *mk._holders([("P-001", "100%")]), "", MOVE]),
        ("same line as a row", ["Holders after the transfer:",
                                f"- P-001 (Aldo Finti): 100%; the seat moves to {mk.OFFICE_B}"]),
        ("pack words: seat", ["Holders after the transfer:", *mk._holders(H), "",
                              f"The company has its seat at {mk.OFFICE_B}."]),
        ("unnamed: operates from", ["Holders after the transfer:", *mk._holders(H), "",
                                    f"From the first of September the company receives its post and holds its "
                                    f"meetings at {mk.OFFICE_B}."]),
        ("unnamed: address only", ["Holders after the transfer:", *mk._holders(H), "", mk.OFFICE_B]),
    ], ("registered_office",)),
    ("An appointment that also states a capital change", "APPOINTMENT", [
        ("separate line", ["Directors in office after this appointment:", *mk._directors(["P-001", "P-003"]), "",
                           "The meeting also resolved to increase the share capital from EUR 50.000,00 to "
                           "EUR 80.000,00."]),
        ("same line as the heading", ["Directors in office after this appointment, with the share capital now "
                                      "EUR 80.000,00:", *mk._directors(["P-001", "P-003"])]),
        ("pack words: paid in", ["Directors in office after this appointment:", *mk._directors(["P-001", "P-003"]),
                                 "", "A further EUR 30.000,00 was paid in by the members."]),
        ("unnamed: members put in", ["Directors in office after this appointment:",
                                     *mk._directors(["P-001", "P-003"]), "",
                                     "The members also put in a further EUR 15.000,00 each, for good."]),
    ], CAPITAL_FIELDS),
    ("An office transfer that also names a new director", "OFFICE", [
        ("same line", [MOVE + " P-003 (Carlo Inventati) is appointed director."]),
        ("separate line", [MOVE, "P-003 (Carlo Inventati) is appointed director."]),
        ("a list of another kind", [MOVE, "Directors:", *mk._directors(["P-003"])]),
        ("unnamed: takes over", [MOVE, "Mr Carlo Inventati takes over the running of the company from Mr Aldo "
                                       "Finti."]),
        ("person line only", [MOVE, "- P-003 (Carlo Inventati)"]),
    ], ("directors",)),
    ("A resolution that holds a holders' table", "RESOLUTION", [
        ("a table read whole", [RAISE, "Holders:", *mk._holders([("P-001", "50%"), ("P-003", "50%")])]),
        ("a table under a heading of its own", [RAISE, "Holders after the increase:",
                                                *mk._holders([("P-001", "50%"), ("P-003", "50%")])]),
        ("a table that does not sum", [RAISE, "Holders:", *mk._holders([("P-001", "50%"), ("P-003", "40%")])]),
        ("two tables", [RAISE, "Holders:", *mk._holders(H), "", "Holders:",
                        *mk._holders([("P-001", "50%"), ("P-003", "50%")])]),
        ("rows without a heading", [RAISE, *mk._holders([("P-001", "50%"), ("P-003", "50%")])]),
    ], ("shareholders",)),
)


def _titles(kind: str):
    own = KINDS[kind][1]
    yield "no title", None
    if own:
        yield "own title", own
    for noun in TITLE_NOUNS:
        yield noun, f"{noun.capitalize()} (synthetic)."


def _sibling(kind: str, title: str | None, body: list[str]) -> tuple[str, str]:
    label, _, edition = KINDS[kind]
    return mk._file("E-0001", "2026-08-20_doc-3.txt", mk._head("E-0001", 3, label, "2026-08-20", edition)
                    + ([title] if title else []) + body)


def _run(docs):
    work = s.tmp()
    code, _, report = s.run(s.tiny(docs, "2026-09-30"), work)
    status = report["entities"]["E-0001"]["status"]
    view = jsonio.load(work / "views" / "E-0001.json")
    prov_path = work / "dossiers" / "E-0001" / "provenance.json"
    prov = jsonio.load(prov_path) if prov_path.exists() else None
    return status, view, prov


def cases():
    """(class, wording, title name, documents, fields changed) for every sibling."""
    for cls, kind, wordings, changes in CLASSES:
        for wording, body in wordings:
            for tname, title in _titles(kind):
                yield cls, wording, tname, [DEED, EXTRACT, _sibling(kind, title, body)], changes


def unsafe(status: str, view: dict, prov: dict | None, changes) -> str:
    """'' when the case is safe (blocked, or every field it changes [TO CONFIRM] and no holding derived from an older
    table), else what was published wrongly."""
    if status == "BLOCKED" and prov is None:
        return ""
    if status != "OK":
        return f"status {status}"
    wrong = [f for f in changes if view["fields"][f]["status"] != "TO_CONFIRM" or "value" in view["fields"][f]]
    if "shareholders" in changes and (prov["derived"] or [f for f in prov["figures"] if f["section"] == "cap_table"]):
        wrong.append("holdings derived")
    return ", ".join(wrong)


class D34_RecognisedTypeSiblings(unittest.TestCase):
    def test_every_sibling_with_every_title_is_safe(self):
        n = 0
        outcomes = s.sweep(_run, [(docs,) for _, _, _, docs, _ in cases()])
        for (cls, wording, tname, docs, changes), outcome in zip(cases(), outcomes):
            with self.subTest(cls=cls, wording=wording, title=tname):
                n += 1
                self.assertEqual(unsafe(*outcome.result(), changes), "")
        self.assertEqual(n, sum(len(w) * (len(TITLE_NOUNS) + 1 + (KINDS[k][1] is not None))
                                for _, k, w, _ in CLASSES))

    def test_the_title_nouns_are_those_of_the_rule(self):
        import re
        nouns = re.search(r"\(\?:((?:[a-z]+\|)+[a-z]+)\)", s.rules().extract["parameters"]["title_nouns"]).group(1)
        self.assertEqual(tuple(nouns.split("|")), TITLE_NOUNS)


class D34_PlainDocumentsStillPublish(unittest.TestCase):
    """The cost side: documents of the generator's own forms are closed, and the facts they do not touch stay facts."""

    def test_plain_resolution_transfer_appointment_office(self):
        docs = [DEED, EXTRACT,
                mk.resolution("E-0001", 3, "2026-08-20", RAISE_FULL),
                mk.transfer("E-0001", 4, "2026-08-21", [("P-001", "50%"), ("P-002", "50%")]),
                mk.appointment("E-0001", 5, "2026-08-22", ["P-001", "P-002"], "P-002"),
                mk.office_transfer("E-0001", 6, "2026-08-23", MOVE)]
        # since v2.0.8 (D37) the new address of an office transfer is a fact only when a later source repeats it
        # (rules/extract.json address_corroboration ADR-020); until then its words cannot be checked: the office
        # stays [TO CONFIRM] (DISC-038) and so does every other field (ADR-999, DISC-006) - the measured cost
        status, view, prov = _run(docs)
        self.assertEqual(status, "OK", view["ownership"])
        self.assertEqual(view["fields"]["registered_office"]["rule"], "DISC-038")
        for f in ("name", "legal_form", "directors", "shareholders", *CAPITAL_FIELDS):
            self.assertEqual(view["fields"][f]["rule"], "DISC-006", (f, view["fields"][f]))
        # a later registry extract repeats the new address and the values after the events: every field is a fact
        docs.append(mk.extract("E-0001", 7, "2026-08-24", 2, mk.OFFICE_B,
                               "Share capital: resolved EUR 80.000,00; subscribed EUR 80.000,00; paid in EUR 80.000,00",
                               [("P-001", "50%"), ("P-002", "50%")], ["P-001", "P-002"]))
        status, view, prov = _run(docs)
        self.assertEqual(status, "OK", view["ownership"])
        for f in ("name", "legal_form", "registered_office", "directors", "shareholders", *CAPITAL_FIELDS):
            self.assertEqual(view["fields"][f]["status"], "STATED", (f, view["fields"][f]))
        self.assertEqual(view["fields"]["registered_office"]["value"], mk.OFFICE_B)
        self.assertEqual(view["warnings"]["classified_checks"], [])

    def test_a_resolution_table_that_agrees_is_summed_and_keeps_the_holders(self):
        # a holders' table in a resolution may change the shareholders: summed (OWN-010), and the field stays
        # [TO CONFIRM] even when the table equals the current one (no agreeing-table exception for these documents)
        rel, text = mk.resolution("E-0001", 3, "2026-08-20", RAISE_FULL)
        text += "Holders:\n" + "\n".join(mk._holders(H)) + "\n"
        status, view, prov = _run([DEED, EXTRACT, (rel, text)])
        self.assertEqual(status, "OK", view["ownership"])
        self.assertEqual(view["fields"]["shareholders"]["status"], "TO_CONFIRM")
        self.assertEqual(view["fields"]["shareholders"]["rule"], "DISC-006")
        for f in CAPITAL_FIELDS:
            self.assertEqual(view["fields"][f]["status"], "STATED", f)

    def test_a_raise_that_does_not_state_the_subscription(self):
        # the resolution is the latest event of the capital and gives no subscribed or paid-in figure: those two
        # fields stay [TO CONFIRM] (DISC-030, as in v2.0.4), never the older figures as fact; the resolved capital
        # is the resolution's (the generator never writes this form)
        status, view, prov = _run([DEED, EXTRACT, mk.resolution("E-0001", 3, "2026-08-20", RAISE)])
        self.assertEqual(status, "OK", view["ownership"])
        self.assertEqual(view["fields"]["share_capital.resolved"]["status"], "STATED")
        for f in ("share_capital.subscribed", "share_capital.paid_in"):
            self.assertEqual(view["fields"][f]["status"], "TO_CONFIRM", f)
            self.assertEqual(view["fields"][f]["rule"], "DISC-030", f)


def load_tests(loader, tests, pattern):
    """v2.0.14: the sweep's cases go to the workers now, while the other tests run (tests/support.py ahead())."""
    s.ahead(tests, "D34_RecognisedTypeSiblings.test_every_sibling_with_every_title_is_safe", _run,
            [(docs,) for _, _, _, docs, _ in cases()])
    return tests


if __name__ == "__main__":
    unittest.main()
