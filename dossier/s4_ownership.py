"""Stage 4 - cap tables and the ownership chain, in exact arithmetic.

* Every holders' table stated by a document of the entity is summed with ``fractions.Fraction``.
  A table that does not sum to exactly the whole blocks the build of that entity (``BLOCKED``).
* A holders' table that exists or may exist and could not be summed - a table that could not be read, a
  document expected to state the holders where no table was found, a document that could not be
  classified or was rejected - leaves the sum unverified. Under the declared ``unverified_holders_table``
  policy (``block``, the default since v2.0.1) that also blocks the build: an unread table may be the one
  that does not sum.
* The graph holder -> held entity is built only from tables that are ``STATED`` (one readable value).
* Cross-holdings are found as strongly connected components (Tarjan) and reported.
* The effective holding of natural persons is a look-through by memoised recursion over the acyclic
  graph; with a cycle the declared ``cycle_policy`` applies: ``abstain`` (default) or ``closure``
  (exact solution of the linear system, by Gaussian elimination on fractions).

The decision for one entity is taken by the ordered rules of ``rules/ownership.json``.
The reference in ``corpus/reference_ownership.py`` uses a different algorithm (path enumeration).
"""
from __future__ import annotations

import re
from fractions import Fraction

from .lib.numbers import frac_str, parse_frac
from .rules_engine import Rules, first_match

_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def is_entity(holder: str) -> bool:
    return holder.startswith("E-")


def unverified_tables(record: dict) -> list[dict]:
    """Every place of the entity where a holders' table is or may be, and could not be summed."""
    out = []
    for a in record["assertions"]:
        if a["field"] == "shareholders" and a["status"] != "STATED":
            out.append({"source_doc": a["source_doc"], "why": a.get("reason") or "could not be read"})
    for u in record.get("unclassified_documents", []):
        date = u.get("date") or ""
        if _ISO_DATE.fullmatch(date) and date > record["as_of"]:
            continue                      # dated after as_of: it cannot hold a table of the dossier
        out.append({"source_doc": u.get("doc_id") or u["file"], "why": f"document not read: {u['reason']}"})
    for r in record.get("rejected_documents", []):
        out.append({"source_doc": r["file"], "why": f"document not read: {r['reason']}"})
    return sorted(out, key=lambda x: (x["source_doc"], x["why"]))


def sum_checks(record: dict, rules: Rules) -> list[dict]:
    """The exact sum of every holders' table any document of the entity states."""
    whole = parse_frac(rules.param("ownership", "sum_must_equal"))
    out = []
    for a in record["assertions"]:
        if a["field"] == "shareholders" and a["status"] == "STATED":
            total = sum((parse_frac(r["share"]) for r in a["value"]), Fraction(0))
            out.append({"source_doc": a["source_doc"], "source_date": a["source_date"], "edition": a["edition"],
                        "sum": frac_str(total), "whole": total == whole})
    return sorted(out, key=lambda c: (c["source_date"], c["source_doc"]))


def build_nodes(records: dict[str, dict], resolutions: dict[str, dict], rules: Rules) -> dict[str, dict]:
    """One node per entity of the dossier set: its holders' table, if there is a single readable one."""
    nodes = {}
    for eid in sorted(records):
        checks = sum_checks(records[eid], rules)
        res = resolutions[eid]["fields"].get("shareholders")
        node = {"status": "TO_CONFIRM", "why": "no source states the holders", "table": [], "source": None,
                "checks": checks, "violations": [c for c in checks if not c["whole"]],
                "unverified": unverified_tables(records[eid])}
        if res is not None:
            node["status"] = res["status"]
            if res["status"] == "STATED":
                node["table"] = [(r["holder"], parse_frac(r["share"])) for r in res["value"]]
                node["source"] = dict(res["sources"][0])
                node["why"] = ""
            elif res["status"] == "DISCREPANCY":
                node["why"] = "the holders are in discrepancy between sources"
            else:
                node["why"] = res["reason"]
        if node["violations"]:
            node["status"], node["table"] = "BLOCKED", []
            v = node["violations"][0]
            node["why"] = f"holders' table of {v['source_doc']} sums to {v['sum']}, not to the whole"
        elif node["unverified"] and rules.param("ownership", "unverified_holders_table") == "block":
            node["status"], node["table"] = "BLOCKED", []
            node["why"] = _unverified_reason(node["unverified"])
        nodes[eid] = node
    return nodes


def _unverified_reason(unverified: list[dict]) -> str:
    u = unverified[0]
    more = f" (and {len(unverified) - 1} more)" if len(unverified) > 1 else ""
    return (f"the holders' table of {u['source_doc']} could not be summed ({u['why']}){more}: "
            "that the cap table sums to the whole is not verified")


