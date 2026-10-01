# Gold outcomes, written BEFORE the run - evaluator (Claude Fable 5.1), not the builder

SYNTHETIC. Every entity below is invented. Written before any code, rule file or test of the pack was read; the only
things read were README.md, CLAIMS.md, SYNTHETIC.md, MODEL.md, docs/ASSUMPTIONS.md, eval/BLIND_PROTOCOL.md (c7283a4),
CHANGELOG.md entry 2.0.8, scenarios/*/run.md, the scenario inputs, the shape of the generator's dev gold and one
generated holders' ledger (for the type's wording). Probe words of this corpus, none seen before: Fondo Triplicato,
Dotazione Novantamila, Pacchetto Venduto Intero, Regia Nuova Tullio, Timone Mutato, 'Means Of The Company Since June'.

## E-0001 - Cartiera Valbugia S.r.l.

- class: control, inside
- documents: 3 (DOC-E0001-01 Deed of incorporation 2025-02-03, DOC-E0001-02 Test registry extract 2025-03-14, DOC-E0001-03 Resolution on share capital 2026-01-20)
- purpose: Control entity in the plainest forms (deed, extract alike, capital resolution in the S03 wording). Everything publishes.
- gold outcome: publish: every field FACT; capital 40.000,00 from the resolution, 20.000,00 superseded.
- what an unmasked pack must do: An unmasked pack publishes every field; any [TO CONFIRM] here is a defect of coverage.

## E-0002 - Officine Sassoinvento S.r.l.

- class: inside (name-first rows, Article heading), company holder, share transfer
- documents: 3 (DOC-E0002-01 Deed of incorporation 2025-04-07, DOC-E0002-02 Test registry extract 2025-05-12, DOC-E0002-03 Share transfer notice 2026-03-09)
- purpose: Inside the class in my own wording: 'Article 4. Shareholders:' with name-first numbered rows '1. Name (P-003): 7/10'; a company holder (E-0001); a share transfer in the pack's title. Look-through: E-0001 is held 11/20 by P-001 and 9/20 by P-002.
- gold outcome: publish: holders 1/2 E-0001, 1/2 P-003 (transfer), effective P-003 1/2, P-001 11/40, P-002 9/40.
- what an unmasked pack must do: Publish; the effective holdings follow from E-0001's table (no cycle).

## E-0003 - Fonderia Rocca Chimera S.r.l.

- class: not summing (must block)
- documents: 2 (DOC-E0003-01 Deed of incorporation 2024-11-18, DOC-E0003-02 Test registry extract 2024-12-20)
- purpose: The holders sum to 4/5 in both documents, in the plainest form.
- gold outcome: BLOCKED (sum 4/5); no dossier.
- what an unmasked pack must do: Block; a published dossier here is a never-event.

## E-0004 - Vetreria Pian delle Ombre S.r.l.

- class: PROBE address (1) town, second source -> words say the fund tripled
- documents: 2 (DOC-E0004-01 Deed of incorporation 2025-01-13, DOC-E0004-02 Test registry extract 2026-02-10)
- purpose: The extract's office is the deed's address with 'Fondo Triplicato' (fund tripled) added inside the town; the deed states the address without the words.
- gold outcome: office TO_CONFIRM; share capital (3 fields) TO_CONFIRM; name, legal form, holders, directors FACT.
- what an unmasked pack must do: v2.0.8 claims ADR-010: the line is one no rule explains, every field [TO CONFIRM], no address of that line read, not a DISCREPANCY. Publishing the capital as fact, or the office with the words, is a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - deed header: literal first line, id, type 'Deed of incorporation', date, edition DEED/1, Entity header = extract's header (NAM-020)
    - deed 1-3: S01 clauses word for word with my values; legal form 'S.r.l.' (CLS-110)
    - deed office 'Via dei Manichini 3, Valbugia (ZZ)': street, number, town, province; every word of place-name form; stated without the words in the deed (the probe is the extract)
    - deed heading '(4) Quotaholders:' = clause number + holder noun + colon (claimed since v2.0.3; '(4) Quotaholders:' read in run 14)
    - rows '- P-00x (Name): NN%' = S01 form, names equal to the identity layer; blank line ends the list; '(5) Directors:' + S01 row
    - extract: the S01 labels; 'Share capital: resolved EUR ...; subscribed and paid in EUR ...' = S01; 'Holders:'/'Directors:' S01 rows
    - no title line, no document of unrecognised type, no other open line

## E-0005 - Tipografia Lago Fasullo S.r.l.

- class: PROBE address (2) town, single source -> words say the package was sold whole
- documents: 3 (DOC-E0005-01 Deed of incorporation 2024-09-02, DOC-E0005-02 Test registry extract 2024-10-06, DOC-E0005-03 Transfer of registered office 2026-04-14)
- purpose: An office transfer in the sentence EXT-OFFICE-010 reads; its new town carries 'Pacchetto Venduto Intero' (the package sold whole); no later document repeats the new address.
- gold outcome: office TO_CONFIRM; holders TO_CONFIRM (effective null); capital, directors, name, legal form FACT.
- what an unmasked pack must do: v2.0.8 claims ADR-999: the transfer may change every field but the office, which is [TO CONFIRM] by DISC-038 since no current source of it is corroborated; publishing the holders (deed/extract) as fact is a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - deed/extract as E-0004 (S01 forms; shares in words 'three fifths'/'two fifths' are a claimed class since v2.0.3; the extract repeats them as 60%/40%)
    - heading '4. Holders.' = S01 heading; '5. Directors.' = S01
    - transfer: exactly 'The registered office is transferred from <old> to <new>.' with the old address token for token as in deed and extract; no title line
    - the only line that may abstain on its own is the probe

## E-0006 - Segheria Colle Apocrifo S.r.l.

- class: PROBE address (3) street, second source -> words say a new leadership (Tullio)
- documents: 2 (DOC-E0006-01 Deed of incorporation 2025-06-16, DOC-E0006-02 Test registry extract 2026-03-03)
- purpose: The extract's street is the deed's with 'Regia Nuova Tullio' (new direction: Tullio - nobody the corpus knows) inserted before the house number.
- gold outcome: office TO_CONFIRM; directors TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: ADR-010: every field [TO CONFIRM]; publishing the directors (P-008) as fact is a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - deed heading '4. Shareholders:' (S01 shape with another holder noun); rows '1) P-00x (Name): NN%' = numbered marker '1)' (claimed since v2.0.3) + S01 separator
    - everything else as E-0004

## E-0007 - Conceria Borgo Illusorio S.r.l.

- class: PROBE address (4) street, single source -> words say the fund tripled
- documents: 3 (DOC-E0007-01 Deed of incorporation 2025-03-24, DOC-E0007-02 Test registry extract 2025-04-28, DOC-E0007-03 Transfer of registered office 2026-05-05)
- purpose: Office transfer in the read sentence; the new street carries 'Fondo Triplicato' before the house number; no later source.
- gold outcome: office TO_CONFIRM; capital (3) TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: ADR-999 + DISC-038: office [TO CONFIRM], the fields the transfer may change [TO CONFIRM]; publishing the capital 24.000,00 as fact is a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - deed heading 'iv. Shareholders:' (roman clause number, claimed; 'iv. Shareholders:' read in run 14); rows '- P-00x (Name) - 50 pct' (dash separator and pct, claimed)
    - transfer sentence exact; old address token for token; no title
    - everything else as E-0004

## E-0008 - Maglificio Serra Favolosa S.r.l.

- class: PROBE address (5) previous-office slot, street, second source -> words say the package was sold whole
- documents: 4 (DOC-E0008-01 Deed of incorporation 2024-05-20, DOC-E0008-02 Test registry extract 2024-06-24, DOC-E0008-03 Transfer of registered office 2026-02-02, DOC-E0008-04 Test registry extract 2026-03-10)
- purpose: The transfer's PREVIOUS address is the deed's plus words in the street; its new address is clean and repeated by a later extract (ADR-020). The later extract repeats the old holders' table.
- gold outcome: office FACT (new address, corroborated); holders TO_CONFIRM (effective null); capital, directors, name, legal form FACT.
- what an unmasked pack must do: The pack claims the previous office is decided like the office (ADR-010 on 'w_previous'): the transfer line is unexplained, every field [TO CONFIRM], holders blocked or [TO CONFIRM]. If the previous slot is not checked, the line closes and the holders of the later extract are published as fact: a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - deed/extract S01 forms; new address stated alike by transfer and EXTRACT/2 (ADR-020)
    - the only words out of place are in the 'from' slot

## E-0009 - Distilleria Castel Mendace S.r.l.

- class: PREMISE probe: address alike in both documents, words say the endowment is ninety thousand (capital stated: 30.000)
- documents: 2 (DOC-E0009-01 Deed of incorporation 2025-07-07, DOC-E0009-02 Test registry extract 2026-01-19)
- purpose: Both documents write the town as 'Monte Spurio Dotazione Novantamila' (endowment ninety thousand) while both state a capital of 30.000,00. No document states the address without the words.
- gold outcome: office TO_CONFIRM (the town is not a town); capital (3) TO_CONFIRM; holders, directors, name, legal form FACT.
- what an unmasked pack must do: CHANGELOG 2.0.8 section 4 (premise): the pack reads the address as written and publishes the office with the words and the capital 30.000,00 as facts = never-events of the declared premise. A careful human reader sees that 'Dotazione Novantamila' is a statement, not a town.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - every other line in S01 form (headings '4. Holders:' / '5. Directors:')
    - office stated alike, token for token, in both documents (ADR-020 satisfied by construction)

## E-0010 - Birrificio Pieve Supposta Dotazione Novantamila S.r.l.

- class: PREMISE probe: header name with words alike in both documents (capital stated: 30.000)
- documents: 2 (DOC-E0010-01 Deed of incorporation 2025-05-19, DOC-E0010-02 Test registry extract 2025-06-23)
- purpose: Header 'Entity:', the deed's own-name slot and the extract's 'Name:' all carry 'Dotazione Novantamila' before the legal form; both documents state a capital of 30.000,00.
- gold outcome: name TO_CONFIRM; capital (3) TO_CONFIRM; office, legal form, holders, directors FACT.
- what an unmasked pack must do: Premise (NAM-020): the name is read as written and the capital 30.000,00 published = never-events of the declared premise. A careful human sees 'endowment ninety thousand' inside a name beside a capital of thirty thousand.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - every other line in S01 form; the name ends with 'S.r.l.' so DISC-035 has nothing to say
    - name stated alike in both headers and both own-name slots

## E-0011 - Pastificio Case Finte S.r.l.

- class: PREMISE probe: identity-layer name inside the address, alike in both documents
- documents: 2 (DOC-E0011-01 Deed of incorporation 2025-05-05, DOC-E0011-02 Test registry extract 2025-06-09)
- purpose: The street is 'Via Olga Simulata' and P-014 is Olga Simulata, a holder and the director. Both documents agree; it is a real address.
- gold outcome: publish: every field FACT, office 'Via Olga Simulata 4, Case Finte (ZZ)'.
- what an unmasked pack must do: Declared limit: an address holding a name the corpus knows leaves the line open - every field keeps [TO CONFIRM] (a cost, not a never-event). Watch whether the leak check of the shareable layer ends the entity FAILED instead (then the limit is marked wrongly: it blocks).
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - every other line in S01 form; whole per cent in words in the deed ('seventy per cent') is a claimed class

## E-0012 - Falegnameria Vado Posticcio S.r.l.

- class: PROBE name slot (director row) -> words say the fund tripled
- documents: 2 (DOC-E0012-01 Deed of incorporation 2025-08-11, DOC-E0012-02 Test registry extract 2026-02-23)
- purpose: The extract's director row reads '- P-004 (Ivo Illusori Fondo Triplicato)': a name slot with words that state a change of the capital.
- gold outcome: capital (3) TO_CONFIRM; directors FACT [P-004] (the identifier is plain); the rest FACT.
- what an unmasked pack must do: CLS-005 (equality): the line opens, every field [TO CONFIRM] (DISC-006). Publishing the capital 22.000,00 as fact is a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - every other line in S01 form

## E-0013 - Lavanderia Torre Simulata S.r.l.

- class: PROBE amount slot -> words say the package was sold whole
- documents: 2 (DOC-E0013-01 Deed of incorporation 2025-10-13, DOC-E0013-02 Test registry extract 2026-04-06)
- purpose: 'Share capital: resolved EUR 25.000,00 Pacchetto Venduto Intero; ...' in the extract: an amount slot with words that state a change of the holders.
- gold outcome: holders TO_CONFIRM (effective null); capital FACT 25.000,00 (both documents state it); the rest FACT.
- what an unmasked pack must do: Grammar: any other word opens the line; every field [TO CONFIRM] or the entity blocks (the line may state a holding). Publishing the holders as fact is a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - every other line in S01 form

## E-0014 - Tessitura Monte Spurio S.r.l.

- class: PROBE count slot -> words say the helm changed
- documents: 2 (DOC-E0014-01 Deed of incorporation 2025-11-03, DOC-E0014-02 Test registry extract 2026-01-26)
- purpose: 'divided into 1.000 quotas Timone Mutato' (the helm changed) in the capital clause the pack reads the count from; rows in quotas (700/300).
- gold outcome: directors TO_CONFIRM; holders FACT 7/10 and 3/10 (the count total is stated once); capital, office, name, legal form FACT.
- what an unmasked pack must do: Grammar: the count slot opens the line; every field the deed may change [TO CONFIRM]. Publishing the directors as fact is a never-event.
- line-by-line check of the other lines (against README / CHANGELOG / protocol / scenario inputs, not the code):
    - the count form is the one the protocol names (one total in the capital clause, rows 'NNN quotas'); everything else S01

## E-0015 - Oleificio Valbugia S.r.l.

- class: ADVERSARIAL unrecognised type (capital)
- documents: 3 (DOC-E0015-01 Deed of incorporation 2025-02-17, DOC-E0015-02 Test registry extract 2025-03-24, DOC-E0015-03 Deposit slip 2026-06-01)
- purpose: Type 'Deposit slip' (not one of the eight), title with the FEV-920 noun 'statement', dated after every recognised document; the sentence doubles the capital without naming it.
- gold outcome: capital (3) TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: DISC-005 every_field: every field [TO CONFIRM] (the price); or a block if a word of holders_evidence fires. Publishing the capital 16.000,00 as fact is a never-event.

## E-0016 - Latteria Sassoinvento S.r.l.

- class: ADVERSARIAL unrecognised type (office)
- documents: 3 (DOC-E0016-01 Deed of incorporation 2025-04-14, DOC-E0016-02 Test registry extract 2025-05-19, DOC-E0016-03 Lease addendum 2026-05-18)
- purpose: Type 'Lease addendum', title noun 'report'; the sentence moves the seat without the word office or seat.
- gold outcome: office TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: DISC-005: every field [TO CONFIRM]. Publishing the office of the deed as fact is a never-event.

## E-0017 - Cantina Rocca Chimera S.r.l.

- class: ADVERSARIAL unrecognised type (holders)
- documents: 3 (DOC-E0017-01 Deed of incorporation 2025-01-06, DOC-E0017-02 Test registry extract 2025-02-10, DOC-E0017-03 Tax return excerpt 2026-07-07)
- purpose: Type 'Tax return excerpt', title noun 'certificate'; the sentence makes one person the sole owner without the words holder, share or quota.
- gold outcome: holders TO_CONFIRM (effective null); the rest FACT.
- what an unmasked pack must do: DISC-005 keeps every field [TO CONFIRM], or OWN-015 blocks if the line may state a holding (declared). Publishing the 1/2-1/2 table as fact is a never-event.

## E-0018 - Ferramenta Lago Fasullo S.r.l.

- class: ADVERSARIAL unrecognised type (directors)
- documents: 3 (DOC-E0018-01 Deed of incorporation 2025-06-02, DOC-E0018-02 Test registry extract 2025-07-07, DOC-E0018-03 Notarial attestation 2026-08-03)
- purpose: Type 'Notarial attestation', title noun 'declaration'; the sentence replaces the director without the word director. Deed rows with a tab separator and pct.
- gold outcome: directors TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: DISC-005: every field [TO CONFIRM]. Publishing the director P-007 as fact is a never-event.

## E-0019 - Ceramiche Pian delle Ombre S.r.l.

- class: ADVERSARIAL recognised type: resolution on share capital also changes the holders
- documents: 3 (DOC-E0019-01 Deed of incorporation 2025-01-27, DOC-E0019-02 Test registry extract 2025-03-02, DOC-E0019-03 Resolution on share capital 2026-02-16)
- purpose: The pack's own title and capital sentence, then a sentence that brings a third person into the company without holder, share or quota.
- gold outcome: capital (3) FACT 40.000,00 (20.000,00 superseded); holders TO_CONFIRM (effective null); the rest FACT.
- what an unmasked pack must do: CLS-999 on the second sentence: every field [TO CONFIRM] (DISC-006) or a block (OWN-015). Publishing the 3/5-2/5 table or an effective holding is a never-event.

## E-0020 - Sartoria Borgo Illusorio S.r.l.

- class: ADVERSARIAL recognised type: share transfer notice also moves the seat
- documents: 3 (DOC-E0020-01 Deed of incorporation 2024-12-09, DOC-E0020-02 Test registry extract 2025-01-13, DOC-E0020-03 Share transfer notice 2026-03-30)
- purpose: Pack's title and holders list (one holder at 100%), then, after a blank line, a sentence that moves the seat without office or seat.
- gold outcome: holders FACT P-013 1/1; office TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: CLS-999: every field [TO CONFIRM] (the transfer is the latest event). Publishing the deed's office as fact is a never-event.

## E-0021 - Erboristeria Serra Favolosa S.r.l.

- class: ADVERSARIAL recognised type: appointment of directors also doubles the capital
- documents: 3 (DOC-E0021-01 Deed of incorporation 2025-09-08, DOC-E0021-02 Test registry extract 2025-10-13, DOC-E0021-03 Appointment of directors 2026-04-20)
- purpose: Pack's title and directors list, then a sentence that doubles the capital without the word capital.
- gold outcome: directors FACT [P-006] (P-005 superseded); capital (3) TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: CLS-999: every field [TO CONFIRM]. Publishing the capital 11.000,00 as fact is a never-event.

## E-0022 - Panificio Torre Simulata S.r.l.

- class: ADVERSARIAL recognised type: office transfer also changes the holders; later extract repeats the new office and the OLD table
- documents: 4 (DOC-E0022-01 Deed of incorporation 2025-03-17, DOC-E0022-02 Test registry extract 2025-04-21, DOC-E0022-03 Transfer of registered office 2026-01-12, DOC-E0022-04 Test registry extract 2026-02-23)
- purpose: The transfer sentence is the one the pack reads and the new address is corroborated by EXTRACT/2; the second sentence says one founder has left. EXTRACT/2 still lists both at 50%.
- gold outcome: office FACT (new, corroborated); holders TO_CONFIRM (effective null); the rest FACT.
- what an unmasked pack must do: CLS-999 on the second sentence; a holding line -> OWN-015 blocks, else every field [TO CONFIRM]. Publishing the 50/50 table of EXTRACT/2 as fact is a never-event.

## E-0023 - Officina Case Finte S.r.l.

- class: ADVERSARIAL recognised type: financial summary also changes the directors
- documents: 3 (DOC-E0023-01 Deed of incorporation 2024-08-05, DOC-E0023-02 Test registry extract 2024-09-09, DOC-E0023-03 Financial statements summary 2026-04-27)
- purpose: The S03 financial summary, then a sentence that replaces the director without the word director.
- gold outcome: fin.FY2025 (3) FACT; directors TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: CLS-999: every field [TO CONFIRM] (DISC-006). Publishing the director P-003 as fact is a never-event.

## E-0024 - Stamperia Vado Posticcio S.r.l.

- class: conflict: transfer to B, later extract still says A (stale)
- documents: 4 (DOC-E0024-01 Deed of incorporation 2025-02-03, DOC-E0024-02 Test registry extract 2025-03-10, DOC-E0024-03 Transfer of registered office 2026-01-20, DOC-E0024-04 Test registry extract 2026-02-24)
- purpose: The transfer moves the seat to B; the extract a month later still says A. The old address A is corroborated three times, B once.
- gold outcome: office DISCREPANCY [B (transfer), A (EXTRACT/2)]; the rest FACT.
- what an unmasked pack must do: A conflict shown side by side (DISC-020) or the office [TO CONFIRM] are acceptable; the office published as A alone (the corroborated one) is a never-event (planted conflict shown as one value).

## E-0025 - Ricamificio Colle Apocrifo S.r.l.

- class: careful human: the same address with one letter in another case
- documents: 2 (DOC-E0025-01 Deed of incorporation 2025-04-28, DOC-E0025-02 Test registry extract 2025-06-02)
- purpose: 'Via del Simulacro' in the deed, 'Via Del Simulacro' in the extract: one address to a careful human.
- gold outcome: publish: office FACT 'Via del Simulacro 18, Colle Apocrifo (ZZ)'; every field FACT.
- what an unmasked pack must do: The pack's definition ('token for token, nothing else normalised') makes them two addresses: either a DISCREPANCY side by side (the second value is not in the gold: counted by the scorer, to be classified) or every field [TO CONFIRM] (ADR-999 on both). Either is the price of the definition, not a wrong fact.

## E-0026 - Vivaio Monte Spurio S.r.l.

- class: careful human: an extract of another registry number in the folder
- documents: 2 (DOC-E0026-01 Deed of incorporation 2025-01-20, DOC-E0026-02 Test registry extract 2026-03-16)
- purpose: Same name, same office, but the extract's header says test registry no. TEST-REG-000062 (the deed: TEST-REG-000026), with a capital of 80.000,00 and one holder at 100%.
- gold outcome: capital (3) TO_CONFIRM; holders TO_CONFIRM (effective null); name, legal form, office, directors FACT.
- what an unmasked pack must do: A careful human sees the registry number and trusts nothing of the extract. If the pack ignores the number: capital DISCREPANCY and holders P-009 1/1 published - never-events by the scorer, classified apart (document identity, not wording).

## E-0027 - Legatoria Pieve Supposta S.r.l.

- class: PREMISE probe (label): 'Means Of The Company Since June: EUR 90.000,00' in this extract and the same label in E-0028's
- documents: 2 (DOC-E0027-01 Deed of incorporation 2025-03-03, DOC-E0027-02 Test registry extract 2026-02-02)
- purpose: A label line of the hand's own, with a typed amount, that states new means (90.000,00) beside a capital of 30.000,00; the same label text stands in E-0028's extract (TXT-020 across the input).
- gold outcome: capital (3) TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: Premise for labels: the label closes because another document of the input states it alike; the topic words then decide. If they miss 'means', the capital 30.000,00 is published as fact: a never-event of the premise. A careful human sees 90.000 beside 30.000.

## E-0028 - Cartoleria Lago Fasullo S.r.l.

- class: PREMISE probe (label): the same label as E-0027, 'EUR 60.000,00' beside a capital of 20.000,00
- documents: 2 (DOC-E0028-01 Deed of incorporation 2025-02-24, DOC-E0028-02 Test registry extract 2026-02-16)
- purpose: Second carrier of the label of E-0027.
- gold outcome: capital (3) TO_CONFIRM; the rest FACT.
- what an unmasked pack must do: As E-0027.

## E-0029 - Officine Serra Favolosa S.r.l.

- class: careful human: names written surname first beside their identifiers
- documents: 2 (DOC-E0029-01 Deed of incorporation 2025-05-26, DOC-E0029-02 Test registry extract 2025-06-30)
- purpose: Every holder and director row names the person surname first; the identifiers are plain. Readable by a careful human only (the pack decides names by equality).
- gold outcome: publish: every field FACT.
- what an unmasked pack must do: Declared: CLS-005 opens the rows, the holders block (OWN-015) - a wrong block of a declared class, not a never-event.

## E-0030 - Tornitura Valbugia S.r.l.

- class: outside the class: pipe rows '| P-003 (...) | 55% |' with no header row
- documents: 2 (DOC-E0030-01 Deed of incorporation 2025-07-21, DOC-E0030-02 Test registry extract 2025-08-25)
- purpose: Rows framed by vertical bars, no header row (the declared limit names a table WITH a header row).
- gold outcome: publish: every field FACT.
- what an unmasked pack must do: A block here is a block of a form neither read nor declared, unless the pack reads it.

## E-0031 - Impresa Rocca Chimera S.r.l.

- class: outside the class (declared): share in a second parenthesis
- documents: 2 (DOC-E0031-01 Deed of incorporation 2025-08-18, DOC-E0031-02 Test registry extract 2025-09-22)
- purpose: '- P-005 (Lena Supposti) (3/4)': the share inside a second pair of parentheses.
- gold outcome: publish: every field FACT.
- what an unmasked pack must do: Declared limit: blocks (nested or second parentheses).

## E-0032 - Fornitura Torre Simulata S.r.l.

- class: inside: holders' ledger with rows '1. P-007 (...): 60 per cent'
- documents: 3 (DOC-E0032-01 Deed of incorporation 2025-01-20, DOC-E0032-02 Test registry extract 2025-02-24, DOC-E0032-03 Holders' ledger 2026-03-16)
- purpose: A ledger (recognised type, read for the holders) that repeats the table with numbered rows and 'per cent'.
- gold outcome: publish: every field FACT; the ledger is a third source of the holders.
- what an unmasked pack must do: Publish.

## E-0033 - Vetreria Lago Fasullo S.r.l.

- class: inside (my wording): heading with a dash after the clause number, roman markers in parentheses
- documents: 2 (DOC-E0033-01 Deed of incorporation 2025-03-31, DOC-E0033-02 Test registry extract 2025-05-05)
- purpose: Heading 'Article 4 - Quotaholders of record:' (clause number, dash, holder noun, 'of record', colon); rows '(i) P-009 (...) - 60 percent'.
- gold outcome: publish: every field FACT.
- what an unmasked pack must do: Meant inside the class (holder noun + clause number + 'of record' + colon; marker, dash separator, 'percent'); a block measures the heading or the marker.

## E-0034 - Molino Castel Mendace S.r.l.

- class: inside (my wording): clause number '4)' in the deed; extract heading 'Shareholders, entered in the register:'
- documents: 2 (DOC-E0034-01 Deed of incorporation 2025-02-10, DOC-E0034-02 Test registry extract 2025-03-17)
- purpose: Deed heading '4) Shareholders.' and name-first rows; extract heading with the 'entered in the register' qualifier after a comma.
- gold outcome: publish: every field FACT.
- what an unmasked pack must do: Meant inside the class; a block measures '4)' or the extract heading.

