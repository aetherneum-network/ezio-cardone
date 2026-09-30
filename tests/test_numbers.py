"""Amounts are decimal strings, shares are exact fractions; a float never enters."""
import unittest
from fractions import Fraction

from . import support as s  # noqa: F401  (socket block, sys.path)

from dossier.lib import jsonio
from dossier.lib.numbers import format_amount, frac_str, parse_amount, parse_frac, parse_share, share_display


class Amounts(unittest.TestCase):
    def test_forms_that_are_read(self):
        for token in ("50.000,00", "50000,00", "50,000.00", "50000.00", "50 000,00", "50000"):
            self.assertEqual(parse_amount(token), ("50000.00", None), token)
        self.assertEqual(parse_amount("1.234.567,89"), ("1234567.89", None))
        self.assertEqual(parse_amount("0,10"), ("0.10", None))

    def test_forms_that_are_not_guessed(self):
        for token, why in (("50.000", "ambiguous"), ("50,000", "ambiguous"), ("8#.###,00", "illegible"),
                           ("[illegible]", "illegible"), ("", "empty"), ("fifty thousand", "not recognised"),
                           ("50.000,0", "not recognised"), ("-50.000,00", "not recognised"),
                           ("50.000,000", "ambiguous"), ("5e4", "not recognised")):
            value, reason = parse_amount(token)
            self.assertIsNone(value, token)
            self.assertIn(why, reason, token)

    def test_no_binary_rounding(self):
        self.assertEqual(parse_amount("0,29"), ("0.29", None))
        self.assertEqual(parse_amount("1.000.000.000.000,01"), ("1000000000000.01", None))
        self.assertEqual(parse_amount("9007199254740993,00"), ("9007199254740993.00", None))

    def test_display_round_trip(self):
        for canon, shown in (("50000.00", "EUR 50.000,00"), ("999.99", "EUR 999,99"), ("0.10", "EUR 0,10"),
                             ("1234567.89", "EUR 1.234.567,89")):
            self.assertEqual(format_amount(canon), shown)
            self.assertEqual(parse_amount(shown[4:]), (canon, None))
        for bad in ("50000", "50000.0", "50.000,00", "EUR 50000.00", "", "5e4"):
            with self.assertRaises(ValueError):
                format_amount(bad)


class Shares(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(parse_share("60%"), (Fraction(3, 5), None))
        self.assertEqual(parse_share("33,33%"), (Fraction(3333, 10000), None))
        self.assertEqual(parse_share("33.33 %"), (Fraction(3333, 10000), None))
        self.assertEqual(parse_share("1/3"), (Fraction(1, 3), None))
        self.assertEqual(parse_share("60/100"), (Fraction(3, 5), None))
        self.assertEqual(parse_share("0,5%"), (Fraction(1, 200), None))

    def test_three_thirds_are_the_whole_three_rounded_percentages_are_not(self):
        thirds = sum((parse_share("1/3")[0] for _ in range(3)), Fraction(0))
        rounded = sum((parse_share("33,33%")[0] for _ in range(3)), Fraction(0))
        self.assertEqual(thirds, 1)
        self.assertEqual(frac_str(rounded), "9999/10000")
        self.assertNotEqual(rounded, 1)
        self.assertEqual(sum(parse_share(t)[0] for t in ("33,34%", "33,33%", "33,33%")), 1)

    def test_not_guessed(self):
        for token in ("", "1/0", "about a third", "6#%", "60", "60 percent", "-10%"):
            value, reason = parse_share(token)
            self.assertIsNone(value, token)
            self.assertTrue(reason)

    def test_canonical_strings(self):
        self.assertEqual(frac_str(Fraction(6, 10)), "3/5")
        self.assertEqual(frac_str(Fraction(1)), "1/1")
        self.assertEqual(parse_frac("3/5"), Fraction(3, 5))
        for bad in ("0.6", "3/0", "60%", "", " 3/5", None, 0.6, 3):
            with self.assertRaises(ValueError):
                parse_frac(bad)

    def test_percentage_shown_only_when_exact(self):
        self.assertEqual(share_display("3/5"), "3/5 (60%)")
        self.assertEqual(share_display("1/8"), "1/8 (12,5%)")
        self.assertEqual(share_display("1/3"), "1/3")
        self.assertEqual(share_display("9/49"), "9/49")
        self.assertEqual(share_display("1/1"), "1/1 (100%)")


class Json(unittest.TestCase):
    def test_floats_are_refused_on_reading(self):
        for text in ('{"a": 0.1}', '{"a": [1, 2.0]}', '{"a": 1e3}', '{"a": {"b": -0.0}}'):
            with self.assertRaises(jsonio.FloatRefused):
                jsonio.loads(text)
        self.assertEqual(jsonio.loads('{"a": 1, "b": "0.1"}'), {"a": 1, "b": "0.1"})

    def test_floats_are_refused_on_writing(self):
        with self.assertRaises(jsonio.FloatRefused):
            jsonio.dumps({"a": 0.1})

    def test_output_is_canonical(self):
        a = jsonio.dumps({"b": 1, "a": ["é", {"d": 1, "c": 2}]})
        b = jsonio.dumps({"a": ["é", {"c": 2, "d": 1}], "b": 1})
        self.assertEqual(a, b)
        self.assertTrue(a.endswith("\n"))
        self.assertNotIn("\r", a)
        self.assertIn("é", a)

    def test_written_bytes_are_verified_and_lf(self):
        path = s.tmp() / "deep" / "x.json"
        sha = jsonio.write(path, {"a": "line\r\nbreak"})
        self.assertEqual(sha, jsonio.sha256_file(path))
        self.assertNotIn(b"\r\n", path.read_bytes().replace(b"\\r\\n", b""))

    def test_exclusive_write_never_replaces(self):
        path = s.tmp() / "x.json"
        jsonio.write(path, {"a": 1}, exclusive=True)
        with self.assertRaises(FileExistsError):
            jsonio.write(path, {"a": 2}, exclusive=True)
        self.assertEqual(jsonio.load(path), {"a": 1})


if __name__ == "__main__":
    unittest.main()
