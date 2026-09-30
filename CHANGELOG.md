# Changelog

SYNTHETIC - proof pack of a synthetic AI agent; every entity, person, deed and registry extract is invented.

## [2.0.2] - 2026-09-30 (freeze tag `v2.0.2-freeze`; not yet run blind)

Source: the evaluator's blind run of `v2.0.1-freeze`, `eval/history.json` run 7, seed 20261012: 0 never-events
on every corpus, and 89 of 150 entities of the perturbed corpus blocked wrongly by `OWN-015` (3 of 150 in the
plain corpus, 0 of 2 in the hand corpus).

### D26 follow-up - owner decision 30-Sep-2026: OWN-015 stays block; more holders'-table forms read

`OWN-015` and its parameter `unverified_holders_table` keep the value `block`, `[TO CONFIRM with legal]`: a
holders' table that cannot be read and verified - exact fractions that sum to the whole, each with its source
document and date - still blocks the entity. What changed is how many forms are read.

Causes of the wrong blocks, reproduced on the v2.0.1 code by the builder, counted per unread table of an
entity the gold builds and the run blocked (an entity can have more than one):

| Form class | stress, seed 20261002 | seed 20261011 perturbed | seed 20261012 perturbed | In v2.0.2 |
|---|---|---|---|---|
| A. holders' heading in another wording (`Members:`, `4. Members.`, `Members at the document date:`, `After the transfer the members are:`) | 82 | 79 | 85 | read |
| B. document type not recognised (`Register of members`, `Articles of incorporation`, `Extract from the test registry`, `Notice of assignment of shares`, `Minutes - ...`, `Summary of the annual accounts`) | 53 | 65 | 64 | body checked; blocks only when it may hold a table that is not read |
| C. a share planted as illegible (the gold abstains on the holders) | 1 | 2 | 3 | still blocked, by design (D26) |

No holder line of another form was found in these corpora. What changed (the rules first, the code where a
rule cannot say it):

- `rules/extract.json` 2.0.2, class A: the heading of `EXT-HOLD-010` is the grammar of the new parameter
  `holders_heading` - a holder noun (holders, shareholders, stockholders, quotaholders, members, partners),
  an optional clause number, an optional qualifier that means "current" (after or following the transfer,
  as at the document date, now, at present) before or after the noun. A qualifier not known to mean
  "current" (before the transfer, former, of the board) is not a heading and the document abstains on the
  holders as before; owners, beneficial owners and directors are not holder nouns. New: two holders'
  headings in one document abstain (`dossier/s1_extract.py`, `_extract_list`; before, the first was taken).
- `rules/extract.json` 2.0.2, class B: new ordered group `holders_evidence` (`HEV-010` to `HEV-080`, default
  `HEV-999`, each with inline tests): a share in any written form, an entity identifier, a holder noun, a
  word of holding, a number of shares, a person identifier with a figure, a list item or table row with a
  figure, a line ending with a bare figure. Phrases such as "holders' meeting" are neutral. The rules err on
  the side of evidence: a line wrongly taken as evidence costs coverage, not a never-event.
