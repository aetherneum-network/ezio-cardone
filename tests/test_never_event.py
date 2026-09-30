"""The never-event of this pack, attacked from every side.

Never-event: a figure rendered as fact in the dossier that differs from the gold or has no source.
Each test tries to make it happen and checks that the builder, the audit, the run or the scorer refuses.
"""
import copy
import json
import random
import unittest

from . import support as s
from .support import mk

from dossier import s3_discrepancy, s6_build, s7_audit
from dossier.lib import jsonio
from eval import score


def _valid_view() -> tuple[dict, dict]:
    inp, work, code, _ = s.scenario_run("S03")
    assert code == 0
    return jsonio.load(work / "views" / "E-0004.json"), jsonio.load(work / "records" / "E-0004.json")


class BuilderRefuses(unittest.TestCase):
    def setUp(self):
        self.view, _ = _valid_view()
        self.out = s.tmp()
        self.assumptions = s.rules().legal_assumptions()

    def _refused(self, view, exc=s6_build.BuildRefused):
        with self.assertRaises(exc):
            s6_build.build(view, self.out, "2026-06-30", self.assumptions)
        self.assertEqual(list(self.out.rglob("*")), [], "nothing may be written when the build is refused")

    def test_valid_view_builds(self):
        built = s6_build.build(self.view, self.out, "2026-06-30", self.assumptions)
        self.assertTrue(built["docx"].exists())

    def test_fact_without_each_source_key(self):
        for key in ("source_doc", "source_date", "edition"):
            for blank in ("", None):
                with self.subTest(key=key, blank=blank):
                    v = copy.deepcopy(self.view)
                    v["fields"]["share_capital.resolved"]["sources"][0][key] = blank
                    self._refused(v)
            with self.subTest(key=key, removed=True):
                v = copy.deepcopy(self.view)
                del v["fields"]["share_capital.resolved"]["sources"][0][key]
                self._refused(v)

    def test_fact_without_any_source(self):
        v = copy.deepcopy(self.view)
        v["fields"]["name"]["sources"] = []
        self._refused(v)

    def test_fact_citing_a_document_that_is_not_in_the_record(self):
        v = copy.deepcopy(self.view)
        v["fields"]["name"]["sources"][0]["source_doc"] = "DOC-E9999-01"
        self._refused(v)

    def test_cap_table_row_without_source(self):
        v = copy.deepcopy(self.view)
        v["fields"]["shareholders"]["sources"][0]["edition"] = ""
        self._refused(v)

    def test_history_row_without_source(self):
        v = copy.deepcopy(self.view)
        hist = v["fields"]["share_capital.resolved"]["historical"]
        self.assertTrue(hist)
        hist[0]["source_date"] = ""
        self._refused(v)

    def test_discrepancy_collapsed_to_one_value(self):
        inp, work, _, _ = s.scenario_run("S01")
        v = jsonio.load(work / "views" / "E-0001.json")
        one = copy.deepcopy(v)
        one["fields"]["share_capital.resolved"]["candidates"].pop()
        self._refused(one)
        chosen = copy.deepcopy(v)
        chosen["fields"]["share_capital.resolved"]["value"] = "80000.00"
        self._refused(chosen)
        unsourced = copy.deepcopy(v)
        unsourced["fields"]["share_capital.resolved"]["candidates"][0]["sources"] = []
        self._refused(unsourced)

    def test_to_confirm_filled_with_a_value(self):
        inp, work, _, _ = s.scenario_run("S10", "insufficient")
        v = jsonio.load(work / "views" / "E-0003.json")
        self.assertEqual(v["fields"]["share_capital.paid_in"]["status"], "TO_CONFIRM")
        v["fields"]["share_capital.paid_in"]["value"] = "250000.00"
        self._refused(v)

    def test_float_anywhere_in_the_view(self):
        v = copy.deepcopy(self.view)
        v["fields"]["share_capital.resolved"]["value"] = 120000.0
        self._refused(v)
        v = copy.deepcopy(self.view)
        v["ownership"]["table"][0]["share"] = 0.7
        self._refused(v)

    def test_amount_not_canonical(self):
        v = copy.deepcopy(self.view)
        v["fields"]["share_capital.resolved"]["value"] = "120.000,00"
        self._refused(v)

    def test_unknown_status(self):
        v = copy.deepcopy(self.view)
        v["fields"]["name"]["status"] = "PROBABLE"
        self._refused(v)

    def test_cap_table_that_does_not_sum_to_the_whole(self):
        v = copy.deepcopy(self.view)
        v["fields"]["shareholders"]["value"][0]["share"] = "69/100"
        self._refused(v, s6_build.BuildBlocked)
        v = copy.deepcopy(self.view)
        v["ownership"]["sum_checks"][0].update(sum="9999/10000", whole=False)
        self._refused(v, s6_build.BuildBlocked)


