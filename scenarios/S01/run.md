# S01 - Deed and registry extract disagree on the share capital

**Claim A2.** Fornace Aurelia S.r.l.: the deed of 2025-03-10 states a share capital of EUR 50.000,00, the test registry extract of 2026-02-02 (EXTRACT/1) states EUR 80.000,00, and no resolution explains the difference. The failure reproduced is the silent choice of one of the two values. Pass: the three capital fields are `DISCREPANCY`; both values are in the DOCX side by side, each with source document, date and edition; no capital figure is among the facts; the run exits 0, because a discrepancy that is shown is a valid dossier. Expected values: `expected/expected.json`, written by hand in `scenarios/make_inputs.py` and never copied from a run. Everything is synthetic; what passes here is internal consistency, not accuracy on real companies.

    python scenarios/S01/check.py
