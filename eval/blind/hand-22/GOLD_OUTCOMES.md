# GOLD OUTCOMES - hand corpus of the blind run D38b (pack v2.0.9-freeze, commit 50a365e)

Written by the evaluator (Claude Fable 5.1), not the builder, on 2026-10-01 at 15:25Z, BEFORE any run and
before reading the pack's code, rules, tests, earlier hand corpora or earlier evaluators' folders.
Sources used to shape the documents: README.md, CLAIMS.md, SYNTHETIC.md (gazetteer section -> the constants
of the synthetic world), MODEL.md, docs/ASSUMPTIONS.md, CHANGELOG.md, eval/BLIND_PROTOCOL.md at db334c9,
scenarios/*/run.md and the scenario input documents. Gazetteer words come from the synthetic world's lists
(towns, streets, trades, first names, surnames) and the scenario inputs; "outside" words are mine.

Corpus: 42 entities, 100 documents, 44 persons in the identity layer (P-041, P-042 are outside the gazetteer;
the surname "Immaginari" and the pair "Dino Fasulli" are gazetteer words held by nobody of the identity layer).
as_of 2026-09-30. Every document is dated before as_of; every adversarial document is dated AFTER the latest
recognised document of its entity.

## Unmask check (method)
`LINE_CHECK.md` (generated with the corpus) classifies every body line by my own patterns of the forms the pack
claims to read (scenario deed clauses 1-3, holders/directors headings and rows in the scenario form and in my
forms F1-F7 within the claimed grammar, the extract labels, the two pack titles, the resolution sentence, the
office-transfer sentence, the three financial lines). Exactly 23 lines are marked `??`:
- E-0006 (4 rows, form O1, outside, by design), E-0041 (1 heading, form O2, outside, by design);
- E-0008 `Holders after the increase:` (a holders' heading in a resolution - the adversarial table itself);
- the 2 adversarial lines (title + sentence) of each of E-0009, E-0010, E-0011, E-0012 (8 lines);
- the single adversarial sentence of E-0013, E-0014, E-0015, E-0016, E-0017 (5 lines);
- the probe lines of E-0019 (amount), E-0020 (count), E-0029 (title, twice) (4 lines).
No other line of a probe entity is outside the claimed forms: every probe is unmasked by construction. For the
address/name/premise probes (E-0018, E-0021..E-0028, E-0030) the probe sits INSIDE a line of a claimed form
(a director row, a Registered office line, clause 2, the office-transfer sentence, the Name line, clause 1,
the Entity header) and the pattern still matches, which is the point: the pack must notice the words, not the form.
After the run I will list every line the pack reports as unread and say whether it masks a probe.

## Per-entity gold (publish / block / field [TO CONFIRM]) and why

| Entity | Kind | Gold | Expected by the pack's own declarations | Never-event if... |
|---|---|---|---|---|
| E-0001 | PLAIN, form F1 `(4) Holders of record:` dash rows, fractions | publish all FACT; 3/5, 2/5 | publish (inside claimed class) | a wrong value as fact |
| E-0002 | PLAIN, form F2 `Article 4. Holders:` `1. P - 55 pct` | publish; 11/20, 9/20 | publish (inside) | - |
| E-0003 | PLAIN S.p.A. Holding pattern, form F3 `§ 4 Shareholders:` name first `(a) Name (P): 70 percent` | publish; 7/10, 3/10 | publish (inside) | - |
| E-0004 | NOT SUMMING 45+35+15 = 95 in both docs | BLOCKED (sum 19/20) | BLOCKED | a published dossier here |
| E-0005 | CAREFUL HUMAN: blank line between the two deed rows | publish 1/2, 1/2 (a human reads both rows) | block (list ends at a blank line - declared) | 1/2 alone published as the whole table |
| E-0006 | OUTSIDE form O1 `- Name [P-015]: 60%` both docs | publish 3/5, 2/5 | block? NOT in the declared list -> limits-completeness finding | the table published wrong |
| E-0007 | form F5 counts `1) P: 1.200 quotas`, total in clause 3 | publish 3/5, 2/5 | publish (inside, count_total) | - |
| E-0008 | ADV RECOGNISED: resolution + `Holders after the increase:` 50/25/25 | capital 80.000 FACT (DOC-03); shareholders TO_CONFIRM; ownership TO_CONFIRM | holders [TO CONFIRM] or BLOCKED (OWN-015) | 70/30 published as fact after 2026-04-08 |
| E-0009 | ADV UNRECOGNISED `Escrow instruction` (capital doubled, no key word) | capital x3 TO_CONFIRM; rest FACT | every field [TO CONFIRM] (DISC-005) | 45.000 as fact |
| E-0010 | ADV UNRECOGNISED `Rent roll` (seat moved) | office TO_CONFIRM | every field [TO CONFIRM] | the old office as fact |
| E-0011 | ADV UNRECOGNISED `Insurance schedule` (director replaced) | directors TO_CONFIRM | every field [TO CONFIRM] | [P-029] as fact |
| E-0012 | ADV UNRECOGNISED `Bank reference` (holder bought out + director) | shareholders, directors TO_CONFIRM; ownership TO_CONFIRM | every field [TO CONFIRM] | 50/50 or [P-030] as fact |
| E-0013 | ADV RECOGNISED: transfer notice 40/40/20 + sentence doubling the capital | shareholders 2/5,2/5,1/5 FACT; capital x3 TO_CONFIRM | holders read; unexplained line -> [TO CONFIRM] / block (DISC-006) | 30.000 as fact; 60/40 as fact |
| E-0014 | ADV RECOGNISED: appointment P-035,P-036 + sentence moving the seat | directors [P-035,P-036] FACT; office TO_CONFIRM | directors read; unexplained line -> [TO CONFIRM] / block | old office as fact; [P-035] alone as fact |
| E-0015 | ADV RECOGNISED: office transfer (claimed sentence) + sentence giving all to P-038; EXTRACT/2 confirms both | office new FACT; shareholders P-038 1/1 FACT; directors [P-037] | new office; holders from EXTRACT/2 (or [TO CONFIRM]); unexplained line -> block? | 3/4-1/4 as fact; old office as fact |
| E-0016 | ADV RECOGNISED: financial summary FY2025 + sentence moving the seat | fin FY2025 FACT (310500.00 / 1250000.00 / 980250.75); office TO_CONFIRM | figures read; unexplained line -> [TO CONFIRM] / block | old office as fact |
| E-0017 | ADV RECOGNISED: extract whose capital line is my sentence ("one hundred and twenty thousand euro") | capital x3 TO_CONFIRM | unexplained line in an extract -> [TO CONFIRM] / block | 80.000 as fact |
| E-0018 | NAME probe: `- P-010 (Mara Campioni Ormai Unica Proprietaria)` in an appointment | directors [P-010] FACT; shareholders TO_CONFIRM; ownership TO_CONFIRM | name beside identifier != identity name -> CLS-005 block or [TO CONFIRM] | 60/40 as fact; the words inside a published name |
| E-0019 | AMOUNT probe: new amount + `Sottoscritti Per Intero Da Zita Ipotetici Che Entra Da Sola` | capital 60.000 FACT (abstention fine); shareholders TO_CONFIRM | the sentence no longer matches -> unexplained line -> block/[TO CONFIRM] | 40.000 as fact after 2026-03-12; 50/50 as fact |
| E-0020 | COUNT probe: `divided into 3.000 quotas Riunite In Mano A Nino Fantasmi` | shareholders TO_CONFIRM; capital 30.000 FACT | clause 3 no longer matches -> count unknown -> rows in quotas cannot be read -> block | 60/40 as fact |
| E-0021 | ADDRESS (1) town + 2nd source: extract `Roccaesempio Fondi Aumentati`, deed plain | office TO_CONFIRM; capital x3 TO_CONFIRM | IDN-999 (non-gazetteer words) -> address open; ADR-999 two readings | either office as fact; 35.000 as fact |
| E-0022 | ADDRESS (2) town, single source, gazetteer only: `Pontecollaudo Valcollaudo` | office TO_CONFIRM | DISC-020 two whole addresses side by side / ADR-020 single source -> open | either town as the office fact |
| E-0023 | ADDRESS (3) street + 2nd source: deed `Via del Collaudo Immaginari 7`, extract plain | office TO_CONFIRM | IDN-040 surname inside an address -> open; the two sources differ -> ADR-999 | either address as fact |
| E-0024 | ADDRESS (4) street, single source, non-gazetteer: `Corso dei Modelli Guida Nuova 4` | office TO_CONFIRM; directors TO_CONFIRM | IDN-999 -> open; ADR-020 | the new office as fact; [P-020] as fact |
| E-0025 | PREMISE town + numeral alike x2: `Lagosintetico Patrimonio Centoventimila` | office TO_CONFIRM; capital x3 TO_CONFIRM | IDN-010 numeral -> open (section 4 item of CHANGELOG 2.0.9) | office with the words as fact; 60.000 as fact |
| E-0026 | PREMISE street, no numeral, alike x2: `Viale degli Esempi Comando Ceduto 6` | office TO_CONFIRM; directors TO_CONFIRM | IDN-999 -> open | office as fact; [P-024] as fact |
| E-0027 | PREMISE company name, gazetteer only: `Fonderie Rivaprova Nora Ipotetici S.r.l.` (P-023 a holder) | name TO_CONFIRM; shareholders TO_CONFIRM; ownership TO_CONFIRM | NAM-005 / IDN-040 person inside the header -> every field [TO CONFIRM] | that name as fact; 50/50 as fact |
| E-0028 | PREMISE company name non-gazetteer + numeral: `Cartiere Poggioesempio Tre Teste Nuove S.r.l.` | name TO_CONFIRM; directors TO_CONFIRM | NAM-005 -> every field [TO CONFIRM] | that name as fact; [P-027] as fact |
| E-0029 | PREMISE title alike x2: `Minutes of the holders' meeting, the chair passing to Sergio Finti (synthetic).` | directors TO_CONFIRM; capital 90.000 FACT (abstention fine) | TXT-005/020 title not identified -> both docs open / block | 70.000 as fact after 2026-02-10; [P-030] or [P-029] as fact |
| E-0030 | PREMISE town, gazetteer only, no numeral: `Borgoprova Dino Fasulli` alike x2 | office, directors, shareholders TO_CONFIRM; ownership TO_CONFIRM | IDN-040 (a person's name inside an address, not of the corpus) -> open; declared limit E-0062-like: words made of gazetteer entries placed where the pattern does not take them | office as fact; [P-031] or 60/40 as fact |
| E-0031 | OWN NAME = town of its own office (`Officine Casalprova S.r.l.` at Casalprova) | publish all | publish (declared identified) | a block here is a wrongly-blocked dossier |
| E-0032 | OWN NAME holding a street word (`Cantieri Largo Simulato S.r.l.`) | publish all | NAM-005 every field [TO CONFIRM], not blocked (declared) | - |
| E-0033 | identity-layer surname inside the address (`Via del Segnaposto 5` and P-007 Gino Segnaposto) | publish all | address with a corpus name inside -> [TO CONFIRM] (declared) | - |
| E-0034 | OUTSIDE gazetteer: town `Pievetorta` | publish all | IDN-999 every field [TO CONFIRM], not blocked | a wrong value as fact |
| E-0035 | OUTSIDE gazetteer: trade `Segherie` | publish all | NAM-005 every field [TO CONFIRM] | - |
| E-0036 | OUTSIDE gazetteer: persons Orsola Parvenze, Benedetto Sembianze | publish all | rows not identified -> BLOCKED (OWN-015) (declared price) | - |
| E-0037 | OUTSIDE gazetteer: street `Via delle Larve` | publish all | IDN-999 every field [TO CONFIRM] | - |
| E-0038 | form F4 `iv. Quotaholders of record.` `a) P (Name) \| 50 %` | publish 1/2, 1/2 | publish (inside) | - |
| E-0039 | form F6 tab separator + `seventy per cent` in words | publish 7/10, 3/10 | publish (inside: per cent in words claimed) | - |
| E-0040 | form F7 share before holder `- 7/10 P-012 (Olga Modelli)` | publish 7/10, 3/10 | publish (inside) | - |
| E-0041 | OUTSIDE form O2 heading `Stockholders as of today:` | publish 3/5, 2/5 | BLOCKED (declared: a "current" qualifier in free words) | - |
| E-0042 | `Total: 100%` last line equal to the sum | publish 11/20, 9/20 | publish (inside: Total equal to the exact sum) | - |

Forms INSIDE the claimed classes written in my own way: F1 (E-0001), F2 (E-0002), F3 (E-0003), F4 (E-0038),
F5 counts (E-0007), F6 tab + words (E-0039), F7 share first (E-0040), Total line (E-0042).
Forms OUTSIDE the claimed classes: O1 name first + square brackets (E-0006, undeclared), O2 "as of today"
heading (E-0041, declared). Table readable only by a careful human: E-0005. Table that truly does not sum: E-0004.

## What a never-event is here (both definitions will be applied after the run)
By protocol §1.5: a wrong value committed as a fact in a field of a published dossier, counted per field, in
the eight kinds the scorer sums (`*_wrong_committed`). By the scorer: the eight fields and their total. For each
non-zero field I will classify (R6): wrong fact / stale fact after a change / probe words published inside a
value / wrongly-blocked is NOT a never-event (it is a cost) / abstention is NOT a never-event.
Careful-human question, recorded per probe after the run: would a careful human reading the whole document
have seen the change? For every probe here the answer is yes by construction (the added words are in plain
sight, in Italian or English, and state the change).
