# S09 - A rule is added and the dossiers are rebuilt

**Claim A4.** Fornace Aurelia S.r.l.: an office-transfer document uses a wording the rules do not know ("The seat of the company is moved from ... to ..."). With the rules as they are, the registered office is `[TO CONFIRM]` and the older address of the deed is not promoted back. The scenario then adds one rule on top (`input/rule_patch.json`, with its own inline test) and rebuilds. The failure reproduced is correcting an output by hand, or a rule change that moves more than intended. Pass: after the rebuild the office is the new address with its source; the diff between the two builds lists that one field; the view and the DOCX of the control entity are byte-identical. Expected values: `expected/expected.json`, written by hand in `scenarios/make_inputs.py` and never copied from a run. Everything is synthetic; what passes here is internal consistency, not accuracy on real companies.

    python scenarios/S09/check.py
