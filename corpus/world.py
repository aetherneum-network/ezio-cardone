"""The synthetic world: invented entities, invented persons, a timeline of events and a plan of documents.

Nothing here reads a document. The world is drawn from a seed; each entity gets a timeline (deed,
then capital increases, transfers, appointments, office moves) and a plan of 4-8 source documents.
A *fault plan* then bends what one document says (a conflicting value, a table that does not sum to
the whole, an illegible figure, a clause whose amounts have no stated nature, a misleading file
name...). The gold labels are computed from this plan (``corpus/gold.py``), never from the text.

Every name is invented: companies are ``<trade word> <invented place>``, persons carry surnames such
as *Finti* or *Provetti*, addresses end in the non-existent province ``(ZZ)``.
"""
from __future__ import annotations

import copy
import datetime as _dt
import random
from dataclasses import dataclass, field
from fractions import Fraction

AS_OF = "2026-09-30"

SECTORS = ["Officine", "Cantieri", "Molini", "Vetrerie", "Cartiere", "Conserve", "Laterizi", "Falegnamerie",
           "Distillerie", "Fonderie", "Tipografie", "Frantoi", "Saline", "Filande", "Ceramiche", "Immobiliare",
           "Finanziaria", "Fornaci"]
TOPONYMS = ["Montefinto", "Valfittizia", "Borgoprova", "Collesintesi", "Roccaesempio", "Pietrafinta",
            "Campomodello", "Pontecollaudo", "Villasimulata", "Portoinventato", "Selvaprototipo",
            "Fontesegnaposto", "Castelfittizio", "Pratofinto", "Rivaprova", "Poggioesempio", "Torremodello",
            "Lagosintetico", "Serrafinta", "Casalprova", "Monteprototipo", "Valcollaudo"]
FIRST = ["Aldo", "Bice", "Carlo", "Dora", "Elio", "Franca", "Gino", "Ida", "Livio", "Mara", "Nino", "Olga",
         "Piero", "Rita", "Sergio", "Tina", "Ugo", "Vera", "Walter", "Zita", "Lia", "Remo", "Nora", "Dino"]
LAST = ["Finti", "Provetti", "Sintetici", "Esempi", "Fittizi", "Immaginari", "Modelli", "Segnaposto",
        "Collaudi", "Simulati", "Inventati", "Prototipi", "Campioni", "Fantasmi", "Fasulli", "Ipotetici"]
STREETS = ["Via del Collaudo", "Piazza del Campione", "Via della Prova", "Corso dei Modelli", "Vicolo Fittizio",
           "Viale degli Esempi", "Largo Simulato", "Via dei Prototipi", "Via del Segnaposto", "Piazza Inventata"]
SPLITS = [["1/1"], ["3/5", "2/5"], ["1/2", "1/2"], ["7/10", "3/10"], ["51/100", "49/100"],
          ["2/5", "7/20", "1/4"], ["1/2", "3/10", "1/5"], ["1/3", "1/3", "1/3"], ["1/4", "1/4", "1/4", "1/4"],
          ["5/8", "3/8"], ["9/10", "1/10"], ["4/5", "1/5"], ["2/3", "1/3"]]

EVENT_KINDS = {"CAPITAL": "RESOLUTION", "TRANSFER": "TRANSFER", "DIRECTORS": "APPOINTMENT", "OFFICE": "OFFICE"}
SLUGS = {"DEED": "deed", "RESOLUTION": "capital-resolution", "TRANSFER": "share-transfer",
         "APPOINTMENT": "appointment", "OFFICE": "office-transfer", "EXTRACT": "registry-extract",
         "LEDGER": "holders-ledger", "FIN": "financial-summary"}
TYPE_LABELS = {"DEED": "Deed of incorporation", "RESOLUTION": "Resolution on share capital",
               "TRANSFER": "Share transfer notice", "APPOINTMENT": "Appointment of directors",
               "OFFICE": "Transfer of registered office", "EXTRACT": "Test registry extract",
               "LEDGER": "Holders' ledger", "FIN": "Financial statements summary"}
ROLE = {"DEED": "event", "RESOLUTION": "event", "TRANSFER": "event", "APPOINTMENT": "event", "OFFICE": "event",
        "EXTRACT": "state", "LEDGER": "state", "FIN": "state"}

