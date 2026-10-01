# Changelog

SYNTHETIC - proof pack of a synthetic AI agent; every entity, person, deed and registry extract is invented.

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
