import pytest

from sinergy_ai_coder import (
    ChangeSetInvariantError,
    EvidenceRecord,
    EngineeringChangeSet,
    review_change_set,
)


def _evidence(kind: str, status: str = "PASS") -> EvidenceRecord:
    digest = "ab" * 32 if kind in {
        "CI_RUN",
        "INTEGRATION_TEST",
        "FORK_TEST",
        "SCHEMA_CONFORMANCE",
    } and status == "PASS" else None
    return EvidenceRecord(
        evidence_id=f"{kind}-{status}",
        kind=kind,
        status=status,
        digest=digest,
        source_ref="example",
    )


def _financial_change(evidence=()) -> EngineeringChangeSet:
    return EngineeringChangeSet(
        change_set_id="chg-fin-001",
        repositories=("Shtenco/synergy_financial_os",),
        requirement_refs=("REQ-FIN-004",),
        hardening_refs=("HARDEN-FIN-VALUATION-001",),
        risk_domains=("FINANCIAL",),
        evidence=tuple(evidence),
        summary="Harden canonical accounting boundary",
    )


def test_financial_change_without_evidence_is_blocked() -> None:
    result = review_change_set(_financial_change())
    assert result.status == "DRAFT_BLOCKED"
    assert set(result.blockers) == {
        "EVIDENCE_MISSING:ECONOMIC_REVIEW",
        "EVIDENCE_MISSING:HUMAN_REVIEW",
        "EVIDENCE_MISSING:SCHEMA_CONFORMANCE",
        "EVIDENCE_MISSING:UNIT_TEST",
    }


def test_pending_test_is_not_treated_as_pass() -> None:
    result = review_change_set(_financial_change((_evidence("UNIT_TEST", "PENDING"),)))
    assert result.status == "DRAFT_BLOCKED"
    assert "EVIDENCE_PENDING:UNIT_TEST" in result.blockers


def test_financial_change_becomes_only_reviewable_after_all_required_evidence_passes() -> None:
    evidence = (
        _evidence("UNIT_TEST"),
        _evidence("ECONOMIC_REVIEW"),
        _evidence("SCHEMA_CONFORMANCE"),
        _evidence("HUMAN_REVIEW"),
    )
    result = review_change_set(_financial_change(evidence))
    assert result.status == "REVIEWABLE"
    assert result.reviewable is True
    assert result.blockers == ()


def test_any_explicit_failure_blocks_even_if_other_evidence_passes() -> None:
    evidence = (
        _evidence("UNIT_TEST"),
        _evidence("ECONOMIC_REVIEW", "FAIL"),
        _evidence("SCHEMA_CONFORMANCE"),
        _evidence("HUMAN_REVIEW"),
    )
    result = review_change_set(_financial_change(evidence))
    assert result.status == "DRAFT_BLOCKED"
    assert "EVIDENCE_FAILED:ECONOMIC_REVIEW" in result.blockers


def test_payment_change_requires_security_and_integration_evidence() -> None:
    change = EngineeringChangeSet(
        change_set_id="chg-pay-001",
        repositories=("Shtenco/synergy_pay_system",),
        requirement_refs=("REQ-PAY-001",),
        hardening_refs=(),
        risk_domains=("PAYMENT",),
        evidence=(
            _evidence("SCHEMA_CONFORMANCE"),
            _evidence("HUMAN_REVIEW"),
        ),
        summary="Payment boundary change",
    )
    result = review_change_set(change)
    assert "EVIDENCE_MISSING:INTEGRATION_TEST" in result.blockers
    assert "EVIDENCE_MISSING:SECURITY_REVIEW" in result.blockers


def test_smart_contract_change_requires_fork_test() -> None:
    change = EngineeringChangeSet(
        change_set_id="chg-contract-001",
        repositories=("Shtenco/synergy_ai_blockchain",),
        requirement_refs=("REQ-CHAIN-001",),
        hardening_refs=(),
        risk_domains=("SMART_CONTRACT",),
        evidence=(
            _evidence("UNIT_TEST"),
            _evidence("SECURITY_REVIEW"),
            _evidence("HUMAN_REVIEW"),
        ),
        summary="Contract boundary change",
    )
    assert "EVIDENCE_MISSING:FORK_TEST" in review_change_set(change).blockers


def test_automation_authority_cannot_be_escalated() -> None:
    with pytest.raises(ChangeSetInvariantError):
        EngineeringChangeSet(
            change_set_id="chg-danger",
            repositories=("Shtenco/synergy_financial_os",),
            requirement_refs=("REQ-FIN-004",),
            hardening_refs=(),
            risk_domains=("FINANCIAL",),
            evidence=(),
            summary="Unsafe",
            automation_authority="MERGE_AND_DEPLOY",
        )


def test_requirement_and_hardening_namespaces_cannot_be_mixed() -> None:
    with pytest.raises(ChangeSetInvariantError):
        EngineeringChangeSet(
            change_set_id="chg-bad-ref",
            repositories=("Shtenco/synergy_financial_os",),
            requirement_refs=("HARDEN-FIN-001",),
            hardening_refs=(),
            risk_domains=("FINANCIAL",),
            evidence=(),
            summary="Bad namespace",
        )


def test_duplicate_repositories_and_evidence_ids_fail_closed() -> None:
    with pytest.raises(ChangeSetInvariantError):
        EngineeringChangeSet(
            change_set_id="chg-dup",
            repositories=("Shtenco/ai_coder", "Shtenco/ai_coder"),
            requirement_refs=(),
            hardening_refs=(),
            risk_domains=("GENERAL",),
            evidence=(),
            summary="duplicate repo",
        )

    duplicated = EvidenceRecord("e1", "UNIT_TEST", "PASS")
    with pytest.raises(ChangeSetInvariantError):
        EngineeringChangeSet(
            change_set_id="chg-dup-evidence",
            repositories=("Shtenco/ai_coder",),
            requirement_refs=(),
            hardening_refs=(),
            risk_domains=("GENERAL",),
            evidence=(duplicated, duplicated),
            summary="duplicate evidence",
        )
