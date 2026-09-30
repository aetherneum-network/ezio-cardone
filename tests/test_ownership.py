"""Ownership arithmetic is exact, and is checked against an implementation that shares no code with it."""
import random
import unittest
from fractions import Fraction

from . import support as s

from corpus import reference_ownership as ref
from dossier import s4_ownership
from dossier.lib.numbers import frac_str, parse_frac

F = Fraction


def _split(rng: random.Random, parts: int) -> list[Fraction]:
    """``parts`` positive exact fractions that sum to the whole (thirds, sevenths, elevenths included)."""
    den = rng.choice([3, 7, 8, 11, 12, 20, 49, 100, 1000])
    while den < parts:
        den *= 2
    cuts = sorted(rng.sample(range(1, den), parts - 1))
    return [F(b - a, den) for a, b in zip([0, *cuts], [*cuts, den])]


def _graph(rng: random.Random, n: int, cyclic: bool) -> dict:
    ents = [f"E-{i:04d}" for i in range(1, n + 1)]
    tables = {}
    for i, e in enumerate(ents):
        upstream = [x for x in ents if x != e] if cyclic else ents[i + 1:]
        k = rng.randint(1, 4)
        holders = [f"P-{rng.randint(1, 6):03d}"]          # at least one natural person in every table
        while len(holders) < k:
            pick = rng.choice(upstream) if upstream and rng.random() < 0.6 else f"P-{rng.randint(1, 6):03d}"
            if pick not in holders:
                holders.append(pick)
        tables[e] = list(zip(sorted(holders), _split(rng, len(holders))))
    return tables


class AgainstTheReference(unittest.TestCase):
    def test_acyclic_graphs(self):
        rng = random.Random(20260930)
        rules = s.rules()
        for _ in range(300):
            tables = _graph(rng, rng.randint(1, 7), cyclic=False)
            nodes = s.nodes_of(tables)
            for target in tables:
                got = s4_ownership.analyse(nodes, target, rules, "abstain")
                want = ref.effective_holdings(tables, target)
                self.assertEqual(want["outcome"], "RESOLVED")
                self.assertEqual((got["outcome"], got["method"]), ("RESOLVED", "look-through"))
                self.assertEqual(got["effective"], {p: frac_str(v) for p, v in want["effective"].items()})
                self.assertEqual(sum(parse_frac(v) for v in got["effective"].values()), 1)

    def test_cyclic_graphs(self):
        rng = random.Random(20260931)
        rules = s.rules()
        cyclic = 0
        for _ in range(300):
            tables = _graph(rng, rng.randint(2, 6), cyclic=True)
            nodes = s.nodes_of(tables)
            for target in tables:
                want = ref.effective_holdings(tables, target)
                abstain = s4_ownership.analyse(nodes, target, rules, "abstain")
                closure = s4_ownership.analyse(nodes, target, rules, "closure")
                if want["outcome"] == "RESOLVED":
                    for got in (abstain, closure):
                        self.assertEqual(got["effective"], {p: frac_str(v) for p, v in want["effective"].items()})
                    continue
                cyclic += 1
                self.assertEqual((abstain["outcome"], abstain["rule"]), ("TO_CONFIRM", "OWN-040"))
                self.assertIsNone(abstain["effective"])
                self.assertEqual({e for c in abstain["cycles"] for e in c},
                                 {e for c in ref.merged_cycles(want["cycles"]) for e in c})
                self.assertEqual((closure["outcome"], closure["method"]), ("RESOLVED", "closure"))
                eff = {p: parse_frac(v) for p, v in closure["effective"].items()}
                self.assertEqual(sum(eff.values()), 1)
                lower, remainder = ref.bracket_closure(tables, target, depth=60)
                self.assertEqual(set(eff), set(lower))
                for p, v in eff.items():
                    self.assertTrue(lower[p] <= v <= lower[p] + remainder, (target, p, v, lower[p], remainder))
        self.assertGreater(cyclic, 200)

    def test_closure_satisfies_its_own_equation(self):
        """x(e) = direct(e) + sum over entity holders h of share(h) * x(h), exactly."""
        rng = random.Random(20260932)
        rules = s.rules()
        for _ in range(100):
            tables = _graph(rng, rng.randint(2, 5), cyclic=True)
            nodes = s.nodes_of(tables)
            x = {e: {p: parse_frac(v) for p, v in s4_ownership.analyse(nodes, e, rules, "closure")["effective"].items()}
                 for e in tables}
            for e, table in tables.items():
                want: dict[str, Fraction] = {}
                for holder, share in table:
                    if holder.startswith("E-"):
                        for p, v in x[holder].items():
                            want[p] = want.get(p, F(0)) + share * v
                    else:
                        want[holder] = want.get(holder, F(0)) + share
                self.assertEqual(x[e], want)


