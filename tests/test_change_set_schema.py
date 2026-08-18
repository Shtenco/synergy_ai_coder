import json
from pathlib import Path

from sinergy_ai_coder import EvidenceRecord, EngineeringChangeSet


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/engineering_change_set_v1.schema.json"


def _change_set() -> EngineeringChangeSet:
    return EngineeringChangeSet(
        change_set_id="chg-schema-001",
        repositories=("Shtenco/ai_coder",),
        requirement_refs=("REQ-AI-001",),
        hardening_refs=("HARDEN-ENG-001",),
        risk_domains=("GENERAL",),
        evidence=(
            EvidenceRecord(
                evidence_id="unit-1",
                kind="UNIT_TEST",
                status="PASS",
                source_ref="tests/test_change_set.py",
            ),
        ),
        summary="Schema/runtime conformance",
    )


def test_runtime_emits_exact_schema_top_level_shape() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = _change_set().to_dict()
    assert set(payload) == set(schema["required"])
    assert set(payload) <= set(schema["properties"])
    assert payload["schema"] == "engineering.change-set/v1"
    assert payload["automation_authority"] == "NONE"


def test_evidence_runtime_shape_matches_schema_definition() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    evidence_schema = schema["properties"]["evidence"]["items"]
    payload = _change_set().to_dict()["evidence"][0]
    assert set(payload) == set(evidence_schema["required"])
    assert set(payload) <= set(evidence_schema["properties"])


def test_schema_forbids_authorizing_automation_value() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["properties"]["automation_authority"] == {"const": "NONE"}
