"""D39 (v2.0.10) (b): the count form of the capital clause, defect D2 of the blind run of v2.0.9 (eval/history.json run 22,
hand corpus eval/blind/hand-22, E-0007).

'The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and fully paid in.' is a line that
CLS-130 explains (the amount, then in either order the count and 'fully subscribed and fully paid in'), but until v2.0.9
the nature of its amount was decided by NAT-070 (the bare capital: resolved only), because NAT-020 reads 'fully
subscribed and fully paid in' only right after the amount. Subscribed and paid in were [TO CONFIRM] while the plain clause
gave all three (E-0001 of hand-22). v2.0.10 adds NAT-025 to rules/figure_nature.json: the count form, in one sentence,
with nothing after it but the full stop, and the amount the only current amount of the clause.

The siblings are the builder's own, by class (R6), never the literal strings of hand-22: the claimed form with and
without the count, 'split into ... shares', 'equal quotas', no comma; the forms that must NOT close - 'subscribed' only,
'paid in' only, partly, for one quarter, to be paid in, 'of which EUR X paid in', 'subscribed for EUR X', a nominal amount
per quota, another count verb, a qualifier or an exception after the words, a negation, an 'of which' before the
amount, the words split across two sentences or two lines, a second capital clause that contradicts, a different amount
elsewhere in the entity. The pack reads English clauses only; one Italian clause shows that it is not read at all.
Each clause is built three ways: the deed alone (with the office witness of tests/support.py), the deed and a later
registry extract that states the plain full values (the shape of E-0007), the deed and a later extract that states
another paid-in amount. A case is unsafe when a capital field is published as a fact with a value the case does not
allow. Run on the code of v2.0.9 (``python -m tests.test_d39_capital_count`` prints the table): 0 unsafe, the count
forms abstain on subscribed and paid in; on v2.0.10: 0 unsafe, the count forms give what the plain form gives.

Every case here is invented for the test (fictitious entities, invented test registry).
"""
import json
import sys
import unittest
from functools import lru_cache

from . import ROOT
from . import support as s
from .support import mk

from dossier.lib import jsonio

E = "E-0001"
C = ("resolved", "subscribed", "paid_in")
T = "20000.00"
A = frozenset({T})
NONE = frozenset()
CNT = [("P-001", "1.200 quotas"), ("P-002", "800 quotas")]
PCT = [("P-001", "60%"), ("P-002", "40%")]
LATER_FULL = "Share capital: resolved EUR 20.000,00; subscribed and paid in EUR 20.000,00"
LATER_PART = "Share capital: resolved EUR 20.000,00; subscribed EUR 20.000,00; paid in EUR 5.000,00"

