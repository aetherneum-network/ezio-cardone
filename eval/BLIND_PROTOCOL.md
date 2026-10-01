# Blind protocol

SYNTHETIC - this protocol measures a test pipeline on invented documents. It measures internal consistency
on synthetic data, never accuracy on real companies. Nothing real may be used as input.

Written after the freeze tag, by the author of the pack, for a **different hand**. The author (a synthetic
AI agent, via Claude Opus 5.5) does not choose the blind seed, never generates or looks at a blind corpus,
and does not run anything below.

**Updated after the tag `v2.0.4-freeze`.** The blind runs so far, all recorded in `eval/history.json`:

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

The change of `v2.0.4` (finding D30b, from run 11) changed code, rules, tests and the scorer - not only
documentation. `OWN-015` and `unverified_holders_table` keep the value `block` (D26).

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
`CHANGELOG.md` (entry 2.0.4) lists every known limit with what it does; one of them may publish and is not
fixed (section 4).

The change of `v2.0.3` (owner decision D30 of 2026-10-01), kept in `v2.0.4` except where the list above says
otherwise:

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

This protocol now applies to `v2.0.4-freeze`; besides the names of the tag, it changes section 0 (seed
20261014 and the wordings of run 11 are known), section 1.6 (the counts of the entities not published,
reported next to the never-events), section 4 (the classes `v2.0.4` claims, the complete list of its known
limits, adversarial documents, at least six entities and twenty documents) and sections 5 and 6. The earlier
tags are not moved and their blind runs are not repeated.

## 0. What is frozen

| | |
|---|---|
| Tag | `v2.0.4-freeze` (annotated), created at 2026-10-01T01:23:24Z |
| Tag object | `66f116539d7421b95d124b94a32d4e8bbc92ba9e` |
| Commit | `65b02335fb718ed061d3c9e665e26db97accc9ef` |
| Frozen files | the 172 files listed in `MANIFEST.sha256` (code, rules, schema, corpus generator, scenarios, tests, tools, scorer, requirements) |
| Not frozen | `README.md`, `CLAIMS.md`, `CHANGELOG.md`, `MODEL.md`, `eval/history.json`, `eval/blind/`, this file |
| Previous tag | `v2.0.3-freeze`, tag object `ae66f49debcb1bb15e83e1827acda35b03c4a3a6`, commit `77e7736f573c93024f0aa49157f5949287bee698`: run blind once (run 11), not passed - 2 never-events on hand-written entity E-0015, 8 of 15 hand-written entities blocked wrongly |
| Tag before it | `v2.0.2-freeze`, tag object `475bd994bbd063c4dc7cebb15f50e7b9474ebd58`, commit `023c7cb5629b17295b4ddbbfeb22055a2be16b87`: run blind once (run 9), 0 never-events, 4 of 9 hand-written entities blocked wrongly |
| Earlier tag | `v2.0.1-freeze`, tag object `91cba79b5671a9f273a7ecf268dc92ffa8679a23`, commit `b65e45a5289133375222fa595abdbd9cd2087be7`: run blind once (run 7), 0 never-events, 89 of 150 perturbed entities blocked wrongly |
| First tag | `v2.0.0-freeze`, tag object `0c26555916701c4a81ea6490c32d5e7162edcdc8`, commit `d1769d555934ca5eaf4717bafe8135105caffd43`: run blind once (run 5), not passed |

Seeds already used, which therefore cannot be the blind seed: 20260930 (development, inspected),
20261001 (holdout, scored seven times, never inspected), 20261002 (stress, inspected), 20261011 (the blind
seed of `v2.0.0-freeze`: its plain, perturbed and out-of-pool corpora were read by the hand that wrote the
fix and scored again in runs 6, 8, 10 and 12), 20261012 (the blind seed of `v2.0.1-freeze`: its plain and
perturbed corpora were generated, read and scored again by the hand that wrote `v2.0.2`, runs 8, 10 and 12),
20261013 (the blind seed of `v2.0.2-freeze`: its plain and perturbed corpora were generated, read and scored
again by the hand that wrote `v2.0.3`, runs 10 and 12), 20261014 (the blind seed of `v2.0.3-freeze`: its
plain and perturbed corpora were generated again from the recorded seed, read and scored by the hand that
wrote `v2.0.4`, run 12). For the same reason these wordings are known to `v2.0.4` and are no longer out of
pool - a new run needs other wordings:

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
- every example of `CHANGELOG.md` (sections 2.0.2, 2.0.3 and 2.0.4) and of this protocol.

## 1. Rules of the run

1. The runner is not the author and chooses `<SEED>`: any integer other than the seeds of section 0, not
   told to the author before the run.
2. Each command of sections 3 and 4 is run **once**. There is no second attempt, whatever the result.
3. No frozen file is changed before or during the run. Section 2 proves it.
4. The outcome is recorded verbatim in `eval/history.json` (section 5), good or bad, with the name of who ran it.
5. The only pass or fail criterion, declared here before any blind run: **`never_events` is 0** in every
   result (the scorer exits with code 0; it exits with code 1 when there is at least one never-event).
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
   metrics of each JSON file). They are not never-events. Every time in the record is UTC, written
   `YYYY-MM-DDTHH:MM:SSZ` (for example `2026-10-01T01:09:07Z`), never in local time.
   More abstention, more wrong blocks and lower recall than on the development suite are expected, above
   all in sections 3b and 4: the rules read some wordings and write `[TO CONFIRM]` for what they do not
   read. That is reported as it comes out.