class AuditRefuses(unittest.TestCase):
    """The audit re-reads what was written; it does not trust the builder."""

    def setUp(self):
        self.view, self.record = _valid_view()
        self.inp = s.ROOT / "scenarios" / "S03" / "input"
        self.out = s.tmp()
        s6_build.build(self.view, self.out, "2026-06-30", s.rules().legal_assumptions())

    def _audit(self):
        return s7_audit.audit_dossier(self.out, self.inp, self.record)

    def _edit_provenance(self, change):
        prov = jsonio.load(self.out / "provenance.json")
        change(prov)
        jsonio.write(self.out / "provenance.json", prov)

    def test_untouched_build_passes(self):
        got = self._audit()
        self.assertEqual(got["problems"], [])
        self.assertEqual(got["figures_total"], got["figures_with_source"])

    def test_value_changed_after_the_build(self):
        def change(prov):
            f = next(f for f in prov["figures"] if f["field"] == "share_capital.resolved" and f["section"] == "facts")
            f["value"] = "130000.00"
            f["display"] = "EUR 130.000,00"
        self._edit_provenance(change)
        got = self._audit()
        self.assertFalse(got["ok"])
        self.assertTrue(any("not supported by the quoted source lines" in p for p in got["problems"]), got["problems"])

    def test_source_removed_after_the_build(self):
        self._edit_provenance(lambda prov: prov["figures"][0].update(source_doc=""))
        got = self._audit()
        self.assertFalse(got["ok"])
        self.assertLess(got["figures_with_source"], got["figures_total"])

    def test_quote_that_is_not_in_the_source(self):
        self._edit_provenance(lambda prov: prov["figures"][0].update(quote="Name: Another Company S.r.l."))
        self.assertFalse(self._audit()["ok"])

    def test_edition_swapped(self):
        self._edit_provenance(lambda prov: prov["figures"][0].update(edition="EXTRACT/9"))
        got = self._audit()
        self.assertTrue(any("date or edition differs" in p or "DOCX row" in p for p in got["problems"]), got["problems"])

    def test_source_document_changed_on_disk(self):
        inp = s.tmp()
        for p in self.inp.rglob("*"):
            if p.is_file():
                jsonio.write_bytes(inp / p.relative_to(self.inp), p.read_bytes())
        target = inp / "entities" / "E-0004" / "2026-01-12_registry-extract.txt"
        target.write_bytes(target.read_bytes().replace(b"120.000,00", b"125.000,00"))
        got = s7_audit.audit_dossier(self.out, inp, self.record)
        self.assertTrue(any("changed since the record was built" in p for p in got["problems"]), got["problems"])

    def test_conflict_shown_as_one_fact(self):
        inp, work, _, _ = s.scenario_run("S01")
        record = jsonio.load(work / "records" / "E-0001.json")
        out = s.tmp()
        for name in ("dossier.docx", "provenance.json"):
            jsonio.write_bytes(out / name, (work / "dossiers" / "E-0001" / name).read_bytes())
        prov = jsonio.load(out / "provenance.json")
        for f in prov["figures"]:
            if f["field"] == "share_capital.resolved" and f["value"] == "80000.00":
                f["section"], f["status"] = "facts", "STATED"
        prov["figures"] = [f for f in prov["figures"]
                           if not (f["field"] == "share_capital.resolved" and f["value"] == "50000.00")]
        jsonio.write(out / "provenance.json", prov)
        got = s7_audit.audit_dossier(out, inp, record)
        self.assertTrue(any("sources disagree but one value is shown as fact" in p for p in got["problems"]),
                        got["problems"])

    def test_docx_row_edited_by_hand(self):
        from docx import Document
        path = self.out / "dossier.docx"
        doc = Document(str(path))
        cell = next(c for t in doc.tables for r in t.rows for c in r.cells if c.text == "EUR 120.000,00")
        cell.text = "EUR 210.000,00"
        doc.save(str(path))
        got = self._audit()
        self.assertTrue(any("DOCX value differs from provenance" in p for p in got["problems"]), got["problems"])


