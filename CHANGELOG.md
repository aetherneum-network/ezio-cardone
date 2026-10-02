# Changelog

SYNTHETIC - proof pack of a synthetic AI agent; every entity, person, deed and registry extract is invented.

## [2.0.12] - 2026-10-02 (freeze tag `v2.0.12-freeze`; how the test suite runs, and documents)

How nine test files run their cases, and documents. No code, rule, schema, corpus generator, scenario or tool
changed, and no test checks anything else than before: the same 364 tests, the same assertions on the same cases,
read in the same order. The version string of the generator stays `dossier 2.0.10`, so the rebuild hashes of the
README do not change. `MANIFEST.sha256` is rewritten, because the test files are in the frozen part of the pack:
nine entries change (`tests/support.py` and the eight files of section 3), no file is added or removed.
`eval/history.json`, `eval/BLIND_PROTOCOL.md` and `eval/blind/` are unchanged. Not run blind; no outcome changes.

### 1. The first complete Windows runs

On commit `44554c0` (`v2.0.11-freeze`, the code of v2.0.10), runs 37019779358 (push) and 37019787788 (pull
request), read on 2026-10-02:

| Job | Image, CPython | Test suite (`Ran ... in`) | Scenarios | Rebuild | Job |
|---|---|---|---|---|---|
| `windows-latest` | windows-2025-vs2026, 3.12.10 | 364 tests OK in 1266.1 s and 1310.4 s | 10/10 PASS | `REBUILD OK`, the four SHA-256 values of the README | 29.5 and 30.3 min |
| `ubuntu-latest` | ubuntu-24.04, 3.12.14 | 364 tests OK in 861.1 s and 865.8 s | 10/10 PASS | `REBUILD OK`, the same four values | 18.4 and 18.5 min |

This is the measurement that 2.0.11 section 2 left `[TO CONFIRM]`: the estimate of 21 to 30 minutes held at its
upper end (30.3 minutes in one run, a little above it). The other steps of the Windows job took about 470 s in both
runs (scenarios 12 and 20 s, development evaluation 149 and 143 s, rebuild 287 and 286 s). The Ubuntu suite took
446.2 s on commit `4c76f8f` (run 37013193685) and 861.1 s on `44554c0` with the same code and tests: the hardware
behind one runner label differs from run to run by up to about two times, so single runs compare versions roughly.
On the same runs the Windows suite took about 1.5 times the Ubuntu one.

### 2. Where the time of the suite goes

Measured on Windows 11 (CPython 3.12.10, 24 logical CPUs), 2026-10-02, by the builder: each tag in a fresh
checkout, each run with an empty temporary folder of its own, one run after the other, the time of every test
recorded:

| Code | Tests | Suite | Pipeline runs in the test process | Their share | Sweeps of siblings |
|---|---|---|---|---|---|
| `v2.0.3-freeze` | 243 | 64.0 s | 118 | 56 % | none |
| `v2.0.7-freeze` | 300 | 352.8 s | 1545 | 87 % | 4 tests, 256.7 s |
| `v2.0.11-freeze` | 364 | 790.6 s | 2983 | 87 % | 7 tests, 599.8 s |

- **The number of runs, not their cost.** One run of the pipeline on a two-document input took 220 ms on v2.0.3
  and 254 ms on v2.0.7 and v2.0.11 (the two DOCX layers 144 to 148 ms of it; the inline tests of the rules, run
  before every run, 4 ms then 33 to 37 ms). A run costs 15 % more than on v2.0.3; the suite makes 25 times as many.
- **The sweeps of siblings.** Since v2.0.5 a finding is probed by class: a test builds every combination of its
  axes (wording x slot x place x sources, up to 624 cases) and runs the whole pipeline once per case - DOCX of both
  layers, audit, snapshot store - because the property under test is what is published. Seven such tests took
  599.8 s, 76 % of the v2.0.11 suite: `tests/test_d36_forms.py` 139.3 s (600 runs),
  `tests/test_d37_forms.py` 120.7 s (420), `tests/test_d38_identification.py` 120.5 s (624),
  `tests/test_d37_slots.py` 86.0 s (300), `tests/test_d34_forms.py` 74.3 s (379), `tests/test_d35_forms.py`
  31.2 s (192), `tests/test_d30b_forms.py` 27.7 s (160). The rest of the suite, 64 tests more than v2.0.7, took
  190.8 s (96.1 s on v2.0.7), 42.0 s of it in class and module set-up.
- **Not the cause.** Child processes: 29 in every version, 21 to 25 s. Fixtures: the corpora and builds that many
  tests share are already built once per process. The antivirus does not explain the CI times: the Windows runner
  image turns real-time monitoring off and excludes its drives from scanning (runner-images,
  `Configure-WindowsDefender.ps1`).

### 3. The sweeps run their cases in worker processes

The cases of a sweep are independent of one another. `tests/support.py` gains `sweep(fn, cases)`: one future per
case, `fn` run in a pool of worker processes started clean (`spawn`, on every system), and the test reads each
outcome inside that case's own `subTest`, with the same assertion as before; an exception raised by a case is raised
where the test reads it, inside its `subTest`, as a call there would. A worker that dies breaks the pool: every case
not yet finished fails with that error, and so does every later sweep; none passes. Workers: `EZIO_TEST_JOBS` when
it is set, else the CPU count, at most 8; `EZIO_TEST_JOBS=1` runs every case in the test process at the moment the
test reads it, as until v2.0.11. A worker removes the temporary folders it made when it ends, as the test process
does. The tests that use it: the seven sweeps of section 2 and the 78 setups of `tests/test_d39_capital_count.py`,
built in that class's set-up. The command is unchanged: `python -m unittest discover -s tests -t .`.

### 4. Before and after, measured

Same machine, same method as section 2 (per-test times, an empty temporary folder per run):

| Code | Sweep workers | Suite | The seven sweeps | The rest |
|---|---|---|---|---|
| `v2.0.11-freeze` | none (one process) | 790.6 s | 599.8 s | 190.8 s |
| v2.0.12 | 4 | 322.2 s | 146.0 s | 176.2 s |
| v2.0.12 | 8 | 257.1 s | 83.9 s | 173.2 s |

The CI command itself on the commit of `v2.0.12-freeze`, same machine, 364 tests OK every time, no temporary
folder left behind: 263.0 s with the default (8 workers here), 316.2 s with `EZIO_TEST_JOBS=4`, 738.6 s with
`EZIO_TEST_JOBS=1` (every case in the test process, as until v2.0.11).

What it does not change: the rest of the suite stays in one process, and the CI job keeps its other steps (about
470 s on Windows, section 1). GitHub documents 4 CPUs for the standard runners of a public repository; if a
Windows runner scaled as this machine did with 4 workers, its suite would take about 515 to 535 s instead of 1266
to 1310 s and the job about 17 minutes. That is an estimate: the first Windows run on this code is
`[TO CONFIRM]`, and `timeout-minutes` stays 60 until it is read.

## [2.0.11] - 2026-10-02 (freeze tag `v2.0.11-freeze`; documentation and the CI time limit only)

Documentation and one value of the CI workflow only. No code, rule, schema, corpus generator, scenario, test or
tool changed: `python tools/manifest.py --check` answers OK against the `MANIFEST.sha256` of `v2.0.10-freeze`,
which is unchanged, and `v2.0.10-freeze` stays where it is. The version string of the generator stays
`dossier 2.0.10`, because it lives in a frozen file, so the rebuild hashes of the README do not change.
`eval/history.json`, `eval/BLIND_PROTOCOL.md` and `eval/blind/` are unchanged; the blind run of
`v2.0.10-freeze` (run 24) measured the same code.

### 1. The workflow has run

Published on 2026-10-02 as pull request #2 of this repository; the workflow runs on GitHub-hosted runners. The
statements written before that - the comment at the top of `.github/workflows/ci.yml` (never executed, the branch
not pushed) and the last paragraph of "Two rebuilds, same bytes" in the README - now state the runs. The lines of
entry 2.0.0 on the workflow ("written, never executed"; "The CI workflow has never been executed") described that
version and stay as written.

- `ubuntu-latest`, run 37013193685 (push, commit `4c76f8f`, ubuntu-24.04, CPython 3.12.14): 364 tests OK in
  446.2 s, scenarios 10/10 PASS, development evaluation with 0 never-events, `REBUILD OK`, and the four SHA-256
  values of the README table (measured on Windows 11 on 2026-10-01) printed identical. One Linux runner agreeing
  with one Windows machine: `CLAIMS.md` row "Deterministic document build" keeps "demonstrated on Windows only"
  and records the observation; `CLAIMS.md` section 13 says what v2.0.11 changes.
- `windows-latest`: cancelled at the time limit of 20 minutes in all six runs on the code of v2.0.10 (section 2),
  so no Windows runner has reached the rebuild step on that code yet.

### 2. The time limit of the Windows job: 20 -> 60 minutes

From the step times GitHub records for each job, read on 2026-10-02 (`windows-latest`: Windows Server 2025,
CPython 3.12.10). The runs of the tags were made on the tag commits before the history rewrite of 2 October 2026
(trees unchanged). Test-suite times are whole seconds of the step, or the `Ran ... in` line where given with a
decimal.

| Code | Run | Test suite on Windows | Windows job | Ubuntu job |
|---|---|---|---|---|
| `v2.0.3-freeze` | 36996964701 | 90 s | 5.0 min, passed | 2.4 min, passed |
| `v2.0.4-freeze` | 36996965487 | 114 s | 4.3 min, passed | 3.9 min, passed |
| `v2.0.5-freeze` | 36996967478 | 264 s | 8.1 min, passed | 5.3 min, passed |
| `v2.0.6-freeze` | 36996970012 | 235 s | 7.9 min, passed | 3.5 min, passed |
| `v2.0.7-freeze` | 36996972750 | 583 s | 15.3 min, passed | 9.6 min, passed |
| `v2.0.8-freeze` | 36996975407 | 852 s | cancelled at 20.1 min, in the rebuild step | 15.0 min, passed |
| `v2.0.9-freeze` | 36996977933 | 994 s | cancelled at 20.1 min, in the rebuild step | 11.1 min, 1 test failed (`tests/test_d38_identification.py`) |
| code of v2.0.10 | 36996964682, 36996984610, 37006469796, 37006476834, 37013193685, 37013199770 | 1056.7 s and 1157.8 s where it finished; still running at about 1190 s in four jobs | cancelled at 20.1 to 20.3 min | 10.0 to 18.6 min, passed |

- **Where the time goes: the test suite.** The other steps of the Windows job took at most about 400 s on the
  earlier versions: setup and install up to 25 s, about 20 to 31 s between the `OK` of the suite and the next
  step, scenarios up to 12 s, development evaluation up to 130 s, rebuild up to 201 s.
- **The four jobs cancelled inside the suite** were in `tests/test_d39_scorer.py` (three) and
  `tests/test_scenarios.py` (one). By per-test times measured on Windows 11 on 2026-10-02 (364 tests OK in
  843.2 s; used for proportions only, the machine was running other work), those tests start at 84 and 92 percent
  of the suite, so the suite would have taken about 1300 to 1420 s on those runners. Five sibling tests
  (`tests/test_d34_forms.py`, `tests/test_d36_forms.py`, `tests/test_d37_forms.py`, `tests/test_d37_slots.py`,
  `tests/test_d38_identification.py`) take 576 s of the 843 s there.
- **Estimate and limit.** On the code of v2.0.10 the Windows job needs about 21 to 30 minutes. `timeout-minutes`
  is now 60, about twice the upper estimate. No test is disabled and Windows stays in the matrix. The first
  Windows job that completes on this code is the measurement of this estimate: until then it is `[TO CONFIRM]`.
- The `v2.0.9-freeze` failure on Ubuntu (`D38_OwnNameStreetWord`) is recorded here as found; it was not examined
  in this version `[TO CONFIRM]`. The code of v2.0.10 passed on Ubuntu in all six runs.

Still `[TO CONFIRM]`: the commit digests of the two actions and the runner image digests.

## [2.0.10] - 2026-10-01 (freeze tag `v2.0.10-freeze`; not yet run blind)

### D39 - blind run of v2.0.9, run 22: no never-event; a measurement that does not fail, the count form of the capital, a declaration not true as written and a block not declared, the test suite

Source: the evaluator's blind run of `v2.0.9-freeze`, `eval/history.json` run 22, seed 20261019 and the hand
corpus `eval/blind/hand-22/` (42 entities, 100 documents): 0 never-events in the plain, the perturbed and the
hand-written corpus, every probe unmasked. The run found four defects, none of which publishes: D1, in a work folder
of 282 characters `eval/score.py` read the build by plain path, counted every built entity failed and 0 fields,
and exited 0 with an empty stderr; D2, the count form "EUR 20.000,00, divided into 2.000 quotas, fully subscribed
and fully paid in" left the subscribed and the paid-in capital `[TO CONFIRM]` (E-0007); D3, the sentence of entry
2.0.9 on an address "with a name the corpus knows inside it" is not what the code does (E-0033); D4, the holder row
`- Name [P-015]: 60%` blocks without being declared (E-0006). The fixer of v2.0.9 left three findings on the test
suite: a docstring that names the wrong entity, temporary folders never removed, and a failure that comes and goes.
Fixed by the builder's hand in this order: (a) first - the scorer -, then (b) the count form, (c) the
declarations, (d) the test suite; (e) the two flags of the measurer change nothing in the pack. `OWN-015` stays
`block` (D26), holders in a sentence stay unread (D31), `DISC-005` stays `every_field`, `DISC-006`, `CLS-005`,
`DISC-035` and `DISC-038` stay; whatever v2.0.9 decides by positive identification (the gazetteer, `IDN-010` to
`IDN-999`, `NAM-005`, `TXT-005`, `TXT-020`) is exactly as strict. Measured on corpora already seen only
(`eval/history.json` run 23): not blind; seed 20261019 and hand-22 are now seen.

#### 1. (a) The scorer reads where the pipeline writes, and a measurement that did not measure fails

Since v2.0.9 the pipeline derives every path of a build from the work folder with the extended-length prefix
(`dossier/run.py` line 63, `jsonio.ext`); the scorer did not. Now:

- `eval/score.py`: `score()` takes the prefix on the work folder (line 121) and reads every provenance file through
  `_read` (line 108), which returns the reason of a failed read instead of a quiet absence; `evaluate()` takes it
  on the base folder, the generated corpus and a given corpus (lines 311-317), and reads the gold through
  `jsonio.read_text`.
- `score()` returns `measurement` (line 303): `OK`, or `FAILED` with its problems (lines 258-278) when an entity the
  run reports as built (status OK) cannot be read; when the run's counts differ from its own list of entities;
  when the number of built entities read differs from the run's count; when the run built entities and no field
  was scored; when an entity of the gold is not in the run.
- `main()` exits **3** (`MEASUREMENT_FAILED`, line 105) when any result is FAILED, and says each problem on stderr
  (`MEASUREMENT FAILED - <label>: ...`) and on stdout; the JSON is still written, with the problems in it. A run
  that raises (no run report, a folder that cannot be written) is exit 3 with its reason (line 370), not a
  traceback. 3 wins over 1 (a never-event); 0 means measured, with no never-event.
- The same pattern elsewhere, fixed: `tools/rebuild.py` walks a build by the prefix and raises `NothingRead` when a
  walk reads no file (lines 28-39; under a deep TEMP two empty walks were "identical"); `scenarios/_common.py`
  `workdir` (line 38: under a deep TEMP the checks "no DOCX written" and "not published" of S02 were made true by
  not reading); `tools/manifest.py` (line 25: `is_file()` False on a long path would have dropped files from the
  manifest on `--write`). Not changed: `tools/assumptions.py` and the `--check` of `scenarios/make_inputs.py` read
  files of the repository by plain path, which fails loudly (an exception), never quietly.

Measured (hand-22, `--work` folder of 282 characters, same machine, no long-path support): the code of
`v2.0.9-freeze` exits 0 with an empty stderr, fields exact 0/0, fields abstained 0/0, 31 built entities counted
failed; this code exits 0 with the numbers of the short folder (78/223 exact, 145/251 abstained, 430/430 figures
with source) and `measurement` OK. An entity whose `provenance.json` is removed after the build: `v2.0.9-freeze`
exits 0 and scores 30 entities as if the 31st had failed (70/215 exact); this code exits 3, stderr "1 entities the
run reports as built (status OK) cannot be read: E-0001 (no file)" and "the scorer read 30 built entities, the
run counts 31". A folder in place of that file: `v2.0.9-freeze` ends with a traceback (exit 1); this code exits 3.

#### 2. (b) The count form of the capital clause: `NAT-025`

`rules/figure_nature.json` `NAT-025` (line 31, after `NAT-020`, before `NAT-030`): the amount, then exactly
", divided (or split) into N [ordinary | registered | equal] quotas (or shares), fully subscribed and fully paid in",
and nothing after it but the full stop, in one sentence of one line; and the amount is the only current amount of
the clause (`single_current_amount`). One amount, three natures (resolved, subscribed, paid in), as `NAT-020`. Read
by grammar, only without qualification: any other word, a second amount, a second sentence or a second line leaves
the amount to the rules below (`NAT-070`: resolved only; `NAT-999`: no nature). `NAT-020` now asks the same
`single_current_amount` (line 22): the siblings found that "the share capital is EUR 100.000,00, of which EUR
20.000,00 fully subscribed and fully paid in" gave the part all three natures; the line, which no capital line rule
explains, kept every field `[TO CONFIRM]`, so nothing was published, but the nature was wrong. Each rule has its
tests inline; the self-test passes.

Siblings, by class (`tests/test_d39_capital_count.py`): 25 clauses - the claimed count form in four wordings, the
plain form, and twenty that must not close (Italian; subscribed only; paid in only; partly; for one quarter; to be
paid in; of which an amount paid in; subscribed for an amount; split across two sentences; qualified after;
negated; of which before; a nominal amount per quota; another count verb; an exception after; a contradiction after
a semicolon) - each in three setups (the deed alone with a witness of its office; with a later extract that states
the full values; with one that states another paid-in amount), plus a second capital clause that contradicts and the
words split across two lines: 78 rows. Published wrongly: **0 on the code of `v2.0.9-freeze`, 0 on v2.0.10**. The
four count forms now give what the plain form gives in every setup (alone and with the full later extract: three
facts; with the other paid-in amount: resolved and subscribed facts, paid in a DISCREPANCY); on v2.0.9 they gave
the resolved capital only. Every other form is as on v2.0.9: every capital field `[TO CONFIRM]`, the entity
blocked when the line is one no rule explains and may state a holding.

Facts gained (run 23 against v2.0.9 on the same corpora): on hand-22, fields exact 78/223 -> 80/223 and fields
abstained 145/251 -> 143/251: the subscribed and the paid-in capital of E-0007, the gold's values. On every other
corpus already seen - the three suites, seeds 20261011 to 20261019 plain and perturbed, the hand corpora of runs 7
to 20 and the out-of-pool corpus of run 5 - every count and metric is that of v2.0.9: the generator does not write
the count form, and the probes of runs 18, 20 and 22 that put words inside it (`divided into 1.000 quotas Timone
Mutato, fully subscribed and fully paid in`, E-0014 of hand-20; E-0017 of hand-18; E-0020 of hand-22) and the
nominal amount per quota of hand-9 E-0008 are still not read: their gold states the three capital values, so
each is an abstention (or a block of its entity), never a value published.

#### 3. (c) Declarations

- D3 - the intended behaviour, kept: an address is read when every word of it is identified (a whole street entry
  of the gazetteer, a house number, a town and a province of the gazetteer) and a second document states it alike;
  a word of a whole gazetteer street entry is part of the street even when it is also a known surname (E-0033 of
  hand-22: `Via del Segnaposto 5, Campomodello (ZZ)`, `Segnaposto` being the surname of P-007; published, the
  value right). The known names are not looked for inside an identified address: a name that is not part of a
  gazetteer entry leaves the address unidentified, and the line open (`Via Gino Segnaposto 5`: the office stays
  `[TO CONFIRM]`). The sentence of entry 2.0.9 "an address without a house number, or with a name the corpus knows
  inside it: the line is open" is true for a known name outside the gazetteer's entries, not for one inside a whole
  street entry; it is restated below. `tests/test_d39_limits.py` `D39_Hand22Limits` checks both.
- D4 - declared, not read: the holder row with the identifier in square brackets (`- Name [P-015]: 60%`, and the
  other bracket orders) is in no rule; the row is not read, the table cannot be summed, the entity **blocks**
  (`OWN-015`). Reading it would need the verification of the C2 form `Name (P-001)` and its own sibling suite;
  left declared (`tests/test_d39_limits.py` `D39_DeclaredLimits`).
- The numeral case of `IDN-010` is **meant to block** when the line may state a holding (E-0025 and E-0028 of
  hand-22, a numeral inside a free-text slot of a deed): a numeral may state a quantity, and a quantity beside a
  holders' table or the capital is not left open. Elsewhere it keeps every field `[TO CONFIRM]`.
