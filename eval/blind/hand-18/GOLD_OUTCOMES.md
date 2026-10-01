# Hand corpus D36b - gold outcomes, written BEFORE the runs and BEFORE reading any code, rule list or test

Written by the evaluator (Claude Fable 5.1), not the builder. 2026-10-01, 07:45-07:58 UTC.
Sources used for the expectations below: `README.md` (v2.0.6 and v2.0.7 entries), `CHANGELOG.md` entry 2.0.7
(section 1 "the rule (a)", section 4 "the premise of the proof", "Known limits of v2.0.7"), `eval/BLIND_PROTOCOL.md`
at 86c4194 (sections 0, 1.5, 4 and 5), the scenario inputs of `scenarios/S01..S10` and the generator's own output for
seeds 20260930 (plain) and 20261002 (perturbed) for the read forms and the gold shape. No file of `dossier/`, `rules/`,
`tests/`, `tools/` was read; `eval/score.py` only through its command line in the protocol.
All data synthetic. Corpus: 27 entities, 67 documents, 15 persons in the identity layer (P-001..P-015); two persons
named only inside probe words and in no identity layer: Rina Fittizia, Zeno Fasullo. as_of 2026-09-30.
Gold file: `gold.json` (schema gold/2.0.0), produced by `make_hand_corpus.py` together with the corpus.

Legend of the expected pack outcome (from the known limits of v2.0.7): PUBLISH = entity OK, field as fact;
TC = field `[TO CONFIRM]`; BLOCK = entity blocked. "NE" = never-event by section 1.5 of the protocol.

## A. Control and own-form holders' tables (inside the claimed grammar unless said)

| Entity | What is probed | Gold | Expected pack outcome | NE if |
|---|---|---|---|---|
| E-0001 | deed heading `Art. 4 Members:`, rows `1) P-001 (...) - 45 pct` (marker `1)`, separator ` - `, unit `pct`); directors `Art. 5 Directors:`; exact extract; FY2025 summary | all FACT, holders 9/20 and 11/20, directors [P-001], fin FY2025 three facts | PUBLISH (heading nouns "Members"/"Directors" with `:` are claimed; if `Art. 4` is not taken as a clause number: holders BLOCK, declared "heading not read") | any value differs, or holders published other than 45/55 |
| E-0002 | extract rows name first `(a) Ada Simulacri (P-001) - 1/2` under `Quotaholders, registered:`; ledger `Partners:` with `*`, dot leaders, `per cent`, last line `Total ...... 100 per cent`; ledger file name date 2026-02-10 vs content 2026-02-12 | all FACT, holders 1/2,1/4,1/4; directors [P-003,P-004]; filename_divergences date on DOC-E0002-03 | PUBLISH; the file-name divergence listed, content date wins | holders differ; divergence published as a date fact |
| E-0003 | NON-SUMMING table (40+35+20 = 95%) in the deed AND the extract | BLOCKED, blocked_by sum 19/20 on both documents | BLOCK (`OWN-010`/`OWN-015`) | entity published at all, or holders shown |
| E-0019 | careful-human row `- P-001 (Ada Simulacri): the rest` (a human computes 15%) | OK, holders 60/25/15 FACT, directors [P-014] | BLOCK (row not typed and may state a holding) - cautious; "readable only by a careful human" | published with holders other than 60/25/15 |
| E-0020 | careful-human rows with names and NO identifiers (`- Fabio Immaginosi: 3/4`), names of the identity layer, heading `4. Members of the company.` | OK, holders P-006 3/4, P-007 1/4 FACT | BLOCK or every field TC; not listed among the known limits in so many words (a holder slot without an identifier) - report as "neither read nor declared" if it blocks | holders published other than 3/4, 1/4 |
| E-0021 | comma separator `- P-002 (Bruno Fasulloni), 70%`, headings `IV. Members:` / `V. Directors:` | OK, holders 7/10, 3/10, directors [P-002] | the comma is not among the claimed separators (`:`, ` - `, `\|`, tab): BLOCK expected and declared-ish ("a row the grammar cannot read ... holders block") | published with other values |
| E-0022 | heading written as a sentence `Those who hold the quotas are:` | OK, holders 2/3, 1/3, directors [P-005] | BLOCK ("headings of other nouns" is declared) or PUBLISH if the noun "quotas" is taken; either is acceptable | wrong values |
| E-0023 | extract heading `Quota holders:` (two words), marker `*`, share `40 %` with a space | OK, holders 2/5, 3/5 | PUBLISH (per cent with a space is claimed, hand-9 saw `60 %`); heading noun in two words may BLOCK (declared: nouns not listed) | wrong values |
| E-0024 | counts `(1) P-010 (Mino Spuri) - 1.500 quotas` with the one total in the capital clause `made up of 2.000 quotas` | OK, holders 3/4, 1/4 | PUBLISH if `made up of N quotas` is read as the `count_total`; otherwise BLOCK (declared: counts without a total) | published with other shares |
| E-0025 | share before the holder with a pipe `a) 1/2 \| P-012 (Oreste Supposti)` under `Quotaholders of the company:` | OK, holders 1/2, 1/2 | PUBLISH (share before the holder is claimed for per cent and `n/d`; a fraction first is not named - may BLOCK, cautious) | wrong values |
| E-0026 | shares in words `sixty per cent` / `forty per cent`, headings `Fourth. Holders:` / `Fifth. Directors:` | OK, holders 3/5, 2/5, directors [P-015] | PUBLISH (whole per cent in words is claimed) unless `Fourth.` is not a clause mark - then BLOCK/TC | wrong values |
| E-0027 | decimal shares `12,5%` in three documents, ledger in the read form | OK, holders 1/8, 1/8, 3/4 | PUBLISH | wrong values |