def _closure(nodes: dict[str, dict], target: str) -> tuple[list[str], list[dict]]:
    """Entities reachable upward from the target through readable tables, and the nodes where the chain stops."""
    seen, order, stops = {target}, [target], []
    queue = [target]
    while queue:
        e = queue.pop(0)
        for holder, _ in nodes[e]["table"]:
            if not is_entity(holder) or holder in seen:
                continue
            seen.add(holder)
            if holder not in nodes:
                stops.append({"entity": holder, "why": "holder entity is not in the dossier set"})
            elif nodes[holder]["status"] != "STATED":
                stops.append({"entity": holder, "why": nodes[holder]["why"]})
            else:
                order.append(holder)
                queue.append(holder)
    return order, sorted(stops, key=lambda s: s["entity"])


def find_cycles(nodes: dict[str, dict], members: list[str]) -> list[list[str]]:
    """Strongly connected components with a cycle among ``members`` (Tarjan, iterative)."""
    inside = set(members)
    graph = {e: sorted(h for h, _ in nodes[e]["table"] if is_entity(h) and h in inside) for e in members}
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    out: list[list[str]] = []
    counter = 0
    for root in sorted(members):
        if root in index:
            continue
        work = [(root, 0)]
        while work:
            v, i = work.pop()
            if i == 0:
                index[v] = low[v] = counter
                counter += 1
                stack.append(v)
                on_stack.add(v)
            recurse = False
            for j in range(i, len(graph[v])):
                w = graph[v][j]
                if w not in index:
                    work.append((v, j + 1))
                    work.append((w, 0))
                    recurse = True
                    break
                if w in on_stack:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1 or v in graph[v]:
                    out.append(sorted(comp))
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
    return sorted(out)


def _look_through(nodes: dict[str, dict], target: str) -> dict[str, Fraction]:
    memo: dict[str, dict[str, Fraction]] = {}

    def eff(e: str) -> dict[str, Fraction]:
        if e in memo:
            return memo[e]
        acc: dict[str, Fraction] = {}
        for holder, share in nodes[e]["table"]:
            if is_entity(holder):
                for p, s in eff(holder).items():
                    acc[p] = acc.get(p, Fraction(0)) + share * s
            else:
                acc[holder] = acc.get(holder, Fraction(0)) + share
        memo[e] = acc
        return acc

    return eff(target)


