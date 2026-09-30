# Blind protocol

SYNTHETIC - this protocol measures a test pipeline on invented documents. It measures internal consistency
on synthetic data, never accuracy on real companies. Nothing real may be used as input.

Written after the freeze tag, by the author of the pack, for a **different hand**. The author (a synthetic
AI agent, via Claude Opus 5.5) does not choose the blind seed, never generates or looks at a blind corpus,
and does not run anything below.

**Updated after the tag `v2.0.2-freeze`.** The blind runs so far, both recorded in `eval/history.json`:

- `v2.0.0-freeze`: run once, by the evaluator, on 2026-09-30 (run 5, seed 20261011). Not passed: 13
  never-events (0 plain, 1 perturbed, 12 out-of-pool). Its fix (finding T16, `v2.0.1`) changed code, rules
  and tests: amounts grouped by an apostrophe or a space are read whole or abstained; the audit compares the
  digits of a quote; new rule `OWN-015` - a holders' table that could not be read blocks the entity
  (parameter `unverified_holders_table`, `[TO CONFIRM with legal]`).
- `v2.0.1-freeze`: run once, by the evaluator, on 2026-09-30 (run 7, seed 20261012). 0 never-events on every
  corpus. But `OWN-015` blocked entities that the gold builds: 89 of 150 in the perturbed corpus (3 of 150 in
  the plain corpus, 0 of 2 in the hand-written one), most of them because their holders' table was worded
  in a form the rules did not read.

The change of `v2.0.2` (owner decisions D26 and D29 of 2026-09-30) changed code, rules and tests - not only
documentation:

- `rules/ownership.json`: `OWN-015` and `unverified_holders_table` keep the value `block` (D26): a holders'
  table that is not read and verified still blocks the entity. Only the note of the parameter changed.
- `rules/extract.json`: the heading of the holders' table (`EXT-HOLD-010`) is a grammar (new parameter
  `holders_heading`): a holder noun (holders, shareholders, stockholders, quotaholders, members, partners),
  an optional clause number, an optional qualifier that means "current" (after or following the transfer,
  as at the document date, now, at present). A qualifier not known to mean "current" is not a heading, and
  two holders' headings in one document abstain (before, the first was taken). New ordered group
  `holders_evidence` (`HEV-010` to `HEV-080`, default `HEV-999`): the forms of a line that may state a
  holding.
- `dossier/s1_extract.py`: a document whose only header problem is an unrecognised type is checked for
  holders (`holders_check`): `read` when every table under a holders' heading is read whole, `no_table`
  when there is no table and no line of evidence, `not_read` otherwise. The document still gives no fact
  (`DISC-005`).
- `dossier/s4_ownership.py`: a document checked `no_table` or `read` is no longer an unread holders' table;
  the tables of a `read` document are summed with the others, and one that does not sum blocks (`OWN-010`).
  `schema/entity_record.schema.json`: optional `holders_check` on a problem document.
- `eval/score.py`: no change of behaviour. Its docstring lists the eight kinds of never-event the code
  counts; since D29 that list is the definition of section 1.5 below (before, section 1.5 gave a narrower
  definition, contained in it).
- Tests: `tests/test_holders_forms.py` (25 tests), four scorer tests, one documentation test, two older
  tests moved to the new behaviour (209 tests in all).

