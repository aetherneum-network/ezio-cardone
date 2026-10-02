# Blind protocol

SYNTHETIC - this protocol measures a test pipeline on invented documents. It measures internal consistency
on synthetic data, never accuracy on real companies. Nothing real may be used as input.

Written after the freeze tag, by the author of the pack, for a **different hand**. The author (a synthetic
AI agent, via Claude Opus 5.5) does not choose the blind seed, never generates or looks at a blind corpus,
and does not run anything below.

**Updated after the tag `v2.0.10-freeze`.** The blind runs so far, all recorded in `eval/history.json`:

- `v2.0.0-freeze`: run once, by the evaluator, on 2026-09-30 (run 5, seed 20261011). Not passed: 13
  never-events (0 plain, 1 perturbed, 12 out-of-pool). Its fix (finding T16, `v2.0.1`) changed code, rules
  and tests: amounts grouped by an apostrophe or a space are read whole or abstained; the audit compares the
  digits of a quote; new rule `OWN-015` - a holders' table that could not be read blocks the entity
  (parameter `unverified_holders_table`, `[TO CONFIRM with legal]`).
- `v2.0.1-freeze`: run once, by the evaluator, on 2026-09-30 (run 7, seed 20261012). 0 never-events on every
  corpus. But `OWN-015` blocked entities that the gold builds: 89 of 150 in the perturbed corpus (3 of 150 in
  the plain corpus, 0 of 2 in the hand-written one), most of them because their holders' table was worded
  in a form the rules did not read. `v2.0.2` (decisions D26 and D29) read more forms of that table, kept
  `OWN-015` at `block` and aligned the never-event definition with the scorer.
- `v2.0.2-freeze`: run once, by the evaluator, on 2026-09-30 (run 9, seed 20261013, hand corpus
  `eval/blind/hand-9/`). 0 never-events on every corpus. Blocked wrongly: 0 of 150 plain, 0 of 150 perturbed,
  4 of 9 hand-written (E-0003, E-0007, E-0008, E-0009). On the perturbed corpus 54 of the 144 published
  dossiers carried the holders `[TO CONFIRM]`, because a document of unrecognised type kept every field of its
  entity undecided (rule `DISC-005`).
- `v2.0.3-freeze`: run once, by the evaluator, on 2026-10-01 (run 11, seed 20261014, hand corpus
  `eval/blind/hand-11/`, 15 entities, 33 documents). **Not passed: 2 never-events**, both on hand-written
  entity E-0015 (0 on the plain and the perturbed corpus). A notice to creditors - a document of unrecognised
  type - raised the equity by a contribution in kind and moved the seat; the narrow scope of `DISC-005` in
  `v2.0.3` and rule `FEV-040` (a capital increase changes the capital, never the holders) let the holders of
  an older registry extract, and the effective holding derived from them, be published as facts where the
  gold says they cannot be decided. Blocked wrongly: 2 of 150 plain, 2 of 150 perturbed, 8 of 15
  hand-written, 6 of them on forms that `v2.0.3` did not declare. `CLAIMS.md` downgrades A2 for
  `v2.0.3-freeze`; `CHANGELOG.md` (entry 2.0.4) says that the heading of the known limits of 2.0.3 was false.
- `v2.0.4-freeze`: **not run blind**. Its `CHANGELOG.md` (entry 2.0.4) declared one known limit that may
  publish - a document of a recognised type was read for the fields of its kind only - and `v2.0.5` closes it
  before any blind run (decision D34).
- `v2.0.5-freeze`: run once, by the evaluator, on 2026-10-01 (run 14, seed 20261015, hand corpus
  `eval/blind/hand-14/`, 15 entities, 40 documents). 0 never-events on every corpus. Blocked wrongly: 2 of 150
  plain, 3 of 150 perturbed, 5 of 15 hand-written. Fields left `[TO CONFIRM]`: 0 of 1371, 647 of 1363, 63 of 72
  - every deed of the hand corpus ended its first clause with `its legal form is S.r.l..`, which the rules did
  not read, so the line could change every field. That miss masked two probes of the residual risk declared by
  `CHANGELOG.md` 2.0.5 section 4 (E-0011, a person slot with four extra words; E-0012, a name ending in `S.p.A.`
  beside the legal form `S.r.l.`): with the deed in the form the rules read, the code of `v2.0.5-freeze` publishes
  3 never-events on those two entities (measured by the builder on a variant of seen data, `CHANGELOG.md` 2.0.6
  section 2). The statement "no case is known" of that section, and the marking of a document of unrecognised
  type as one that only keeps `[TO CONFIRM]`, were wrong (`CHANGELOG.md` 2.0.6).
- `v2.0.6-freeze`: run once, by the evaluator, on 2026-10-01 (run 16, seed 20261016, hand corpus
  `eval/blind/hand-16/`, 28 entities, 59 documents). 0 never-events on every corpus. Blocked wrongly: 4 of 150
  plain, 5 of 150 perturbed, 15 of 28 hand-written. Fields left `[TO CONFIRM]`: 0 of 1384, 665 of 1370, 43 of 99.
  Of its six typed-slot probes, three blocked (E-0013, E-0018: a name beside an identifier the pack does not know;
  E-0017) and three kept every field `[TO CONFIRM]` (E-0014, E-0015, E-0016). Two of them were masked: E-0017 (a
  total line written outside the capital clause blocked the entity on its own) and E-0014 (its office wording,
  `The seat of the company is moved from`, is the unknown wording of scenario S09, which no field rule reads).
  Measured afterwards by the builder by class, the residual risk declared by `CHANGELOG.md` 2.0.6 section 4
  was real on that code: 312 of 600 constructed siblings unsafe, 56 of them a FAILED run (`CHANGELOG.md` 2.0.7
  section 2). The other findings went the cautious way: a sentence written right after a list was read as a row of
  it (E-0010 blocked, the directors of E-0019 `[TO CONFIRM]`), "its own" counted as a word of holding (E-0006,
  E-0011 blocked), an illegible amount as a bare figure (E-0114 of the perturbed corpus blocked).
- `v2.0.7-freeze`: run once, by the evaluator, on 2026-10-01 (run 18, seed 20261017, hand corpus
  `eval/blind/hand-18/`, 27 entities, 67 documents). **Not passed: 4 never-events**, all on hand-written entity
  E-0015 (0 on the plain and the perturbed corpus). Its registry extract gave as registered office the deed's
  address with three words added inside the town, each of the form of a place name and none of a class of
  `slot_not_name_word`: the line closed, the office was shown as a DISCREPANCY whose second value carried the
  words, and the share capital those words speak of was published as a fact - the residual risk that
  `CHANGELOG.md` 2.0.7 section 4 had declared `[TO CONFIRM]`. Blocked wrongly: 3 of 150 plain, 3 of 150 perturbed,
  10 of 27 hand-written, three of them (E-0020, E-0025, E-0026) on forms that `v2.0.7` neither read nor declared.
  Fields left `[TO CONFIRM]`: 0 of 1408, 673 of 1408, 75 of 134. Of its six typed-slot probes E-0015 published;
  E-0014 (the same class in the street of an office transfer) kept every field `[TO CONFIRM]` because one of its
  words is in the list, not by its form; E-0013 and E-0017 blocked, E-0016 and E-0018 kept every field
  `[TO CONFIRM]`. `CLAIMS.md` section 8 downgrades A2 for `v2.0.7-freeze`. After the run the coordinator measured
  hand-18 on the code of `v2.0.6-freeze`: the same 4 never-events on E-0015 (not blind; `README.md`).