class RunRefuses(unittest.TestCase):
    def test_unmarked_source_document_fails_the_run(self):
        rel, text = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"),
                            [("P-001", "100%")], ["P-001"])
        inp = s.tiny([(rel, text.replace(mk.MARKER + "\n", ""))])
        work = s.tmp()
        code, out, report = s.run(inp, work)
        self.assertEqual(code, 3)
        self.assertEqual(report["entities"]["E-0001"]["status"], "FAILED")
        self.assertNotIn("RUN OK", out)
        self.assertFalse((work / "dossiers" / "E-0001" / "dossier.docx").exists())

    def test_a_failed_write_is_a_failed_run(self):
        inp = s.ROOT / "scenarios" / "S01" / "input"
        real = jsonio.write_bytes

        def failing(path, data, **kw):
            if str(path).endswith("provenance.json"):
                raise jsonio.WriteFailed("write verification failed for provenance.json")
            return real(path, data, **kw)

        jsonio.write_bytes = failing
        try:
            work = s.tmp()
            code, out, report = s.run(inp, work)
        finally:
            jsonio.write_bytes = real
        self.assertEqual(code, 3)
        self.assertTrue(out.strip().split("\n")[-1].startswith("RUN FAILED"))
        self.assertIn("WriteFailed", report["entities"]["E-0001"]["reason"])
        self.assertFalse((work / "dossiers" / "E-0001").exists())

    def test_two_files_under_one_document_id_fail_the_run(self):
        h = [("P-001", "60%"), ("P-002", "40%")]
        one = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"), h, ["P-001"])
        two = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_B, mk.FULL.format(a="60.000,00"), h, ["P-001"])
        work = s.tmp()
        code, out, report = s.run(s.tiny([one, (two[0].replace("_deed", "_deed_copy"), two[1])]), work)
        self.assertEqual((code, report["entities"]["E-0001"]["status"]), (3, "FAILED"))
        self.assertIn("document id DOC-E0001-01 is already used", report["entities"]["E-0001"]["reason"])
        self.assertFalse((work / "dossiers").exists())

    def test_record_with_a_float_is_refused(self):
        _, record = _valid_view()
        bad = s.tmp()
        text = jsonio.dumps(record).replace('"value": "120000.00"', '"value": 120000.00', 1)
        self.assertIn('"value": 120000.00', text)
        jsonio.write_text(bad / "E-0004.json", text)
        work = s.tmp()
        code, _, report = s.run(s.ROOT / "scenarios" / "S03" / "input", work, records_dir=bad)
        self.assertEqual((code, report["entities"]["E-0004"]["status"]), (3, "FAILED"))
        self.assertIn("floating-point", report["entities"]["E-0004"]["reason"])


def _assertion(i, role, series, date, value, no):
    a = {"field": "f", "role": role, "series": series, "edition_no": no, "source_doc": f"D{i:02d}",
         "source_file": f"D{i:02d}.txt", "source_date": date, "edition": f"{series}/{no}", "line": 1,
         "line_end": 1, "quote": "q", "nature": "resolved", "rule": "T"}
    if value is None:
        a.update(status="TO_CONFIRM", reason="unreadable")
    else:
        a.update(status="STATED", value=value)
    return a