# weight of each planted fault (one primary fault per entity; NONE = clean entity)
FAULTS = [("NONE", 38), ("CONFLICT_CAPITAL", 7), ("CONFLICT_DIRECTOR", 5), ("CONFLICT_OFFICE", 5),
          ("CONFLICT_SHARE", 5), ("SUM", 7), ("SUPERSEDED_EDITION", 5), ("FILENAME", 8), ("MULTI_OK", 4),
          ("MULTI_AMBIG", 6), ("ILLEGIBLE", 8), ("RESTATED", 5), ("BARE", 3)]
CROSS_HOLDING_GROUPS = 5


@dataclass
class State:
    name: str
    form: str
    office: str
    cap: tuple[int, int, int]                  # cents: resolved, subscribed, paid in
    holders: list[tuple[str, Fraction]]
    directors: list[str]


@dataclass
class Doc:
    entity: str
    kind: str
    date: str
    doc_id: str = ""
    series: str = ""
    edition_no: int = 1
    fy: str = ""
    render: dict = field(default_factory=dict)   # what the text will say (after the fault plan)
    filename: str = ""
    folder: str = ""
    faults: list[str] = field(default_factory=list)

    @property
    def edition(self) -> str:
        return f"{self.series}/{self.edition_no}"


@dataclass
class Entity:
    eid: str
    registry_no: str
    group: int
    fault: str
    variant: str = ""
    docs: list[Doc] = field(default_factory=list)


@dataclass
class World:
    seed: int
    as_of: str
    persons: dict[str, dict]
    entities: dict[str, Entity]
    labels: dict[str, str]                       # holder id -> label written next to it in documents
    cross_groups: list[int]


def share_text(share: Fraction) -> str:
    """How a share is written in a document: a percentage when exact with at most two decimals, else n/d."""
    pct = share * 100
    if (pct * 100).denominator == 1:
        whole, frac = divmod(int(pct * 100), 100)
        if frac == 0:
            return f"{whole}%"
        return f"{whole},{frac // 10}%" if frac % 10 == 0 else f"{whole},{frac:02d}%"
    return f"{share.numerator}/{share.denominator}"


def _date(o: int) -> str:
    return _dt.date.fromordinal(o).isoformat()


def _pick_weighted(rng: random.Random, table: list[tuple[str, int]]) -> str:
    total = sum(w for _, w in table)
    x = rng.randrange(total)
    for name, w in table:
        if x < w:
            return name
        x -= w
    raise AssertionError


def _address(rng: random.Random) -> str:
    return f"{rng.choice(STREETS)} {rng.randint(1, 98)}, {rng.choice(TOPONYMS)} (ZZ)"