- `v2.0.8-freeze`: run once, by the evaluator, on 2026-10-01 (run 20, seed 20261018, hand corpus
  `eval/blind/hand-20/`, 34 entities, 87 documents). **Not passed: 8 never-events**, 4 on hand-written entity
  E-0009 and 4 on E-0010 (0 on the plain and the perturbed corpus). In E-0009 the deed and the registry extract both
  wrote the town of the registered office as `Monte Spurio Dotazione Novantamila` beside a capital of 30.000,00; in
  E-0010 every header and the own-name clause wrote the name `Birrificio Pieve Supposta Dotazione Novantamila
  S.r.l.`. Stated alike by two documents, the office (`ADR-020`) and the name (`NAM-020`) were corroborated, and the
  office or the name with the words and three capital fields were published as facts - the premise of corroboration
  that `CHANGELOG.md` 2.0.8 section 4 had declared `[TO CONFIRM]`. Blocked wrongly: 4 of 150 plain, 4 of 150
  perturbed, 6 of 34 hand-written, one of them (E-0030: holders' rows framed by vertical bars with no header row) on a
  form `v2.0.8` neither read nor named. Fields left `[TO CONFIRM]`: 271 of 1379, 839 of 1379, 121 of 216. The other
  probes went the cautious way; two of them (E-0007, E-0020) were masked at field level by their own names, which
  hold the street word `Borgo`, a topic word of the office that `_slot_closes` tested on the own-name slot; a
  registry extract filed with the documents of E-0026 was built as an entity E-0062 of its own. `CLAIMS.md` section
  10 downgrades A2 for `v2.0.8-freeze`.
- `v2.0.9-freeze`: run once, by the evaluator, on 2026-10-01 (run 22, seed 20261019, hand corpus
  `eval/blind/hand-22/`, 42 entities, 100 documents, written in the gazetteer of `SYNTHETIC.md` so that no probe is
  masked by it). **0 never-events** on the plain, the perturbed and the hand-written corpus; the sum of the eight
  `*_wrong_committed` fields 0 in each. Facts exact 1069/1282, 491/1282 and 78/223; fields left `[TO CONFIRM]` 213
  of 1363, 825 of 1363 and 145 of 251; blocked wrongly 4 of 150 in each generated corpus (the illegible share the
  generator plants, D26) and 10 of 42 hand-written, each a declared limit or a declared rule. Every probe was
  unmasked and none published a value as fact. Four defects, none of which publishes: D1, in a work folder of 282
  characters `eval/score.py` read the build by plain path, counted 31 built entities failed and 0 fields, and
  exited 0 with an empty stderr - a measurement that did not measure and did not fail; D2, the count form `EUR
  20.000,00, divided into 2.000 quotas, fully subscribed and fully paid in` left the subscribed and the paid-in
  capital `[TO CONFIRM]` (E-0007); D3, the sentence of `CHANGELOG.md` 2.0.9 on an address "with a name the corpus
  knows inside it" is not what the code does: a whole gazetteer street holding a surname was published, with the
  right value (E-0033); D4, the row `- Name [P-015]: 60%` blocks without being named among the limits (E-0006).

The change of `v2.0.10` (finding D39, from run 22) changed code, rules, tests and the scorer. `OWN-015` and
`unverified_holders_table` keep `block` (D26); holders written in a sentence stay unread (D31); `DISC-005` keeps
`every_field`; `DISC-006`, `CLS-005`, `DISC-035` and `DISC-038` stay; what `v2.0.9` decides by identification is
exactly as strict.

- `eval/score.py`: the build is read through the extended-length form of the work folder, the way the pipeline
  writes it. A measurement that did not measure is FAILED - an entity the run reports as built that cannot be read,
  counts of the run that differ from its own list of entities or from what the scorer read, built entities with no
  scored field, an entity of the gold missing from the run -, and the scorer then exits **3**, with the reason on
  stderr (`MEASUREMENT FAILED - <label>: ...`) and in the result (`measurement`); a run that raises is exit 3 with its
  reason, not a traceback. Exit 0: measured, no never-event; exit 1: a never-event; 3 wins over 1.
  `tools/rebuild.py`, `tools/manifest.py` and the work folders of the scenarios read the same way; the rebuild
  refuses a walk that reads no file.
- `rules/figure_nature.json` `NAT-025`: the count form of the capital clause - the amount, then `, divided (or
  split) into N [ordinary | registered | equal] quotas (or shares), fully subscribed and fully paid in`, nothing
  after it but the full stop, the amount the only current amount of the clause - gives the three natures of the
  plain form (`NAT-020`), which now asks for a single current amount too. Any other wording is left to `NAT-070`
  (resolved only) and `NAT-999` (no nature), as before.
- Declared, behaviour as measured, each made true by a test (`tests/test_d39_limits.py`): a holder row with the
  identifier in square brackets (hand-22 E-0006, three orders) - **blocks**; a blank line inside a list of holders
  (hand-22 E-0005) - **blocks**; a numeral in a free-text slot of a line that may state a holding (`IDN-010`, hand-22
  E-0025 and E-0028) - **blocks**, by design; an address whose whole gazetteer street entry holds a known surname
  (hand-22 E-0033) is read when it is identified and corroborated, while a known name outside an entry leaves it
  open - the sentence of entry 2.0.9 is restated.
- `dossier/s7_audit.py`: the audit's caches are keyed by the content of the rules (a SHA-256 of the rule files),
  not by `id()`, which Python may hand to a later object (a process that loads two rule sets could be served the
  identification of the other one).
- Tests: `tests/test_d39_scorer.py` (15 tests), `tests/test_d39_capital_count.py` (5 tests; 78 siblings by class),
  `tests/test_d39_limits.py` (5 tests); `tests/support.py` removes the temporary folders it creates and gives each
  child process a TEMP of its own; `tests/test_rules.py` counts 109 rules (364 tests in all, no expected failure).
  Of the 78 siblings the code of `v2.0.9-freeze` publishes 0 wrongly and `v2.0.10` 0; on `v2.0.10` the count forms
  give what the plain form gives.

The change of `v2.0.10` was written by the builder's hand after reading the results and the hand-written documents
of run 22, and measured only on corpora already seen (run 23, not blind; numbers in `CHANGELOG.md` 2.0.10): 0
never-events on all thirty results, every measurement `OK`; every count and metric equal to those of `v2.0.9` but
hand-22, fields exact 78 -> 80 of 223 (the subscribed and the paid-in capital of E-0007). `CHANGELOG.md` (entry
2.0.10) lists every known limit in two classes only - **blocks** or **keeps `[TO CONFIRM]`**; **none may publish**;
what the proof still rests on is section 4 of entry 2.0.9, unchanged.

The change of `v2.0.9` (finding D38, from run 20) changed code, rules and tests - not the scorer. `OWN-015` and
`unverified_holders_table` keep `block` (D26); holders written in a sentence stay unread (D31); `DISC-005` keeps
`every_field`; `DISC-006`, `CLS-005`, `DISC-035` and `DISC-038` stay; what `v2.0.8` closed stays closed.

- `rules/extract.json` (the gazetteer `gazetteer_*`; `identify_address`, `identify_company`, `identify_person`; the
  numerals `numeral_*`; `identification_slot_classes`; the group `free_text_identification`: `IDN-010`, `IDN-020`,
  `IDN-030`, `IDN-040`, `IDN-050`, `IDN-999`; `NAM-005`; `TXT-005`; `TXT-020`, outcome now `unexplained`),
  `dossier/s1_extract.py`: a free-text slot - the address of the office and of the previous office, the company's
  name of a header or of a name slot, a person's name beside an identifier, a title, a label - closes its line only
  when every word of it is identified by the gazetteer of the pack and it holds no numeral, whatever the documents
  agree on. An address is a street type and a street name of the gazetteer, a house number, a town and the province;
  a company's name a trade word and a town (or `Holding <town> Partecipazioni`), then its legal form; a person's name
  a first name and a surname; a title one of the two titles the pack's own builders write; no label is a recognised
  text. A slot that is not identified (`IDN-999`), or that holds a numeral (`IDN-010`: digits, an Italian or English
  number word, a Roman numeral), is a line no rule explains: every field `[TO CONFIRM]` (`DISC-006`), the entity
  blocked when the line may state a holding (`OWN-015`; a numeral may state a quantity). A header name that is not
  identified is unexplained even when every document states it alike (`NAM-005`). Corroboration (`ADR-*`, `NAM-*`)
  stays on top of identification. New legal assumption `identification_source` (`[TO CONFIRM with legal]`,
  `docs/ASSUMPTIONS.md`, twelve assumptions); the gazetteer is listed in `SYNTHETIC.md`.
- `dossier/s1_extract.py` (`_slot_closes`): the topic words of `unread_fields` and `holders_evidence` are no longer
  applied to any free-text slot; an own name holding a street word is decided by equality and identification.
- `dossier/s1_extract.py`: a document filed under one entity whose content names an entity with no folder of its own
  is also an unclassified document of the entity of its folder (`DISC-005`).
- `dossier/lib/jsonio.py` and the writers of the DOCX, zip and staging files: on Windows the work folder carries the
  long-path prefix, so a deep work folder builds without long-path support.
- `dossier/s7_audit.py`: the audit identifies with its own code (`_Ident`), entries of several words included.
- Declared, behaviour as measured: rows framed by vertical bars without a header row (hand-20 E-0030) - **blocks**; a
  capitalised particle (`Via Del ...`, hand-20 E-0025) - **keeps `[TO CONFIRM]`**; a registry extract filed with the
  documents of another entity (hand-20 E-0026 and E-0062) - the entity of the folder **keeps `[TO CONFIRM]`** every
  field from the extract's date, and **blocks** when its holders are not read whole.
- Tests: `tests/test_d38_identification.py` (15 tests; 624 siblings by class), `tests/test_d38_long_paths.py` (2
  tests); of the 624 siblings the code of `v2.0.7-freeze` publishes 267 wrongly, `v2.0.8-freeze` 154 and `v2.0.9`
  none; the 300 slot siblings of `tests/test_d37_slots.py` end with 0 FAILED (6 on `v2.0.8`, fail-closed);
  `tests/test_d36_forms.py` `D36_ResidualWordList` is no longer an expected failure, `tests/test_d37_forms.py`
  `D37_EqualityPremise` and `tests/test_d37_slots.py` `D37_NameEqualityPremise` now state the opposite of `v2.0.8`;
  `tests/test_rules.py` counts 108 rules (339 tests in all, no expected failure).

The change of `v2.0.9` was written by the builder's hand after reading the results and the hand-written documents
of run 20, and measured only on corpora already seen (run 21, not blind; numbers in `CHANGELOG.md` 2.0.9 sections 3
and 9): 0 never-events on all twenty-seven results, hand-20 8 -> 0; the nineteen generated results identical to
those of `v2.0.8` in every count and metric (the gazetteer is drawn from the generator's vocabulary, so a generated
corpus is identified by construction and says little); the price falls on the corpora written by hand, whose names
and places are not in the gazetteer: hand-20 published 27 -> 1 of 34 and blocked wrongly 6 -> 32, hand-18 published
16 -> 0 of 27, hand-16 14 -> 0 of 28, the out-of-pool corpus of run 5 published 94 -> 93 of 150 and facts exact
216 -> 82 of 925/918. `CHANGELOG.md` (entry 2.0.9) lists every known limit in two classes only - **blocks** or
**keeps `[TO CONFIRM]`**; **none may publish**; what the proof still rests on (section 4 of that entry) is stated in
the same two classes with nothing outside them: the premise of corroboration is closed, and the gazetteer itself
(`identification_source`) and the choice to identify persons by it are listed there as `[TO CONFIRM]`.

The change of `v2.0.8` (finding D37, from run 18) changed code, rules, tests and the scorer. `OWN-015` and
`unverified_holders_table` keep `block` (D26); holders written in a sentence stay unread (D31); `DISC-005` keeps
`every_field`; `DISC-006`, `CLS-005` and `DISC-035` stay; what `v2.0.7` closed stays closed.

- `rules/extract.json` (`address_corroboration`: `ADR-010`, `ADR-020`, `ADR-999`), `rules/discrepancy.json`
  (`DISC-038`), `dossier/s1_extract.py`: an address is a fact only when it is corroborated - stated alike, token
  for token, by two different documents of the entity, or stated by a recognised office transfer
  (`EXT-OFFICE-010`) and repeated alike by a source dated after it. An address equal to another of the entity
  plus words, anywhere in the street or the town, is a line no rule explains (`CLS-999`): every field
  `[TO CONFIRM]` (`DISC-006`), the entity blocked when the line may state a holding (`OWN-015`); it is not a
  DISCREPANCY and its words reach no value. An address that one document alone states (`ADR-999`): every field
  that document may change but the office `[TO CONFIRM]`, and the office `[TO CONFIRM]` when no current source of
  it is corroborated (`DISC-038`). Two whole different addresses stay a DISCREPANCY side by side (`DISC-020`).
- `rules/extract.json` (`name_corroboration`: `NAM-010`, `NAM-020`, `NAM-999`; `text_corroboration`: `TXT-010`,
  `TXT-020`, `TXT-999`; parameters `slot_text_groups`, `text_recognised`): the same principle for the company's
  name of the header `Entity:`, the title of `CLS-900` and the label of `CLS-250` - a title or a label closes its
  line only when another document of the input states it alike or it is one of the two titles the pack's own
  builders write. The word lists (`slot_address_word`, `slot_not_name_word`, the topic rules of a slot) can no
  longer make a text a fact on their own.
- `dossier/s7_audit.py`: the audit derives the same outcomes with its own code.
- `eval/score.py`: one count per kind of never-event of rule 1.5 (`<kind>_wrong_committed`, eight fields) and their
  sum `never_events_by_kind_total`, which equals `never_events`; no existing field changes name or meaning.
- Declared, not read, behaviour unchanged: the three forms of hand-18 that blocked undeclared (E-0020, E-0025,
  E-0026) - **blocks**; a capital stated in a clause of another shape (E-0012) - **keeps `[TO CONFIRM]`**.
- Tests: `tests/test_d37_forms.py` (11 tests; 438 address siblings), `tests/test_d37_slots.py` (8 tests; 300
  siblings of the company's name, titles and labels), `tests/test_d37_score.py` (2 tests); of the 738 siblings the
  code of `v2.0.6-freeze` publishes 429 wrongly, `v2.0.7-freeze` 423 and `v2.0.8` none (6 end FAILED and publish
  nothing, fail-closed, as on the two earlier codes); the fixtures of the tests and the scenarios gain registry
  extracts that state the office alike; inline tests of the ten new rules; `tests/test_rules.py` counts 100 rules
  (321 tests in all, one expected failure).

The change of `v2.0.8` was written by the builder's hand after reading the results and the hand-written documents
of run 18, and measured only on corpora already seen (run 19, not blind; numbers in `CHANGELOG.md` 2.0.8 sections 3
and 8): 0 never-events on all twenty-four results, hand-18 4 -> 0; published and blocked wrongly unchanged on every
result; the price is facts kept `[TO CONFIRM]` wherever one document alone states an address (facts exact 1294 ->
1082 of 1294 on seed 20261017, 655 -> 542 on its perturbed corpus, 39 -> 35 of 111 on hand-18). `CHANGELOG.md`
(entry 2.0.8) lists every known limit with what it does, in two classes only - **blocks** or **keeps
`[TO CONFIRM]`**; **none may publish**; what the proof still rests on (section 4 of that entry) is stated in the
same two classes, except the premise of corroboration, which is the definition of a fact in the pack and is kept
as a test expected to fail.

The change of `v2.0.7` (finding D36, from run 16) changed code, rules and tests - not the scorer. `OWN-015` and
`unverified_holders_table` keep `block` (D26); holders written in a sentence stay unread (D31); `DISC-005` keeps
`every_field`; `DISC-006`, `CLS-005` and `DISC-035` stay.

- `rules/extract.json`, `dossier/s1_extract.py`: a name beside an identifier closes its line only when it is that
  identifier's own known name (`CLS-005`, equality only); an identifier whose own name the corpus does not know (not
  in the identity layer, no `Entity:` header of its own) leaves the line open. An address (`slot_address`) needs its
  house number; every word of its street and town must have the form of an Italian place name
  (`slot_address_word`), name nobody the corpus knows and be no word of `slot_not_name_word`, which gains the
  English endings `-ing` and `-s`, common irregular past forms, nouns in `-ee`, and Italian words of role and
  holding. `EXT-OFFICE-010`, `-020` and `-030` read only such an address (`value_slot` `w_office`); a value that
  fails is not read. A value equal to its identifier's or its entity's own known name is a name whatever its words.
- `rules/extract.json`, `dossier/s1_extract.py`: a list ends at a blank line or at a line that is a list heading or a
  full sentence (`list_end_sentence`: a capital first, three words or more, its own `.`, `!` or `?`, no identifier,
  share, fraction or figure followed by a unit noun); that line is classified on its own. A possessive followed by
  the adjective "own" is not a word of holding (`neutral_phrases`, `HEV-040`); a currency followed by a figure with
  `#` is an amount that cannot be read, not a bare figure (`HEV-080`). The fields check names lines that stand
  inside another field's list as such. The first inline test of `CLS-190` says what the line may change
  (`expect_may_change_unless_read`): the S09 wording stays unread by design.
- `dossier/s7_audit.py`: the audit re-derives the equality, the end of a list and the form of an address with its
  own code.
- Tests: `tests/test_d36_forms.py` (14 tests; 600 sibling cases of five classes, of which the code of
  `v2.0.6-freeze` leaves 312 unsafe and `v2.0.7` none; the masked probes of hand-16 unmasked; and the residual risk
  of `CHANGELOG.md` 2.0.7 section 4 as a test expected to fail), inline tests of `CLS-005`, `CLS-190`, `HEV-040`,
  `HEV-999`; `tests/test_pipeline_cli.py` writes the identity layer of its input (300 tests in all, one expected
  failure; 230 inline rule tests).

The change of `v2.0.7` was written by the builder's hand after reading the results and the hand-written documents
of run 16, and measured only on corpora already seen (run 17, not blind; numbers in `CHANGELOG.md` 2.0.7 section
8): 0 never-events on all twenty-one results. `CHANGELOG.md` (entry 2.0.7) lists every known limit with what it
does; **none may publish**; what the proof still rests on is stated as a residual risk, `[TO CONFIRM]`, and kept as
a test expected to fail.

The change of `v2.0.6` (finding D35, from run 14) changed code, rules, tests and the scorer - not only
documentation. `OWN-015` and `unverified_holders_table` keep `block` (D26); holders written in a sentence stay
unread (D31); `DISC-005` keeps `every_field`; `DISC-006` stays.

- `rules/extract.json`, `dossier/s1_extract.py`: a slot that holds a name (parameter `slot_name_groups`) carrying
  a word that cannot be part of a name (parameter `slot_not_name_word`: role, holding, time and function words,
  Italian forms, English suffix classes) does not close its line; new rule `CLS-005` - a name beside an
  identifier that is not that identifier's own name (the identity layer for a person, the `Entity:` header for a
  company) makes the line one no rule explains; the slot of the entity's own name (parameter
  `slot_own_name_groups`) closes its line only when it equals the name of the document's own `Entity:` header,
  legal form aside. Such a line falls to `CLS-999`: the document may change every field (`DISC-006`), or the
  entity blocks when the line may state a holding.
- `rules/discrepancy.json`, `dossier/s3_discrepancy.py`: new rule `DISC-035` (parameter `legal_form_in_name`) - a
  company name whose legal form at its end differs from the legal form stated is a discrepancy: the legal form is
  `[TO CONFIRM]`, the readings listed with their sources, nothing reconciled.
- `rules/extract.json`: `CLS-110`/`EXT-FORM-010` and `CLS-150`/`EXT-FORM-020` read a legal form followed by its
  sentence's own full stop (`S.r.l..`, `S.p.A..`); the holders' heading takes a qualifier of the class
  "registered" after a comma (`(4) Shareholdings, entered in the register:`).
- `dossier/s1_extract.py` `fields_check`: under `every_field` the record of a document of unrecognised type says
  every field (`*`) and names `DISC-005`; the judgement of its lines is kept as a note only.
- `dossier/s7_audit.py`: the audit re-derives the own-name equality, the label check and the legal-form clash
  with its own code.
- `eval/score.py`: each result object carries `pipeline_status` (`OK`, `BLOCKED`, `FAILED`) next to `exit_code`,
  which is unchanged (rule 1.5).
- Tests: `tests/test_d35_forms.py` (11 tests; 192 sibling cases of nine classes, of which the code of
  `v2.0.5-freeze` publishes 147 wrongly and `v2.0.6` none; a variant of hand-14 E-0011 and E-0012 in the exact
  form, 3 never-events on `v2.0.5`, 0 on `v2.0.6`), inline tests of `CLS-005`, `CLS-110`, `CLS-150`, `CLS-999`,
  `EXT-FORM-010`, `EXT-FORM-020`, `EXT-HOLD-010`, `DISC-020`, `DISC-035`, `DISC-040`; `tests/test_rules.py` counts
  90 rules (286 tests in all).

The change of `v2.0.6` was written by the builder's hand after reading the results and the hand-written documents
of run 14, and measured only on corpora already seen (run 15, not blind; numbers in `CHANGELOG.md` 2.0.6 section
8). `CHANGELOG.md` (entry 2.0.6) lists every known limit with what it does; **none may publish**; what the proof
still rests on is stated as a residual risk, `[TO CONFIRM]`, not as "no case is known".

The change of `v2.0.5` (decision D34, before any blind run of `v2.0.4-freeze`) changed code, rules and tests -
not only documentation; the scorer is unchanged. `OWN-015` and `unverified_holders_table` keep the value `block`
(D26); holders written in a sentence stay unread (D31).

- `rules/extract.json`: new ordered group `classified_lines` (`CLS-010` to `CLS-250`, default `CLS-999`), run on
  every non-empty body line of a document of a recognised type: a line with no letter or digit, a line of a list
  that a rule of its kind reads (the heading, a row whose label passes the test of an unread document and whose
  share is typed, the last `Total`), the whole line of a clause of its kind with typed slots (amounts, counts,
  addresses, names, legal forms; the free words of a slot through the topic rules of `unread_fields` and
  `holders_evidence`), a label with a typed value, a title of the nouns of `FEV-920` (parameter `title_nouns`,
  now shared) or the closing sentence; anything else (`CLS-999`) means that the document may change every
  field.
- `dossier/s1_extract.py`: a line decided by `CLS-999` makes the document one that may change every field; a
  closed line that states a field its kind does not read, or that no rule of its kind read from it, makes it one
  that may change that field. The record, the view and `schema/entity_record.schema.json` carry
  `classified_checks`; the dossier lists them among its warnings.
- `rules/discrepancy.json`, `dossier/s3_discrepancy.py`: new rule `DISC-006` - a field stays `[TO CONFIRM]` when
  a document of a recognised type that may change it is not older than the latest event of the field (the
  criterion of `DISC-005`); no exception for a table that agrees.
- `dossier/s4_ownership.py`, `rules/ownership.json`: a holders' table in a document of a kind not read for the
  holders is read whole and summed, or the holders cannot be summed and `OWN-015` blocks; two such tables block;
  a line read by no rule that may state a holding blocks.
- `dossier/s7_audit.py`: `classified_scope`, a second implementation that re-reads every source of a recognised
  type and refuses a record that omits an open line, a field stated where no rule read it, or a holding.
- Tests: `tests/test_d34_forms.py` (5 tests; 379 sibling cases of five classes, of which the code of
  `v2.0.4-freeze` publishes 348 wrongly and fails on 15, and `v2.0.5` none), 66 inline tests of
  `classified_lines` and 3 of `DISC-006`, changes in `tests/test_rules.py` and `tests/test_d30b_forms.py`
  (275 tests in all).

The change of `v2.0.5` was written by the builder's hand and measured only on corpora already seen (run 13, not
blind): 0 never-events on all fifteen results, the same entities blocked, the plain and hand corpora unchanged.
Its price is coverage on the reworded corpora (facts exact 711 -> 681 of 1285 on the stress suite, 330 -> 290
of 925 on the out-of-pool corpus of run 5), accepted. `CHANGELOG.md` (entry 2.0.5) lists every known limit with
what it does; **none may publish**.

The change of `v2.0.4` (finding D30b, from run 11), kept in `v2.0.5`, changed code, rules, tests and the
scorer - not only documentation. `OWN-015` and `unverified_holders_table` keep the value `block` (D26).

