"""D37 (c), v2.0.8: eval/score.py gives one count per kind of never-event of section 1.5 of eval/BLIND_PROTOCOL.md,
named <kind>_wrong_committed (score.WRONG_COMMITTED), and their sum never_events_by_kind_total. Each is counted by the
same call that writes the never-event into the list. These tests check the agreement on the recorded hand corpora
(every one of them, on this code) and, so that the counts are not checked at zero only, on the output of the hand
corpus of run 7 scored against a gold changed so that every kind occurs (the changed gold and provenance are copies in a
temporary folder; nothing recorded is changed). No existing field of the scorer is changed: the test of the existing
names is that the recorded results still read (eval/history.json, tests/test_eval.py)."""
import json
import re
import shutil
import unittest

from . import support as s

from eval import score
from dossier.lib import jsonio

BLIND = s.ROOT / "eval" / "blind"
# the wording of each kind in the never-event list, read independently of the counter
TEXT = {
    "fact_value_wrong_committed": re.compile(r": shown .*, gold "),
    "planted_conflict_wrong_committed": re.compile(r"conflict shown with values that are not the gold's|planted conflict "
                                                   r"shown as one value"),
    "gold_to_confirm_wrong_committed": re.compile(r"gold says it cannot be read, shown as"),
    "not_in_gold_wrong_committed": re.compile(r"shown but not in the gold$"),
    "unsummed_table_wrong_committed": re.compile(r"cap table does not sum to the whole, run status"),
    "published_table_sum_wrong_committed": re.compile(r"the published cap table sums to"),
    "effective_holding_wrong_committed": re.compile(r"effective holdings (differ from|shown where) the reference"),
    "figure_source_wrong_committed": re.compile(r"figure without source, date or edition$"),
}


def by_text(never: list[str]) -> dict[str, int]:
    out = {k: 0 for k in TEXT}
    for t in never:
        hits = [k for k, rx in TEXT.items() if rx.search(t)]
        assert len(hits) == 1, (t, hits)
        out[hits[0]] += 1
    return out


class D37_WrongCommittedAgree(unittest.TestCase):
    def check(self, got: dict):
        m = got["metrics"]
        self.assertEqual(list(score.WRONG_COMMITTED), list(TEXT))
        for k in score.WRONG_COMMITTED:
            self.assertIsInstance(m[k], int, k)
        self.assertEqual({k: m[k] for k in score.WRONG_COMMITTED}, by_text(got["never_event_list"]))
        self.assertEqual(m["never_events_by_kind_total"], m["never_events"])
        self.assertEqual(sum(m[k] for k in score.WRONG_COMMITTED), m["never_events"])

    def test_recorded_hand_corpora(self):
        for hand in ("hand", "hand-9", "hand-11", "hand-14", "hand-16", "hand-18"):
            with self.subTest(hand=hand):
                work = s.tmp()
                got = score.evaluate(hand, corpus=BLIND / hand / "input", gold_path=BLIND / hand / "gold.json",
                                     work=work)
                self.check(got)
                # v2.0.8: no never-event on any recorded hand corpus (hand-18: 4 in E-0015 on v2.0.6 and v2.0.7)
                self.assertEqual(got["metrics"]["never_events"], 0, got["never_event_list"])
                if hand == "hand-18":
                    self.hand18(work / "work")

    def hand18(self, out):
        """Goals (a), (b), (d) on the recorded corpus: E-0015 every field [TO CONFIRM]; E-0020, E-0025, E-0026 block
        (declared limits); E-0012's capital keeps [TO CONFIRM] (declared limit)."""
        report = jsonio.load(out / "run_report.json")["entities"]
        for e in ("E-0020", "E-0025", "E-0026"):
            self.assertEqual(report[e]["status"], "BLOCKED", e)
        for e, fields in (("E-0015", None), ("E-0012", ("share_capital.resolved", "share_capital.subscribed",
                                                        "share_capital.paid_in"))):
            self.assertEqual(report[e]["status"], "OK", e)
            view = jsonio.load(out / "views" / f"{e}.json")["fields"]
            for f in fields or view:
                self.assertEqual(view[f]["status"], "TO_CONFIRM", (e, f))

    def test_every_kind_counted(self):
        work = s.tmp()
        score.evaluate("hand", corpus=BLIND / "hand" / "input", gold_path=BLIND / "hand" / "gold.json", work=work)
        out = work / "work"
        gold = json.loads((BLIND / "hand" / "gold.json").read_text(encoding="utf-8"))

        # every kind but the unsummed table: one changed gold and one changed provenance of E-0001
        g = json.loads(json.dumps(gold))
        f = g["entities"]["E-0001"]["fields"]
        f["name"]["value"] = "Altra Ditta Inventata S.r.l."                                        # kind 1
        f["registered_office"] = {"status": "DISCREPANCY", "values": [f["registered_office"]["value"], "x"]}  # kind 2
        f["share_capital.paid_in"]["values"] = ["1.00", "2.00"]                                     # kind 2
        f["legal_form"] = {"status": "TO_CONFIRM"}                                                  # kind 3
        del f["directors"]                                                                          # kind 4
        g["entities"]["E-0001"]["ownership"]["effective"] = {"P-001": "1/2", "P-002": "1/2"}        # kind 7
        changed = s.tmp() / "work"
        shutil.copytree(out, changed)
        prov_path = changed / "dossiers" / "E-0001" / "provenance.json"
        prov = jsonio.load(prov_path)
        cap = [x for x in prov["figures"] if x["section"] == "cap_table"]
        cap[0]["value"] = "1/7"                                                                     # kind 6
        next(x for x in prov["figures"] if x["section"] == "facts" and x["field"].startswith("fin."))["edition"] = ""  # 8
        jsonio.write(prov_path, prov)
        got = score.score(changed, g)
        self.check(got)
        for k in score.WRONG_COMMITTED:
            if k != "unsummed_table_wrong_committed":
                self.assertGreaterEqual(got["metrics"][k], 1, k)

        # the unsummed table: the gold blocks the entity that the run published
        g = json.loads(json.dumps(gold))
        g["entities"]["E-0001"]["build"] = "BLOCKED"
        got = score.score(out, g)
        self.check(got)
        self.assertEqual(got["metrics"]["unsummed_table_wrong_committed"], 1)


if __name__ == "__main__":
    unittest.main()
