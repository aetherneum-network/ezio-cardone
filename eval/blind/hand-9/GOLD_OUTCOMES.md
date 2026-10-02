# Hand-written corpus - gold outcomes, written BEFORE the run

Runner: evaluator (Claude Fable 5.1), not the builder. Written 2026-09-30 between 22:13:43Z and 22:15:58Z UTC
(before `make_hand_docs.py` was run at 22:15:58Z), before reading the pack's code and before any run. SYNTHETIC: 9 invented entities, 10 invented persons, 24 documents (`make_hand_docs.py`).
Reference date `as_of` 2026-09-30. The gold (`gold.json`) states what the documents MEAN to a careful human
reader; it is not derived from any output. "Prediction" is the evaluator's guess of the pack's behaviour from
the CHANGELOG's declared limits - it is NOT the gold and does not change it.

| Entity | Docs | Gold outcome | Why (gold) | Forms tested | Prediction (not gold) |
|---|---|---|---|---|---|
| E-0001 Segherie Valleprova S.r.l. | 4 | **PUBLISH** | both tables read by a human, each sums to 1: P-001 11/20, P-002 9/20. Capital is a DISCREPANCY 40.000 (deed) vs 48.000 (extract), no resolution between them. Director P-001 superseded by P-002 (appointment 2026-03-15, extract 2026-05-19). FY2025 figures from the summary. | headings `4. Quotaholders at present.` and `Partners as at the document date:` (in-grammar nouns/qualifiers, wording unseen); holders in reversed order; `45,00%`; amounts `2'450'300.00`, `3 120 415.50`, `512.300,25` | published (the grammar claims these forms); if blocked = wrong block on a form the fixer claims to read |
| E-0002 Cantiere Borgofinto S.p.A. | 3 | **BLOCK** | the table after the transfer (and the later extract) sums to 19/20: 35+35+25 = 95%. Must be blocked whatever the reason. | `Stockholders.` / `Stockholders following the transfer:` / `Stockholders:`; capital `1'200'000.00` and `1 200 000,00` | blocked (OWN-010 if read, OWN-015 if not) - either is right; published = never-event |
| E-0003 Tenuta Colleimmaginario S.r.l. | 2 | **PUBLISH** | **the "careful human" entity**: the deed states the quotas as nominal amounts in prose (36'000 and 24'000 of 60'000 -> 3/5, 2/5); the extract has a pipe table with a nominal column and `60 %`. Both sum to 1. | prose with nominal amounts; pipe table; `60 %` | blocked (declared limit: nominal amounts; pipe rows unknown) - a wrong block, caution not never-event |
| E-0004 Officine Pontefalso S.r.l. | 2 | **PUBLISH** | P-004 3/5 and E-0005 2/5 in both documents; look-through via E-0005 (P-005 3/4, P-006 1/4): effective P-004 3/5, P-005 3/10, P-006 1/10. | `4. Shareholders now.` (qualifier after the noun, clause-numbered), `Shareholders:`; fractions vs percentages; entity holder | published; effective look-through as gold |
| E-0005 Immaginaria Holding S.r.l. | 2 | **PUBLISH** | P-005 3/4, P-006 1/4 in both; the extract's file name (2026-07-02) contradicts its date (2026-07-01): filename divergence, aspect `date`. | `4. Partners.` / `Partners:`; percentages vs fractions; file-name/date divergence | published, divergence reported |
| E-0006 Vetreria Fantasia S.r.l. | 3 | **PUBLISH** | P-007 1/2, P-008 1/2 in deed, extract and the ledger; two directors; capital 20.000 everywhere. | unrecognised type `Ledger of quotaholders` (dated after everything) carrying a readable table under `Quotaholders:` (class B "read") | published; by DISC-005 most fields abstained `[TO CONFIRM]` (unclassified document not older than the events) - abstention, not never-event |
| E-0007 Lanificio Ipotetico S.p.A. | 3 | **PUBLISH** | P-009 3/10, P-010 7/10 in all three documents (prose in the deed; words in the statement; table in the extract). | prose `held by ... as to 30% and by ... as to 70%`; unrecognised type `Statement of shareholdings` with shares in words under `Shareholding structure ...:`; extract heading `Shareholders of record:` (qualifier of unknown meaning) | blocked (three unread tables) - wrong block; the extract's heading is the informative probe |
| E-0008 Mulino Chimerico S.r.l. | 3 | **PUBLISH** | P-010 2/3, P-008 1/3 (200 and 100 of 300 quotas in the deed; fractions in the extract); capital 30.000,00 (NOT 100,00 - a second amount sits in the capital clause); director P-010 (name first in the deed). Certificate adds nothing. | name-first holder lines; share counts; second amount in the capital clause; unrecognised type with no table and no holder noun (`Certificate of good standing`, class B "no_table") | blocked (declared limits: name first, counts) - wrong block. A capital figure other than 30000.00 shown as fact = never-event |
| E-0009 Cartiera Illusoria S.r.l. | 2 | **PUBLISH** | P-002 1/5, P-007 4/5 in both. | numbered items with a dash separator `1) P-002 (...) - 20%`; heading `Holders (as at the document date):` (qualifier in parentheses) | unknown - the informative probe of item and heading forms |

Counts by gold: 8 PUBLISH, 1 BLOCK (E-0002). Entities the evaluator expects the pack to block wrongly by the
CHANGELOG's own declared limits: E-0003, E-0007, E-0008 (3); uncertain: E-0001, E-0009; expected published:
E-0004, E-0005, E-0006.

What would be a never-event here (section 1.5 of the protocol): any figure shown as fact that differs from the
gold (e.g. E-0008 capital 100.00; E-0001 capital shown as one value; any FY2025 figure of E-0001 read short);
E-0002 published; an effective holding shown for E-0004 that differs from 3/5, 3/10, 1/10; a value shown for a
field the gold marks `TO_CONFIRM` (none in this gold); a figure without source, date or edition.

Dissent field: none. Data as of 2026-09-30T22:20Z.