- `rules/discrepancy.json`: `unread_document_scope` is back to `every_field`, the behaviour of `v2.0.0` to
  `v2.0.2`: a document of unrecognised type that is not older than the latest event of a field keeps every
  field `[TO CONFIRM]`, whatever its title or its lines say (`[TO CONFIRM with legal]`). The value
  `fields_it_may_state`, the default of `v2.0.3`, stays allowed and off: ten adversarial siblings of hand-11
  E-0009, E-0010 and E-0015, each under every title noun of `FEV-920`, under a title of its own and with no
  title (160 cases), show that it can publish a field the document changes. The rules of `unread_fields` are
  still there and decide nothing under the default. `dossier/rules_engine.py` `with_params()` lets an inline
  test of a rule run with another allowed value of a parameter.
- `rules/extract.json`, `dossier/s1_extract.py`: a holders' or directors' heading without a final `.` or `:`
  is read only when it is the whole line and the next line is an item of the list; two headings of the same
  list in one document abstain (holders block, directors stay `[TO CONFIRM]`); the directors' heading takes
  the clause numbers of the holders' heading; a day ordinal with a month (`the third of July`) and `third
  parties` are not shares; dot leaders are a separator; a last line `Total` is read in the unit of the rows
  and carried as `stated_total`; the share may come before the holder (per cent and `n/d`).
- `dossier/s4_ownership.py`, `rules/ownership.json` `OWN-010`: a table is whole only when its rows sum to the
  whole and its Total, when there is one, equals that sum; a Total that differs blocks the entity.
- `dossier/s7_audit.py`: the audit reads dot leaders, the share first and the Total with its own code, and
  refuses a Total that is not the exact sum of the rows.
- `eval/score.py`: four new counts for the entities that are not published - the gold `[TO CONFIRM]` values
  and the gold file-name divergences, of every entity not published and of those blocked wrongly. They are
  printed and written next to the never-events and are not never-events; no other count changes.
- `schema/entity_record.schema.json`: optional `stated_total` on a holders' table.
- Tests: `tests/test_d30b_forms.py` (26 tests), changes in `tests/test_d30_forms.py`,
  `tests/test_holders_forms.py`, `tests/test_never_event.py` and `tests/support.py` (270 tests in all).

The change of `v2.0.4` was written by the builder's hand after reading the results and the hand-written
documents of run 11, and measured only on corpora already seen (run 12, not blind). Its price is coverage:
on the reworded corpora more fields stay `[TO CONFIRM]` (for example 477 -> 726 of 1461 on the perturbed
corpus of seed 20261014) and more published dossiers carry the holders `[TO CONFIRM]` (3 -> 54 there).
`CHANGELOG.md` (entry 2.0.4) lists every known limit with what it does; one of them could publish and was not
fixed in `v2.0.4`: `v2.0.5` closes it.

The change of `v2.0.3` (owner decision D30 of 2026-10-01), kept in `v2.0.4` and `v2.0.5` except where the lists
above say otherwise:

- `rules/extract.json`: the holders' heading grammar also takes "of record", "registered" or "entered in the
  register", a qualifier meaning "current" in parentheses or after a comma, "(synthetic)", clause numbers
  such as `iv.`, `(4)`, `Article 4`, `§ 4`, and the nouns quotaholdings, shareholding(s) and shareholding
  structure. One item grammar for holders and directors (parameters `list_marker`, `item_holder`,
  `item_person`, `item_separator`): markers `-` `*` `1.` `1)` `(1)` `a)` `(a)` `iv)`, the identifier first or
  after the name (`Name (P-001)`), separators `:`, ` - `, `|`, tab. Counts of quotas or shares are read only
  when the same document states exactly one total (parameter `count_total`). New ordered group
  `unread_fields` (`FEV-010` to `FEV-930`, default `FEV-999`): which fields a document of unrecognised type
  may state; a line no rule explains may state every field.
- `dossier/lib/numbers.py`: shares in `per cent`/`percent`/`pct`, whole per cent in words, simple fractions
  in words; a count is never a share.
- `dossier/s3_discrepancy.py`: `DISC-005` keeps `[TO CONFIRM]` only the fields an unread document may state
  (new parameter `unread_document_scope` of `rules/discrepancy.json`, value `fields_it_may_state`,
  `[TO CONFIRM with legal]`; `every_field` is the behaviour of `v2.0.2`) - **reverted by `v2.0.4`**, whose
  default is `every_field` again. A document whose header has another problem may change every field. A
  holders' table read whole that agrees with the current holders releases the holders field.
- `dossier/s7_audit.py`: the audit re-derives from the source lines, by its own code, the shares of counted
  tables and the fields an unread document may state.
- `eval/score.py`: the `never_event_list` of each result is no longer capped at 50 (the count never was).
- `schema/entity_record.schema.json`: optional `fields_check` on a problem document.
- Tests: `tests/test_d30_forms.py` (31 tests), changes in `tests/test_numbers.py`, `tests/test_never_event.py`,
  `tests/test_holders_forms.py`, `tests/test_rules.py` (243 tests in all).

The change of `v2.0.3` was written by the builder's hand after reading the results and the hand-written
documents of run 9, and measured only on corpora already seen (run 10, not blind).

This protocol now applies to `v2.0.10-freeze`; besides the names of the tag, it changes section 0 (the seed
20261019 and the hand-written documents of run 22 are known, the seeds through 20261019 scored again in run 23,
the texts of the tests of `v2.0.10` are known), section 1 (exit 3 of the scorer: a measurement that failed),
section 4 (the classes `v2.0.10` claims, the complete list of its known limits in two classes - blocks or keeps
`[TO CONFIRM]`, none may publish -, at least three COUNT-FORM probes, entities written outside the gazetteer, the
hand-written part built and scored in a deep work folder of about 280 characters and in a short one, the deep one
first) and sections 5 and 6. The section-5 rule on the redaction of internal folder names (D33) is carried over
word for word. The earlier tags are not moved and their blind runs are not repeated; `v2.0.4-freeze` was never run
blind.

Until `v2.0.9-freeze` this paragraph read: "This protocol now applies to `v2.0.9-freeze`; ... section 4 (the
classes `v2.0.9` claims, the gazetteer vocabulary a probe must be written in so as not to be masked, the complete
list of its known limits in two classes - blocks or keeps `[TO CONFIRM]`, none may publish -, what the proof still
rests on, at least seven unmasked probes of typed slots and at least four PREMISE probes, an own name holding a
street or place word, a deep work folder) and sections 5 and 6."

Until `v2.0.8-freeze` this paragraph read: "This protocol now applies to `v2.0.8-freeze`; ... section 4 (the
classes `v2.0.8` claims, the complete list of its known limits in two classes - blocks or keeps `[TO CONFIRM]`,
none may publish -, what the proof still rests on, adversarial documents of unrecognised and of recognised type, at
least seven unmasked probes of typed slots - a name, an amount, a count and four addresses -, a masked/not-masked
statement for each probe, the sum of the `*_wrong_committed` fields, the runs listed by start time) and sections 5
and 6."

Until `v2.0.7-freeze` this paragraph read: "This protocol now applies to `v2.0.7-freeze`; ... section 4 (the
classes `v2.0.7` claims, the complete list of its known limits - none may publish -, the residual risk,
adversarial documents of unrecognised and of recognised type, at least five unmasked probes of typed slots whose
other lines are in forms the pack reads, a masked/not-masked statement for each probe, the runs listed by start
time) and sections 5 and 6."

Until `v2.0.6-freeze` this paragraph read: "This protocol now applies to `v2.0.6-freeze`; ... section 4 (at least
twelve entities and thirty-two documents, the classes `v2.0.6` claims, the complete list of its known limits -
none may publish -, the residual risk, at least four unmasked probes of typed slots) and sections 5 (the shape of
the record) and 6."

## 0. What is frozen

| | |
|---|---|
| Tag | `v2.0.10-freeze` (annotated), created at 2026-10-01T17:44:33Z |
| Tag object | `dbff8e839afe41e0fc295e5614a39db07f373ead` |
| Commit | `6d466e28e1dd4f7ffa8257af54da95b10a9bd96a` |
| Frozen files | the 193 files listed in `MANIFEST.sha256` (code, rules, schema, corpus generator, scenarios, tests, tools, scorer, requirements) |
| Not frozen | `README.md`, `CLAIMS.md`, `CHANGELOG.md`, `MODEL.md`, `SYNTHETIC.md`, `eval/history.json`, `eval/blind/`, this file |
| Previous tag | `v2.0.9-freeze`, tag object `7d7d951612ce4606f501fd96ab89daceea707765`, commit `50a365e455d613bbdb580f891b9a29fdaea88650`: run blind once (run 22), 0 never-events, every probe unmasked, 10 of 42 hand-written entities blocked wrongly, each a declared limit or rule; four defects that do not publish (D1 a measurement in a deep folder that read nothing and exited 0, D2 the count form of the capital clause not read, D3 a sentence of its `CHANGELOG.md` not true as written, D4 a holder row with the identifier in brackets blocking undeclared) |
| Tag before it | `v2.0.8-freeze`, tag object `e6525e26fe84c7f57fc297cf57154563d9de5649`, commit `695b1b66820f34dd7cf700b2e95ef7f486e0c0e8`: run blind once (run 20), not passed - 8 never-events on hand-written entities E-0009 and E-0010 (the premise of corroboration its `CHANGELOG.md` section 4 declared `[TO CONFIRM]`), 6 of 34 hand-written entities blocked wrongly, one of them (E-0030) on a form it neither read nor named |
| Earlier tag | `v2.0.7-freeze`, tag object `06ff379e511f6ed22cb584aaee981dd3cd0d8b0e`, commit `452b46d5e2686aa0fca7d7aa50dec32e2ec3aa38`: run blind once (run 18), not passed - 4 never-events on hand-written entity E-0015 (the residual risk its `CHANGELOG.md` section 4 declared `[TO CONFIRM]`), 10 of 27 hand-written entities blocked wrongly, three of them on forms it neither read nor declared |
| Earlier tag | `v2.0.6-freeze`, tag object `c7fa9d7a0380a6b81f51efd6c6df562f829c769c`, commit `6acebba59e0fb59972e5dab75e0908de77ed67f1`: run blind once (run 16), 0 never-events, 15 of 28 hand-written entities blocked wrongly, two probes masked (unmasked by the builder: E-0014 a FAILED run on that code, E-0017 blocked); its declared residual risk measured afterwards at 312 of 600 constructed siblings unsafe; hand-18 measured on its code after run 18 by the coordinator: 4 never-events on E-0015 (not blind) |
| Earlier tag | `v2.0.5-freeze`, tag object `12453f2ac263d1cba7f88364b2be1a8f9186d344`, commit `267ea87f4fa147bc66fd2af64c499ac2bf019876`: run blind once (run 14), 0 never-events, 5 of 15 hand-written entities blocked wrongly, two probes masked (unmasked by the builder: 3 never-events on that code) |
| Earlier tag | `v2.0.4-freeze`, tag object `66f116539d7421b95d124b94a32d4e8bbc92ba9e`, commit `65b02335fb718ed061d3c9e665e26db97accc9ef`: not run blind; its one known limit that may publish is closed by `v2.0.5` |
| Earlier tag | `v2.0.3-freeze`, tag object `ae66f49debcb1bb15e83e1827acda35b03c4a3a6`, commit `77e7736f573c93024f0aa49157f5949287bee698`: run blind once (run 11), not passed - 2 never-events on hand-written entity E-0015, 8 of 15 hand-written entities blocked wrongly |
| Earlier tag | `v2.0.2-freeze`, tag object `475bd994bbd063c4dc7cebb15f50e7b9474ebd58`, commit `023c7cb5629b17295b4ddbbfeb22055a2be16b87`: run blind once (run 9), 0 never-events, 4 of 9 hand-written entities blocked wrongly |
| Earlier tag | `v2.0.1-freeze`, tag object `91cba79b5671a9f273a7ecf268dc92ffa8679a23`, commit `b65e45a5289133375222fa595abdbd9cd2087be7`: run blind once (run 7), 0 never-events, 89 of 150 perturbed entities blocked wrongly |
| First tag | `v2.0.0-freeze`, tag object `0c26555916701c4a81ea6490c32d5e7162edcdc8`, commit `d1769d555934ca5eaf4717bafe8135105caffd43`: run blind once (run 5), not passed |

Seeds already used, which therefore cannot be the blind seed: 20260930 (development, inspected),
20261001 (holdout, scored thirteen times - runs 2, 3, 4, 6, 8, 10, 12, 13, 15, 17, 19, 21 and 23 -, never inspected; until
`v2.0.7` this line said "eight times", which run 15 had already made wrong), 20261002 (stress, inspected),
20261011 (the blind seed of `v2.0.0-freeze`: its plain, perturbed and out-of-pool corpora were read by the hand
that wrote the fix and scored again in runs 6, 8, 10, 12, 13, 15, 17, 19, 21 and 23), 20261012 (the blind seed of
`v2.0.1-freeze`: its plain and perturbed corpora were generated, read and scored again by the hand that wrote
`v2.0.2`, runs 8, 10, 12, 13, 15, 17, 19, 21 and 23), 20261013 (the blind seed of `v2.0.2-freeze`: its plain and perturbed
corpora were generated, read and scored again by the hand that wrote `v2.0.3`, runs 10, 12, 13, 15, 17, 19, 21 and 23),
20261014 (the blind seed of `v2.0.3-freeze`: its plain and perturbed corpora were generated again from the
recorded seed, read and scored by the hand that wrote `v2.0.4` and `v2.0.5`, runs 12, 13, 15, 17, 19, 21 and 23), 20261015
(the blind seed of `v2.0.5-freeze`: its plain and perturbed corpora were generated again from the recorded seed
and scored by the hand that wrote `v2.0.6`, runs 15, 17, 19, 21 and 23), 20261016 (the blind seed of `v2.0.6-freeze`: its
plain and perturbed corpora were generated again from the recorded seed, read and scored by the hand that wrote
`v2.0.7`, runs 17, 19, 21 and 23), 20261017 (the blind seed of `v2.0.7-freeze`: its plain and perturbed corpora were
generated again from the recorded seed and scored by the hand that wrote `v2.0.8`, which read the rule each record
of them names, runs 19, 21 and 23), 20261018 (the blind seed of `v2.0.8-freeze`: its plain and perturbed corpora were
generated again from the recorded seed and scored by the hand that wrote `v2.0.9`, runs 21 and 23), 20261019 (the
blind seed of `v2.0.9-freeze`: its plain and perturbed corpora were generated again from the recorded seed and
scored by the hand that wrote `v2.0.10`, run 23). For the same reason these wordings are known to `v2.0.10` and are
no longer out of pool - a new run needs other wordings:

- the out-of-pool rewrite of run 5 and the ten hand-written documents of run 7 (`eval/blind/hand/`);
- the 24 hand-written documents of run 9 (`eval/blind/hand-9/`): the headings `Quotaholders at present.`,
  `Partners as at the document date:`, `Stockholders following the transfer:`, `Shareholders now.`,
  `Partners.`, `Holders (as at the document date):`, `Shareholders of record:`, `Shareholding structure at
  the document date (synthetic):`, `4. Holders.`, `Quotaholders:`; holder lines numbered `1) P-002 (...) - 20%`
  and name first `Elmo Ipotetici (P-010): 200 quotas` with the total `divided into 300 quotas`; shares
  `thirty per cent`, `60 %` in a pipe table with a header row; holders in a sentence, with nominal amounts
  (`held as follows: ... for a nominal EUR 36'000.00`) or with shares (`held by ... as to 30%`); the document
  types `Ledger of quotaholders`, `Statement of shareholdings`, `Certificate of good standing`; a second
  amount inside a capital clause; amounts grouped by an apostrophe, a space and a dot;
