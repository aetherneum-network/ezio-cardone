"""Reference for cap-table sums and effective holdings - independent of the code under test.

The pipeline (``dossier/s4_ownership.py``) finds cycles with Tarjan's algorithm and looks through the
graph by memoised recursion (or Gaussian elimination under the ``closure`` policy). This reference
does neither: it **enumerates every path** from the entity up to a natural person and adds the
products of the exact fractions along each path. A path that meets an entity twice is a cycle.

It imports nothing from ``dossier``. It is used to write the gold labels and by the tests.
"""
from __future__ import annotations

from fractions import Fraction

Table = list[tuple[str, Fraction]]


def is_entity(holder: str) -> bool:
    return holder.startswith("E-")


def table_sum(table: Table) -> Fraction:
    total = Fraction(0)
    for _, share in table:
        total += share
    return total


def enumerate_paths(tables: dict[str, Table], target: str) -> tuple[list[tuple[list[str], Fraction]], list[list[str]], list[str]]:
    """(paths to persons with their product, cycles met, entities whose table is missing)."""
    paths: list[tuple[list[str], Fraction]] = []
    cycles: list[list[str]] = []
    missing: list[str] = []
    stack: list[tuple[list[str], Fraction]] = [([target], Fraction(1))]
    while stack:
        path, product = stack.pop()
        node = path[-1]
        if node not in tables or tables[node] is None:
            if node not in missing:
                missing.append(node)
            continue
        for holder, share in tables[node]:
            if not is_entity(holder):
                paths.append((path + [holder], product * share))
            elif holder in path:
                cyc = sorted(path[path.index(holder):])
                if cyc not in cycles:
                    cycles.append(cyc)
            else:
                stack.append((path + [holder], product * share))
    return paths, sorted(cycles), sorted(missing)


def effective_holdings(tables: dict[str, Table], target: str) -> dict:
    """Exact effective holding of natural persons in ``target``; abstains on a cycle or a missing table."""
    paths, cycles, missing = enumerate_paths(tables, target)
    if missing or cycles:
        return {"outcome": "TO_CONFIRM", "effective": None, "cycles": cycles, "missing": missing,
                "paths": len(paths)}
    eff: dict[str, Fraction] = {}
    for path, product in paths:
        eff[path[-1]] = eff.get(path[-1], Fraction(0)) + product
    return {"outcome": "RESOLVED", "effective": dict(sorted(eff.items())), "cycles": [], "missing": [],
            "paths": len(paths)}


def merged_cycles(cycles: list[list[str]]) -> list[list[str]]:
    """Cycles that share an entity merged into one group (comparable with strongly connected components)."""
    groups: list[set[str]] = []
    for cyc in cycles:
        hit = [g for g in groups if g & set(cyc)]
        merged = set(cyc).union(*hit) if hit else set(cyc)
        groups = [g for g in groups if g not in hit] + [merged]
    return sorted(sorted(g) for g in groups)


def bracket_closure(tables: dict[str, Table], target: str, depth: int = 40) -> tuple[dict[str, Fraction], Fraction]:
    """For a graph with cycles: the look-through summed over every walk of at most ``depth`` entities.

    Returns ``(lower, remainder)``: the exact closure of each person lies in
    ``[lower[p], lower[p] + remainder]``. No linear algebra is used.
    """
    lower: dict[str, Fraction] = {}
    frontier: dict[str, Fraction] = {target: Fraction(1)}
    for _ in range(depth):
        nxt: dict[str, Fraction] = {}
        for node, weight in frontier.items():
            for holder, share in tables[node]:
                if is_entity(holder):
                    nxt[holder] = nxt.get(holder, Fraction(0)) + weight * share
                else:
                    lower[holder] = lower.get(holder, Fraction(0)) + weight * share
        frontier = nxt
        if not frontier:
            break
    remainder = Fraction(0)
    for weight in frontier.values():
        remainder += weight
    return dict(sorted(lower.items())), remainder
