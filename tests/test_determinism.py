"""The dossier is a build artefact: same inputs, same bytes - in another folder, in another process."""
import unittest
import zipfile

from . import ROOT
from . import support as s
from .support import mk

from corpus import generate
from dossier.lib import jsonio
from tools import assumptions, manifest


class SameBytes(unittest.TestCase):
    def test_two_builds_of_the_dev_corpus_in_different_folders(self):
        base, first, code = s.built(24)
        second = s.tmp("ezio-second-") / "a folder with spaces" / "più lunga" / ("x" * 60)
        code2, _, _ = s.run(base / "input", second)
        a, b = s.tree_hashes(first), s.tree_hashes(second)
        self.assertEqual(code, code2)
        self.assertEqual(a, b)
        self.assertGreater(sum(1 for f in a if f.endswith(".docx")), 30)

    def test_another_process_with_another_hash_seed(self):
        inp = ROOT / "scenarios" / "S07" / "input"
        runs = []
        for seed in ("1", "4242"):
            work = s.tmp()
            got = s.child(["-m", "dossier.run", "--input", str(inp), "--work", str(work)], PYTHONHASHSEED=seed)
            self.assertIn(got.returncode, (0, 2), got.stdout + got.stderr)
            runs.append(s.tree_hashes(work))
        here = s.tmp()
        s.run(inp, here)
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(runs[0], s.tree_hashes(here))
        self.assertTrue(any(f.endswith("dossier.docx") for f in runs[0]))

    def test_docx_container_carries_no_clock(self):
        _, work, _ = s.built(24)
        docx = sorted(work.rglob("*.docx"))[0]
        with zipfile.ZipFile(docx) as z:
            infos = z.infolist()
            self.assertEqual({i.date_time for i in infos}, {(2026, 9, 30, 0, 0, 0)})  # as_of of the input, not the clock
            self.assertEqual({(i.create_system, i.external_attr) for i in infos}, {(0, 0o600 << 16)})
            self.assertEqual(infos[0].filename, "[Content_Types].xml")
            core = z.read("docProps/core.xml").decode("utf-8")
        self.assertNotRegex(core, r"20\d\d-\d\d-\d\dT(?!00:00:00Z)")

    def test_rebuild_from_the_records_gives_the_same_dossier(self):
        """Claim A4: the record is the source of the build; the DOCX is never the master."""
        inp, work, _, _ = s.scenario_run("S03")
        again = s.tmp()
        code, _, _ = s.run(inp, again, records_dir=work / "records")
        self.assertEqual(code, 0)
        for name in ("dossier.docx", "provenance.json"):
            self.assertEqual(jsonio.sha256_file(work / "dossiers" / "E-0004" / name),
                             jsonio.sha256_file(again / "dossiers" / "E-0004" / name), name)


class Generators(unittest.TestCase):
    def test_dev_corpus_matches_its_manifest(self):
        files = generate.build_files(s.DEV_SEED)
        self.assertEqual(generate.check(files, ROOT / "corpus" / "MANIFEST.sha256", "dev"), [])
        self.assertEqual(files, generate.build_files(s.DEV_SEED))

    def test_corpus_check_can_fail(self):
        files = dict(generate.build_files(s.DEV_SEED, entities=6))
        self.assertTrue(generate.check(files, ROOT / "corpus" / "MANIFEST.sha256", "dev"))

    def test_every_generated_source_document_is_marked_synthetic(self):
        files = generate.build_files(s.DEV_SEED, entities=24)
        docs = {k: v for k, v in files.items() if k.startswith("input/entities/")}
        self.assertGreater(len(docs), 60)
        for name, data in docs.items():
            self.assertTrue(data.decode("utf-8").startswith(mk.MARKER + "\n"), name)
            self.assertIn(b"TEST-REG-", data, name)
            self.assertNotIn(b"\r", data, name)

    def test_scenario_files_are_what_make_inputs_says(self):
        self.assertEqual(mk.check(), [])

    def test_pack_manifest(self):
        self.assertEqual(manifest.check(), [])

    def test_assumptions_document_is_generated(self):
        self.assertEqual((ROOT / "docs" / "ASSUMPTIONS.md").read_bytes(), assumptions.render().encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
