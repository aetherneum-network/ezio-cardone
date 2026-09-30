"""Snapshots are appended, never overwritten; any alteration of the store is detected."""
import unittest

from . import support as s

from dossier.lib import jsonio
from dossier.s5_snapshot import GENESIS, SnapshotStore


class Store(unittest.TestCase):
    def setUp(self):
        self.dir = s.tmp("ezio-store-")
        self.store = SnapshotStore(self.dir)
        self.a, made = self.store.append("E-0001", "2026-01-31", {"capital": "50000.00"})
        self.assertTrue(made)
        self.b, made = self.store.append("E-0001", "2026-03-31", {"capital": "80000.00"})
        self.assertTrue(made)

    def test_answers_by_date(self):
        self.assertIsNone(self.store.at("E-0001", "2026-01-30"))
        self.assertEqual(self.store.at("E-0001", "2026-01-31")["snapshot"]["payload"], {"capital": "50000.00"})
        self.assertEqual(self.store.at("E-0001", "2026-03-30")["as_of"], "2026-01-31")
        self.assertEqual(self.store.at("E-0001", "2026-12-31")["snapshot"]["payload"], {"capital": "80000.00"})
        self.assertIsNone(self.store.at("E-0002", "2026-12-31"))

    def test_same_content_is_not_written_twice(self):
        entry, made = self.store.append("E-0001", "2026-06-30", {"capital": "80000.00"})
        self.assertFalse(made)
        self.assertEqual(entry["seq"], 2)
        self.assertEqual(len(self.store.entries()), 2)

    def test_a_correction_for_a_past_date_is_a_new_snapshot(self):
        first = (self.dir / self.a["file"]).read_bytes()
        entry, made = self.store.append("E-0001", "2026-01-31", {"capital": "55000.00"})
        self.assertTrue(made)
        self.assertEqual(entry["seq"], 3)
        self.assertEqual((self.dir / self.a["file"]).read_bytes(), first)
        self.assertEqual(self.store.at("E-0001", "2026-01-31")["snapshot"]["payload"], {"capital": "55000.00"})
        self.assertEqual(self.store.verify(), [])

    def test_an_existing_snapshot_file_is_never_replaced(self):
        collide = self.dir / "E-0001" / "2026-06-30__0003.json"
        jsonio.write_text(collide, "already here\n")
        with self.assertRaises(FileExistsError):
            self.store.append("E-0001", "2026-06-30", {"capital": "90000.00"})
        self.assertEqual(collide.read_text(encoding="utf-8"), "already here\n")
        self.assertEqual(len(self.store.entries()), 2)

    def test_chain(self):
        self.assertEqual(self.a["prev_hash"], GENESIS)
        self.assertEqual(self.b["prev_hash"], self.a["entry_hash"])
        self.assertEqual(self.store.verify(), [])

    def test_changed_snapshot_is_detected(self):
        path = self.dir / self.a["file"]
        path.write_bytes(path.read_bytes().replace(b"50000.00", b"51000.00"))
        self.assertTrue(any("snapshot content changed" in p for p in self.store.verify()))

    def test_deleted_snapshot_is_detected(self):
        (self.dir / self.a["file"]).unlink()
        self.assertTrue(any("snapshot file missing" in p for p in self.store.verify()))

    def test_edited_index_is_detected(self):
        index = self.dir / "index.jsonl"
        index.write_bytes(index.read_bytes().replace(b"2026-01-31", b"2026-02-28", 1))
        self.assertTrue(any("index line altered" in p for p in self.store.verify()))

    def test_removed_index_line_is_detected(self):
        index = self.dir / "index.jsonl"
        index.write_bytes(b"\n".join(index.read_bytes().split(b"\n")[1:]))
        self.assertTrue(self.store.verify())

    def test_float_payload_is_refused(self):
        with self.assertRaises(jsonio.FloatRefused):
            self.store.append("E-0001", "2026-06-30", {"capital": 90000.0})
        self.assertEqual(len(self.store.entries()), 2)


class InTheRun(unittest.TestCase):
    def test_a_second_identical_run_adds_nothing(self):
        inp = s.ROOT / "scenarios" / "S01" / "input"
        work = s.tmp()
        s.run(inp, work)
        before = s.tree_hashes(work / "snapshots")
        code, _, report = s.run(inp, work)
        self.assertEqual(code, 0)
        self.assertFalse(report["entities"]["E-0001"]["snapshot"]["created"])
        self.assertEqual(s.tree_hashes(work / "snapshots"), before)

    def test_a_tampered_store_fails_the_run(self):
        inp = s.ROOT / "scenarios" / "S01" / "input"
        work = s.tmp()
        s.run(inp, work)
        snap = next((work / "snapshots" / "E-0001").glob("*.json"))
        snap.write_bytes(snap.read_bytes().replace(b"50000.00", b"51000.00"))
        code, out, report = s.run(inp, work)
        self.assertEqual(code, 3, out)
        self.assertTrue(report["snapshot_store_problems"])
        self.assertNotIn("RUN OK", out)


if __name__ == "__main__":
    unittest.main()
