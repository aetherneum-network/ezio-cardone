# CLAIMS

SYNTHETIC - every claim below is about a test pipeline that runs on invented data. "Demonstrated" means:
there is a scenario or a test in this repository that fails if the claim stops being true **on the
synthetic data of this repository**. It never means accuracy on real companies, and it is not a legal
opinion. The author is a synthetic AI agent, not a lawyer, a notary, an accountant or an auditor.

Three statuses are used, and only these three:

- **demonstrated** - by the scenario or test named in the row;
- **not demonstrated: out of v2.0** - nothing in this repository supports the sentence;
- **awaiting legal review — not touched** - the sentence is left exactly as it was, neither edited nor removed.

## 1. Claims demonstrated in v2.0

| # | Sentence of the profile (README) | Status | Where it would fail |
|---|---|---|---|
| A1 | "Every figure in the rendered dossier carries the source document it came from and that document's date." | demonstrated | `scenarios/S03` (every figure of a valid dossier has document, date and edition; four tampered records are refused), `scenarios/S04` (a superseded figure in outgoing text is traced to the edition that replaced it), `scenarios/S10` (boundary: the nature of each amount), `tests/test_never_event.py`, `tests/test_amount_grouping.py` (since v2.0.1: an amount is read whole or abstained; the audit refuses a figure whose digits are not those of its quote) |
| A2 | "Conflicting sources are surfaced side by side rather than silently reconciled" | demonstrated; **downgraded at `v2.0.3-freeze`** (section 7) **and at `v2.0.7-freeze`** (section 8) **and at `v2.0.8-freeze`** (section 10) | `scenarios/S01` (deed vs registry extract on share capital), `scenarios/S06` (file name vs content), `tests/test_never_event.py` (a discrepancy collapsed to one value is refused by the builder and caught by the audit; ties are never broken by a guess) |
| A3 | "a cap table that does not resolve to 100% per entity is blocked, not footnoted" | demonstrated | `scenarios/S02` (3 x 33,33% = 9999/10000 is blocked, 3 x 1/3 builds), `scenarios/S07` (cross-holding: reported, never silently resolved), `tests/test_ownership.py` (exact fractions against an independent reference), `tests/test_amount_grouping.py` (since v2.0.1: a holders' table that could not be read blocks the entity, rule `OWN-015`), `tests/test_holders_forms.py` (since v2.0.2, owner decision D26: `OWN-015` stays `block`; a reworded holders' heading is read, a document of unrecognised type is checked and blocks only when it may hold a table that is not read, a table read there that does not sum blocks by `OWN-010`), `tests/test_d30_forms.py` (since v2.0.3, owner decision D30: more headings and holder lines are read, shares in words, counts of quotas only with one total stated in the same document; counts that do not add up to it block by `OWN-010`; the forms still not read keep blocking) |
| A4 | "the dossier is a build artifact regenerated from the entity-record JSON, never hand-assembled" | demonstrated | `scenarios/S09` (a rule change moves only the expected field; the diff is reported), `tests/test_determinism.py` (same inputs, same bytes, DOCX included; a rebuild from the records gives the same dossier), `tools/rebuild.py` |
| A5 | "\"what did this entity look like in March\" is always answerable, because no snapshot is ever overwritten" | demonstrated | `scenarios/S05`, `tests/test_snapshot.py` |
| A6 | "Identity-data separation — ... the graph structure stays shareable" | demonstrated, **in part** | `scenarios/S08`, `tests/test_shareable.py`: the shareable layer contains no string of the identity layer and keeps the graph under opaque identifiers. See row N3 for the part that is not demonstrated. |

Related sentences of the profile covered by the same evidence:

| Sentence | Status | Where |
|---|---|---|
| "the ownership graph is sum-checked to 100% per node before it is allowed to render" | demonstrated | A3 |
| "Ownership-graph construction — directed shareholding graphs (entity → entity → natural person), percentages sum-checked per node" | demonstrated | A3, `scenarios/S08` |
| "Cross-source discrepancy detection — stated capital, officers, and registered address compared across deed vs registry, divergence surfaced with provenance" | demonstrated on synthetic data | A2; capital in `scenarios/S01`; officers, address and holders only through the generated suites scored by `eval/score.py` |
| "Provenance-per-fact indexing — every figure linked to its source document and that document's date" | demonstrated | A1 |
| "Versioned dossier snapshots — a dated snapshot on each material change" | demonstrated | A5 |
| "Deterministic document build" | demonstrated on Windows only | A4; identity between operating systems is not verified |
| "Will not round a figure to make a table look tidy, and will not let a cap table render until its percentages resolve to a hundred" | demonstrated | A3, `tests/test_numbers.py` |
| "lets a human adjudicate — the discrepancy is the finding" | demonstrated | A2; the parameter `adjudication` is `none` in `rules/discrepancy.json` |

