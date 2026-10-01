# Blind protocol

SYNTHETIC - this protocol measures a test pipeline on invented documents. It measures internal consistency
on synthetic data, never accuracy on real companies. Nothing real may be used as input.

Written after the freeze tag, by the author of the pack, for a **different hand**. The author (a synthetic
AI agent, via Claude Opus 5.5) does not choose the blind seed, never generates or looks at a blind corpus,
and does not run anything below.

**Updated after the tag `v2.0.7-freeze`.** The blind runs so far, all recorded in `eval/history.json`:

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

This protocol now applies to `v2.0.7-freeze`; besides the names of the tag, it changes section 0 (the seed
20261016 and the hand-written documents of run 16 are known, the seeds through 20261016 scored again in run 17,
the texts of the tests of `v2.0.7` are known), section 4 (the classes `v2.0.7` claims, the complete list of its
known limits - none may publish -, the residual risk, adversarial documents of unrecognised and of recognised
type, at least five unmasked probes of typed slots whose other lines are in forms the pack reads, a
masked/not-masked statement for each probe, the runs listed by start time) and sections 5 and 6. The section-5
rule on the redaction of internal folder names (D33) is carried over word for word. The earlier tags are not
moved and their blind runs are not repeated; `v2.0.4-freeze` was never run blind.

Until `v2.0.6-freeze` this paragraph read: "This protocol now applies to `v2.0.6-freeze`; ... section 4 (at least
twelve entities and thirty-two documents, the classes `v2.0.6` claims, the complete list of its known limits -
none may publish -, the residual risk, at least four unmasked probes of typed slots) and sections 5 (the shape of
the record) and 6."

## 0. What is frozen

| | |
|---|---|
| Tag | `v2.0.7-freeze` (annotated), created at 2026-10-01T07:17:00Z |
| Tag object | `06ff379e511f6ed22cb584aaee981dd3cd0d8b0e` |
| Commit | `452b46d5e2686aa0fca7d7aa50dec32e2ec3aa38` |
| Frozen files | the 175 files listed in `MANIFEST.sha256` (code, rules, schema, corpus generator, scenarios, tests, tools, scorer, requirements) |
| Not frozen | `README.md`, `CLAIMS.md`, `CHANGELOG.md`, `MODEL.md`, `eval/history.json`, `eval/blind/`, this file |
| Previous tag | `v2.0.6-freeze`, tag object `c7fa9d7a0380a6b81f51efd6c6df562f829c769c`, commit `6acebba59e0fb59972e5dab75e0908de77ed67f1`: run blind once (run 16), 0 never-events, 15 of 28 hand-written entities blocked wrongly, two probes masked (unmasked by the builder: E-0014 a FAILED run on that code, E-0017 blocked); its declared residual risk measured afterwards at 312 of 600 constructed siblings unsafe |
| Tag before it | `v2.0.5-freeze`, tag object `12453f2ac263d1cba7f88364b2be1a8f9186d344`, commit `267ea87f4fa147bc66fd2af64c499ac2bf019876`: run blind once (run 14), 0 never-events, 5 of 15 hand-written entities blocked wrongly, two probes masked (unmasked by the builder: 3 never-events on that code) |
| Earlier tag | `v2.0.4-freeze`, tag object `66f116539d7421b95d124b94a32d4e8bbc92ba9e`, commit `65b02335fb718ed061d3c9e665e26db97accc9ef`: not run blind; its one known limit that may publish is closed by `v2.0.5` |
| Earlier tag | `v2.0.3-freeze`, tag object `ae66f49debcb1bb15e83e1827acda35b03c4a3a6`, commit `77e7736f573c93024f0aa49157f5949287bee698`: run blind once (run 11), not passed - 2 never-events on hand-written entity E-0015, 8 of 15 hand-written entities blocked wrongly |
| Earlier tag | `v2.0.2-freeze`, tag object `475bd994bbd063c4dc7cebb15f50e7b9474ebd58`, commit `023c7cb5629b17295b4ddbbfeb22055a2be16b87`: run blind once (run 9), 0 never-events, 4 of 9 hand-written entities blocked wrongly |
| Earlier tag | `v2.0.1-freeze`, tag object `91cba79b5671a9f273a7ecf268dc92ffa8679a23`, commit `b65e45a5289133375222fa595abdbd9cd2087be7`: run blind once (run 7), 0 never-events, 89 of 150 perturbed entities blocked wrongly |
| First tag | `v2.0.0-freeze`, tag object `0c26555916701c4a81ea6490c32d5e7162edcdc8`, commit `d1769d555934ca5eaf4717bafe8135105caffd43`: run blind once (run 5), not passed |

