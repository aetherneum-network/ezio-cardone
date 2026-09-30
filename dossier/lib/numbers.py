"""Exact numbers: amounts as decimal strings, shares as fractions. No float is ever produced.

``parse_amount`` and ``parse_share`` return ``(canonical, None)`` or ``(None, reason)``: a token that is
illegible, ambiguous or in a form this module does not know is *not* guessed.

Grouping read by ``parse_amount`` (one separator throughout the token, groups of exactly three digits):
dot with comma decimals (``50.000,00``), comma with dot decimals (``50,000.00``), apostrophe ASCII or
typographic (``50'000.00``, ``50’000,00``) and space - ASCII, no-break U+00A0, figure U+2007, thin U+2009,
narrow no-break U+202F - with dot or comma decimals. Apostrophe and space are never a decimal mark, so
without decimals they still read (``50'000``); dot or comma without decimals is ambiguous and abstains.
Any other grouping character (a look-alike apostrophe, a hair space, a middle dot...) abstains.
"""
from __future__ import annotations

import re
from decimal import Decimal
from fractions import Fraction

_IT = re.compile(r"^\d{1,3}(\.\d{3})+,\d{2}$")          # 50.000,00
_IT_PLAIN = re.compile(r"^\d+,\d{2}$")                   # 50000,00
_EN = re.compile(r"^\d{1,3}(,\d{3})+\.\d{2}$")           # 50,000.00
_EN_PLAIN = re.compile(r"^\d+\.\d{2}$")                  # 50000.00
_APOS = re.compile(r"^\d{1,3}(['’])\d{3}(?:\1\d{3})*(?:[.,]\d{2})?$")                   # 50'000.00
_SPACE = re.compile(r"^\d{1,3}([ \u00a0\u2007\u2009\u202f])\d{3}(?:\1\d{3})*(?:[.,]\d{2})?$")  # 50 000,00
_INT = re.compile(r"^\d+$")                              # 50000
_AMBIGUOUS = re.compile(r"^\d{1,3}([.,]\d{3})+$")        # 50.000 or 50,000: thousands or decimals?
_KNOWN_CHARS = re.compile(r"^[\d.,'’ \u00a0\u2007\u2009\u202f]*$")

AMOUNT_CANON = re.compile(r"^\d+\.\d{2}$")
FRACTION_CANON = re.compile(r"^\d+/[1-9]\d*$")


def parse_amount(token: str) -> tuple[str | None, str | None]:
    """Return the amount as a canonical string with two decimals (``"50000.00"``)."""
    t = token.strip()
    if not t:
        return None, "empty amount"
    if "#" in t or "illegible" in t.lower():
        return None, "illegible figure"
    if _IT.match(t):
        return _canon(t.replace(".", "").replace(",", ".")), None
    if _IT_PLAIN.match(t):
        return _canon(t.replace(",", ".")), None
    if _EN.match(t):
        return _canon(t.replace(",", "")), None
    if _EN_PLAIN.match(t):
        return _canon(t), None
    m = _APOS.match(t) or _SPACE.match(t)
    if m:
        return _canon(t.replace(m.group(1), "").replace(",", ".")), None
    if _AMBIGUOUS.match(t):
        return None, "ambiguous separator (thousands or decimals)"
    if _INT.match(t):
        return _canon(t), None
    odd = sorted({c for c in t if not c.isalnum() and c not in "+-" and not _KNOWN_CHARS.match(c)})
    if odd:
        return None, "grouping character not recognised: " + ", ".join(f"U+{ord(c):04X}" for c in odd)
    return None, "amount in a form that is not recognised"


def _canon(plain: str) -> str:
    return f"{Decimal(plain):.2f}"


def format_amount(canonical: str) -> str:
    """``"50000.00"`` -> ``"EUR 50.000,00"``."""
    if not AMOUNT_CANON.match(canonical):
        raise ValueError(f"not a canonical amount: {canonical!r}")
    whole, cents = canonical.split(".")
    groups = []
    while whole:
        groups.append(whole[-3:])
        whole = whole[:-3]
    return f"EUR {'.'.join(reversed(groups))},{cents}"


_PER_CENT = r"(?:%|per\s?-?\s?cent|percent|pct\.?)"
_PCT = re.compile(r"^(\d+)(?:[.,](\d+))?\s*" + _PER_CENT + r"$", re.I)
_FRAC = re.compile(r"^(\d+)\s*/\s*(\d+)$")
_UNITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
          "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_ORDINALS = {"half": 2, "third": 3, "quarter": 4, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
             "ninth": 9, "tenth": 10, "twentieth": 20, "hundredth": 100}