## 2. Claims not demonstrated

| # | Sentence of the profile (README) | Status | Note |
|---|---|---|---|
| N1 | "Statutory-obligation calendars — filing and renewal deadlines derived from legal form and jurisdiction, not hand-maintained" | not demonstrated: out of v2.0 | Statutory deadlines are legal content. Nothing in this repository computes, stores or checks a statutory deadline (`tests/test_hygiene.py` fails if such a module appears). Decision 1 of the approved plan. |
| N2 | "He has carried entity records through capital increases, new shareholders, and changes of officer without once losing the audit line from a figure back to its source." | not demonstrated: out of v2.0 | A statement about past work that no file here can prove. The same events exist only as synthetic scenarios (S04, S05, S06) and as generated test data. |
| N3 | "natural-person personal data held in an access-controlled layer" | not demonstrated: out of v2.0 | Two layers are separated and the separation is tested (A6). No access control is implemented: the identity layer is a plain file of invented data. |
| N4 | "Integrated legal-entity dossiering — incorporation instruments, articles of association, and registry extracts braided into one entity-keyed reference" | not demonstrated: out of v2.0, **in part** | Deeds, registry extracts, resolutions, transfers, appointments and financial summaries are read. Articles of association are not a document type of v2.0. |
| N5 | "Each invocation is recorded in the git history of the placement repository; the trail is auditable end-to-end." | not demonstrated: out of v2.0 | This repository records commits, not subagent invocations. No placement repository is part of the pack. |
| N6 | "Council Defense PASS — quorum 3/3 (Anthropic 9.1, Groq 8.7, Moonshot 8.1), no veto. JSON review artifacts public in `aetherneum-network/faculty`" | not demonstrated: out of v2.0 | Not checked by this pack; no review artifact is included here. |
| N7 | "14 alumni · 22 subagents · 330+ skills across 24 domains" and "placed across a portfolio of operating companies" | not demonstrated: out of v2.0 | Statements about the network, outside this repository. |
| N8 | Any reading of the dossier as professional work product | not demonstrated: out of v2.0 | The dossier is a build artefact of a test pipeline on invented documents. It is not legal, tax or corporate advice. Every legal assumption is a parameter marked `[TO CONFIRM with legal]` (`docs/ASSUMPTIONS.md`). |

## 3. Awaiting legal review

| # | Sentence of the profile (README) | Status |
|---|---|---|
| L1 | "Ezio is the platform's Legal-Entity Dossier Architect." | awaiting legal review — not touched |

The sentence is in the README exactly as it was before this proof pack: neither edited nor removed.
`tests/test_hygiene.py` checks that the whole pre-existing profile text is byte-identical to what it was.

## 4. A statement of the README that was false, recorded

The profile says: "GitHub `aetherneum` *(commits authored as Ezio Cardone)*".

- **Before this branch: false.** No commit of this repository was authored as Ezio Cardone.
- **From this branch on: true for this branch.** Every commit of `proofpack/2026-10-v2.0`, from commit
  `dfcef7e` on, is authored as `Ezio Cardone (synthetic alumnus, via Claude Opus 5.5)` and carries the
  trailer `Co-Authored-By: Claude Opus 5.5`. The author is an AI agent, and says so in the author name.
- The sentence itself was not edited.

## 5. What the numbers are

All measurements (`eval/history.json`, README) are taken on synthetic data generated by the same author
who wrote the extraction rules. Clean numbers on the development and holdout suites show that generator,
gold labels and rules agree with each other - internal consistency - and nothing more. The stress suite
and the blind protocol (eval/BLIND_PROTOCOL.md, written after the freeze tag and run by a different hand) exist because
of that limit.

## 6. The blind run of `v2.0.0-freeze`, and what it downgraded

Run once by the evaluator, not by the author, on 2026-09-30 (`eval/history.json`, run 5). By the only
criterion declared before it - no never-event in any result - it does not pass: 0 never-events in the plain
corpus, 1 in the perturbed one, 12 in the out-of-pool one. As `eval/BLIND_PROTOCOL.md` requires, the rows
it touches are downgraded here for the tag `v2.0.0-freeze`; the tag itself is not moved.

