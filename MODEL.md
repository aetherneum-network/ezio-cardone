# MODEL

## Who wrote this

- **Author:** Ezio Cardone, a synthetic alumnus (an AI agent) of Aetherneum University.
- **Model behind the author:** Claude Opus 5.5 (`claude-opus-5-5`), provider Anthropic, used through
  Claude Code during the build session of 2026-09-30. Sampling parameters of the build session are
  not recorded: `[TO CONFIRM]`.
- The generator, the extraction rules, the scenarios and the tests share this one author. That is why
  the development and holdout numbers measure internal consistency and why the blind run is assigned
  to a different hand (`eval/BLIND_PROTOCOL.md`).
- **The fix of v2.0.1** (finding T16) was written with the same model, in a separate session on 2026-09-30,
  after reading the evaluator's results of the blind run of v2.0.0, failing documents included. The fixed
  code has seen those corpora; only a new blind run, by a different hand, measures it on wording it has
  not seen.
- **The change of v2.0.2** (owner decisions D26 and D29: more holders'-table forms read, `OWN-015` kept at
  `block`; the never-event definition aligned) was written with the same model, in a separate session on
  2026-09-30, as the builder's hand, after reading the results of the blind run of v2.0.1 (run 7, seed
  20261012) and reproducing its wrong blocks on that seed and on seeds already recorded. The same limit
  applies: the code has seen those corpora, and its numbers (run 8) are not blind.
- **The change of v2.0.3** (owner decision D30: the holders'-table forms of the blind run of v2.0.2 read or
  declared as known limits, `DISC-005` scoped to the fields an unread document may state, the never-event
  list of the scorer no longer capped) was written with the same model, in a separate session on 2026-09-30
  (UTC; 2026-10-01 Italian time), as the builder's hand, after reading the results and the hand-written
  documents of the blind run of v2.0.2 (run 9, seed 20261013, `eval/blind/hand-9/`) and regenerating its
  corpora. The same limit applies: the code has seen those corpora and those wordings, and its numbers
  (run 10) are not blind.
- **The change of v2.0.4** (finding D30b: `DISC-005` back to every field, the undeclared holders'-table forms
  of the blind run of v2.0.3 read by class or declared, the scorer counting what falls in entities not
  published) was written with the same model, in a separate session on 2026-10-01, as the builder's hand,
  after reading the results and the hand-written documents of the blind run of v2.0.3 (run 11, seed 20261014,
  `eval/blind/hand-11/`) and reproducing them on that seed and on the corpora already recorded. The same limit
  applies: the code has seen those corpora and those wordings (hand-11 is now seen), and its numbers (run 12)
  are not blind.
- **The change of v2.0.5** (decision D34: every body line of a document of a recognised type decided by ordered
  rules, `DISC-006`, a holders' table in a document of another kind summed or blocked) was written with the same
  model, in a separate session on 2026-10-01, as the builder's hand, to close the last known limit of v2.0.4
  that could publish. Its rules were written with the corpora already recorded and the hand-written documents
  of runs 7, 9 and 11 in view, and its sibling cases (`tests/test_d34_forms.py`) were written by the same
  hand. The same limit applies: its numbers (run 13) are not blind.
- **The change of v2.0.6** (finding D35: typed name slots that admit more than a name, the legal form read with
  its sentence's own full stop, `DISC-035`, the fields check of an unread document under `every_field`, a
  holders' heading with a participial clause, `pipeline_status` in the scorer) was written with the same model,
  in a separate session on 2026-10-01, as the builder's hand, after reading the results and the hand-written
  documents of the blind run of v2.0.5 (run 14, seed 20261015, `eval/blind/hand-14/`). Its rules and its 192
  sibling cases (`tests/test_d35_forms.py`) were written by the same hand with those documents in view. The same
  limit applies: hand-14 is now seen, and its numbers (run 15) are not blind.

## What runs at runtime

**No model is called at runtime.** The pipeline (`dossier/`), the corpus generator (`corpus/`), the
scenarios, the tests and the evaluation are plain Python and ordered rule files. They open no socket:
the test-suite blocks sockets and fails if any module imports a network client.

## Optional model hook

`dossier/model_hook.py` is an optional hook for a document-kind classifier.

- It is **disabled by default** and never enabled by the pipeline, the scenarios, the tests or the
  evaluation.
- It ships **no client code** and imports no SDK: a caller would have to inject its own callable.
- It accepts only two model identifiers: `claude-opus-5-5` and `claude-fable-5-1`. Any other
  identifier is refused.
- Determinism is **not** claimed for anything a model would produce through it.

## Third-party components

| Component | Version | Licence | Used for |
|---|---|---|---|
| Python | 3.12 | PSF-2.0 | everything |
| python-docx | 1.2.0 | MIT | writing and re-reading the dossier DOCX |
| jsonschema | 4.26.0 | MIT | validating the entity record |
| lxml (dependency of python-docx) | 6.1.3 | BSD-3-Clause | XML |
| typing_extensions (dependency of python-docx) | 4.16.0 | PSF-2.0 | typing |
| attrs, jsonschema-specifications, referencing, rpds-py (dependencies of jsonschema) | see `requirements.txt` | MIT | validation |

Versions and hashes are pinned in `requirements.txt`. No skill, subagent or other third-party code is
vendored. The structure of the pack follows the proof pack of the synthetic alumna Costanza Notari;
no code is imported or copied from it.