- `dossier/s1_extract.py`: `holders_check` of a document whose only header problem is its type: `read`
  (every table under a holders' heading read whole with the item grammar of `EXT-HOLD-010`), `no_table`
  (no table and no line of evidence), `not_read` (anything else). A document with any other header problem
  (no valid date, no edition, no id) stays `not_read`. The document still gives no fact: `DISC-005` keeps
  every field it may change `[TO CONFIRM]`.
- `dossier/s4_ownership.py`: a document checked `no_table` or `read` is no longer an unread table
  (`unverified_tables`); the tables of a `read` document are summed with the others (`sum_checks`), so one
  that does not sum blocks the entity (`OWN-010`). `schema/entity_record.schema.json`: optional
  `holders_check` on a problem document (`schema_version` stays 2.0.0). `rules/ownership.json` 2.0.2: the
  note of `unverified_holders_table` says this; the value is unchanged.
- Known limits, still blocked: a holders' table without a heading or under a heading of another form
  ("Allocation of the capital:"), a holder line with the name before the identifier, a share in words or in
  "per cent" inside a table, shares counted rather than fractioned, nominal amounts per holder, a document
  date in words, two tables in one document. Classified documents of other kinds (resolutions,
  appointments, office transfers, financial summaries) are still not searched for holders' tables, as in
  v2.0.1.

### D29 - never-event definition aligned

The definition in `eval/BLIND_PROTOCOL.md` section 1.5 ("a figure rendered as fact that differs from the
gold or has no source", with two inclusions) and in the README was narrower than what `eval/score.py`
counts. The README now states the scorer's list word for word, and the protocol does from the commit after
the tag. `eval/score.py`: no change of behaviour; its docstring now lists all eight kinds the code counts
(two were missing: a field shown that is not in the gold, a published cap table that does not sum). Tests:
`tests/test_hygiene.py` requires the README to carry the scorer's list; `tests/test_never_event.py` counts
one never-event of each kind that had no test (field not in the gold, conflict with values not the gold's,
published cap table not summing, effective holdings where the reference abstains).

### Tests and numbers

- `tests/test_holders_forms.py`, 25 tests. Run on the v2.0.1 code, 16 fail: 13 end-to-end cases (every new
  form read; every document of unrecognised type that should now publish; a class-A and a class-B table that
  does not sum, which v2.0.1 blocked for the wrong reason, `OWN-015` instead of `OWN-010`; two holders'
  headings in one document, which v2.0.1 published by taking the first table) and the 3 unit tests of the new
  functions. 9 pass on both: the limits, which v2.0.1 also blocked.
- Two older tests expected the v2.0.1 block for a document of unrecognised type with no holders in it
  (`tests/test_extract.py`, `tests/test_never_event.py`): they now expect the dossier with no fact, and the
  same document with a holding in its text still blocks. `tests/test_rules.py` counts 56 rules.
- Measured by the builder on corpora already seen (`eval/history.json` run 8; NOT blind): dossiers published
  v2.0.1 -> v2.0.2, stress 45 -> 137, seed 20261011 perturbed 42 -> 135, seed 20261012 perturbed 48 -> 134;
  entities blocked wrongly 93 -> 1, 96 -> 3, 89 -> 3, the same count as the plain corpora of those seeds
  (shares planted as illegible). Development, holdout and the plain corpora of 20261011 and 20261012 do not
  move. The evaluator's out-of-pool corpus of run 5: 9 -> 44 published. Never-events 0 on every corpus.

## [2.0.1] - 2026-09-30 (freeze tag `v2.0.1-freeze`; not yet run blind)

### Fixed - finding T16, source: the evaluator's blind run of `v2.0.0-freeze` (2026-09-30, `eval/history.json` run 5)

The blind run found 13 never-events: 0 in the plain corpus, 1 in the perturbed one, 12 in the
out-of-pool one (wordings written by the evaluator). They are of two kinds.

1. **Five figures shown as fact a thousand times too small** (T16; out-of-pool only). `EUR 150'000.00`,
   an apostrophe as the thousands separator, was read as `150.00`: capital resolved of E-0065; resolved,
   subscribed and paid-in capital of E-0114; one side of the discrepancy of E-0112 (`220.00` against
   `230000.00`). Cause: the amount token of `rules/extract.json` (`amount_token`, line 10 at the tag)
   accepted only digits, dots, commas and spaces, so it stopped at the apostrophe and `150` was taken
   for the whole amount; the audit (`dossier/s7_audit.py`, `_AMOUNT_IN_QUOTE`) cut its quote at the same
   place and confirmed the wrong figure; `dossier/lib/numbers.py` did not know apostrophe grouping.
2. **Eight dossiers published for entities whose holders' table does not sum to the whole** (7 out-of-pool,
   1 perturbed). The table was not read - a share written "30 per cent", a holder line with the name before
   the identifier, the heading "Shareholders:", a document date written in words, and, in the perturbed
   corpus, the document type "Articles of incorporation", which is in the pack's own perturbation list -
   so the holders were shown `[TO CONFIRM]` with no cap table and the dossier was published. No figure
   was wrong, but claim A3 says "blocked, not footnoted", and the scorer counts the published dossier of an
   entity whose table does not sum as a never-event.

What changed (the rules first, the code where a rule cannot say it):

- `rules/extract.json` 2.0.1: the amount token no longer stops at a separator (dot, comma, apostrophe,
  the typographic and look-alike apostrophes, any horizontal space). An amount is abstained, with its
  reason, when a further separator, an attached character or a magnitude word follows it
  (`EUR 150 thousand`, `EUR 150k`), when a magnitude word stands before it (`Mio. EUR 1`), or when its
  document states a scale (`in thousands of EUR`, `TEUR`, `EUR '000`). New inline tests in `EXT-CAP-010`
  and `EXT-FIN-010/020/030`.
- `dossier/lib/numbers.py`: read are `1.500.000,00`, `1,500,000.00`, and grouping by apostrophe (`'`,
  `’` U+2019), space, no-break space (U+00A0), figure space (U+2007), thin space (U+2009) and narrow
  no-break space (U+202F), with dot or comma decimals and the same character throughout. Mixed or
  look-alike groupings (U+2018, U+02BC, U+2032, acute accent, backtick, middle dot, two different
  separators) give no value and a reason that names the character: abstained, never guessed.
- `dossier/s7_audit.py`: the audit reads the whole figure of the quote, and so does the scan of outgoing
  text; a figure is supported by its quote only if the quote writes the same digits.
- `rules/ownership.json` 2.0.1, rule `OWN-015` and parameter `unverified_holders_table` (value `block`,
  `[TO CONFIRM with legal]`): a holders' table that could not be summed - a share not read, a holder line
  or heading not read, a document that should state the holders where none was found, a document dated
  up to the reference date that was not classified or was rejected - blocks the entity, as a table that
  does not sum would. `report` gives back the behaviour of v2.0.0.
- `tests/test_amount_grouping.py`: 9 tests built from the evaluator's documents (synthetic, copied). Run on
  `v2.0.0-freeze`, 8 fail; the ninth (look-alike separators are not read) is a guard v2.0.0 already passed.
  Three older tests expected a dossier where OWN-015 now blocks (`tests/test_extract.py`,
  `tests/test_never_event.py`); they now expect the block, and the old expectation is kept under
  `unverified_holders_table = report`. `tests/test_rules.py` now counts 47 rules and 10 legal
  assumptions. 179 tests in all.

### The price, and what is still not known

- **Coverage.** An entity with any holders' table that could not be read is no longer published. Run 6
  (`eval/history.json`): dossiers published, development 141 -> 139, holdout 139 -> 137 (shares planted
  as illegible), stress 138 -> 45 (headings, holder lines and document-type labels of the perturbed
  wording); on the evaluator's corpora of run 5, 135, 42 and 9 of 150. Never-events are 0 on all six.
  Whether this price is the right one is a decision, not a measurement: the parameter above.
- The evaluator's out-of-pool wordings were **not** added to the reading rules: they would stop being
  out of pool. They are still not read; they are now abstained or blocked.
- The fix was measured by the hand that wrote it, on corpora that hand had already seen (run 6). It has
  not been run blind. `eval/BLIND_PROTOCOL.md` names the new tag for a different hand.
- Magnitude words and scale statements are a fixed list in `rules/extract.json` (English words and
  abbreviations, and a few Italian, German and Indian ones). A scale written another way is not detected.

## [2.0.0] - 2026-09-30 (freeze tag `v2.0.0-freeze`; the blind run is not part of this entry)

First proof pack. Before it the repository held only the profile (README, avatar, licence).

### Added

- `dossier/`: one chained run - documents, entity record, resolution of each field, ownership graph,
  snapshot, DOCX with provenance, audit of what was written, shareable layer - with exit codes
  0 (OK), 2 (BLOCKED), 3 (FAILED). `RUN OK` is printed only on exit 0.
- `rules/`: four ordered rule files (first match wins, exceptions on top); 46 rules, each with an id,
  a rationale and inline tests that every run executes before it builds anything.
- `schema/`: JSON Schema of the entity record. Amounts are decimal strings, shares are fractions;
  floating-point numbers are refused on reading and on writing.
- `corpus/`: generator of synthetic corpora from a seed, gold labels written from the generated world
  (never by reading the rendered documents back), `MANIFEST.sha256`, an ownership reference that shares
  no code with the pipeline.
- `scenarios/S01..S10/`: input, hand-written expected values, a checker, one paragraph each;
  `scenarios/run_all.py`.
- `tests/`: offline `unittest` suite; sockets are blocked in the process and in its children.
- `eval/score.py`, `eval/history.json`: the scorer and every measurement taken, in order, verbatim.
- `tools/`: pack manifest, generated `docs/ASSUMPTIONS.md`, double rebuild with hashes.
- `SYNTHETIC.md`, `MODEL.md`, `CLAIMS.md`, `requirements.txt` with hashes, an offline CI workflow
  (written, never executed).
- README: a proof-pack section above the profile. The profile text itself is unchanged.

### Out of v2.0, on purpose

- Statutory-obligation calendars and any statutory deadline (decision 1 of the approved plan).
- Access control on the identity layer; articles of association as a document type; real registries.
- Any measurement on real companies.

### Changed during development - each one decided after looking at output, and recorded for that reason

1. **Stress suite, first run: 32 never-events** (history run 2, code `9a50ea3`). Two causes, found by
   reading the stress cases: a document whose type wording was not recognised was left out and an older
   value was shown as fact; and when one current source could not be read, the value of the other one
   was shown as fact. Fixed in the rules, not in the outputs: `DISC-005` (an unread document that may
   change a field blocks every fact of that field) and `DISC-030` (an unreadable current source blocks
   the fact; what could be read is listed as a statement). After the fix: 0 never-events on the three
   suites (history run 3), at the price of abstaining on about half of the stress fields.
2. **Scenario S04, first run: one false positive.** A decoy line about a "capital expenditure plan" was
   flagged as a stale share capital. Fixed in the rule file (`field_cue_exclusions` of the outgoing
   scan, with an inline test), not in the scenario. Decoys and guards share an author: 0 false positives
   on ten decoys is a weak result, and S04 says so.
3. **Register of superseded values**: it now names both the newest source of the current value and the
   document that changed it, after a hand-written expectation of S04 disagreed with the first output.
4. **Found while writing the tests, not by any suite** (none of these changed a measured number):
   - two event documents of the same day, or two documents carrying the same edition of the same series,
     were ordered by document id - a silent tie-break. They are now all current: if they disagree the
     field is a `DISCREPANCY` (`rules/discrepancy.json`, reading and inline tests of `DISC-020`);
   - two files under one document id now fail the run for that entity, with that reason;
   - a value that is not in canonical form now makes the builder refuse instead of crash;
   - floats are refused on writing too, not only on reading;
   - a run that finds nothing to build is `RUN FAILED`, no longer `RUN OK` with zero dossiers;
   - a rejected document is named in the failure reason before the schema error it causes.
   The random test of the resolution had been written with the same tie-break as the code and could
   not have found the first item; its oracle is now written over sets, without any ordering.

### Known limits

- Generator, gold labels, rules, scenarios and tests share one author and one model. Clean numbers on
  the development and holdout suites measure internal consistency, not accuracy.
- The holdout suite was scored more than once (runs 2, 3 and 4); it was never inspected, and no rule
  was changed because of it. It is no longer a clean holdout: the blind run is the only untouched test.
- Byte identity of the DOCX is verified on Windows only. The CI workflow has never been executed.
- Every legal assumption is a parameter marked `[TO CONFIRM with legal]`; none has been reviewed.