class Refusals(unittest.TestCase):
    def setUp(self):
        self.rules = s.rules()

    def _one(self, tables, target="E-0001", policy=None):
        return s4_ownership.analyse(s.nodes_of(tables), target, self.rules, policy)

    def test_sum_below_and_above_the_whole(self):
        for shares, total in (((F(3333, 10000),) * 3, "9999/10000"), ((F(1, 2), F(1, 2), F(1, 10000)), "10001/10000"),
                              ((F(60, 100), F(39, 100)), "99/100")):
            table = [(f"P-00{i + 1}", sh) for i, sh in enumerate(shares)]
            got = self._one({"E-0001": table})
            self.assertEqual((got["outcome"], got["rule"]), ("BLOCKED", "OWN-010"))
            self.assertEqual(got["sum_checks"][0]["sum"], total)
            self.assertEqual((got["table"], got["chain"], got["effective"]), ([], [], None))

    def test_blocked_wins_over_everything_else(self):
        tables = {"E-0001": [("E-0002", F(1, 2)), ("P-001", F(49, 100))], "E-0002": [("E-0001", F(1))]}
        self.assertEqual(self._one(tables)["rule"], "OWN-010")

    def test_upstream_not_readable(self):
        got = self._one({"E-0001": [("E-0002", F(1, 2)), ("P-001", F(1, 2))], "E-0002": None})
        self.assertEqual((got["outcome"], got["rule"], got["effective"]), ("TO_CONFIRM", "OWN-030", None))
        self.assertEqual([r["holder"] for r in got["table"]], ["E-0002", "P-001"])

    def test_upstream_blocked_is_not_looked_through(self):
        got = self._one({"E-0001": [("E-0002", F(1))], "E-0002": [("P-001", F(1, 2)), ("P-002", F(49, 100))]})
        self.assertEqual((got["outcome"], got["effective"]), ("TO_CONFIRM", None))

    def test_a_loop_without_any_person_is_never_resolved(self):
        tables = {"E-0001": [("E-0002", F(1))], "E-0002": [("E-0001", F(1))]}
        for policy in ("abstain", "closure"):
            got = self._one(tables, policy=policy)
            self.assertEqual((got["outcome"], got["effective"]), ("TO_CONFIRM", None), policy)

    def test_unknown_cycle_policy(self):
        with self.assertRaises(ValueError):
            self._one({"E-0001": [("P-001", F(1))]}, policy="average")

    def test_default_policy_abstains(self):
        self.assertEqual(self.rules.param("ownership", "cycle_policy"), "abstain")

    def test_the_known_closure_of_scenario_s07(self):
        tables = {"E-0001": [("P-001", F(3, 10)), ("E-0002", F(7, 10))],
                  "E-0002": [("P-002", F(9, 10)), ("E-0003", F(1, 10))],
                  "E-0003": [("P-003", F(4, 5)), ("E-0002", F(1, 5))]}
        got = self._one(tables, policy="closure")
        self.assertEqual(got["effective"], {"P-001": "3/10", "P-002": "9/14", "P-003": "2/35"})


if __name__ == "__main__":
    unittest.main()