- E-0005 of hand-22, now a named limit: a blank line inside a list of holders ends the list; the rows after it are
  not part of the table, the table sums to less than the whole (`OWN-010`) and the entity **blocks**.

#### 4. (d) The test suite

- `tests/test_d38_identification.py` line 405: the docstring names E-0025 of hand-20 (it said E-0007).
- `tests/support.py`: every folder `tmp()` creates is removed when the test process ends (`_remove_created`,
  lines 29-47, registered with `atexit`), and nothing else; a child process gets a TEMP of its own made by `tmp()`
  (line 176), removed with it; the scenario checks that `tests/test_scenarios.py` runs in its own process make their
  work folders with `tmp()` too. Measured, a full suite with a TEMP of its own: 6015 entries left on the code of
  `v2.0.9-freeze`, 12 after the first commit of D39 (the scenario checks), 0 on v2.0.10.
- The failure that comes and goes: three full runs in parallel on commit `b2b34ae` (the code of `v2.0.9-freeze`),
  each with its own TEMP and verbose output kept, under the load of six measurements at once
  (2026-10-01 16:34:50Z to 16:47:39Z): 339 tests, `OK`, three times - it did not reproduce. A second attempt, three
  full runs in parallel on the working tree of v2.0.10 before its commit, under the same load (16:58:19Z to
  17:14:16Z): 364 tests each, 362 passed and the same two failed in each run, both expected of that snapshot (its
  manifest was not yet written, and it still counted 108 rules) - no intermittent failure. Read in the code, one
  cause that is the pack's: the audit's caches were keyed by `id(rules)` (`dossier/s7_audit.py`, v2.0.9 lines
  370-376 and 463); `rules_engine.load()` makes a new `Rules` for each run, and once one is freed its id may be
  handed to the next, so a process that runs with two rule sets - the suite does, with copies whose gazetteer
  holds more words - may be served the identification built from the other set: an audit that disagrees with the
  extractor (a FAILED run, fail-closed) or the reverse, by the allocator's chance. Measured on the v2.0.9 code: 400
  loads alternating two rule sets, 7 ids reused and 7 wrong answers, in each of three processes. Now the caches are
  keyed by the content of the rules (`_rules_key`, a SHA-256 of the four files, computed once per object and
  checked by a weak reference, lines 373-401; `own_names` line 488, `corpus_texts` line 535, whose key also lacked
  the rules); the same probe: 69 ids reused, 0 wrong answers. Whether this is the failure of 2026-10-01 18:07 is
  `[TO CONFIRM]`: its name was not kept. `tests/test_d39_scorer.py` `D39_AuditCacheFollowsTheRules` (3 tests, all
  failing on the v2.0.9 code).

#### 5. (e) The measurer's flags

Nothing changed in the pack: the model name in `tests/test_shareable.py` and in this file is a refused value inside
a negative test (a false positive of E10), and the README's run block is an indented code block.

### Known limits of v2.0.10

The complete list: those of v2.0.9, restated where v2.0.10 changes them, and those of v2.0.10. Each limit is marked
with what it does to the entity, with two classes only: **blocks** or **keeps `[TO CONFIRM]`**. **No known limit
may publish.** What the proof still rests on is section 4 of entry 2.0.9, unchanged, in the same two classes.

Since v2.0.10 (D39):

- the count form of the capital clause in any wording but `NAT-025`'s - "It is fully subscribed and fully paid in."
  as a second sentence, the words across two lines, a nominal amount per quota (`quotas of EUR 10,00 each`),
  another count verb (`consisting of`), `wholly`, `entirely`, `paid up`, a qualification after it, a part
  introduced by `of which` -: the subscribed and the paid-in capital **keep `[TO CONFIRM]`**; when the line is one
  no capital line rule explains and the document states holders - **blocks** (`DISC-006`, `OWN-015`);
- E-0006 of hand-22, by class: a holder row with the identifier in square brackets (`- Name [P-015]: 60%`,
  `- P-015 [Name]: 60%`, `- [P-015] Name: 60%`) - **blocks** (`OWN-015`);
- E-0005 of hand-22, by class: a blank line inside a list of holders ends the list; the rows after it are not read
  and the table does not sum to the whole - **blocks**;

Since v2.0.9 (D38), unchanged unless said:

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

Since v2.0.8 (D37), unchanged unless said:

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

From v2.0.7 and earlier, unchanged unless said:

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

Count of limits marked **may publish**: v2.0.4 1, v2.0.5 0, v2.0.6 0, v2.0.7 0 (but its section 4 left a residual
risk outside the list, and run 18 found it), v2.0.8 0 (but its section 4 left a premise outside the two classes, and
run 20 found it), v2.0.9 0 (run 22 found none publishing), v2.0.10 0, with section 4 of entry 2.0.9 in the same two
classes and nothing outside them.

### Tests and numbers

- `tests/test_d39_scorer.py`, 15 tests in 3 classes: a build scored from a folder of 280 characters equals the short
  one, by a given corpus and by a generated one (`--seed`); the rebuild walk reads a deep build whole and refuses an
  empty walk; the measurement FAILS on an entity missing, a folder in place of its file or a truncated file, counts
  that disagree, nothing scored, an entity of the gold missing from the run, and `main()` exits 3 with the reason on
  stderr, also when the run raises; a clean build measures OK; the audit's caches follow the rules (d).
- `tests/test_d39_capital_count.py`, 5 tests in 2 classes: the 78 siblings of (b), the rule-level reading of every
  qualified clause, and E-0007 and E-0001 of hand-22 as the gold.
- `tests/test_d39_limits.py`, 5 tests in 2 classes: the bracket rows block (three orders, two setups), a blank line
  inside a list blocks, the declared blocks of hand-22 (E-0005, E-0006, E-0025, E-0028), and D3 both ways.
- Of the 25 new tests, 17 fail on the code of `v2.0.9-freeze` (19 counting subtests); the 8 that pass there state
  behaviour v2.0.10 keeps: the declarations of (c), the 0 wrongly published siblings, the forms that must not close.
- `tests/test_rules.py` counts 109 rules (108 + `NAT-025`); `tests/test_d38_identification.py` line 405 docstring.
- `tests/test_scenarios.py`: the scenario checks it runs in its own process make their work folders with `tmp()`
  (`ScenariosCanFail._with_expected`), so that a full suite leaves nothing in its TEMP (section 4).
- 364 tests: `OK`. Scenarios 10/10. Rebuild identical (README).
- Measured by the builder on corpora already seen (`eval/history.json` run 23; NOT blind): 0 never-events on all thirty
  results, every measurement `OK`, every command exit 0, and the sum of the eight `*_wrong_committed` fields 0 in each
  (the evaluator's tool, 240 values); every count and metric equal to those of v2.0.9 but hand-22 (section 2); the
  table of the README is unchanged.

## [2.0.9] - 2026-10-01 (freeze tag `v2.0.9-freeze`; not yet run blind)

### D38 - blind run of v2.0.8, run 20: eight never-events in two entities (the premise of corroboration), an own name read by topic words, three limits undeclared, long paths

Source: the evaluator's blind run of `v2.0.8-freeze`, `eval/history.json` run 20, seed 20261018 and the hand
corpus `eval/blind/hand-20/` (34 entities, 87 documents): 0 never-events in the plain and the perturbed corpus, 8
in the hand-written one, 4 in E-0009 and 4 in E-0010. In E-0009 the deed and the registry extract both write the
town of the registered office with words that state an endowment of ninety thousand beside a capital of 30.000; in
E-0010 every header and the own-name clause write the company's name with the same words. Stated alike by two
documents, the office (`ADR-020`) and the name (`NAM-020`) were corroborated, and the share capital was published
as a fact where the gold keeps it `[TO CONFIRM]`. This is the premise that section 4 of entry 2.0.8 declared: a
declared premise that publishes a wrong value is still a never-event, and `CLAIMS.md` section 10 downgrades A2 for
`v2.0.8-freeze`. The same run found a company's own name read by topic words (E-0007, E-0020), a capitalised
particle (`Via Del ...`), rows framed by vertical bars without a header row (E-0030) and a registry extract filed
with another entity's documents (E-0062), none of them declared; and a build that fails in a deep folder on a
machine without long-path support. Fixed by the builder's hand in this order: (a) first - the free-text slots are
decided by positive identification of every word, not by the agreement of the documents, a longer word list or a
tighter form -, then (b) the own name, (c) the limits declared, (d) long paths, (e) the measurer's two flags.
`OWN-015` stays `block` (D26), holders in a sentence stay unread (D31), `DISC-005` stays `every_field`,
`DISC-006`, `CLS-005`, `DISC-035` and `DISC-038` stay. Measured on corpora already seen only (`eval/history.json`
run 21): not blind; seed 20261018 and hand-20 are now seen.

#### 1. The rule (a): a free-text slot is a fact only when every word of it is identified

Written in `rules/extract.json`: the gazetteer (`gazetteer_town`, `gazetteer_province`, `gazetteer_street_type`,
`gazetteer_street_name`, `gazetteer_trade`, `gazetteer_first_name`, `gazetteer_surname`, `gazetteer_street`, lines
85-92), how its entries combine (`identify_address`, `identify_company`, `identify_person`, lines 99-101;
`gazetteer_note`, line 102), what a numeral is (`numeral_word_it`, `numeral_word_en`, `numeral_token`,
`numeral_note`, lines 103-106), which slot is of which class (`identification_slot_classes`, line 107;
`slot_note_2_0_9`, line 108), the ordered group `free_text_identification` (lines 957-1041: `IDN-010` line 961,
`IDN-020` 976, `IDN-030` 988, `IDN-040` 1000, `IDN-050` 1011, `IDN-999` 1022), `name_corroboration` `NAM-005`
(line 1116, after `NAM-010` and before `NAM-020`), `text_corroboration` `TXT-005` (line 1154) and `TXT-020` (line
1175, outcome now `unexplained`), and the legal assumption `identification_source` (lines 93-98,
`docs/ASSUMPTIONS.md`, the twelfth). Each group is ordered, first match wins, the exception on top. The code
extracts (`dossier/s1_extract.py` `identify`, `identified`, `numerals_in`, `_slot_closes`, `corroborate_names`,
`text_outcomes`, `known_names`); the audit derives the same outcomes with its own code (`dossier/s7_audit.py`
`_Ident`).

The principle chosen, and why. A free-text slot - the address of the office and of the previous office, the
company's name of a header or of a name slot, a person's name beside an identifier, the title of `CLS-900`, the
label of `CLS-250` - closes its line only when **every word of it is accounted for**, and the agreement of the
documents accounts for none:

- **(i) Identified by the gazetteer** (`IDN-020` to `IDN-050`): an address is a street type and a street name of
  the gazetteer, a house number of the slot grammar, a town and the province of the gazetteer, and optionally
  ` - interno`, ` - scala` or ` - piano` and a mark; a company's name is a trade word and a town (or `Holding`, a
  town and `Partecipazioni`), its legal form at the end read apart (`DISC-035`); a person's name is a first name
  and a surname; a title is one of the titles the pack's own builders write (`text_recognised`). Each entry is
  matched whole, case and particles included. The gazetteer is the closed list of the synthetic world: the
  vocabulary the generator draws from and the pack's scenarios write (`SYNTHETIC.md`).
- **(ii) Nothing left over**: a word that the gazetteer does not hold, before, inside or after the slot, leaves it
  unidentified (`IDN-999`), however many documents state it alike.
- **(iii) A numeral is a quantity** (`IDN-010`, the exception on top): a word of the street, the town, the name, the
  title or the label that holds a digit, is an Italian or English number word or a Roman numeral of two letters or
  more means the slot may state a quantity - an amount, a count, a share; such a line may state a holding.
- **What an unidentified slot does**: its line is one that no rule explains (`CLS-999`): every field the document
  may change **keeps `[TO CONFIRM]`** (`DISC-006`, under the date criterion of `DISC-005`), no value of that slot
  is read, and when the line may state a holding (`holders_evidence`, or a numeral) the entity **blocks**
  (`OWN-015`). A header name that is not identified (`NAM-005`) does the same for the document whose header it is.
  A title or a label closes its line only when it is a recognised text (`TXT-005`); a label stated alike by other
  documents (`TXT-020`) is now read by no rule.
- **Corroboration stays on top of identification**: an identified address is a fact only when it is also
  corroborated (`ADR-020`), an identified header name only with `NAM-020`; `ADR-010`, `ADR-999`, `NAM-010`,
  `NAM-999` and `DISC-038` are unchanged. A genuine difference of two identified addresses is still shown side by
  side (`DISC-020`, `tests/test_d38_identification.py` `D38_PlainStillPublishes`).

Why not the alternatives. A longer word list or a tighter form is what failed in runs 16 and 18. Equality with a
second document is what failed in run 20: the hand can write the same words twice. The names known to the corpus
(`CLS-005`: the identity layer, the `Entity:` headers) are in the same position: the hand writes the identity layer
and the headers too, so a person's name is identified by the gazetteer like any other slot, and a name of the
identity layer counts as known only when the gazetteer identifies it. This last choice has a price on the
hand-written corpora (section 3), and it is listed in section 4 as a choice `[TO CONFIRM]`.

#### 2. Siblings by class, and the code of v2.0.7 and v2.0.8

`tests/test_d38_identification.py`, written by the builder with fixtures of its own (every entity invented, never
the strings of hand-20): 16 wordings - words that state a change of the capital, the holders, the directors or the
office; with and without a numeral; of the form of an Italian place name and of another form - in 13 slots and
positions - the town (after and before its words), the street (before the number, inside it), the province (inside
the parentheses), the company's name (before the legal form, after its first word, before it, after the legal form,
inside the legal form), a title (before its closing mark), a label (after and before its words) - each with 3
sources: stated alike by 2 documents and by 3 documents (the class of run 20), and by one document beside a second
that states the slot without them (the class of run 18). 624 cases. A case is published wrongly when a field the
words may change is published as fact, the office or the name that holds the words is shown as a fact or as one
value of a DISCREPANCY, or a holding is derived from a table the words may contradict; a FAILED run publishes
nothing and is counted apart (none on any code). The same file was run on clones of `v2.0.7-freeze` and
`v2.0.8-freeze`.

| Siblings, `tests/test_d38_identification.py` | cases | v2.0.7 | v2.0.8 | v2.0.9 |
|---|---|---|---|---|
| words of the capital | 156 | 72 | 44 | **0** |
| words of the holders | 156 | 87 | 50 | **0** |
| words of the directors | 156 | 60 | 32 | **0** |
| words of the office | 156 | 48 | 28 | **0** |
| with a numeral / without | 312 / 312 | 123 / 144 | 68 / 86 | **0 / 0** |
| place-name form / other form | 312 / 312 | 216 / 51 | 128 / 26 | **0 / 0** |
| town (after, before), each | 48 | 21 | 14 | 0 |
| street (before the number, inside), each | 48 | 21 | 14 | 0 |
| province, inside the parentheses | 48 | 0 | 0 | 0 |
| company's name: before the legal form, after its first word, before it, each | 48 | 27 | 18 | 0 |
| company's name: after the legal form, inside it, each | 48 | 0 | 0 | 0 |
| title, before its closing mark | 48 | 30 | 0 | 0 |
| label (after, before its words), each | 48 | 36 | 22 | 0 |
| 2 documents alike / 3 documents alike | 208 / 208 | 89 / 89 | 77 / 77 | **0 / 0** |
| 1 document, a second without the words | 208 | 89 | 0 | **0** |
| **all siblings: published wrongly** | 624 | **267** | **154** | **0** |

v2.0.8 closed the class of run 18 (one document, a second without the words: 89 -> 0) and left the class of run 20
open (77 + 77 alike); v2.0.9 closes both. The run-18 and run-20 classes, by their shape, are also tested one by one
(`D38_Hand20Classes`: a town with a numeral in two documents blocks and its record names `IDN-010`; a name with a
numeral in every header blocks and its record names `NAM-005`; words without a numeral keep every field
`[TO CONFIRM]`). The sibling suites of D36 and D37 stay at 0 published wrongly (`tests/test_d36_forms.py`,
`tests/test_d37_forms.py`, `tests/test_d37_slots.py`), and the last now with 0 FAILED: its six fail-closed
cases of v2.0.8, a person's name of the identity layer in a company's name stated by one document, are not
identified (`NAM-005`) and publish every field `[TO CONFIRM]`.

hand-20, scored by `eval/score.py`: 8 never-events on v2.0.8 (run 20, and the builder's re-run in run 21), 0 on
v2.0.9. E-0009 and E-0010 publish nothing: each blocks, because the slot holds a numeral (`IDN-010`: line 9 of the
deed of E-0009, the office; line 8 of the deed of E-0010, the name) and such a line may state a holding
(`OWN-015`); without the numeral the same words keep every field `[TO CONFIRM]` (`tests/test_d37_score.py`
`hand20`, `D38_Hand20Classes`).

#### 3. The price of (a)

Measured by the builder on every corpus already recorded (`eval/history.json` run 21, NOT blind), against the code
of `v2.0.8-freeze` run by the builder on the same commands (every count of it equals runs 19 and 20). **No field is
published that v2.0.8 kept `[TO CONFIRM]`; no entity is published that v2.0.8 blocked.**

| Result | published, v2.0.8 -> v2.0.9 | blocked wrongly | facts exact | fields `[TO CONFIRM]` |
|---|---|---|---|---|
| development, holdout, stress | unchanged (139, 137, 137 of 150) | unchanged | unchanged | unchanged |
| seeds 20261011 to 20261017, plain and perturbed | unchanged | unchanged | unchanged | unchanged |
| **seed 20261018, plain / perturbed** | **133/150 / 133/150, unchanged** | **4 / 4, unchanged** | **1008/1279 / 474/1279, unchanged** | **271/1379 / 839/1379, unchanged** |
| out-of-pool corpus of run 5 | 94/150 -> 93/150 | 44 -> 45 | 216/925 -> 82/918 | 727/986 -> 860/978 |
| hand (run 7) | 1/2 -> 0/2 | 0 -> 1 | 10/10 -> 0/0 | 0/11 -> 0/0 |
| hand-9 | 6/9 -> 0/9 | 2 -> 8 | 24/48 -> 0/0 | 27/51 -> 0/0 |
| hand-11 | 10/15 -> 0/15 | 3 -> 13 | 5/71 -> 0/0 | 66/86 -> 0/0 |
| hand-14 | 9/15 -> 0/15 | 5 -> 14 | 14/64 -> 0/0 | 50/72 -> 0/0 |
| **hand-16** | **14/28 -> 0/28** | **13 -> 27** | **33/102 -> 0/0** | **69/118 -> 0/0** |
| **hand-18** | **16/27 -> 0/27** | **10 -> 26** | **35/111 -> 0/0** | **79/134 -> 0/0** |
| **hand-20** | **27/34 -> 1/34** | **6 -> 32** | **48/169 -> 0/5** | **121/216 -> 5/8** |

Where it comes from. The generated corpora do not move at all, and that says little: their places, streets, trade
words and names are drawn from the very lists the gazetteer is made of, so they are identified by construction.
The hand-written corpora show the price. Their writers use places, trades and names of their own: every header name
of every hand corpus is unidentified (`NAM-005`: 2, 9, 15, 15, 28, 27 and 35 entities), which keeps every field
`[TO CONFIRM]`; and their holders' rows name persons that the gazetteer does not hold, so the rows are read by no
rule and may state a holding (`HEV-010` on most entities, `HEV-030`, `HEV-040`, `HEV-060` on the others), and the
entity **blocks** (`OWN-015`). The one hand-20 entity still published (E-0028) has its eight fields `[TO CONFIRM]`.
On the out-of-pool corpus the labels that many documents state alike are no longer facts (`TXT-020`, in the records
of 104 entities): E-0144 now blocks (a label line that may state a holding, `HEV-080`), and 134 facts move to
`[TO CONFIRM]` or out of the published entity. The same documents leave what is derived from those fields undecided
too: effective holdings exact out-of-pool 13/60 -> 4/60, hand-20 7/21 -> 0/1, every other hand corpus to 0.

The price is accepted on the ground of the asymmetry of the pack (one wrong figure published as fact is worse than
any number of `[TO CONFIRM]`), and on the order of D38: a smaller safe gain with 0 never-events is worth more than a
bigger one with any. What would lower it is a decision, not a rule of the builder: a gazetteer made of real
registers for real documents (`identification_source`, `[TO CONFIRM with legal]`), and the choice of section 4 on
persons.

#### 4. What the proof still rests on, for v2.0.9 (section 4 of entry 2.0.8, rewritten)

Entry 2.0.8 closed the free-text slots by corroboration and declared its premise - two documents that state the
same text alike state it - outside its two classes. Run 20 showed that the premise publishes. This section says, for
every slot of `classified_lines`, how it is decided, and for each thing that still rests on a list or on form, what
it does to the entity, with only two classes: **blocks** or **keeps `[TO CONFIRM]`**. Nothing in it may publish,
and nothing in it is left outside the two classes.

Census of the free-text slots (`identification_slot_classes` and the groups of `classified_lines`):

- **Decided by identification, then by corroboration and equality** (since v2.0.9): the address of the office and
  of the previous office (`w_office`, `w_previous`: `IDN-*`, then `address_corroboration`); the company's name of
  the header `Entity:` and of the slots of the entity's own name (`w_name`: `IDN-*`, equal to its header since
  v2.0.6, then `name_corroboration`); a person's name beside an identifier (`w_person`, `w_person_first`: `IDN-*`,
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
   published. Since v2.0.9 they are no longer applied to any slot of `identification_slot_classes` to decide whether
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
opposite of v2.0.8. What the pack takes as written is a slot whose every word is of the gazetteer, stated alike by
two documents: the gazetteer itself (item 1, and `identification_source`, `[TO CONFIRM with legal]`).