class ResolutionNeverInvents(unittest.TestCase):
    """4000 random sets of assertions: a fact only when every current source is readable and agrees.

    The sets are small and the dates few on purpose: same-day events and twice-issued editions are frequent.
    """

    def test_random_assertion_sets(self):
        rng = random.Random(20260930)
        rules = s.rules()
        dates = ["2026-01-10", "2026-02-10", "2026-03-10", "2026-04-10"]
        seen = {"STATED": 0, "DISCREPANCY": 0, "TO_CONFIRM": 0}
        ties = 0
        for _ in range(4000):
            n = rng.randint(1, 6)
            assertions = []
            for i in range(n):
                role = rng.choice(["event", "state", "state"])
                series = rng.choice(["DEED", "RESOLUTION"]) if role == "event" else rng.choice(["EXTRACT", "LEDGER"])
                value = rng.choice([None, "50000.00", "80000.00", "80000.00", "120000.00"])
                assertions.append(_assertion(i, role, series, rng.choice(dates), value, rng.randint(1, 2)))
            unread = [{"doc_id": "DX", "date": rng.choice(dates)}] if rng.random() < 0.15 else []
            got = s3_discrepancy.resolve_field("f", assertions, rules, unread)
            seen[got["status"]] += 1

            # an oracle written here from the declared semantics, as sets: no ordering, no tie-break
            events = [a for a in assertions if a["role"] == "event"]
            day = max((a["source_date"] for a in events), default=None)
            current = [a for a in events if a["source_date"] == day]
            ties += len(current) > 1
            for name in sorted({a["series"] for a in assertions if a["role"] == "state"}):
                mine = [a for a in assertions if a["role"] == "state" and a["series"] == name]
                top = max((a["source_date"], a["edition_no"]) for a in mine)
                if day is None or top[0] >= day:
                    current += [a for a in mine if (a["source_date"], a["edition_no"]) == top]
            values = {a["value"] for a in current if a["status"] == "STATED"}
            blocked = any(day is None or u["date"] >= day for u in unread)
            if blocked or not current:
                want = "TO_CONFIRM"
            elif len(values) >= 2:
                want = "DISCREPANCY"
            elif any(a["status"] != "STATED" for a in current):
                want = "TO_CONFIRM"
            else:
                want = "STATED"
            self.assertEqual(got["status"], want, (assertions, unread))
            if got["status"] == "STATED":
                self.assertEqual({got["value"]}, values)
                self.assertTrue(got["sources"])
                self.assertTrue(all(src["source_doc"] and src["source_date"] and src["edition"]
                                    for src in got["sources"]))
            else:
                self.assertNotIn("value", got)
            if got["status"] == "DISCREPANCY":
                self.assertEqual({c["value"] for c in got["candidates"]}, values)
        self.assertTrue(all(seen.values()), seen)
        self.assertGreater(ties, 300)

    def test_same_day_events_that_disagree_are_shown_side_by_side(self):
        a = _assertion(1, "event", "RESOLUTION", "2026-03-10", "80000.00", 1)
        b = _assertion(2, "event", "RESOLUTION", "2026-03-10", "90000.00", 2)
        for pair in ([a, b], [b, a]):
            got = s3_discrepancy.resolve_field("f", pair, s.rules(), [])
            self.assertEqual(got["status"], "DISCREPANCY")
            self.assertEqual([c["value"] for c in got["candidates"]], ["80000.00", "90000.00"])

    def test_the_same_edition_issued_twice_with_two_values(self):
        a = _assertion(1, "state", "EXTRACT", "2026-03-10", "80000.00", 3)
        b = _assertion(2, "state", "EXTRACT", "2026-03-10", "90000.00", 3)
        got = s3_discrepancy.resolve_field("f", [a, b], s.rules(), [])
        self.assertEqual(got["status"], "DISCREPANCY")
        b["status"] = "TO_CONFIRM"; b["reason"] = "unreadable"; del b["value"]
        got = s3_discrepancy.resolve_field("f", [a, b], s.rules(), [])
        self.assertEqual((got["status"], "value" in got), ("TO_CONFIRM", False))


class UnreadSourcesNeverBecomeFacts(unittest.TestCase):
    def _fields(self, docs, as_of="2026-06-30"):
        work = s.tmp()
        code, _, _ = s.run(s.tiny(docs, as_of), work)
        view = jsonio.load(work / "views" / "E-0001.json")
        prov = jsonio.load(work / "dossiers" / "E-0001" / "provenance.json")
        return code, view["fields"], prov

    def test_unknown_document_type_after_the_deed_blocks_every_fact(self):
        h = [("P-001", "60%"), ("P-002", "40%")]
        deed = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"), h, ["P-001"])
        rel, text = mk.resolution("E-0001", 2, "2026-01-15",
                                  "The meeting resolved to increase the share capital from EUR 50.000,00 to "
                                  "EUR 80.000,00. The increase has been fully subscribed and fully paid in.")
        unknown = (rel, text.replace("Resolution on share capital", "Minutes about the capital"))
        code, fields, prov = self._fields([deed, unknown])
        self.assertEqual(code, 0)
        self.assertEqual({f["status"] for f in fields.values()}, {"TO_CONFIRM"})
        self.assertEqual([f for f in prov["figures"] if f["section"] in ("facts", "cap_table")], [])
        self.assertTrue(all(t["marker"] == "[TO CONFIRM]" and "value" not in t for t in prov["to_confirm"]))

    def test_illegible_latest_event_does_not_promote_the_older_value(self):
        h = [("P-001", "60%"), ("P-002", "40%")]
        deed = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"), h, ["P-001"])
        res = mk.resolution("E-0001", 2, "2026-01-15",
                            "The meeting resolved to increase the share capital from EUR 50.000,00 to "
                            "EUR 8#.###,00. The increase has been fully subscribed and fully paid in.")
        code, fields, prov = self._fields([deed, res])
        self.assertEqual(fields["share_capital.resolved"]["status"], "TO_CONFIRM")
        shown = [f for f in prov["figures"] if f["field"] == "share_capital.resolved" and f["section"] == "facts"]
        self.assertEqual(shown, [])

    def test_one_unreadable_current_source_blocks_the_other(self):
        h = [("P-001", "60%"), ("P-002", "40%")]
        deed = mk.deed("E-0001", 1, "2025-03-10", mk.OFFICE_A, mk.FULL.format(a="50.000,00"), h, ["P-001"])
        ext = mk.extract("E-0001", 2, "2026-02-02", 1, mk.OFFICE_A,
                         "Share capital: resolved EUR [illegible]; subscribed and paid in EUR 50.000,00", h, ["P-001"])
        code, fields, prov = self._fields([deed, ext])
        self.assertEqual(fields["share_capital.resolved"]["status"], "TO_CONFIRM")
        self.assertEqual([c["value"] for c in fields["share_capital.resolved"]["readable"]], ["50000.00"])
        self.assertEqual(fields["share_capital.paid_in"]["status"], "STATED")
        rows = [f for f in prov["figures"] if f["field"] == "share_capital.resolved"]
        self.assertTrue(rows and all(f["section"] in ("unconfirmed", "history") for f in rows))


