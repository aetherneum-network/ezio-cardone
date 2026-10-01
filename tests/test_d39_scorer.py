"""D39 (a), (d): the scorer reads where the pipeline writes, and a measurement that did not measure fails loudly.

Defect D1 of the blind run of v2.0.9 (run 22): eval/score.py read the build with plain paths. In a --work folder of
about 280 characters, on a machine without long-path support, every provenance file 'did not exist': the scorer
counted 0 fields, called every built entity 'failed', and exited 0 with an empty stderr (hand-22: fields exact 0/0,
blocked wrongly 10). Since v2.0.10 every reader of eval/, tools/ and scenarios/ takes the extended-length prefix
(jsonio.ext), and the scorer says MEASUREMENT FAILED (exit 3, stderr) when an entity the run reports as built cannot
be read, when the run built entities and no field was scored, when its counts disagree with the run's, or when an
entity of the gold is not in the run.

D39 (d): the audit's caches were keyed by id(rules); a freed rule set's id may be handed to the next one, so a process
that runs with two rule sets (this suite) could get the identification of the other set. They are keyed by the content
of the rules since v2.0.10."""
import contextlib
import copy
import dataclasses
import io
import json
import shutil
import unittest
from pathlib import Path
from unittest import mock

from . import ROOT
from . import support as s

from dossier import rules_engine, s7_audit
from dossier.lib import jsonio
from eval import score
from tools import rebuild


def deep(base: Path, length: int) -> Path:
    """A folder under ``base`` whose path is about ``length`` characters long, in parts of at most 40 characters."""
    p = base
    while len(str(p)) < length - 1:
        p = p / ("d" * min(40, length - len(str(p)) - 1))
    return p


def _copy_work(work: Path) -> Path:
    """A copy of a build folder, so that a test may break it without touching the shared build."""
    dst = s.tmp("ezio-d39-copy-") / "work"
    shutil.copytree(jsonio.ext(work), jsonio.ext(dst))
    return dst


def _first_ok(work: Path) -> str:
    report = jsonio.load(work / "run_report.json")
    return next(e for e, v in sorted(report["entities"].items()) if v["status"] == "OK")


class D39_ScorerReadsDeep(unittest.TestCase):
    """A build scored from a deep folder (about 280 characters) gives exactly what the same build gives from a short
    one: on v2.0.9 code the deep result was fields exact 0/0 and exit 0."""

    @classmethod
    def setUpClass(cls):
        base = s.corpus(24)
        cls.corpus, cls.gold = base / "input", base / "gold.json"
        cls.deep = deep(s.tmp("ezio-d39-deep-"), 280)
        cls.short = s.tmp("ezio-d39-short-")
        cls.r_deep = score.evaluate("deep", corpus=cls.corpus, gold_path=cls.gold, work=cls.deep)
        cls.r_short = score.evaluate("short", corpus=cls.corpus, gold_path=cls.gold, work=cls.short)

    def test_the_deep_folder_is_deep(self):
        longest = max(len(str(self.deep / "work" / p.relative_to(Path(jsonio.ext(self.deep / "work")))))
                      for p in Path(jsonio.ext(self.deep / "work")).rglob("*"))
        self.assertGreater(longest, 300)

    def test_a_deep_build_scores_the_same_as_a_short_one(self):
        self.assertEqual(self.r_deep["measurement"], {"status": "OK", "problems": []})
        self.assertEqual(self.r_short["measurement"], {"status": "OK", "problems": []})
        self.assertEqual(self.r_deep["metrics"], self.r_short["metrics"])
        self.assertEqual(self.r_deep["counts"], self.r_short["counts"])
        self.assertEqual(self.r_deep["run"], self.r_short["run"])
        self.assertGreater(self.r_deep["counts"]["published"], 0)
        self.assertGreater(self.r_deep["counts"]["fields_gold_fact"], 0)

    def test_a_generated_corpus_in_a_deep_folder_scores_the_same(self):
        # the mode of the blind run (--seed): the corpus is written, built and read under the deep folder
        a = score.evaluate("seed-deep", seed=s.DEV_SEED, entities=24, work=deep(s.tmp("ezio-d39-sdeep-"), 280))
        b = score.evaluate("seed-short", seed=s.DEV_SEED, entities=24, work=s.tmp("ezio-d39-sshort-"))
        self.assertEqual(a["measurement"]["status"], "OK", a["measurement"])
        self.assertEqual((a["metrics"], a["counts"]), (b["metrics"], b["counts"]))

    def test_rebuild_reads_a_deep_build_whole(self):
        self.assertEqual(rebuild.tree(self.deep / "work"), rebuild.tree(self.short / "work"))

    def test_rebuild_refuses_an_empty_walk(self):
        with self.assertRaises(rebuild.NothingRead):
            rebuild.tree(s.tmp("ezio-d39-empty-"))