#### 5. (b) The own name and the topic words

In v2.0.8 `_slot_closes` (`dossier/s1_extract.py` line 848) applied the whole list of topic words (`slot_topics`:
the topic rules of `unread_fields` and `holders_evidence`) to every free-text slot, the slot of the entity's own name
among them, and closed the slot only when its topics were all of the fields of the line. A word of the office's topic
(`FEV-030`: `Borgo`, `Corso`, `Largo`, `Viale` ...) in a company's own name therefore left that name unread in every
document and kept every field of the entity `[TO CONFIRM]`; at field level it masked two probes of run 20 (E-0007,
E-0020). Since v2.0.9 no slot of `identification_slot_classes` - the seven free-text groups: `w_office`,
`w_previous`, `w_name`, `w_person`, `w_person_first`, `w_title`, `w_label` - is decided by topic words: it closes
when it is identified (and, for an address, holds no name known to the corpus). Tested both ways
(`D38_OwnNameStreetWord`): four own names that open with a street word (`Borgo`, `Corso`, `Largo`, `Viale`) are
names, every field published, with a copy of the rules whose gazetteer holds them; with the pack's gazetteer, which
does not, they are not read and every field stays `[TO CONFIRM]`.

Does any other slot apply a topic list that is not its own? Before v2.0.9, yes: every group above, the person's
name and the title included. Since v2.0.9 none of the seven. The topic words are still applied in two places: the
label of `CLS-250` names with them the field its line states (`_label_line_fields`), which is its own function, and
since v2.0.9 no label closes a line (`text_recognised` holds no label), so it decides nothing that is published; and
the name beside an identifier in a row of a list (`_label_ok`), only when that name is not the identifier's own
known name - such a row is open whatever its words (checked by the builder: a row whose name is not its own blocks
with and without a street word) - so there the topic list decides between two blocks.

#### 6. (c) The limits of run 20, declared

Tested by class with fixtures of the builder's own (`tests/test_d38_identification.py` `D38_DeclaredLimits`):

- E-0030 of hand-20, by class: holders' rows framed by vertical bars (`| P-001 (...) | 60% |`) with no header row
  - not read - **blocks** (unchanged since v2.0.8, now declared);
- the capitalised particle of hand-20 (`Via Del ...`): the gazetteer holds `del Collaudo`, matched whole, case
  included - the address is not identified (`IDN-999`) - every field **keeps `[TO CONFIRM]`**; when the line may
  state a holding - **blocks**;
