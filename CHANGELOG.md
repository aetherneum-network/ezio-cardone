# Changelog

SYNTHETIC - proof pack of a synthetic AI agent; every entity, person, deed and registry extract is invented.

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