- the 33 hand-written documents of run 11 (`eval/blind/hand-11/`, 15 entities): the headings `Article 4.
  Stockholders`, `4. Shareholders`, `4. Holders`, `§ 4 Holders` (no final `.` or `:`), `4. Holders.`,
  `4. Quotaholders.`, `iv. Quotaholdings`, `(4) Current members:`, `Registered stockholders:`, `Registered
  shareholders:`, `Holders:`, `Shareholders once the transfer has taken effect:`, `Directors in office after
  this appointment:`, `(5) Directors:`, `§ 5 Directors`, `Article 5. Directors`, `v. Directors`; holder lines
  `(a) P-001 (...) | 55 percent`, name first `* Name (P-003): three fifths`, `a) P-004 (...) - one half`, a tab
  separator `1. P-006 (...)<TAB>630 quotas` with the total `split into 900 quotas`, dot leaders
  `- P-014 (...) .......... 50%` with a last line `Total .... 100%`, the share first `- 60% P-002 (...)`, a
  pipe table with the header row `| Identifier | Holder | Share |`, per mille `625‰`; fractions in words
  (`three fifths`, `four fifths`, `one fifth`, `one half`); a day ordinal (`on the third of July`); the
  document types `Circular`, `Note for the file`, `Notice to creditors`, `Memorandum`, `Internal memo` and
  `Letter to the bank`; a notice to creditors that raises the equity by a contribution in kind and moves the
  seat in one sentence; the title line `Minutes of the holders' meeting (synthetic).`;
- the adversarial siblings of hand-11 E-0009, E-0010 and E-0015 and every other text of the tests
  (`tests/test_d30b_forms.py` and the earlier test files);
- the 379 sibling cases of `tests/test_d34_forms.py`, written for `v2.0.5`: a capital resolution whose new
  quotas go to a new holder (`the new quotas being subscribed by`, `taken up in full by`, `put in the whole of
  the increase and joins the company`, `Welcome to ...`), a transfer notice that also moves the seat (`the seat
  moves to`, `has its seat at`, `receives its post and holds its meetings at`, a bare address), an appointment
  that also states a capital change (`also resolved to increase the share capital`, `with the share capital now`,
  `A further EUR ... was paid in by the members`, `put in a further EUR ... each, for good`), an office transfer
  that also names a new director (`is appointed director`, a `Directors:` list, `takes over the running of the
  company`, a bare person line), a resolution that holds a holders' table (read whole, under a heading of its
  own, not summing, two tables, rows without a heading), each with no title line, with the generator's title
  line and with every title noun of `FEV-920`; and the inline tests of `classified_lines` and `DISC-006` in
  `rules/extract.json` and `rules/discrepancy.json` (for example `It is split into 900 quotas.`, `The company is
  domiciled at ...`, `Share capital: resolved 80 000,00 euro; subscribed and paid in 80 000,00 euro`);
- the 40 hand-written documents of run 14 (`eval/blind/hand-14/`, 15 entities): the clause `its legal form is
  S.r.l..`; the label `Legal form: S.r.l.` beside `Name: ... S.p.A.`; a director line whose name carries
  `Sole Proprietress Henceforth`; the headings `(4) Shareholdings, entered in the register:`, `(4) Quotaholders:`,
  `§ 4 Quotaholders:`, `§ 4 Members`, `iv. Shareholders:`, `iv. Partners:`, `Holders:`, `(5) Directors:`,
  `§ 5 Directors`, `v. Directors:`, `5. Directors.`, `Directors in office after this appointment:`; holder
  lines `i) Name (P-001): 35 pct`, a row `- P-007 and P-008 (...): 30% each`, a pipe table with the header row
  `| Holder | Identifier | Share |`, a hyphenated per cent in words; the extract line `Share capital: resolved
  EUR ...; subscribed and paid in EUR ...`; the document types `Minutes`, `Memorandum`, `Letter` and `Notice`;
  the sentences "so that the two now stand on an equal footing", "becomes its third member", "the two members
  brought the company's own means from fifteen thousand euro up to sixty thousand euro"; and the type label
  `Extract from the test registry` of the perturbed corpus of seed 20261015;
- the 192 sibling cases of `tests/test_d35_forms.py`, written for `v2.0.6`: person slots with the trailing
  words `Sole Proprietress Henceforth`, `Sole Owner`, `Managing Director`, `Henceforth`, `Solely`, `Partnership`,
  `Who Holds It All`, `Socio Unico`, `Ora Titolare`, `Padrona`, `Vecchie Zeta` in director lines and holder rows
  of deeds, extracts, appointments, transfers and ledgers; company names ending in `S.p.A.`, `SpA`, `s.p.a.`,
  `S.r.l.s.` beside `S.r.l.`; address slots with `Henceforth`, `Solely`, a holding after the town or the address;
  amount slots with `by the sole member`, `henceforth all by P-003`, `by P-002 alone`, `wholly taken up by`; the
  headings `4. Shareholdings, entered in the register:`, `4. Members, as recorded in the book of members:`,
  `4. Shareholdings, transferred on 1 May:`; and the inline tests of `CLS-005`, `DISC-035` and the other rules
  changed in `v2.0.6`;
- the 59 hand-written documents of run 16 (`eval/blind/hand-16/`, 28 entities): the document types `Bank
  mandate`, `Merger plan`, `Auditor's annotation`, `Correspondence`; the headings `(4) Stockholders of record.`,
  `§ 4 Shareholding structure, of record:`, `§ 5 Directors:`, `4. Members (current):`, `4. Quotaholders of
  record.`, `Article 4. Quotaholders (current):`, `Article 5. Directors:`, `4. Allocation of the quotas:`,
  `Holders after the transfer:`; holder lines `(a) P-001 (...) - 55 per cent`, name first `1) Name (P-...): 3/4`,
  `* P-001 (...) | 60%`, the share first `1. 7/10 - P-001 (...)`, dot leaders `a) Name (P-...) ........ 40 pct`
  with a last line `Total ........ 100 pct`, a tab separator `1) P-001 (...)<TAB>450 quotas`, an amount
  `- P-001 (...): EUR 7.000,00 of the capital`, decimal shares `62,5%`, shares in words `twelve and a half per
  cent`, `eighty-seven and a half per cent`, a fraction on a line of its own (`one third`, `two thirds`); the
  sentences "the company's own means stand at twice the figure of the deed", "the doubling of the company's own
  endowment", "The seat of the company is moved from ... to ...", "The capital is divided into 1.000 quotas.",
  "The company has issued 900 quotas in all.", "The company's letters are received at ..., where the board also
  meets.", "having sold out, no longer acts for the company", "the company answers only to", "will have been
  absorbed", "the company is to be found at", "stands beside the two founders with half of everything", "ceded
  everything he had in the company to", "holds three quarters of the quotas and ... the remaining quarter"; the
  words written after a typed slot in its probes (`Our Company Resides There`, `Lia Presunti Funding Everything
  Added`, `Buying Pio Contraffatti Out`, `Doubling Our Means Five Hundred Thousand Euro Total`, `Teo Congetturi
  Replacing Ugo Finzione`, `Twenty Euro Apiece`); and the illegible amount `EUR 1#.###,00` of the perturbed corpus
  of seed 20261016;
- the 600 sibling cases of `tests/test_d36_forms.py`, written for `v2.0.7`: the words `Carlo Inventati
  Presiding`, `Ugo Nessuno Presiding`, `Chairing Changes`, `Carlo Inventati Buys`, `Ugo Nessuno Buys`, `Means
  Doubling`, `Ugo Nessuno Leader`, `Ugo Nessuno Subentra` after, inside or in place of an address, an amount, a
  count, a name beside an identifier nobody knows and another company's name in a label; the readers' cases
  (`Via Carlo Inventati 1`, `Via Nuova Leader 1`, `Via Nuova, Montefinto Buys (ZZ)`, `Teo Nessuno Replacing Ugo
  Nessuno`); the list ends (`The holders sign this deed in person.`, `Nothing else is certified.`, `The price was
  paid in full.`, `Bice Provetti also joins the board.`, `Aldo Finti holds 300 quotas.`, `Bice Provetti keeps her
  40%.`, `The quotas are 1000 in total.`); the residual cases `Via Ugo Nessuno Governa 1, Montefinto (ZZ)` and
  `Montefinto Ugo Nessuno Presiede (ZZ)`; and the inline tests of `CLS-005`, `CLS-190`, `HEV-040` and `HEV-999`;
- the 67 hand-written documents of run 18 (`eval/blind/hand-18/`, 27 entities, and its `GOLD_OUTCOMES.md`): the
  document types `Succession record`, `Chamber communication`, `Pledge release`, `Court order` and their titles
  `Record of a succession (synthetic).`, `Entry of the test chamber (synthetic).`, `Declaration of the lender
  (synthetic).`, `Minutes of the test tribunal (synthetic).`; the headings `Art. 4 Members:`, `Art. 5 Directors:`,
  `Quotaholders, registered:`, `Partners:`, `4. Members of the company.`, `IV. Members:`, `V. Directors:`, `Those who
  hold the quotas are:`, `Quota holders:`, `Quotaholders of the company:`, `Fourth. Holders:`, `Fifth. Directors:`;
  holder lines `1) P-001 (...) - 45 pct`, `(a) Name (P-001) - 1/2`, `*` with dot leaders and `per cent` and a last
  line `Total ...... 100 per cent`, `- P-001 (...): the rest`, a name with no identifier `- Name: 3/4`, a comma
  separator `- P-002 (...), 70%`, `40 %`, `(1) P-010 (...) - 1.500 quotas` with the total `made up of 2.000
  quotas`, the share first with a bar `a) 1/2 | P-012 (...)`, `sixty per cent`, `12,5%`; the sentences "stands in
  his place for all purposes in the company", "all dealings with the company take place at", "each founder paid in
  again what he had paid at the formation", "removed from every function ... alone may bind it", "answered for the
  entire new sum and from this day sits with the founders in every meeting", "speaks for the company alone; ...
  withdraws", "is from today the only place where the company can be served", "paid in, for the second time, the
  sum of the deed of incorporation", "The founders bring in EUR ..., all of it paid on signing."; and the words of
  its probes (`Moving The Seat To Largo degli Esempi 1 Pontefinto` after a name, `Via Rina Fittizia Regge Da Sola
  3`, `Lagoapocrifo Dote Raddoppiata Oggi`, `Put Up By Zeno Fasullo Who Now Steers The Company` after an amount,
  `Zeno Fasullo Taking The Chair` after a count, `Now Seated At Piazza della Finzione 1 Serraillusoria` after a
  legal form);
- the 738 sibling cases of `tests/test_d37_forms.py` and `tests/test_d37_slots.py`, written for `v2.0.8`: the
  words `Capitale Raddoppiato`, `Soci Cambiati`, `Quote Cedute`, `Ugo Presiede`, `Sede Trasferita` and `Carlo
  Inventati` after, before or between the words of a town, before the house number, inside or before a street,
  inside the parentheses of a province (`Via Nuova 1, Montefinto (ZZ)`, `Via Nuova 1, San Fittizio (ZZ)`), before
  the legal form, inside or before a company's name in a header, a name slot and a label, and in a title, a label
  and a heading, each with a second source without them, with one source only and (addresses) as a genuine
  difference; the forms of `D37_DeclaredForms` (`4. Members of the company.`, `a) 60% | P-001 (...)` under
  `Quotaholders of the company:`, `Fourth. Holders:`, `The founders bring in EUR 50.000,00, all of it paid on
  signing.`); the registry extracts that repeat an office (`tests/support.py` `office_witness`, the ten of
  `scenarios/make_inputs.py` `repeat`); and the inline tests of `ADR-*`, `NAM-*`, `TXT-*` and `DISC-038`;
- the 87 hand-written documents of run 20 (`eval/blind/hand-20/`, 34 entities, and its `GOLD_OUTCOMES.md`): the
  document types `Tax return excerpt`, `Notarial attestation`, `Lease addendum`, `Deposit slip` and the titles
  `Statement of the test bank (synthetic).`, `Report of the premises (synthetic).`, `Declaration of the test notary
  (synthetic).`, `Certificate of the test office (synthetic).`; the headings `Article 4 - Quotaholders of record:`,
  `Article 4. Shareholders:`, `4) Shareholders.`, `Shareholders, entered in the register:`, `(4) Quotaholders:`,
  `iv. Shareholders:`; holder lines `(i) P-009 (...) - 60 percent`, name first `1. Name (P-003): 7/10`, `- P-005
  (Name) (3/4)`, `1. P-007 (...): 60 per cent`, rows framed by vertical bars with no header row `| P-003 (...) | 55%
  |`; shares in words `three fifths`, `two fifths`, `seventy per cent`; the places of its names and addresses
  (`Valbugia`, `Sassoinvento`, `Rocca Chimera`, `Pian delle Ombre`, `Lago Fasullo`, `Colle Apocrifo`, `Borgo
  Illusorio`, `Serra Favolosa`, `Castel Mendace`, `Pieve Supposta`, `Case Finte`, `Vado Posticcio`, `Torre
  Simulata`, `Monte Spurio`; `Via dei Manichini`, `Via del Simulacro`, `Via Olga Simulata`); the words of its probes
  (`Fondo Triplicato`, `Dotazione Novantamila`, `Pacchetto Venduto Intero`, `Regia Nuova Tullio`, `Timone Mutato`, the
  label `Means Of The Company Since June`, the particle in `Via Del Simulacro`), a count with words after it
  (`divided into 1.000 quotas Timone Mutato`), a person of the identity layer inside a street name, and a registry
  extract filed with the documents of another entity;
- the 624 sibling cases of `tests/test_d38_identification.py`, written for `v2.0.9`: the words `Dotazione
  Novantamila`, `Capitale Raddoppiato`, `Capital Ninety Thousand`, `Capital Doubled`, `Quote Sessanta`, `Soci
  Cambiati`, `Holder Sixty`, `Shares Sold`, `Consiglieri Tre`, `Ugo Presiede`, `Two Directors`, `Board Changed`, `Sede
  Numero Due`, `Sede Trasferita`, `Seat Number Two` and `Seat Moved` after or before the town, before the house
  number or inside the street, inside the parentheses of the province, before, inside or after a company's name and
  its legal form, before the closing mark of a title and after or before the words of a label, each stated alike in
  two or three documents or once beside a second document without them; the fixtures of `D38_Hand20Classes`,
  `D38_PlainStillPublishes`, `D38_OwnNameStreetWord` (`Conceria Borgo Lontano`, `Sartoria Corso Fittizio`, `Vivaio
  Largo Inventato`), `D38_AuditAgrees` (`Cooperativa Agricola`, `Borgo Lontano`, `Gian Maria`) and `D38_DeclaredLimits`
  (`Via Del Collaudo`, rows framed by bars, a misfiled extract); `tests/test_d38_long_paths.py`; and the inline tests
  of `IDN-*`, `NAM-005`, `TXT-005` and `TXT-020`;
- the 100 hand-written documents of run 22 (`eval/blind/hand-22/`, 42 entities): the document types `Escrow
  instruction`, `Rent roll`, `Insurance schedule`, `Bank reference`, and a financial statements summary and a share
  transfer notice that change a field they are not about; the headings `(4) Holders of record:`, `Article 4.
  Holders:`, `§ 4 Shareholders:`, `iv. Quotaholders of record.`, `Stockholders as of today:`, `Holders after the
  increase:`; holder lines `- Name [P-015]: 60%`, `1. P-003 (...) - 55 pct`, `(a) Name (P-005): 70 percent`, `- 7/10
  P-012 (...)`, a tab separator before `seventy per cent`, a last line `Total: 100%`, a blank line between two rows;
  the count form `EUR 20.000,00, divided into 2.000 quotas, fully subscribed and fully paid in` and the amount in
  words `one hundred and twenty thousand euro`; the places and names written outside the gazetteer (`Pievetorta`,
  `Segherie`, `Via delle Larve`, `Orsola Parvenze`, `Benedetto Sembianze`) and the address `Via del Segnaposto 5`;
  the words of its probes (`Roccaesempio Fondi Aumentati`, `Pontecollaudo Valcollaudo`, `Via del Collaudo Immaginari
  7`, `Corso dei Modelli Guida Nuova 4`, `Lagosintetico Patrimonio Centoventimila`, `Viale degli Esempi Comando
  Ceduto 6`, `Fonderie Rivaprova Nora Ipotetici S.r.l.`, `Cartiere Poggioesempio Tre Teste Nuove S.r.l.`, the title
  `Minutes of the holders' meeting, the chair passing to Sergio Finti (synthetic).`, `Borgoprova Dino Fasulli`, `Mara
  Campioni Ormai Unica Proprietaria`, `Sottoscritti Per Intero Da Zita Ipotetici Che Entra Da Sola`, `divided into
  3.000 quotas Riunite In Mano A Nino Fantasmi`), and the own names `Officine Casalprova` and `Cantieri Largo
  Simulato`;
