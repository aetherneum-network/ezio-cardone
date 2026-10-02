# SYNTHETIC

**Everything in this repository is synthetic.**

- **The author is an AI system.** Ezio Cardone is a synthetic alumnus (an AI agent) of Aetherneum
  University. He is not a person, not a notary, not a lawyer, not an accountant and not an auditor.
  The code and the documents were written by Claude Opus 5.5 (`claude-opus-5-5`) acting as that agent.
- **No real company.** Every entity is invented: Fornace Aurelia S.r.l., Holding Aurelia
  Partecipazioni S.r.l., Finanziaria Collelungo S.p.A., Tessiture Monteverde S.r.l. and the generated
  ones (sector word + invented place name such as *Montefinto*, *Valfittizia*, *Borgoprova*). Any
  resemblance to an existing company is accidental and no fact about a real company is stated.
- **No real person.** Natural persons exist only as test identifiers (`P-001`, ...) with invented
  names built from surnames such as *Finti*, *Provetti*, *Fittizi*. Birth dates, addresses and
  identifiers in `identity/persons.json` are generated from the seed.
- **No real registry.** The "test registry" is an invented registry. Its extracts imitate no official
  record and carry numbers of the form `TEST-REG-000123`. Tax and registration identifiers have the
  forms `SYN-VAT-000123` and `SYN-CF-P001`: neither can be mistaken for a real identifier.
- **No real deed.** Deeds, resolutions, ledgers and financial summaries are plain-text test documents.
  Every source document starts with the line
  `SYNTHETIC TEST DOCUMENT - fictitious entity, invented test registry, not an official record.`
  and the pipeline refuses a document that does not carry it.
- **Only `.example` domains** appear in generated content.
- **No client data, no personal data, no credentials.** Nothing in this repository comes from a real
  company, a client, or any dispute.

## How the data is generated

`corpus/generate.py --seed N` builds a world (groups, entities, persons, a dated timeline of events),
plans the source documents and the planted faults, renders the documents from templates and writes the
gold labels from the world's timeline and fault plan - never by reading the rendered documents back.
The same seed always gives the same bytes (`corpus/MANIFEST.sha256`).

## The gazetteer (since v2.0.9)

The pipeline takes a town, a province, a street, a company's name and a person's name as written only when every
word of it is an entry of the gazetteer of the pack (`rules/extract.json`, parameters `gazetteer_*`; the rule
group `free_text_identification`). The gazetteer is the closed vocabulary of this synthetic world, and nothing else:

- **towns**: the invented place names the generator draws from (`corpus/world.py` `TOPONYMS`: *Montefinto*,
  *Valfittizia*, *Borgoprova* ...) and the three of the scenarios (*Aurelia*, *Collelungo*, *Monteverde*);
- **province**: the invented `ZZ` only;
- **streets**: a street type (*Via*, *Viale*, *Piazza*, *Corso*, *Vicolo*, *Largo*) and an invented street name
  (`corpus/world.py` `STREETS`: *del Collaudo*, *della Prova*, *Simulato* ...);
- **company names**: a trade word (`SECTORS` and the scenarios: *Officine*, *Cantieri*, *Fornace*, *Tessiture* ...)
  and a town, or *Holding*, a town and *Partecipazioni*; the legal form at the end is read apart;
- **person names**: a first name and an invented surname (`FIRST`, `LAST` and the scenarios: *Aldo Finti*,
  *Fulvia Posticci* ...).

Each entry is matched whole, case and particles included. A word that the gazetteer does not hold, or a numeral,
keeps every field of its document `[TO CONFIRM]`, and blocks the entity when the line may state a holding. A
hand-written corpus whose places and names are not of this vocabulary therefore blocks (`CHANGELOG.md` 2.0.9). On
real documents the list would be an official register; which one, and whether a value no register holds may ever be
taken as written, is a legal question (`docs/ASSUMPTIONS.md`, `identification_source`, `[TO CONFIRM with legal]`).

## What the numbers mean

Every measurement in this repository is taken on this synthetic data, written by the same author as
the extraction rules. The numbers measure **internal consistency**, not accuracy on real companies.

## Not advice

The dossier is a build artefact of a test pipeline. It is not legal, tax or corporate advice, and
every legal assumption it relies on is a parameter marked `[TO CONFIRM with legal]`
(`docs/ASSUMPTIONS.md`).

## Images and metadata

`avatar.jpg` is a generated portrait of a synthetic alumnus. No structured metadata in this
repository declares `"@type": "Person"`.
