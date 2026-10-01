"""The command line says what happened: RUN OK only on exit 0; a run that published nothing is never 'OK'."""
import unittest

from . import ROOT
from . import support as s
from .support import mk

from dossier import run as runner
from dossier.lib import jsonio

SC = ROOT / "scenarios"


def _cli(*args):
    got = s.child(["-m", "dossier.run", *map(str, args)])
    return got.returncode, got.stdout.strip().split("\n"), got.stderr


class ExitCodes(unittest.TestCase):
    def test_ok(self):
        work = s.tmp()
        code, lines, err = _cli("--input", SC / "S01" / "input", "--work", work)
        self.assertEqual((code, lines[-1]), (0, "RUN OK"), err)
        self.assertEqual(lines[-2], "dossiers: 1 published, 0 BLOCKED, 0 FAILED (as of 2026-03-31)")
        self.assertEqual(jsonio.load(work / "run_report.json")["status"], "OK")

    def test_blocked(self):
        work = s.tmp()
        code, lines, err = _cli("--input", SC / "S02" / "input" / "percent", "--work", work)
        self.assertEqual(code, 2, err)
        self.assertEqual(lines[-1], "RUN BLOCKED - not everything was published")
        self.assertTrue(any("sums to 9999/10000, not to the whole" in line for line in lines))
        self.assertFalse(any(line == "RUN OK" for line in lines))
        self.assertEqual(list((work / "dossiers").glob("*/*.docx")) if (work / "dossiers").exists() else [], [])
        self.assertFalse((work / "shareable").exists())
        self.assertFalse((work / "_staging").exists())

    def test_failed_entity(self):
        rel, text = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"),
                            [("P-001", "100%")], ["P-001"])
        inp = s.tiny([(rel, text.replace(mk.MARKER, "An ordinary document."))])
        code, lines, err = _cli("--input", inp, "--work", s.tmp())
        self.assertEqual(code, 3, err)
        self.assertEqual(lines[-1], "RUN FAILED - not everything was published")
        self.assertIn("without the SYNTHETIC marker line", lines[0])

    def test_one_bad_entity_does_not_pass_silently_among_good_ones(self):
        base = s.corpus(24)
        inp = s.tmp()
        for p in (base / "input").rglob("*"):
            if p.is_file():
                jsonio.write_bytes(inp / p.relative_to(base / "input"), p.read_bytes())
        victim = sorted((inp / "entities").iterdir())[3]
        doc = sorted(victim.glob("*.txt"))[0]
        doc.write_bytes(doc.read_bytes().replace(mk.MARKER.encode(), b"An ordinary document."))
        work = s.tmp()
        code, out, report = s.run(inp, work)
        self.assertEqual(code, 3)
        self.assertEqual(report["entities"][victim.name]["status"], "FAILED")
        self.assertFalse((work / "dossiers" / victim.name).exists())
        self.assertGreater(report["counts"]["OK"], 10)
        self.assertTrue(out.strip().endswith("RUN FAILED - not everything was published"))


class RefusedBeforeAnythingIsBuilt(unittest.TestCase):
    def _no_config(self):
        """A deed and its identity layer, and no config.json (so no reference date). Since v2.0.7 (D36) the identity
        layer is part of what makes the deed publishable: a name beside a person identifier whose own name the corpus
        does not know leaves its line open (CLS-005), and its holders block."""
        rel, text = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"),
                            [("P-001", "100%")], ["P-001"])
        rel_id, text_id = mk.identity(["P-001"])
        return s.write_tree(s.tmp(), {rel: text, rel_id: text_id})

    def test_the_date_is_never_taken_from_the_clock(self):
        work = s.tmp()
        code, lines, err = _cli("--input", self._no_config(), "--work", work)
        self.assertEqual(code, 3, err)
        self.assertTrue(lines[-1].startswith("RUN FAILED - as_of is required"), lines)
        self.assertFalse((work / "dossiers").exists())
        with self.assertRaises(runner.RunError):
            runner.run(self._no_config(), s.tmp())

    def test_with_a_date_the_same_input_builds(self):
        code, lines, err = _cli("--input", self._no_config(), "--work", s.tmp(), "--as-of", "2026-06-30")
        self.assertEqual((code, lines[-1]), (0, "RUN OK"), err)

    def test_invalid_date(self):
        for bad in ("2026-13-40", "30/06/2026", "today"):
            code, lines, _ = _cli("--input", self._no_config(), "--work", s.tmp(), "--as-of", bad)
            self.assertEqual(code, 3, bad)
            self.assertTrue(lines[-1].startswith("RUN FAILED"), lines)

    def test_a_folder_with_nothing_to_build_is_not_a_success(self):
        for folder in (s.tmp(), s.tmp() / "does-not-exist"):
            code, lines, _ = _cli("--input", folder, "--work", s.tmp(), "--as-of", "2026-06-30")
            self.assertEqual(code, 3)
            self.assertTrue(lines[-1].startswith("RUN FAILED - nothing to build"), lines)

    def test_neither_input_nor_records(self):
        code, lines, _ = _cli("--work", s.tmp(), "--as-of", "2026-06-30")
        self.assertEqual(code, 3)
        self.assertTrue(lines[-1].startswith("RUN FAILED"), lines)


class Selection(unittest.TestCase):
    def test_only_the_named_entity_is_built(self):
        work = s.tmp()
        code, lines, err = _cli("--input", SC / "S08" / "input", "--work", work, "--entity", "E-0004")
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(p.name for p in (work / "dossiers").iterdir()), ["E-0004"])

    def test_an_entity_that_is_not_there_fails(self):
        code, lines, _ = _cli("--input", SC / "S01" / "input", "--work", s.tmp(), "--entity", "E-0099")
        self.assertEqual(code, 3)
        self.assertIn("E-0099 FAILED - no document of this entity in the input", lines)

    def test_diff_of_two_identical_runs_is_empty(self):
        a, b = s.tmp(), s.tmp()
        s.run(SC / "S01" / "input", a)
        s.run(SC / "S01" / "input", b)
        self.assertEqual(runner.diff_runs(a, b), [])


if __name__ == "__main__":
    unittest.main()