def build_world(seed: int, n_entities: int = 150, as_of: str = AS_OF) -> World:
    rng = random.Random(seed)
    sizes: list[int] = []
    while sum(sizes) < n_entities:
        sizes.append(min(rng.randint(3, 7), n_entities - sum(sizes)))
    combos = [(s, t) for s in SECTORS for t in TOPONYMS]
    rng.shuffle(combos)
    person_names = [f"{a} {b}" for a in FIRST for b in LAST]
    rng.shuffle(person_names)
    cross = sorted(rng.sample(range(len(sizes)), min(CROSS_HOLDING_GROUPS, len(sizes))))

    persons: dict[str, dict] = {}
    labels: dict[str, str] = {}
    entities: dict[str, Entity] = {}
    n = 0
    for g, size in enumerate(sizes):
        group_persons = []
        for _ in range(rng.randint(2, 5)):
            pid = f"P-{len(persons) + 1:03d}"
            name = person_names[len(persons)]
            slug = name.lower().replace(" ", ".")
            persons[pid] = {"name": name, "born": _date(rng.randint(_dt.date(1950, 1, 1).toordinal(),
                                                                     _dt.date(1995, 12, 31).toordinal())),
                            "email": f"{slug}@persons.example", "tax_code": f"SYN-CF-{pid.replace('-', '')}"}
            labels[pid] = name
            group_persons.append(pid)
        eids = []
        toponym = None
        for i in range(size):
            n += 1
            eid = f"E-{n:04d}"
            sector, top = combos[n - 1]
            form = "S.p.A." if rng.random() < 0.2 else "S.r.l."
            if i == 0:
                toponym = top
                name = f"Holding {top} Partecipazioni {form}"
            else:
                name = f"{sector} {top} {form}"
            labels[eid] = name
            eids.append((eid, name, form))
        # initial holders: the holding is held by persons; the others by earlier entities of the group and persons
        initial: dict[str, list[tuple[str, Fraction]]] = {}
        for i, (eid, _, _) in enumerate(eids):
            split = [Fraction(s) for s in rng.choice(SPLITS)]
            if i == 0:
                split = split[:len(group_persons)] if len(split) <= len(group_persons) else [Fraction(1)]
                holders = rng.sample(group_persons, len(split))
            else:
                k_ent = min(rng.randint(1, 2), i, len(split))
                ent_holders = rng.sample([e for e, _, _ in eids[:i]], k_ent)
                k_per = min(len(split) - k_ent, len(group_persons))
                split = split[:k_ent + k_per]
                if sum(split, Fraction(0)) != 1:
                    split = [Fraction(s) for s in SPLITS[[len(s) for s in SPLITS].index(k_ent + k_per)]]
                holders = ent_holders + rng.sample(group_persons, k_per)
            initial[eid] = list(zip(holders, split))
        if g in cross and size >= 2:
            # cross-holding: a subsidiary held (directly) by the holding takes one tenth of the holding
            top_eid = eids[0][0]
            subs = [e for e, _, _ in eids[1:] if any(h == top_eid for h, _ in initial[e])] or [eids[1][0]]
            sub = rng.choice(subs)
            if not any(h == top_eid for h, _ in initial[sub]):
                initial[sub] = [(top_eid, Fraction(1, 2))] + [(h, s / 2) for h, s in initial[sub]]
            initial[top_eid] = [(h, s * Fraction(9, 10)) for h, s in initial[top_eid]] + [(sub, Fraction(1, 10))]
        for i, (eid, name, form) in enumerate(eids):
            fault = _pick_weighted(rng, FAULTS)
            ent = Entity(eid=eid, registry_no=f"TEST-REG-{int(eid[2:]):06d}", group=g, fault=fault)
            _plan_entity(rng, ent, name, form, initial[eid], group_persons, [e for e, _, _ in eids], as_of)
            entities[eid] = ent
    return World(seed=seed, as_of=as_of, persons=persons, entities=entities, labels=labels, cross_groups=cross)


# ----------------------------------------------------------------------------------------------
# one entity: timeline, documents, fault

