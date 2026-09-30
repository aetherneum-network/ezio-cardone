# S03 - A figure without its source (negative scenario)

**Claim A1.** Tessiture Monteverde S.r.l.: a valid run, then four tampered copies of its entity record (`input/tamper.json`): source document removed, source date blanked, edition blanked, value changed while the source is kept. The failure reproduced is the never-event of this pack: a figure rendered as fact without a source, or different from what its source says. Pass: in the valid run every figure of the provenance file and every figure row of the DOCX carries source document, date and edition; each tampered record makes the run exit 3 (`FAILED`), for the reason the tamper names, and publishes nothing. Expected values: `expected/expected.json`, written by hand in `scenarios/make_inputs.py` and never copied from a run. Everything is synthetic; what passes here is internal consistency, not accuracy on real companies.

    python scenarios/S03/check.py