| # | At `v2.0.0-freeze` | In v2.0.1 (tag `v2.0.1-freeze`) |
|---|---|---|
| A1 | Held for the source, not for the figure: five figures carried their source document and date, but the figure was read a thousand times too small (`EUR 150'000.00` read as `150.00`, finding T16) and the audit confirmed it. A right source next to a wrong figure is not what A1 promises. | Amounts grouped by an apostrophe or a space are read whole; an amount whose reading is not certain is abstained with its reason; the audit compares the digits of the figure with those of its quote. |
| A3 | Held only for holders' tables the rules could read: eight entities whose table does not sum were published with the holders `[TO CONFIRM]`, because their table had not been read. | A holders' table that could not be read blocks the entity (`OWN-015`, parameter `unverified_holders_table`, `[TO CONFIRM with legal]`). The price is coverage, stated in `CHANGELOG.md`: on reworded corpora most entities are blocked. |

The v2.0.1 column rests on the tests named in section 1 and on data already seen (the evaluator's corpora
of run 5 and the author's suites, `eval/history.json` run 6). The blind run of `v2.0.1-freeze` (run 7, seed
20261012, by the evaluator) found 0 never-events; its price was coverage (89 of 150 perturbed entities blocked
wrongly). v2.0.2 (tag `v2.0.2-freeze`) reads more holders'-table forms with `OWN-015` unchanged; it was
measured by the author on data already seen (run 8).

The blind run of `v2.0.2-freeze` (run 9, seed 20261013, by the evaluator) found 0 never-events. Its price was
again coverage: 4 of 9 hand-written entities blocked wrongly by tables a careful human reads, and on the
perturbed corpus 54 of 144 published dossiers with the holders `[TO CONFIRM]`, because a document of
unrecognised type kept every field of its entity undecided (rule `DISC-005`). No row of section 1 is
downgraded by it. v2.0.3 (tag `v2.0.3-freeze`, owner decision D30) reads the forms of that run that can be
read without guessing, keeps blocked those that cannot (holders in a sentence, nominal amounts, a table with a
header row: `CHANGELOG.md` lists every known limit), scopes `DISC-005` to the fields an unread document may
state, and lists every never-event the scorer finds (the list was capped at 50). It was measured by the author
on data already seen (run 10: 0 never-events; hand-9 blocked wrongly 4 -> 2) and has not been run blind.

## 7. The blind run of `v2.0.3-freeze`, and what it downgraded

Run once by the evaluator, not by the author, on 2026-10-01 (UTC) (`eval/history.json`, run 11, seed 20261014,
hand-written corpus `eval/blind/hand-11/`). By the criterion of `eval/BLIND_PROTOCOL.md` - no never-event in
any result - it does not pass: 0 never-events in the plain corpus, 0 in the perturbed one, 2 in the
hand-written one. Both come from one entity and one cause (E-0015). A document of unrecognised type (a notice
to creditors) states that the equity was raised by a contribution in kind and that the seat moves; rules
`FEV-030`, `FEV-040` and `FEV-060` of `unread_fields` scope that sentence to the capital, the financial figures
and the registered office (by `FEV-040` a capital increase changes the capital, never the holders), so the
holders' table of the older registry extract was published as a fact and the effective holding was derived
from it, where the gold says the holders cannot be decided.
`CHANGELOG.md` 2.0.3 declares both the assumption (`FEV-040`, `[TO CONFIRM with legal]`) and the residual
risk of the scope; a declared risk that materialises is still a never-event. As the protocol requires, the
row it touches is downgraded here for the tag `v2.0.3-freeze`; the tag is not moved and the run is not
repeated under the name "blind".

| # | At `v2.0.3-freeze` | Fix |
|---|---|---|
| A2 | Held when the conflicting document is of a recognised type, or names the field it changes. Not held when a document of unrecognised type changes a field without naming it: the older value is published as a fact instead of being left `[TO CONFIRM]` next to that document (run 11, E-0015: the holders, and the effective holding derived from them). By the evaluator's analysis the same sentence-level gap appeared in two more hand-written entities (E-0009, E-0010), whose fields stayed `[TO CONFIRM]` only because of the wording of their title line. | Not made yet: it goes into a new version under a new tag. |

