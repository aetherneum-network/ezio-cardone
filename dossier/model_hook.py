"""Optional model hook - disabled by default, never used by the pipeline, the tests or the evaluation.

The pipeline classifies documents with ordered rules and calls no model. This module only fixes the
contract a future, optional document-kind classifier would have to respect:

* it is off unless a caller explicitly enables it and injects its own callable;
* only ``claude-opus-5-5`` and ``claude-fable-5-1`` are accepted as model identifiers;
* it contains no client, imports no SDK and opens no connection;
* whatever a model returns is a *suggestion*: the kind must be one of the known kinds, and the
  answer never replaces an abstention with a value.

Determinism is not claimed for anything obtained through this hook.
"""
from __future__ import annotations

from typing import Callable

ALLOWED_MODELS = ("claude-opus-5-5", "claude-fable-5-1")
ENABLED_BY_DEFAULT = False
KINDS = ("DEED", "RESOLUTION", "TRANSFER", "APPOINTMENT", "OFFICE", "EXTRACT", "LEDGER", "FIN", "UNKNOWN")


class ModelHookDisabled(RuntimeError):
    """The optional model hook is disabled (the default)."""


class ModelNotAllowed(ValueError):
    """The model identifier is not one of the two allowed."""


class ModelHook:
    def __init__(self, model: str | None = None, call: Callable[[str, str], str] | None = None,
                 enabled: bool = ENABLED_BY_DEFAULT):
        if model is not None and model not in ALLOWED_MODELS:
            raise ModelNotAllowed(f"{model!r} is not allowed; use one of {ALLOWED_MODELS}")
        self.model, self._call, self.enabled = model, call, bool(enabled)

    def suggest_kind(self, document_text: str) -> str:
        """Ask the injected callable for the kind of a document. Raises unless explicitly enabled."""
        if not self.enabled or self._call is None or self.model is None:
            raise ModelHookDisabled("the model hook is disabled by default and no model is called at runtime")
        answer = str(self._call(self.model, document_text)).strip().upper()
        return answer if answer in KINDS else "UNKNOWN"
