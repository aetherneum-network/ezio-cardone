# Hand corpus D39b - gold outcomes and unmask check

Written by the evaluator (Claude Fable 5.1), not the builder, on 2026-10-01 (UTC 19:05-19:20), BEFORE any run and
BEFORE reading the pack's code, rules or tests. Sources used for the check: README.md, CHANGELOG.md (2.0.10 and the
known-limit lists), SYNTHETIC.md (gazetteer), docs/ASSUMPTIONS.md, eval/BLIND_PROTOCOL.md (commit 11f1559), the ten
scenarios' run.md and input documents (the reference forms). 45 entities, 114 documents, as_of 2026-09-30.

Gold = what a careful human reads from the documents. For every probe the gold says what an UNMASKED pack must do:
publish (every field a fact), block, or keep the named field [TO CONFIRM]. A block or an abstention where the gold
publishes is a price (counted, classified against the declared limits), never a never-event; a value shown as fact
where the gold abstains or differs is a never-event.

## 0. Reference forms (every "standard" line below is one of these, token for token)

Header (6 lines, then a blank line): `SYNTHETIC TEST DOCUMENT - fictitious entity, invented test registry, not an
official record.` / `Document id: DOC-E00NN-KK` / `Document type: <one of the 8 labels>` / `Document date: YYYY-MM-DD` /
`Edition: DEED/1 | EXTRACT/n | RESOLUTION/1 | TRANSFER/1 | APPOINTMENT/1 | OFFICE/1 | FIN-FY2025/1` /
`Entity: <name> (test registry no. TEST-REG-0000NN)`; the financial summary adds `Financial year: YYYY`.
Deed: `1. Name and form. The company is named <name>; its legal form is <form>` (S01) / `2. Registered office. The
registered office is at <street> <no>, <town> (ZZ).` (S01) / `3. Share capital. The share capital is EUR N, fully
subscribed and fully paid in.` (S01) / `4. Holders.` + rows `- P-00N (<own name>): NN%` (S01) / blank /
`5. Directors.` + rows `- P-00N (<own name>)` (S01); an entity holder row `- E-00NN (<its header name>): NN%` (S06).
Extract: `Name:` / `Legal form:` / `Registered office:` / `Share capital: resolved EUR N; subscribed and paid in EUR N`
or `resolved EUR N; subscribed EUR N; paid in EUR N` (S03) / `Holders:` rows / blank / `Directors:` rows.
Resolution: `Minutes of the holders' meeting (synthetic).` / `The meeting resolved to increase the share capital from
EUR A to EUR B. The increase has been fully subscribed and fully paid in.` (S03, S06).
Transfer: `Notice of a transfer of shares (synthetic).` / `Holders after the transfer:` rows (S06).
Appointment: `Minutes of the holders' meeting (synthetic).` / `Directors in office after this appointment:` rows (S06).
Office transfer: `The registered office is transferred from <addr> to <addr>.` (CHANGELOG, EXT-OFFICE-010).
Financial summary: `Net equity: EUR N` / `Total assets: EUR N` / `Revenue: EUR N` (S04).
Count form (NAT-025, CHANGELOG 2.0.10 section 2): `EUR N, divided|split into N [ordinary|registered|equal]
quotas|shares, fully subscribed and fully paid in.` one sentence, one line, single amount.
Gazetteer (SYNTHETIC.md): every town, street, trade word, first name and surname used below is an entry, matched
whole, except where the entity is marked OUTSIDE. Every person's name beside an identifier is that identifier's own
name of input/identity/persons.json (checked by the generator: the rows are built from the identity layer).

File names: `<document date>_<slug>.txt` with the slugs of the pack (deed, capital-resolution, share-transfer,
appointment, office-transfer, registry-extract, financial-summary); the unrecognised documents carry a slug of their
own. The one deliberate divergence is E-0045 (file date 2026-02-15, header date 2026-02-10).

## 1. Gold per entity

### A. Plain, gazetteer only, corroborated (the three PLAIN slot kinds: town, street, company name)
- E-0001 Ceramiche Torremodello S.r.l. - deed + extract alike. Gold: PUBLISH every field; effective P-001 3/5, P-002 2/5.
  Plain town (Torremodello, also in the name), plain street (Via del Collaudo), plain company name.