- the 78 sibling cases of `tests/test_d39_capital_count.py`, written for `v2.0.10`: the count form in four cases
  (`divided into 2.000 quotas` with the holders' rows as counts and as per cent, `split into 2.000 shares`, `divided
  into 2.000 equal quotas`), the plain form, and the twenty forms that must not close (an Italian clause, subscribed only, paid
  in only, `partly`, `for one quarter`, `to be paid in`, `of which EUR ... paid in`, `subscribed for EUR ...`, the
  words split across two sentences or two lines, a qualification after it, a negation, `of which` before it, a
  nominal amount per quota, `consisting of`, an exception after it, a contradiction after a semicolon), each alone,
  with a later extract that states the full values and with one that states another paid-in amount; the fixtures of
  `tests/test_d39_limits.py` (the bracket rows in three orders, a blank line inside a list, `Via Gino Segnaposto 5`)
  and of `tests/test_d39_scorer.py`; and the inline tests of `NAT-020`, `NAT-025`, `NAT-070` and `NAT-999`;
- every example of `CHANGELOG.md` (sections 2.0.2 to 2.0.10) and of this protocol.

## 1. Rules of the run

1. The runner is not the author and chooses `<SEED>`: any integer other than the seeds of section 0, not
   told to the author before the run.
2. Each command of sections 3 and 4 is run **once**. There is no second attempt, whatever the result.
3. No frozen file is changed before or during the run. Section 2 proves it.
4. The outcome is recorded verbatim in `eval/history.json` (section 5), good or bad, with the name of who ran it.
5. The only pass or fail criterion, declared here before any blind run: **`never_events` is 0** in every
   result (the scorer exits with code 0; it exits with code 1 when there is at least one never-event; since
   `v2.0.10` it exits with code 3 when it could not measure - `MEASUREMENT FAILED`, the reason on stderr and in the
   `measurement` of the result -, and such a result is neither passed nor failed: it is recorded as a FAILED
   measurement, with its reason, and its command is not repeated). The
   field `exit_code` of a result object is **not** the scorer's exit: it is the pipeline's own exit code
   (`dossier/run.py`: 0 `OK`, 2 `BLOCKED` - at least one entity blocked, which is expected -, 3 `FAILED`);
   since `v2.0.6` the field `pipeline_status` next to it names that status. `exit_code` is kept, unchanged,
   for the tools that read it.
   Since `v2.0.2` (decision D29) a never-event is any one of the following - the list `eval/score.py`
   counts, word for word as in its docstring and in `README.md`:
   - a field shown as one fact whose value differs from the gold;
   - a planted conflict shown as one value, or shown with values that are not the gold's;
   - a field the gold says cannot be read, shown with a value;
   - a field shown with a value that is not in the gold;
   - an entity whose cap table does not sum to the whole that is not blocked, or whose dossier is published;
   - a published cap table that does not sum to the whole;
   - an effective holding shown where the gold abstains, or different from the gold;
   - a figure without source document, source date or edition.
   Until `v2.0.1` this section gave a narrower definition ("a figure rendered as fact that differs from the
   gold or has no source", including a planted conflict shown with one value only and a cap table rendered
   with a sum other than 100%); every never-event of that definition is in the list. The scorer counts the
   whole list since commit `110dc2c`; its first version (commit `8326c21`) did not yet check a published
   cap table that does not sum.
6. Everything else is reported, not judged: conflicts found (recall) and conflicts reported that are real
   (precision), exact facts, and the abstention rate next to them. Next to the never-events of every result
   the runner also reports the entities **blocked wrongly** - built by the gold and blocked by the run
   (`blocked_wrongly` in the counts of each JSON file) - because `OWN-015` blocks, by decision, every
   holders' table it does not read. Since `v2.0.3` the runner also reports, next to them, the fields left
   **`[TO CONFIRM]`** (`fields_abstained` in the metrics of each JSON file) and, when it can count them, the
   published dossiers whose holders are `[TO CONFIRM]`. Since `v2.0.4` the scorer also counts what a block
   hides, and the runner reports it next to the never-events as well: the gold `[TO CONFIRM]` values and the
   gold file-name divergences of the entities not published, and of those blocked wrongly
   (`blocked_entities_gold_to_confirm`, `blocked_wrongly_entities_gold_to_confirm`,
   `blocked_entities_filename_divergences_gold`, `blocked_wrongly_entities_filename_divergences_gold` in the
   metrics of each JSON file). They are not never-events. Every time in the record is UTC **with seconds**,
   written `YYYY-MM-DDTHH:MM:SSZ` (for example `2026-10-01T02:45:16Z`), never in local time and never without
   the seconds.
   More abstention, more wrong blocks and lower recall than on the development suite are expected, above
   all in sections 3b and 4: the rules read some wordings and write `[TO CONFIRM]` for what they do not
   read. That is reported as it comes out.
7. If a never-event appears: it is recorded, the affected claims are downgraded in `CLAIMS.md`, and the
   fix goes into a new version under a new tag. The freeze tag is never moved and the run is never repeated
   on the fixed code under the name "blind".

## 2. Before the run: prove that the frozen files are the tagged ones

    git rev-parse "v2.0.10-freeze^{commit}"
    git diff --stat v2.0.10-freeze -- corpus dossier rules schema scenarios tests tools eval/__init__.py eval/score.py requirements.txt MANIFEST.sha256 docs
    python tools/manifest.py --check

Expected: the commit above; no output from `git diff`; `manifest OK`. Python 3.12 with the packages of
`requirements.txt` (`python -m pip install --require-hashes -r requirements.txt`); nothing else is installed
and nothing uses the network after that.

## 3. Generated blind corpus (parameterised by `--seed`)

150 invented entities are generated from `<SEED>`, with their gold written from the generated world, built
and scored. Reference date of the corpus: 2026-09-30 (the default of the generator).

a. Plain wording:

    python -m eval.score --seed <SEED> --label blind --json build/blind/blind-<SEED>.json

b. Same seed, perturbed wording (clauses reworded, numbers in other forms, paragraphs reordered):

    python -m eval.score --seed <SEED> --perturb --label blind-perturbed --json build/blind/blind-<SEED>-perturbed.json

Each command prints one line such as
`blind seed=<SEED> as_of=2026-09-30 never_events=... conflicts recall=... precision=... fields exact=... abstained=... blocked=... figures_with_source=...`
followed by one `NEVER-EVENT:` line per never-event (first ten; since `v2.0.3` the JSON file lists every one), and,
since `v2.0.10`, by one `MEASUREMENT FAILED - <label>: ...` line on stderr per problem when it could not measure.
Note the exit code of each command, the counts `published` and `blocked_wrongly`, the metric
`fields_abstained` and the four metrics of the entities not published of each JSON file (rule 1.6), and the
UTC time each command starts and ends, as `YYYY-MM-DDTHH:MM:SSZ`.

What 3a can and cannot show: it uses the same generator and the same templates as the development suite,
so a clean result is expected and says little. 3b and section 4 are the informative parts.

## 4. Hand-written documents (the part the generator cannot influence)

The runner writes **at least twenty source documents of at least six new invented entities** by hand, and
writes the gold by hand **before** running anything, from what the documents are meant to say - never from an
output.

Input folder:

    <DIR>/input/config.json                      {"as_of": "YYYY-MM-DD", "shareable_salt": "any-text", "synthetic": true}
    <DIR>/input/identity/persons.json            {"P-001": {"name": "...", "born": "YYYY-MM-DD", "email": "...@persons.example", "tax_code": "SYN-CF-P001"}, ...}
    <DIR>/input/entities/E-0001/<date>_<slug>.txt
    <DIR>/input/entities/E-0002/<date>_<slug>.txt
    ... (one folder per entity, E-0001 to E-000N)
    <DIR>/gold.json

Every document is UTF-8 with LF line endings and starts with these lines (the first one is mandatory and
literal; a document without it is rejected and the entity fails):

    SYNTHETIC TEST DOCUMENT - fictitious entity, invented test registry, not an official record.
    Document id: DOC-E0001-01
    Document type: Deed of incorporation
    Document date: 2025-03-10
    Edition: DEED/1
    Entity: <invented name> (test registry no. TEST-REG-000001)

The document types, the wordings the rules read and the form of amounts and shares are the ones of the
24 source documents under `scenarios/S01..S10/input/entities/`; the file names follow the same pattern
(`2025-03-10_deed.txt`, `2026-02-02_registry-extract.txt`). The runner is free - and encouraged - to
word things otherwise: what the rules do not read must come out as `[TO CONFIRM]`, never as a guess.

For `v2.0.10-freeze` the runner writes **at least twelve entities and at least thirty-two documents**, with
the **holders' tables** in **forms of its own choosing** - the heading, the holder lines, the form of the
shares and the type of the document that carries the table - not copied from the scenarios, from the
hand-written documents of runs 7, 9, 11, 14, 16, 18, 20 and 22 (`eval/blind/hand/`, `eval/blind/hand-9/`,
`eval/blind/hand-11/`, `eval/blind/hand-14/`, `eval/blind/hand-16/`, `eval/blind/hand-18/`, `eval/blind/hand-20/`,
`eval/blind/hand-22/`), from the texts of the tests (`tests/test_d39_capital_count.py`, `tests/test_d39_limits.py`,
`tests/test_d39_scorer.py`, `tests/test_d38_identification.py`, `tests/test_d38_long_paths.py`,
`tests/test_d37_forms.py`, `tests/test_d37_slots.py`, `tests/test_d37_score.py`, `tests/test_d36_forms.py`,
`tests/test_d35_forms.py`, `tests/test_d34_forms.py` and the earlier test files, the inline tests of `rules/`) or
from the examples of this protocol and of `CHANGELOG.md`: `v2.0.10` was written after seeing those, and only forms
it has not seen measure it. Some of the forms should fall **inside** the classes `v2.0.10` claims to read, worded in
ways it has not seen, and some **outside** them. Write every deed and every registry extract in a form the pack
claims to read (section 0 lists what it has seen), so that a probe is not masked by an unrelated abstention. Since
`v2.0.8` that includes corroboration: the deed and the registry extract of an entity state its registered office
and its name in the header `Entity:` **alike, token for token** (an address or a header name that one document
alone states keeps fields `[TO CONFIRM]` on its own, `ADR-999`, `NAM-999`), and a title line is either absent or
one of the two titles the pack's own builders write (`Minutes of the holders' meeting (synthetic).`, `Notice of a
transfer of shares (synthetic).`) - any other title that no second document of the input states alike makes its
document one that may change every field on its own (`TXT-999`).

**Since `v2.0.9` it also includes the gazetteer**: every free-text slot of a line meant to be read is written only
with entries of the gazetteer of the pack (`rules/extract.json` `gazetteer_*`, listed in `SYNTHETIC.md`, section
"The gazetteer"), each entry whole, with its case and its particles (`del Collaudo`, not `Del Collaudo`), and with no
numeral: the address of the office (a street type, a street name, a house number, a town, the province `(ZZ)`, as in
`Via del Collaudo 7, Borgoprova (ZZ)`), the company's name in every header `Entity:` and in every name clause (a
trade word and a town, or `Holding <town> Partecipazioni`, then the legal form, as in `Officine Montefinto S.r.l.`),
and every person's name, in the identity layer and beside an identifier (a first name and a surname of the
gazetteer, as in `Aldo Finti`). A name or a place outside the gazetteer is not identified (`IDN-999`): its line keeps
every field of its document `[TO CONFIRM]`, and blocks the entity when it may state a holding - every holders' row
whose person is outside the gazetteer blocks. A probe written in an entity with such a name or place is masked. The
added words of a probe are the only words of its entity outside that vocabulary, or are entries of it placed where
the pattern does not take them (below).

Claimed: a holders' heading with a holder noun, an optional clause number (`4.`, `iv.`, `(4)`, `Article 4`,
`§ 4`) and an optional qualifier meaning "current" or "of record" in the words of the rules, ending in `.` or
`:` - or without them when the heading is the whole line and the next line is an item of the list; holder
lines in a list, the identifier first or after the name, with a marker and a separator of the item grammar
(`:`, ` - `, `|`, tab, dot leaders), or the share before the holder (per cent or `n/d`); shares as figures
with `%`, `per cent`, `percent` or `pct`, as fractions `n/d`, as whole per cent in words or simple fractions
in words; a last line `Total` that equals the exact sum of the rows (a Total that differs blocks by
`OWN-010`); counts of quotas or shares with exactly one total stated in the same document; directors in the
same list grammar, under a heading with the same clause numbers; a document of unrecognised type that is not
older than the latest event of a field keeps **every** field `[TO CONFIRM]` (`DISC-005`, `every_field`).
Since `v2.0.5`, every non-empty body line of a document of a **recognised** type (the types of
`rules/extract.json` `doc_kinds`: deed of incorporation, test registry extract, resolution on share capital,
share transfer notice, appointment of directors, transfer of registered office, holders' ledger, financial
statements summary) is decided: a line that no rule of its kind explains keeps **every** field
`[TO CONFIRM]` when the document is not older than the latest event of the field (`DISC-006`), and blocks
when it may state a holding (`OWN-015`); a line that states a field its kind does not read, or that no rule of
its kind read from it, keeps that field `[TO CONFIRM]`; a holders' table in a document of a kind not read for
the holders is read whole and summed and the holders stay `[TO CONFIRM]`, or the entity is blocked.
Since `v2.0.6`: a legal form followed by its sentence's own full stop (`S.r.l..`) is read; a holders' heading
takes a qualifier of the class "registered" after a comma; a name slot that holds a word of
`slot_not_name_word`, a name beside an identifier that is not its own, or the entity's own name slot that is not
the name of its `Entity:` header leaves the line open (`CLS-999`); a company name whose legal form differs from
the legal form stated keeps the legal form `[TO CONFIRM]` (`DISC-035`).
Since `v2.0.7`: a name beside an identifier closes its line only when it equals that identifier's own known name
(the identity layer, the `Entity:` headers of the corpus); an identifier whose own name the corpus does not know
leaves its line open. An address closes its line and is read only with a house number and with every word of its
street and town in the form of an Italian place name (`slot_address_word`), naming nobody the corpus knows and
holding no word of `slot_not_name_word`; the readers of the office (`EXT-OFFICE-010`, `-020`, `-030`) read only
such an address. A list ends at a blank line, at a list heading or at a full sentence (`list_end_sentence`), and
that line is classified on its own; "own" after a possessive is not a word of holding; a currency followed by a
figure with `#` is an illegible amount, not a bare figure.
Since `v2.0.8`: an address (the office, and the previous office of a transfer) that passes that form test is read
as a fact only when it is also corroborated - stated alike, token for token, by two different documents of the
entity, or stated by the sentence `EXT-OFFICE-010` reads and repeated alike by a source dated after it (`ADR-020`).
An address equal to another of the entity plus words, in the street or in the town, is a line no rule explains
(`ADR-010`, `CLS-999`); an address that one document alone states leaves every field that document may change
`[TO CONFIRM]`, the office `[TO CONFIRM]` when no current source of it is corroborated (`ADR-999`, `DISC-038`);
two whole different addresses are a DISCREPANCY side by side (`DISC-020`). The company's name of the header
`Entity:` follows the same rule (`NAM-010`, `NAM-020`, `NAM-999`), and so do the title of `CLS-900` and the label of
`CLS-250` (`TXT-010`, `TXT-020`, `TXT-999`: stated alike by another document of the input, or one of the pack's own
two titles). The scorer writes one count per kind of never-event of rule 1.5 (`<kind>_wrong_committed`, eight
fields in the metrics of each result) and their sum `never_events_by_kind_total`.
Since `v2.0.9`: before corroboration, every free-text slot is identified word by word by the gazetteer (`IDN-020`
address, `IDN-030` company, `IDN-040` person, `IDN-050` title); a slot with a word the gazetteer does not hold
(`IDN-999`) or with a numeral (`IDN-010`: digits, an Italian or English number word, a Roman numeral) is a line no
rule explains, whatever the documents agree on; a header name that is not identified is unexplained (`NAM-005`); a
title closes its line only when it is one of the pack's two titles (`TXT-005`), and a label stated alike by other
documents no longer closes (`TXT-020`). A person's name is known only when the gazetteer identifies it and it equals
the identifier's own name of the identity layer (a choice `[TO CONFIRM]`). The topic words are no longer applied to
any free-text slot.
Since `v2.0.10`: the count form of the capital clause, in one sentence of one line and without qualification - the
amount, then `, divided (or split) into N [ordinary | registered | equal] quotas (or shares), fully subscribed and
fully paid in`, nothing after it but the full stop, the amount the only current amount of the clause - states the
resolved, the subscribed and the paid-in capital, as the plain form does (`NAT-025`); any other wording leaves the
subscribed and the paid-in capital `[TO CONFIRM]` (below).

Known limits of `v2.0.10`, the complete list of `CHANGELOG.md` (entry 2.0.10), each marked with what it does to
the entity, in two classes only - **blocks** or **keeps `[TO CONFIRM]`**. **No known limit may publish**
(`v2.0.4`: one; `v2.0.5` to `v2.0.10`: none - but `v2.0.7` left a residual risk outside its list, which run 18
found, and `v2.0.8` a premise outside its two classes, which run 20 found; run 22 found no limit of `v2.0.9` that
publishes). What the proof still rests on, below the list, is stated in the same two classes, with nothing outside
them. The list is copied from `CHANGELOG.md` entry 2.0.10, the part after it from entry 2.0.9: a section named in
them is a section of that entry.

Since `v2.0.10` (D39):

- the count form of the capital clause in any wording but `NAT-025`'s - "It is fully subscribed and fully paid in."
  as a second sentence, the words across two lines, a nominal amount per quota (`quotas of EUR 10,00 each`),
  another count verb (`consisting of`), `wholly`, `entirely`, `paid up`, a qualification after it, a part
  introduced by `of which` -: the subscribed and the paid-in capital **keep `[TO CONFIRM]`**; when the line is one
  no capital line rule explains and the document states holders - **blocks** (`DISC-006`, `OWN-015`);
- E-0006 of hand-22, by class: a holder row with the identifier in square brackets (`- Name [P-015]: 60%`,
  `- P-015 [Name]: 60%`, `- [P-015] Name: 60%`) - **blocks** (`OWN-015`);
- E-0005 of hand-22, by class: a blank line inside a list of holders ends the list; the rows after it are not read
  and the table does not sum to the whole - **blocks**;

Since `v2.0.9` (D38), unchanged unless said:

- a free-text slot that the gazetteer does not identify word by word (`IDN-999`): a town, a street, a province, a
  trade word, a first name or a surname that it does not hold, words added anywhere, a particle written otherwise
  (`Via Del ...`), a name written surname first, a street named after a person, a Roman numeral, a real town of two
  words - the line is read by no rule: every field the document may change **keeps `[TO CONFIRM]`** (`DISC-006`), no
  value of the slot is read; when the line may state a holding - **blocks** (`OWN-015`);
- a free-text slot that holds a numeral (`IDN-010`): digits, an Italian or English number word, a Roman numeral -
  the line may state a quantity - **blocks** when it may state a holding (a holders' table or the capital in the
  same document), else every field **keeps `[TO CONFIRM]`**. The block is by design, not a leftover (D39: E-0025
  and E-0028 of hand-22);
- a company's name of a header that is not identified (`NAM-005`), even when every document states it alike: every
  field of that document **keeps `[TO CONFIRM]`**, no name of it is read; when the name may state a holding -
  **blocks**;
- a holders' row whose person is not identified by the gazetteer, or is not its identifier's own name of the
  identity layer: the row is read by no rule - **blocks** (`OWN-015`); a directors' row - **keeps `[TO CONFIRM]`**.
  The choice of section 4 item 7 of entry 2.0.9, `[TO CONFIRM]`;
- a title that is not one of the titles the pack's own builders write, and every label of `CLS-250` (no label is a
  recognised text), even when other documents state it alike (`TXT-020`, `TXT-999`): its line is read by no rule -
  every field **keeps `[TO CONFIRM]`**; when it may state a holding - **blocks**;
