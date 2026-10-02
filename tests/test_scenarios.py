"""Scenarios S01-S10: they pass, they pass the way the council executor runs them, and they can fail."""
import copy
import json
import unittest
from pathlib import Path

from . import ROOT
from . import support as s

import _common
import run_all

from dossier.lib import jsonio

SIDS = [f"S{n:02d}" for n in range(1, 11)]


class ScenariosPass(unittest.TestCase):
    def test_run_all(self):
        got = s.child(["scenarios/run_all.py"])
        lines = got.stdout.strip().split("\n")
        self.assertEqual(got.returncode, 0, got.stdout + got.stderr)
        self.assertEqual(lines[-1], "Scenarios: 10/10 PASS")
        self.assertEqual([line.split()[:2] for line in lines[:-1]], [[sid, "PASS"] for sid in SIDS])

    def test_each_scenario_as_the_executor_runs_it(self):
        """cwd = the scenario folder, `python` = this interpreter, a bare environment, no network."""
        for sid in SIDS:
            with self.subTest(scenario=sid):
                folder = ROOT / "scenarios" / sid
                spec = json.loads((folder / "scenario.json").read_text(encoding="utf-8"))
                self.assertEqual(spec["run"][0], "python")
                self.assertTrue((folder / spec["run"][1]).is_file())
                got = s.child(spec["run"][1:], cwd=folder, timeout=spec.get("timeout_s", 300))
                self.assertEqual(got.returncode, spec.get("expect_exit", 0), got.stdout + got.stderr)
                self.assertTrue(got.stdout.startswith(f"{sid} PASS"), got.stdout)


class ScenariosCanFail(unittest.TestCase):
    """Mutation: with a wrong expected value the check must say FAIL (it compares, it does not just run)."""

    def _with_expected(self, sid, change):
        real, real_workdir = _common.expected, _common.workdir
        exp = copy.deepcopy(real(sid))
        change(exp)
        _common.expected = lambda _sid: exp
        # v2.0.10 (D39 d): the check runs in this process, so its work folders are made by support.tmp() and removed
        # when the process ends (in v2.0.9 each of these checks left its folders in TEMP)
        _common.workdir = lambda _sid: Path(jsonio.ext(s.tmp(f"ezio-{_sid}-")))
        try:
            return run_all.load_check(sid)()
        finally:
            _common.expected, _common.workdir = real, real_workdir

    def _fails(self, sid, change):
        ok, line, _ = self._with_expected(sid, change)
        self.assertFalse(ok, line)
        self.assertTrue(line.startswith(f"{sid} FAIL"), line)

    def test_unchanged_expected_passes(self):
        ok, line, _ = self._with_expected("S01", lambda e: None)
        self.assertTrue(ok, line)

    def test_s01_expects_a_single_fact_instead_of_the_discrepancy(self):
        self._fails("S01", lambda e: e["fields"].update(
            {"share_capital.resolved": {"status": "STATED", "value": "80000.00"}}))

    def test_s01_other_value(self):
        self._fails("S01", lambda e: e["fields"]["share_capital.resolved"]["values"][0].update(value="55000.00"))

    def test_s02_expects_a_build(self):
        self._fails("S02", lambda e: e["percent"].update(exit_code=0))

    def test_s04_expects_a_decoy_to_be_flagged(self):
        self._fails("S04", lambda e: e["stale"].append({"file": "invoice-2026-02-14.txt", "line": 3}))

    def test_s04_expects_one_stale_figure_less(self):
        self._fails("S04", lambda e: (e["stale"].pop(), e.update(max_false_positives=0)))

    def test_s04_other_replacing_edition(self):
        self._fails("S04", lambda e: e["every_finding"].update(new_edition="EXTRACT/2"))

    def test_s07_other_fraction(self):
        def change(e):
            text = json.dumps(e)
            assert '"45/49"' in text
            e.clear()
            e.update(json.loads(text.replace('"45/49"', '"44/49"')))
        self._fails("S07", change)

    def test_s10_other_nature(self):
        def change(e):
            text = json.dumps(e)
            assert '"250000.00"' in text
            e.clear()
            e.update(json.loads(text.replace('"250000.00"', '"400000.00"')))
        self._fails("S10", change)


class ScenarioFolders(unittest.TestCase):
    def test_five_pieces_each(self):
        for sid in SIDS:
            folder = ROOT / "scenarios" / sid
            with self.subTest(scenario=sid):
                spec = json.loads((folder / "scenario.json").read_text(encoding="utf-8"))
                self.assertEqual(spec["run"], ["python", "check.py"])
                self.assertTrue(any((folder / "input").rglob("*.txt")) or any((folder / "input").rglob("*.json")))
                self.assertTrue((folder / "expected" / "expected.json").is_file())
                self.assertTrue((folder / "check.py").is_file())
                text = (folder / "run.md").read_text(encoding="utf-8")
                paragraphs = [p for p in text.split("\n\n") if p.strip() and not p.startswith(("#", "    "))]
                self.assertEqual(len(paragraphs), 1, "run.md is one paragraph")
                self.assertRegex(paragraphs[0], r"\*\*Claim A[1-6]")
                self.assertIn("synthetic", text.lower())

    def test_expected_values_are_not_produced_by_the_pipeline(self):
        """The generator of the scenario files imports nothing of the pipeline."""
        text = (ROOT / "scenarios" / "make_inputs.py").read_text(encoding="utf-8")
        self.assertNotIn("dossier", [line.split()[1].split(".")[0] for line in text.split("\n")
                                     if line.startswith(("import ", "from "))])


if __name__ == "__main__":
    unittest.main()