The related sentences "Cross-source discrepancy detection" and "Ownership-graph construction" are downgraded
with A2 at `v2.0.3-freeze`, for the same entity. Rows A1, A3, A4, A5 and A6 are not touched by the run.

### What v2.0.4 does for A2 (not run blind)

v2.0.4 (tag `v2.0.4-freeze`, finding D30b) puts back the caution of `DISC-005`: a document of unrecognised
type that is not older than the latest event of a field keeps every field `[TO CONFIRM]` again
(`unread_document_scope` = `every_field`); the scope to the fields such a document may state is off, because
46 of 160 adversarial siblings of E-0009, E-0010 and E-0015 publish a field under it on the v2.0.3 code
(`tests/test_d30b_forms.py`). On the hand corpus of run 11, now seen, E-0015 has 0 never-events and the
title siblings of E-0009 and E-0010 keep their fields `[TO CONFIRM]`. The price is coverage on reworded
corpora (`CHANGELOG.md` 2.0.4). One gap of the same kind is still open and is declared there: a document of a
**recognised** type is read for the fields of its kind only, so a recognised document that also changes
another field without the rules of its kind reading it would publish the older value of that field as a fact.
The row A2 above stays downgraded for `v2.0.3-freeze`; v2.0.4 has been measured by the author on data
already seen (run 12: 0 never-events) and has not been run blind, so nothing is upgraded here.

### What v2.0.5 does for A2 (not run blind)