def _plan_entity(rng: random.Random, ent: Entity, name: str, form: str, holders: list[tuple[str, Fraction]],
                 group_persons: list[str], group_entities: list[str], as_of: str) -> None:
    fault = ent.fault
    n_docs = rng.randint(4, 8)
    events: list[str] = []
    states: list[str] = []
    variant = ""
    if fault.startswith("CONFLICT") or fault == "SUPERSEDED_EDITION":
        states.append("EXTRACT")
        if fault == "SUPERSEDED_EDITION":
            states.append("EXTRACT")
            variant = rng.choice(["office", "capital", "directors"])
    elif fault == "FILENAME":
        variant = rng.choice(["date", "kind", "appointee", "folder"])
        if variant == "appointee":
            events.append("DIRECTORS")
    elif fault in ("MULTI_OK", "MULTI_AMBIG"):
        events.append("CAPITAL")
        if fault == "MULTI_AMBIG":
            variant = rng.choice(["extract_no_cues", "extract_partial_cues", "resolution"])
            if variant != "resolution":
                states.append("EXTRACT")
    elif fault == "ILLEGIBLE":
        variant = rng.choice(["capital", "holders", "fin", "event"])
        if variant == "capital":
            states.append("EXTRACT")
        elif variant == "holders":
            states.append(rng.choice(["LEDGER", "EXTRACT"]))
        elif variant == "fin":
            states.append("FIN")
        else:
            events.append("CAPITAL")
    elif fault == "RESTATED":
        states += ["FIN", "FIN"]
    elif fault == "SUM":
        variant = rng.choice(["minus", "plus", "thirds"])
    ent.variant = variant
    if not states:
        states.append("EXTRACT")
    n_docs = max(n_docs, 1 + len(events) + len(states))
    n_events = rng.randint(len(events), max(len(events), min(5, n_docs - 1 - len(states))))
    while len(events) < n_events:
        events.append(rng.choice(["CAPITAL", "TRANSFER", "DIRECTORS", "OFFICE"]))
    while 1 + len(events) + len(states) < n_docs:
        room = [k for k, cap in (("EXTRACT", 3), ("LEDGER", 1), ("FIN", 2)) if states.count(k) < cap]
        if not room:
            break
        states.append(rng.choice(room))
    order = [("event", e) for e in events] + [("state", s) for s in states]
    rng.shuffle(order)
    needs_last_extract = fault.startswith("CONFLICT") or (fault == "MULTI_AMBIG" and variant != "resolution") or (
        fault == "ILLEGIBLE" and variant == "capital")
    if needs_last_extract or fault == "SUPERSEDED_EDITION":
        idx = max(i for i, o in enumerate(order) if o == ("state", "EXTRACT"))
        order.append(order.pop(idx))

    lo = _dt.date(2019, 1, 10).toordinal()
    d0 = rng.randint(lo, _dt.date(2022, 6, 30).toordinal())
    hi = _dt.date.fromisoformat(as_of).toordinal() - 10
    later = sorted(rng.sample(range(d0 + 20, hi), len(order)))

    c = rng.choice([10, 20, 50, 100, 120, 200, 500]) * 1000 * 100
    state = State(name=name, form=form, office=_address(rng), cap=(c, c, c),
                  holders=list(holders), directors=rng.sample(group_persons, rng.randint(1, min(3, len(group_persons)))))
    docs = [Doc(entity=ent.eid, kind="DEED", date=_date(d0), series="DEED", render=_snapshot(state, "full"))]
    counters: dict[str, int] = {}
    partial_wanted = fault in ("MULTI_OK", "MULTI_AMBIG")
    fin_first: dict | None = None
    for (role, what), o in zip(order, later):
        date = _date(o)
        if role == "event":
            prev = copy.deepcopy(state)
            kind = EVENT_KINDS[what]
            if what == "CAPITAL":
                new_r = prev.cap[0] + rng.choice([10, 20, 30, 50, 80, 100]) * 1000 * 100
                if partial_wanted or rng.random() < 0.25:
                    partial_wanted = False
                    step = (new_r - prev.cap[0]) // 4
                    sub = prev.cap[0] + step * rng.choice([2, 3])
                    paid = prev.cap[0] + step * rng.choice([0, 1])
                    state.cap = (new_r, sub, paid)
                    style = "res_partial"
                else:
                    state.cap = (new_r, new_r, new_r)
                    style = "res_full"
                render = {"cap": state.cap, "cap_style": style, "prev_cap": prev.cap[0]}
            elif what == "TRANSFER":
                state.holders = _transfer(rng, prev.holders, group_persons)
                render = {"holders": [(h, share_text(s)) for h, s in state.holders]}
            elif what == "DIRECTORS":
                pool = [p for p in group_persons if p not in prev.directors] or group_persons
                keep = prev.directors[:rng.randint(0, len(prev.directors))] if len(group_persons) > 1 else []
                new = list(dict.fromkeys(keep + rng.sample(pool, 1)))
                if sorted(new) == sorted(prev.directors):
                    new = rng.sample(pool, 1)
                state.directors = new
                render = {"directors": list(new)}
            else:
                office = _address(rng)
                while office == prev.office:
                    office = _address(rng)
                state.office = office
                render = {"office": office, "prev_office": prev.office}
            counters[kind] = counters.get(kind, 0) + 1
            docs.append(Doc(entity=ent.eid, kind=kind, date=date, series=kind, edition_no=counters[kind],
                            render=render))
        elif what == "EXTRACT":
            counters["EXTRACT"] = counters.get("EXTRACT", 0) + 1
            style = "split" if len(set(state.cap)) > 1 or rng.random() < 0.7 else "combined"
            docs.append(Doc(entity=ent.eid, kind="EXTRACT", date=date, series="EXTRACT",
                            edition_no=counters["EXTRACT"], render=_snapshot(state, style)))
        elif what == "LEDGER":
            counters["LEDGER"] = counters.get("LEDGER", 0) + 1
            docs.append(Doc(entity=ent.eid, kind="LEDGER", date=date, series="LEDGER",
                            edition_no=counters["LEDGER"],
                            render={"holders": [(h, share_text(s)) for h, s in state.holders]}))
        else:
            fy = str(max(int(docs[0].date[:4]), int(date[:4]) - 1))
            fin = {k: rng.randint(20_000, 9_000_000) * 100 + rng.choice([0, 0, 25, 50, 78])
                   for k in ("net_equity", "total_assets", "revenue")}
            if fin_first is not None and (fault == "RESTATED" or fin_first["fy"] == fy):
                fy = fin_first["fy"]
                if fault != "RESTATED":
                    fin = dict(fin_first["fin"])       # a re-issue: same figures, next edition
            series = f"FIN-FY{fy}"
            counters[series] = counters.get(series, 0) + 1
            docs.append(Doc(entity=ent.eid, kind="FIN", date=date, series=series, edition_no=counters[series], fy=fy,
                            render={"fin": {k: _amount_text(v) for k, v in fin.items()}}))
            if fin_first is None:
                fin_first = {"fy": fy, "fin": fin}
    for i, d in enumerate(docs, 1):
        d.doc_id = f"DOC-{ent.eid.replace('-', '')}-{i:02d}"
        d.folder = ent.eid
        d.filename = f"{d.date}_{SLUGS[d.kind]}.txt"
        if d.kind == "APPOINTMENT":
            d.filename = f"{d.date}_{SLUGS[d.kind]}_{d.render['directors'][0]}.txt"
    ent.docs = docs
    _apply_fault(rng, ent, group_persons, group_entities)