class D39_ScorerFailsLoudly(unittest.TestCase):
    """A measurement that did not measure is FAILED, with its reason; on v2.0.9 code each of these was a quiet 0."""

    @classmethod
    def setUpClass(cls):
        cls.base, cls.work, _ = s.built(24)
        cls.gold = json.loads((cls.base / "gold.json").read_text(encoding="utf-8"))

    def _problems(self, work: Path, gold: dict | None = None) -> dict:
        return score.score(work, gold or self.gold)["measurement"]

    def test_a_clean_build_measures(self):
        self.assertEqual(self._problems(self.work), {"status": "OK", "problems": []})

    def test_an_entity_built_and_not_readable_fails_the_measurement(self):
        for mode in ("missing", "folder", "truncated"):
            with self.subTest(mode=mode):
                work = _copy_work(self.work)
                eid = _first_ok(work)
                prov = Path(jsonio.ext(work / "dossiers" / eid / "provenance.json"))
                if mode == "missing":
                    prov.unlink()
                elif mode == "folder":
                    prov.unlink()
                    prov.mkdir()
                else:
                    prov.write_bytes(prov.read_bytes()[:100])
                got = self._problems(work)
                self.assertEqual(got["status"], "FAILED")
                self.assertTrue(any("cannot be read" in p and eid in p for p in got["problems"]), got)

    def test_counts_that_disagree_with_the_run_fail_the_measurement(self):
        work = _copy_work(self.work)
        path = work / "run_report.json"
        report = jsonio.load(path)
        report["counts"]["OK"] += 1
        jsonio.write(path, report)
        got = self._problems(work)
        self.assertEqual(got["status"], "FAILED")
        self.assertTrue(any("differ from its own entity list" in p for p in got["problems"]), got)
        self.assertTrue(any("the scorer read" in p for p in got["problems"]), got)

    def test_nothing_scored_fails_the_measurement(self):
        gold = copy.deepcopy(self.gold)
        for g in gold["entities"].values():
            g["fields"] = {}
        got = self._problems(self.work, gold)
        self.assertEqual(got["status"], "FAILED")
        self.assertTrue(any("no field was scored" in p for p in got["problems"]), got)

    def test_an_entity_of_the_gold_missing_from_the_run_fails_the_measurement(self):
        gold = copy.deepcopy(self.gold)
        gold["entities"]["E-9999"] = copy.deepcopy(next(iter(gold["entities"].values())))
        got = self._problems(self.work, gold)
        self.assertEqual(got["status"], "FAILED")
        self.assertTrue(any("E-9999" in p and "not in the run" in p for p in got["problems"]), got)

    def test_the_command_exits_3_and_says_why_on_stderr(self):
        real = score.dossier_run.run
        hit = []

        def run(inp, w, *a, **k):
            code, report = real(inp, w, *a, **k)
            eid = next(e for e, v in sorted(report["entities"].items()) if v["status"] == "OK")
            Path(jsonio.ext(w)).joinpath("dossiers", eid, "provenance.json").unlink()
            hit.append(eid)
            return code, report

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(score.dossier_run, "run", run), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = score.main(["--corpus", str(self.base / "input"), "--gold", str(self.base / "gold.json"),
                               "--label", "forced", "--work", str(s.tmp("ezio-d39-forced-")),
                               "--json", str(s.tmp("ezio-d39-json-") / "r.json")])
        self.assertEqual(code, score.MEASUREMENT_FAILED)
        self.assertIn(f"MEASUREMENT FAILED - forced: 1 entities the run reports as built (status OK) cannot be read: "
                      f"{hit[0]} (no file)", err.getvalue())

    def test_a_run_that_raises_exits_3(self):
        err = io.StringIO()
        with mock.patch.object(score.dossier_run, "run", side_effect=OSError("disk gone")), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = score.main(["--corpus", str(self.base / "input"), "--gold", str(self.base / "gold.json"),
                               "--work", str(s.tmp("ezio-d39-raise-"))])
        self.assertEqual(code, score.MEASUREMENT_FAILED)
        self.assertIn("MEASUREMENT FAILED - OSError: disk gone", err.getvalue())


def _gazetteer_plus(street: str) -> rules_engine.Rules:
    base = rules_engine.load()
    extract = copy.deepcopy(base.extract)
    extract["parameters"]["gazetteer_street_name"] = extract["parameters"]["gazetteer_street_name"] + [street]
    return dataclasses.replace(base, extract=extract)


class D39_AuditCacheFollowsTheRules(unittest.TestCase):
    """The audit answers with the rule set it is given, whatever it was asked before in the same process."""

    def test_an_id_handed_to_another_rule_set_is_not_served_its_identification(self):
        # the allocator may give a freed Rules' id to the next one; a constant id() is the worst case of that
        a, b = rules_engine.load(), _gazetteer_plus("delle Prove Finte")
        with mock.patch.object(s7_audit, "id", lambda _o: 0, create=True):
            first = s7_audit._ident(a)
            second = s7_audit._ident(b)
        self.assertFalse(any(st.endswith(" delle Prove Finte") for st in first.streets))
        self.assertTrue(any(st.endswith(" delle Prove Finte") for st in second.streets))

    def test_two_rule_sets_alternating_in_one_process(self):
        wrong = 0
        for i in range(60):
            r = _gazetteer_plus("delle Prove Finte") if i % 2 else rules_engine.load()
            wrong += any(st.endswith(" delle Prove Finte") for st in s7_audit._ident(r).streets) != bool(i % 2)
            del r
        self.assertEqual(wrong, 0)

    def test_the_recognised_texts_follow_the_rules_on_the_same_input(self):
        inp = s.corpus(24) / "input"
        a = rules_engine.load()
        extract = copy.deepcopy(a.extract)
        extract["parameters"]["text_recognised"] = {g: [] for g in extract["parameters"]["text_recognised"]}
        b = dataclasses.replace(a, extract=extract)
        facts_a = {k for k, v in s7_audit.corpus_texts(inp, a).items() if v == "fact"}
        facts_b = {k for k, v in s7_audit.corpus_texts(inp, b).items() if v == "fact"}
        self.assertTrue(facts_a)
        self.assertEqual(facts_b, set())


if __name__ == "__main__":
    unittest.main()