- E-0062 of hand-20, by class: a registry extract filed with the documents of one entity whose content names
  another entity (another registry number) that has no folder of its own in the input. Until v2.0.8 it was built as
  an entity of its own and nothing told the entity of its folder. Since v2.0.9 it is still built for the entity its
  content names, as ever, and it is also an unclassified document of the entity of its folder (`DISC-005`,
  `every_field`, `dossier/s1_extract.py` `extract_corpus`): which of the two it belongs to is not the pack's to
  choose. **E-0026 must abstain, and does**: every field of the entity of the folder **keeps `[TO CONFIRM]`** from
  the date of that document; its holders are checked as an unread document's - **blocks** when they are not read
  whole. On hand-20 E-0026 blocks (its own holders' rows, section 3) and E-0062 blocks. A control: when the entity
  the content names has a folder of its own, nothing changes (the generator's `folder` fault, decided as before).
- `slot_note_2_0_7` item (3) was corrected in D37's follow-up; unchanged here.

#### 7. (d) Windows long paths

A build in a work folder of about 230 characters, and `tests/test_determinism.py` with a `TEMP` of about 100
characters, failed on a machine without long-path support (`WinError 206`, `FileNotFoundError`: the staging files of
the shareable layer pass 260 characters). Since v2.0.9 the work folder carries the `\\?\` prefix on Windows
(`dossier/run.py`, `dossier/lib/jsonio.py` `ext`), and every place that opens a file by a path of its own goes
through it too (`dossier/s6_build.py`, `dossier/s7_audit.py` `read_docx`, `dossier/s8_shareable.py`,
`dossier/lib/zipnorm.py`, `tests/support.py` `tree_hashes`). Measured on this machine (`LongPathsEnabled` = 0):
`tests/test_determinism.py` with a `TEMP` of 103 characters passes its build tests on v2.0.9 and fails on
`v2.0.8-freeze` (`test_two_builds_of_the_dev_corpus_in_different_folders`: exit codes 2 and 3). Regression tests:
`tests/test_d38_long_paths.py` - a build in a work folder of 230 characters (scenario S07, no `WinError`, the tree
equal to a short build, the longest path over 260) and the folder shape of `test_determinism` under a `TEMP` of 100
characters. Both fail on the code of `v2.0.8-freeze`. Elsewhere than on Windows the prefix is not added.

#### 8. (e) The measurer's two flags: false positives, nothing changed

- E10 flags `claude-sonnet-5` in `tests/test_shareable.py` line 87: it is the refused value of the negative test
  `test_only_two_models_are_allowed` (the model hook must refuse any identifier but the two of `MODEL.md`). The
  string is there to be refused; removing it would remove the test.
- E1 reports `readme_run_block` false: the four commands of the README section "Re-run it" are an indented code
  block (CommonMark), and the measurer looks for fenced blocks only. The block is there and runs as written.

#### 9. The numbers, measured on every corpus already seen

Run 21 (v2.0.9, builder's hand, NOT blind): the commands of run 19 plus seed 20261018 plain and perturbed and
hand-20, on the files of the code commit extracted with `git archive`. The code of `v2.0.8-freeze` was re-run by the
builder on all twenty-seven: every count and metric equals runs 19 and 20. **Never-events 0 on all twenty-seven
results**; every never_event_list is empty and every `<kind>_wrong_committed` is 0.

| Result | never-events | published | blocked wrongly | facts exact | fields `[TO CONFIRM]` |
|---|---|---|---|---|---|
| hand-20 | 8 -> **0** | 27/34 -> 1/34 | 6 -> 32 | 48/169 -> 0/5 | 121/216 -> 5/8 |
| hand-18 | 0 -> 0 | 16/27 -> 0/27 | 10 -> 26 | 35/111 -> 0/0 | 79/134 -> 0/0 |
| hand-16 | 0 -> 0 | 14/28 -> 0/28 | 13 -> 27 | 33/102 -> 0/0 | 69/118 -> 0/0 |
| 20261018 plain | 0 -> 0 | 133/150 -> 133/150 | 4 -> 4 | 1008/1279 -> 1008/1279 | 271/1379 -> 271/1379 |
| 20261018 perturbed | 0 -> 0 | 133/150 -> 133/150 | 4 -> 4 | 474/1279 -> 474/1279 | 839/1379 -> 839/1379 |
| 20261017 plain | 0 -> 0 | 137/150 -> 137/150 | 3 -> 3 | 1082/1294 -> 1082/1294 | 212/1408 -> 212/1408 |
| 20261017 perturbed | 0 -> 0 | 137/150 -> 137/150 | 3 -> 3 | 542/1294 -> 542/1294 | 786/1408 -> 786/1408 |
| every other result | 0 -> 0 | section 3 | section 3 | section 3 | section 3 |

### Known limits of v2.0.9

The complete list: those of v2.0.8, restated where v2.0.9 changes them, and those of v2.0.9. Each limit is marked
with what it does to the entity, with two classes only: **blocks** or **keeps `[TO CONFIRM]`**. **No known limit
may publish.** What the proof still rests on is section 4, with the same two classes.

Since v2.0.9 (D38):

- a free-text slot that the gazetteer does not identify word by word (`IDN-999`): a town, a street, a province, a
  trade word, a first name or a surname that it does not hold, words added anywhere, a particle written otherwise
  (`Via Del ...`), a name written surname first, a street named after a person, a Roman numeral, a real town of two
  words - the line is read by no rule: every field the document may change **keeps `[TO CONFIRM]`** (`DISC-006`), no
  value of the slot is read; when the line may state a holding - **blocks** (`OWN-015`);
- a free-text slot that holds a numeral (`IDN-010`): digits, an Italian or English number word, a Roman numeral -
  the line may state a quantity - **blocks** when it may state a holding (a holders' table or the capital in the
  same document), else every field **keeps `[TO CONFIRM]`**;
- a company's name of a header that is not identified (`NAM-005`), even when every document states it alike: every
  field of that document **keeps `[TO CONFIRM]`**, no name of it is read; when the name may state a holding -
  **blocks**;
- a holders' row whose person is not identified by the gazetteer, or is not its identifier's own name of the
  identity layer: the row is read by no rule - **blocks** (`OWN-015`); a directors' row - **keeps `[TO CONFIRM]`**.
  The choice of section 4 item 7, `[TO CONFIRM]`; every hand-written corpus blocks by it;
- a title that is not one of the titles the pack's own builders write, and every label of `CLS-250` (no label is a
  recognised text), even when other documents state it alike (`TXT-020`, `TXT-999`): its line is read by no rule -
  every field **keeps `[TO CONFIRM]`**; when it may state a holding - **blocks**;
- E-0030 of hand-20, by class: holders' rows framed by vertical bars without a header row - **blocks** (section 6);
- E-0062 of hand-20, by class: a document filed under one entity whose content names an entity with no folder of
  its own: it is built for that entity, and the entity of its folder reads it as an unclassified document - every
  field **keeps `[TO CONFIRM]`** from its date; its holders not read whole - **blocks** (section 6);
- the name beside an identifier in a row of a list that is not the identifier's own known name, with or without a
  word of the topic lists: the row is open - holders **block**, directors **keep `[TO CONFIRM]`** (section 5).

Since v2.0.8 (D37), unchanged unless said:

- an address that no second document of the entity states alike, token for token (`ADR-999`): the fields that
  document may change (every field but the office), when it is not older than the latest event of a field, **keep
  `[TO CONFIRM]`** (`DISC-006`); the office **keeps `[TO CONFIRM]`** when no current source of it is corroborated
  (`DISC-038`); when the line may state a holding - **blocks** (`OWN-015`). A genuine difference of two whole
  identified addresses is shown side by side as a DISCREPANCY (`DISC-020`), the other fields **keep
  `[TO CONFIRM]`**. Since v2.0.9 an address is also read only when it is identified (above);
- an address equal to another of the entity plus words (`ADR-010`): every field **keeps `[TO CONFIRM]`**, no address
  of that line is read; when the line may state a holding - **blocks**;
- a company's name in the header `Entity:` equal to another header of the entity plus words (`NAM-010`): every
  field **keeps `[TO CONFIRM]`**, no name of that document is read; when the name may state a holding -
  **blocks**. A header name that one document alone states (`NAM-999`): every other field of that document, when
  it is not older than the latest event, and the name (`DISC-038`) **keep `[TO CONFIRM]`**;
- a company's name, stated by one document only, that holds a person's name of the identity layer: when the run of
  the entity ends FAILED by the leak check of the shareable layer (A6), nothing of it is published - **blocks**
  (fail-closed); since v2.0.9 such a name is not identified (`NAM-005`) and every field **keeps `[TO CONFIRM]`**;
- a title or a label equal to another plus words (`TXT-010`) - every field **keeps `[TO CONFIRM]`**; when it may
  state a holding - **blocks**. A short sentence of one to eight words ending in a full stop right after a holders'
  list (no blank line) - **blocks** (`tests/test_d36_forms.py` `D36_ListEnd`);
- E-0020 of hand-18, by class: holder rows that name the holder by a person's name alone, with no identifier, and a
  holders' heading of another noun (`Members of the company`) - **blocks**;
- E-0025 of hand-18, by class: a lettered item with the share before the holder, separated by a vertical bar -
  **blocks**;
- E-0026 of hand-18, by class: an ordinal word before the holders' heading (`Fourth. Holders:`) - **blocks**;
- E-0012 of hand-18, by class: the capital stated in a clause of a shape the pack does not have (`The founders
  bring in ...`) - every field the document may change, the capital among them, **keeps `[TO CONFIRM]`**.

From v2.0.7 and earlier, unchanged unless said:

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
  Since v2.0.9 a name is known only when the gazetteer identifies it (above);
- a name beside an identifier whose own name the corpus does not know (not in the identity layer, no `Entity:`
  header of its own; every person when the identity layer names nobody): the line is open - every field **keeps
  `[TO CONFIRM]`**, and the holders **block** (`OWN-015`);
- an address without a house number, or with a name the corpus knows inside it: the line is open and the office
  is not read from it - every field **keeps `[TO CONFIRM]`** (`DISC-006`), and when the line may state a holding -
  **blocks**. Since v2.0.9 the form of a place name (`slot_address_word`) no longer decides anything that
  identification does not: an address is read only when it is identified and corroborated (above);
- a company name whose legal form differs from the legal form stated (`S.r.l.s.` against `S.r.l.` included, by
  design) - the name is a discrepancy and the legal form **keeps `[TO CONFIRM]`** (`DISC-035`).

Count of limits marked **may publish**: v2.0.4 1, v2.0.5 0, v2.0.6 0, v2.0.7 0 (but its section 4 left a residual
risk outside the list, and run 18 found it), v2.0.8 0 (but its section 4 left a premise outside the two classes, and
run 20 found it), v2.0.9 0, with section 4 in the same two classes and nothing outside them.

### Tests and numbers

- `tests/test_d38_identification.py`, 15 tests in 6 classes: the 624 siblings of section 2 (267 published
  wrongly on the code of `v2.0.7-freeze`, 154 on `v2.0.8-freeze`, 0 on v2.0.9; no FAILED), the two classes of
  hand-20 by their shape, what still publishes (plain documents, a genuine difference side by side) and what a word
  outside the gazetteer costs, the own name both ways (b), the limits of (c) with a control, and the audit against
  the extractor (`D38_AuditAgrees`: the same outcome for every value, with the gazetteer of the pack and with one
  whose trade, town and first name hold two words). The audit identifies with its own code
  (`dossier/s7_audit.py` `_Ident`, line 307); its first version cut a name after its first word, so a trade of two
  words - which the gazetteer of the pack does not hold - was identified by the extractor and not by the audit, and
  the run ended FAILED (fail-closed, nothing published). `tests/test_d37_score.py` found it before the commit;
  every way of cutting the name is now tried, each part matched whole.
- `tests/test_d38_long_paths.py`, 2 tests (d); both fail on the code of `v2.0.8-freeze`.
- Tests whose expectation v2.0.9 changes, each with the reason written beside it: `tests/test_d36_forms.py`
  (`D36_ResidualWordList` no longer an expected failure; the plain addresses use the gazetteer, those outside it are
  a test of the price; hand-16 E-0014 blocks), `tests/test_d37_forms.py` and `tests/test_d37_slots.py` (the equality
  premises now state the opposite; a label stated alike no longer closes; a rename uses a name of the gazetteer),
  `tests/test_d37_score.py` (hand-20 added to the recorded hand corpora, 0 never-events, E-0009, E-0010 and E-0026
  checked; the hand corpus of run 7 scored with a copy of the rules whose gazetteer holds its words, so that the
  scorer is still checked on a published entity), `tests/test_d30b_forms.py` and `tests/test_d35_forms.py` (hand-11
  and hand-14 now block: the price of section 3).
- `tests/test_rules.py` counts 108 rules (100 + `IDN-010`, `IDN-020`, `IDN-030`, `IDN-040`, `IDN-050`, `IDN-999`,
  `NAM-005`, `TXT-005`); `free_text_identification` ends with a default and has its exception on top; 12 legal
  assumptions (`identification_source` added).
- 339 tests: `OK`. Scenarios 10/10. Rebuild identical (README).
- Measured by the builder on corpora already seen (`eval/history.json` run 21; NOT blind): sections 3 and 9.

## [2.0.8] - 2026-10-01 (freeze tag `v2.0.8-freeze`; not yet run blind)

### D37 - blind run of v2.0.7, run 18: four never-events in one entity (words added inside a town), three forms that block undeclared

Source: the evaluator's blind run of `v2.0.7-freeze`, `eval/history.json` run 18, seed 20261017 and the hand
corpus `eval/blind/hand-18/` (27 entities, 67 documents): 0 never-events in the plain and the perturbed corpus, 4
in the hand-written one, all in E-0015. Its registry extract gives as registered office the deed's address with
three words added inside the town; each word has the form of a place name and none is of a class of
`slot_not_name_word`, so the line closed, the office was shown as a DISCREPANCY whose second value carries the
words, and the share capital those words speak of was published as a fact. This is the residual risk that section
4 of entry 2.0.7 declared `[TO CONFIRM]`: a declared risk that materialises is still a never-event, and
`CLAIMS.md` section 8 downgrades A2 for `v2.0.7-freeze`. The same run found three forms that block without being
read or declared (E-0020, E-0025, E-0026). Fixed by the builder's hand in this order: (a) first - the free-text
slots are decided by corroboration and equality, not by a longer word list or a tighter form -, then (b) the three
forms declared, (c) one count per kind of never-event in the scorer, (d) E-0012 declared. `OWN-015` stays `block`
(D26), holders in a sentence stay unread (D31), `DISC-005` stays `every_field`, `DISC-006`, `CLS-005` and
`DISC-035` stay. Measured on corpora already seen only (`eval/history.json` run 19): not blind; seed 20261017 and
hand-18 are now seen.

#### 1. The rule (a): a free-text value is a fact only when it is corroborated

Written in `rules/extract.json` `address_corroboration` (lines 931-989: `ADR-010`, `ADR-020`, `ADR-999`),
`name_corroboration` (lines 990-1027: `NAM-010`, `NAM-020`, `NAM-999`), `text_corroboration` (lines 1028-1066:
`TXT-010`, `TXT-020`, `TXT-999`), the parameters `slot_text_groups` and `text_recognised` (lines 82-84), and
`rules/discrepancy.json` `DISC-038` (line 489). Each group is ordered, first match wins, the exception on top; the
code extracts (`dossier/s1_extract.py` `corroborate_entity`, `corroborate_names`, `text_outcomes`,
`classified_check`), the audit derives the same outcomes with its own code (`dossier/s7_audit.py`
`address_audit`, `name_audit`, `corpus_texts`).

- **An address is a fact only when it is corroborated**: stated alike, token for token (spaces collapsed, nothing
  else normalised), by two different documents of the entity; or stated by a recognised office transfer
  (`EXT-OFFICE-010`) and repeated alike by a source dated after it (`ADR-020`). `DISC-038` keeps the office
  `[TO CONFIRM]` when no current source of it is corroborated; what was read is listed beside it as a statement.
- **An address equal to another plus words is unexplained, not a discrepancy** (`ADR-010`): the tokens of another
  address of the entity stand in it, in the same order, with tokens added - in the street, in the town, before,
  after or between them. Its line is one no rule explains (`CLS-999`): `DISC-006` keeps every field
  `[TO CONFIRM]`, the line is checked for holdings and `OWN-015` blocks when it may state one; no address of that
  line is read, so the words never reach a value, a DISCREPANCY or the published files.
- **Single source** (`ADR-999`): the siblings of section 2 show that words added to an address that no second
  document states can change another field undetected. So the cautious outcome applies: the document may change
  every field but the office (`fields_check` `except`), `DISC-006` keeps them `[TO CONFIRM]` under the date
  criterion of `DISC-005`, `DISC-038` keeps the office `[TO CONFIRM]`, the line is checked for holdings.
- **A genuine difference stays a DISCREPANCY side by side** (claim A2): two whole different addresses, neither
  equal to the other plus words, are both shown with their sources (`DISC-020`).
- **The other free-text slots decided by form, the same principle**: the company's name of the header `Entity:`
  (`NAM-*`: plus words - every field `[TO CONFIRM]`, the name checked for holdings, no name of that document read;
  alone - every field but the name `[TO CONFIRM]`, the name `[TO CONFIRM]` by `DISC-038`), and the title of
  `CLS-900` and the label of `CLS-250` (`TXT-*`: a title or a label closes its line only when another document of
  the input states it alike or it is one of the titles the pack's own builders write; otherwise its line is read by
  no rule). The census of the other slots is in section 4.

#### 2. Siblings by class, and the code of v2.0.6 and v2.0.7

Written by the builder with fixtures of its own (every entity invented), by class (R6): words of the form of an
Italian place name that state a change of another field (the capital, the holders - two wordings -, the
directors, the office) or that are the name of a person of the identity layer; each in every position of the slot
and in every place where the pack reads it; with a second source that states the text without the words, with one
source only, and (addresses) as a genuine difference. A case is published wrongly when a field the words may change
is published as fact, the office or the name is shown with the words (as fact or as one value of a DISCREPANCY), or
a holding is derived from a table the words may contradict. A FAILED run publishes nothing and is counted apart. The
same two files were run on the code of `v2.0.6-freeze` and `v2.0.7-freeze` (the test files copied into a clone of
each tag).

| Siblings | cases | v2.0.6: wrong + FAILED | v2.0.7: wrong + FAILED | v2.0.8: wrong + FAILED |
|---|---|---|---|---|
| addresses, `tests/test_d37_forms.py` | 438 | 252 + 52 | 246 + 0 | **0 + 0** |
| - second source without the words | 294 | 178 (incl. FAILED) | 144 | 0 |
| - one source only | 126 | 111 (incl. FAILED) | 90 | 0 |
| - genuine difference (side by side expected) | 18 | 15 (incl. FAILED) | 12 | 0 |
| - town (after, before, between its words), each | 66 | 52 | 43 | 0 |
| - street (before the number, inside, before it), each | 60 | 47 | 39 | 0 |
| - province, inside the parentheses | 60 | 7 | 0 | 0 |
| names, titles, labels, `tests/test_d37_slots.py` | 300 | 177 + 18 | 177 + 18 | **0 + 6** |
| - company's name (header, name slot, label; 3 positions) | 234 | 138 + 18 | 138 + 18 | 0 + 6 |
| - title, label, heading | 66 | 39 + 0 | 39 + 0 | 0 + 0 |
| - second source without the words | 216 | 127 + 12 | 127 + 12 | 0 + 0 |
| - one source only | 84 | 50 + 6 | 50 + 6 | 0 + 6 |
| **all siblings: published wrongly** | 738 | **429** | **423** | **0** |

By the words added: capital 51/51/0 of 73 addresses and 31/31/0 of 50 slots (v2.0.6/v2.0.7/v2.0.8), holders
102/102/0 and 68/68/0, directors 51/51/0 and 30/30/0, office 42/42/0 and 29/29/0, a person's name of the identity
layer 58/0/0 and 37/37/6 (the counts with FAILED). The six FAILED of v2.0.8 are one class, fail-closed by design:
a company's name, stated by one document only, that holds a person's name of the identity layer is listed beside
its `[TO CONFIRM]` name field, and the leak check of the shareable layer (A6) refuses the entity - nothing is
published (known limits: **blocks**). The same six FAILED on v2.0.6 and v2.0.7. With a second source, the name
with the words is never read (`NAM-010`) and nothing fails.

hand-18 E-0015, scored by `eval/score.py`: 4 never-events on `v2.0.6-freeze` (the coordinator's measurement after
run 18) and on `v2.0.7-freeze` (run 18), 0 on v2.0.8: the extract's office is the deed's plus words (`ADR-010`),
every field is `[TO CONFIRM]`, the office is not shown with the words (`tests/test_d37_score.py`,
`test_recorded_hand_corpora`: 0 never-events on every recorded hand corpus, and E-0015 checked field by field).

#### 3. The price of (a)

Measured by the builder on every corpus already recorded (`eval/history.json` run 19, NOT blind), against the code
of `v2.0.7-freeze` run by the builder on the same commands. **Published and blocked wrongly do not move on any of the
twenty-four results**; no field is published that v2.0.7 kept `[TO CONFIRM]`; the price is facts that v2.0.7
published and v2.0.8 keeps `[TO CONFIRM]`.

| Result | facts exact, v2.0.7 -> v2.0.8 | fields `[TO CONFIRM]`, v2.0.7 -> v2.0.8 |
|---|---|---|
| development, seed 20260930 | 1386/1386 -> 1180/1386 | 0/1472 -> 206/1472 |
| holdout, seed 20261001 | 1285/1285 -> 1122/1285 | 0/1378 -> 163/1378 |
| stress, seed 20261002 | 681/1285 -> 591/1285 | 635/1372 -> 725/1372 |
| seed 20261011, plain / perturbed | 1323 -> 1091 / 568 -> 494 (of 1323) | 0 -> 232 / 782 -> 856 (of 1413) |
| seed 20261012, plain / perturbed | 1328 -> 1104 / 653 -> 530 (of 1328) | 0 -> 224 / 688 -> 811 (of 1396) |
| seed 20261013, plain / perturbed | 1379 -> 1124 / 618 -> 476 (of 1379) | 0 -> 255 / 796 -> 941 (of 1482) |
| seed 20261014, plain / perturbed | 1365 -> 1099 / 652 -> 539 (of 1365) | 0 -> 266 / 748 -> 861 (of 1461) |
| seed 20261015, plain / perturbed | 1300 -> 1041 (of 1300) / 667 -> 564 (of 1293) | 0 -> 259 (of 1371) / 647 -> 750 (of 1363) |
| seed 20261016, plain / perturbed | 1274 -> 1077 / 649 -> 538 (of 1274) | 0 -> 197 / 678 -> 790 (of 1384) |
| **seed 20261017, plain / perturbed** | **1294 -> 1082 / 655 -> 542 (of 1294)** | **0 -> 212 / 673 -> 786 (of 1408)** |
| out-of-pool corpus of run 5 | 290/925 -> 216/925 | 652/986 -> 727/986 |
| hand (run 7) | 10/10 -> 10/10 | 0/11 -> 0/11 |
| hand-9 | 32/48 -> 24/48 | 16/51 -> 27/51 |
| hand-11 | 32/71 -> 5/71 | 39/86 -> 66/86 |
| hand-14 | 27/64 -> 14/64 | 37/72 -> 50/72 |
| **hand-16** | **47/102 -> 33/102** | **55/118 -> 69/118** |
| **hand-18** | **39/111 -> 35/111** | **75/134 -> 79/134** (`[TO CONFIRM]` kept 16/20 -> 20/20) |

The same documents leave what is derived from those fields undecided too: effective holdings, cycles and
superseded figures are abstained, never shown differently (v2.0.7 -> v2.0.8):

| Result | effective holdings exact | cycles found | superseded linked |
|---|---|---|---|
| development | 92/92 -> 70/92 | 14/14 -> 11/14 | 510/510 -> 449/510 |
| holdout | 91/91 -> 71/91 | 16/16 -> 11/16 | 578/578 -> 489/578 |
| stress | 48/84 -> 38/84 | 7/22 -> 4/22 | 262/607 -> 219/607 |
| seed 20261017 plain | 79/79 -> 45/79 | 7/7 -> 7/7 | 541/541 -> 445/541 |
| seed 20261017 perturbed | 38/79 -> 26/79 | 5/7 -> 5/7 | 279/541 -> 226/541 |
| out-of-pool | 19/60 -> 13/60 | 6/13 -> 0/13 | 125/339 -> 108/339 |
| hand-16 | 5/11 -> 4/11 | 0/0 | 1/13 -> 1/13 |
| hand-18 | 5/14 -> 4/14 | 0/0 | 0/16 -> 0/16 |

Seeds 20261011 to 20261016 move the same way (every count in `eval/history.json` run 19). Conflicts found move
on four results, each conflict now `[TO CONFIRM]` (a document it rests on is one of those below; precision stays
whole): hand-9 3/3 -> 0/3, seed 20261013 perturbed 18/53 -> 15/53, seed 20261016 perturbed 27/80 -> 26/80,
out-of-pool 12/29 -> 11/29.

Where it comes from (the rule each record names, entities per result): on the generated corpora only `ADR-999` -
22 to 44 entities of 150 whose office one document alone states: an office transfer that no later source
repeats, a registry extract that is the only statement of an address, a deed with no extract. On the out-of-pool
corpus `ADR-999` (44 entities) and `TXT-010` (17: appointments whose title is the pack's own title plus words). On
the hand corpora: hand-9 `TXT-999` 1; hand-11 `ADR-999` 8, `NAM-999` 5, `TXT-999` 1; hand-14 `ADR-999` 5, `NAM-999`
1; hand-16 `ADR-999` 14, `NAM-999` 6, `TXT-999` 1; hand-18 `ADR-010` 1 (E-0015), `ADR-999` 2, `NAM-999` 1,
`TXT-010` 2, `TXT-999` 2. A smaller rule (only plus words, `ADR-010`) would cost almost nothing on the generated
corpora; the siblings of section 2 show that it is not safe: 90 of the 126 one-source address siblings publish
wrongly on v2.0.7, and `ADR-010` cannot see them, since there is nothing to compare them with. The price is
accepted on that ground (the asymmetry of the pack: one wrong figure published as fact is worse than any number
of `[TO CONFIRM]`).

#### 4. What the proof still rests on, for v2.0.8 (section 4 of entry 2.0.7, rewritten)

The proof of entry 2.0.5 section 1 assumes that a typed slot states nothing but the value of its own field. Entry
2.0.7 closed the name slots by equality and the amount and count slots by grammar, and declared what still rested
on a word list - the words of a street or a town of place-name form - as a residual risk, `[TO CONFIRM]`. Run 18
showed that this was not a class of outcome: those words published a capital. This section therefore says, for
every slot of `classified_lines`, how it is decided, and, for each thing that still rests on a word list or on
form, what it does to the entity, with only two classes: **blocks** or **keeps `[TO CONFIRM]`**.

Census of the free-text slots (`rules/extract.json` `slot_*` parameters and the groups of `classified_lines`):

- **Decided by corroboration and equality** (since v2.0.8): the address of the office and of the previous office
  (`w_office`, `w_previous`: `address_corroboration`); the company's name of the header `Entity:` and the slots of
  the entity's own name (`w_name` in the slot of its own name must equal its header since v2.0.6;
  `name_corroboration`); the title of `CLS-900` (`w_title`) and the label of `CLS-250` (`w_label`:
  `text_corroboration`).
- **Decided by equality** (since v2.0.6/v2.0.7): a person's name beside an identifier (`w_person`, `CLS-005`: the
  identity layer); another company's name beside an identifier (its own `Entity:` header); the document type
  (`doc_kinds`, `KIND-010` to `KIND-080`); the fixed words of each shape of `classified_lines` (the pack's own
  wording, matched whole).
- **Decided by grammar**: amounts (currency and figure) and counts (figure and unit noun) - any other word opens the
  line; the house number of an address; a share (per cent, fraction, words of a whole per cent or a simple
  fraction).
- **Place names** (`slot_address_word`, the form of an Italian place name) and `slot_not_name_word`: since v2.0.8
  they can no longer make an address a fact; an address is read only when it passes them **and** is corroborated.
  Failing them opens the line - every field **keeps `[TO CONFIRM]`**, and when the line may state a holding the
  entity **blocks**.

What still rests on a word list or on form, each with its class:

1. `holders_evidence` (`HEV-*`) and `unread_fields` (`FEV-*`), the words that say whether an open line, an open
   name or an unread document may state a holding: under `every_field` they decide only between **blocks**
   (`OWN-015`) and **keeps `[TO CONFIRM]`** (`DISC-005`, `DISC-006`); no word of these lists lets a field be
   published.
2. The topic words of a slot (`dossier/s1_extract.py` `slot_topics`: the topic rules of `unread_fields` and
   `holders_evidence` applied to the free words of a slot): since v2.0.8 they are applied only to a text that is
   corroborated or equal (an address, a name, a title, a label). A word they find opens the line (every field
   **keeps `[TO CONFIRM]`**, or **blocks** with a holding) or, on a label, names the field of its kind that the
   line states, which **keeps `[TO CONFIRM]`** (`DISC-006`: no label line gives a value). A word they miss no longer
   decides anything: the text that holds it is either another text plus words (read by no rule) or stated alike by
   a second document (the premise below).
3. `list_end_sentence` and the item grammar (form): where a list ends. A line that is not a full sentence or a
   heading is a row of the list; a row that cannot be read leaves the list unread - holders **block**, directors
   **keep `[TO CONFIRM]`**. A line that ends the list is classified on its own; if no rule of its kind explains it,
   every field **keeps `[TO CONFIRM]`** and, when it may state a holding, the entity **blocks**.
4. The shapes of `classified_lines` (form): a line that no shape matches is `CLS-999` - every field **keeps
   `[TO CONFIRM]`**, or **blocks** with a holding. A shape matches only its fixed words around typed slots, so no
   free word of a closed line is left undecided by a list.
5. The date criterion of `DISC-005`/`DISC-006`: a document older than the latest event of a field cannot change
   it. It decides between the field read from the newer event and **keeps `[TO CONFIRM]`**; it publishes nothing
   that the newer event does not state.

**The premise of corroboration** - the definition of a fact in this pack, not a limit of reading, so it carries no
class of its own: two different documents that state the same text alike, token for token, are taken to state
it. When two documents of an entity carry the **same** added words in an address, or two headers the same name with
words, or two documents of the input the same label, the text is read as it is written, and a change those words
were meant to state is not seen. `tests/test_d36_forms.py` `D36_ResidualWordList` stays an expected failure for
this reason only (its address is written alike in the deed and the extract), and `tests/test_d37_forms.py`
`D37_EqualityPremise` and `tests/test_d37_slots.py` `D37_NameEqualityPremise` state it as tests. Any input that
states the text once, or states it once more without the words, is decided by sections 1-2: plus words or alone,
never published. The blind protocol asks the next hand for both of those, unmasked. **[TO CONFIRM]**: whether a
careful human would read two documents that agree as two documents that are both wrong is a question of the
inputs, not of the pack; the pack does not claim to see it.

#### 5. (b) Three forms of hand-18 that block, now declared

Run 18 blocked three hand-18 entities with forms that `CHANGELOG.md` 2.0.7 neither read nor declared. They are not
read in v2.0.8 either; they are declared, by class, with the class **blocks**, and tested with fixtures of the
builder's own (`tests/test_d37_forms.py` `D37_DeclaredForms`; the same outcome on the code of v2.0.6 and v2.0.7):

- E-0020: holder rows that name the holder by a person's name alone, with no identifier, under a numbered heading
  of another noun (`4. Members of the company.`); each of the two alone blocks too - **blocks**;
- E-0025: a lettered item with the share before the holder, separated from it by a vertical bar
  (`a) 1/2 | P-012 (...)` under `Quotaholders of the company:`) - **blocks**; a dash item of that shape and a
  lettered item with the holder first are read (controls of the same test);
- E-0026: an ordinal word before the holders' heading (`Fourth. Holders:`), with shares in words or in figures -
  **blocks**.

On hand-18 the three stay among the ten blocked wrongly of run 18 and run 19; the other seven are limits that
v2.0.7 already declared. Reading any of the three is a change of rule for a later version, with its own siblings.

#### 6. (c) One count per kind of never-event in the scorer

`eval/score.py` now gives, beside `never_events` and `never_event_list`, one integer per kind of never-event of
section 1.5 of `eval/BLIND_PROTOCOL.md`, counted by the same call that writes the never-event into the list:
`fact_value_wrong_committed`, `planted_conflict_wrong_committed`, `gold_to_confirm_wrong_committed`,
`not_in_gold_wrong_committed`, `unsummed_table_wrong_committed`, `published_table_sum_wrong_committed`,
`effective_holding_wrong_committed`, `figure_source_wrong_committed` (`score.WRONG_COMMITTED`), and their sum
`never_events_by_kind_total`, which must equal `never_events`. No existing field changes name or meaning.
`tests/test_d37_score.py` checks, on every recorded hand corpus, that the eight counts agree with the wording of
the list read independently of the counter, and that each kind is counted (not only checked at zero) on a gold and
a provenance changed in a temporary copy. Run 19 records the new fields; the results of runs 1 to 18 are not
changed and do not have them.

#### 7. (d) E-0012: the capital in a sentence of another shape

hand-18 E-0012 states its capital in a clause of a shape the pack does not have (`The founders bring in EUR ...,
all of it paid on signing.`). The line is one that no rule of its kind explains (`CLS-999`): every field the
document may change **keeps `[TO CONFIRM]`** (`DISC-006`, under the date criterion of `DISC-005`), the capital
among them; nothing of it is published as fact. Declared as a known limit and tested by class
(`D37_DeclaredForms`, with a registry extract and on the deed alone); on hand-18 the capital fields of E-0012 are
`[TO CONFIRM]` (`tests/test_d37_score.py`). Unchanged from v2.0.7.

#### 8. The numbers, measured on every corpus already seen

Run 19 (v2.0.8, builder's hand, NOT blind): the commands of run 17 plus seed 20261017 plain and perturbed and
hand-18, on the files of the code commit extracted with `git archive`. The code of `v2.0.7-freeze` was re-run by
the builder on all twenty-four: every count and metric equals runs 17 and 18. **Never-events 0 on all twenty-four
results**; every never_event_list is empty and every `<kind>_wrong_committed` is 0.

| Result | never-events | published | blocked wrongly | facts exact | fields `[TO CONFIRM]` |
|---|---|---|---|---|---|
| hand-18 | 4 -> **0** | 16/27 -> 16/27 | 10 -> 10 | 39/111 -> 35/111 | 75/134 -> 79/134 |
| hand-16 | 0 -> 0 | 14/28 -> 14/28 | 13 -> 13 | 47/102 -> 33/102 | 55/118 -> 69/118 |
| 20261017 plain | 0 -> 0 | 137/150 -> 137/150 | 3 -> 3 | 1294/1294 -> 1082/1294 | 0/1408 -> 212/1408 |
| 20261017 perturbed | 0 -> 0 | 137/150 -> 137/150 | 3 -> 3 | 655/1294 -> 542/1294 | 673/1408 -> 786/1408 |
| every other result | 0 -> 0 | unchanged | unchanged | section 3 | section 3 |

hand-18 E-0015 is published with every field `[TO CONFIRM]` (4 never-events -> 0; `[TO CONFIRM]` kept 16/20 ->
20/20). Run 19 was taken twice on v2.0.8 (the working tree before the commit, and the files of the code commit):
every count and metric is identical. Every other count that moves is an abstention of section 3 (facts,
effective holdings, cycles, superseded links, four conflicts); figures with source change in number with what is
read and are all with source in every result; published, blocked wrongly and blocked rightly do not move.

### Known limits of v2.0.8

The complete list: those of v2.0.7, restated where v2.0.8 changes them, and those of v2.0.8. Each limit is marked
with what it does to the entity, with two classes only: **blocks** or **keeps `[TO CONFIRM]`**. **No known limit
may publish.** What the proof still rests on is section 4, with the same two classes.

Since v2.0.8 (D37):

- an address that no second document of the entity states alike, token for token (`ADR-999`): an entity whose
  office one document alone states (a deed with no extract, an extract that is the only statement of an address),
  an office transfer whose new address no later source repeats, an address stated once by an extract that differs
  from the deed's - the fields that document may change (every field but the office), when it is not older than
  the latest event of a field, **keep `[TO CONFIRM]`** (`DISC-006`); the office **keeps `[TO CONFIRM]`** when no
  current source of it is corroborated (`DISC-038`); when the line may state a holding - **blocks** (`OWN-015`).
  A genuine difference of two whole addresses is shown side by side as a DISCREPANCY (`DISC-020`), the other
  fields **keep `[TO CONFIRM]`**;
- an address equal to another of the entity plus words (`ADR-010`), anywhere in the street or the town, a real
  suffix such as `- interno 2` written in one document and not in the other included: its line is one no rule
  explains - every field **keeps `[TO CONFIRM]`** (`DISC-006`), no address of that line is read; when the line may
  state a holding - **blocks** (`OWN-015`);
- a company's name in the header `Entity:` equal to another header of the entity plus words (`NAM-010`): every
  field **keeps `[TO CONFIRM]`**, no name of that document is read; when the name may state a holding -
  **blocks**. A header name that one document alone states (`NAM-999`): every other field of that document, when
  it is not older than the latest event, and the name (`DISC-038`) **keep `[TO CONFIRM]`**;
- a company's name, stated by one document only, that holds a person's name of the identity layer: the name is
  `[TO CONFIRM]`, the reading is listed beside it, and the leak check of the shareable layer (A6) ends the run of
  the entity FAILED - nothing of it is published - **blocks** (fail-closed; the same on v2.0.6 and v2.0.7;
  `tests/test_d37_slots.py`, six cases);
- a title of `CLS-900` or a label of `CLS-250` that no other document of the input states alike and that is not
  one of the titles the pack's own builders write (`TXT-999`), or that is another title or label plus words
  (`TXT-010`): its line is read by no rule - every field **keeps `[TO CONFIRM]`**; when it may state a holding -
  **blocks**. A short sentence of one to eight words ending in a full stop has the form of a label: right after a
  holders' list (no blank line) it is such a line - **blocks** (`tests/test_d36_forms.py` `D36_ListEnd`, the
  case of a deed's holders and a sentence);
- E-0020 of hand-18, by class: holder rows that name the holder by a person's name alone, with no identifier, and
  a holders' heading of another noun (`Members of the company`) - **blocks** (section 5);
- E-0025 of hand-18, by class: a lettered item with the share before the holder, separated by a vertical bar -
  **blocks** (section 5);
- E-0026 of hand-18, by class: an ordinal word before the holders' heading (`Fourth. Holders:`) - **blocks**
  (section 5);
- E-0012 of hand-18, by class: the capital stated in a clause of a shape the pack does not have (`The founders
  bring in ...`) - every field the document may change, the capital among them, **keeps `[TO CONFIRM]`** (section
  7).

From v2.0.7 and earlier, unchanged unless said:

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
  also a line whose address, name, title or label is not corroborated, above): every field, when the document is
  not older than the latest event (`DISC-006`) - **keeps `[TO CONFIRM]`**; when the line may state a holding -
  **blocks** (`OWN-015`);
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
- a name slot with a word of `slot_not_name_word` that is not its identifier's or its entity's own known name, a
  name beside an identifier that is not its own (`CLS-005`), or the entity's own name slot that differs from its
  `Entity:` header: the line is one no rule explains - every field **keeps `[TO CONFIRM]`** (`DISC-006`), and
  when the line may state a holding - **blocks**. A real name that holds such a word and is not beside its own
  identifier costs the same;
- a name beside an identifier whose own name the corpus does not know (not in the identity layer, no `Entity:`
  header of its own; every person when the identity layer names nobody): the line is open - every field **keeps
  `[TO CONFIRM]`**, and the holders **block** (`OWN-015`);
- an address without a house number, or whose street or town holds a word that is not of the form of a place name
  (a real `Viale Kennedy` or `Via Roma Nord` included), a name the corpus knows, or a word of
  `slot_not_name_word`: the line is open and the office is not read from it - every field **keeps
  `[TO CONFIRM]`** (`DISC-006`), and when the line may state a holding - **blocks**. Since v2.0.8 an address that
  passes this form test is read only when it is also corroborated (above);
- a company name whose legal form differs from the legal form stated (`S.r.l.s.` against `S.r.l.` included, by
  design) - the name is a discrepancy and the legal form **keeps `[TO CONFIRM]`** (`DISC-035`).

Count of limits marked **may publish**: v2.0.4 1, v2.0.5 0, v2.0.6 0, v2.0.7 0 (but its section 4 left a residual
risk `[TO CONFIRM]` outside the list, and run 18 found it), v2.0.8 0, with section 4 in the same two classes.

### Tests and numbers

- `tests/test_d37_forms.py`, 11 tests in 4 classes: the 438 address siblings (420 with a second source or one
  source, 18 genuine differences; 304 unsafe on the code of `v2.0.6-freeze`, 52 of them FAILED, 246 on
  `v2.0.7-freeze`, 0 on v2.0.8), what corroboration still publishes and what it costs, the equality premise of
  section 4, and the declared forms of (b) and (d) with two controls that are read.
- `tests/test_d37_slots.py`, 8 tests in 3 classes: the 300 siblings of the company's name, titles and labels (177
  wrong and 18 FAILED on both earlier codes; 0 wrong and 6 FAILED of the fail-closed class on v2.0.8), names and
  texts that still publish, a genuine rename side by side, and the equality premise for names.
- `tests/test_d37_score.py`, 2 tests: the eight counts by kind agree with the never-event list on every recorded
  hand corpus and on a changed gold where every kind occurs; 0 never-events on every recorded hand corpus, and
  hand-18 E-0015, E-0012, E-0020, E-0025, E-0026 checked one by one.
- Fixtures: the tests of how a deed's forms are read gain a registry extract dated the day before the deed that
  states its office alike (`tests/support.py` `office_witness`: it corroborates the office and is a current source
  of nothing), and the scenarios gain ten registry extracts that repeat a deed or, in S09, the new address of the
  office transfer (S02 two, S04, S05, S07 three, S08 two, S09; `scenarios/make_inputs.py` `repeat`; the
  documents after them in S05 are renumbered, and in S09 the office is now sourced from the extract that repeats
  it), so that they keep testing what they tested. `tests/test_d36_forms.py` `D36_ListEnd`: a deed's holders followed by a short
  sentence now block (`TXT-999`), an appointment's directors followed by a sentence that adds a director keep
  every field `[TO CONFIRM]`. `D36_ResidualWordList` stays an expected failure (section 4).
- `tests/test_rules.py` counts 100 rules (90 + `ADR-010`, `ADR-020`, `ADR-999`, `NAM-010`, `NAM-020`, `NAM-999`,
  `TXT-010`, `TXT-020`, `TXT-999`, `DISC-038`); each new group ends with a default and has its exception on top.
- 321 tests: `OK (expected failures=1)`. Scenarios 10/10. Rebuild identical (README).
- Measured by the builder on corpora already seen (`eval/history.json` run 19; NOT blind): sections 3 and 8.

## [2.0.7] - 2026-10-01 (freeze tag `v2.0.7-freeze`; not yet run blind)

### D36 - blind run of v2.0.6, run 16: the residual risk of section 4 measured by class, a list that ends without a blank line, "own", an illegible amount

Source: the evaluator's blind run of `v2.0.6-freeze`, `eval/history.json` run 16, seed 20261016 and the hand
corpus `eval/blind/hand-16/` (28 entities, 59 documents): 0 never-events on the three corpora. Found: (a) the
residual risk of section 4 of entry 2.0.6 was probed, but two probes were masked - E-0014 (an address slot with
extra words) used the office-transfer wording of scenario S09, which no field rule reads, and E-0017 (a count
slot with extra words) blocked on a total line written outside the capital clause that `count_total` reads;
(b) a sentence or a heading written right after a list with no blank line was read as a row of that list, so the
whole list was unread (E-0010 blocked; the directors of E-0008 and E-0019 `[TO CONFIRM]`); (c) the adjective
"own" (`its own means`) counted as a word of holding (`HEV-040`; E-0006 and E-0011 blocked); (d) an illegible
amount `EUR 1#.###,00` counted as a bare figure that may state a holding (`HEV-080`; E-0114 of the perturbed
corpus blocked); (e) the fields check of E-0025 named holder rows without a share "lines that state the
directors"; (f) the list of known limits of 2.0.6 did not cover E-0010's form, and the first test of `CLS-190`
did not say what the rule does; (g) the protocol asked the history entry for keys that the recorder does not
write. Fixed by the builder's hand in this order: (a) first, then (b), (c), (d), (e), (f), (g). `OWN-015` stays
`block` (D26), holders in a sentence stay unread (D31), `DISC-005` stays `every_field`, `DISC-006`, `CLS-005`
and `DISC-035` stay. Measured on corpora already seen only (`eval/history.json` run 17): not blind.