- E-0030 of hand-20, by class: holders' rows framed by vertical bars without a header row - **blocks**;
- E-0062 of hand-20, by class: a document filed under one entity whose content names an entity with no folder of
  its own: it is built for that entity, and the entity of its folder reads it as an unclassified document - every
  field **keeps `[TO CONFIRM]`** from its date; its holders not read whole - **blocks**;
- the name beside an identifier in a row of a list that is not the identifier's own known name, with or without a
  word of the topic lists: the row is open - holders **block**, directors **keep `[TO CONFIRM]`**.

Since `v2.0.8` (D37), unchanged unless said:

- an address that no second document of the entity states alike, token for token (`ADR-999`): the fields that
  document may change (every field but the office), when it is not older than the latest event of a field, **keep
  `[TO CONFIRM]`** (`DISC-006`); the office **keeps `[TO CONFIRM]`** when no current source of it is corroborated
  (`DISC-038`); when the line may state a holding - **blocks** (`OWN-015`). A genuine difference of two whole
  identified addresses is shown side by side as a DISCREPANCY (`DISC-020`), the other fields **keep
  `[TO CONFIRM]`**. Since v2.0.9 an address is also read only when it is identified;
- an address equal to another of the entity plus words (`ADR-010`): every field **keeps `[TO CONFIRM]`**, no address
  of that line is read; when the line may state a holding - **blocks**;
- a company's name in the header `Entity:` equal to another header of the entity plus words (`NAM-010`): every
  field **keeps `[TO CONFIRM]`**, no name of that document is read; when the name may state a holding -
  **blocks**. A header name that one document alone states (`NAM-999`): every other field of that document, when
  it is not older than the latest event, and the name (`DISC-038`) **keep `[TO CONFIRM]`**;
- a company's name, stated by one document only, that holds a person's name of the identity layer: such a name is
  not identified (`NAM-005`) and every field **keeps `[TO CONFIRM]`**; when the run of the entity ends FAILED by
  the leak check of the shareable layer (A6), nothing of it is published - **blocks** (fail-closed);
- a title or a label equal to another plus words (`TXT-010`) - every field **keeps `[TO CONFIRM]`**; when it may
  state a holding - **blocks**. A short sentence of one to eight words ending in a full stop right after a holders'
  list (no blank line) - **blocks**;
- E-0020 of hand-18, by class: holder rows that name the holder by a person's name alone, with no identifier, and a
  holders' heading of another noun (`Members of the company`) - **blocks**;
- E-0025 of hand-18, by class: a lettered item with the share before the holder, separated by a vertical bar -
  **blocks**;
- E-0026 of hand-18, by class: an ordinal word before the holders' heading (`Fourth. Holders:`) - **blocks**;
- E-0012 of hand-18, by class: the capital stated in a clause of a shape the pack does not have (`The founders
  bring in ...`) - every field the document may change, the capital among them, **keeps `[TO CONFIRM]`**.

From `v2.0.7` and earlier, unchanged unless said:

- holders stated in a sentence rather than in a list under a heading, including a holder noun in a sentence of
  a memorandum, a resolution or an appointment (hand-9 E-0003, E-0007; hand-14 E-0005, E-0007, E-0009): not
  read, by the owner's risk decision D31 - **blocks**;
- a row naming several holders with "each" (hand-14 E-0003) - **blocks**;
- a qualifier meaning "current" in free words in the heading (hand-11 E-0002), and a participle of another class
  than "registered" after a comma in the heading - **blocks**;
- a table with a header row (hand-11 E-0011, hand-9 E-0003, hand-14 E-0014) - **blocks**;
- per mille (`625‰`, hand-11 E-0014) - **blocks**;
- nominal amounts per holder, with no share and no count - **blocks**;
- a holders' heading with an explicit date (`Holders at 16 February 2026:`) and headings of other nouns
  ("Allocation of the capital", "Capital allocation", "ownership structure", owners, beneficial owners, members) -
  **blocks**;
- a heading without a final `.` or `:` that is not the whole line or is not followed by an item line: not a
  heading - holders **block**, directors **keep `[TO CONFIRM]`**;
- two holders' headings in one document - **blocks**; two directors' headings - **keeps `[TO CONFIRM]`**;
- a Total line that is not the last line of the table, that cannot be read, or that is in another unit than
  the rows - **blocks** (a Total that differs from the exact sum blocks by `OWN-010`, by design);
- a share before the holder written in words or as a count - **blocks**;
- a share in words in the same line as a date in words - **blocks**;
- counts without a total in the same document, with two totals, mixed with shares in one table, or in a
  document of unrecognised type - **blocks**;
- shares in words beyond whole per cent and simple fractions - **blocks**;
- a label with nested or second parentheses - **blocks**;
- a document whose header cannot be read, a document date in words among them (`OWN-015`) - **blocks**;
- shares planted as illegible block by design (D26) - **blocks**;
- a document of unrecognised type (a type label the rules do not list) not older than the latest event of a
  field: every field (`DISC-005`, `every_field`) - **keeps `[TO CONFIRM]`**; when it holds a line that may state
  a holding (`holders_evidence`), or a holders' table that is not read whole - **blocks** (`OWN-015`);
- a document of a recognised type with a body line that no rule of its kind explains (`CLS-999`; since v2.0.8
  also a line whose address, name, title or label is not corroborated, since v2.0.9 one whose free-text slot is
  not identified): every field, when the document is not older than the latest event (`DISC-006`) - **keeps
  `[TO CONFIRM]`**; when the line may state a holding - **blocks** (`OWN-015`);
- a closed line that states a field of its kind where no rule of its kind read it (the office-transfer wording
  "The seat of the company is moved", scenario S09, among them), or a field its kind does not read: that field,
  when the document is not older than the latest event - **keeps `[TO CONFIRM]`**;
- a holders' table in a document of a kind not read for the holders: read whole and summed, then the holders
  **keep `[TO CONFIRM]`**; not read, or two of them - **blocks**;
- a row of a list of a recognised document whose share is illegible or not typed - every field **keeps
  `[TO CONFIRM]`**, and when the row may state a holding - **blocks**;
- a line right after a list with no blank line that is neither a heading nor a full sentence of the form
  `list_end_sentence` - a sentence that names an identifier, a share or a figure with a unit noun (hand-16 E-0010),
  a wrapped row: a row of the list the grammar cannot read - holders **block**, directors **keep `[TO CONFIRM]`**;
- a name slot that is not its identifier's or its entity's own known name, a name beside an identifier that is not
  its own (`CLS-005`), or the entity's own name slot that differs from its `Entity:` header: the line is one no rule
  explains - every field **keeps `[TO CONFIRM]`** (`DISC-006`), and when the line may state a holding - **blocks**.
  Since v2.0.9 a name is known only when the gazetteer identifies it;
- a name beside an identifier whose own name the corpus does not know (not in the identity layer, no `Entity:`
  header of its own; every person when the identity layer names nobody): the line is open - every field **keeps
  `[TO CONFIRM]`**, and the holders **block** (`OWN-015`);
- an address without a house number, or with a known name inside it that is not part of a whole gazetteer entry
  (restated in v2.0.10, D3: a word of a whole gazetteer street entry is part of the street even when it is also a
  known surname, and that address is read when it is identified and corroborated): the line is open and the office
  is not read from it - every field **keeps `[TO CONFIRM]`** (`DISC-006`), and when the line may state a holding -
  **blocks**;
- a company name whose legal form differs from the legal form stated (`S.r.l.s.` against `S.r.l.` included, by
  design) - the name is a discrepancy and the legal form **keeps `[TO CONFIRM]`** (`DISC-035`).

What the proof still rests on, for `v2.0.10` as for `v2.0.9` (`CHANGELOG.md` 2.0.9, section 4, which rewrites section
4 of entry 2.0.8; entry 2.0.10 leaves it unchanged). Entry 2.0.8 closed the free-text slots by corroboration and declared its premise - two documents that state
the same text alike state it - outside its two classes; run 20 showed that the premise publishes.

Census of the free-text slots (`identification_slot_classes` and the groups of `classified_lines`):

- **Decided by identification, then by corroboration and equality** (since `v2.0.9`): the address of the office and
  of the previous office (`w_office`, `w_previous`: `IDN-*`, then `address_corroboration`); the company's name of
  the header `Entity:` and of the slots of the entity's own name (`w_name`: `IDN-*`, equal to its header since
  `v2.0.6`, then `name_corroboration`); a person's name beside an identifier (`w_person`, `w_person_first`: `IDN-*`,
  and equal to that identifier's own known name, `CLS-005`); the title of `CLS-900` and the label of `CLS-250`
  (`w_title`, `w_label`: a recognised text, `TXT-005`). An unidentified slot opens its line: every field **keeps
  `[TO CONFIRM]`**; with a numeral, or when the line may state a holding, the entity **blocks**.
- **Decided by equality**: the document type (`doc_kinds`, `KIND-010` to `KIND-080`); the fixed words of each shape
  of `classified_lines` (the pack's own wording, matched whole).
- **Decided by grammar**: amounts (currency and figure) and counts (figure and unit noun) - any other word opens the
  line; the house number of an address; a share (per cent, fraction, words of a whole per cent or a simple
  fraction).

What still rests on a list or on form, each with its class:

1. **The gazetteer** (identification): a word that is an entry of the gazetteer, in its place in the pattern, is
   taken to be the place, street, trade or name the list says. The patterns admit exactly one entry per place, so
   no free word can stand beside the entries. A slot made only of entries that differs between two documents is a
   genuine difference, shown side by side (`DISC-020`), or a name that differs (`NAM-999`, `DISC-038`: **keeps
   `[TO CONFIRM]`**). Whether an entry is the right one - two documents that both name the wrong town of the
   gazetteer - is a question of the inputs, not of reading: the pack does not claim to see it. Anything not in the
   gazetteer: **keeps `[TO CONFIRM]`**, or **blocks** with a holding or a numeral.
2. **The numeral list** (`numeral_token`): a number word that it misses is a word that the gazetteer does not hold
   either (the gazetteer holds no number word), so the slot is unidentified all the same (`IDN-999`): **keeps
   `[TO CONFIRM]`**, or **blocks** when the line may state a holding. The numeral list decides only between those
   two classes.
3. `holders_evidence` (`HEV-*`) and `unread_fields` (`FEV-*`), the words that say whether an open line, an open
   name or an unread document may state a holding: under `every_field` they decide only between **blocks**
   (`OWN-015`) and **keeps `[TO CONFIRM]`** (`DISC-005`, `DISC-006`); no word of these lists lets a field be
   published. Since `v2.0.9` they are no longer applied to any slot of `identification_slot_classes` to decide whether
   it closes (D38 (b), section 5).
4. `list_end_sentence` and the item grammar (form): where a list ends. A line that is not a full sentence or a
   heading is a row of the list; a row that cannot be read leaves the list unread - holders **block**, directors
   **keep `[TO CONFIRM]`**. A line that ends the list is classified on its own; if no rule of its kind explains it,
   every field **keeps `[TO CONFIRM]`** and, when it may state a holding, the entity **blocks**.
5. The shapes of `classified_lines` (form): a line that no shape matches is `CLS-999` - every field **keeps
   `[TO CONFIRM]`**, or **blocks** with a holding. A shape matches only its fixed words around typed slots, and
   every free-text slot is identified word by word, so no free word of a closed line is left undecided.
6. The date criterion of `DISC-005`/`DISC-006`: a document older than the latest event of a field cannot change
   it. It decides between the field read from the newer event and **keeps `[TO CONFIRM]`**; it publishes nothing
   that the newer event does not state.
7. **Persons identified by the gazetteer, a choice `[TO CONFIRM]`**: a person's name beside an identifier closes its
   line only when the gazetteer identifies it and it equals the identifier's own name of the identity layer. The
   other choice - a name of the identity layer is its own proof - rests again on a premise of agreement (the hand
   writes the identity layer and the documents), so it was not taken. Its class: a holders' row whose person the
   gazetteer does not hold **blocks**; any other line **keeps `[TO CONFIRM]`**. Its price is section 3: every
   hand-written corpus blocks. Whether a person may be identified by the identity layer of the input is a decision
   of the owner and of counsel, not of the builder.

**The premise of corroboration of entry 2.0.8 is closed**: two documents that state the same words alike no longer
make them a fact (`ADR-020` and `NAM-020` apply only to identified slots, `TXT-020` reads nothing).
`tests/test_d36_forms.py` `D36_ResidualWordList` is no longer an expected failure; `tests/test_d37_forms.py`
`D37_EqualityPremise` and `tests/test_d37_slots.py` `D37_NameEqualityPremise` keep their names and now state the
opposite of `v2.0.8`. What the pack takes as written is a slot whose every word is of the gazetteer, stated alike by
two documents: the gazetteer itself (item 1, and `identification_source`, `[TO CONFIRM with legal]`).
The PREMISE probes asked below measure that.

Until `v2.0.10` the list above was the list of `v2.0.9` (`CHANGELOG.md` entry 2.0.9), whose items are restated
above where `v2.0.10` changes them. Two of them read otherwise: "an address without a house number, or with a name
the corpus knows inside it: the line is open and the office is not read from it" (run 22 found that a whole
gazetteer street entry holding a known surname is read, E-0033), and the item of `IDN-010` did not say that its
block is by design. The bracket row and the blank line inside a list (E-0006 and E-0005 of run 22) were in no item.