CLAIMED = "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and fully paid in."
# (id, clause, holders' rows, values allowed for resolved / subscribed / paid_in on the deed alone, class)
CASES = (
    ("C01", CLAIMED, CNT, (A, A, A), "claimed count form, rows as counts"),
    ("C02", CLAIMED, PCT, (A, A, A), "claimed count form, rows as per cent"),
    ("C03", "The share capital is EUR 20.000,00, split into 2.000 shares, fully subscribed and fully paid in.", PCT,
     (A, A, A), "claimed count form, split into shares"),
    ("C04", "The share capital is EUR 20.000,00, divided into 2.000 equal quotas, fully subscribed and fully paid in.",
     PCT, (A, A, A), "claimed count form, equal quotas"),
    ("C05", "The share capital is EUR 20.000,00, fully subscribed and fully paid in.", PCT, (A, A, A), "plain form"),
    ("C06", "Il capitale sociale e' di EUR 20.000,00, suddiviso in 2.000 quote, interamente sottoscritto e interamente "
     "versato.", PCT, (A, A, A), "Italian: not read"),
    ("C07", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed.", PCT, (A, A, NONE),
     "subscribed only"),
    ("C08", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully paid in.", PCT, (A, NONE, A),
     "paid in only"),
    ("C09", "The share capital is EUR 20.000,00, fully subscribed.", PCT, (A, A, NONE), "subscribed only, no count"),
    ("C10", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and partly paid in.", PCT,
     (A, A, NONE), "partly"),
    ("C11", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and paid in for one "
     "quarter.", PCT, (A, A, NONE), "for one quarter"),
    ("C12", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and to be paid in.", PCT,
     (A, A, NONE), "to be paid in"),
    ("C13", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed, of which EUR 5.000,00 paid "
     "in.", PCT, (A, A, frozenset({"5000.00"})), "of which EUR X paid in"),
    ("C14", "The share capital is EUR 20.000,00, divided into 2.000 quotas, subscribed for EUR 15.000,00.", PCT,
     (A, frozenset({"15000.00"}), NONE), "subscribed for EUR X"),
    ("C15", "The share capital is EUR 20.000,00, divided into 2.000 quotas. The quotas are fully subscribed and fully "
     "paid in.", PCT, (A, NONE, NONE), "split across two sentences"),
    ("C16", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and fully paid in by "
     "contributions in kind still to be valued.", PCT, (A, NONE, NONE), "qualified after the words"),
    ("C17", "The share capital is EUR 20.000,00, divided into 2.000 quotas, not yet fully subscribed and fully paid in.",
     PCT, (A, NONE, NONE), "negated"),
    ("C18", "The share capital is EUR 100.000,00, of which EUR 20.000,00, divided into 2.000 quotas, fully subscribed "
     "and fully paid in.", PCT, (frozenset({"100000.00"}), A, A), "of which before the amount, with the count"),
    ("C19", "The share capital is EUR 100.000,00, of which EUR 20.000,00 fully subscribed and fully paid in.", PCT,
     (frozenset({"100000.00"}), A, A), "of which before the amount, no count"),
    ("C20", "The share capital is EUR 20.000,00, fully subscribed, of which EUR 5.000,00 paid in.", PCT,
     (A, A, frozenset({"5000.00"})), "of which EUR X paid in, no count"),
    ("C21", "The share capital is EUR 20.000,00, subscribed for EUR 15.000,00.", PCT,
     (A, frozenset({"15000.00"}), NONE), "subscribed for EUR X, no count"),
    ("C22", "The share capital is EUR 20.000,00, divided into 2.000 quotas of EUR 10,00 each, fully subscribed and fully "
     "paid in.", PCT, (A, A, A), "nominal amount per quota"),
    ("C23", "The share capital is EUR 20.000,00, consisting of 2.000 quotas, fully subscribed and fully paid in.", PCT,
     (A, A, A), "another count verb"),
    ("C24", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and fully paid in, except "
     "EUR 5.000,00 still due.", PCT, (A, A, NONE), "an exception after the words"),
    ("C25", "The share capital is EUR 20.000,00, divided into 2.000 quotas, fully subscribed and fully paid in; EUR "
     "5.000,00 remain to be paid in.", PCT, (A, A, NONE), "a contradiction after a semicolon"),
)
# the claimed count forms, which v2.0.10 reads as the plain form C05
COUNT_FORMS = ("C01", "C02", "C03", "C04")


def _deed(clause, holders):
    return mk.deed(E, 1, "2025-03-10", mk.OFFICE_A, clause, holders, ["P-001"])


def _later(capital):
    return mk.extract(E, 2, "2025-12-01", 1, mk.OFFICE_A, capital, PCT, ["P-001"])


def _setups(deed, allowed):
    """(name, documents, allowed): the deed alone with its office witness, then with a later extract that states the full
    values (the later edition may state 20000.00 for every nature), then with one that states another paid-in amount
    (20000.00 paid in must never be a fact)."""
    return (("alone", tuple(s.office_witness([deed])), allowed),
            ("later full", (deed, _later(LATER_FULL)), tuple(a | A for a in allowed)),
            ("later part", (deed, _later(LATER_PART)), (allowed[0] | A, allowed[1] | A, frozenset({"5000.00"}))))


def _special():
    """The cases built on a deed of another shape: a second capital clause in the same deed that contradicts, and the
    words split across two lines."""
    rel, text = _deed(CLAIMED, CNT)
    two = (rel, text.replace("4. Holders.", "3-bis. Paid-in share capital. The paid-in share capital is EUR 5.000,00.\n"
                                            "4. Holders."))
    rel, text = _deed("The share capital is EUR 20.000,00, divided into 2.000 quotas.", PCT)
    lines = (rel, text.replace("4. Holders.", "The quotas are fully subscribed and fully paid in.\n4. Holders."))
    return (("C26", "alone", tuple(s.office_witness([two])), (A, A, NONE), "a second clause that contradicts"),
            ("C26", "later full", (two, _later(LATER_FULL)), (A, A, A), "a second clause that contradicts"),
            ("C27", "alone", tuple(s.office_witness([lines])), (A, NONE, NONE), "split across two lines"))


@lru_cache(maxsize=None)
def _capital(docs: tuple) -> tuple[int, dict]:
    work = s.tmp("ezio-d39-")
    code, _, _ = s.run(s.tiny(list(docs)), work)
    view = jsonio.load(work / "views" / f"{E}.json")["fields"]
    return code, {n: view.get("share_capital." + n, {"status": "ABSENT"}) for n in C}


