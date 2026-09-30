"""Text of the synthetic source documents, from the document plan.

Every document opens with the SYNTHETIC marker line. The layout imitates no official record: the
"test registry extract" is a plain list of ``Key: value`` lines of an invented test registry.
"""
from __future__ import annotations

from .world import TYPE_LABELS, Doc, World, _amount_text

MARKER = "SYNTHETIC TEST DOCUMENT - fictitious entity, invented test registry, not an official record."
ILLEGIBLE_AMOUNT = "8#.###,00"


def header(doc: Doc, world: World) -> list[str]:
    ent = world.entities[doc.entity]
    lines = [MARKER,
             f"Document id: {doc.doc_id}",
             f"Document type: {TYPE_LABELS[doc.kind]}",
             f"Document date: {doc.date}",
             f"Edition: {doc.edition}",
             f"Entity: {world.labels[doc.entity]} (test registry no. {ent.registry_no})"]
    if doc.kind == "FIN":
        lines.append(f"Financial year: {doc.fy}")
    return lines


def _eur(doc: Doc, nature: str, cents: int) -> str:
    if doc.render.get("cap_illegible") == nature:
        return f"EUR {ILLEGIBLE_AMOUNT}"
    return f"EUR {_amount_text(cents)}"


def capital_clause(doc: Doc) -> str:
    r, s, p = doc.render["cap"]
    style = doc.render["cap_style"]
    R, S, P = _eur(doc, "resolved", r), _eur(doc, "subscribed", s), _eur(doc, "paid_in", p)
    if style == "full":
        return f"3. Share capital. The share capital is {R}, fully subscribed and fully paid in."
    if style == "bare":
        return f"3. Share capital. The share capital is {R}."
    if style == "split":
        return f"Share capital: resolved {R}; subscribed {S}; paid in {P}"
    if style == "combined":
        return f"Share capital: resolved {R}; subscribed and paid in {S}"
    if style == "ambiguous":
        return f"Share capital: {R}, of which {S} and {P}"
    if style == "partial_cues":
        return f"Share capital: resolved {R}, of which {S} and {P}"
    prev = f"EUR {_amount_text(doc.render['prev_cap'])}"
    if style == "res_full":
        return (f"The meeting resolved to increase the share capital from {prev} to {R}. "
                f"The increase has been fully subscribed and fully paid in.")
    if style == "res_partial":
        return (f"The meeting resolved to increase the share capital from {prev} to {R}; after the increase "
                f"the subscribed capital is {S} and the paid-in capital is {P}.")
    if style == "res_ambiguous":
        return f"The meeting resolved to increase the share capital from {prev} to {R}, with {S} and {P}."
    raise ValueError(style)


def holder_lines(doc: Doc, world: World) -> list[str]:
    return [f"- {h} ({world.labels[h]}): {share}" for h, share in doc.render["holders"]]


def director_lines(doc: Doc, world: World) -> list[str]:
    return [f"- {p} ({world.labels[p]})" for p in doc.render["directors"]]


def body(doc: Doc, world: World) -> list[str]:
    r = doc.render
    if doc.kind == "DEED":
        return [f"1. Name and form. The company is named {r['name']}; its legal form is {r['form']}",
                f"2. Registered office. The registered office is at {r['office']}.",
                capital_clause(doc),
                "4. Holders.", *holder_lines(doc, world), "",
                "5. Directors.", *director_lines(doc, world)]
    if doc.kind == "EXTRACT":
        return [f"Name: {r['name']}", f"Legal form: {r['form']}", f"Registered office: {r['office']}",
                capital_clause(doc),
                "Holders:", *holder_lines(doc, world), "",
                "Directors:", *director_lines(doc, world)]
    if doc.kind == "RESOLUTION":
        return ["Minutes of the holders' meeting (synthetic).", capital_clause(doc)]
    if doc.kind == "TRANSFER":
        return ["Notice of a transfer of shares (synthetic).", "Holders after the transfer:",
                *holder_lines(doc, world)]
    if doc.kind == "APPOINTMENT":
        return ["Minutes of the holders' meeting (synthetic).", "Directors in office after this appointment:",
                *director_lines(doc, world)]
    if doc.kind == "OFFICE":
        return [f"The registered office is transferred from {r['prev_office']} to {r['office']}."]
    if doc.kind == "LEDGER":
        return ["Holders as at the document date:", *holder_lines(doc, world)]
    if doc.kind == "FIN":
        return [f"Net equity: EUR {r['fin']['net_equity']}", f"Total assets: EUR {r['fin']['total_assets']}",
                f"Revenue: EUR {r['fin']['revenue']}"]
    raise ValueError(doc.kind)


def render(doc: Doc, world: World) -> str:
    return "\n".join(header(doc, world) + [""] + body(doc, world)) + "\n"
