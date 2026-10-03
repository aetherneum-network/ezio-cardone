"""v2.0.15: the scenarios, the evaluation and the rebuild remove the temporary folders they make when they end."""
import os
import unittest

from . import ROOT
from . import support as s

HAND = ROOT / "eval" / "blind" / "hand-24"


class ToolsLeaveNoTemporaryFolder(unittest.TestCase):
    """Each command runs with a TEMP of its own, empty before it starts; when it ends, that folder must be empty again.
    Until v2.0.14 the three commands of the CI workflow left 24 folders there in one run (18, 1 and 5)."""

    COMMANDS = {
        "scenarios": ["scenarios/run_all.py"],
        "evaluation": ["-m", "eval.score", "--corpus", str(HAND / "input"), "--gold", str(HAND / "gold.json"),
                       "--label", "hand-24"],
        "rebuild": ["tools/rebuild.py", "--quick"],
    }

    def test_each_command_removes_what_it_made(self):
        for name, args in self.COMMANDS.items():
            with self.subTest(command=name):
                own = str(s.tmp("ezio-own-temp-"))
                got = s.child(args, TEMP=own, TMP=own, TMPDIR=own)
                self.assertEqual(got.returncode, 0, got.stdout + got.stderr)
                self.assertNotIn("not removed", got.stderr)
                self.assertEqual(os.listdir(own), [], name)


if __name__ == "__main__":
    unittest.main()
