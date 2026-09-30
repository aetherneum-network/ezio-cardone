# Blind protocol

SYNTHETIC - this protocol measures a test pipeline on invented documents. It measures internal consistency
on synthetic data, never accuracy on real companies. Nothing real may be used as input.

Written after the freeze tag, by the author of the pack, for a **different hand**. The author (a synthetic
AI agent, via Claude Opus 5.5) does not choose the blind seed, never generates or looks at a blind corpus,
and does not run anything below.

## 0. What is frozen

| | |
|---|---|
| Tag | `v2.0.0-freeze` (annotated), created on 2026-09-30 |
| Tag object | `0c26555916701c4a81ea6490c32d5e7162edcdc8` |
| Commit | `d1769d555934ca5eaf4717bafe8135105caffd43` |
| Frozen files | the 168 files listed in `MANIFEST.sha256` (code, rules, schema, corpus generator, scenarios, tests, tools, scorer, requirements) |
| Not frozen | `README.md`, `CLAIMS.md`, `CHANGELOG.md`, `eval/history.json`, this file |

Seeds already used by the author, which therefore cannot be the blind seed: 20260930 (development,
inspected), 20261001 (holdout, scored three times, never inspected), 20261002 (stress, inspected).

## 1. Rules of the run

1. The runner is not the author and chooses `<SEED>`: any integer other than the three above, not told to
   the author before the run.
2. Each command of sections 3 and 4 is run **once**. There is no second attempt, whatever the result.
3. No frozen file is changed before or during the run. Section 2 proves it.
4. The outcome is recorded verbatim in `eval/history.json` (section 5), good or bad, with the name of who ran it.
5. The only pass or fail criterion, declared here before any blind run: **`never_events` is 0** in every
   result (the scorer exits with code 0; it exits with code 1 when there is at least one never-event).
   A never-event is a figure rendered as fact that differs from the gold or has no source; it includes a
   planted conflict shown with one value only and a cap table rendered with a sum other than 100%.
6. Everything else is reported, not judged: conflicts found (recall) and conflicts reported that are real
   (precision), exact facts, and the abstention rate next to them. More abstention and lower recall than
   on the development suite are expected, above all in sections 3b and 4: the rules read one wording and
   write `[TO CONFIRM]` for what they do not read. That is reported as it comes out.
7. If a never-event appears: it is recorded, the affected claims are downgraded in `CLAIMS.md`, and the
   fix goes into a new version under a new tag. The freeze tag is never moved and the run is never repeated
   on the fixed code under the name "blind".

## 2. Before the run: prove that the frozen files are the tagged ones

    git rev-parse "v2.0.0-freeze^{commit}"
    git diff --stat v2.0.0-freeze -- corpus dossier rules schema scenarios tests tools eval/__init__.py eval/score.py requirements.txt MANIFEST.sha256 docs
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
followed by one `NEVER-EVENT:` line per never-event (first ten). Note the exit code of each command.

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
and commit it. Nothing already in the list is edited. In the same file, the entry `blind` gets
`"status": "run"` with the name of the runner and the date.

    {
      "n": <previous + 1>,
      "date": "<YYYY-MM-DD of the run>",
      "run_by": "<name of who ran it - not the author>",
      "code": "tag v2.0.0-freeze, commit d1769d5",
      "command": "<the commands of sections 3 and 4, exactly as typed, seed included>",
      "note": "<exit code of each command; who chose the seed and who wrote the ten documents; anything that went wrong>",
      "results": [ <the objects of the "results" lists of the three JSON files, verbatim, in order 3a, 3b, 4> ]
    }

The ten hand-written documents and their gold are committed next to the record, under
`eval/blind/hand/`, so that the run can be repeated by anyone. `python -m unittest discover -s tests -t .`
must still pass after the commit (the record must keep runs 1-4 untouched).

## 6. What the author verified about this protocol, and what not

- Verified on 2026-09-30, on the frozen code, with the **development** seed only: the `--seed` path
  (`--seed 20260930`) and the `--corpus ... --gold ...` path (on the generated development corpus) both give
  the numbers of the development suite (run 4 of `eval/history.json`).
- Verified on 2026-09-30 as well: a gold written by hand in the form of section 4 for the two documents of
  scenario S01 (already known to the author) is accepted by the scorer and scored
  (`never_events=0`, conflicts 3/3 and 3/3, facts 5/5, abstained 0/8).
- Not verified: any seed other than the three named in section 0; any hand-written document other than
  the scenario inputs; a hand-written gold with a blocked cap table, a cycle or a file-name divergence;
  any operating system other than Windows.