## B. Documents of UNRECOGNISED type that change a field in their own words (latest document of the entity)

| Entity | Document (type label / title noun) | Field changed, how | Gold | Expected pack outcome |
|---|---|---|---|---|
| E-0004 | `Succession record` / "Record of a succession (synthetic)." - "Gilda Presunta (P-007) stands in his place for all purposes in the company" | holders AND directors change, neither named | shareholders TC, directors TC, ownership TO_CONFIRM | `DISC-005` `every_field`: every field TC, or BLOCK if "in his place"/the identifiers count as a line that may state a holding (declared) |
| E-0005 | `Chamber communication` / "Entry of the test chamber (synthetic)." - "all dealings with the company take place at Largo degli Esempi 11, Borgochimera (ZZ)" | office moved, the word office absent | registered_office TC | every field TC (`DISC-005`); NE if the office is published as either address |
| E-0006 | `Pledge release` / "Declaration of the lender (synthetic)." - "each founder paid in again what he had paid at the formation" | capital doubled, the word capital absent | share_capital.* TC | every field TC; NE if capital published as 30.000 |
| E-0007 | `Court order` / "Minutes of the test tribunal (synthetic)." - "removed from every function ... Lea Fantomatici (P-009) alone may bind it" | director replaced, the word director absent | directors TC | every field TC; NE if directors published as [P-006] |

## C. Documents of RECOGNISED type that also change a field they are not about (read form + one own sentence after a blank line)

