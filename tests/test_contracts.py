import importlib.util
from pathlib import Path
from uuid import UUID

import pytest

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"runtime"/"contracts.py"
spec=importlib.util.spec_from_file_location("contracts",PATH)
mod=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def test_requirement_trace_must_target_repository():
    with pytest.raises(ValueError):
        mod.consume_requirement_trace(
            {
                "requirement_id":"REQ-1",
                "statement":"x",
                "affected_repositories":["Shtenco/other"],
                "validation_targets":[],
                "status":"OPEN",
            },
            target_repository="Shtenco/synergy_ai_coder",
        )


def test_approved_change_requires_passing_checks():
    with pytest.raises(ValueError):
        mod.change_evidence_payload(
            change_id=UUID("11111111-1111-4111-8111-111111111111"),
            repository="Shtenco/synergy_ai_coder",
            commit_sha="1"*40,
            requirements=["REQ-1"],
            checks=[{"name":"pytest","status":"FAIL","evidence_id":None}],
            review_status="APPROVED",
        )


def test_change_evidence_is_bounded_and_hashes_artifact():
    p=mod.change_evidence_payload(
        change_id=UUID("11111111-1111-4111-8111-111111111111"),
        repository="Shtenco/synergy_ai_coder",
        commit_sha="1"*40,
        requirements=["REQ-1"],
        checks=[mod.check_record(name="pytest",passed=True,evidence_bytes=b"pass")],
        review_status="APPROVED",
        artifact_bytes=b"artifact",
    )
    assert p["review_status"]=="APPROVED"
    assert len(p["artifact_sha256"])==64