Seeds already used, which therefore cannot be the blind seed: 20260930 (development, inspected),
20261001 (holdout, scored ten times - runs 2, 3, 4, 6, 8, 10, 12, 13, 15 and 17 -, never inspected; until
`v2.0.7` this line said "eight times", which run 15 had already made wrong), 20261002 (stress, inspected),
20261011 (the blind seed of `v2.0.0-freeze`: its plain, perturbed and out-of-pool corpora were read by the hand
that wrote the fix and scored again in runs 6, 8, 10, 12, 13, 15 and 17), 20261012 (the blind seed of
`v2.0.1-freeze`: its plain and perturbed corpora were generated, read and scored again by the hand that wrote
`v2.0.2`, runs 8, 10, 12, 13, 15 and 17), 20261013 (the blind seed of `v2.0.2-freeze`: its plain and perturbed
corpora were generated, read and scored again by the hand that wrote `v2.0.3`, runs 10, 12, 13, 15 and 17),
20261014 (the blind seed of `v2.0.3-freeze`: its plain and perturbed corpora were generated again from the
recorded seed, read and scored by the hand that wrote `v2.0.4` and `v2.0.5`, runs 12, 13, 15 and 17), 20261015
(the blind seed of `v2.0.5-freeze`: its plain and perturbed corpora were generated again from the recorded seed
and scored by the hand that wrote `v2.0.6`, runs 15 and 17), 20261016 (the blind seed of `v2.0.6-freeze`: its
plain and perturbed corpora were generated again from the recorded seed, read and scored by the hand that wrote
`v2.0.7`, run 17). For the same reason these wordings are known to `v2.0.7` and are no longer out of pool - a
new run needs other wordings:

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
- every example of `CHANGELOG.md` (sections 2.0.2 to 2.0.7) and of this protocol.

## 1. Rules of the run

1. The runner is not the author and chooses `<SEED>`: any integer other than the seeds of section 0, not
   told to the author before the run.
2. Each command of sections 3 and 4 is run **once**. There is no second attempt, whatever the result.
3. No frozen file is changed before or during the run. Section 2 proves it.
4. The outcome is recorded verbatim in `eval/history.json` (section 5), good or bad, with the name of who ran it.
5. The only pass or fail criterion, declared here before any blind run: **`never_events` is 0** in every
   result (the scorer exits with code 0; it exits with code 1 when there is at least one never-event). The
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

    git rev-parse "v2.0.7-freeze^{commit}"
    git diff --stat v2.0.7-freeze -- corpus dossier rules schema scenarios tests tools eval/__init__.py eval/score.py requirements.txt MANIFEST.sha256 docs
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
followed by one `NEVER-EVENT:` line per never-event (first ten; since `v2.0.3` the JSON file lists every one).
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