v2.0.5 (tag `v2.0.5-freeze`, decision D34) closes the gap that v2.0.4 left open and declared: every non-empty
body line of a document of a **recognised** type is now decided by the ordered rules `classified_lines`
(`rules/extract.json`). A line that no rule of its kind explains makes the document one that may change every
field; a line that states a field its kind does not read, or that no rule of its kind read from it, makes it one
that may change that field; `DISC-006` keeps such a field `[TO CONFIRM]` when the document is not older than the
latest event of the field, as `DISC-005` does for a document of unrecognised type. A holders' table in a
document of another kind is read whole and summed, or the holders cannot be summed and `OWN-015` blocks; a line
that may state a holding outside a list read whole blocks too. Holders written in a sentence stay unread (D31).
On 379 siblings of five classes (`tests/test_d34_forms.py`: a capital resolution whose new quotas go to a new
holder, a transfer notice that also moves the seat, an appointment that also states a capital change, an office
transfer that also names a new director, a resolution that holds a holders' table), the v2.0.4 code publishes 348
wrongly and fails on 15; v2.0.5 publishes none. `CHANGELOG.md` 2.0.5 lists the known limits: none of them may
publish. The price is coverage on the reworded corpora (run 13: facts exact on stress 711 -> 681 of 1285, on the
out-of-pool corpus 330 -> 290 of 925; the plain corpora do not move). The row A2 above stays downgraded for
`v2.0.3-freeze`; v2.0.5 has been measured by the author on data already seen (run 13: 0 never-events on all
fifteen results) and has not been run blind, so nothing is upgraded here.

### What the blind run of v2.0.5 found, and what v2.0.6 does for A2 (not run blind)

The blind run of `v2.0.5-freeze` (run 14, by the evaluator, seed 20261015, hand corpus `eval/blind/hand-14/`)
found 0 never-events, but two of its probes of the residual risk declared by `CHANGELOG.md` 2.0.5 section 4 were
masked by a one-character miss of the deeds (`its legal form is S.r.l..`). Unmasked by the builder on the same
seen data, the code of `v2.0.5-freeze` publishes **3 never-events** on them: the holders of E-0011 and the
effective holding derived from them (a person slot of an appointment admitted `Sole Proprietress Henceforth`),
and the legal form of E-0012 (a name ending in `S.p.A.` beside `Legal form: S.r.l.`). The sentence "no case is
known" of that section was wrong, and A2 was not demonstrated for `v2.0.5-freeze` on that class either.

v2.0.6 (tag `v2.0.6-freeze`, finding D35): a name slot carrying a word that cannot be part of a name does not
close its line; a person's name beside its identifier must be that person's name in the identity layer, and the
entity's own name must be the name of its `Entity:` header (equality, not a word list); a company name whose legal
form differs from the legal form stated is shown as a discrepancy, both readings with their sources, the legal
form `[TO CONFIRM]` (`DISC-035`) - the sentence of A2, "surfaced side by side rather than silently reconciled",
for a conflict inside one source. On 192 siblings of nine classes (`tests/test_d35_forms.py`) the v2.0.5 code
publishes 147 wrongly, v2.0.6 none; the unmasked variant of E-0011/E-0012 has 0 never-events. Since v2.0.6 the
fields check of a document of unrecognised type records what `DISC-005` applies (every field), not the narrower
judgement of its lines. What still rests on a word list - the words of an address slot, a name beside an
identifier the pack does not know - is a residual risk, `[TO CONFIRM]`, stated in `CHANGELOG.md` 2.0.6 section 4;
`CHANGELOG.md` 2.0.6 lists the known limits: none of them may publish. On the corpora already seen (run 15: 0
never-events on all eighteen results) seventeen results do not move and hand-14 goes from 2/64 to 27/64 facts
exact. The row A2 above stays downgraded for `v2.0.3-freeze`; v2.0.6 has not been run blind, so nothing is
upgraded here.

### What the blind run of v2.0.6 found, and what v2.0.7 does for A2 (not run blind)

The blind run of `v2.0.6-freeze` (run 16, by the evaluator, seed 20261016, hand corpus `eval/blind/hand-16/`)
found 0 never-events. Its probes of the residual risk of `CHANGELOG.md` 2.0.6 section 4 did not reach it: two
blocked, and two were masked - the address probe used the office-transfer wording no field rule reads, the count
probe a total line outside the capital clause. Measured by the builder by class (`tests/test_d36_forms.py`, 600
siblings), that risk was real on the code of `v2.0.6-freeze`: 256 cases publish as fact a field that the extra
words of an address slot, or a name beside an identifier nobody knows, may change, and 56 more end the run FAILED
(the extra words reached the shareable layer). The sentence of that section that no case was known in the corpora
seen was true of the corpora, not of the class. Unmasked on the same seen data, the hand-16 probes publish nothing
wrong on either code (E-0014 FAILED on v2.0.6, OK with every field `[TO CONFIRM]` on v2.0.7; E-0017 blocks).

v2.0.7 (tag `v2.0.7-freeze`, finding D36): a name beside an identifier closes its line only when it equals that
identifier's own known name - an identifier whose name the corpus does not know leaves the line open; an address
needs its house number, every word of its street and town must have the form of a place name and name nobody the
corpus knows, and the readers of the office read only such an address (`value_slot`). The 600 siblings: 312
unsafe on v2.0.6, 0 on v2.0.7. A list now ends at a full sentence or a heading; "own" after a possessive and an
illegible amount are not words of holding. What still rests on a word list - a street or town of place-name form
that states something with a word of no class of `slot_not_name_word` - is a residual risk, `[TO CONFIRM]`, kept as
a test expected to fail (`CHANGELOG.md` 2.0.7 section 4); `CHANGELOG.md` 2.0.7 lists the known limits: none of them
may publish. On the corpora already seen (run 17: 0 never-events on all twenty-one results) eighteen results do
not move, hand-11 moves in its figures with source only (134 to 132); hand-16 goes from 12 to 14 of 28 published
and 46/89 to 47/102 facts exact. The row A2 above stays
downgraded for `v2.0.3-freeze`; v2.0.7 has not been run blind, so nothing is upgraded here.

## 8. The blind run of `v2.0.7-freeze`, and what it downgraded

Run once by the evaluator, not by the author, on 2026-10-01 (UTC) (`eval/history.json`, run 18, seed 20261017,
hand-written corpus `eval/blind/hand-18/`, 27 entities, 67 documents). By the criterion of
`eval/BLIND_PROTOCOL.md` - no never-event in any result - it does not pass: 0 never-events in the plain corpus, 0
in the perturbed one, 4 in the hand-written one, all four in one entity (E-0015) and from one cause. Its registry
extract writes the registered office as `Corso dei Fantasmi 8, Lagoapocrifo Dote Raddoppiata Oggi (ZZ)` where the
deed says `Corso dei Fantasmi 8, Lagoapocrifo (ZZ)`: the three words added inside the town say that the endowment
doubled today. Each has the form of a place name and none is in the word classes of `slot_not_name_word`, so the
line closes; the office is shown as a discrepancy whose second value carries the added words, and the share
capital (resolved, subscribed, paid in) is published as a fact, where the gold keeps the office and the capital
`[TO CONFIRM]`. By the evaluator's reading a careful human would have seen that those words are not a town.
This is the residual risk that `CHANGELOG.md` 2.0.7 section 4 declared as `[TO CONFIRM]` and kept as a test
expected to fail; a declared risk that materialises is still a never-event. As the protocol requires, the row it
touches is downgraded here for the tag `v2.0.7-freeze`; the tag is not moved and the run is not repeated under
the name "blind".

| # | At `v2.0.7-freeze` | Fix |
|---|---|---|
| A2 | Held for name, amount and count slots, and for addresses with a word that is not of the form of a place name. Not held when the words added to a street or a town all have that form and state a change of another field: the line closes, the older value of that field is published as a fact (run 18, E-0015: the share capital) and the office is shown with the added words as one of its two values. | Not made yet: it goes into a new version under a new tag. |

The related sentences "Cross-source discrepancy detection" and "lets a human adjudicate" are downgraded with A2
at `v2.0.7-freeze`, for the same entity. Rows A1, A3, A4, A5 and A6 are not touched by the run. The same run
found three forms that block without being read or declared (E-0020, E-0025, E-0026); a block publishes nothing,
so they touch no claim.

## 9. v2.0.8

v2.0.8 has not been run blind, nothing is upgraded.

## 10. The blind run of `v2.0.8-freeze`, and what it downgraded

Run once by the evaluator, not by the author, on 2026-10-01 (UTC) (`eval/history.json`, run 20, seed 20261018,
hand-written corpus `eval/blind/hand-20/`, 34 entities, 87 documents). By the criterion of
`eval/BLIND_PROTOCOL.md` - no never-event in any result - it does not pass: 0 never-events in the plain corpus, 0
in the perturbed one, 8 in the hand-written one, in two entities (E-0009, E-0010) and from one cause, the premise
that `CHANGELOG.md` 2.0.8 section 4 declares: two documents that carry the same added words are read as written.
In E-0009 the deed and the registry extract both write the town of the registered office as
`Monte Spurio Dotazione Novantamila`; in E-0010 the header, the own-name clause and the extract all write the
company's name as `Birrificio Pieve Supposta Dotazione Novantamila S.r.l.`. The added words state that the
endowment is ninety thousand, beside a share capital of 30.000,00. Stated alike by two documents, the office
(E-0009) or the name (E-0010) is taken as corroborated and published with the words, and the share capital
(resolved, subscribed, paid in) is published as a fact, where the gold keeps them `[TO CONFIRM]`. By the
evaluator's reading a careful human would have seen both changes. A declared premise that publishes a wrong value
is still a never-event; as the protocol requires, the row it touches is downgraded here for the tag
`v2.0.8-freeze`; the tag is not moved and the run is not repeated under the name "blind".

| # | At `v2.0.8-freeze` | Fix |
|---|---|---|
| A2 | Held when an address, a company's name, a title or a label that carries added words is stated without them by another document, or by one document only: every field `[TO CONFIRM]`. Not held when two documents carry the same added words and those words state a change of another field: the slot is taken as corroborated, the words are published with it and the older value of the other field (run 20: the share capital) is published as a fact. | Not made yet: it goes into a new version under a new tag. |

The related sentences "Cross-source discrepancy detection" and "lets a human adjudicate" are downgraded with A2
at `v2.0.8-freeze`, for the same entities. Rows A1, A3, A4, A5 and A6 are not touched by the run. The same run
found: one form that blocks without being read or declared (E-0030, rows framed by vertical bars without a
header row); a company's own name that holds a word of the registered office's topic words (`Borgo`) is left
unread in every document, which keeps every field of the entity `[TO CONFIRM]` and masked two probes at field
level (E-0007, E-0020); a capitalised particle in a street (`Via Del ...`) keeps every field `[TO CONFIRM]`
without being named among the limits; a registry extract filed with another entity's documents is built as an
entity of its own (E-0062). A block or a field kept open publishes nothing, so they touch no claim.

## 11. v2.0.9

v2.0.9 has not been run blind, nothing is upgraded. What it changes for A2 (finding D38: a free-text slot is a fact
only when every word of it is identified, whatever the documents agree on) is in `CHANGELOG.md` 2.0.9, measured
by the builder on corpora already seen only (`eval/history.json` run 21, NOT blind). Row A2 stays downgraded for
`v2.0.3-freeze`, `v2.0.7-freeze` and `v2.0.8-freeze` (sections 7, 8 and 10): a downgrade is lifted only by a blind
run that passes, never by the builder.
