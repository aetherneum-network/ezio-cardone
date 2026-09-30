# Changelog

SYNTHETIC - proof pack of a synthetic AI agent; every entity, person, deed and registry extract is invented.

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
