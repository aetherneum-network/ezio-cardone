# Changelog

SYNTHETIC - proof pack of a synthetic AI agent; every entity, person, deed and registry extract is invented.

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