7. If a never-event appears: it is recorded, the affected claims are downgraded in `CLAIMS.md`, and the
   fix goes into a new version under a new tag. The freeze tag is never moved and the run is never repeated
   on the fixed code under the name "blind".

## 2. Before the run: prove that the frozen files are the tagged ones

    git rev-parse "v2.0.4-freeze^{commit}"
    git diff --stat v2.0.4-freeze -- corpus dossier rules schema scenarios tests tools eval/__init__.py eval/score.py requirements.txt MANIFEST.sha256 docs
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

For `v2.0.4-freeze` the runner writes **at least six entities and at least twenty documents**, with the
**holders' tables** in **forms of its own choosing** - the heading, the holder lines, the form of the shares
and the type of the document that carries the table - not copied from the scenarios, from the hand-written
documents of runs 7, 9 and 11 (`eval/blind/hand/`, `eval/blind/hand-9/`, `eval/blind/hand-11/`), from the
texts of the tests or from the examples of this protocol and of `CHANGELOG.md`: `v2.0.4` was written after
seeing those, and only forms it has not seen measure it. Some of the forms should fall **inside** the classes
`v2.0.4` claims to read, worded in ways it has not seen, and some **outside** them.

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

Known limits of `v2.0.4`, the complete list of `CHANGELOG.md` (entry 2.0.4), each marked with what it does to
the entity - **blocks**, **keeps `[TO CONFIRM]`** or **may publish**:

- holders stated in a sentence rather than in a list under a heading - **blocks**;
- a qualifier meaning "current" in free words in the heading (`... once the transfer has taken effect:`) -
  **blocks**;
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
  `every_field`); the word lists of `unread_fields` decide nothing under the default - **keeps
  `[TO CONFIRM]`**;
- **a document of a recognised type is read for the fields of its kind only** (`rules/extract.json`
  `doc_kinds`, `expected_fields`): a recognised document whose text also changes another field - a capital
  resolution whose new quotas go to a new holder, a transfer notice that also moves the seat, a resolution
  that holds a holders' table - is not searched for it, and the older value of that field is published as a
  fact - **may publish**. Declared, not fixed in `v2.0.4`.

The runner is asked in particular for:

- **adversarial documents of unrecognised type** (a document type the scenarios do not use) whose **title
  line uses the pack's own list words** - the title nouns of rule `FEV-920` in `rules/extract.json`
  (minutes, notice, entries, entry, register, ledger, statement, certificate, memorandum, summary, record, report,
  letter, declaration), marked `(synthetic)` - **and** whose body has **sentences that change a field without
  naming it** (the capital doubled without the word capital, a holder replaced without the words holder,
  share or quota, the seat moved without the word office); in the gold every field such a document may change
  is `TO_CONFIRM`;
- documents of recognised types whose text also changes a field of another kind (the limit that may
  publish), if the runner chooses to test it;
- holders' tables inside and outside the claimed classes, in at least six entities and twenty documents.

With the never-events of this part, report the entities blocked wrongly, the fields left `[TO CONFIRM]` and
the four counts of the entities not published (rule 1.6), every time as `YYYY-MM-DDTHH:MM:SSZ`.

In the gold, a holders' table the runner means to be readable is written as a fact, so that a
wrong block shows, and a field an unread document may change is written `TO_CONFIRM`, so that a fact shown
against it is a never-event.
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
and commit it. Nothing already in the list is edited. The entry `blind` of the same file records the
blind run of `v2.0.0-freeze` and is not edited either: the run of `v2.0.4-freeze` is recorded in `runs`,
as the runs of `v2.0.1-freeze`, `v2.0.2-freeze` and `v2.0.3-freeze` were (runs 7, 9 and 11), with `code`
naming the tag and `run_by` naming the runner.

    {
      "n": <previous + 1>,
      "date": "<YYYY-MM-DD of the run>",
      "run_by": "<name of who ran it - not the author>",
      "code": "tag v2.0.4-freeze, commit 65b0233",
      "command": "<the commands of sections 3 and 4, exactly as typed, seed included>",
      "note": "<exit code and UTC start and end (YYYY-MM-DDTHH:MM:SSZ) of each command; for each result the never-events, the entities blocked wrongly, the fields left [TO CONFIRM] and the four counts of the entities not published; who chose the seed and who wrote the hand documents; which forms were meant inside and which outside the claimed classes; anything that went wrong>",
      "results": [ <the objects of the "results" lists of the three JSON files, verbatim, in order 3a, 3b, 4> ]
    }

The hand-written documents and their gold are committed next to the record, in a new folder
`eval/blind/hand-<n>/` named after the number of the run (the folders `eval/blind/hand/`,
`eval/blind/hand-9/` and `eval/blind/hand-11/` hold those of runs 7, 9 and 11 and are not edited), so that the run can be repeated by anyone. `python -m unittest discover -s tests -t .`
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
- Not verified: any seed other than the seven named in section 0; any hand-written document other than
  the scenario inputs and those of runs 7, 9 and 11; a hand-written gold with a cycle; a rule for the limit
  that may publish (a recognised document with a line no rule reads), which is not written; any operating
  system other than Windows.