For `v2.0.7-freeze` the runner writes **at least twelve entities and at least thirty-two documents**, with
the **holders' tables** in **forms of its own choosing** - the heading, the holder lines, the form of the
shares and the type of the document that carries the table - not copied from the scenarios, from the
hand-written documents of runs 7, 9, 11, 14 and 16 (`eval/blind/hand/`, `eval/blind/hand-9/`,
`eval/blind/hand-11/`, `eval/blind/hand-14/`, `eval/blind/hand-16/`), from the texts of the tests
(`tests/test_d36_forms.py`, `tests/test_d35_forms.py`, `tests/test_d34_forms.py` and the earlier test files, the
inline tests of `rules/`) or from the examples of this protocol and of `CHANGELOG.md`: `v2.0.7` was written after
seeing those, and only forms it has not seen measure it. Some of the forms should fall **inside** the classes
`v2.0.7` claims to read, worded in ways it has not seen, and some **outside** them. Write every deed and every
registry extract in a form the pack claims to read (section 0 lists what it has seen), so that a probe is not
masked by an unrelated abstention.

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

Known limits of `v2.0.7`, the complete list of `CHANGELOG.md` (entry 2.0.7), each marked with what it does to
the entity - **blocks**, **keeps `[TO CONFIRM]`** or **may publish**. **No known limit may publish**
(`v2.0.4`: one; `v2.0.5`, `v2.0.6` and `v2.0.7`: none):

- holders stated in a sentence rather than in a list under a heading, a holder noun in a sentence of a
  memorandum, a resolution or an appointment among them (D31) - **blocks**;
- a row naming several holders with "each" - **blocks**;
- a qualifier meaning "current" in free words in the heading (`... once the transfer has taken effect:`), or a
  participle of another class than "registered" after a comma in the heading - **blocks**;
- a table with a header row - **blocks**;
- per mille - **blocks**;
- nominal amounts per holder, with no share and no count - **blocks**;
- a holders' heading with an explicit date, and headings of other nouns ("Allocation of the capital",
  "Capital allocation", ownership structure, owners, beneficial owners) - **blocks**;
- a heading without a final `.` or `:` that is not the whole line or is not followed by an item line: not a
  heading - holders **block**, directors **keep `[TO CONFIRM]`**;
- two holders' headings in one document - **blocks**; two directors' headings - **keeps `[TO CONFIRM]`**;
- a Total line that is not the last line of the table, that cannot be read, or that is in another unit than
  the rows - **blocks** (a Total that differs from the exact sum blocks by `OWN-010`, by design);
- a share before the holder written in words or as a count - **blocks**;
- a share in words in the same line as a date in words - **blocks**;
- counts without a total in the same document, with two totals, mixed with shares in one table, or in a
  document of unrecognised type - **blocks**;
- shares in words beyond whole per cent and simple fractions (`half` alone, decimals in words, a number that
  does not agree, more than a hundred per cent) - **blocks**;
- a label with nested or second parentheses - **blocks**;
- a document whose header cannot be read, a document date in words among them: it may change every field and
  its holders cannot be summed (`OWN-015`) - **blocks**;
- shares planted as illegible, by design (D26) - **blocks**;
- a document of unrecognised type not older than the latest event of a field: every field (`DISC-005`,
  `every_field`; since `v2.0.6` the record says so) - **keeps `[TO CONFIRM]`**; when it holds a line that may
  state a holding, or a holders' table that is not read whole - **blocks** (`OWN-015`). The list of `v2.0.5`
  gave the first outcome only, which was wrong;
- since `v2.0.5`, a document of a recognised type with a body line that no rule of its kind explains
  (`CLS-999`): every field, when the document is not older than the latest event (`DISC-006`) - **keeps
  `[TO CONFIRM]`**; when the line may state a holding - **blocks** (`OWN-015`);