- E-0002 Molini Pietrafinta S.r.l. - deed, resolution 100.000->150.000, transfer, appointment, office transfer, FY2025,
  extract/1 stating every current value. Gold: PUBLISH; office Largo Simulato 9 (superseded Corso dei Modelli 3), capital
  150.000 x3, holders P-003 1/2 P-004 1/2, directors [P-004], FY2025 three figures.
- E-0003 Holding Valcollaudo Partecipazioni S.p.A. - deed + extract. PUBLISH; effective P-006 7/10, P-007 3/10.
- E-0004 Vetrerie Valcollaudo S.r.l. - held 40% by E-0003, 60% by P-008. PUBLISH; effective P-006 7/25, P-007 3/25, P-008 3/5.
- E-0005 Cartiere Lagosintetico S.r.l. - deed, extract/1, FY2024, transfer, extract/2, FY2025. PUBLISH; holders P-009 1/2,
  P-010 1/2 (superseded: deed and extract/1, P-009 1/1); two financial years.

### B. Holders' tables in the evaluator's own forms
- E-0006 Fonderie Serrafinta S.r.l. - deed table INSIDE the claimed classes (CHANGELOG 2.0.3: headings "of record" or a
  parenthesised number, name-first and lettered rows, shares in words of a whole per cent and simple fractions):
  `(4) Quotaholders of record:` / `(a) Nino Simulati (P-011): 35%` / `(b) Olga Prototipi (P-012): forty per cent` /
  `(c) Piero Campioni (P-013): one quarter`. Extract standard. Gold: PUBLISH; holders 7/20, 2/5, 1/4. A block here is
  a wrongly blocked entity NOT covered by the known limits (unless the noun Quotaholders or the word "forty" is).
- E-0007 Laterizi Campomodello S.r.l. - deed table OUTSIDE the classes: a header row `Holder | Identifier | Share` then
  `Rita Fantasmi | P-014 | 55%` / `Sergio Fasulli | P-015 | 45%`. Gold: PUBLISH 11/20, 9/20. Declared limit: "a table
  with a header row - blocks" -> a block is rightly blocked by declaration (scorer: blocked where gold publishes).
- E-0008 Conserve Rivaprova S.r.l. - 45% + 45% in deed and extract. Gold: BLOCK (sum 9/10). Publishing = never-event.
- E-0009 Falegnamerie Valfittizia S.r.l. - counts 2.000 + 2.500 quotas, `Total: 5.000 quotas`; extract 40% + 50%.
  Gold: BLOCK (9/10, OWN-010 / sum). Publishing = never-event.

### D. Adversarial documents of UNRECOGNISED type (dated after the extract, the latest recognised document)
- E-0010 Tipografie Portoinventato S.r.l. - `Chamber annotation` 2026-08-18, title `Record of an entry (synthetic).`,
  sentence: every quota belongs to P-020 alone, P-021 has left. Gold: holders P-020 1/1 (superseded 60/40), effective
  P-020 1/1; unmasked pack: every field [TO CONFIRM] (DISC-005) and, as the line may state a holding, BLOCK (OWN-015).
  Never-event if the 60/40 table is published as fact or an effective holding is derived from it.
- E-0011 Distillerie Castelfittizio S.r.l. - `Notarial certificate` 2026-07-21, title `Certificate of the notary
  (synthetic).`, sentence: capital stands at 120.000 after a contribution, quotas in the same hands. Gold: capital
  120.000 x3 (superseded 80.000), holders unchanged 1/2 1/2. Unmasked pack: every field [TO CONFIRM] / block.
  Never-event if 80.000 is published as fact.
- E-0012 Filande Poggioesempio S.r.l. - `Letter to the registry` 2026-09-02, title `Letter of the chairman (synthetic).`,
  sentence: the company answers at Piazza Inventata 4, the former seat is closed. Gold: office Piazza Inventata 4,
  Poggioesempio (ZZ). Unmasked pack: every field [TO CONFIRM]. Never-event if Via della Prova 6 is published as fact.
- E-0013 Saline Montefinto S.r.l. - `Report of the auditor` 2026-08-30, title `Report on the management (synthetic).`,
  sentence: management entrusted to P-027 alone, P-026 left office. Gold: directors [P-027]. Unmasked pack: every field
  [TO CONFIRM]. Never-event if [P-026] is published as fact.