def _snapshot(state: State, cap_style: str) -> dict:
    return {"name": state.name, "form": state.form, "office": state.office, "cap": state.cap,
            "cap_style": cap_style, "holders": [(h, share_text(s)) for h, s in state.holders],
            "directors": list(state.directors)}


def _amount_text(cents: int) -> str:
    whole, frac = divmod(cents, 100)
    return f"{whole:,}".replace(",", ".") + f",{frac:02d}"


def _transfer(rng: random.Random, holders: list[tuple[str, Fraction]], group_persons: list[str]) -> list[tuple[str, Fraction]]:
    table = dict(holders)
    persons = [h for h in table if h.startswith("P-")]
    giver = rng.choice(persons or list(table))
    part = table[giver] if rng.random() < 0.4 else table[giver] / 2
    outside = [p for p in group_persons if p not in table]
    taker = rng.choice(outside) if outside and rng.random() < 0.7 else rng.choice(
        [h for h in table if h != giver] or outside or group_persons)
    if taker == giver:
        return list(holders)
    table[giver] -= part
    if table[giver] == 0:
        del table[giver]
    table[taker] = table.get(taker, Fraction(0)) + part
    return list(table.items())


# ----------------------------------------------------------------------------------------------
# the fault plan: bends what ONE document says; the world above stays the truth

def _last(ent: Entity, kind: str) -> Doc | None:
    found = [d for d in ent.docs if d.kind == kind]
    return found[-1] if found else None