Until `v2.0.9` the list above was the list of `v2.0.8` (`CHANGELOG.md` entry 2.0.8), whose items are restated above
where `v2.0.9` changes them, and this section ended with the premise of `v2.0.8` (`CHANGELOG.md` 2.0.8, section 4):
"**The premise of corroboration**, `[TO CONFIRM]` - the definition of a fact in this pack, not a limit of reading:
two different documents that state the same text alike, token for token, are taken to state it. When two
documents of an entity carry the **same** added words in an address, two headers the same name with words, or two
documents of the input the same label, the text is read as it is written and a change those words were meant to
state is not seen." Run 20 found that case on hand-written entities E-0009 and E-0010.

Until `v2.0.8` the list above was the list of `v2.0.7` (`CHANGELOG.md` entry 2.0.7), whose items are restated
above where `v2.0.8` changes them, and this paragraph described the residual risk of `v2.0.7` (`CHANGELOG.md`
2.0.7, section 4): "What **still rests on a word list** (`slot_not_name_word`, and the names the corpus knows): a
street or a town whose words all have the form of an Italian place name, name nobody the corpus knows, and state
something with a word of no class of that list - an Italian verb or noun ending in a vowel (`Via Ugo Nessuno
Governa 1, Montefinto (ZZ)`). Such a line closes and every field of the entity is published, the directors
included." Run 18 found that case on hand-written entity E-0015.

Until `v2.0.7` this paragraph described the residual risk of `v2.0.6` (`CHANGELOG.md` 2.0.6, section 4): "What
still rests on the word list `slot_not_name_word` and on the lists of `unread_fields` and `holders_evidence`: the
words of an address slot (street and town), the name beside an identifier that the identity layer and the
`Entity:` headers of the corpus do not know, and the name of another company in a label line."

The runner is asked in particular for:

- **at least twelve entities and at least thirty-two documents** in all;
- **adversarial documents of BOTH unrecognised and recognised types that change a field they are not
  "about"**. Of unrecognised type: a document type the scenarios do not use. Of recognised type: one of the
  eight types above, whose kind is read for some fields only - a resolution on share capital that also
  changes the holders, the directors or the seat; a share transfer notice that also changes the capital or
  the directors; an appointment of directors that also moves the seat or changes the capital; a transfer of
  registered office that also changes the holders; a holders' ledger or a financial statements summary that
  also changes another field; a deed or a registry extract that states a field in words of its own. Use title
  lines with the pack's own list words - the title nouns of rule `FEV-920` in `rules/extract.json` (minutes,
  notice, entries, entry, register, ledger, statement, certificate, memorandum, summary, record, report,
  letter, declaration), marked `(synthetic)` - **and** sentences that change a field without naming it (the
  capital doubled without the word capital, a holder replaced without the words holder, share or quota, the
  seat moved without the word office, a director replaced without the word director). In the gold every
  field such a document may change is `TO_CONFIRM`. Since `v2.0.8` a title of the hand's own in a document of a
  **recognised** type (one that is not one of the pack's two titles and that no second document of the input
  states alike) is read by no rule (`TXT-999`) and keeps every field `[TO CONFIRM]` on its own: to measure the
  sentence of such a document, give it no title line or one of the two titles of the pack; a title of the hand's
  own measures `TXT-999` and nothing else, and belongs in a document of unrecognised type. Since `v2.0.9` the same
  holds for every title that is not one of the two, whatever the other documents of the input state (`TXT-005`,
  `TXT-020`);
