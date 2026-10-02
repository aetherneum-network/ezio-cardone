"""What the repository contains: synthetic data only, no internal reference, the declared files, LF and UTF-8."""
import hashlib
import re
import unittest

from . import ROOT
from . import support as s
from .support import mk

SKIP_DIRS = {".git", "build", "__pycache__", "out"}
BINARY = {".jpg", ".docx", ".png"}
ME = "tests/test_hygiene.py"

# the profile text that existed before this proof pack (commit c1859cb), from its first heading to the end
# The text changed in PR #1 (week-1 review, merge commit 468cbd6 on main), not in the pack: hash of the reviewed text.
PROFILE_SHA256 = "66c476bed24befcec8f9f57a075f1f88b3ed3bf9b7929a74d886e5b4a3c34529"
BANNER_START = "**SYNTHETIC - Ezio Cardone is a synthetic alumnus (an AI agent) of Aetherneum University, not a person"


def _files():
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if p.is_file() and not (set(rel.parts[:-1]) & SKIP_DIRS) and p.suffix != ".pyc":
            yield rel.as_posix(), p


def _texts():
    for rel, p in _files():
        if p.suffix not in BINARY:
            yield rel, p.read_bytes()


class TextFiles(unittest.TestCase):
    def test_utf8_and_lf(self):
        for rel, data in _texts():
            with self.subTest(file=rel):
                data.decode("utf-8")
                self.assertNotIn(b"\r", data)
                self.assertFalse(data.startswith(b"\xef\xbb\xbf"), "no byte-order mark")

    def test_no_internal_path_machine_or_private_name(self):
        """Patterns are assembled here so that this file does not contain them either."""
        drive = "[A-Za-z]:" + r"[\\/]" + r"(?:Users|Windows|Program)"
        unix = r"/(?:opt|home|var|srv|mnt|root|Users)/" + r"[A-Za-z]"
        names = "|".join(["line" + "work", "global" + "master", "crypto" + "host", "desk" + "top", "app" + "data",
                          "scratch" + "pad", "one" + "drive"])
        ipv4 = r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.,])"
        documentation_net = re.compile(r"^198\.51\.100\.\d+$")
        for rel, data in _texts():
            text = data.decode("utf-8")
            with self.subTest(file=rel):
                self.assertIsNone(re.search(drive, text), "drive path")
                self.assertIsNone(re.search(unix, text), "absolute path")
                self.assertIsNone(re.search(names, text, re.IGNORECASE), "internal name")
                self.assertEqual([ip for ip in re.findall(ipv4, text) if not documentation_net.match(ip)], [])

    def test_mail_domains(self):
        allowed = {"persons.example", "aetherneum.com", "anthropic.com"}
        mail = re.compile(r"[A-Za-z0-9._+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
        for rel, data in _texts():
            for domain in mail.findall(data.decode("utf-8")):
                self.assertTrue(domain in allowed or domain.endswith(".example"), f"{rel}: {domain}")

    def test_no_credential_shaped_string(self):
        shapes = re.compile(r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY")
        for rel, data in _texts():
            self.assertIsNone(shapes.search(data.decode("utf-8")), rel)

    def test_links_outside_the_profile(self):
        """The pack itself links nowhere; the only links are the ones of the pre-existing profile."""
        for rel, data in _texts():
            if rel in ("README.md", "schema/entity_record.schema.json", ".github/workflows/ci.yml"):
                continue
            self.assertIsNone(re.search(r"https?://", data.decode("utf-8")), rel)


class SyntheticOnly(unittest.TestCase):
    def test_every_source_document_of_the_scenarios_is_marked(self):
        docs = [(rel, p) for rel, p in _files() if rel.startswith("scenarios/") and "/entities/" in rel]
        self.assertGreater(len(docs), 30)
        for rel, p in docs:
            text = p.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(mk.MARKER + "\n"), rel)
            self.assertRegex(text, r"test registry no\. TEST-REG-\d{6}", rel)

    def test_identifiers_cannot_be_mistaken_for_real_ones(self):
        tax = re.compile(r'"tax_code": "([^"]*)"')
        seen = 0
        for rel, data in _texts():
            if rel == ME:
                continue
            for code in tax.findall(data.decode("utf-8")):
                seen += 1
                self.assertRegex(code, r"^SYN-CF-P\d{3}$", rel)
        self.assertGreater(seen, 10)
        world = (ROOT / "corpus" / "world.py").read_text(encoding="utf-8")
        self.assertIn("SYN-", world)
        self.assertIn("(ZZ)", world)

    def test_only_the_four_scenario_companies_and_generated_names(self):
        self.assertEqual(sorted(mk.ENT), ["E-0001", "E-0002", "E-0003", "E-0004"])
        text = " ".join((ROOT / "SYNTHETIC.md").read_text(encoding="utf-8").split())
        for name, _ in mk.ENT.values():
            self.assertIn(name, text)


class DeclaredFiles(unittest.TestCase):
    def test_required_files_exist(self):
        for rel in ("SYNTHETIC.md", "CLAIMS.md", "MODEL.md", "CHANGELOG.md", "requirements.txt", "LICENSE",
                    ".github/workflows/ci.yml", "MANIFEST.sha256", "docs/ASSUMPTIONS.md", "eval/history.json",
                    "eval/score.py", "scenarios/run_all.py", "corpus/MANIFEST.sha256", "rules/extract.json",
                    "schema/entity_record.schema.json"):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_readme_opens_with_the_banner_and_the_proof_pack(self):
        lines = (ROOT / "README.md").read_text(encoding="utf-8").split("\n")
        self.assertTrue(lines[0].startswith(BANNER_START))
        heads = [line for line in lines if line.startswith("# ")]
        self.assertEqual(heads[:2], ["# Proof pack v2.0", "# Ezio Cardone"])

    def test_the_profile_text_is_untouched(self):
        """Nothing of the pre-existing profile was edited or removed - the sentence on "the platform" included."""
        data = (ROOT / "README.md").read_bytes()
        start = data.index(b"\n# Ezio Cardone\n") + 1
        self.assertEqual(hashlib.sha256(data[start:]).hexdigest(), PROFILE_SHA256)
        self.assertEqual(data.count(b"Ezio is the platform's Legal-Entity Dossier Architect."), 1)

    def test_proof_pack_section_says_what_it_must(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        pack = text[text.index("# Proof pack v2.0"):text.index("\n# Ezio Cardone\n")]
        for needle in ("synthetic AI agent", "not a lawyer", "notary", "accountant", "auditor", "not legal advice",
                       "[TO CONFIRM with legal]", "internal consistency", "NOT demonstrated", "Windows only",
                       "python -m unittest discover -s tests -t .", "python scenarios/run_all.py",
                       "seed 20260930", "as of 2026-09-30", "SHA-256", "statutory"):
            self.assertIn(needle, pack)
        self.assertLessEqual(len(re.findall(r"^    python ", pack, re.MULTILINE)), 5, "under five commands")
        self.assertIsNone(re.search(r"https?://", pack))

    def test_the_never_event_definition_is_the_scorers(self):
        """D29 (v2.0.2): the README states the never-event with the list that eval/score.py counts, word for word."""
        doc = (ROOT / "eval" / "score.py").read_text(encoding="utf-8").split('"""')[1]
        kinds = re.findall(r"^\* (.+?)[;.]$", doc, re.MULTILINE)
        self.assertEqual(len(kinds), 8, kinds)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        pack = readme[readme.index("# Proof pack v2.0"):readme.index("\n# Ezio Cardone\n")]
        for kind in kinds:
            self.assertIn(f"- {kind}", pack)

    def test_claims_file(self):
        text = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
        for claim in ("A1", "A2", "A3", "A4", "A5", "A6"):
            self.assertIn(f"| {claim} |", text)
        for sid in (f"S{n:02d}" for n in range(1, 11)):
            self.assertIn(sid, text)
        for rel in set(re.findall(r"`((?:tests|scenarios|dossier|rules|eval|docs|corpus|tools)/[\w./-]+)`", text)):
            self.assertTrue((ROOT / rel).exists(), rel)
        self.assertIn("not demonstrated: out of v2.0", text)
        self.assertIn("awaiting legal review — not touched", text)
        self.assertRegex(text, r"(?i)statutory")

    def test_requirements_are_pinned_with_hashes(self):
        text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        reqs = [b for b in re.split(r"\n(?=[A-Za-z])", text) if re.match(r"[A-Za-z]", b)]
        names = sorted(r.split("==")[0].lower() for r in reqs)
        self.assertEqual(names, ["attrs", "jsonschema", "jsonschema-specifications", "lxml", "python-docx",
                                 "referencing", "rpds-py", "typing-extensions"])
        for r in reqs:
            self.assertRegex(r, r"^[A-Za-z0-9_-]+==\d+(\.\d+)+ \\\n", r)
            self.assertGreaterEqual(len(re.findall(r"--hash=sha256:[0-9a-f]{64}", r)), 1, r)

    def test_installed_versions_are_the_pinned_ones(self):
        from importlib import metadata
        text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        for name, version in re.findall(r"^([A-Za-z0-9_-]+)==([\d.]+)", text, re.MULTILINE):
            self.assertEqual(metadata.version(name), version, name)

    def test_ci_workflow_is_offline_after_install(self):
        text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("--require-hashes", text)
        self.assertIn("python -m unittest discover -s tests -t .", text)
        self.assertIn("python scenarios/run_all.py", text)
        self.assertIn("contents: read", text)
        self.assertNotRegex(text, r"(?i)secrets\.|api[_-]?key|curl |wget ")
        self.assertEqual(len(re.findall(r"pip install", text)), 1)

    def test_no_statutory_calendar_is_implemented(self):
        for rel, _ in _files():
            if rel.startswith(("dossier/", "rules/", "schema/")):
                self.assertNotRegex(rel, r"(?i)calendar|deadline|obligation")
        text = "".join((ROOT / "rules" / f).read_text(encoding="utf-8") for f in
                       ("extract.json", "figure_nature.json", "discrepancy.json", "ownership.json"))
        self.assertNotRegex(text, r"(?i)deadline|filing date|due date")

    def test_history_keeps_the_bad_first_runs(self):
        from dossier.lib import jsonio
        runs = jsonio.load(ROOT / "eval" / "history.json")["runs"]
        self.assertGreaterEqual(len(runs), 4)
        self.assertEqual([r["n"] for r in runs], list(range(1, len(runs) + 1)))
        text = jsonio.dumps(runs)
        self.assertIn('"never_events": 32', text)


if __name__ == "__main__":
    unittest.main()
