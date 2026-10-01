"""Inputs and expected values of scenarios S01-S10, written by hand in this file.

    python scenarios/make_inputs.py --check     # the committed files are exactly what this file says
    python scenarios/make_inputs.py --write     # (re)write scenarios/S0x/input and expected

Everything is synthetic: four invented companies of an invented test registry, six invented persons,
addresses in invented places of an invented province (ZZ), ``.example`` mail domains, tax codes that
begin with ``SYN-``. Every source document opens with the SYNTHETIC marker line.

The expected values are written here as literals. They are never copied from a run of the pipeline:
the checks compare what the pipeline produced with what this file says.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = "SYNTHETIC TEST DOCUMENT - fictitious entity, invented test registry, not an official record."

ENT = {
    "E-0001": ("Fornace Aurelia S.r.l.", "S.r.l."),
    "E-0002": ("Holding Aurelia Partecipazioni S.r.l.", "S.r.l."),
    "E-0003": ("Finanziaria Collelungo S.p.A.", "S.p.A."),
    "E-0004": ("Tessiture Monteverde S.r.l.", "S.r.l."),
}
PERSONS = {
    "P-001": ("Aldo Finti", "1961-02-03"),
    "P-002": ("Bice Provetti", "1968-07-19"),
    "P-003": ("Carlo Inventati", "1972-11-30"),
    "P-004": ("Dora Campione", "1959-04-12"),
    "P-005": ("Elio Simulati", "1980-09-08"),
    "P-006": ("Fulvia Posticci", "1977-01-25"),
}
LABEL = {**{k: v[0] for k, v in ENT.items()}, **{k: v[0] for k, v in PERSONS.items()}}

OFFICE_A = "Via del Collaudo 7, Borgoprova (ZZ)"
OFFICE_B = "Piazza del Campione 3, Montefinto (ZZ)"
OFFICE_C = "Via dei Prototipi 12, Collesintesi (ZZ)"
OFFICE_D = "Via della Prova 21, Selvaprototipo (ZZ)"
OFFICE_E = "Via del Segnaposto 5, Campomodello (ZZ)"

FULL = "The share capital is EUR {a}, fully subscribed and fully paid in."


# ----------------------------------------------------------------------------------------------
# documents

def _doc_id(eid: str, n: int) -> str:
    return f"DOC-{eid.replace('-', '')}-{n:02d}"


def _head(eid: str, n: int, type_label: str, date: str, edition: str, fy: str = "") -> list[str]:
    lines = [MARKER, f"Document id: {_doc_id(eid, n)}", f"Document type: {type_label}",
             f"Document date: {date}", f"Edition: {edition}",
             f"Entity: {ENT[eid][0]} (test registry no. TEST-REG-00{eid[2:]})"]
    if fy:
        lines.append(f"Financial year: {fy}")
    return lines + [""]


def _holders(rows: list[tuple[str, str]]) -> list[str]:
    return [f"- {h} ({LABEL[h]}): {share}" for h, share in rows]


def _directors(ids: list[str]) -> list[str]:
    return [f"- {p} ({LABEL[p]})" for p in ids]


def _file(eid: str, name: str, lines: list[str]) -> tuple[str, str]:
    return f"entities/{eid}/{name}", "\n".join(lines) + "\n"


def deed(eid, n, date, office, capital, holders, directors):
    name, form = ENT[eid]
    return _file(eid, f"{date}_deed.txt", _head(eid, n, "Deed of incorporation", date, "DEED/1") + [
        f"1. Name and form. The company is named {name}; its legal form is {form}",
        f"2. Registered office. The registered office is at {office}.",
        f"3. Share capital. {capital}",
        "4. Holders.", *_holders(holders), "",
        "5. Directors.", *_directors(directors)])


def extract(eid, n, date, ed, office, capital, holders, directors):
    name, form = ENT[eid]
    return _file(eid, f"{date}_registry-extract.txt", _head(eid, n, "Test registry extract", date, f"EXTRACT/{ed}") + [
        f"Name: {name}", f"Legal form: {form}", f"Registered office: {office}", capital,
        "Holders:", *_holders(holders), "",
        "Directors:", *_directors(directors)])


def repeat(eid, n, date, ed, office, amount, holders, directors):
    """A registry extract that repeats a deed: since v2.0.8 (D37, rules/extract.json address_corroboration) an address
    is a fact only when a second document states it alike, and a deed alone keeps every field [TO CONFIRM]."""
    return extract(eid, n, date, ed, office, f"Share capital: resolved EUR {amount}; subscribed and paid in EUR {amount}",
                   holders, directors)


def resolution(eid, n, date, sentence):
    return _file(eid, f"{date}_capital-resolution.txt",
                 _head(eid, n, "Resolution on share capital", date, "RESOLUTION/1") + [
                     "Minutes of the holders' meeting (synthetic).", sentence])


def transfer(eid, n, date, holders):
    return _file(eid, f"{date}_share-transfer.txt", _head(eid, n, "Share transfer notice", date, "TRANSFER/1") + [
        "Notice of a transfer of shares (synthetic).", "Holders after the transfer:", *_holders(holders)])


def appointment(eid, n, date, directors, name_says):
    return _file(eid, f"{date}_appointment_{name_says}.txt",
                 _head(eid, n, "Appointment of directors", date, "APPOINTMENT/1") + [
                     "Minutes of the holders' meeting (synthetic).",
                     "Directors in office after this appointment:", *_directors(directors)])


def office_transfer(eid, n, date, sentence):
    return _file(eid, f"{date}_office-transfer.txt",
                 _head(eid, n, "Transfer of registered office", date, "OFFICE/1") + [sentence])


def fin(eid, n, date, fy, net_equity, total_assets, revenue):
    return _file(eid, f"{date}_financial-summary.txt",
                 _head(eid, n, "Financial statements summary", date, f"FIN-FY{fy}/1", fy) + [
                     f"Net equity: EUR {net_equity}", f"Total assets: EUR {total_assets}", f"Revenue: EUR {revenue}"])


def _json(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def identity(ids: list[str]) -> tuple[str, str]:
    data = {}
    for p in ids:
        name, born = PERSONS[p]
        data[p] = {"name": name, "born": born, "tax_code": f"SYN-CF-{p.replace('-', '')}",
                   "email": name.lower().replace(" ", ".") + "@persons.example"}
    return "identity/persons.json", _json(data)


def config(sid: str, as_of: str | None) -> tuple[str, str]:
    cfg = {"shareable_salt": f"scenario-salt-{sid}", "synthetic": True}
    if as_of:
        cfg["as_of"] = as_of
    return "config.json", _json(cfg)


def root(sid: str, as_of: str | None, persons: list[str], docs: list[tuple[str, str]], prefix: str = "") -> dict:
    """One input root: config, identity layer, source documents."""
    return {prefix + k: v for k, v in [config(sid, as_of), identity(persons), *docs]}


def src(eid: str, n: int, date: str, edition: str) -> list[str]:
    return [_doc_id(eid, n), date, edition]


# ----------------------------------------------------------------------------------------------
# the ten scenarios: (input files, expected values)

def s01():
    h = [("P-001", "60%"), ("P-002", "40%")]
    files = root("S01", "2026-03-31", ["P-001", "P-002"], [
        deed("E-0001", 1, "2025-03-10", OFFICE_A, FULL.format(a="50.000,00"), h, ["P-001"]),
        extract("E-0001", 2, "2026-02-02", 1, OFFICE_A,
                "Share capital: resolved EUR 80.000,00; subscribed and paid in EUR 80.000,00", h, ["P-001"]),
    ])
    both = {"status": "DISCREPANCY", "values": [
        {"value": "50000.00", "sources": [src("E-0001", 1, "2025-03-10", "DEED/1")]},
        {"value": "80000.00", "sources": [src("E-0001", 2, "2026-02-02", "EXTRACT/1")]}]}
    exp = {"entity": "E-0001", "exit_code": 0, "fields": {
        "share_capital.resolved": both, "share_capital.subscribed": both, "share_capital.paid_in": both,
        "name": {"status": "STATED", "value": "Fornace Aurelia S.r.l."},
        "registered_office": {"status": "STATED", "value": OFFICE_A},
        "directors": {"status": "STATED", "value": ["P-001"]},
        "shareholders": {"status": "STATED", "value": [{"holder": "P-001", "share": "3/5"},
                                                       {"holder": "P-002", "share": "2/5"}]}},
        "docx_discrepancy_rows": [
            ["share_capital.resolved", "EUR 50.000,00", "DOC-E0001-01", "2025-03-10", "DEED/1"],
            ["share_capital.resolved", "EUR 80.000,00", "DOC-E0001-02", "2026-02-02", "EXTRACT/1"]],
        "fields_never_shown_as_fact": ["share_capital.resolved", "share_capital.subscribed",
                                       "share_capital.paid_in"]}
    return files, exp


def s02():
    def one(prefix, share):
        h = [("P-001", share), ("P-002", share), ("P-003", share)]
        return root("S02", "2026-03-31", ["P-001", "P-002", "P-003"], [
            deed("E-0003", 1, "2024-06-03", OFFICE_C, FULL.format(a="300.000,00"), h, ["P-001"]),
            repeat("E-0003", 2, "2024-07-01", 1, OFFICE_C, "300.000,00", h, ["P-001"])], prefix)
    files = {**one("percent/", "33,33%"), **one("exact/", "1/3")}
    exp = {"entity": "E-0003",
           "percent": {"exit_code": 2, "status": "BLOCKED", "sum": "9999/10000", "published": False,
                       "last_line": "RUN BLOCKED - not everything was published"},
           "exact": {"exit_code": 0, "status": "OK", "published": True, "sum": "1/1",
                     "cap_table": [{"holder": "P-001", "share": "1/3"}, {"holder": "P-002", "share": "1/3"},
                                   {"holder": "P-003", "share": "1/3"}]}}
    return files, exp


def s03():
    h = [("P-004", "70%"), ("P-005", "30%")]
    cap = "Share capital: resolved EUR 120.000,00; subscribed EUR 100.000,00; paid in EUR 75.000,00"
    files = root("S03", "2026-06-30", ["P-004", "P-005"], [
        deed("E-0004", 1, "2023-09-18", OFFICE_D, FULL.format(a="75.000,00"), h, ["P-004"]),
        resolution("E-0004", 2, "2025-10-06",
                   "The meeting resolved to increase the share capital from EUR 75.000,00 to EUR 120.000,00; "
                   "after the increase the subscribed capital is EUR 100.000,00 and the paid-in capital is "
                   "EUR 75.000,00."),
        extract("E-0004", 3, "2026-01-12", 1, OFFICE_D, cap, h, ["P-004"]),
        fin("E-0004", 4, "2026-04-20", "2025", "412.300,50", "1.905.118,00", "2.240.760,25"),
    ])
    files["tamper.json"] = _json({"reading": "Each entry is applied to a fresh copy of the entity record of a "
                                             "valid run; the run is then repeated from the tampered record.",
                                  "tampers": [
        {"name": "source_doc removed from one figure", "field": "share_capital.resolved",
         "doc": "DOC-E0004-03", "op": "drop", "key": "source_doc", "reason_contains": "source_doc"},
        {"name": "source date blanked on one figure", "field": "fin.FY2025.net_equity",
         "doc": "DOC-E0004-04", "op": "set", "key": "source_date", "to": "", "reason_contains": "source_date"},
        {"name": "edition blanked on one figure", "field": "registered_office",
         "doc": "DOC-E0004-03", "op": "set", "key": "edition", "to": "", "reason_contains": "edition"},
        {"name": "value changed, source kept", "field": "fin.FY2025.revenue",
         "doc": "DOC-E0004-04", "op": "set", "key": "value", "to": "9240760.25",
         "reason_contains": "not supported by the quoted source lines"}]})
    exp = {"entity": "E-0004",
           "valid": {"exit_code": 0, "all_figures_sourced": True, "minimum_figures": 12,
                     "fields": {"share_capital.resolved": {"status": "STATED", "value": "120000.00"},
                                "share_capital.subscribed": {"status": "STATED", "value": "100000.00"},
                                "share_capital.paid_in": {"status": "STATED", "value": "75000.00"},
                                "fin.FY2025.revenue": {"status": "STATED", "value": "2240760.25"}}},
           "every_tamper": {"exit_code": 3, "status": "FAILED", "published": False}}
    return files, exp


OUTGOING_STALE = {
    "outgoing/letter-bank-2026-02-10.txt": (
        "Date: 2026-02-10\n\nTo: Banca di Prova (synthetic)\nRe: Fornace Aurelia S.r.l.\n\n"
        "The share capital of Fornace Aurelia S.r.l. is EUR 50.000,00, fully paid in.\n", 6),
    "outgoing/company-profile-2026-03-02.txt": (
        "Date: 2026-03-02\n\nCompany profile (synthetic)\n"
        "Fornace Aurelia S.r.l. - share capital € 50.000,00\n", 4),
    "outgoing/supplier-form-2026-02-20.txt": (
        "Date: 2026-02-20\n\nSupplier qualification form (synthetic)\nCompany: Fornace Aurelia S.r.l.\n"
        "Share capital: 50,000.00 EUR\n", 5),
    "outgoing/email-signature-2026-03-05.txt": (
        "Date: 2026-03-05\n\n--\nFornace Aurelia S.r.l.\nRegistered office: " + OFFICE_A + "\n"
        "Share capital EUR 50000 fully paid in\n", 6),
    "outgoing/tender-declaration-2026-03-12.txt": (
        "Date: 2026-03-12\n\nDeclaration for a tender (synthetic)\n"
        "The undersigned declares that Fornace Aurelia S.r.l. has a share capital of euro 50.000.\n", 4),
}
OUTGOING_DECOYS = {
    "outgoing/letter-bank-2025-11-03.txt": (
        "Date: 2025-11-03\n\nFornace Aurelia S.r.l. - share capital EUR 50.000,00 fully paid in\n",
        "written before the increase: the value was current on its date"),
    "outgoing/invoice-2026-02-14.txt": (
        "Date: 2026-02-14\n\nInvoice to Fornace Aurelia S.r.l., total EUR 50.000,00\n",
        "same amount, not the share capital"),
    "outgoing/board-note-2026-02-01.txt": (
        "Date: 2026-02-01\n\nUntil the increase the share capital of Fornace Aurelia was EUR 50.000,00.\n",
        "the line presents the amount as past"),
    "outgoing/holding-profile-2026-03-02.txt": (
        "Date: 2026-03-02\n\nHolding Aurelia Partecipazioni S.r.l. - share capital EUR 50.000,00\n",
        "another entity whose capital really is this amount"),
    "outgoing/generic-note-2026-03-03.txt": (
        "Date: 2026-03-03\n\nThe share capital amounts to EUR 50.000,00.\n",
        "no entity named"),
    "outgoing/letter-bank-2026-03-20.txt": (
        "Date: 2026-03-20\n\nFornace Aurelia S.r.l. - share capital EUR 80.000,00 fully paid in\n",
        "already carries the new value"),
    "outgoing/guarantee-2026-02-25.txt": (
        "Date: 2026-02-25\n\nGuarantee issued in favour of Fornace Aurelia S.r.l. up to EUR 50.000,00.\n",
        "same amount, a guarantee"),
    "outgoing/press-note-2026-01-20.txt": (
        "Date: 2026-01-20\n\nFornace Aurelia S.r.l. increased its share capital from EUR 50.000,00 to "
        "EUR 80.000,00.\n", "the old amount is introduced by 'from'"),
    "outgoing/group-overview-2026-03-01.txt": (
        "Date: 2026-03-01\n\nFornace Aurelia S.r.l. - share capital EUR 80.000,00\n"
        "Holding Aurelia Partecipazioni S.r.l. - share capital EUR 50.000,00\n",
        "two entities in two lines: the old amount belongs to the other one"),
    "outgoing/investment-plan-2026-02-27.txt": (
        "Date: 2026-02-27\n\nCapital expenditure plan of Fornace Aurelia S.r.l.: EUR 50.000,00 for the new kiln.\n",
        "the word 'capital' without 'share capital'"),
}


def s04():
    h1 = [("P-001", "60%"), ("E-0002", "40%")]
    h2 = [("P-001", "50%"), ("P-002", "50%")]
    files = root("S04", "2026-03-31", ["P-001", "P-002"], [
        deed("E-0001", 1, "2025-03-10", OFFICE_A, FULL.format(a="50.000,00"), h1, ["P-001"]),
        resolution("E-0001", 2, "2026-01-15",
                   "The meeting resolved to increase the share capital from EUR 50.000,00 to EUR 80.000,00. "
                   "The increase has been fully subscribed and fully paid in."),
        extract("E-0001", 3, "2026-02-02", 1, OFFICE_A,
                "Share capital: resolved EUR 80.000,00; subscribed and paid in EUR 80.000,00", h1, ["P-001"]),
        deed("E-0002", 1, "2025-05-05", OFFICE_C, FULL.format(a="50.000,00"), h2, ["P-002"]),
        repeat("E-0002", 2, "2025-06-02", 1, OFFICE_C, "50.000,00", h2, ["P-002"]),
    ])
    files.update({k: v[0] for k, v in OUTGOING_STALE.items()})
    files.update({k: v[0] for k, v in OUTGOING_DECOYS.items()})
    exp = {"entity": "E-0001", "exit_code": 0, "files_scanned": 15,
           "stale": [{"file": k.split("/", 1)[1], "line": v[1]} for k, v in sorted(OUTGOING_STALE.items())],
           "decoys": {k.split("/", 1)[1]: v[1] for k, v in sorted(OUTGOING_DECOYS.items())},
           "max_false_positives": 1,
           "every_finding": {"old_value": "50000.00", "new_value": "80000.00",
                             "changed_on": "2026-01-15", "changed_by_doc": "DOC-E0001-02",
                             "changed_by_edition": "RESOLUTION/1",
                             "new_source_doc": "DOC-E0001-03", "new_edition": "EXTRACT/1"},
           "capital_now": {"status": "STATED", "value": "80000.00",
                           "sources": [src("E-0001", 2, "2026-01-15", "RESOLUTION/1"),
                                       src("E-0001", 3, "2026-02-02", "EXTRACT/1")]}}
    return files, exp


def s05():
    before = [("P-001", "60%"), ("P-002", "40%")]
    after = [("P-001", "40%"), ("P-002", "40%"), ("P-003", "20%")]
    files = root("S05", None, ["P-001", "P-002", "P-003"], [
        deed("E-0002", 1, "2025-05-05", OFFICE_C, FULL.format(a="100.000,00"), before, ["P-001"]),
        repeat("E-0002", 2, "2025-06-02", 1, OFFICE_C, "100.000,00", before, ["P-001"]),
        transfer("E-0002", 3, "2026-02-20", after),
        appointment("E-0002", 4, "2026-05-11", ["P-002", "P-003"], "P-002"),
        extract("E-0002", 5, "2026-06-15", 2, OFFICE_C,
                "Share capital: resolved EUR 100.000,00; subscribed and paid in EUR 100.000,00",
                after, ["P-002", "P-003"]),
    ])
    files["plan.json"] = _json({"entity": "E-0002", "runs_as_of": ["2026-01-31", "2026-03-31", "2026-06-30"],
                                "asked": ["2026-01-15", "2026-01-31", "2026-03-31", "2026-04-30", "2026-06-30"]})
    t0 = [{"holder": "P-001", "share": "3/5"}, {"holder": "P-002", "share": "2/5"}]
    t1 = [{"holder": "P-001", "share": "2/5"}, {"holder": "P-002", "share": "2/5"},
          {"holder": "P-003", "share": "1/5"}]
    exp = {"entity": "E-0002", "snapshots": 3,
           "answers": {
               "2026-01-15": None,
               "2026-01-31": {"as_of": "2026-01-31", "shareholders": t0, "directors": ["P-001"]},
               "2026-03-31": {"as_of": "2026-03-31", "shareholders": t1, "directors": ["P-001"]},
               "2026-04-30": {"as_of": "2026-03-31", "shareholders": t1, "directors": ["P-001"]},
               "2026-06-30": {"as_of": "2026-06-30", "shareholders": t1, "directors": ["P-002", "P-003"]}}}
    return files, exp


def s06():
    h = [("P-004", "50%"), ("P-005", "30%"), ("P-006", "20%")]
    files = root("S06", "2026-03-31", ["P-004", "P-005", "P-006"], [
        deed("E-0003", 1, "2024-06-03", OFFICE_C, FULL.format(a="300.000,00"), h, ["P-004"]),
        appointment("E-0003", 2, "2026-03-02", ["P-006"], "P-005"),
    ])
    exp = {"entity": "E-0003", "exit_code": 0,
           "directors": {"status": "STATED", "value": ["P-006"],
                         "source": src("E-0003", 2, "2026-03-02", "APPOINTMENT/1")},
           "filename_divergences": [{"doc_id": "DOC-E0003-02", "aspect": "appointee",
                                     "filename_says": "P-005", "content_says": "P-006"}],
           "never_a_director": "P-005"}
    return files, exp


def s07():
    files = root("S07", "2026-03-31", ["P-001", "P-002", "P-003"], [
        deed("E-0001", 1, "2025-03-10", OFFICE_A, FULL.format(a="50.000,00"),
             [("P-001", "30%"), ("E-0002", "70%")], ["P-001"]),
        repeat("E-0001", 2, "2025-04-07", 1, OFFICE_A, "50.000,00", [("P-001", "30%"), ("E-0002", "70%")], ["P-001"]),
        deed("E-0002", 1, "2025-05-05", OFFICE_C, FULL.format(a="100.000,00"),
             [("P-002", "90%"), ("E-0003", "10%")], ["P-002"]),
        repeat("E-0002", 2, "2025-06-02", 1, OFFICE_C, "100.000,00", [("P-002", "90%"), ("E-0003", "10%")], ["P-002"]),
        deed("E-0003", 1, "2024-06-03", OFFICE_E, FULL.format(a="300.000,00"),
             [("P-003", "80%"), ("E-0002", "20%")], ["P-003"]),
        repeat("E-0003", 2, "2024-07-01", 1, OFFICE_E, "300.000,00", [("P-003", "80%"), ("E-0002", "20%")], ["P-003"]),
    ])
    files["policy_override.json"] = _json({"file": "ownership.json", "parameter": "cycle_policy",
                                           "value": "closure"})
    exp = {"entity": "E-0002", "cycles": [["E-0002", "E-0003"]],
           "abstain": {"exit_code": 0, "outcome": "TO_CONFIRM", "effective": None,
                       "also_to_confirm": ["E-0001", "E-0003"]},
           "closure": {"exit_code": 0, "outcome": "RESOLVED", "method": "closure",
                       "effective": {"E-0001": {"P-001": "3/10", "P-002": "9/14", "P-003": "2/35"},
                                     "E-0002": {"P-002": "45/49", "P-003": "4/49"},
                                     "E-0003": {"P-002": "9/49", "P-003": "40/49"}}}}
    return files, exp


def s08():
    files = root("S08", "2026-03-31", ["P-001", "P-002", "P-004"], [
        deed("E-0004", 1, "2023-09-18", OFFICE_D, FULL.format(a="75.000,00"),
             [("P-004", "55%"), ("E-0002", "45%")], ["P-004"]),
        repeat("E-0004", 2, "2023-10-16", 1, OFFICE_D, "75.000,00", [("P-004", "55%"), ("E-0002", "45%")], ["P-004"]),
        deed("E-0002", 1, "2025-05-05", OFFICE_C, FULL.format(a="100.000,00"),
             [("P-001", "60%"), ("P-002", "40%")], ["P-001"]),
        repeat("E-0002", 2, "2025-06-02", 1, OFFICE_C, "100.000,00", [("P-001", "60%"), ("P-002", "40%")], ["P-001"]),
    ])
    exp = {"entity": "E-0004", "exit_code": 0, "salt": "scenario-salt-S08",
           "edges": [{"holder": "P-001", "held": "E-0002", "share": "3/5"},
                     {"holder": "P-002", "held": "E-0002", "share": "2/5"},
                     {"holder": "E-0002", "held": "E-0004", "share": "9/20"},
                     {"holder": "P-004", "held": "E-0004", "share": "11/20"}],
           "effective": {"P-001": "27/100", "P-002": "9/50", "P-004": "11/20"},
           "identity_strings_that_must_not_appear": 15}
    return files, exp


def s09():
    moved = f"The seat of the company is moved from {OFFICE_A} to {OFFICE_B}."
    files = root("S09", "2026-03-31", ["P-001", "P-002", "P-004"], [
        deed("E-0001", 1, "2025-03-10", OFFICE_A, FULL.format(a="50.000,00"),
             [("P-001", "60%"), ("P-002", "40%")], ["P-001"]),
        office_transfer("E-0001", 2, "2026-02-09", moved),
        # v2.0.8 (D37): a later extract repeats the new address, so that the address the transfer states is
        # corroborated (rules/extract.json ADR-020); without it the new office stays [TO CONFIRM] (DISC-038)
        extract("E-0001", 3, "2026-03-02", 1, OFFICE_B, "Share capital: resolved EUR 50.000,00; subscribed EUR "
                "50.000,00; paid in EUR 50.000,00", [("P-001", "60%"), ("P-002", "40%")], ["P-001"]),
        deed("E-0004", 1, "2023-09-18", OFFICE_D, FULL.format(a="75.000,00"),
             [("P-004", "100%")], ["P-004"]),
    ])
    files["rule_patch.json"] = _json({
        "file": "extract.json", "insert_before": "EXT-OFFICE-010", "new_version": "2.0.0+S09",
        "rule": {"id": "EXT-OFFICE-005", "field": "registered_office", "extractor": "text", "nature": "text",
                 "kinds": ["OFFICE"],
                 "line_matches": "The seat of the company is moved from (?P<previous>.+?) to (?P<value>.+)\\.$",
                 "rationale": "Exception on top: a second wording of the office transfer.",
                 "tests": [{"kind": "OFFICE", "text": moved, "expect": OFFICE_B, "expect_previous": OFFICE_A}]}})
    exp = {"entity": "E-0001", "control_entity": "E-0004",
           "before": {"exit_code": 0, "registered_office": {"status": "TO_CONFIRM"}},
           "after": {"exit_code": 0, "registered_office": {
               "status": "STATED", "value": OFFICE_B,       # v2.0.8: the latest current source, which repeats it
               "source": src("E-0001", 3, "2026-03-02", "EXTRACT/1")}},
           "diff": [{"entity": "E-0001", "field": "registered_office",
                     "before": {"status": "TO_CONFIRM"},
                     "after": {"status": "STATED", "value": OFFICE_B, "source_doc": "DOC-E0001-03"}}]}
    return files, exp


def s10():
    h = [("P-004", "50%"), ("P-005", "30%"), ("P-006", "20%")]
    base = [
        deed("E-0003", 1, "2024-06-03", OFFICE_C, FULL.format(a="300.000,00"), h, ["P-004"]),
        resolution("E-0003", 2, "2026-04-14",
                   "The meeting resolved to increase the share capital from EUR 300.000,00 to EUR 500.000,00; "
                   "after the increase the subscribed capital is EUR 400.000,00 and the paid-in capital is "
                   "EUR 250.000,00."),
    ]
    vague = extract("E-0003", 3, "2026-05-20", 1, OFFICE_C,
                    "Share capital: resolved EUR 500.000,00, of which EUR 400.000,00 and EUR 250.000,00",
                    h, ["P-004"])
    persons = ["P-004", "P-005", "P-006"]
    files = {**root("S10", "2026-06-30", persons, base, "clear/"),
             **root("S10", "2026-06-30", persons, base + [vague], "insufficient/")}
    res = src("E-0003", 2, "2026-04-14", "RESOLUTION/1")
    exp = {"entity": "E-0003",
           "clear": {"exit_code": 0, "fields": {
               "share_capital.resolved": {"status": "STATED", "value": "500000.00", "source": res},
               "share_capital.subscribed": {"status": "STATED", "value": "400000.00", "source": res},
               "share_capital.paid_in": {"status": "STATED", "value": "250000.00", "source": res}},
               "natures_of_the_clause": {"300000.00": "historical", "500000.00": "resolved",
                                         "400000.00": "subscribed", "250000.00": "paid_in"}},
           "insufficient": {"exit_code": 0, "fields": {
               "share_capital.resolved": {"status": "STATED", "value": "500000.00"},
               "share_capital.subscribed": {"status": "TO_CONFIRM"},
               "share_capital.paid_in": {"status": "TO_CONFIRM"}},
               "readable_not_fact": {"share_capital.subscribed": ["400000.00"],
                                     "share_capital.paid_in": ["250000.00"]}}}
    return files, exp


SCENARIOS = {"S01": s01, "S02": s02, "S03": s03, "S04": s04, "S05": s05,
             "S06": s06, "S07": s07, "S08": s08, "S09": s09, "S10": s10}


def all_files() -> dict[str, bytes]:
    """relative path under scenarios/ -> bytes (UTF-8, LF)."""
    out: dict[str, bytes] = {}
    for sid, fn in SCENARIOS.items():
        files, exp = fn()
        for rel, text in files.items():
            out[f"{sid}/input/{rel}"] = text.encode("utf-8")
        out[f"{sid}/expected/expected.json"] = _json(exp).encode("utf-8")
    return out


def check() -> list[str]:
    want = all_files()
    problems = []
    for rel, data in sorted(want.items()):
        p = HERE / rel
        if not p.exists():
            problems.append(f"missing: {rel}")
        elif p.read_bytes() != data:
            problems.append(f"differs: {rel}")
    have = {p.relative_to(HERE).as_posix() for sid in SCENARIOS for sub in ("input", "expected")
            for p in (HERE / sid / sub).rglob("*") if p.is_file()}
    problems += [f"not declared in make_inputs.py: {rel}" for rel in sorted(have - set(want))]
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.write:
        for rel, data in sorted(all_files().items()):
            p = HERE / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        print(f"written: {len(all_files())} files")
    problems = check()
    for line in problems:
        print(line)
    print("scenario inputs OK" if not problems else f"scenario inputs: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
