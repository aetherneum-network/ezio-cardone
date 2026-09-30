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
