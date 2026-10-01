"""Decisions live in ordered rule files: first match wins, every rule has a reason and a test."""
import copy
import dataclasses
import json
import shutil
import unittest

from . import ROOT
from . import support as s

from dossier import rules_engine
from dossier.lib import jsonio


def _copy_rules():
    dst = s.tmp("ezio-rules-") / "rules"
    shutil.copytree(ROOT / "rules", dst)
    return dst


def _edit(directory, name, change):
    path = directory / name
    obj = json.loads(path.read_text(encoding="utf-8"))
    change(obj)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


class RuleFiles(unittest.TestCase):
    def test_every_inline_test_passes(self):
        self.assertEqual(rules_engine.self_test(s.rules()), [])

    def test_every_rule_has_an_id_a_reason_and_a_test(self):
        ids = []
        for group in rules_engine.rule_groups(s.rules()):
            self.assertTrue(group)
            for r in group:
                ids.append(r["id"])
                self.assertGreater(len(r["rationale"]), 20, r["id"])
                self.assertTrue(r["tests"], r["id"])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 90)       # 47 until v2.0.1; + HEV-010..080, HEV-999 in v2.0.2; + FEV-010..060, FEV-900..930, FEV-999 in v2.0.3;
        #                                      + CLS-010..CLS-999 (20) and DISC-006 in v2.0.5;
        #                                      + CLS-005 and DISC-035 in v2.0.6

    def test_every_group_ends_with_a_default(self):
        r = s.rules()
        self.assertEqual(r.extract["doc_kinds"][-1]["id"], "KIND-999")
        self.assertEqual(r.extract["holders_evidence"]["rules"][-1]["id"], "HEV-999")
        self.assertEqual(r.figure_nature["rules"][-1]["id"], "NAT-999")
        self.assertEqual(r.discrepancy["outgoing_scan"]["rules"][-1]["id"], "SCAN-999")
        self.assertEqual(r.ownership["rules"][-1]["when"], "always")

    def test_exceptions_are_on_top(self):
        r = s.rules()
        self.assertEqual(r.ownership["rules"][0]["outcome"], "BLOCKED")
        self.assertEqual(r.discrepancy["rules"][0]["id"], "DISC-005")

    def test_legal_assumptions_are_parameters_to_confirm(self):
        got = s.rules().legal_assumptions()
        self.assertEqual(len(got), 11)       # + discrepancy.json unread_document_scope in v2.0.3
        for a in got:
            self.assertEqual(a["status"], "[TO CONFIRM with legal]", a["parameter"])
            self.assertGreater(len(a["note"]), 20)
        listed = (ROOT / "docs" / "ASSUMPTIONS.md").read_text(encoding="utf-8")
        for a in got:
            self.assertIn(f"`{a['parameter']}`", listed)
        self.assertEqual(listed.count("[TO CONFIRM with legal]"), 11 + 1)

    def test_rule_files_carry_a_version(self):
        r = s.rules()
        for name in ("extract", "figure_nature", "discrepancy", "ownership"):
            self.assertRegex(getattr(r, name)["version"], r"^2\.0\.\d+$")


class RuleFilesRefuse(unittest.TestCase):
    def test_duplicate_id(self):
        d = _copy_rules()
        _edit(d, "ownership.json", lambda o: o["rules"][1].update(id="OWN-010"))
        with self.assertRaisesRegex(rules_engine.RuleError, "duplicate rule id OWN-010"):
            rules_engine.load(d)

    def test_rule_without_rationale(self):
        d = _copy_rules()
        _edit(d, "discrepancy.json", lambda o: o["rules"][2].pop("rationale"))
        with self.assertRaises(rules_engine.RuleError):
            rules_engine.load(d)

    def test_wrong_file_name_inside(self):
        d = _copy_rules()
        _edit(d, "extract.json", lambda o: o.update(file="other.json"))
        with self.assertRaises(rules_engine.RuleError):
            rules_engine.load(d)

    def test_float_parameter(self):
        d = _copy_rules()
        _edit(d, "ownership.json", lambda o: o["parameters"]["sum_must_equal"].update(value=1.0))
        with self.assertRaises(jsonio.FloatRefused):
            rules_engine.load(d)

    def test_rule_without_tests_fails_the_self_test(self):
        d = _copy_rules()
        _edit(d, "figure_nature.json", lambda o: o["rules"][0].pop("tests"))
        failures = rules_engine.self_test(rules_engine.load(d))
        self.assertTrue(any("has no inline test" in f for f in failures), failures)

    def test_a_run_refuses_rules_whose_tests_fail(self):
        d = _copy_rules()
        _edit(d, "ownership.json", lambda o: o["rules"].insert(0, o["rules"].pop(2)))   # OWN-020 above OWN-010
        self.assertTrue(rules_engine.self_test(rules_engine.load(d)))
        work = s.tmp()
        got = s.child(["-m", "dossier.run", "--input", str(ROOT / "scenarios" / "S01" / "input"),
                       "--work", str(work), "--rules", str(d)])
        self.assertEqual(got.returncode, 3, got.stdout + got.stderr)
        self.assertIn("RUN FAILED", got.stdout)
        self.assertNotIn("RUN OK", got.stdout)
        self.assertFalse((work / "dossiers").exists())