### E. Adversarial documents of RECOGNISED type (also change a field they are not about)
- E-0014 Officine Collesintesi S.r.l. - resolution 2026-05-05 (standard sentence) + a second line: the increase subscribed
  by P-029 who enters; quotas held 5/7 P-028, 2/7 P-029. Gold: capital 70.000 x3; holders P-028 5/7, P-029 2/7.
  Unmasked pack: the second line is one no resolution rule explains -> DISC-006 every field, holding words -> BLOCK.
  Never-event if P-028 1/1 is published as fact.
- E-0015 Cantieri Fontesegnaposto S.r.l. - appointment 2026-06-06 standard + blank + `The meeting also moved the seat of
  the company to Via del Segnaposto 19, Fontesegnaposto (ZZ).` Gold: directors [P-031]; office Via del Segnaposto 19.
  Unmasked pack: every field [TO CONFIRM]. Never-event if Largo Simulato 2 is published as fact.
- E-0016 Immobiliare Pratofinto S.r.l. - transfer 2026-04-14 standard rows 50/50 + blank + a sentence fixing the price by
  reference to a share capital of 95.000 "as increased by the same meeting". Gold: holders 1/2 1/2; resolved 95.000;
  subscribed and paid in [TO CONFIRM]. Never-event if 60.000 is published as fact.
- E-0017 Frantoi Casalprova S.r.l. - office transfer 2026-03-03 standard + a second line: P-034 sold all her quotas to
  P-035, now the only quotaholder. Gold: office Corso dei Modelli 11; holders P-035 1/1. Unmasked pack: BLOCK (holding
  line). Never-event if 60/40 is published as fact.
- E-0018 Vetrerie Villasimulata S.r.l. - FY2025 summary standard + blank + a sentence: the quotas of P-037 bought back by
  P-036, now the sole quotaholder. Gold: holders P-036 1/1; FY2025 three figures. Never-event if 50/50 is published.