| Entity | Document | Extra sentence changes | Gold | Expected pack outcome |
|---|---|---|---|---|
| E-0008 | capital resolution 20.000 -> 40.000 (read form) | holders: "Nora Illusori (P-011) answered for the entire new sum and from this day sits with the founders in every meeting." | capital 40.000 FACT (superseded 20.000), shareholders TC, ownership TO_CONFIRM | `CLS-999` + `DISC-006`: every field TC (capital included - cautious), or BLOCK if the sentence counts as holding evidence; NE if holders published 70/30 as fact |
| E-0009 | share transfer (read form, 30/70) | directors: "From this date Clelia Posticcia (P-003) speaks for the company alone; Ada Simulacri (P-001) withdraws." | holders 30/70 FACT (superseded 50/50), directors TC | every field TC or BLOCK; NE if directors published [P-001] |
| E-0010 | appointment of P-012 (read form) | office: "Vicolo Immaginario 3, Borgochimera (ZZ) is from today the only place where the company can be served." | directors [P-012] FACT (superseded [P-011]), registered_office TC | every field TC; NE if office published (either address) |
| E-0011 | financial summary FY2025 (read form) | capital: "In the year the founders paid in, for the second time, the sum of the deed of incorporation." | fin.FY2025.* FACT, share_capital.* TC | every field TC; NE if capital published 25.000 |
| E-0012 | deed whose capital clause is in own words: "The founders bring in EUR 25.000,00, all of it paid on signing." vs extract 30.000 | conflict deed/extract on the capital, stated by the deed in a form not read | share_capital.* DISCREPANCY [25.000, 30.000] (the generator's own convention: deed vs extract without a resolution = discrepancy) | by the known limits the deed is OLDER than the extract, so `DISC-006` does not hold the field: capital 30.000 published as one fact = "planted conflict shown as one value" (NE by 1.5) unless the pack reads the clause. To classify, not to hide: it is the "older than the latest event" clause of the limits |

## D. Typed-slot probes, UNMASKED - every other line in a read form, checked line by line

Read forms taken from the scenario inputs and the generator (plain seed 20260930): header six lines; deed clauses
`1. Name and form. ...; its legal form is S.r.l.` / `2. Registered office. The registered office is at <street> <no>, <town> (ZZ).` /
`3. Share capital. The share capital is EUR n, fully subscribed and fully paid in.` / `4. Holders.` rows `- P-xxx (Name): share` /
blank / `5. Directors.` rows; extract label lines `Name:`, `Legal form:`, `Registered office:`, `Share capital: resolved EUR n; subscribed and paid in EUR n`,
`Holders:` rows, blank, `Directors:` rows; resolution `Minutes of the holders' meeting (synthetic).` + `The meeting resolved to increase the share capital from EUR a to EUR b. The increase has been fully subscribed and fully paid in.`;
appointment `Minutes of the holders' meeting (synthetic).` + `Directors in office after this appointment:` rows, file `<date>_appointment_P-xxx.txt`;
office transfer `The registered office is transferred from A to B.`, file `<date>_office-transfer.txt`.

| Entity | Slot | Probed line (only this line differs from the read form; the document is the LATEST of the entity) | Gold | What an unmasked v2.0.7 must do (README v2.0.7, CHANGELOG 2.0.7 s.1 and s.4) | NE if |
|---|---|---|---|---|---|
| E-0013 | NAME of a person beside its identifier | appointment row `- P-005 (Elsa Finzioni Moving The Seat To Largo degli Esempi 1 Pontefinto)`; file `2026-06-02_appointment_P-005.txt` (appointee matches) | directors [P-005] FACT, registered_office TC | `CLS-005` by equality: the slot is not P-005's own name "Elsa Finzioni" -> the line is open -> every field TC (`DISC-006`); the directors stay TC too (cautious, not an NE). Nothing may be published from this line. | office published; or directors published AND office published as the deed's address |
| E-0014 | ADDRESS, new address of an office transfer (the residual risk of s.4: street words all of place-name form, naming nobody the corpus knows) | `The registered office is transferred from Via delle Ipotesi 5, Rivaposticcia (ZZ) to Via Rina Fittizia Regge Da Sola 3, Rivaposticcia (ZZ).` - every word ends in a vowel or is a particle (`Da`); house number 3; "Rina Fittizia" is in no identity layer | registered_office TC, directors TC (an Italian reader reads "Rina Fittizia rules alone") | s.4 says such a line CLOSES and every field is published, the office with those words as its value - the declared residual risk `[TO CONFIRM]`, "the blind protocol asks the next hand to probe the address slot, unmasked". If `Regge` is on the `slot_not_name_word` list the line is open and every field TC. | office published (any value), directors published [P-006]: NE by 1.5 (field the gold says cannot be read shown with a value) - to be classified as the residual risk of s.4, measured |
| E-0015 | ADDRESS, label line of the extract, words inside the town | `Registered office: Corso dei Fantasmi 8, Lagoapocrifo Dote Raddoppiata Oggi (ZZ)` (deed: `Corso dei Fantasmi 8, Lagoapocrifo (ZZ)`) | registered_office TC, share_capital.* TC ("endowment doubled today") | same residual risk, in the town; the line closes -> office DISCREPANCY (two values) or FACT, capital 50.000 published: NE by 1.5 on the capital (gold TC) and on the office. If `Dote` or `Raddoppiata` is on the list: line open, every field TC. | capital or office published |
| E-0016 | AMOUNT, second amount of a capital resolution | `The meeting resolved to increase the share capital from EUR 40.000,00 to EUR 80.000,00 Put Up By Zeno Fasullo Who Now Steers The Company. The increase has been fully subscribed and fully paid in.` | share_capital.* 80.000 FACT (superseded 40.000), directors TC, shareholders TC | s.1: "any other word opens the line" for an amount slot -> `CLS-999`, every field TC or BLOCK (if "Put Up" counts as holding). Nothing published. | capital 40.000 or 80.000 published together with directors [P-010] or holders 80/20 |
| E-0017 | COUNT, total of quotas in the capital clause (deed only, so the clause is in the latest document) | `3. Share capital. The share capital is EUR 10.000,00, divided into 1.000 quotas Zeno Fasullo Taking The Chair, fully subscribed and fully paid in.` | all FACT from the deed, directors TC | s.1: a count slot is a figure and its unit noun, extra words open the line -> every field TC (`DISC-006`, the deed is the latest document) or BLOCK. | directors [P-012] published |
| E-0018 | LEGAL FORM label (the evaluator's own choice) | `Legal form: S.r.l. Now Seated At Piazza della Finzione 1 Serraillusoria` (deed and extract agree on `Via del Simulacro 20, Serraillusoria (ZZ)`) | registered_office TC, legal_form S.r.l. FACT, name FACT | not a slot named in s.1; `DISC-035` or `CLS-999`: the legal form TC (DISC-035) or every field TC (DISC-006). The office must not be published. | office published as `Via del Simulacro 20, Serraillusoria (ZZ)` while this line closed |

Masking check, per probe: the header is the standard six-line header with a standard edition token; the file name carries the right
slug and date; every other body line is byte-equal to the read form; no second deviation (no sentence outside a list, no heading
of another noun, no illegible amount, no total outside the capital clause). E-0014 and E-0015 are the one class the pack itself
marks `[TO CONFIRM]` (s.4): they are not masked, they measure that class. The probe NOT included: a name of the identity layer used
as a street word (the corpus-known names are excluded by s.1 and would only confirm the list) - noted as [TO CONFIRM] for a later hand.

## E. Blocked wrongly - how it will be counted

The scorer's `blocked_wrongly` counts every OK gold entity the pack blocks. For each such entity the report says whether the block is
a declared limit (list above), a careful-human form (E-0019, E-0020), or neither read nor declared. A block is never an NE; a
published wrong value is.

## F. Never-events, both definitions

Section 1.5 of the protocol (fact differing from gold; planted conflict shown as one value or with non-gold values; field the gold
says cannot be read shown with a value; value not in gold; non-summing cap table not blocked; published cap table not summing;
effective holding where gold abstains or differs; figure without source/date/edition) is applied by hand to every published entity,
next to `metrics.never_events` of `eval/score.py`. Each one is classified (R6): residual risk of s.4, "older than the latest event",
or a defect, with "would a careful human reader have seen the change: yes/no".
