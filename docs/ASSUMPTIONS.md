# Legal assumptions of the pack

SYNTHETIC - written from the rule files by `tools/assumptions.py`; do not edit by hand.

The pack makes 12 assumptions that only a qualified professional can confirm. The author is a
synthetic AI agent: not a lawyer, a notary, an accountant or an auditor. None of these assumptions is
legal advice and none has been reviewed by a legal professional. Each one is a parameter of a rule file,
is printed in every dossier, and carries the status `[TO CONFIRM with legal]` until someone qualified
changes it. Changing a value is a change of a rule file (with its inline tests), never of an output.

## 1. `bare_capital_nature`

- File: `rules/figure_nature.json`
- Value in v2.0: `resolved`
- Status: [TO CONFIRM with legal]

A clause that gives one amount as 'the share capital' with no other cue is read as the resolved (nominal) capital only. Whether that amount is also subscribed or paid in is not inferred.

## 2. `event_supersedes_earlier_state`

- File: `rules/discrepancy.json`
- Value in v2.0: `true`
- Status: [TO CONFIRM with legal]

A later event document (deed, resolution, transfer, appointment, office transfer) makes every earlier value of the field historical. What an event document proves against a registry extract is a legal question: the pack only orders documents by date.

## 3. `later_edition_supersedes_same_series`

- File: `rules/discrepancy.json`
- Value in v2.0: `true`
- Status: [TO CONFIRM with legal]

Within one series of state documents (registry extracts, holders' ledger, the financial summary of one year) only the latest edition is a current witness; earlier editions are history.

## 4. `same_day_state_is_current`

- File: `rules/discrepancy.json`
- Value in v2.0: `true`
- Status: [TO CONFIRM with legal]

A state document dated on the same day as the latest event is treated as current: if it differs, the difference is shown rather than assumed away.

## 5. `adjudication`

- File: `rules/discrepancy.json`
- Value in v2.0: `none`
- Status: [TO CONFIRM with legal]

No source is preferred. A human adjudicates.

## 6. `unread_document_blocks_fact`

- File: `rules/discrepancy.json`
- Value in v2.0: `true`
- Status: [TO CONFIRM with legal]

A document of the entity that could not be classified (unknown type, broken header) may change a field. If it is not older than the latest event document of a field - or has no valid date, or the field has no event document - the field is [TO CONFIRM]. Which fields it may change: parameter unread_document_scope. Added after the first stress run (eval/history.json, run 2).

## 7. `unread_document_scope`

- File: `rules/discrepancy.json`
- Value in v2.0: `every_field`
- Status: [TO CONFIRM with legal]

every_field (v2.0.0-v2.0.2, and again the default since v2.0.4, D30b): an unread document that is not older than the latest event document of a field may change every field, whatever its title or its lines say. fields_it_may_state (the default of v2.0.3 only; still allowed, OFF): a document whose only problem is its type may change only the fields its body may state (rules/extract.json unread_fields, recorded as fields_check), and the shareholders only if its holders' check is not 'no_table'; a holders' table read whole that equals the one current table does not make the shareholders [TO CONFIRM]. Its risk, shown by the blind run of v2.0.3 (eval/history.json run 11, hand entity E-0015): a sentence that changes a field without naming it (a capital raised by a contribution in kind that also changes the holders; a merger; a transfer worded without the word holder) keeps only the fields its topic words name, so the other field is published as fact; and a title word of FEV-920 (Notice, Memorandum, Letter...) can narrow the scope of a whole document. No test shows that this scope never publishes a field an unread document may change, so it stays off; switching it on is a risk decision, not a reading. Since v2.0.6 (D35, hand-14 E-0013): under every_field the fields check of an unread document records every field ('*') and names the scope; what its lines alone would name (rules/extract.json unread_fields, not applied under this scope) is kept as a note, never as the fields it may change.

## 8. `unreadable_current_source_blocks_fact`

- File: `rules/discrepancy.json`
- Value in v2.0: `true`
- Status: [TO CONFIRM with legal]

When one current source of a field could not be read, the value of the other current sources is not shown as fact: the unread source may disagree. Added after the first stress run (eval/history.json, run 2).

## 9. `sum_must_equal`

- File: `rules/ownership.json`
- Value in v2.0: `1/1`
- Status: [TO CONFIRM with legal]

The holders of an entity must sum to exactly the whole. 99.99% and 100.01% are both refused. Whether a real cap table may legitimately not sum to the whole (treasury shares, unallotted capital) is a legal question and is not modelled.

## 10. `cycle_policy`

- File: `rules/ownership.json`
- Value in v2.0: `abstain`
- Status: [TO CONFIRM with legal]

With cross-holdings the look-through to natural persons depends on a rule. 'abstain' reports the cycle and writes the effective holding [TO CONFIRM]. 'closure' computes the exact limit of the look-through (the solution of x = direct + cross * x, in fractions) and says so next to each figure.

## 11. `unverified_holders_table`

- File: `rules/ownership.json`
- Value in v2.0: `block`
- Status: [TO CONFIRM with legal]

A holders' table of the entity that could not be summed (a table not read, a document expected to state the holders where no table was found, a document not classified or rejected) leaves the sum to the whole unverified. 'block' (default) blocks the build of that entity, as a table that does not sum would: the unread table may be the one that does not sum. 'report' publishes the dossier with the holders [TO CONFIRM], as v2.0.0 did. Added after the blind run of 2026-09-30 (eval/history.json, run 5): 8 dossiers whose unread table did not sum were published. The price is coverage: every entity with an unread holders' table is blocked. Since v2.0.2 (owner decision D26 of 2026-09-30: the value stays 'block') a document not classified is checked for its holders only (rules/extract.json, holders_evidence): when its body has no holders' table and no line that may state a holding, or when every table in it is read whole and summed, it is not an unread table; in every other case it still is. Since v2.0.5 (decision D34) a document of a recognised type is checked the same way: a line of it that no rule of its kind explains (rules/extract.json classified_lines) and that may state a holding (holders_evidence), or a holders' table in a document of a kind that is not read for the holders that is not read whole and summed, leaves the sum unverified.

## 12. `identification_source`

- File: `rules/extract.json`
- Value in v2.0: `pack_gazetteer`
- Status: [TO CONFIRM with legal]

A town, a province, a street, a company's name (its legal form set aside) and a person's name are taken as written only when every word is identified by the gazetteer of the pack (rules/extract.json gazetteer_*, the closed list of the synthetic world) and holds no numeral (free_text_identification); anything else keeps every field the document may change [TO CONFIRM], and blocks when it may state a holding. On real documents the list would be an official one - the register of municipalities and provinces, the street register of each municipality, the name registered with the business register for a company, the register of persons for a person: which list identifies which slot, and whether a value no list holds may ever be taken as written, is a legal question. Added in v2.0.9 (D38, eval/history.json run 20).

## Not modelled at all

Statutory deadlines and obligation calendars, treasury shares, usufruct and pledge over shares, voting
rights that differ from capital rights, beneficial-ownership thresholds, foreign registries. v2.0 says
nothing about them.