def _solve_closure(nodes: dict[str, dict], members: list[str], target: str) -> dict[str, Fraction] | None:
    """Exact solution of x = direct + cross * x over the members; None when the system is singular."""
    persons = sorted({h for e in members for h, _ in nodes[e]["table"] if not is_entity(h)})
    idx = {e: i for i, e in enumerate(members)}
    n = len(members)
    a = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    b = [[Fraction(0) for _ in persons] for _ in range(n)]
    pidx = {p: k for k, p in enumerate(persons)}
    for e in members:
        for holder, share in nodes[e]["table"]:
            if is_entity(holder):
                a[idx[e]][idx[holder]] -= share
            else:
                b[idx[e]][pidx[holder]] += share
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col] != 0), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        b[col], b[pivot] = b[pivot], b[col]
        inv = 1 / a[col][col]
        a[col] = [x * inv for x in a[col]]
        b[col] = [x * inv for x in b[col]]
        for r in range(n):
            if r != col and a[r][col] != 0:
                f = a[r][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
                b[r] = [x - f * y for x, y in zip(b[r], b[col])]
    row = b[idx[target]]
    return {p: row[pidx[p]] for p in persons if row[pidx[p]] != 0}


def analyse(nodes: dict[str, dict], target: str, rules: Rules, cycle_policy: str | None = None,
            unverified_policy: str | None = None) -> dict:
    """The ownership result of one entity, decided by the ordered rules of ownership.json."""
    policy = cycle_policy or rules.param("ownership", "cycle_policy")
    if policy not in rules.ownership["parameters"]["cycle_policy"]["allowed"]:
        raise ValueError(f"cycle_policy {policy!r} is not allowed")
    node = nodes[target]
    members, stops = _closure(nodes, target) if node["status"] == "STATED" else ([target], [])
    cycles = find_cycles(nodes, members) if node["status"] == "STATED" else []
    unverified_policy = unverified_policy or rules.param("ownership", "unverified_holders_table")
    if unverified_policy not in rules.ownership["parameters"]["unverified_holders_table"]["allowed"]:
        raise ValueError(f"unverified_holders_table {unverified_policy!r} is not allowed")
    facts = {"holder_table_sum_not_whole": bool(node["violations"]),
             "holder_table_sum_not_verified": bool(node["unverified"]) and unverified_policy == "block",
             "holders_not_stated": node["status"] != "STATED",
             "upstream_not_resolved": bool(stops),
             "cycle_upstream": bool(cycles),
             "always": True}
    rule = first_match(rules.ownership["rules"], lambda r: facts[r["when"]])
    outcome = rule["outcome"].replace("{cycle_policy}", "TO_CONFIRM" if policy == "abstain" else "RESOLVED")
    res: dict = {"entity": target, "outcome": outcome, "rule": rule["id"], "cycle_policy": policy,
                 "sum_checks": node["checks"], "unverified_tables": node["unverified"],
                 "cycles": cycles, "unresolved_nodes": stops,
                 "table": [], "chain": [], "effective": None, "method": None, "reason": ""}
    if node["status"] == "STATED":
        res["table"] = [dict(holder=h, share=frac_str(s), **node["source"]) for h, s in node["table"]]
        for e in members:
            for h, s in nodes[e]["table"]:
                res["chain"].append(dict(holder=h, held=e, share=frac_str(s), **nodes[e]["source"]))
        res["chain"].sort(key=lambda c: (c["held"], c["holder"]))
    if outcome == "BLOCKED":
        res["reason"] = (node["why"] if rule["when"] == "holder_table_sum_not_whole"
                         else _unverified_reason(node["unverified"]))
        res["table"], res["chain"] = [], []
    elif outcome == "TO_CONFIRM":
        if rule["when"] == "holders_not_stated":
            res["reason"] = node["why"]
        elif rule["when"] == "upstream_not_resolved":
            res["reason"] = "the chain stops at " + "; ".join(f"{s['entity']} ({s['why']})" for s in stops)
        else:
            res["reason"] = ("cross-holding " + "; ".join(" <-> ".join(c) for c in cycles)
                             + ": effective holding not computed under cycle_policy 'abstain'")
    else:
        if cycles:
            eff = _solve_closure(nodes, members, target)
            res["method"] = "closure"
            if eff is None:
                res["outcome"], res["reason"] = "TO_CONFIRM", "the cross-holding leaves no share to any natural person"
        else:
            eff = _look_through(nodes, target)
            res["method"] = "look-through"
        if eff is not None:
            res["effective"] = {p: frac_str(s) for p, s in sorted(eff.items())}
    return res


def analyse_all(records: dict[str, dict], resolutions: dict[str, dict], rules: Rules) -> dict[str, dict]:
    nodes = build_nodes(records, resolutions, rules)
    return {eid: analyse(nodes, eid, rules) for eid in sorted(nodes)}


def run_inline_tests(rules: Rules) -> tuple[int, list[str]]:
    whole = parse_frac(rules.param("ownership", "sum_must_equal"))
    n, bad = 0, []
    for r in rules.ownership["rules"]:
        for t in r.get("tests", []):
            n += 1
            nodes = {}
            for eid, table in t["tables"].items():
                node = {"status": "TO_CONFIRM", "why": "unreadable", "table": [], "source": None, "checks": [],
                        "violations": [], "unverified": t.get("unverified", {}).get(eid, [])}
                if table is not None:
                    rows = [(h, parse_frac(s)) for h, s in table]
                    total = sum((s for _, s in rows), Fraction(0))
                    check = {"source_doc": "T", "source_date": "2026-01-01", "edition": "T/1",
                             "sum": frac_str(total), "whole": total == whole}
                    node.update(status="STATED", why="", table=rows, checks=[check],
                                source={"source_doc": "T", "source_date": "2026-01-01", "edition": "T/1"})
                    if not check["whole"]:
                        node.update(status="BLOCKED", table=[], violations=[check], why="sum")
                upolicy = t.get("unverified_holders_table") or rules.param("ownership", "unverified_holders_table")
                if node["unverified"] and node["status"] != "BLOCKED" and upolicy == "block":
                    node.update(status="BLOCKED", table=[], why=_unverified_reason(node["unverified"]))
                nodes[eid] = node
            got = analyse(nodes, t["target"], rules, t.get("cycle_policy"), t.get("unverified_holders_table"))
            exp = t["expect"]
            ok = got["outcome"] == exp["outcome"] and got["rule"] == r["id"]
            if "sum" in exp:
                ok = ok and got["sum_checks"][0]["sum"] == exp["sum"]
            if "effective" in exp:
                ok = ok and got["effective"] == exp["effective"]
            if "cycles" in exp:
                ok = ok and got["cycles"] == exp["cycles"]
            if got["outcome"] != "RESOLVED" and got["effective"] is not None:
                ok = False
            if not ok:
                bad.append(f"{r['id']}: got {got['outcome']} by {got['rule']} eff={got['effective']}, expected {exp}")
    return n, bad