### F. Typed-slot probes (words inside a typed slot; every other line standard - see section 2)
- E-0019 NAME - extract directors' row `- P-038 (Rita Modelli Dimessa E Rimpiazzata Da Nora Finti)` (deed: `- P-038
  (Rita Modelli)`). Gold: directors [TO CONFIRM] (the latest state document says the director resigned and was replaced
  by Nora Finti, P-047, of the identity layer); every other field a fact. Unmasked pack: the name is not identified ->
  the line opens -> every field of the extract [TO CONFIRM] (declared: a directors' row keeps [TO CONFIRM]).
  Never-event if [P-038] is published as fact. A careful human sees the change: yes.
- E-0020 AMOUNT - resolution: `... from EUR 40.000,00 to EUR 90.000,00 Versati Per Intero Da Tina Collaudi Che Diventa
  Socia Unica. The increase has been fully subscribed and fully paid in.` (Tina Collaudi = P-040, the 40% holder).
  Gold: capital 90.000 x3 (the increase is stated); holders [TO CONFIRM] (the words say P-040 became the sole holder);
  ownership [TO CONFIRM]. Unmasked pack: any other word in the amount -> the line is not explained -> every field
  [TO CONFIRM], and "Socia Unica" may state a holding -> BLOCK. Never-events: 40.000 as fact; 60/40 as fact or an
  effective holding.
- E-0021 COUNT - deed clause: `EUR 36.000,00, divided into 3.600 quotas Passate Tutte A Walter Campioni Dopo La Rinuncia
  Degli Altri, fully subscribed and fully paid in.` (Walter Campioni = P-043, the 20% holder; the table says 50/30/20;
  the later extract says 50/30/20 and the three capital values). Gold: capital 36.000 x3 (deed amount + extract);
  holders [TO CONFIRM] (the clause says every quota passed to P-043, the table says otherwise); ownership [TO CONFIRM].
  Unmasked pack: words inside the count -> NAT-999 and an unexplained line; a name + "quotas" may state a holding ->
  BLOCK. Never-event if 50/30/20 is published as fact or an effective holding derived.
- E-0022 ADDRESS town + second source, gazetteer entries only out of pattern: `Via della Prova 9, Selvaprototipo
  Casalprova (ZZ)` in deed and extract alike. Gold: office [TO CONFIRM] (two towns side by side); all else fact,
  PUBLISH. Never-event if the office is published as fact.
- E-0023 ADDRESS town, single source: office transfer 2026-05-20 to `Via del Collaudo 31, Monteprototipo Compagine Dei
  Soci Interamente Rinnovata (ZZ)`. Gold: office [TO CONFIRM]; holders [TO CONFIRM] (the words say the holders were
  wholly renewed); ownership [TO CONFIRM]. Never-events: the new or old office as fact; 70/30 as fact or effective.
- E-0024 ADDRESS street + second source, gazetteer entries only out of pattern: `Corso dei Modelli Fonderie 12,
  Borgoprova (ZZ)` in deed and extract alike (a trade word inside the street). Gold: office [TO CONFIRM]; PUBLISH the rest.
- E-0025 ADDRESS street, single source: office transfer 2026-07-07 to `Viale degli Esempi Dotazione Portata A
  Trecentomila 40, Pietrafinta (ZZ)` (a numeral word). Gold: office [TO CONFIRM]; capital x3 [TO CONFIRM] (the words say
  the endowment was brought to 300.000); holders and directors fact. Unmasked pack: numeral in a slot -> IDN-010; no
  holding -> every field [TO CONFIRM] (a block is also declared for a numeral). Never-events: 150.000 as fact; any office.
- E-0026 identity-layer name inside an address: extract office `Via del Segnaposto Zita Fantasmi 8, Torremodello (ZZ)`
  (deed: `Via del Segnaposto 8, Torremodello (ZZ)`; Zita Fantasmi = P-044, a person of another entity). Gold: office
  [TO CONFIRM]; the rest fact. Never-event if either office is published as fact.

### G. Premise probes (the same added words alike in two documents)
- E-0027 P1 town, WITH numeral: `Vicolo Fittizio 3, Lagosintetico Capitale Elevato A Duecentomila (ZZ)` in deed and
  extract (clause: 50.000). Gold: office [TO CONFIRM]; capital x3 [TO CONFIRM]; holders/directors fact. Unmasked pack:
  IDN-010 numeral with the capital in the same document -> BLOCK (declared). Never-events: office as fact; 50.000 as fact.
- E-0028 P2 street, no numeral: `Via dei Prototipi Quote Riunite In Un Solo Socio 15, Castelfittizio (ZZ)` in deed and
  extract (table 50/50). Gold: office [TO CONFIRM]; holders [TO CONFIRM]; ownership [TO CONFIRM]. Unmasked pack: IDN-999,
  "Socio" may state a holding -> BLOCK. Never-events: office as fact; 50/50 as fact or effective.
- E-0029 P3 company name, gazetteer entries only, person first: `Olga Fasulli Saline Valfittizia S.r.l.` in every
  header, clause 1 and `Name:` (Olga Fasulli = P-060, holder of E-0032, not of this entity). Gold: name [TO CONFIRM];
  the rest fact. Never-event if the name is published as fact.
- E-0030 P4 title alike in two documents of the same day: `Minutes of the holders' meeting that moved the seat
  (synthetic).` in the resolution and the appointment. Gold: capital 80.000 x3; directors [P-058]; office [TO CONFIRM]
  (two documents say the seat moved; no address). Unmasked pack: TXT-999 -> every field of both [TO CONFIRM].
  Never-event if Via del Collaudo 3 is published as fact.
- E-0031 P5 street with an identity-layer person's name, gazetteer entries only: `Piazza Inventata Walter Campioni 6,
  Portoinventato (ZZ)` in deed and extract (Walter Campioni = P-043, holder of E-0021). Gold: office [TO CONFIRM].
- E-0032 P6 town + surname, gazetteer entries only: `Via della Prova 27, Pratofinto Collaudi (ZZ)` in deed and extract.
  Gold: office [TO CONFIRM].
  (Different from run 22's wordings: none of `Pontecollaudo Valcollaudo`, `Borgoprova Dino Fasulli`, `Fonderie
  Rivaprova Nora Ipotetici`, `Dotazione Novantamila`, `Capitale Raddoppiato`, `Sede Trasferita` ... is reused.)

### H. Count-form probes
- E-0033 C1 exact NAT-025 in the evaluator's wording: `EUR 240.000,00, split into 2.400 registered shares, fully
  subscribed and fully paid in.` (S.p.A.); extract agrees. Gold: PUBLISH 240.000 x3. Unmasked pack: three facts.
- E-0034 C2 partial payment: `EUR 80.000,00, divided into 8.000 quotas, subscribed in full and paid in as to one half.`;
  extract resolved 80.000; subscribed 80.000; paid in 40.000. Gold: resolved 80.000, subscribed 80.000, paid in 40.000,
  holders fact. Unmasked pack per CHANGELOG 2.0.10: not the NAT-025 wording -> subscribed and paid in [TO CONFIRM],
  and BLOCK if the line is one no capital rule explains (declared). Never-event: 80.000 published as paid in.
- E-0035 C3 exact form in the deed, later extract contradicts the paid-in amount (25.000). Gold: resolved 50.000 fact,
  subscribed 50.000 fact, paid in DISCREPANCY [50.000, 25.000]. Unmasked pack: the same (CHANGELOG 2.0.10 section 2:
  "with the other paid-in amount: resolved and subscribed facts, paid in a DISCREPANCY"). Never-event: paid in shown as
  one value.
- E-0036 C3b exact form + a second sentence of the same clause (`Of that amount EUR 15.000,00 is still to be paid in.`);
  extract says paid in 45.000. Gold: resolved 60.000, subscribed 60.000, paid in [TO CONFIRM] (the clause contradicts
  itself). Unmasked pack: a second sentence -> NAT-070 resolved only; subscribed/paid in from the extract alone or
  [TO CONFIRM]. Never-event: paid in 60.000 or 45.000 as a single fact.
- E-0037 C4 counts of quotas per holder with a Total that equals the rows (1.500 + 500 = 2.000) and the count form of the
  capital. Gold: PUBLISH 3/4, 1/4; 20.000 x3 (inside the classes: counts with one total, since 2.0.3/2.0.4).

### I, K, L, M
- E-0038 Frantoi Vicolo Fittizio S.r.l. - own name holding a street entry, alike in deed and extract. Gold: PUBLISH
  (every word identified, two documents alike). Declared: NAM-005 keeps [TO CONFIRM] -> an abstention is a price.
- E-0039 Saline Castelbugia S.r.l. (town OUTSIDE the gazetteer, in the office and the name), E-0040 Birrerie Montefinto
  S.r.l. (trade word OUTSIDE), E-0041 Cartiere Serrafinta S.r.l. (holder P-071 Orazio Larve, director P-072 Tancredi
  Finti: a surname and a first name OUTSIDE), E-0042 Tipografie Valcollaudo S.r.l. (street `Via delle Fucine 3` OUTSIDE).
  No other probe. Gold: PUBLISH all four. The pack's declared behaviour: [TO CONFIRM] (IDN-999), and BLOCK for E-0041
  (a holders' row whose person the gazetteer does not hold). That is the price of the gazetteer, measured.
- E-0043 Immobiliare Fontesegnaposto S.r.l. - a table only a careful human reads: rows `see note (a)` / `see note (b)`
  then `Note (a): three quarters of the capital.` / `Note (b): the remaining quarter.` with no blank line; extract 75/25.
  Gold: PUBLISH 3/4, 1/4. Declared: a row whose share is not typed / a line after a list -> BLOCK (rightly by class).
- E-0044 Saline Borgoprova S.r.l. - heading `Article 4 Stockholders:` and rows `1) P-013 (Piero Campioni): 55 per
  cent` / `2) P-015 (Sergio Fasulli): 45 per cent`. Gold: PUBLISH 11/20, 9/20. Inside the classes if "per cent" after
  digits is a share form; if blocked, to be classified against the list (not declared as such).
- E-0045 Frantoi Lagosintetico S.r.l. - appointment file `2026-02-15_appointment.txt` with header date 2026-02-10.
  Gold: PUBLISH; directors [P-019]; filename_divergences [{DOC-E0045-03, date}].

## 2. Unmask check of every probe entity (every OTHER line checked against section 0)

Method: for each probe entity the generator writes every line that is not the probe from the reference forms of
section 0 (same function, same fixed words, standard rows built from the identity layer, amounts in the pack's own
format `EUR N.NNN,NN`, dates ISO, slugs of the pack). The check below names the probe line(s) and states that every
other line is standard; where any other line is NOT standard, it is named. Verified by reading the generated files
(E-0006, E-0025, E-0036, E-0045 read in full after generation; the rest by the generator's code paths).

| Entity | Probe line(s) | Every other line standard? | Note |
|---|---|---|---|
| E-0010 | the whole third document (type `Chamber annotation`, title, one sentence) | yes (deed S01 form, extract S01 form) | header of the third document is well formed (6 lines, edition ANNOT/1, Entity line alike) |
| E-0011 | third document (`Notarial certificate`) | yes | idem, CERT/1 |
| E-0012 | third document (`Letter to the registry`) | yes | idem, LETTER/1 |
| E-0013 | third document (`Report of the auditor`) | yes | idem, REPORT/1 |
| E-0014 | second line of the resolution | yes (title and first sentence S03 form) | - |
| E-0015 | last line of the appointment (after a blank) | yes (title, heading, row S06 form) | - |
| E-0016 | last line of the transfer (after a blank) | yes (title, heading, rows S06 form) | - |
| E-0017 | second line of the office transfer | yes (first line EXT-OFFICE-010 form, both addresses gazetteer, old = deed's) | - |
| E-0018 | last line of the summary (after a blank) | yes (three figure lines S04 form; `Financial year: 2025` header) | - |
| E-0019 | directors' row of the extract | yes (deed fully standard; extract labels standard; holders row standard) | - |
| E-0020 | the resolution sentence (words after the second amount) | yes | the rest of the sentence is the S03 form |
| E-0021 | deed clause 3 (words inside the count) | yes (clauses 1, 2, 4, 5 standard; extract standard with three values) | the form around the words is NAT-025's |
| E-0022 | office line of deed (clause 2) and of extract (`Registered office:`) - the same words alike | yes | - |
| E-0023 | new address of the office transfer | yes (deed, extract standard; old address = deed's) | - |
| E-0024 | office line of deed and extract alike | yes | - |
| E-0025 | new address of the office transfer | yes (S.p.A. deed with two directors, both rows standard) | - |
| E-0026 | office line of the extract | yes (deed clean) | - |
| E-0027 | office line of deed and extract alike (numeral word) | yes | - |
| E-0028 | office line of deed and extract alike | yes | - |
| E-0029 | `Entity:` header of both documents, clause 1, `Name:` (the same name alike) | yes | - |
| E-0030 | title line of the resolution and of the appointment (alike) | yes (sentence, heading, row standard) | - |
| E-0031 | office line alike | yes | - |
| E-0032 | office line alike | yes | - |
| E-0033 | deed clause 3 (count form, no probe word) | yes | - |
| E-0034 | deed clause 3 (partial payment); extract capital in the S03 three-value form | yes | - |
| E-0035 | deed clause 3 (exact count form); extract capital S03 three-value form | yes | - |
| E-0036 | deed clause 3 (two sentences on one line) | yes | - |
| E-0037 | deed clause 3 (count form) and holders' rows with counts + `Total:` | yes | counts form claimed since 2.0.3 |
| E-0038 | the name (every header, clause 1, `Name:`) | yes | - |
| E-0039..42 | the OUTSIDE word in its slot | yes | no other probe |
| E-0043 | holders' rows + two note lines | yes | - |
| E-0044 | holders' heading + two rows | yes | - |
| E-0045 | file name of the appointment | yes | - |
| E-0006, E-0007, E-0008, E-0009 | the holders' table | yes | - |

Known shared trait of every document: clause 1 ends with the legal form and no further full stop (as S01), the
blank line between the holders' rows and `5. Directors.` is present everywhere, every row names the identifier's own
name of the identity layer. Nothing else deviates from section 0, so a field kept [TO CONFIRM] or a block in a probe
entity is caused by the probe, not by another line (masked: no). After the run every unread/open line the pack reports
per probe entity is listed in the evaluator's folder README with the verdict masked yes/no.

## 3. Expected tally (gold)
45 entities; 2 BLOCKED (E-0008, E-0009); 43 build OK. Fields [TO CONFIRM] in the gold: E-0016 (2), E-0019 (1),
E-0020 (1), E-0021 (1), E-0022 (1), E-0023 (2), E-0024 (1), E-0025 (4), E-0026 (1), E-0027 (4), E-0028 (2), E-0029 (1),
E-0030 (1), E-0031 (1), E-0032 (1), E-0036 (1) = 25. One DISCREPANCY (E-0035 paid in). Ownership [TO CONFIRM]:
E-0020, E-0021, E-0023, E-0028. One filename divergence (E-0045).