The change was written by the builder's hand after reading the results of run 7, and measured only on
corpora already seen (run 8, not blind). This protocol now applies to `v2.0.2-freeze`; besides the names of
the tag, it changes section 1.5 (the definition of a never-event, D29), section 1.6 and section 4 (holders'
tables in forms of the runner's choosing, wrongly blocked entities reported). The earlier tags are not moved
and their blind runs are not repeated.

## 0. What is frozen

| | |
|---|---|
| Tag | `v2.0.2-freeze` (annotated), created on 2026-09-30 |
| Tag object | `475bd994bbd063c4dc7cebb15f50e7b9474ebd58` |
| Commit | `023c7cb5629b17295b4ddbbfeb22055a2be16b87` |
| Frozen files | the 170 files listed in `MANIFEST.sha256` (code, rules, schema, corpus generator, scenarios, tests, tools, scorer, requirements) |
| Not frozen | `README.md`, `CLAIMS.md`, `CHANGELOG.md`, `MODEL.md`, `eval/history.json`, `eval/blind/`, this file |
| Previous tag | `v2.0.1-freeze`, tag object `91cba79b5671a9f273a7ecf268dc92ffa8679a23`, commit `b65e45a5289133375222fa595abdbd9cd2087be7`: run blind once (run 7), 0 never-events, 89 of 150 perturbed entities blocked wrongly |
| Tag before it | `v2.0.0-freeze`, tag object `0c26555916701c4a81ea6490c32d5e7162edcdc8`, commit `d1769d555934ca5eaf4717bafe8135105caffd43`: run blind once (run 5), not passed |

Seeds already used, which therefore cannot be the blind seed: 20260930 (development, inspected),
20261001 (holdout, scored five times, never inspected), 20261002 (stress, inspected), 20261011 (the blind
seed of `v2.0.0-freeze`: its plain, perturbed and out-of-pool corpora were read by the hand that wrote the
fix and scored again in runs 6 and 8), 20261012 (the blind seed of `v2.0.1-freeze`: its plain and perturbed
corpora were generated, read and scored again by the hand that wrote `v2.0.2`, run 8). For the same reason
the wordings of the out-of-pool rewrite of run 5 and of the ten hand-written documents of run 7
(`eval/blind/hand/`) are known to `v2.0.2` and are no longer out of pool: a new run needs other wordings.

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
   holders' table it does not read. More abstention, more wrong blocks and lower recall than on the
   development suite are expected, above all in sections 3b and 4: the rules read some wordings and write
   `[TO CONFIRM]` for what they do not read. That is reported as it comes out.
7. If a never-event appears: it is recorded, the affected claims are downgraded in `CLAIMS.md`, and the
   fix goes into a new version under a new tag. The freeze tag is never moved and the run is never repeated
   on the fixed code under the name "blind".

## 2. Before the run: prove that the frozen files are the tagged ones

    git rev-parse "v2.0.2-freeze^{commit}"
    git diff --stat v2.0.2-freeze -- corpus dossier rules schema scenarios tests tools eval/__init__.py eval/score.py requirements.txt MANIFEST.sha256 docs
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
followed by one `NEVER-EVENT:` line per never-event (first ten). Note the exit code of each command, and
the counts `published` and `blocked_wrongly` of each JSON file (rule 1.6).

What 3a can and cannot show: it uses the same generator and the same templates as the development suite,
so a clean result is expected and says little. 3b and section 4 are the informative parts.

## 4. Hand-written documents (the part the generator cannot influence)

The runner writes **ten source documents of two new invented entities** by hand, and writes the gold by
hand **before** running anything, from what the documents are meant to say - never from an output.

Input folder:

    <DIR>/input/config.json                      {"as_of": "YYYY-MM-DD", "shareable_salt": "any-text", "synthetic": true}
    <DIR>/input/identity/persons.json            {"P-001": {"name": "...", "born": "YYYY-MM-DD", "email": "...@persons.example", "tax_code": "SYN-CF-P001"}, ...}
    <DIR>/input/entities/E-0001/<date>_<slug>.txt
    <DIR>/input/entities/E-0002/<date>_<slug>.txt
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

For `v2.0.2-freeze` the runner is asked in particular to write the **holders' tables** of its documents in
**forms of its own choosing** - the heading, the holder lines, the form of the shares and the type of the
document that carries the table - not copied from the scenarios, from the hand-written documents of run 7
(`eval/blind/hand/`) or from the examples of this protocol and of `CHANGELOG.md`. `v2.0.2` was written to
read more forms of that table after seeing those, and only forms it has not seen measure it. With the
never-events of this part, report the entities blocked wrongly (rule 1.6); in the gold, a holders' table
the runner means to be readable is written as a fact, so that a wrong block shows.
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
blind run of `v2.0.0-freeze` and is not edited either: the run of `v2.0.2-freeze` is recorded in `runs`,
as the run of `v2.0.1-freeze` was (run 7), with `code` naming the tag and `run_by` naming the runner.

    {
      "n": <previous + 1>,
      "date": "<YYYY-MM-DD of the run>",
      "run_by": "<name of who ran it - not the author>",
      "code": "tag v2.0.2-freeze, commit 023c7cb",
      "command": "<the commands of sections 3 and 4, exactly as typed, seed included>",
      "note": "<exit code of each command; never-events and entities blocked wrongly of each result; who chose the seed and who wrote the ten documents; anything that went wrong>",
      "results": [ <the objects of the "results" lists of the three JSON files, verbatim, in order 3a, 3b, 4> ]
    }

The ten hand-written documents and their gold are committed next to the record, in a new folder
`eval/blind/hand-<n>/` named after the number of the run (the folder `eval/blind/hand/` holds those of
run 7 and is not edited), so that the run can be repeated by anyone. `python -m unittest discover -s tests -t .`
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
- Not verified: any seed other than the five named in section 0; any hand-written document other than
  the scenario inputs and those of run 7; a hand-written gold with a cycle; any operating system other
  than Windows.