_PCT_WORDS = re.compile(r"^([a-z]+(?:[\s-][a-z]+)*)\s+" + _PER_CENT + r"$", re.I)
_FRAC_WORDS = re.compile(r"^(?:(a|an|[a-z]+)\s+)?(halves|half|[a-z]+?)(s?)$", re.I)


def words_to_int(text: str) -> int | None:
    """An integer from 0 to 100 written in English words ("thirty", "thirty-five", "thirty five", "one hundred",
    "a hundred"); None for anything else (decimals, "and", ordinals, numbers above one hundred)."""
    t = re.sub(r"[\s-]+", " ", text.strip().lower())
    if t in ("one hundred", "a hundred", "hundred"):
        return 100
    if t in _UNITS:
        return _UNITS.index(t)
    if t in _TENS:
        return _TENS[t]
    parts = t.split(" ")
    if len(parts) == 2 and parts[0] in _TENS and parts[1] in _UNITS[1:10]:
        return _TENS[parts[0]] + _UNITS.index(parts[1])
    return None


def _share_in_words(t: str) -> tuple[Fraction | None, str | None]:
    m = _PCT_WORDS.match(t)
    if m:
        n = words_to_int(m.group(1))
        if n is None:
            return None, "per cent in words that are not a whole number from zero to one hundred"
        return Fraction(n, 100), None
    m = _FRAC_WORDS.match(t.strip().lower())
    if m and m.group(2) in ("half", "halves") or (m and m.group(2) in _ORDINALS):
        num_word, ordinal, plural = m.group(1), m.group(2), m.group(3)
        if ordinal == "halves":
            ordinal, plural = "half", "s"
        if num_word is None:
            return None, "a fraction in words without its numerator"
        num = 1 if num_word in ("a", "an") else words_to_int(num_word)
        if num is None or num == 0:
            return None, "the numerator of a fraction in words is not read"
        if (num == 1) == bool(plural):       # "one thirds", "two third": singular and plural disagree
            return None, "a fraction in words whose number and ordinal disagree"
        return Fraction(num, _ORDINALS[ordinal]), None
    return None, "share in a form that is not recognised"


def parse_share(token: str) -> tuple[Fraction | None, str | None]:
    """``"60%"``, ``"60 %"``, ``"33,33%"``, ``"60 per cent"``, ``"60 percent"``, ``"1/3"``, ``"60/100"``,
    ``"thirty per cent"``, ``"thirty-five per cent"``, ``"one third"``, ``"two fifths"``, ``"a half"`` -> exact
    ``Fraction``. Since v2.0.3 (D30) the per cent words and the shares written in words are read; a share in
    words that is not a whole number of per cent or a simple fraction (numerator in words, ordinal
    denominator) is not read. Counts and nominal amounts are not shares: they are read only with a total
    stated in the same document (``dossier/s1_extract.py``)."""
    t = token.strip()
    if not t:
        return None, "empty share"
    if "#" in t or "illegible" in t.lower():
        return None, "illegible figure"
    m = _PCT.match(t)
    if m:
        digits = m.group(2) or ""
        return Fraction(int(m.group(1) + digits), 100 * 10 ** len(digits)), None
    m = _FRAC.match(t)
    if m:
        if int(m.group(2)) == 0:
            return None, "zero denominator"
        return Fraction(int(m.group(1)), int(m.group(2))), None
    if re.search(r"\d", t):
        return None, "share in a form that is not recognised"
    return _share_in_words(t)


_COUNT = re.compile(r"^(\d{1,3}(?:([.,'’ ])\d{3})?(?:\2\d{3})*|\d+)\s+(?:(?:ordinary|registered)\s+)?"
                    r"(quotas?|shares?)$", re.I)


def parse_count(token: str) -> tuple[int | None, str | None]:
    """``"200 quotas"``, ``"1.200 shares"``, ``"1 ordinary share"`` -> 200, 1200, 1: a number of quotas or shares,
    which is a share only with the total the same document states."""
    m = _COUNT.match(token.strip())
    if not m:
        return None, "not a number of quotas or shares"
    return int(re.sub(r"\D", "", m.group(1))), None


def frac_str(f: Fraction) -> str:
    """Canonical exact form, always ``n/d`` in lowest terms (``1/1`` for the whole)."""
    return f"{f.numerator}/{f.denominator}"


def parse_frac(s: str) -> Fraction:
    if not isinstance(s, str) or not FRACTION_CANON.match(s):
        raise ValueError(f"not a canonical fraction string: {s!r}")
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def share_display(s: str) -> str:
    """``"3/5"`` -> ``"3/5 (60%)"``; the percentage is shown only when it is exact."""
    f = parse_frac(s)
    pct = f * 100
    d = pct.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d != 1:
        return s
    dec = Decimal(pct.numerator) / Decimal(pct.denominator)
    text = format(dec, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return f"{s} ({text.replace('.', ',')}%)"