def _judge(fields, allowed) -> list[str]:
    return [n for n, ok in zip(C, allowed) if fields[n]["status"] == "STATED" and fields[n].get("value") not in ok]


def table() -> list[dict]:
    setups = [(cid, name, docs, alw, cls) for cid, clause, holders, allowed, cls in CASES
              for name, docs, alw in _setups(_deed(clause, holders), allowed)] + list(_special())
    rows = []
    for (cid, name, docs, alw, cls), outcome in zip(setups, s.sweep(_capital, [(d,) for _, _, d, _, _ in setups])):
        code, fields = outcome.result()
        rows.append({"case": cid, "setup": name, "class": cls, "exit": code, "unsafe": _judge(fields, alw),
                     "facts": sum(1 for n in C if fields[n]["status"] == "STATED"),
                     "shown": {n: fields[n].get("value", fields[n]["status"]) for n in C}})
    return rows


class D39_CountForm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = table()

    def test_no_sibling_publishes_a_capital_figure_wrongly(self):
        self.assertEqual(len(self.rows), 78)
        bad = [r for r in self.rows if r["unsafe"]]
        self.assertEqual(bad, [], json.dumps(bad, indent=1))

    def test_the_count_form_gives_what_the_plain_form_gives(self):
        plain = {r["setup"]: r["shown"] for r in self.rows if r["case"] == "C05"}
        for r in self.rows:
            if r["case"] in COUNT_FORMS:
                self.assertEqual(r["shown"], plain[r["setup"]], r)
        alone = [r for r in self.rows if r["case"] in COUNT_FORMS and r["setup"] == "alone"]
        self.assertTrue(all(r["shown"] == dict.fromkeys(C, T) for r in alone), alone)

    def test_the_forms_that_must_not_close_do_not_close(self):
        # subscribed and paid in are never both a fact from the deed alone, except in the claimed forms
        for r in self.rows:
            if r["setup"] == "alone" and r["case"] not in (*COUNT_FORMS, "C05"):
                self.assertFalse(r["shown"]["subscribed"] == T and r["shown"]["paid_in"] == T, r)

    def test_rule_level_the_amount_of_a_qualified_clause_is_resolved_or_nothing(self):
        from dossier.s1_extract import classify_natures
        for cid, clause, *_ in CASES:
            if cid in (*COUNT_FORMS, "C05", "C06"):
                continue
            for amt in classify_natures(clause, s.rules()):
                self.assertFalse({"subscribed", "paid_in"} <= set(amt["natures"]) and amt["token"] == "20.000,00",
                                 (cid, amt))


class D39_Hand22(unittest.TestCase):
    """E-0007 of hand-22 (now seen data): the count form gives its three facts; E-0001 (the plain form) is unchanged."""

    @classmethod
    def setUpClass(cls):
        d = ROOT / "eval" / "blind" / "hand-22"
        cls.gold = json.loads((d / "gold.json").read_text(encoding="utf-8"))
        cls.work = s.tmp("ezio-d39-hand22-")
        cls.code, _, cls.report = s.run(d / "input", cls.work)

    def test_E0007_and_E0001_capital_as_the_gold(self):
        for eid in ("E-0007", "E-0001"):
            self.assertEqual(self.report["entities"][eid]["status"], "OK")
            view = jsonio.load(self.work / "views" / f"{eid}.json")["fields"]
            for n in C:
                fld = "share_capital." + n
                self.assertEqual(view[fld]["status"], "STATED", (eid, fld))
                self.assertEqual(view[fld]["value"], self.gold["entities"][eid]["fields"][fld]["value"], (eid, fld))


def load_tests(loader, tests, pattern):
    """v2.0.14: the sweep's cases go to the workers now, while the other tests run (tests/support.py ahead()); the
    set-up of D39_CountForm reads them (table())."""
    docs = [d for _, clause, holders, allowed, _ in CASES for _, d, _ in _setups(_deed(clause, holders), allowed)]
    s.ahead(tests, ".D39_CountForm.", _capital, [(d,) for d in docs + [d for _, _, d, _, _ in _special()]])
    return tests


if __name__ == "__main__":
    for r in table():
        print(r["case"], r["setup"], "exit", r["exit"], "facts", r["facts"], "UNSAFE " + ",".join(r["unsafe"])
              if r["unsafe"] else "safe", r["shown"], r["class"], file=sys.stdout)
