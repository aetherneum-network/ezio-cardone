# S06 - File named after one person, text appoints another

**Claim A2.** Finanziaria Collelungo S.p.A.: the file is named `2026-03-02_appointment_P-005.txt`, the text appoints P-006. The failure reproduced is taking a fact from a file name. Pass: the director in office is P-006, sourced from the text (APPOINTMENT/1); P-005 is never shown as a director; the divergence between file name and content is recorded and reported in the DOCX. Expected values: `expected/expected.json`, written by hand in `scenarios/make_inputs.py` and never copied from a run. Everything is synthetic; what passes here is internal consistency, not accuracy on real companies.

    python scenarios/S06/check.py