def _apply_fault(rng: random.Random, ent: Entity, group_persons: list[str], group_entities: list[str]) -> None:
    fault, variant = ent.fault, ent.variant
    if fault == "NONE" or fault == "MULTI_OK":
        return
    if fault == "CONFLICT_CAPITAL":
        d = _last(ent, "EXTRACT")
        r, s, p = d.render["cap"]
        bump = rng.choice([10, 20, 30]) * 1000 * 100
        d.render["cap"] = (r + bump, s + bump if s == r else s, p + bump if p == r else p)
    elif fault == "CONFLICT_DIRECTOR":
        d = _last(ent, "EXTRACT")
        others = [p for p in group_persons if p not in d.render["directors"]]
        d.render["directors"] = [rng.choice(others)] if others else d.render["directors"][:-1]
    elif fault == "CONFLICT_OFFICE":
        d = _last(ent, "EXTRACT")
        d.render["office"] = _address(rng) + " - interno 2"
    elif fault == "CONFLICT_SHARE":
        d = _last(ent, "EXTRACT")
        d.render["holders"] = _other_table(rng, d.render["holders"], group_persons)
    elif fault == "SUM":
        d = rng.choice([x for x in ent.docs if "holders" in x.render])
        d.render["holders"] = _broken_sum(d.render["holders"], variant)
    elif fault == "SUPERSEDED_EDITION":
        d = [x for x in ent.docs if x.kind == "EXTRACT"][-2]
        if variant == "office":
            d.render["office"] = _address(rng) + " - scala B"
        elif variant == "capital":
            r, s, p = d.render["cap"]
            d.render["cap"] = (r + 500_000, s + 500_000 if s == r else s, p + 500_000 if p == r else p)
        else:
            others = [p for p in group_persons if p not in d.render["directors"]]
            d.render["directors"] = [rng.choice(others)] if others else d.render["directors"][:-1]
    elif fault == "FILENAME":
        if variant == "appointee":
            d = _last(ent, "APPOINTMENT")
            wrong = [p for p in group_persons if p not in d.render["directors"]]
            if wrong:
                d.filename = f"{d.date}_appointment_{rng.choice(wrong)}.txt"
            else:                       # every person of the group is a director: mislead on the date instead
                d.filename = f"{int(d.date[:4]) - 1}{d.date[4:]}_appointment_{d.render['directors'][0]}.txt"
        elif variant == "date":
            d = rng.choice(ent.docs)
            year = int(d.date[:4])
            d.filename = d.filename.replace(d.date, f"{year - 1}{d.date[4:]}", 1)
        elif variant == "kind":
            d = rng.choice([x for x in ent.docs if x.kind != "APPOINTMENT"])
            wrong = rng.choice(sorted(s for k, s in SLUGS.items() if k not in (d.kind, "APPOINTMENT")))
            d.filename = f"{d.date}_{wrong}.txt"
        else:
            d = rng.choice(ent.docs)
            d.folder = rng.choice([e for e in group_entities if e != ent.eid] or [ent.eid])
            d.filename = f"{d.date}_{SLUGS[d.kind]}_{ent.eid}.txt"
    elif fault == "MULTI_AMBIG":
        if variant == "resolution":
            d = _last(ent, "RESOLUTION")
            d.render["cap_style"] = "res_ambiguous"
        else:
            d = _last(ent, "EXTRACT")
            d.render["cap_style"] = "ambiguous" if variant == "extract_no_cues" else "partial_cues"
    elif fault == "ILLEGIBLE":
        if variant == "capital":
            d = _last(ent, "EXTRACT")
            d.render["cap_style"] = "split"
            d.render["cap_illegible"] = rng.choice(["resolved", "subscribed", "paid_in"])
        elif variant == "holders":
            d = rng.choice([x for x in ent.docs if x.kind in ("LEDGER", "EXTRACT")])
            rows = list(d.render["holders"])
            i = rng.randrange(len(rows))
            rows[i] = (rows[i][0], rng.choice(["4#%", "[illegible]", "#0%"]))
            d.render["holders"] = rows
        elif variant == "fin":
            d = _last(ent, "FIN")
            key = rng.choice(sorted(d.render["fin"]))
            d.render["fin"][key] = rng.choice(["[illegible]", "1#.###,00"])
        else:
            d = _last(ent, "RESOLUTION")
            d.render["cap_illegible"] = "resolved"
    elif fault == "RESTATED":
        return
    elif fault == "BARE":
        d = ent.docs[0]
        d.render["cap_style"] = "bare"
        return
    else:
        raise AssertionError(fault)
    d.faults.append(fault + (f":{ent.variant}" if ent.variant else ""))


def _other_table(rng: random.Random, rows: list[tuple[str, str]], group_persons: list[str]) -> list[tuple[str, str]]:
    """A different holders' table that still sums to the whole."""
    if len(rows) == 1:
        others = [p for p in group_persons if p != rows[0][0]]
        return [(rows[0][0], "90%"), (rng.choice(others), "10%")]
    a, b = rows[0], rows[1]
    if a[1] != b[1]:
        return [(a[0], b[1]), (b[0], a[1])] + rows[2:]
    from .gold import parse_share_text    # only to move five points between two equal shares
    fa, fb = parse_share_text(a[1]), parse_share_text(b[1])
    delta = min(fa, fb) / 10
    return [(a[0], share_text(fa + delta)), (b[0], share_text(fb - delta))] + rows[2:]


def _broken_sum(rows: list[tuple[str, str]], variant: str) -> list[tuple[str, str]]:
    """The same table with a sum that is not the whole: 99,99%, 100,01% or three times 33,33%."""
    from .gold import parse_share_text
    if variant == "thirds" and len(rows) == 3:
        return [(h, "33,33%") for h, _ in rows]
    delta = Fraction(1, 10000) * (1 if variant == "plus" else -1)
    h, s = rows[0]
    return [(h, share_text(parse_share_text(s) + delta))] + rows[1:]
