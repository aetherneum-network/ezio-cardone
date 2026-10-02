"""Stage 2 - the entity record: the sole source of truth of the dossier.

The record keeps every assertion of every document, side by side. Nothing is merged or chosen here:
two documents that state two capitals give two assertions. The record is validated against
``schema/entity_record.schema.json``; a figure without ``source_doc``, ``source_date`` or ``edition``,
or a value written as a JSON number, makes the record invalid and the run FAILED.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import jsonschema

from .lib import jsonio

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "entity_record.schema.json"
SCHEMA_VERSION = "2.0.0"


class RecordInvalid(ValueError):
    """The entity record does not satisfy the schema."""


@lru_cache(maxsize=1)
def _validator() -> jsonschema.Draft202012Validator:
    schema = jsonio.load(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def validate(record: dict) -> None:
    errors = sorted(_validator().iter_errors(record), key=lambda e: list(e.absolute_path))
    if errors:
        e = errors[0]
        where = "/".join(str(x) for x in e.absolute_path) or "(root)"
        raise RecordInvalid(f"entity record invalid at {where}: {e.message[:200]} ({len(errors)} error(s))")


def build_record(raw: dict, as_of: str) -> dict:
    """Turn the raw extraction of one entity into a validated record."""
    record = {
        "schema_version": SCHEMA_VERSION,
        "entity": {"id": raw["entity_id"], "registry_no": raw["registry_no"]},
        "as_of": as_of,
        "documents": sorted(raw["documents"], key=lambda d: (d["date"], d["doc_id"])),
        "assertions": sorted(raw["assertions"], key=lambda a: (a["field"], a["source_date"], a["source_doc"],
                                                               a["nature"])),
        "filename_divergences": sorted(raw["filename_divergences"], key=lambda d: (d["doc_id"], d["aspect"])),
        "unclassified_documents": sorted(raw["unclassified_documents"], key=lambda d: d["file"]),
        "classified_checks": sorted(raw["classified_checks"], key=lambda d: d["file"]),
        "rejected_documents": sorted(raw["rejected_documents"], key=lambda d: d["file"]),
        "ignored_after_as_of": sorted(raw["ignored_after_as_of"]),
    }
    validate(record)
    return record


def load_record(path: Path | str) -> dict:
    """Read a record from disk. Floats are refused by the reader, the rest by the schema."""
    record = jsonio.load(path)
    validate(record)
    return record
