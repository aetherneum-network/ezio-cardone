# S02 - Three holders at 33,33% (negative scenario)

**Claim A3.** Finanziaria Collelungo S.p.A.: the deed lists three holders at 33,33% each, which sum to 9999/10000. The failure reproduced is a cap table that does not sum to the whole and is published anyway, or rounded. Pass: the run exits 2, the entity is `BLOCKED` with the exact sum in the reason, no DOCX and no snapshot are written and `RUN OK` is not printed; the same deed written with three holders at 1/3 builds, and its cap table sums to exactly 1/1. Since v2.0.8 each deed is followed by a registry extract that repeats it: an address is a fact only when a second document states it alike (`rules/extract.json` ADR-020), and a deed alone keeps every field `[TO CONFIRM]`. Expected values: `expected/expected.json`, written by hand in `scenarios/make_inputs.py` and never copied from a run. Everything is synthetic; what passes here is internal consistency, not accuracy on real companies.

    python scenarios/S02/check.py