**One statement of entry 2.0.6 was incomplete, and is completed here (the entry 2.0.6 is kept as written):**

- section 4 of 2.0.6 called the words of an address slot and a name beside an identifier nobody knows a residual
  risk of which "no case ... is in the corpora seen". The siblings of section 2 below show that on the code of
  `v2.0.6-freeze` the class was wide: 256 of 600 cases publish a field that the extra words may change as fact,
  and 56 more end the run FAILED. The probes of run 16 did not reach it (two blocked, two masked).
- `CHANGELOG.md:220-221` at `v2.0.6-freeze` (a row of a list that is illegible or not typed) did not cover the
  form of E-0010: a sentence written right after a list, with no blank line. Since v2.0.7 a full sentence or a
  heading ends the list (section 5); a sentence that names an identifier, a share or a count, as in E-0010, still
  does not, and is marked below (**blocks** for the holders, **keeps `[TO CONFIRM]`** for the directors).

#### 1. The rule (a): a typed slot states only its own value - by equality where the value is known, by form where it is not

- An address (`rules/extract.json:59` `slot_address`) is a street, a house number, a town and the province in
  parentheses (optionally `- interno`, `- scala` or `- piano` and a mark), then the end of the line or the
  sentence's own full stop. The house number is no longer optional, so that no word stands in its place. Every
  word of the street and of the town must have the form of an Italian place name (`:76` `slot_address_word`: it
  ends in a vowel, or is a particle, an elided particle, a truncated form such as `San` or `Castel`, or a Roman
  numeral), must not be a name the corpus knows (a person of the identity layer, a company of an `Entity:`
  header, its legal form set aside) and must not be a word of `slot_not_name_word` (`:73`), which adds the
  English verb endings `-ing` and `-s`, the commonest irregular past forms, nouns in `-ee`, and Italian nouns
  and verbs of role and holding (`subentra`, `cede`, `detiene`, `amministratore`...). `dossier/s1_extract.py:762`
  `address_form_ok`, `:736` `known_name_inside`, `:772` `_slot_closes`.
- The readers of the registered office read only such an address: `EXT-OFFICE-010`, `-020` and `-030`
  (`rules/extract.json:224`, `:235`, `:246`) carry `value_slot` `w_office` (`:230`, `:241`, `:252`); an address
  read is judged as that slot of `classified_lines`, and one that fails is not read
  (`dossier/s1_extract.py:237-241`). The extra words therefore never reach the office value nor the shareable
  layer: on v2.0.6 they did, and the run FAILED (`s8`).
