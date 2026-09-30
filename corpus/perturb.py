"""Stress perturbations: the same content, said otherwise.

Used only by the ``stress`` suite, which is a *diagnosis* set and is declared as such. A perturbed
document states exactly what the unperturbed one states, so the gold does not change; what changes
is whether the ordered rules can still read it. The expected honest behaviour is to abstain
(``[TO CONFIRM]``), never to read something else.

Four families: amounts in other formats (and in words), rephrased clauses, reordered paragraphs,
another wording of the document type.
"""
from __future__ import annotations

import random
import re

_AMOUNT = re.compile(r"EUR (\d{1,3}(?:\.\d{3})*),(\d{2})")
_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
         "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

REPHRASE = [
    ("The registered office is at ", "The company has its seat at "),
    ("The registered office is transferred from ", "The seat of the company is moved from "),
    (", fully subscribed and fully paid in.", ", entirely subscribed and paid up."),
    ("The increase has been fully subscribed and fully paid in.", "The new shares were all taken up and paid for."),
    ("Holders after the transfer:", "After the transfer the members are:"),
    ("Holders as at the document date:", "Members at the document date:"),
    ("4. Holders.", "4. Members."),
    ("Holders:", "Members:"),
    ("Directors in office after this appointment:", "The board now consists of:"),
    ("5. Directors.", "5. Board."),
    ("Directors:", "Board:"),
    ("Share capital: resolved ", "Share capital: authorised "),
    ("; paid in ", "; paid up "),
    ("Net equity: ", "Equity (net): "),
    ("Revenue: ", "Turnover: "),
    ("Registered office: ", "Seat: "),
    ("to increase the share capital from", "to raise the share capital from"),
    ("the subscribed capital is", "the capital taken up is"),
]
TYPE_SYNONYMS = {
    "Test registry extract": "Extract from the test registry",
    "Deed of incorporation": "Articles of incorporation",
    "Resolution on share capital": "Minutes - capital increase",
    "Share transfer notice": "Notice of assignment of shares",
    "Appointment of directors": "Minutes - change of the board",
    "Transfer of registered office": "Minutes - change of seat",
    "Holders' ledger": "Register of members",
    "Financial statements summary": "Summary of the annual accounts",
}


def words(n: int) -> str:
    """English words of a non-negative integer below one thousand million."""
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("-" + _ONES[n % 10] if n % 10 else "")
    if n < 1000:
        return _ONES[n // 100] + " hundred" + (" and " + words(n % 100) if n % 100 else "")
    if n < 1_000_000:
        return words(n // 1000) + " thousand" + (" " + words(n % 1000) if n % 1000 else "")
    return words(n // 1_000_000) + " million" + (" " + words(n % 1_000_000) if n % 1_000_000 else "")


def _reformat(match: re.Match, style: str) -> str:
    whole, cents = int(match.group(1).replace(".", "")), match.group(2)
    if style == "us":
        return f"EUR {whole:,}.{cents}"
    if style == "plain":
        return f"EUR {whole},{cents}"
    if style == "suffix":
        return f"{whole:,}".replace(",", " ") + f",{cents} euro"
    if style == "symbol":
        dotted = f"{whole:,}".replace(",", ".")
        return f"€ {dotted}" if cents == "00" else f"€ {dotted},{cents}"
    if style == "words" and cents == "00":
        return f"{words(whole)} euro"
    return f"EUR {whole:,}.{cents}"


def _blocks(body: list[str]) -> list[list[str]]:
    """Paragraphs of a body: a list heading keeps its items; every other line stands alone."""
    out: list[list[str]] = []
    i = 0
    while i < len(body):
        line = body[i]
        if not line.strip():
            i += 1
            continue
        block = [line]
        i += 1
        while i < len(body) and body[i].startswith("- "):
            block.append(body[i])
            i += 1
        out.append(block)
    return out


def perturb(text: str, rng: random.Random) -> tuple[str, list[str]]:
    """The perturbed text and the list of what was done (empty when the document is left alone)."""
    lines = text.rstrip("\n").split("\n")
    cut = lines.index("")
    head, body = lines[:cut], lines[cut + 1:]
    done: list[str] = []
    if rng.random() < 0.08:
        for i, line in enumerate(head):
            if line.startswith("Document type: "):
                label = line.split(": ", 1)[1]
                head[i] = f"Document type: {TYPE_SYNONYMS[label]}"
                done.append("type-label")
    if rng.random() < 0.35:
        style = rng.choice(["us", "plain", "suffix", "symbol", "words"])
        new = [_AMOUNT.sub(lambda m: _reformat(m, style), line) for line in body]
        if new != body:
            body = new
            done.append(f"amount-format:{style}")
    if rng.random() < 0.35:
        usable = [(a, b) for a, b in REPHRASE if any(a in line for line in body)]
        for a, b in rng.sample(usable, min(len(usable), rng.randint(1, 2))):
            body = [line.replace(a, b) for line in body]
            done.append(f"rephrase:{b.strip(' :.,;')}")
    if rng.random() < 0.25:
        blocks = _blocks(body)
        if len(blocks) > 2:
            rng.shuffle(blocks)
            body = []
            for block in blocks:
                body.extend(block)
                if len(block) > 1:
                    body.append("")
            while body and body[-1] == "":
                body.pop()
            done.append("reorder")
    return "\n".join(head + [""] + body) + "\n", done