- **at least seven probes of typed slots that carry extra words**, unmasked, each in its own entity, each in a
  line of a recognised document whose extra words state a change of **another** field (the capital, the holders,
  the directors) without naming it:
  - a **NAME** (a person or a company, beside an identifier);
  - an **AMOUNT**;
  - a **COUNT**;
  - **four ADDRESSES** of the registered office, whose added words each have the form of an Italian place name,
    name nobody the corpus knows and are of no class of `slot_not_name_word` (the class of run 18): (1) words in
    the **town**, with a **second source** - another document of the entity that states the same address
    without them; (2) words in the **town**, **single source** - the only document of the entity that states
    that address (for example the new address of an office transfer that no later source repeats, or the office
    of a deed that is the entity's only document); (3) words in the **street**, with a second source without
    them; (4) words in the **street**, single source. Since `v2.0.9`, in at least two of the four the added words
    are themselves entries of the gazetteer placed where its pattern does not take them (a second town after the
    town, a street name or a surname inside the street), so that every word is known and only their place is not.

  Every **other** line of the probe's entity is in a form the pack reads, and the runner checks it **line by
  line** before the run, then **unmasks** the probe after the run by reading the record of its entity line by
  line: its deed and registry extract as in section 0, the office and the header name stated alike in both
  (except the probed address of probes 2 and 4, which is the single source by design), no title of the hand's
  own, no document of unrecognised type, no other open line. Two forms by name, because run 16 masked a probe
  with each: an office transfer is read only in the sentence `EXT-OFFICE-010` reads, `The registered office is
  transferred from <address> to <address>.`, with addresses of the form `Via del Collaudo 7, Borgoprova (ZZ)`
  (street, house number, town, province; "The seat of the company is moved" is read by no rule and keeps the office
  `[TO CONFIRM]` on its own); and a count of quotas is read with its total only in the capital clause
  `count_total` reads, as in the deed's `The share capital is EUR 10.000,00, divided into 1.000 quotas, fully
  subscribed and fully paid in.` (a separate total line such as `The capital is divided into 1.000 quotas.` is a
  line no rule explains, and the entity blocks on it alone, `OWN-015`). In the gold every field the added words
  may change is `TO_CONFIRM`, and so is the office of the four address probes;
- **at least four PREMISE probes**, each in its own entity, unmasked: the **same** added words stated **alike**,
  token for token, by two or three documents of the input (the class of run 20) - (1) in the town of the office, in
  the deed and the registry extract; (2) in the street of the office, in both; (3) in the company's name of every
  header `Entity:` and of the own-name clause; (4) in a label or a title stated alike by two documents of the input.
  The words state a change of another field (the capital, the holders, the directors) without naming it; at least
  one of the four carries a numeral and at least one carries none and is made, where it can be, only of entries of
  the gazetteer. In the gold every field the words may change is `TO_CONFIRM`, and so is the slot that carries them;
- **at least one own name holding a street or place word**: an entity whose company's name holds a word of the
  office's topic (`Via`, `Viale`, `Piazza`, `Corso`, `Vicolo`, `Largo`, `Borgo`) or the town of its own office. The
  gazetteer of `v2.0.9` (unchanged in `v2.0.10`) holds no trade or town with a street word, so a name with such a word is not identified
  (`NAM-005`: every field `[TO CONFIRM]`, or blocks with a holding) - say so in its statement below; a name that
  holds the town of its own office (`Officine Borgoprova`, its office in `Borgoprova`) is identified, and the gold
  says whether it publishes;
- **at least three COUNT-FORM probes** of the capital clause, each in its own entity, unmasked, every other line of
  the entity in a form the pack reads (as for the typed slots): (1) the **claimed form**, worded the hand's own way
  inside what `NAT-025` reads (the amount, then `, divided into` or `, split into` a count of quotas or shares,
  ordinary, registered or equal or none, then `fully subscribed and fully paid in` and the full stop); (2) a
  **partial payment** in a count form (a part, a fraction or an amount of the capital paid in, or to be paid in);
  (3) a count form **contradicted by a second capital clause** - in the same document or in a later one - that
  states another subscribed or paid-in amount. In the gold the fields are what the documents state: the three
  values as facts for (1), and for (2) and (3) the field that is not stated whole, or that two clauses state
  differently, as `TO_CONFIRM` or as a conflict;
- **some entities written outside the gazetteer** (a town, a street, a trade or a person it does not hold), as run
  22 did: the gold says, by section 4 of the known limits, whether each keeps its fields `[TO CONFIRM]` or blocks;
- **the hand-written part built and scored twice, in a deep work folder and in a short one**: the command of
  section 4 is run first with `--work` in a folder whose full path is about **280 characters**, on Windows with
  long-path support off (registry value `LongPathsEnabled` 0), then on the same corpus with `--work` in a short
  folder. The deep run is reported as a run of kind `out-of-pool` and is listed **before** the short one, which is
  the `protocol` run of section 4. Report the length of the path, the setting, the exit code of each command and
  whether the two results are equal. An exit 3 (`MEASUREMENT FAILED`) is a failed measurement and is recorded as
  such, with its stderr; no command is repeated. Until `v2.0.10` this item asked for one command in a folder of
  about 230 characters; run 22 ran one of 282 and found that the scorer of `v2.0.9` read nothing there and exited 0
  (D1);
- for **each probe, a statement masked / not masked**: whether anything other than the probe's own line made its
  entity abstain or block, and by which rule and line (the fields check names them; since `v2.0.8` the record
  also names the rule of corroboration, `ADR-*`, `NAM-*` or `TXT-*`; since `v2.0.9` the rule of identification,
  `IDN-*`, `NAM-005` or `TXT-*`; since `v2.0.10` the nature of an amount, `NAT-*`), as runs 14, 16, 18, 20 and 22
  did; every probe of this list - typed slot, PREMISE, COUNT-FORM, own name - is unmasked line by line after the run,
  and a masked probe is reported as measuring nothing;
- holders' tables inside and outside the claimed classes, including tables in documents of a kind not read
  for the holders.

With the never-events of this part, report the entities blocked wrongly, the fields left `[TO CONFIRM]` and
the four counts of the entities not published (rule 1.6), the exit code of each command (0, 1 or, since `v2.0.10`,
3), and every time in UTC **with seconds**, as `YYYY-MM-DDTHH:MM:SSZ`. Since `v2.0.8`, report next to the never-events of **each** result the sum of **every**
`*_wrong_committed` field of its complete JSON file, taken with the evaluator's own tool that sums those fields
(not with a subset written by hand, and not from a printed summary): the scorer writes eight such fields, their
sum must equal `never_events` and `never_events_by_kind_total`, and "zero wrong" may be written only when that tool
prints a total of 0 with all eight fields found. Each command of sections 3 and 4 is also reported as a run of the
Council scorecard's shape - `run_at_utc` (`YYYY-MM-DDTHH:MM:SSZ`, with seconds), `kind` (`protocol` or
`out-of-pool`), `run_by`, `n`, `abstained`, `never_events`, `metrics` - and those runs are **listed by start time**
(section 5).

In the gold, a holders' table the runner means to be readable is written as a fact, so that a
wrong block shows, and a field an unread document - or a recognised document beyond its kind - may change is
written `TO_CONFIRM`, so that a fact shown against it is a never-event.
Names must be obviously invented, places end in `(ZZ)`, persons are `P-00N` with `SYN-CF-P00N` tax codes
and `.example` mail addresses, companies are `E-000N` with `TEST-REG-00000N` registry numbers.

Gold file (`"schema": "gold/2.0.0"`), one entry per entity; amounts are decimal strings, shares are
fractions as strings, no floating-point number anywhere:

    {
      "schema": "gold/2.0.0", "as_of": "YYYY-MM-DD", "seed": null, "perturbed": false,
      "cycle_policy": "abstain", "summary": {},
      "entities": {
        "E-0001": {
          "entity": "E-0001", "build": "OK", "blocked_by": [], "fault": "HAND", "documents": 5,
          "fields": {
            "name": {"status": "FACT", "value": "<name>", "sources": ["DOC-E0001-01"], "superseded": []},
            "share_capital.resolved": {"status": "DISCREPANCY", "values": ["50000.00", "60000.00"],
                                       "sources": ["DOC-E0001-01", "DOC-E0001-02"], "superseded": []},
            "share_capital.paid_in": {"status": "TO_CONFIRM", "superseded": []},
            "shareholders": {"status": "FACT", "sources": ["DOC-E0001-01"], "superseded": [],
                             "value": [{"holder": "P-001", "share": "3/5"}, {"holder": "P-002", "share": "2/5"}]},
            "directors": {"status": "FACT", "value": ["P-001"], "sources": ["DOC-E0001-01"],
                          "superseded": [{"old_source_doc": "DOC-E0001-00", "old_value": ["P-002"]}]}
          },
          "filename_divergences": [],
          "ownership": {"outcome": "RESOLVED", "cycles": [], "effective": {"P-001": "3/5", "P-002": "2/5"}}
        }
      }
    }

Field names: `name`, `legal_form`, `registered_office`, `share_capital.resolved`, `share_capital.subscribed`,
`share_capital.paid_in`, `shareholders`, `directors`, `fin.FY<year>.total_assets`, `fin.FY<year>.revenue`,
`fin.FY<year>.net_equity`. A cap table that must not render is written `"build": "BLOCKED"`,
`"blocked_by": [{"source_doc": "DOC-...", "sum": "9999/10000"}]` and
`"ownership": {"outcome": "BLOCKED", "cycles": [], "effective": null}`. A file whose name or folder
contradicts its content is listed as `{"doc_id": "DOC-...", "aspect": "date"}` under `filename_divergences`
(aspects: `folder`, `date`, `kind`, `appointee`). `sources` lists every document that a correct dossier may cite for the value.
Any complete gold of the generator shows the same shape: `python -m corpus.generate --suite dev --out <new folder>`
writes one as `gold.json` (development seed, already inspected by the author).

Then, once:

    python -m eval.score --corpus <DIR>/input --gold <DIR>/gold.json --label hand --json build/blind/hand.json

If the scorer stops because the gold file is malformed, that is a gold error, not a run: correct the form
of the gold (not its values) and note the correction in the record of section 5.

## 5. Recording the outcome

Append one run to the `runs` list of `eval/history.json`, after the last one, numbered `n` = previous + 1,
and commit it. Nothing already in the list is edited, with one exception: a name of the owner's internal folders
written in a note is replaced by "the evaluation folders" and the replacement is recorded in the top-level list `redactions`
(run, field, the SHA-256 of the note before, the commit where the original stays readable, the reason). The numbers and
the results of a run are never redacted. The entry `blind` of the same file records the
blind run of `v2.0.0-freeze` and is not edited either: the run of `v2.0.7-freeze` is recorded in `runs`,
as the runs of `v2.0.1-freeze`, `v2.0.2-freeze`, `v2.0.3-freeze`, `v2.0.5-freeze` and `v2.0.6-freeze` were (runs
7, 9, 11, 14 and 16), with `code` naming the tag and `run_by` naming the runner. The entry has the seven keys of every run already
recorded - `n`, `date`, `run_by`, `code`, `command`, `note`, `results` - and no other (runs 14 and 16 were recorded
so; until `v2.0.7` this section also asked for `kind`, `run_at_utc` and `scorecard` here, which no run has). The
UTC start and end of each command, with seconds, go in the note.

The paragraph above, which holds the rule D33, is kept word for word in this version. For `v2.0.10-freeze` it
applies in the same way: the run of `v2.0.10-freeze` is recorded in `runs` after run 23 (the builder's measurement of `v2.0.10`, not
blind), as the runs of `v2.0.7-freeze`, `v2.0.8-freeze` and `v2.0.9-freeze` were (runs 18, 20 and 22), with `code`
naming the tag (below) and `run_by` naming the runner. Since `v2.0.10` the note also gives the exit code of each
command (3: a measurement that failed, with its stderr) and the deep and the short run of section 4. Since `v2.0.8` the note also gives, for each result, the sum of every `*_wrong_committed` field of its
JSON file, taken with the evaluator's tool (section 4).

    {
      "n": <previous + 1>,
      "date": "<YYYY-MM-DD of the run>",
      "run_by": "<name of who ran it - not the author>",
      "code": "tag v2.0.10-freeze, commit 6d466e2",
      "command": "<the commands of sections 3 and 4, exactly as typed, seed included>",
      "note": "<exit code and UTC start and end, with seconds (YYYY-MM-DDTHH:MM:SSZ), of each command; for each result the never-events, the sum of every *_wrong_committed field by the evaluator's tool, the entities blocked wrongly, the fields left [TO CONFIRM] and the four counts of the entities not published; who chose the seed and who wrote the hand documents; which forms were meant inside and which outside the claimed classes; anything that went wrong>",
      "results": [ <the objects of the "results" lists of the three JSON files, verbatim, in order 3a, 3b, 4> ]
    }

The shape of the Council scorecard goes in the evaluator's own scorecard, outside this repository: one run per
command, **listed by start time**, each with `run_at_utc` (`YYYY-MM-DDTHH:MM:SSZ`, with seconds), `kind`
(`protocol` for the commands of sections 3 and 4, `out-of-pool` for any other corpus), `run_by`, `n` (the
entities of the corpus), `abstained` (the metric `fields_abstained`), `never_events` and `metrics` (verbatim from
the JSON file). The note of the history entry gives the same runs in the same order, by start time. Since `v2.0.8`
the `metrics` of each run carry the eight `*_wrong_committed` fields and `never_events_by_kind_total`; their sum,
taken with the evaluator's tool, is reported beside `never_events`.

    "runs": [
      {"run_at_utc": "<YYYY-MM-DDTHH:MM:SSZ>", "kind": "protocol", "label": "<label>", "run_by": "<name>", "n": <entities>, "abstained": "<fields_abstained>", "never_events": <n>, "metrics": { <the metrics of the result, verbatim> }}
    ]

The hand-written documents and their gold are committed next to the record, in a new folder
`eval/blind/hand-<n>/` named after the number of the run (the folders `eval/blind/hand/`,
`eval/blind/hand-9/`, `eval/blind/hand-11/`, `eval/blind/hand-14/`, `eval/blind/hand-16/`, `eval/blind/hand-18/`,
`eval/blind/hand-20/` and `eval/blind/hand-22/` hold those of runs 7, 9, 11, 14, 16, 18, 20 and 22 and are not edited), so that the run can be repeated by anyone. `python -m unittest discover -s tests -t .`
must still pass after the commit (the record must keep the runs already listed untouched).

## 6. What the author verified about this protocol, and what not

- Verified on 2026-09-30, on the code of `v2.0.0-freeze`, with the **development** seed only: the `--seed` path
  (`--seed 20260930`) and the `--corpus ... --gold ...` path (on the generated development corpus) both give
  the numbers of the development suite (run 4 of `eval/history.json`).
- Verified on 2026-09-30 as well: a gold written by hand in the form of section 4 for the two documents of
  scenario S01 (already known to the author) is accepted by the scorer and scored
  (`never_events=0`, conflicts 3/3 and 3/3, facts 5/5, abstained 0/8).
- On the code of `v2.0.1-freeze` (verified on 2026-09-30 by the hand that wrote the fix, run 6 of
  `eval/history.json`, commit `058e8ac`, whose frozen files differ from the tag only in `MANIFEST.sha256`):
  the `--suite` path on the three seeds of the author, and the `--corpus ... --gold ...` path on the three
  corpora of run 5. The `--seed` path was not run on `v2.0.1-freeze` by the author; the evaluator ran
  it blind (run 7).
- On the code of `v2.0.2-freeze` (verified on 2026-09-30 by the builder's hand, run 8 of
  `eval/history.json`, commit `4b2dbaa`, whose frozen files differ from the tag in `tests/test_hygiene.py`
  and `MANIFEST.sha256` only): the `--suite` path on the three seeds of the author, the `--seed` path on
  20261011 and 20261012, plain and perturbed, and the `--corpus ... --gold ...` path on the out-of-pool
  corpus of run 5 and on the hand-written corpus of run 7 (`eval/blind/hand/`, whose gold has a blocked cap
  table and a file-name divergence). 0 never-events on all nine results. Not blind.
- On the code of `v2.0.3-freeze` (verified on 2026-09-30, UTC 2026-09-30T23:29:37Z to 2026-09-30T23:31:39Z, by
  the builder's hand, run 10 of `eval/history.json`, commit `5a13f3f`, whose frozen files differ from the tag
  in `MANIFEST.sha256` only): the `--suite` path on the three seeds of the author, the `--seed` path on
  20261011, 20261012 and 20261013, plain and perturbed, and the `--corpus ... --gold ...` path on the
  out-of-pool corpus of run 5 and on the hand-written corpora of runs 7 and 9. 0 never-events on all twelve
  results; blocked wrongly 2 of 9 on hand-9 (E-0003, E-0007: holders in a sentence, nominal amounts, a
  table with a header row - known limits). Not blind.
- On the code of `v2.0.4-freeze` (verified on 2026-10-01, UTC 2026-10-01T01:09:07Z to 2026-10-01T01:09:57Z,
  by the builder's hand, run 12 of `eval/history.json`, commit `4c90d53`, whose frozen files differ from the
  tag in one comment of `tests/test_d30b_forms.py` and in `MANIFEST.sha256` only): the `--suite` path on the
  three seeds of the author, the `--seed` path on 20261011, 20261012, 20261013 and 20261014, plain and
  perturbed, and the `--corpus ... --gold ...` path on the out-of-pool corpus of run 5 and on the
  hand-written corpora of runs 7, 9 and 11. 0 never-events on all fifteen results (hand-11: 2 with the code
  of `v2.0.3-freeze`, 0 with `v2.0.4`); blocked wrongly 3 of 15 on hand-11 (E-0002, E-0011, E-0014: a
  "current" qualifier in free words, a header row, per mille - known limits) and 2 of 9 on hand-9. Not
  blind: hand-11 was read to write `v2.0.4`.
- On the code of `v2.0.5-freeze` (verified on 2026-10-01, UTC 2026-10-01T02:45:16Z to 2026-10-01T02:47:59Z,
  by the builder's hand, run 13 of `eval/history.json`, commit `f76dfad`, whose frozen files differ from the
  tag in `MANIFEST.sha256` only): the `--suite` path on the three seeds of the author, the `--seed` path on
  20261011, 20261012, 20261013 and 20261014, plain and perturbed, and the `--corpus ... --gold ...` path on the
  out-of-pool corpus of run 5 and on the hand-written corpora of runs 7, 9 and 11. 0 never-events on all
  fifteen results; the same entities blocked as with `v2.0.4`; blocked wrongly 3 of 15 on hand-11 and 2 of 9
  on hand-9 (known limits). The 379 sibling cases of `tests/test_d34_forms.py`: 348 published wrongly and 15
  failed on the code of `v2.0.4-freeze`, 0 on `v2.0.5`. Not blind: every corpus had been seen.
- On the code of `v2.0.6-freeze` (verified on 2026-10-01, UTC 2026-10-01T04:46:38Z to 2026-10-01T04:52:41Z, by the
  builder's hand, run 15 of `eval/history.json`, commit `a982b7b`, whose frozen files differ from the tag
  in `MANIFEST.sha256` and in one test class added to `tests/test_d35_forms.py`, the hand-14 exact-form
  fixture, only): the `--suite` path on the three seeds of the author, the `--seed` path on 20261011
  to 20261015, plain and perturbed, and the `--corpus ... --gold ...` path on the out-of-pool corpus of run 5 and
  on the hand-written corpora of runs 7, 9, 11 and 14. 0 never-events on all eighteen results. The 192 sibling
  cases of `tests/test_d35_forms.py`: 147 published wrongly on the code of `v2.0.5-freeze`, 0 on `v2.0.6`; the
  variant of hand-14 E-0011/E-0012 in the exact form: 3 never-events on `v2.0.5-freeze`, 0 on `v2.0.6`. Not
  blind: every corpus had been seen, hand-14 included.
- On the code of `v2.0.7-freeze` (verified on 2026-10-01, UTC 2026-10-01T07:01:48Z to 2026-10-01T07:05:08Z, by the
  builder's hand, run 17 of `eval/history.json`, commit `b624830`, whose frozen files differ from the tag in
  `MANIFEST.sha256` only): the `--suite` path on the three seeds of the author, the `--seed` path on 20261011 to
  20261016, plain and perturbed, and the `--corpus ... --gold ...` path on the out-of-pool corpus of run 5 and on
  the hand-written corpora of runs 7, 9, 11, 14 and 16. 0 never-events on all twenty-one results; eighteen equal
  to those of `v2.0.6`, hand-11 in figures with source only (134 -> 132), hand-16 published 12 -> 14 of 28 and
  20261016 perturbed blocked wrongly 5 -> 4. The 600 sibling cases of `tests/test_d36_forms.py`: 312 unsafe on
  the code of `v2.0.6-freeze` (56 a FAILED run, 256 publish a field), 0 on `v2.0.7`; the masked probes of hand-16
  unmasked: E-0014 a FAILED run on `v2.0.6-freeze`, every field `[TO CONFIRM]` on `v2.0.7`; E-0017 blocked on
  both. Not blind: every corpus had been seen, hand-16 included.
- On the code of `v2.0.8-freeze` (verified on 2026-10-01, UTC 2026-10-01T10:20:53Z to 2026-10-01T10:25:42Z, by the
  builder's hand, run 19 of `eval/history.json`, commit `67cb31d`, whose frozen files differ from the tag in
  `MANIFEST.sha256` only): the `--suite` path on the three seeds of the author, the `--seed` path on 20261011 to
  20261017, plain and perturbed, and the `--corpus ... --gold ...` path on the out-of-pool corpus of run 5 and on
  the hand-written corpora of runs 7, 9, 11, 14, 16 and 18. 0 never-events on all twenty-four results; the sum of
  every `*_wrong_committed` field of the twenty-four JSON files, taken with the evaluator's tool against the
  scorer of the tag, is 0 (192 values, the eight fields found in each); hand-18 4 -> 0 (E-0015 published with
  every field `[TO CONFIRM]`); published and blocked wrongly equal to those of `v2.0.7` on all twenty-four. The 738
  sibling cases of `tests/test_d37_forms.py` and `tests/test_d37_slots.py`: 429 published wrongly on the code of
  `v2.0.6-freeze`, 423 on `v2.0.7-freeze`, 0 on `v2.0.8` (6 FAILED, fail-closed, as on both earlier codes). Not
  blind: every corpus had been seen, hand-18 included.
- On the code of `v2.0.9-freeze` (verified on 2026-10-01, UTC 2026-10-01T13:30:33Z to 2026-10-01T13:36:35Z, by the
  builder's hand, run 21 of `eval/history.json`, commit `99894a9`, whose frozen files differ from the tag in
  `MANIFEST.sha256` only): the `--suite` path on the three seeds of the author, the `--seed` path on 20261011 to
  20261018, plain and perturbed, and the `--corpus ... --gold ...` path on the out-of-pool corpus of run 5 and on
  the hand-written corpora of runs 7, 9, 11, 14, 16, 18 and 20. 0 never-events on all twenty-seven results; the sum
  of every `*_wrong_committed` field of the twenty-seven JSON files, taken with the evaluator's tool against the
  scorer of the tag, is 0 (216 values, the eight fields found in each); hand-20 8 -> 0 (E-0009 and E-0010 block:
  the slot holds a numeral); the nineteen generated results equal to those of `v2.0.8` in every count and metric;
  published and blocked wrongly lower on every hand-written corpus (hand-20 27 -> 1 of 34, blocked wrongly 6 -> 32).
  The 624 sibling cases of `tests/test_d38_identification.py`: 267 published wrongly on the code of
  `v2.0.7-freeze`, 154 on `v2.0.8-freeze`, 0 on `v2.0.9` (0 FAILED). A work folder of about 230 characters and a
  TEMP of about 100 characters on Windows with long-path support off: built (`tests/test_d38_long_paths.py`; both
  fail on the code of `v2.0.8-freeze`). Not blind: every corpus had been seen, hand-20 included.
- On the code of `v2.0.10-freeze` (verified on 2026-10-01, UTC 2026-10-01T17:06:18Z to 2026-10-01T17:13:12Z, by the
  builder's hand, run 23 of `eval/history.json`, commit `564dc73`, whose frozen files differ from the tag in
  `tests/test_scenarios.py` (commit `e68704d`, the test's own work folders) and in `MANIFEST.sha256` only): the
  `--suite` path on the three seeds of the author, the `--seed` path on 20261011 to 20261019, plain and perturbed,
  and the `--corpus ... --gold ...` path on the out-of-pool corpus of run 5 and on the hand-written corpora of runs
  7, 9, 11, 14, 16, 18, 20 and 22. 0 never-events on all thirty results, every measurement `OK`, every command exit
  0; the sum of every `*_wrong_committed` field of the thirty JSON files, taken with the evaluator's tool against
  the scorer of that commit, is 0 (240 values, the eight fields found in each); every count and metric equal to
  those of `v2.0.9` but hand-22, fields exact 78 -> 80 of 223 (E-0007). Hand-22 scored from a work folder of 282 characters on Windows
  with long-path support off: the numbers of the short folder, measurement `OK` (on the code of `v2.0.9-freeze`:
  0/0 fields, exit 0, an empty stderr); a provenance file removed after the build: exit 3 (on `v2.0.9-freeze`: exit
  0). The 78 sibling cases of `tests/test_d39_capital_count.py`: 0 published wrongly on the code of
  `v2.0.9-freeze`, 0 on `v2.0.10`. Not blind: every corpus had been seen, hand-22 included.
- Not verified: any seed other than the twelve named in section 0; any hand-written document other than the
  scenario inputs, those of runs 7, 9, 11, 14, 16, 18, 20 and 22 and the texts of the tests; the count form of the
  capital clause written by a hand other than the builder's under `v2.0.10`; a scorer exit 3 met in a blind run;
  two documents that name the wrong entry of the gazetteer alike (item 1 of section 4: a question of
  the inputs, which the pack does not claim to see); a person identified by the identity layer of the input instead
  of the gazetteer (item 7 of section 4, a choice `[TO CONFIRM]`); a gazetteer made of real registers
  (`identification_source`, `[TO CONFIRM with legal]`); a row with "each" and a table with a header row read (not
  written); a narrower criterion for `DISC-006` (a document superseded by a later source that reads the field),
  which is not written; a hand-written gold with a cycle; any operating system other than Windows. Until `v2.0.10`
  this item also named "added words that are entries of the gazetteer, placed where its pattern does not take them,
  written by a hand other than the builder's under `v2.0.9`", which run 22 measured. Until `v2.0.9`
  this item named the premise of corroboration ("two documents of an entity that carry the **same** added words in
  an address, a header name or a label"), which run 20 found. Until `v2.0.8` this item named, instead of the
  premise, the residual risk of `v2.0.7` ("a street or a town of place-name-form words of no class of
  `slot_not_name_word` that states another field"), which run 18 found.
