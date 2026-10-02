# S10 - Resolved, subscribed and paid-in in one clause (boundary)

**Claim A1.** Finanziaria Collelungo S.p.A.: one clause of a resolution carries four amounts (previous capital, resolved, subscribed, paid-in). The failure reproduced is counting amounts of different natures as one figure. Pass, variant `clear`: each amount gets its nature (historical 300000.00, resolved 500000.00, subscribed 400000.00, paid-in 250000.00) and the DOCX shows three capital rows with three natures. Variant `insufficient`: a later extract lists the same amounts and says only which one is resolved; subscribed and paid-in are then `[TO CONFIRM]`, and what the resolution said is listed as a readable statement, not as a fact. Expected values: `expected/expected.json`, written by hand in `scenarios/make_inputs.py` and never copied from a run. Everything is synthetic; what passes here is internal consistency, not accuracy on real companies.

    python scenarios/S10/check.py
