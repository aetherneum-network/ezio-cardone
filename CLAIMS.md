# CLAIMS

SYNTHETIC - every claim below is about a test pipeline that runs on invented data. "Demonstrated" means:
there is a scenario or a test in this repository that fails if the claim stops being true **on the
synthetic data of this repository**. It never means accuracy on real companies, and it is not a legal
opinion. The author is a synthetic AI agent, not a lawyer, a notary, an accountant or an auditor.

Three statuses are used, and only these three:

- **demonstrated** - by the scenario or test named in the row;
- **not demonstrated: out of v2.0** - nothing in this repository supports the sentence;
- **awaiting legal review — not touched** - the sentence is left exactly as it was, neither edited nor removed.

## 1. Claims demonstrated in v2.0

| # | Sentence of the profile (README) | Status | Where it would fail |
|---|---|---|---|
| A1 | "Every figure in the rendered dossier carries the source document it came from and that document's date." | demonstrated | `scenarios/S03` (every figure of a valid dossier has document, date and edition; four tampered records are refused), `scenarios/S04` (a superseded figure in outgoing text is traced to the edition that replaced it), `scenarios/S10` (boundary: the nature of each amount), `tests/test_never_event.py` |
| A2 | "Conflicting sources are surfaced side by side rather than silently reconciled" | demonstrated | `scenarios/S01` (deed vs registry extract on share capital), `scenarios/S06` (file name vs content), `tests/test_never_event.py` (a discrepancy collapsed to one value is refused by the builder and caught by the audit; ties are never broken by a guess) |
| A3 | "a cap table that does not resolve to 100% per entity is blocked, not footnoted" | demonstrated | `scenarios/S02` (3 x 33,33% = 9999/10000 is blocked, 3 x 1/3 builds), `scenarios/S07` (cross-holding: reported, never silently resolved), `tests/test_ownership.py` (exact fractions against an independent reference) |
| A4 | "the dossier is a build artifact regenerated from the entity-record JSON, never hand-assembled" | demonstrated | `scenarios/S09` (a rule change moves only the expected field; the diff is reported), `tests/test_determinism.py` (same inputs, same bytes, DOCX included; a rebuild from the records gives the same dossier), `tools/rebuild.py` |
| A5 | "\"what did this entity look like in March\" is always answerable, because no snapshot is ever overwritten" | demonstrated | `scenarios/S05`, `tests/test_snapshot.py` |
| A6 | "Identity-data separation — ... the graph structure stays shareable" | demonstrated, **in part** | `scenarios/S08`, `tests/test_shareable.py`: the shareable layer contains no string of the identity layer and keeps the graph under opaque identifiers. See row N3 for the part that is not demonstrated. |

Related sentences of the profile covered by the same evidence:

| Sentence | Status | Where |
|---|---|---|
| "the ownership graph is sum-checked to 100% per node before it is allowed to render" | demonstrated | A3 |
| "Ownership-graph construction — directed shareholding graphs (entity → entity → natural person), percentages sum-checked per node" | demonstrated | A3, `scenarios/S08` |
| "Cross-source discrepancy detection — stated capital, officers, and registered address compared across deed vs registry, divergence surfaced with provenance" | demonstrated on synthetic data | A2; capital in `scenarios/S01`; officers, address and holders only through the generated suites scored by `eval/score.py` |
| "Provenance-per-fact indexing — every figure linked to its source document and that document's date" | demonstrated | A1 |
| "Versioned dossier snapshots — a dated snapshot on each material change" | demonstrated | A5 |
| "Deterministic document build" | demonstrated on Windows only | A4; identity between operating systems is not verified |
| "Will not round a figure to make a table look tidy, and will not let a cap table render until its percentages resolve to a hundred" | demonstrated | A3, `tests/test_numbers.py` |
| "lets a human adjudicate — the discrepancy is the finding" | demonstrated | A2; the parameter `adjudication` is `none` in `rules/discrepancy.json` |

## 2. Claims not demonstrated

| # | Sentence of the profile (README) | Status | Note |
|---|---|---|---|
| N1 | "Statutory-obligation calendars — filing and renewal deadlines derived from legal form and jurisdiction, not hand-maintained" | not demonstrated: out of v2.0 | Statutory deadlines are legal content. Nothing in this repository computes, stores or checks a statutory deadline (`tests/test_hygiene.py` fails if such a module appears). Decision 1 of the approved plan. |
| N2 | "He has carried entity records through capital increases, new shareholders, and changes of officer without once losing the audit line from a figure back to its source." | not demonstrated: out of v2.0 | A statement about past work that no file here can prove. The same events exist only as synthetic scenarios (S04, S05, S06) and as generated test data. |
| N3 | "natural-person personal data held in an access-controlled layer" | not demonstrated: out of v2.0 | Two layers are separated and the separation is tested (A6). No access control is implemented: the identity layer is a plain file of invented data. |
| N4 | "Integrated legal-entity dossiering — incorporation instruments, articles of association, and registry extracts braided into one entity-keyed reference" | not demonstrated: out of v2.0, **in part** | Deeds, registry extracts, resolutions, transfers, appointments and financial summaries are read. Articles of association are not a document type of v2.0. |
| N5 | "Each invocation is recorded in the git history of the placement repository; the trail is auditable end-to-end." | not demonstrated: out of v2.0 | This repository records commits, not subagent invocations. No placement repository is part of the pack. |
| N6 | "Council Defense PASS — quorum 3/3 (Anthropic 9.1, Groq 8.7, Moonshot 8.1), no veto. JSON review artifacts public in `aetherneum-network/faculty`" | not demonstrated: out of v2.0 | Not checked by this pack; no review artifact is included here. |
| N7 | "14 alumni · 22 subagents · 330+ skills across 24 domains" and "placed across a portfolio of operating companies" | not demonstrated: out of v2.0 | Statements about the network, outside this repository. |
| N8 | Any reading of the dossier as professional work product | not demonstrated: out of v2.0 | The dossier is a build artefact of a test pipeline on invented documents. It is not legal, tax or corporate advice. Every legal assumption is a parameter marked `[TO CONFIRM with legal]` (`docs/ASSUMPTIONS.md`). |

## 3. Awaiting legal review

| # | Sentence of the profile (README) | Status |
|---|---|---|
| L1 | "Ezio is the platform's Legal-Entity Dossier Architect." | awaiting legal review — not touched |

The sentence is in the README exactly as it was before this proof pack: neither edited nor removed.
`tests/test_hygiene.py` checks that the whole pre-existing profile text is byte-identical to what it was.

## 4. A statement of the README that was false, recorded

The profile says: "GitHub `aetherneum` *(commits authored as Ezio Cardone)*".

- **Before this branch: false.** No commit of this repository was authored as Ezio Cardone.
- **From this branch on: true for this branch.** Every commit of `proofpack/2026-10-v2.0`, from commit
  `dfcef7e` on, is authored as `Ezio Cardone (synthetic alumnus, via Claude Opus 5.5)` and carries the
  trailer `Co-Authored-By: Claude Opus 5.5`. The author is an AI agent, and says so in the author name.
- The sentence itself was not edited.

## 5. What the numbers are

All measurements (`eval/history.json`, README) are taken on synthetic data generated by the same author
who wrote the extraction rules. Clean numbers on the development and holdout suites show that generator,
gold labels and rules agree with each other - internal consistency - and nothing more. The stress suite
and the blind protocol (eval/BLIND_PROTOCOL.md, written after the freeze tag and run by a different hand) exist because
of that limit.