- since `v2.0.5`, a closed line that states a field of its kind where no rule of its kind read it (a reworded
  label, an amount in words, a second clause or list; the office-transfer wording "The seat of the company is
  moved" of scenario S09 among them, unread by design), or a field its kind does not read: that field, when the
  document is not older than the latest event, even if a later source reads the field - **keeps
  `[TO CONFIRM]`**;
- since `v2.0.5`, a holders' table in a document of a kind not read for the holders: read whole and summed,
  then the holders **keep `[TO CONFIRM]`** (no exception for a table that agrees); not read, or two of them -
  **blocks**;
- since `v2.0.5`, a row of a list of a recognised document whose share is illegible or not typed: the row is
  not closed (`CLS-999`) - every field **keeps `[TO CONFIRM]`**, and when the row may state a holding
  (`holders_evidence`) - **blocks**;
- since `v2.0.7` marked (the list of `v2.0.6` did not cover it), a line right after a list with no blank line
  that is neither a list heading nor a full sentence of the form `list_end_sentence` - a sentence that names an
  identifier, a share or a figure with a unit noun (hand-16 E-0010), a wrapped row: a row of the list the grammar
  cannot read - holders **block**, directors **keep `[TO CONFIRM]`**;
- since `v2.0.6`, a name slot with a word of `slot_not_name_word` that is not its identifier's or its entity's
  own known name, a name beside an identifier that is not its own (`CLS-005`), or the entity's own name slot that
  differs from its `Entity:` header - every field **keeps `[TO CONFIRM]`** (`DISC-006`), and when the line may
  state a holding - **blocks**; a real name holding such a word and not beside its own identifier costs the same
  (since `v2.0.7` a name equal to its identifier's or its entity's own known name is a name whatever its words);
- since `v2.0.7`, a name beside an identifier whose own name the corpus does not know (not in the identity layer,
  no `Entity:` header of its own; every person when the identity layer names nobody): the line is open - every
  field **keeps `[TO CONFIRM]`**, and the holders **block** (`OWN-015`);
- since `v2.0.7`, an address without a house number, or whose street or town holds a word that is not of the form
  of a place name (a real `Viale Kennedy` or `Via Roma Nord` included), a name the corpus knows, or a word of
  `slot_not_name_word`: the line is open and the office is not read from it - every field **keeps
  `[TO CONFIRM]`** (`DISC-006`), and when the line may state a holding - **blocks**;
- since `v2.0.6`, a company name whose legal form differs from the legal form stated (`S.r.l.s.` against
  `S.r.l.` included, by design) - the legal form **keeps `[TO CONFIRM]`** and the name is shown as a discrepancy
  (`DISC-035`).

Residual risk, `[TO CONFIRM]` (`CHANGELOG.md` 2.0.7, section 4). Entry 2.0.6 stated it for the words of an
address slot, the name beside an identifier nobody knows and another company's name in a label; run 16 probed it,
two probes were masked, and measured afterwards by class the code of `v2.0.6` leaves 312 of 600 constructed
siblings unsafe (56 of them a FAILED run, 256 publish a field). `v2.0.7` closes every name slot by equality and
the amount, the count and the house number of an address by grammar, and the words of a street and a town by
their form. What **still rests on a word list** (`slot_not_name_word`, and the names the corpus knows): a street or
a town whose words all have the form of an Italian place name, name nobody the corpus knows, and state something
with a word of no class of that list - an Italian verb or noun ending in a vowel (`Via Ugo Nessuno Governa 1,
Montefinto (ZZ)`). Such a line closes and every field of the entity is published, the directors included. The case
is constructed and kept as a test expected to fail (`tests/test_d36_forms.py` `D36_ResidualWordList`). The lists of
`unread_fields` and `holders_evidence` are word lists too; under `every_field` they decide only whether an entity
blocks or keeps every field `[TO CONFIRM]`.

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
  field such a document may change is `TO_CONFIRM`;
- **at least five probes of typed slots that carry extra words**, unmasked, each in its own entity: a **name**
  (a person or a company, beside an identifier), an **ADDRESS**, an **AMOUNT**, a **COUNT**, and one more of the
  runner's choice - each in a line of a recognised document whose extra words change another field (the
  residual risk above: the words of a street or a town above all). Every **other** line of the probe's entity is
  in a form the pack reads, and the runner checks it **line by line** before the run: its deed and registry
  extract as in section 0, no document of unrecognised type, no other open line. Two forms by name, because run
  16 masked a probe with each: an office transfer is read only in the sentence `EXT-OFFICE-010` reads, `The
  registered office is transferred from <address> to <address>.`, with addresses of the form `Via del Collaudo 7,
  Borgoprova (ZZ)` (street, house number, town, province; "The seat of the company is moved" is read by no rule
  and keeps the office `[TO CONFIRM]` on its own); and a count of quotas is read with its total only in the
  capital clause `count_total` reads, as in the deed's `The share capital is EUR 10.000,00, divided into 1.000
  quotas, fully subscribed and fully paid in.` (a separate total line such as `The capital is divided into 1.000
  quotas.` is a line no rule explains, and the entity blocks on it alone, `OWN-015`);
- for **each probe, a statement masked / not masked**: whether anything other than the probe's own line made its
  entity abstain or block, and by which rule and line (the fields check names them), as runs 14 and 16 did; a
  masked probe is reported as measuring nothing;
- holders' tables inside and outside the claimed classes, including tables in documents of a kind not read
  for the holders.

With the never-events of this part, report the entities blocked wrongly, the fields left `[TO CONFIRM]` and
the four counts of the entities not published (rule 1.6), and every time in UTC **with seconds**, as
`YYYY-MM-DDTHH:MM:SSZ`. Each command of sections 3 and 4 is also reported as a run of the Council scorecard's
shape, and those runs are **listed by start time** (section 5).

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

    {
      "n": <previous + 1>,
      "date": "<YYYY-MM-DD of the run>",
      "run_by": "<name of who ran it - not the author>",
      "code": "tag v2.0.7-freeze, commit 452b46d",
      "command": "<the commands of sections 3 and 4, exactly as typed, seed included>",
      "note": "<exit code and UTC start and end, with seconds (YYYY-MM-DDTHH:MM:SSZ), of each command; for each result the never-events, the entities blocked wrongly, the fields left [TO CONFIRM] and the four counts of the entities not published; who chose the seed and who wrote the hand documents; which forms were meant inside and which outside the claimed classes; anything that went wrong>",
      "results": [ <the objects of the "results" lists of the three JSON files, verbatim, in order 3a, 3b, 4> ]
    }

The shape of the Council scorecard goes in the evaluator's own scorecard, outside this repository: one run per
command, **listed by start time**, each with `run_at_utc` (`YYYY-MM-DDTHH:MM:SSZ`, with seconds), `kind`
(`protocol` for the commands of sections 3 and 4, `out-of-pool` for any other corpus), `run_by`, `n` (the
entities of the corpus), `abstained` (the metric `fields_abstained`), `never_events` and `metrics` (verbatim from
the JSON file). The note of the history entry gives the same runs in the same order, by start time.

    "runs": [
      {"run_at_utc": "<YYYY-MM-DDTHH:MM:SSZ>", "kind": "protocol", "label": "<label>", "run_by": "<name>", "n": <entities>, "abstained": "<fields_abstained>", "never_events": <n>, "metrics": { <the metrics of the result, verbatim> }}
    ]

The hand-written documents and their gold are committed next to the record, in a new folder
`eval/blind/hand-<n>/` named after the number of the run (the folders `eval/blind/hand/`,
`eval/blind/hand-9/`, `eval/blind/hand-11/`, `eval/blind/hand-14/` and `eval/blind/hand-16/` hold those of runs 7,
9, 11, 14 and 16 and are not edited), so that the run can be repeated by anyone. `python -m unittest discover -s tests -t .`
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
- Not verified: any seed other than the nine named in section 0; any hand-written document other than
  the scenario inputs, those of runs 7, 9, 11, 14 and 16 and the texts of the tests; a street or a town of
  place-name-form words of no class of `slot_not_name_word` that states another field (the residual risk of
  section 4, constructed and kept as a test expected to fail, not closed); a row with "each" and a table with a
  header row read (not written); a narrower
  criterion for `DISC-006` (a document superseded by a later source that reads the field), which is not written;
  a hand-written gold with a cycle; any operating system other than Windows.