- A name beside an identifier is judged by equality only (`CLS-005`, `rules/extract.json:636`;
  `dossier/s1_extract.py:716` `label_not_its_own`): it closes its line only when it is that identifier's own
  known name. An identifier whose own name the corpus does not know (no name in the identity layer, no `Entity:`
  header of its own) cannot be checked, and the line is open - the word list is no longer consulted there. A
  value that is its identifier's own known name, or the entity's own name equal to its header, is a name whatever
  its words (`:751` `_own_value`: `Holding` or `Trading` in a company's own name is not a verb).
- An amount slot (currency and figure, and the words the rules already read) and a count slot (a figure and the
  unit noun) were already typed in v2.0.6: extra words after them make the line one no rule explains. The
  siblings below confirm it on both codes (0 unsafe). Another company's name in a label is judged by equality with
  that company's header (holder rows) or with the document's own header (label lines), as in v2.0.6.
- The audit re-derives all of it in its own code (`dossier/s7_audit.py:349` `_not_its_own`, `:470`
  `address_form`, `:474` `names_of`) and refuses a record less strict than its own reading.

#### 2. Siblings by class (`tests/test_d36_forms.py`), and the code of v2.0.6

Each case is a deed and a registry extract that agree, with one slot changed, or a later document (an office
transfer, a capital resolution, a financial summary, a transfer notice, a ledger, an appointment) dated after
both. The extra words are eight wordings of capitalised words that state another field - the directors, the
holders or the capital - naming a person the corpus knows, a person it does not know, or nobody, among them an
Italian verb (`Subentra`) and a noun of role in no list (`Leader`); none is a literal string of hand-16. A case is
unsafe when a field the words may change is published as fact, the slot's own field is published with the words
in it, a holding is derived from a table the words may contradict, or the run FAILED. The same file was run on the
code of `v2.0.6-freeze` (commit `6acebba`).

| Class (places) | Cases | Unsafe on v2.0.6 | of which FAILED | Unsafe on v2.0.7 |
|---|---|---|---|---|
| address slot: after the province, after the house number, in place of it, inside the town, inside the street, after `interno`, as the town (deed, extract, label line, office transfer new and previous address) | 280 | 164 | 56 | 0 |
| amount slot (deed clause, extract, capital resolution, financial summary) | 80 | 0 | 0 | 0 |
| count slot (capital clause, holder rows in quotas) | 32 | 0 | 0 | 0 |
| a name beside an identifier nobody knows (holder rows `P-`, `E-`; director lines `ID (name)`, `name (ID)`) | 176 | 148 | 0 | 0 |
| another company's name in a label (holder row, label line) | 32 | 0 | 0 | 0 |
| all | 600 | 312 | 56 | 0 |

The unmasked probes (goal (a) on seen data): `D36_HandSixteenUnmasked` builds at run time, from
`eval/blind/hand-16/` (not changed), E-0014 with its office change in the wording `EXT-OFFICE-010` reads and the
extra words after the new address kept, and E-0017 with the total of quotas inside the deed's capital clause that
`count_total` reads and the extra words on a holder row. v2.0.6: 0 never-events, E-0014 **FAILED** (the reader
took the extra words, two person names among them, into the office, and they reached the shareable layer; nothing
published), E-0017 BLOCKED (the row is not typed: `CLS-999`, `OWN-015`). v2.0.7: 0 never-events, E-0014 OK with
every field `[TO CONFIRM]` and no office value read from the transfer (`value_slot`), E-0017 BLOCKED. Nothing is
published as fact on either code. `D36_ReaderRefusesTheSlot` (5 reader cases) fails on v2.0.6, passes on v2.0.7;
the plain addresses and the plain office transfer of `D36_PlainAddressesStillRead` pass on both (its third test,
the address without a house number, is the price of section 3 and fails on v2.0.6 by design).

#### 3. The price of (a)

Counted with `address_form_ok` on every address of the recorded corpora (suites, seeds 20261011 to 20261016 plain
and perturbed, the out-of-pool corpus of run 5, hand corpora of runs 7, 9, 11, 14 and 16, scenarios): 8845 of
8848 pass. The 3 that do not are one address without a house number (hand-11 E-0009, `Piazza Senza Numero`),
which is no longer an address; its fields were `[TO CONFIRM]` already (`DISC-005`). A corpus whose identity layer
names no person cannot check any name beside a person identifier: its holders block (`D36_UnknownIdentifierIsOpen`;
`tests/test_pipeline_cli.py` now writes the identity layer of its one-deed input). A real street or town with a
word of another form (`Viale Kennedy`, `Via Roma Nord`) costs the same as an address with extra words. In run 17,
(a) moves one count of one result: on hand-11, figures with source 134/134 -> 132/132 - the two readings of
E-0009's office (deed and extract) are no longer read and no longer listed beside the `[TO CONFIRM]` field; no
status of any field changes there.

#### 4. The premise of the proof, for v2.0.7 (what still rests on it)

The proof of entry 2.0.5 section 1 assumes that a typed slot states nothing but the value of its own field.
**Closed by equality** in v2.0.7: every name slot - a name beside an identifier (the identifier's own known name,
or the line is open), the entity's own name (its header), another company's name (its header). **Closed by
grammar**: the amount and count slots (currency and figure, figure and unit noun: any other word opens the line),
the house number of an address, and the form of the words of a street and a town (each ends in a vowel, or is a
particle, a truncated form or a Roman numeral).
What **still rests on a word list** (`slot_not_name_word`, and the names the corpus knows): a street or a town
whose words all have the form of a place name, name nobody the corpus knows, and state something with a word of
no class of that list - an Italian verb or noun ending in a vowel (`Via Ugo Nessuno Governa 1, Montefinto (ZZ)`;
`Montefinto Ugo Nessuno Presiede (ZZ)`). No grammar tells such a street from `Via Giuseppe Garibaldi 1`. Such a
line closes, and every field of the entity is published - the directors included, whatever those words were meant
to say. This is a residual risk, **`[TO CONFIRM]`**, not "no case is known": the case above is constructed and
kept as a test expected to fail (`tests/test_d36_forms.py` `D36_ResidualWordList`); when it passes, this section
must change. The lists of `unread_fields` and `holders_evidence` (sentences) are word lists too; under
`every_field` they decide only whether an entity blocks or keeps every field `[TO CONFIRM]`. The blind protocol
asks the next hand to probe the address slot, unmasked.

#### 5. (b) A list ends at a sentence or a heading

`dossier/s1_extract.py:356` `ends_list`, `:370` `_block`, and the audit's own reading
(`dossier/s7_audit.py:444`): a list (a holders' table, a directors' list) runs from its heading to the first blank
line or to the first line that is a heading of a list (`holders_heading`, `directors_heading`, with or without the
terminal mark, no identifier) or a full sentence (`rules/extract.json:29` `list_end_sentence`: a capital first, no
list marker, three words or more, `.`, `!` or `?` after a letter, no identifier, no share, no fraction, no figure
followed by a unit noun). That line is classified on its own (`classified_lines`; `CLS-999` and `DISC-006`;
`OWN-015` when it may state a holding). Any other line stays a row: a wrapped row, a share, an identifier, a line
that ends in a figure leaves the whole list unread, as before. `D36_ListEnd`: a sentence or a heading after a
list in a deed, an extract, a transfer notice and an appointment (5 of 6 fail on v2.0.6), and a wrapped row, a
sentence with a count, a sentence with a share, a sentence of the total, which still block. hand-16: E-0019's
directors are read (`[TO CONFIRM]` -> `P-007`, exact); E-0008 keeps every field `[TO CONFIRM]` on both codes, by
`DISC-006`: its line 11, a sentence that gives an address where the board meets, is read by no rule of an
appointment - on v2.0.6 as a row of the list, on v2.0.7 on its own; E-0010 still blocks (its sentence names
`P-001` and `P-013`), as marked below.

#### 6. (c) and (d): "own" after a possessive; an illegible amount

- `rules/extract.json:387` `neutral_phrases`: a possessive (`its`, `their`, `the company's`, a name's) followed by
  the adjective "own" is not a word of holding unless "own" is followed by an article, a determiner or a figure;
  the verb ("Aldo Finti and Bice Provetti own the company", "they own the whole of it") still is (`HEV-040`,
  `:426`, 3 new tests). `D36_PossessiveOwn` on a document of unrecognised type: 2 cases blocked on v2.0.6 now keep
  every field `[TO CONFIRM]` (`DISC-005`); 3 still block. hand-16 E-0006, E-0011: BLOCKED -> OK, every field
  `[TO CONFIRM]`.
- `HEV-080` (`:470`): a currency followed by a figure with `#` in it is an amount that cannot be read, not a bare
  figure. `D36_IllegibleAmount`: 2 cases blocked on v2.0.6 are now published; a name and a bare figure still
  block. E-0114 of seed 20261016 perturbed: BLOCKED -> OK; the thirteen gold facts it adds are all left
  `[TO CONFIRM]` and the field the gold leaves open is kept (section 8).

#### 7. (e), (f), (g)

- (e) `dossier/s1_extract.py:927` `_list_region`, `:993`: lines that stand inside another field's list are named
  as such - hand-16 E-0025: "lines 12, 14 stand in the holders' table of line 11 and are not rows it reads (each
  reads as a line of the directors, CLS-240); no rule of its kind read them" (it said "state the directors"). The
  outcome is unchanged (BLOCKED). `D36_ListLineMessage`.
- (f) The first test of `CLS-190` (`rules/extract.json:780`) says what the line may change with a new key,
  `expect_may_change_unless_read` (`dossier/s1_extract.py:1162` `run_inline_tests`): `registered_office` when no
  field rule of its kind reads it, nothing when one does - scenario S09 adds such a rule. "The seat of the company
  is moved" **stays unread by design**: it is S09's unknown wording, and reading it would break S09's
  expectation that the rule added on top moves that field only. A test of the read wording ("is transferred",
  nothing may change) is added.
- (g) `eval/BLIND_PROTOCOL.md` section 5 now asks the history entry for the seven keys the recorder writes (`n`,
  `date`, `run_by`, `code`, `command`, `note`, `results`) and the Council-shape runs, listed by start time, in the
  evaluator's scorecard. The paragraph of D33 is unchanged.

#### 8. The price, measured on every corpus already seen

Run 17 (v2.0.7, builder's hand, NOT blind): the commands of run 15 plus seed 20261016 plain and perturbed and
hand-16. Compared with v2.0.6 (run 15 for eighteen results, run 16 - the evaluator on the same code - for 20261016
plain, perturbed and hand-16; the v2.0.6 code was re-run by the builder on all twenty-one, and every count and
metric equals the recorded one). Never-events 0 on all twenty-one results; every never_event_list is empty.

**Eighteen of the twenty-one results do not move at all**: dev, holdout, stress, seeds 20261011 to 20261016 plain,
20261011 to 20261015 perturbed, the out-of-pool corpus of run 5, hand (run 7), hand-9, hand-14. hand-11 moves in
one count only (section 3).

| Result | v2.0.6 | v2.0.7 |
|---|---|---|
| hand-16: never-events | 0 | 0 |
| hand-16: published, blocked wrongly | 12/28, 15 | 14/28, 13 |
| hand-16: facts exact | 46/89 | 47/102 |
| hand-16: fields `[TO CONFIRM]` | 43/99 | 55/118 |
| hand-16: `[TO CONFIRM]` kept | 7/7 | 13/13 |
| hand-16: effective holdings exact, superseded linked, figures with source | 5/9, 0/13, 144/144 | 5/11, 1/13, 181/181 |
| 20261016 perturbed: never-events | 0 | 0 |
| 20261016 perturbed: published, blocked wrongly | 136/150, 5 | 137/150, 4 |
| 20261016 perturbed: facts exact, fields `[TO CONFIRM]`, kept | 649/1261, 665/1370, 29/29 | 649/1274, 678/1384, 30/30 |
| 20261016 perturbed: effective holdings exact, superseded linked, figures with source | 34/86, 211/496, 2760/2760 | 34/87, 211/507, 2778/2778 |
| hand-11: figures with source (all else unchanged) | 134/134 | 132/132 |

hand-16 moves on four entities: E-0006 and E-0011 are published with every field `[TO CONFIRM]` ((c)), the
directors of E-0019 are exact ((b)), and the fields check of E-0025 has its new message ((e)); 20261016 perturbed
on one, E-0114 ((d)). The thirteen blocked wrongly are declared limits: holders in a sentence (D31),
a table with a header row, a row with "each", per mille, a sentence with an identifier right after a list
(E-0010), and the typed-slot probes that open a line which may state a holding (E-0013, E-0017, E-0018).
[TO CONFIRM: the per-entity attribution of the thirteen is the builder's reading of the views; the counts are the
scorer's.]

### Known limits of v2.0.7

Each limit is marked with what it does to the entity: **blocks**, **keeps `[TO CONFIRM]`** or **may publish**.
**No known limit may publish.** The residual risk of section 4 is stated there, as `[TO CONFIRM]`.

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
  ("Allocation of the capital", "Capital allocation", "ownership structure", owners, beneficial owners) -
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
- a document of a recognised type with a body line that no rule of its kind explains (`CLS-999`): every field,
  when the document is not older than the latest event (`DISC-006`) - **keeps `[TO CONFIRM]`**; when the line
  may state a holding - **blocks** (`OWN-015`);
- a closed line that states a field of its kind where no rule of its kind read it (the office-transfer wording
  "The seat of the company is moved", scenario S09, among them), or a field its kind does not read: that field,
  when the document is not older than the latest event - **keeps `[TO CONFIRM]`**;
- a holders' table in a document of a kind not read for the holders: read whole and summed, then the holders
  **keep `[TO CONFIRM]`**; not read, or two of them - **blocks**;
- a row of a list of a recognised document whose share is illegible or not typed - every field **keeps
  `[TO CONFIRM]`**, and when the row may state a holding - **blocks**;
- since v2.0.7 marked (2.0.6 did not list it), a line right after a list with no blank line that is neither a
  heading nor a full sentence of the form `list_end_sentence` - a sentence that names an identifier, a share or a
  figure with a unit noun (hand-16 E-0010), a wrapped row: a row of the list the grammar cannot read - holders
  **block**, directors **keep `[TO CONFIRM]`**;
- a name slot with a word of `slot_not_name_word` that is not its identifier's or its entity's own known name, a
  name beside an identifier that is not its own (`CLS-005`), or the entity's own name slot that differs from its
  `Entity:` header: the line is one no rule explains - every field **keeps `[TO CONFIRM]`** (`DISC-006`), and
  when the line may state a holding - **blocks**. A real name that holds such a word and is not beside its own
  identifier (since v2.0.7 a name equal to its identifier's or its entity's own known name is a name whatever its
  words) costs the same;
- since v2.0.7, a name beside an identifier whose own name the corpus does not know (not in the identity layer,
  no `Entity:` header of its own; every person when the identity layer names nobody): the line is open - every
  field **keeps `[TO CONFIRM]`**, and the holders **block** (`OWN-015`);
- since v2.0.7, an address without a house number, or whose street or town holds a word that is not of the form
  of a place name (a real `Viale Kennedy` or `Via Roma Nord` included), a name the corpus knows, or a word of
  `slot_not_name_word`: the line is open and the office is not read from it - every field **keeps
  `[TO CONFIRM]`** (`DISC-006`), and when the line may state a holding - **blocks**;
- a company name whose legal form differs from the legal form stated (`S.r.l.s.` against `S.r.l.` included, by
  design) - the name is a discrepancy and the legal form **keeps `[TO CONFIRM]`** (`DISC-035`).

Count of limits marked **may publish**: v2.0.4 1, v2.0.5 0, v2.0.6 0, v2.0.7 0.

### Tests and numbers

- `tests/test_d36_forms.py`, 14 tests in 10 classes: the 600 siblings (312 unsafe on the v2.0.6 code, 0 on
  v2.0.7), the unmasked hand-16 probes through the scorer, the plain addresses that still publish and the address
  without a house number that does not, the readers that refuse the slot, the end of a list, "own" after a
  possessive, an illegible amount, the message of a line inside a list, an identity layer with nobody in it, and
  the residual of section 4 as a test expected to fail (an expected failure on both codes). Run on the code of
  `v2.0.6-freeze` (the reader test with the two-argument call of that code), 10 of the 13 others fail
  (`test_ends_list` errors: `ends_list` is new); the 3 that pass on both are controls - plain addresses, a plain
  office transfer, a broken row and sentences with a share or a count that still block.
- Inline rule tests: `classified_lines` 83 -> 87 (`CLS-005` 4 -> 7, `CLS-190` 2 -> 3), `holders_evidence` 23 ->
  30 (`HEV-040` 1 -> 4, `HEV-999` 9 -> 13); 219 -> 230 in all. `tests/test_rules.py` still counts 90 rules.
- `tests/test_pipeline_cli.py`: the one-deed input of `RefusedBeforeAnythingIsBuilt` now has its identity layer.
- Measured by the builder on corpora already seen (`eval/history.json` run 17; NOT blind): section 8.

## [2.0.6] - 2026-10-01 (freeze tag `v2.0.6-freeze`; not yet run blind)

### D35 - blind run of v2.0.5, run 14: two probes masked by a one-character miss, a judgement shown wrongly, a limit marked wrongly

Source: the evaluator's blind run of `v2.0.5-freeze`, `eval/history.json` run 14, seed 20261015 and the hand
corpus `eval/blind/hand-14/` (15 entities, 40 documents): 0 never-events on the three corpora. Found: (a) two
probes of the residual risk of section 4 of entry 2.0.5 - a person slot that admitted `Hilde Simulanti Sole
Proprietress Henceforth` (E-0011) and an extract whose `Name:` ends in `S.p.A.` beside `Legal form: S.r.l.`
(E-0012) - passed the pack's checks and were not published only because of (c); (b) the fields check of a
document of unrecognised type named the directors only (E-0013) while `DISC-005` kept every field; (c) every deed
of the corpus ends its first clause with `its legal form is S.r.l..`, which `CLS-110` and `EXT-FORM-010` did not
match, so 62 of 64 gold facts were abstained; (d) 5 of 15 entities blocked wrongly; (e) the list of known limits
marked a document of unrecognised type as one that keeps `[TO CONFIRM]`, while with a line that may state a
holding it blocks; (f) `exit_code` in a result object of `eval/score.py` is the pipeline's status, not the
scorer's exit. Fixed by the builder's hand in this order: (a) first, then (c) - fixing (c) alone would have
unmasked (a). `OWN-015` stays `block` (D26), holders in a sentence stay unread (D31), `DISC-005` stays
`every_field`, `DISC-006` stays. Measured on corpora already seen only (`eval/history.json` run 15): not blind.

**Two statements of entry 2.0.5 were wrong, and are corrected here (the entry 2.0.5 is kept as written):**

- section 4 of 2.0.5, "Residual risk of the premise (not a known limit: no case is known)": a case existed in the
  very shape that section describes. E-0011 of hand-14 is one, and the 192 siblings of section 2 below show that
  the class was wide: on the v2.0.5 code 147 of them publish a wrong value. "No case is known" was a statement
  about what had not been looked for, not about the code.
- `CHANGELOG.md:189-190` at `v2.0.5-freeze`, "a document of unrecognised type ... **keeps `[TO CONFIRM]`**": that
  marking is incomplete. When such a document holds a line that may state a holding (`holders_evidence`), or a
  holders' table that is not read whole, the holders cannot be summed and `OWN-015` **blocks** the entity
  (hand-14 E-0005, perturbed E-0054 of run 14). More cautious than declared, but marked wrongly; the list below
  gives both outcomes.

#### 1. The rule (a): a typed slot that admits more than its own value does not pass

- `rules/extract.json:70-72`, parameters `slot_name_groups` (the groups of `classified_lines` that hold a name:
  `w_name`, `w_office`, `w_previous`, `w_person`, `w_person_first`), `slot_not_name_word` (words that cannot be
  part of a name, by class: role, holding, time, function words, their Italian forms, and English suffix classes
  such as `-ly`, `-ship`, `-hood`) and `slot_own_name_groups` (`w_name`); `dossier/s1_extract.py:625`
  `not_name_words`. A name slot holding such a word does not close its line: the line falls to `CLS-999` and the
  document may change every field (`DISC-006`), or the entity blocks when the line may state a holding.
- Equality where the identity is known, not the lexicon: `CLS-005` (`rules/extract.json:619`,
  `dossier/s1_extract.py:689` `label_not_its_own`) - a name beside an identifier that is not that identifier's
  own name (the identity layer for a person `P-...`, the `Entity:` header of the entity's documents for a company)
  makes the line one no rule explains; and the slot of the entity's own name (the deed's `is named`, the
  extract's `Name:`, a label line with a company name) closes its line only when it is the name of the
  document's own `Entity:` header, spaces collapsed and the legal form at the end set aside
  (`dossier/s1_extract.py:664` `own_name_differs`, applied at `:766`). A word of no class of the lexicon in a
  person or company name slot is caught by that equality.
- `DISC-035` (`rules/discrepancy.json:465`, parameter `legal_form_in_name` at `:37`; `dossier/s3_discrepancy.py:158`
  `legal_form_clash`): a company name whose legal form at its end differs from the legal form stated (`S.p.A.`
  against `S.r.l.`, `S.r.l.s.` against `S.r.l.`, dotted or not, any case) is a discrepancy of its own. Both
  readings are listed with their sources, nothing is reconciled, the legal form is `[TO CONFIRM]` and the name is
  shown as a discrepancy (`DISC-020` when the names differ). Placed above `DISC-040`, below `DISC-020`/`DISC-030`.
- The audit re-derives all three in its own code (`dossier/s7_audit.py:236` `_bare_name`, `:244` `form_clash`,
  `:341` `_not_its_own`, `:448` the own-name slot) and reports a record less strict than its reading.

#### 2. Siblings by class (`tests/test_d35_forms.py`), and the code of v2.0.5

Every case below is a deed and a registry extract that agree, with one slot changed, or a later document dated
after both. A case is unsafe when a field it may change is published as fact, or a holding is derived from a
table the slot may contradict. The same file was run on the code of `v2.0.5-freeze` (commit `267ea87`).

| Class | Cases | Unsafe on v2.0.5 | Unsafe on v2.0.6 |
|---|---|---|---|
| person slot with trailing words in a director line (deed, extract, appointment; `ID (name)` and `name (ID)`) | 54 | 42 | 0 |
| person slot with trailing words in a holder row (deed, extract, transfer, ledger) | 72 | 56 | 0 |
| company name whose legal form differs from the one stated | 7 | 4 | 0 |
| company name slot with words that are not part of a name | 18 | 12 | 0 |
| person slot with words of no class of the lexicon, director line | 12 | 12 | 0 |
| person slot with words of no class of the lexicon, holder row | 16 | 16 | 0 |
| company name slot with words of no class of the lexicon | 4 | 4 | 0 |
| address slot with a trailing clause | 5 | 1 | 0 |
| amount slot with a trailing clause | 4 | 0 | 0 |
| all | 192 | 147 | 0 |

No case failed (raised) on either code. The trailing words are of nine classes (`Sole Proprietress Henceforth`,
`Sole Owner`, `Managing Director`, `Henceforth`, `Solely`, `Partnership`, `Who Holds It All`, `Socio Unico`,
`Ora Titolare`) and two of no class (`Padrona`, `Vecchie Zeta`); none is a literal string of hand-14 except the
first, which is its class.

The exact-form probes (goal (a) on seen data): `tests/test_d35_forms.py` class `D35_HandFourteenExactForm` builds
at run time, from `eval/blind/hand-14/` (not changed), E-0011 and E-0012 with the deed's legal-form clause in the
exact form v2.0.5 reads (`S.r.l.` then the end of the line). On the v2.0.5 code that variant has **3
never-events** (E-0011 holders shown as fact, E-0011 effective holdings derived, E-0012 legal form shown as
fact); on v2.0.6 0: every field of E-0011 is `[TO CONFIRM]` (the appointment's director line falls to `CLS-999`,
`DISC-006`), E-0012 shows the name as a discrepancy (`DISC-020`) and the legal form `[TO CONFIRM]` (`DISC-035`).
`D35_ExactFormProbes` repeats both shapes on entities of the test.

#### 3. The rule (c): the legal form followed by its sentence's own full stop

`CLS-110` and `EXT-FORM-010` (`rules/extract.json:654`, `:194`) read `its legal form is S.r.l..` and
`S.p.A..` together, by class (any recognised abbreviation, then the sentence's full stop); `CLS-150` and
`EXT-FORM-020` (`:711`, `:206`) do the same for the label line `Legal form: S.r.l..`. The value never includes
the second stop. hand-14, three stages, same command: v2.0.5 (run 14) facts exact 2/64, fields `[TO CONFIRM]`
63/72, conflicts 0/1; with (a) only 1/64, 64/72 (E-0011's directors went to `[TO CONFIRM]`); with (a) and (c)
27/64, 37/72, conflicts 1/1. Never-events 0, blocked wrongly 5, `[TO CONFIRM]` kept 7/7 at every stage.

#### 4. The premise of the proof, for v2.0.6 (what still rests on it)

The proof of entry 2.0.5 section 1 assumes that a typed slot states nothing but the value of its own field.
v2.0.6 tightens it where the identity is known: the name of a person beside its identifier must be that
person's name in the identity layer, and the entity's own name must be the name of its `Entity:` header (both by
equality, not by a word list); a company name must not carry another legal form. What **still rests on the word
list** `slot_not_name_word` (and on the lists of `unread_fields` and `holders_evidence`, which run 11 showed
incomplete for sentences): the words of an address slot (street and town), the name in a label beside an
identifier that neither the identity layer nor an `Entity:` header of the corpus knows, and the name of another
company in a label line. A change of
another field written entirely inside such a slot, in capitalised words of no class of those lists, would not be
seen and could publish. That is a residual risk, `[TO CONFIRM]`: no case of it is in the corpora seen, the
siblings above do not cover it, and the blind protocol asks the next hand to probe it, unmasked. It is not
written as "no case is known".

#### 5. (b) The fields check says what `DISC-005` applies

`dossier/s1_extract.py:576` `fields_check`: under `unread_document_scope` = `every_field` (the default) the
record of a document of unrecognised type says every field (`*`) and names the scope; what its lines alone would
name (`unread_fields`) is kept as a note, never as the fields it may change. hand-14 E-0013: the record said
`directors: line 9`; it now says every field, with the note. Under the narrow scope (OFF) nothing changes.
`tests/test_d35_forms.py` `D35_UnreadScopeReported`.

#### 6. (d) What is read by class, and what stays blocked

- Read: a holders' heading whose qualifier of the class "registered" follows the noun after a comma
  (`(4) Shareholdings, entered in the register:`, `Members, as recorded in the book of members:`), the same
  heading as without the comma (`rules/extract.json:23` `holders_heading_body`, 2 new tests of `EXT-HOLD-010`,
  `D35_HeadingWithParticipialClause`). A participle of another class after the comma (`transferred on 1 May`) is
  not a heading: it blocks.
- Not read, declared, **blocks**: a row naming several holders with "each" (`- P-007 and P-008 (...): 30% each`,
  hand-14 E-0003) - reading it would need the number of holders and the share each from one row, in the reader,
  the holders' check and the audit; not done in this cycle; holder nouns in a sentence (hand-14 E-0005
  memorandum, E-0007 resolution "becomes its third member", E-0009 appointment) - D31; a table with a header row
  (hand-14 E-0014, hand-11 E-0011, hand-9 E-0003) - not read safely in this cycle.

#### 7. (f) `pipeline_status`

`eval/score.py:233-235`: each result object carries `pipeline_status` (`OK`, `BLOCKED`, `FAILED`) next to
`exit_code`, which is unchanged and still the pipeline's own exit code (0 OK, 2 BLOCKED - at least one entity
blocked -, 3 FAILED). The scorer process exits 1 only when a result has a never-event. Documented in
`eval/BLIND_PROTOCOL.md`.

#### 8. The price, measured on every corpus already seen

Run 15 (v2.0.6, commit `a982b7b`), the same commands as run 13 plus seed 20261015 plain and perturbed and
hand-14, builder's hand, NOT blind, UTC 2026-10-01T04:46:38Z to 2026-10-01T04:52:41Z. Compared with v2.0.5:
run 13 for fifteen results, run 14 (the evaluator, same code) for 20261015 plain, perturbed and hand-14.
Never-events 0 on all eighteen results; every never_event_list is empty; every command exits 0 (the scorer),
every `pipeline_status` is `BLOCKED` (`exit_code` 2: at least one entity blocked, as expected).

**Seventeen of the eighteen results do not move at all** - every count and every metric of `eval/score.py` is
identical to v2.0.5: dev, holdout, stress, seeds 20261011 to 20261015 plain and perturbed, the out-of-pool corpus
of run 5, hand (run 7), hand-9, hand-11. The generator writes the legal form without the second stop and no name
slot of those corpora carries a word of `slot_not_name_word`, a name that is not its identifier's or an own name
other than its header (counted by the builder on the inputs: 0), so the checks of (a) cost nothing there.

| hand-14 (run 14 -> run 15) | v2.0.5 | v2.0.6 |
|---|---|---|
| never-events | 0 | 0 |
| facts exact | 2/64 | 27/64 |
| fields `[TO CONFIRM]` | 63/72 | 37/72 |
| conflicts found / reported that are real | 0/1, 0/0 | 1/1, 1/1 |
| effective holdings exact | 0/5 | 3/5 |
| superseded values linked | 3/7 | 1/7 |
| figures with source | 117/117 | 115/115 |
| blocked wrongly, `[TO CONFIRM]` kept | 5, 7/7 | 5, 7/7 |

The two superseded links lost are those of E-0011's directors: the appointment's director line carries
`Sole Proprietress Henceforth`, so since (a) it is a line no rule explains and every field of E-0011 is
`[TO CONFIRM]` (`DISC-006`) - the price of (a), accepted. The 44 fields `[TO CONFIRM]` of the nine published
hand-14 dossiers (37 gold facts or conflicts and the 7 gold `[TO CONFIRM]`), counted by the builder from the
views: every field of E-0004, E-0006 and E-0013 (`DISC-005`, a document of unrecognised type) and of E-0008 and
E-0011 (`DISC-006`, a line no rule explains), the office of E-0001 and the office and the holders of E-0010
(`DISC-006`), the legal form of E-0012 (`DISC-035`); E-0015 none. The five blocked wrongly are the limits of
section 6: E-0003 "each", E-0005 and E-0009 holder nouns in a sentence, E-0007 "becomes its third member" in the
resolution, E-0014 a header row.

### Known limits of v2.0.6

Each limit is marked with what it does to the entity: **blocks**, **keeps `[TO CONFIRM]`** or **may publish**.
**No known limit may publish.** The residual risk of section 4 is stated there, as `[TO CONFIRM]`.

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
  ("Allocation of the capital", "Capital allocation", "ownership structure", owners, beneficial owners) -
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
- a document of unrecognised type (a type label the rules do not list, e.g. `Minutes`, `Memorandum`, `Extract
  from the test registry`) not older than the latest event of a field: every field (`DISC-005`, `every_field`;
  since v2.0.6 the record says so) - **keeps `[TO CONFIRM]`**; when it holds a line that may state a holding
  (`holders_evidence`), or a holders' table that is not read whole - **blocks** (`OWN-015`; hand-14 E-0005,
  perturbed E-0054 of run 14). Corrected marking: 2.0.5 gave the first outcome only;
- a document of a recognised type with a body line that no rule of its kind explains (`CLS-999`): every field,
  when the document is not older than the latest event (`DISC-006`) - **keeps `[TO CONFIRM]`**; when the line
  may state a holding - **blocks** (`OWN-015`);
- a closed line that states a field of its kind where no rule of its kind read it, or a field its kind does not
  read: that field, when the document is not older than the latest event - **keeps `[TO CONFIRM]`**;
- a holders' table in a document of a kind not read for the holders: read whole and summed, then the holders
  **keep `[TO CONFIRM]`**; not read, or two of them - **blocks**;
- a row of a list of a recognised document whose share is illegible or not typed - every field **keeps
  `[TO CONFIRM]`**, and when the row may state a holding - **blocks**;
- since v2.0.6, a name slot with a word of `slot_not_name_word`, a name beside an identifier that is not its own
  (`CLS-005`), or the entity's own name slot that differs from its `Entity:` header: the line is one no rule
  explains - every field **keeps `[TO CONFIRM]`** (`DISC-006`), and when the line may state a holding - **blocks**.
  A real name that holds such a word (a person or company called `Sole`, `Ora`, `Partnership`...) costs the same;
- since v2.0.6, a company name whose legal form differs from the legal form stated (`S.r.l.s.` against `S.r.l.`
  included, by design) - the name is a
  discrepancy and the legal form **keeps `[TO CONFIRM]`** (`DISC-035`).

Count of limits marked **may publish**: v2.0.4 1, v2.0.5 0 (as written; one marking corrected above), v2.0.6 0.

### Tests and numbers

- `tests/test_d35_forms.py`, 11 tests in 7 classes: the 192 siblings (147 unsafe on the v2.0.5 code, 0 on
  v2.0.6), the exact-form probes on test entities and on the hand-14 variant, the plain documents that still
  publish, the fields check under both scopes, the heading with a participial clause, hand-14 through the
  scorer (never-events 0, `[TO CONFIRM]` kept 7/7, facts exact at least 27, `pipeline_status` names
  `exit_code`).
- Inline rule tests: `classified_lines` 66 -> 83 (`CLS-005` 4 new, `CLS-110` 2 -> 4, `CLS-150` 1 -> 2,
  `CLS-999` 17 -> 26), field rules 61 -> 66 (`EXT-FORM-010` 1 -> 3, `EXT-FORM-020` 1 -> 2, `EXT-HOLD-010` 27 ->
  29), discrepancy rules 21 -> 28 (`DISC-035` 3 new, `DISC-020` 3 -> 4, `DISC-040` 5 -> 8).
  `tests/test_rules.py` counts 90 rules (88 + `CLS-005` + `DISC-035`). 286 tests in all (275 in v2.0.5).
- Measured by the builder on corpora already seen (`eval/history.json` run 15, commit `a982b7b`; NOT blind):
  section 8.

## [2.0.5] - 2026-10-01 (freeze tag `v2.0.5-freeze`; not yet run blind)

### D34 - the limit "may publish" of v2.0.4 closed: every body line of a document of a recognised type is decided

Source: the last known limit of entry 2.0.4 (`CHANGELOG.md:133-143` at `v2.0.4-freeze`), the only one marked
**may publish**: a document of a recognised type was read for the fields of its kind only, so a recognised
document whose text also changed another field left the older value of that field published as a fact.
Decision D34 (2026-10-01, under the owner's delegation of that day): close it before any further blind run, by
class and not by literal strings, and measure the price on every corpus already seen. `OWN-015` stays `block`;
holders written in a sentence stay unread (D31). Measured by the builder's hand on corpora already seen only
(`eval/history.json` run 13): not blind.

The entry 2.0.4 is kept as written (`CHANGELOG.md:100` "One limit may publish" refers to that version). On the
corpora seen, every field that v2.0.5 moves from a value to `[TO CONFIRM]` is counted in section 3 with its cause;
none of the values v2.0.4 published there was a never-event (0 in run 12), so the move is caution, not a second
gap found. A recognised document that states a field of its own kind in a wording its rule does not read already kept
that field `[TO CONFIRM]` in v2.0.4 when the document was current, by `DISC-030`.

#### 1. The rule

- `rules/extract.json:605-871`, new ordered group `classified_lines` (20 rules, first match wins, default last),
  run on every non-empty body line of a document whose type is recognised (`dossier/s1_extract.py:682`
  `classify_line`, `:774` `classified_check`):
  - `CLS-010` a line with no letter or digit (a banner, a rule);
  - `CLS-020` a line of a list that a rule of its kind reads: the heading, a row whose label passes the test of an
    unread document and whose share is typed (`:643` `_share_typed`: a share or a count that is read, or a
    figure that is not read, parameter `slot_share_unread`; a share in other words leaves the row open), the
    last `Total`;
  - `CLS-110` to `CLS-240` the whole line of a clause of its kind (name and form, office, capital and its
    counts, financial figures, resolution, office transfer, appointment, transfer, list headings), with typed
    slots: an amount, a count, an address, a company or person name, a legal form (`slot_*` parameters,
    `rules/extract.json:49-69`); the free words of a slot go through the topic rules of `unread_fields` and
    `holders_evidence` (digits removed) and may name only the fields of the rule;
  - `CLS-250` a label and a typed value (`:717` `_label_line_fields`): the label (at most eight words of letters)
    may name fields of its kind only; the line states the fields of the kind that both the label and the type of
    the value name (`value_topics`), else it is not closed;
  - `CLS-900` a title made of the nouns of `FEV-920` (parameter `title_nouns`, now shared), `CLS-910` the
    closing sentence;
  - `CLS-999` anything else: **the document may change every field**.
- What a line does (`dossier/s1_extract.py:774-817`): a line decided by `CLS-999` makes the document one that may
  change every field (`*`); a closed line whose field no rule of its kind read from that very line (no assertion
  of the field, or one read from another line) or whose field its kind does not read makes it one that may
  change that field. The record carries `classified_checks` (`dossier/s2_record.py:51`,
  `schema/entity_record.schema.json:25`), the run report and the view list them (`dossier/run.py:46`), the
  dossier prints them in section 6 (`dossier/s6_build.py:303`).
- `rules/discrepancy.json:151` new rule `DISC-006` (`dossier/s3_discrepancy.py:121` `classified_that_matter`,
  `:146-149`, `:177`): a field stays `[TO CONFIRM]` when a document of a recognised type that may change it is not
  older than the latest event of the field - the criterion of `DISC-005`. There is no exception for a table that
  agrees with the current one.
- Holders (`dossier/s1_extract.py:736` `_classified_holders`, `dossier/s4_ownership.py:49` and `:87`): a holders'
  table in a document of a kind that is not read for the holders is searched as in an unread document - read
  whole and summed (`OWN-010`), or the holders cannot be summed and `OWN-015` blocks; two such tables block; a
  line decided by `CLS-999` that may state a holding (`holders_evidence`) blocks by `OWN-015`.
  `rules/ownership.json` (note of `unverified_holders_table`, version 2.0.5) and `docs/ASSUMPTIONS.md` say so.
- The audit (`dossier/s7_audit.py:293` `classified_scope`, `:449-465`) is a second implementation: it re-reads
  every source of a recognised type, finds the list blocks by their headings, reads the rows with its own
  grammar (`:264` `_list_row`) and words (`:238` `_Words`), matches the shapes and the label rule with its own
  slot test, re-sums the holders' tables of other kinds, and refuses a record that omits an open line, a field
  stated again where no rule read it, or a line that may state a holding.

**Equivalence with the rule asked for.** The rule asked for: in a document of a recognised type, every body line
that no rule of its kind reads is checked by the test of a line of an unread document (`unread_fields`: a holders'
heading `FEV-910`, a title `FEV-920` and a closing sentence `FEV-930` state no field; anything else may state any
field, `FEV-900`, `FEV-999`). v2.0.5 is at least as strict, in four steps: (a) every non-empty body line is
decided, and the default `CLS-999` is every field; (b) a line means no field only as a title of the nouns of
`FEV-920` (`CLS-900`), the closing sentence of `FEV-930` (`CLS-910`), a heading of a list that a rule of its kind
reads (`CLS-020`, as `FEV-910`) or a line with no letter and no digit (`CLS-010`, which cannot write a value); (c)
every other closed line is a whole fixed statement of named fields with typed values (`CLS-020` rows and Total,
`CLS-110` to `CLS-250`), whose free words pass the topic test of a line of an unread document, and each field it
states is either read from that very line by a rule of its kind - the document is then a source of that field, as
before - or kept `[TO CONFIRM]` by `DISC-006` when the document is not older than the latest event; (d) a line that
may state a holding and is not a row of a list read whole and summed blocks by `OWN-015`, as in an unread document.
So a field is published from an older document only if no line of the newer document can state it. The proof rests
on one premise: a typed slot states nothing but the value of its own field (section 4). `CLS-999` and `DISC-006`
are tested by `tests/test_d34_forms.py` and by 66 inline tests of `classified_lines`.

#### 2. The sibling classes, tested by class (`tests/test_d34_forms.py`)

Five classes in 24 wordings - a separate line, the same line (or the same line as a row or a heading), words of the
pack's own lists (`taken up`, `has its seat at`, `paid in`, a `Directors:` list in an office transfer) and
sentences that change the field without naming it (`put in the whole of the increase`, `receives its post and holds
its meetings at`, `takes over the running of the company`, a bare address, a bare name); for the holders' table: a
table read whole, under a heading of its own, one that does not sum, two tables, rows without a heading. Each
wording runs with no title line, with the generator's own title line of its kind (the office transfer has none) and
with each of the 14 title nouns of `FEV-920`: 379 cases. The base is a deed and a registry extract that agree; the
sibling is dated after both.
Safe = the entity blocked, or every field the text changes `[TO CONFIRM]` and no holding derived from an older
table. Run on the code of `v2.0.4-freeze` (commit `65b0233`) and on v2.0.5:

| Class | Cases | v2.0.4 published wrongly | v2.0.5 |
|---|---|---|---|
| a capital resolution whose new quotas go to a new holder | 80 | 80 (the older holders as a fact, holdings derived) | 0 |
| a transfer notice that also moves the seat | 80 | 64 (the older office; the 16 with the seat in a row blocked) | 0 |
| an appointment that also states a capital change | 64 | 64 (the older capital) | 0 |
| an office transfer that also names a new director | 75 | 60 (the older directors) + 15 runs that failed (the office value took the appointment sentence and the identity check refused the shareable layer) | 0 |
| a resolution that holds a holders' table | 80 | 80 (the older holders, holdings derived) | 0 |

348 of 379 published wrongly on v2.0.4, 15 failed, 16 were safe; on v2.0.5, 0 of 379. The cost side is tested
too: a plain resolution, transfer, appointment and office transfer in the generator's own forms keep every field
`STATED` with no classified check; a resolution with a holders' table that agrees is summed and keeps the holders
`[TO CONFIRM]` (`DISC-006`).

#### 3. The price, measured on every corpus already seen (that cost is accepted)

Run 12 (v2.0.4, commit `4c90d53`) -> run 13 (v2.0.5, commit `f76dfad`), same commands, builder's hand, NOT blind.
Never-events 0 on all fifteen results, before and after; every never_event_list is empty. Dossiers published,
entities blocked wrongly and rightly, `[TO CONFIRM]` kept and the published dossiers whose holders are
`[TO CONFIRM]` do not move on any corpus. Dev, holdout, the four plain corpora (20261011 to 20261014) and the
three hand corpora (runs 7, 9, 11) do not move at all.

| Corpus | Facts exact | Fields `[TO CONFIRM]` | Conflicts found |
|---|---|---|---|
| stress, seed 20261002 | 711 -> 681 of 1285 | 605 -> 635 of 1372 | 16 -> 16 of 47 |
| 20261011 perturbed | 603 -> 568 of 1323 | 744 -> 782 of 1413 | 26 -> 23 of 50 |
| 20261012 perturbed | 686 -> 653 of 1328 | 655 -> 688 of 1396 | 23 -> 23 of 36 |
| 20261013 perturbed | 650 -> 618 of 1379 | 761 -> 796 of 1482 | 21 -> 18 of 53 |
| 20261014 perturbed | 667 -> 652 of 1365 | 726 -> 748 of 1461 | 16 -> 9 of 44 |
| out-of-pool corpus of run 5 | 330 -> 290 of 925 | 611 -> 652 of 986 | 13 -> 12 of 29 |
| hand (run 7), hand-9, hand-11 | 10/10, 32/48, 32/71 (unchanged) | 0/11, 16/51, 39/86 (unchanged) | unchanged |

Where it falls (fields of published dossiers that went from a value to `[TO CONFIRM]`, all by `DISC-006`): stress
31, the four perturbed corpora 42, 43, 35, 23, out-of-pool 50 - 224 in all. 200 of them (stress 31, perturbed
38, 36, 35, 23, out-of-pool 37) come from a closed line that the rule of its kind does not read - mostly lines of a
registry extract (`Seat:`, `Share capital:` with an amount in words or `paid up`, `Board:`), some figure labels of a
financial statement - in an **intermediate** edition that a later source reading the same field supersedes;
`DISC-006` keeps the field `[TO CONFIRM]` because it compares with the latest event, as `DISC-005` does, not with
the latest source. 20 come from a line decided by `CLS-999` in the latest document (perturbed 20261011 4, 20261012
7, out-of-pool 9) and 4 from a closed line in the latest document (out-of-pool). A narrower criterion - a classified
document older than a later source that reads the field does not count - could win back up to those 200; it is
not written and not measured: it publishes more, and needs its own proof and the owner's decision.

Every figure published still carries its source (stress 2868/2868, the four perturbed corpora 2915, 2909, 3086,
2965, out-of-pool 1787, each N of N). The shapes of `classified_lines` were written by the builder with the
corpora already seen in view - the generator's own clauses and the variants seen (the currency after the figure,
`nominal` and `issued` capital, `wholly subscribed and wholly paid in`, `domiciled at`, `go up` or `be raised`, a
second sentence `It is split into N quotas`, from hand-11 E-0003, which otherwise blocked) and the label rule
`CLS-250` - so these numbers are not a blind measure. A wording the shapes do not know opens the line (`CLS-999`):
it costs coverage, never a fact.

#### 4. Residual risk of the premise (not a known limit: no case is known)

The proof of section 1 assumes that a typed slot states nothing but the value of its own field. A name or address
slot admits only capitalised words of letters and a few particles (a company name of up to eight words and its
legal form, a person name of up to five, an address made of a street, a house number, a town and a province in
parentheses), no other figure and no identifier; an amount or a count slot admits a figure and its currency only.
The words of a slot are judged by the same lists of `unread_fields` and `holders_evidence` that run 11 showed incomplete for whole
sentences. A change of another field written entirely inside such a slot, in words those lists do not know, would
not be seen; if one is found it publishes, and it goes into a new version under a new tag. None is known; the
blind protocol asks the next hand for it.

### Known limits of v2.0.5

Each limit is marked with what it does to the entity: **blocks**, **keeps `[TO CONFIRM]`** or **may publish**.
**No known limit may publish** (v2.0.4: one). The residual risk of section 4 is not a known limit and is stated
there.

- holders stated in a sentence rather than in a list under a heading (hand-9 E-0003 and E-0007): not read, by
  the owner's risk decision D31 - **blocks**;
- a qualifier meaning "current" in free words in the heading (`Shareholders once the transfer has taken
  effect:`, hand-11 E-0002) - **blocks**;
- a table with a header row (`| Identifier | Holder | Share |`, hand-11 E-0011, hand-9 E-0003) - **blocks**;
- per mille (`625‰`, hand-11 E-0014) - **blocks**;
- nominal amounts per holder, with no share and no count - **blocks**;
- a holders' heading with an explicit date (`Holders at 16 February 2026:`) and headings of other nouns
  ("Allocation of the capital", "Capital allocation", "ownership structure", owners, beneficial owners) -
  **blocks**;
- a heading without a final `.` or `:` that is not the whole line or is not followed by an item line: not a
  heading - holders **block**, directors **keep `[TO CONFIRM]`**;
- two holders' headings in one document - **blocks**; two directors' headings - **keeps `[TO CONFIRM]`**;
- a Total line that is not the last line of the table, that cannot be read, or that is in another unit than
  the rows - **blocks** (a Total that differs from the exact sum blocks by `OWN-010`, by design);
- a share before the holder written in words or as a count - **blocks**;
- a share in words in the same line as a date in words (`On the third of July ... received a third`) -
  **blocks**;
- counts without a total in the same document, with two totals, mixed with shares in one table, or in a
  document of unrecognised type - **blocks**;
- shares in words beyond whole per cent and simple fractions: `half` alone, decimals in words, a number that
  does not agree (`two third`, `one thirds`), more than a hundred per cent - **blocks**;
- a label with nested or second parentheses - **blocks**;
- a document whose header cannot be read, a document date in words among them: it may change every field and
  its holders cannot be summed (`OWN-015`; 41 of the 44 entities blocked wrongly in the out-of-pool corpus of
  run 5) - **blocks**;
- shares planted as illegible block by design (D26): 2, 2, 1, 3, 3, 3, 3, 0, 0, 2, 2 entities of dev, holdout,
  stress and the seeds 20261011 to 20261014, plain and perturbed - **blocks**;
- a document of unrecognised type not older than the latest event of a field: every field (`DISC-005`,
  `every_field`); the rules of `unread_fields` decide nothing under the default - **keeps `[TO CONFIRM]`**;
- since v2.0.5, a document of a recognised type with a body line that no rule of its kind explains
  (`CLS-999`): every field, when the document is not older than the latest event (`DISC-006`) - **keeps
  `[TO CONFIRM]`**; when the line may state a holding - **blocks** (`OWN-015`);
- since v2.0.5, a closed line that states a field of its kind where no rule of its kind read it (a reworded
  label, an amount in words, a second clause or list), or a field its kind does not read: that field, when the
  document is not older than the latest event, even if a later source reads the field (section 3) - **keeps
  `[TO CONFIRM]`**;
- since v2.0.5, a holders' table in a document of a kind not read for the holders: read whole and summed, then
  the holders **keep `[TO CONFIRM]`** (no exception for a table that agrees); not read, or two of them -
  **blocks**;
- since v2.0.5, a row of a list of a recognised document whose share is illegible or not typed: the row is not
  closed (`CLS-999`) - every field **keeps `[TO CONFIRM]`**, and when the row may state a holding
  (`holders_evidence`) - **blocks**.

Count of limits marked **may publish**: v2.0.4 1, v2.0.5 0.

### Tests and numbers

- `tests/test_d34_forms.py`, 5 tests in 2 classes: the 379 siblings (348 published wrongly and 15 failed on the
  v2.0.4 code, 0 on v2.0.5), the title nouns of the rule, the plain documents that still publish, a table that
  agrees and still keeps the holders, a capital raise that does not state the subscription (subscribed and
  paid-in `[TO CONFIRM]` by `DISC-030`, as in v2.0.4).
- Inline rule tests: `classified_lines` 66 (17 of them on `CLS-999`), `DISC-006` 3; `tests/test_rules.py` counts
  88 rules (67 + 20 `CLS` + `DISC-006`) and checks that the inline tests of `classified_lines` bite.
  `tests/test_d30b_forms.py` reads the title nouns from the shared parameter. 275 tests in all.
- An inline test that expects what a line may change depends on the field rules: the expectation of `CLS-190`
  sits on a wording that no field rule reads, so that scenario S09, which adds a field rule on top for the other
  wording, still passes.
- Measured by the builder on corpora already seen (`eval/history.json` run 13, commit `f76dfad`; NOT blind):
  section 3. hand-11 stays at 10 of 15 published, 3 blocked wrongly (the three limits above), `[TO CONFIRM]`
  kept 12/12.

## [2.0.4] - 2026-10-01 (freeze tag `v2.0.4-freeze`; not yet run blind)

### D30b - blind run of v2.0.3, run 11: two never-events (DISC-005 scope, FEV-040), undeclared blocks, scorer gap

Source: the evaluator's blind run of `v2.0.3-freeze`, `eval/history.json` run 11, seed 20261014 and the hand
corpus `eval/blind/hand-11/` (15 entities, 33 documents): 0 never-events on the plain and perturbed corpora,
**2 on the hand corpus**, both on entity E-0015. A notice to creditors (a document of unrecognised type)
says that the equity was raised by a contribution in kind and that the seat moves. The rules of
`unread_fields` scoped that sentence to the capital, the financial figures and the office; by `FEV-040` a
capital increase changes the capital, never the holders. So the holders of the older registry extract were
published as a fact, with the effective holding derived from them, where the gold says they cannot be decided.

**`CHANGELOG.md:63` at `v2.0.3-freeze` (entry 2.0.3) was false for `FEV-040`.** The heading said that each known limit "still
blocks the entity, or keeps the field `[TO CONFIRM]`"; the `FEV-040` limit (`:81-82` at that tag) and the
residual risk of the scope (`:83-86`) could publish a field as a fact, and on E-0015 one did. The same heading
was false also for the limit at `:79-80` (classified documents of other kinds are not searched for holders'
tables): it may publish too (see the last limit below, not fixed). The 2.0.3 entry is left as it was written.

Also from run 11: 8 of the 15 hand entities were blocked wrongly, 6 of them on forms that 2.0.3 does not
declare; and `eval/score.py` scored nothing in an entity that was not published, so the gold `[TO CONFIRM]`
values and file-name divergences of blocked entities were never counted.

#### 1. DISC-005: every field again

- `rules/discrepancy.json:32` `unread_document_scope`: `fields_it_may_state` (v2.0.3) -> `every_field`, the
  v2.0.0-v2.0.2 behaviour. An unread document that is not older than the latest event of a field keeps every
  field `[TO CONFIRM]`, whatever its title or its lines say. `fields_it_may_state` stays allowed and OFF; its
  risk is written in the note of the parameter and in `docs/ASSUMPTIONS.md`. Turning it on is a risk decision
  of the owner, not a reading.
- Proof that the narrow scope is not safe, `tests/test_d30b_forms.py` class `S_UnreadScopeAdversarialSiblings`:
  10 sibling documents of hand-11 E-0009, E-0010 and E-0015 (E-0009 as written: an office sentence beside a
  capital doubled without the word capital; the doubled capital alone; E-0010's transfer without the word
  holder; E-0015's contribution in kind and new seat; a contribution in kind with the holders not named; a
  merger with and without the word merger; a transfer worded as a gift; a capital cut and a capital raised in
  figures without the word capital), each with every title noun of `FEV-920` (14), with a title of its own
  and with no title line: 160 cases. With the default every field stays `[TO CONFIRM]` and no effective
  holding is derived in all 160. On the v2.0.3 code, where the narrow scope was the default, 46 of the 160
  publish a field the document changes (E-0009 as written 15, E-0010 15, E-0015 16); on the v2.0.4 code with
  the option switched on, the E-0010 sibling under a `Notice` title still publishes the holders
  (`test_the_narrow_scope_is_not_safe_and_stays_off`). The E-0009 and E-0010 title siblings keep their fields
  `[TO CONFIRM]`; E-0015 has 0 never-events.
- `dossier/rules_engine.py` `with_params()`: an inline test may run with another allowed parameter value
  (`"params"`); the DISC-005 tests pin `every_field`, the DISC-040 tests of the option pin
  `fields_it_may_state` (`dossier/s3_discrepancy.py` `run_inline_tests`).
- Coverage cost, before -> after, on every corpus already seen (fields `[TO CONFIRM]` in published dossiers;
  published dossiers with the holders `[TO CONFIRM]`): stress 433 -> 605 of 1372, 0 -> 0; seed 20261011
  perturbed 512 -> 744 of 1413, 8 -> 45; 20261012 perturbed 462 -> 655 of 1396, 4 -> 43; 20261013 perturbed
  543 -> 761 of 1482, 3 -> 54; 20261014 perturbed 477 -> 726 of 1461, 3 -> 54; out-of-pool corpus of run 5
  475 -> 611 of 986, 7 -> 34; hand-9 5 -> 16 of 51, 0 -> 2. Dev, holdout, the four plain corpora and the hand
  corpus of run 7 do not move. The number of published dossiers does not move on any of these corpora.

#### 2. The undeclared forms of run 11, read by class

| Class | Found in run 11 | v2.0.3 | v2.0.4 |
|---|---|---|---|
| D1. a heading without a final `.` or `:` | 7 hand deeds: E-0001, E-0002, E-0003, E-0005, E-0006, E-0011, E-0012 (`4. Shareholders`, `Article 4. Stockholders`, `§ 4 Holders`) | not read, blocked | read only when it is the whole line and the next line is an item of the list |
| D2. a day ordinal with a month (`the third of July`, `July the fifth`, `the twenty-fifth day of March`) and `third parties` | E-0008 memorandum | read as a share in words (`HEV-010`), blocked | neutral; a share in words beside a date still blocks |
| D3. the directors' heading with a clause number (`(5) Directors:`, `§ 5 Directors`, `Article 5. Directors`) | E-0013 | not read | read as the holders' heading is |
| D4. dot leaders as separator and a last line `Total` | E-0006 | not read, blocked | read; the Total must equal the exact sum of the rows, else `OWN-010` blocks |
| D5. the share before the holder (`- 60% P-001 (...)`, `1. 3/5 - Name (P-001)`) | E-0012 | not read, blocked | read for per cent and n/d |

Root causes and what changed (file:line of v2.0.3 -> v2.0.4):

- D1, D3: `rules/extract.json:23` (`holders_heading` ends in `[.:]$`) and `:257` (directors: one literal form,
  `^(?:\d+\. )?Directors...[.:]$`); `dossier/s1_extract.py:398-402` (`_extract_list` took the first heading
  only) -> `rules/extract.json:23-29` (`holders_heading_body`, `holders_heading`, `holders_heading_bare`,
  `directors_heading_body` with `clause_number`, `directors_heading`, `directors_heading_bare`), `:243` and
  `:285` (`line_matches_bare`), `dossier/s1_extract.py:444-462` (`_list_headings`: the bare form only before an
  item line; two headings of one list in one document abstain - holders block, directors stay `[TO CONFIRM]`).
- D2: `rules/extract.json:312` (`neutral_phrases`) -> `:346`, with the parameters `month_names` and
  `day_ordinals` (`:40-41`).
- D4: `rules/extract.json:27` (`item_separator`) -> `:33` (dot leaders) and `:34` (`item_total`);
  `dossier/s1_extract.py:347` (`_read_items`) -> `:370-436` (a Total read only as the last line of the table,
  in the unit of the rows, carried as `stated_total`); `dossier/s4_ownership.py:54` (`sum_checks`) -> `:54-63`
  (`table_check`: whole only when the rows sum to the whole AND the Total equals that sum) and `:115`
  (`violation_reason`); `schema/entity_record.schema.json` (`stated_total`); `rules/ownership.json` `OWN-010`
  (rationale and two tests).
- D5: `rules/extract.json:35` (`share_token_first`) and `:245` (`item_matches_share_first`);
  `dossier/s1_extract.py:163` (`_Items`: the item grammar, then the share-first grammar).
- The audit reads the same forms with its own code: `dossier/s7_audit.py:48` (v2.0.3, `_SHARE_IN_LINE` only)
  -> `:47-54` (`_SEP` with dot leaders, `_SHARE_FIRST_LINE`, `_TOTAL_LINE`), `:94-132` (`_holder_lines`: a Total
  that is not the exact sum is refused) and `:135` (`_is_holder_row`).

#### 3. The scorer counts what is not published

`eval/score.py:88-96` (v2.0.3: an entity not published was skipped with `continue`) -> `:91-99` and
`:111-117`: for every entity not published the scorer counts, separately, the gold `[TO CONFIRM]` values and
the gold file-name divergences, and the same two counts for the entities blocked wrongly
(`blocked_entities_gold_to_confirm`, `blocked_wrongly_entities_gold_to_confirm`,
`blocked_entities_filename_divergences_gold`, `blocked_wrongly_entities_filename_divergences_gold`). They are
printed next to the never-events and are not never-events; no other count changes.

### Known limits of v2.0.4

Each limit is marked with what it does to the entity: **blocks**, **keeps `[TO CONFIRM]`** or **may publish**.
One limit may publish; it is the last one, and it is not fixed in v2.0.4.

- holders stated in a sentence rather than in a list under a heading (hand-9 E-0003 and E-0007): not read, by
  the owner's risk decision - **blocks**;
- a qualifier meaning "current" in free words in the heading (`Shareholders once the transfer has taken
  effect:`, hand-11 E-0002) - **blocks**;
- a table with a header row (`| Identifier | Holder | Share |`, hand-11 E-0011, hand-9 E-0003) - **blocks**;
- per mille (`625‰`, hand-11 E-0014) - **blocks**;
- nominal amounts per holder, with no share and no count - **blocks**;
- a holders' heading with an explicit date (`Holders at 16 February 2026:`) and headings of other nouns
  ("Allocation of the capital", "Capital allocation", "ownership structure", owners, beneficial owners) -
  **blocks**;
- a heading without a final `.` or `:` that is not the whole line or is not followed by an item line: not a
  heading - holders **block**, directors **keep `[TO CONFIRM]`**;
- two holders' headings in one document - **blocks**; two directors' headings - **keeps `[TO CONFIRM]`**;
- a Total line that is not the last line of the table, that cannot be read, or that is in another unit than
  the rows - **blocks** (a Total that differs from the exact sum blocks by `OWN-010`, by design);
- a share before the holder written in words or as a count - **blocks**;
- a share in words in the same line as a date in words (`On the third of July ... received a third`) -
  **blocks**;
- counts without a total in the same document, with two totals, mixed with shares in one table, or in a
  document of unrecognised type - **blocks**;
- shares in words beyond whole per cent and simple fractions: `half` alone, decimals in words, a number that
  does not agree (`two third`, `one thirds`), more than a hundred per cent - **blocks**;
- a label with nested or second parentheses - **blocks**;
- a document whose header cannot be read, a document date in words among them: the document may change every
  field and its holders cannot be summed, `OWN-015` (41 of the 44 entities blocked wrongly in the out-of-pool
  corpus of run 5) - **blocks**;
- shares planted as illegible block by design (D26): 2, 2, 1, 3, 3, 3, 3, 0, 0, 2, 2 entities of dev,
  holdout, stress and the seeds 20261011 to 20261014, plain and perturbed - **blocks**;
- a document of unrecognised type not older than the latest event of a field: every field (DISC-005,
  `every_field`); the rules of `unread_fields` (`FEV-040` and the others) decide nothing under the default -
  **keeps `[TO CONFIRM]`**. The option `fields_it_may_state` is off; on, it is not safe (section 1);
- **a document of a recognised type is read for the fields of its kind only** (`rules/extract.json`
  `doc_kinds`, `expected_fields`: a resolution on share capital changes the capital, a share transfer notice the
  holders, an appointment the directors, an office transfer the office). A recognised document whose text also
  changes another field - a capital resolution whose new quotas go to a new holder, a transfer notice that
  also moves the seat, a resolution that holds a holders' table - is not searched for it, and the older value
  of that field is published as a fact - **may publish**. Not fixed in v2.0.4; it is the same sentence-level
  gap as run 11, for documents whose type is recognised. Measured by the builder on corpora already seen: on
  the plain corpora every body line of a classified document that no rule reads is a title of `FEV-920`
  (dev 897 documents, seed 20261014 893: none may state a field), so a rule that keeps every field
  `[TO CONFIRM]` after such a line would cost nothing there; it is not written, not tested and not measured on
  the reworded corpora.

### Tests and numbers

- `tests/test_d30b_forms.py`, 26 tests in 8 classes. Run on the v2.0.3 code (with the hand-11 corpus copied
  in), 14 fail or error: `test_default_scope_is_every_field`, `test_every_sibling_with_every_title_keeps_every_field`
  (46 of 160 cases), `test_a_sibling_with_a_holders_table_of_the_same_holders_keeps_the_holders`, the bare
  holders' and directors' headings (7 and 7 cases), `test_two_directors_headings_abstain`,
  `test_dates_in_words`, `test_dot_leaders_with_a_total_equal_to_the_sum`, `test_a_total_that_differs_blocks_by_own_010`,
  `test_counts_with_a_total`, `test_share_first`, `test_share_first_that_does_not_sum_blocks_by_own_010`,
  `test_hand_11` (2 never-events) and `test_unpublished_entities_are_counted_not_scored` (error: no such count).
  12 pass on both: the limits that still block (class `F5_StillNotRead`, two tests of F1 and one each of F2
  to F4), the title nouns, the narrow option kept off, and `test_hand_9_and_hand`.
- Changed to the every-field default: `tests/test_d30_forms.py` (C1 shareholding structure, class C6),
  `tests/test_holders_forms.py` (`test_register_of_members_with_a_reworded_heading`), `tests/test_never_event.py`
  (the document of unknown type after the deed: every field by default, only the capital with the option).
- Inline rule tests: `rules/extract.json` `EXT-HOLD-010` 27 (13 new), `EXT-DIR-010` 10 (6 new), `HEV-999` and
  `HEV-010` 3 new each; `rules/ownership.json` `OWN-010` 2 new; `rules/discrepancy.json` `DISC-005` 2 new.
  No rule added: `tests/test_rules.py` still counts 67 rules. 270 tests in all.
- Measured by the builder on corpora already seen (`eval/history.json` run 12, commit `4c90d53`; NOT blind),
  v2.0.3 -> v2.0.4: hand-11 never-events 2 -> 0, published 5 -> 10 of 15, blocked wrongly 8 -> 3 (E-0002,
  E-0011, E-0014: limits above), `[TO CONFIRM]` kept 9/10 -> 12/12; never-events 0 on every other corpus, as
  before; the coverage cost of section 1. Every never_event_list is empty.

## [2.0.3] - 2026-10-01 (freeze tag `v2.0.3-freeze`; not yet run blind)

### D30 - forms found by the blind run of v2.0.2, run 9; DISC-005 over-reach; never_event_list cap

Source: the evaluator's blind run of `v2.0.2-freeze`, `eval/history.json` run 9, seed 20261013 and the hand
corpus `eval/blind/hand-9/`: 0 never-events on every corpus; 4 of 9 hand-written entities blocked wrongly
(E-0003, E-0007, E-0008, E-0009); on the perturbed corpus 54 of the 144 published dossiers with the holders
`[TO CONFIRM]` and 761 of 1482 fields abstained. Owner decision D30 (2026-10-01): classify the forms by class,
generalise the rules first and the code second; counts and nominal amounts are read only with a total stated
in the same document; an ambiguous form stays blocked. `OWN-015` and `unverified_holders_table` stay `block`
(D26). The asymmetry is unchanged: a wrong published figure is worse than any number of blocks.

Form classes, from the hand-9 documents (the entity where each was found) and generalised:

| Class | Found in run 9 | v2.0.2 | v2.0.3 |
|---|---|---|---|
| C1. holders' heading: "of record", "registered", "entered in the register of members"; a qualifier meaning "current" in parentheses or after a comma; "(synthetic)"; clause numbers `4.`, `(4)`, `iv.`, `Article 4`, `§ 4`; nouns quotaholdings, shareholding(s), shareholding structure | E-0007 `Shareholders of record:`, `Shareholding structure at the document date (synthetic):`; E-0009 `Holders (as at the document date):` | not read, blocked | read |
| C2. holder line: markers `-` `*` `•` `–` `—` `·` `1.` `1)` `(1)` `a)` `(a)` `iv)`; identifier first (label optional) or name first `Name (P-001)`; separators `:`, ` - `, `\|`, tab, space | E-0009 `1) P-002 (...) - 20%`; E-0008 `Elmo Ipotetici (P-010): 200 quotas` | not read, blocked | read |
| C3. share in words: `60 per cent`, `60 percent`, `60 pct`, whole per cent in words (`thirty per cent`, `thirty-five per cent`), simple fractions in words (`one third`, `two fifths`, `a half`, `three quarters`) | E-0007 `thirty per cent` | not read, blocked | read |
| C4. counts of quotas or shares with exactly one total stated in the same document (`divided into 300 quotas`, `consisting of`, `a total of`): each share is count/total, exact; counts that do not add up to the total do not sum (`OWN-010`) | E-0008 deed | not read, blocked | read |
| C5. directors' lines in the same item grammar (numbered, name first) | - | not read | read |
| C6. a document of unrecognised type blocks only the fields it may state (`DISC-005`) | E-0006 ledger, E-0007 statement, E-0008 certificate; the 54 dossiers of the perturbed corpus | every field `[TO CONFIRM]` | the fields it may state |
| C7. holders in a sentence; nominal amounts per holder; a pipe table with a header row | E-0003 deed and extract, E-0007 deed | blocked | still blocked (known limits) |

Root causes and what changed (file:line of v2.0.2 -> v2.0.3):

- C1: `rules/extract.json:19-21` (v2.0.2) - the heading grammar knew no "of record", no qualifier in
  parentheses and none of the nouns above. -> `rules/extract.json:19-23`: parameters `holders_heading`,
  `holders_heading_nouns`, `holders_heading_registered`, `clause_number`.
- C2: `rules/extract.json:217` and `:235` (v2.0.2) - one item form, `- ID (label): share`. -> `:232` and `:258`:
  `item_matches` built from the parameters `list_marker`, `item_holder`, `item_person`, `item_separator`.
  A label with nested or second parentheses is no longer read: v2.0.2 read it with a greedy label; v2.0.3
  abstains (a tightening).
- C3: `dossier/lib/numbers.py:81-97` (v2.0.2, `parse_share`: figures with `%` and `n/d` only) ->
  `dossier/lib/numbers.py:89-165` (`words_to_int`, `_share_in_words`, `parse_share`, `parse_count`; a count
  is never a share).
- C4: no count was read in v2.0.2. -> `rules/extract.json:31` (parameter `count_total`) and
  `dossier/s1_extract.py:328` (`count_total`), `:347` (`_read_items`); the audit re-derives the shares from
  the quote with its own parser (`dossier/s7_audit.py:46-56`, `:88`).
- C6, the DISC-005 over-reach: `dossier/s3_discrepancy.py:79-84` (v2.0.2, `unread_that_matter`) ignored the
  field: every unclassified document not older than the latest event blocked every FACT field of its entity.
  -> `dossier/s3_discrepancy.py:79-117`: new parameter `unread_document_scope` = `fields_it_may_state`
  (`rules/discrepancy.json:31`, `[TO CONFIRM with legal]`, allowed also `every_field`, the v2.0.2 behaviour);
  `fields_check` of each unclassified document (`dossier/s1_extract.py:477-526`) by the new ordered group
  `unread_fields` (`rules/extract.json:414`, `FEV-010`..`FEV-060` topics, all tried; `FEV-900` a figure, an
  entity identifier, an amount or a label -> every field; `FEV-910` a holders' heading, `FEV-920` a title
  marked as invented, `FEV-930` a closing sentence -> no field; default `FEV-999` -> every field). A
  document whose header has another problem may change every field. A shareholders table read whole that
  agrees with the current holders releases the holders field (`unread_agreeing`). The audit re-derives the
  scope from the source lines by its own code (`dossier/s7_audit.py:146-192`).
- The never_event_list cap: `eval/score.py:190` (v2.0.2) `never[:50]` -> `never`: every never-event is
  listed; the count was never capped.

Found by the builder before the tag, and closed: in the first commit of this change (`e779adc`) the default
`FEV-999` said "no field", so a sentence with no topic word, no figure and no identifier ("Ugo Apparenti now
runs the company.") would have let an older fact be published. Commit `5a13f3f` makes the default keep every
field; on the corpora already seen only holders' headings and titles fell to it, so no number moved.

### Known limits of v2.0.3 (each still blocks the entity, or keeps the field `[TO CONFIRM]`)

- holders stated in a sentence rather than in a list under a heading (hand-9 E-0003 and E-0007 deeds);
- nominal amounts per holder (no share, no count);
- a table with a header row (`| Holder | Nominal quota | Share |`);
- a holders' heading with an explicit date (`Holders at 16 February 2026:`) and headings of other nouns
  ("Allocation of the capital", "Capital allocation", "ownership structure", owners, beneficial owners);
- counts without a total in the same document, with two totals, mixed with shares in one table, or in a
  document of unrecognised type;
- per mille;
- shares in words beyond whole per cent and simple fractions: `half` alone, decimals in words, a number
  that does not agree (`two third`, `one thirds`), more than a hundred per cent;
- a label with nested or second parentheses (read by v2.0.2, abstained by v2.0.3);
- two holders' tables in one document;
- a document date in words: the header cannot be read and the document may change every field (41 of the
  44 entities still blocked wrongly in the out-of-pool corpus of run 5);
- classified documents of other kinds (resolutions, appointments, office transfers, financial summaries)
  are not searched for holders' tables;
- a text of a capital increase or reduction is read as a change of the capital, never of the holders
  (`FEV-040`; assumption, `[TO CONFIRM with legal]` with `unread_document_scope`);
- the rules of `unread_fields` are word lists: a topic word present by chance keeps its field
  `[TO CONFIRM]` (coverage cost; for example "named" in a certificate keeps name and legal form); a line with
  a topic word that also changes another field without naming it keeps only the named field - the residual
  risk of the scope, declared here;
- shares planted as illegible block by design (D26): 2, 2, 1, 3, 3, 3, 3 entities of the generated corpora
  of dev, holdout, stress and the seeds 20261011 and 20261012, plain and perturbed.

### Tests and numbers

- `tests/test_d30_forms.py`, 31 tests in 7 classes (C1..C7 above). Run on the v2.0.2 code, 19 fail or error:
  every C1, C2, C3 and C5 test, the three C4 tests that read counts with a total, three C6 tests (ledger,
  register, minutes of a change of seat, which v2.0.2 kept every field `[TO CONFIRM]`) and
  `test_nested_parentheses` (v2.0.2 read the label), plus `test_fields_check_of_a_header_problem_is_every_field`
  (error: no `fields_check`). 12 pass on both: the limits of C7 but one, the two C4 limits, and the three C6
  tests that keep every field (`test_a_sentence_no_rule_explains_keeps_every_field` fails on `e779adc`).
- Also failing on v2.0.2: `tests/test_numbers.py` `test_per_cent_words_are_read` (9 of 10 forms) and
  `test_counts_are_not_shares` (error), `tests/test_never_event.py` `test_never_event_list_is_never_capped`
  and `test_unknown_document_type_after_the_deed_blocks_the_facts_it_may_change`, and
  `tests/test_holders_forms.py` `test_register_of_members_with_a_reworded_heading` (now published with the
  holders stated). 243 tests in all; `tests/test_rules.py` counts 67 rules.
- Measured by the builder on corpora already seen (`eval/history.json` run 10, commit `5a13f3f`; NOT blind),
  v2.0.2 -> v2.0.3: hand-9 published 4 -> 6 of 9, blocked wrongly 4 -> 2; out-of-pool corpus of run 5
  published 44 -> 94, blocked wrongly 94 -> 44; fields `[TO CONFIRM]` stress 605 -> 433, seed 20261011
  perturbed 744 -> 512, 20261012 perturbed 655 -> 462, 20261013 perturbed 761 -> 543; published dossiers with
  the holders `[TO CONFIRM]` 33 -> 3, 45 -> 8, 43 -> 4, 54 -> 3. Dev, holdout, the plain corpora and the hand
  corpus of run 7 do not move. Never-events 0 on every corpus, and every never_event_list empty.

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
