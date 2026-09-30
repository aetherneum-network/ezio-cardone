"""Two layers: the structure can be shared, the identity data cannot. And the optional model hook stays off."""
import unittest

from . import ROOT
from . import support as s

from dossier import model_hook, s7_audit, s8_shareable
from dossier.lib import jsonio


class ShareableLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inp, cls.work, cls.code, _ = s.scenario_run("S08")
        cls.identity = jsonio.load(cls.inp / "identity" / "persons.json")
        cls.eid = jsonio.load(ROOT / "scenarios" / "S08" / "expected" / "expected.json")["entity"]
        cls.out = cls.work / "shareable" / cls.eid

    def test_nothing_of_the_identity_layer_leaks(self):
        self.assertEqual(self.code, 0)
        self.assertGreaterEqual(len(s8_shareable.identity_strings(self.identity)), 15)
        self.assertEqual(s8_shareable.leaks(self.out, self.identity), [])

    def test_the_leak_check_can_fail(self):
        """A control: the internal dossier does contain the names, and a planted one is found."""
        internal = s7_audit.read_docx(self.work / "dossiers" / self.eid / "dossier.docx")
        text = "\n".join(c for rows in internal["tables"].values() for r in rows for c in r)
        self.assertIn("Aldo Finti", text)
        out = s.tmp()
        for p in self.out.iterdir():
            jsonio.write_bytes(out / p.name, p.read_bytes())
        graph = jsonio.load(out / "graph.json")
        graph["note"] = "holder born 1961-02-03"
        jsonio.write(out / "graph.json", graph)
        self.assertEqual(s8_shareable.leaks(out, self.identity), ["1961-02-03"])
        graph["note"] = "see P-001"
        jsonio.write(out / "graph.json", graph)
        self.assertIn("person identifier pattern", s8_shareable.leaks(out, self.identity))

    def test_opaque_identifiers(self):
        a = s8_shareable.opaque("P-001", "salt-one")
        self.assertEqual(a, s8_shareable.opaque("P-001", "salt-one"))
        self.assertNotEqual(a, s8_shareable.opaque("P-001", "salt-two"))
        self.assertNotEqual(a, s8_shareable.opaque("P-002", "salt-one"))
        self.assertNotIn("P-001", a)
        self.assertNotRegex(a, r"P-\d{3}")

    def test_structure_is_kept(self):
        graph = jsonio.load(self.out / "graph.json")
        internal = jsonio.load(self.work / "views" / f"{self.eid}.json")
        self.assertEqual(len(graph["edges"]), len(internal["ownership"]["chain"]))
        self.assertEqual(sorted(e["share"] for e in graph["edges"]),
                         sorted(c["share"] for c in internal["ownership"]["chain"]))
        prov = jsonio.load(self.out / "provenance_shareable.json")
        self.assertEqual(prov["layer"], "shareable")
        for f in prov["figures"]:
            self.assertNotIn("quote", f)
            self.assertNotIn("source_file", f)
            self.assertTrue(f["source_doc"] and f["source_date"] and f["edition"])

    def test_no_shareable_layer_without_a_salt(self):
        inp = s.tmp()
        for p in self.inp.rglob("*"):
            if p.is_file() and p.name != "config.json":
                jsonio.write_bytes(inp / p.relative_to(self.inp), p.read_bytes())
        work = s.tmp()
        code, _, report = s.run(inp, work, "2026-06-30")
        self.assertFalse((work / "shareable").exists())
        self.assertNotEqual(report["entities"][self.eid].get("shareable", {}).get("status"), "OK")


class ModelHook(unittest.TestCase):
    def test_disabled_by_default(self):
        self.assertFalse(model_hook.ENABLED_BY_DEFAULT)
        calls = []
        hook = model_hook.ModelHook("claude-opus-5-5", lambda m, t: calls.append(m) or "DEED")
        with self.assertRaises(model_hook.ModelHookDisabled):
            hook.suggest_kind("any text")
        with self.assertRaises(model_hook.ModelHookDisabled):
            model_hook.ModelHook().suggest_kind("any text")
        with self.assertRaises(model_hook.ModelHookDisabled):
            model_hook.ModelHook("claude-opus-5-5", None, enabled=True).suggest_kind("any text")
        self.assertEqual(calls, [])

    def test_only_two_models_are_allowed(self):
        self.assertEqual(model_hook.ALLOWED_MODELS, ("claude-opus-5-5", "claude-fable-5-1"))
        for name in ("claude-sonnet-5", "gpt-x", "", "claude-opus-5-5 ", "CLAUDE-OPUS-5-5"):
            with self.assertRaises(model_hook.ModelNotAllowed):
                model_hook.ModelHook(name, lambda m, t: "DEED", enabled=True)

    def test_when_enabled_it_only_suggests_a_known_kind(self):
        seen = []
        hook = model_hook.ModelHook("claude-fable-5-1", lambda m, t: seen.append((m, t)) or " deed ", enabled=True)
        self.assertEqual(hook.suggest_kind("text"), "DEED")
        self.assertEqual(seen, [("claude-fable-5-1", "text")])
        odd = model_hook.ModelHook("claude-opus-5-5", lambda m, t: "The capital is EUR 1.000,00", enabled=True)
        self.assertEqual(odd.suggest_kind("text"), "UNKNOWN")

    def test_model_file_says_the_same(self):
        text = (ROOT / "MODEL.md").read_text(encoding="utf-8")
        for needle in ("claude-opus-5-5", "claude-fable-5-1", "disabled by default"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