class InlineTestsBite(unittest.TestCase):
    """Mutation: changing the order or the outcome of a rule makes its inline tests fail."""

    def _mutated(self, change):
        r = s.rules()
        data = {f: copy.deepcopy(getattr(r, f)) for f in ("extract", "figure_nature", "discrepancy", "ownership")}
        change(data)
        return rules_engine.self_test(dataclasses.replace(r, **data))

    def test_order_matters_in_every_group(self):
        groups = {
            "doc_kinds": lambda d: d["extract"]["doc_kinds"],
            "holders_evidence": lambda d: d["extract"]["holders_evidence"]["rules"],
            "classified_lines": lambda d: d["extract"]["classified_lines"]["rules"],
            "nature": lambda d: d["figure_nature"]["rules"],
            "discrepancy": lambda d: d["discrepancy"]["rules"],
            "scan": lambda d: d["discrepancy"]["outgoing_scan"]["rules"],
            "ownership": lambda d: d["ownership"]["rules"],
        }
        for name, pick in groups.items():
            with self.subTest(group=name):
                failures = self._mutated(lambda d: pick(d).reverse())
                self.assertTrue(failures, f"reversing {name} went unnoticed")

    def test_outcome_matters(self):
        def change(d):
            rule = next(r for r in d["discrepancy"]["rules"] if r["id"] == "DISC-020")
            rule["status"] = "STATED"
        self.assertTrue(self._mutated(change))

    def test_an_abstention_rule_that_never_fires_is_noticed(self):
        """The tests live with the rule: a rule that stops matching fails its own tests.

        The group has no catch-all on purpose: when no rule matches, the resolution stops with an error
        instead of falling back to a value. Both ways of being noticed are accepted here.
        """
        for rid in ("DISC-005", "DISC-030"):
            with self.subTest(rule=rid):
                def change(d, rid=rid):
                    next(r for r in d["discrepancy"]["rules"] if r["id"] == rid)["when"] = "never"
                try:
                    failures = self._mutated(change)
                except RuntimeError as exc:
                    self.assertIn("has no rule for field", str(exc))
                else:
                    self.assertTrue(any(f.startswith(rid) for f in failures), failures)

    def test_a_rule_cannot_be_dropped_with_its_tests_and_go_unnoticed(self):
        """Dropping a rule removes its inline tests too; the suites of the evaluation and these tests remain."""
        from dossier import s3_discrepancy
        r = s.rules()
        data = copy.deepcopy(r.discrepancy)
        data["rules"] = [x for x in data["rules"] if x["id"] != "DISC-030"]
        weak = dataclasses.replace(r, discrepancy=data)
        self.assertEqual(rules_engine.self_test(weak), [])          # the gap, stated
        base = {"field": "f", "edition_no": 1, "source_file": "x", "line": 1, "line_end": 1, "quote": "q",
                "nature": "resolved", "rule": "T"}
        deed = dict(base, role="event", series="DEED", source_doc="D1", source_date="2025-01-10",
                    edition="DEED/1", status="STATED", value="50000.00")
        extract = dict(base, role="state", series="EXTRACT", source_doc="D2", source_date="2026-01-10",
                       edition="EXTRACT/1", status="TO_CONFIRM", reason="illegible figure")
        self.assertEqual(s3_discrepancy.resolve_field("f", [deed, extract], r, [])["status"], "TO_CONFIRM")
        self.assertEqual(s3_discrepancy.resolve_field("f", [deed, extract], weak, [])["status"], "STATED")

    def test_scan_cue_exclusion_is_a_rule_parameter(self):
        def change(d):
            d["discrepancy"]["outgoing_scan"]["parameters"]["field_cue_exclusions"] = {}
        failures = self._mutated(change)
        self.assertTrue(any("SCAN-020" in f for f in failures), failures)


if __name__ == "__main__":
    unittest.main()
