"""D38 (d): Windows long paths. A build in a work folder of about 230 characters, and the folder shape of
``tests/test_determinism.py`` under a TEMP of about 100 characters, succeed on a machine without long-path support:
every file call of a build goes through ``jsonio.ext`` (the ``\\\\?\\`` prefix on Windows). On other systems the
same tests run and pass with plain paths."""
import os
import tempfile
import unittest
from pathlib import Path

from . import ROOT
from . import support as s

from dossier.lib import jsonio

SCENARIO = ROOT / "scenarios" / "S07" / "input"


def deep(base: Path, length: int) -> Path:
    """A folder under ``base`` whose path is about ``length`` characters long, in parts of at most 40 characters."""
    p = base
    while len(str(p)) < length - 1:
        p = p / ("d" * min(40, length - len(str(p)) - 1))
    return p


# the longest path a build writes: the container of the shareable DOCX while it is normalised, in the staging folder
STAGED = "/_staging/E-0000/shareable/dossier_shareable.docx.norm"


def longest(root: Path, hashes: dict[str, str]) -> int:
    return max(len(str(root)) + 1 + len(rel) for rel in hashes)


class D38_LongPaths(unittest.TestCase):
    def test_a_build_in_a_work_folder_of_230_characters(self):
        work = deep(s.tmp("ezio-lp-"), 230)
        self.assertGreaterEqual(len(str(work)), 228)
        code, out, report = s.run(SCENARIO, work)
        self.assertIn(code, (0, 2), out)
        self.assertNotIn("WinError", out)
        self.assertFalse([e for e, v in report["entities"].items() if v["status"] == "FAILED"], out)
        here = s.tmp()
        code2, _, _ = s.run(SCENARIO, here)
        deep_hashes = s.tree_hashes(work)
        self.assertEqual(code, code2)
        self.assertEqual(deep_hashes, s.tree_hashes(here))
        self.assertTrue(any(f.endswith("dossier.docx") for f in deep_hashes))
        self.assertGreater(longest(work, deep_hashes), 260)

    def test_the_determinism_folder_shape_under_a_temp_of_100_characters(self):
        temp = deep(s.tmp("ezio-lt-"), 100)
        os.makedirs(jsonio.ext(temp), exist_ok=True)
        old = tempfile.tempdir
        tempfile.tempdir = str(temp)
        try:
            second = s.tmp("ezio-second-") / "a folder with spaces" / "più lunga" / ("x" * 60)
        finally:
            tempfile.tempdir = old
        first = s.tmp()
        code, _, _ = s.run(SCENARIO, first)
        code2, out, report = s.run(SCENARIO, second)
        self.assertEqual(code, code2, out)
        self.assertFalse([e for e, v in report["entities"].items() if v["status"] == "FAILED"], out)
        a, b = s.tree_hashes(first), s.tree_hashes(second)
        self.assertEqual(a, b)
        self.assertGreater(len(str(second)) + len(STAGED), 260)


if __name__ == "__main__":
    unittest.main()