class ScorerSeesNeverEvents(unittest.TestCase):
    """The instrument that counts never-events must be able to count one."""

    @classmethod
    def setUpClass(cls):
        cls.base, cls.work, cls.code = s.built(24)
        cls.gold = json.loads((cls.base / "gold.json").read_text(encoding="utf-8"))

    def test_clean_run_has_none(self):
        got = score.score(self.work, self.gold)
        self.assertEqual(got["metrics"]["never_events"], 0, got["never_event_list"])
        self.assertGreater(got["counts"]["fact_exact"], 100)

    def _first_fact(self, gold):
        for eid, g in sorted(gold["entities"].items()):
            if g["build"] == "OK" and g["fields"].get("share_capital.resolved", {}).get("status") == "FACT":
                return eid
        self.fail("no entity with a capital fact in the small corpus")

    def test_gold_changed_under_a_published_fact(self):
        gold = copy.deepcopy(self.gold)
        eid = self._first_fact(gold)
        gold["entities"][eid]["fields"]["share_capital.resolved"]["value"] = "1.00"
        got = score.score(self.work, gold)
        self.assertEqual(got["metrics"]["never_events"], 1, got["never_event_list"])

    def test_published_fact_changed_under_the_gold(self):
        eid = self._first_fact(self.gold)
        work = s.tmp()
        for rel in ("run_report.json",):
            jsonio.write_bytes(work / rel, (self.work / rel).read_bytes())
        for p in (self.work / "dossiers").rglob("provenance.json"):
            jsonio.write_bytes(work / p.relative_to(self.work), p.read_bytes())
        path = work / "dossiers" / eid / "provenance.json"
        prov = jsonio.load(path)
        fig = next(f for f in prov["figures"] if f["field"] == "share_capital.resolved" and f["section"] == "facts")
        fig["value"] = "1.00"
        jsonio.write(path, prov)
        self.assertEqual(score.score(work, self.gold)["metrics"]["never_events"], 1)
        fig["value"], fig["source_doc"] = self.gold["entities"][eid]["fields"]["share_capital.resolved"]["value"], ""
        jsonio.write(path, prov)
        self.assertGreaterEqual(score.score(work, self.gold)["metrics"]["never_events"], 1)

    def test_blocked_entity_published_anyway(self):
        gold = copy.deepcopy(self.gold)
        eid = self._first_fact(gold)
        gold["entities"][eid]["build"] = "BLOCKED"
        self.assertEqual(score.score(self.work, gold)["metrics"]["never_events"], 1)

    def test_conflict_in_gold_shown_as_one_value(self):
        gold = copy.deepcopy(self.gold)
        eid = self._first_fact(gold)
        f = gold["entities"][eid]["fields"]["share_capital.resolved"]
        f.update(status="DISCREPANCY", values=[f.pop("value"), "1.00"])
        self.assertEqual(score.score(self.work, gold)["metrics"]["never_events"], 1)

    def test_unreadable_in_gold_shown_with_a_value(self):
        gold = copy.deepcopy(self.gold)
        eid = self._first_fact(gold)
        gold["entities"][eid]["fields"]["share_capital.resolved"] = {"status": "TO_CONFIRM", "superseded": []}
        self.assertEqual(score.score(self.work, gold)["metrics"]["never_events"], 1)


if __name__ == "__main__":
    unittest.main()
