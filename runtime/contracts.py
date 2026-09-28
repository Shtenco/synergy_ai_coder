from __future__ import annotations

from hashlib import sha256
from typing import Any
from uuid import UUID


REQUIREMENT_CONTRACT_ID = "synergy.engineering.requirement-trace/v1"
CHANGE_CONTRACT_ID = "synergy.engineering.change-evidence/v1"
AUTHORITY = "engineering_evidence"


def consume_requirement_trace(payload: dict[str, Any], *, target_repository: str) -> dict[str, Any]:
    req_id = str(payload.get("requirement_id", ""))
    status = str(payload.get("status", "")).upper()
    affected = [str(x) for x in payload.get("affected_repositories", [])]
    if not req_id.startswith("REQ-"):
        raise ValueError("invalid requirement id")
    if target_repository not in affected:
        raise ValueError("requirement does not target this repository")
    if status == "REJECTED":
        raise ValueError("rejected requirement cannot produce a change")
    return {
        "requirement_id": req_id,
        "statement": str(payload.get("statement", "")),
        "validation_targets": list(payload.get("validation_targets", [])),
        "source_status": status,
        "target_repository": target_repository,
    }


def check_record(*, name: str, passed: bool, evidence_bytes: bytes | None = None) -> dict[str, Any]:
    if not name:
        raise ValueError("check name required")
    evidence_id = None
    if evidence_bytes is not None:
        evidence_id = (
            "urn:synergy:evidence:synergy_ai_coder:check:sha256:"
            + sha256(evidence_bytes).hexdigest()
        )
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "evidence_id": evidence_id,
    }


def change_evidence_payload(
    *,
    change_id: UUID | str,
    repository: str,
    commit_sha: str,
    requirements: list[str],
    checks: list[dict[str, Any]],
    review_status: str,
    artifact_bytes: bytes | None = None,
) -> dict[str, Any]:
    if not repository.startswith("Shtenco/"):
        raise ValueError("repository must be canonical Shtenco repo")
    if len(commit_sha) != 40 or any(c not in "0123456789abcdef" for c in commit_sha.lower()):
        raise ValueError("commit_sha must be 40 hex")
    if not requirements or any(not str(r).startswith("REQ-") for r in requirements):
        raise ValueError("at least one REQ-* requirement is required")
    if not checks:
        raise ValueError("change evidence requires checks")
    normalized_checks = []
    for c in checks:
        status = str(c.get("status", "")).upper()
        if status not in {"PASS", "FAIL", "SKIP"}:
            raise ValueError("invalid check status")
        normalized_checks.append({
            "name": str(c.get("name", "")),
            "status": status,
            "evidence_id": c.get("evidence_id"),
        })
    review = review_status.upper()
    if review not in {"DRAFT", "REVIEWABLE", "APPROVED", "REJECTED"}:
        raise ValueError("invalid review status")
    if review == "APPROVED" and any(c["status"] != "PASS" for c in normalized_checks):
        raise ValueError("APPROVED change requires all checks PASS")
    artifact_hash = sha256(artifact_bytes).hexdigest() if artifact_bytes is not None else None
    return {
        "change_id": str(change_id),
        "repository": repository,
        "commit_sha": commit_sha.lower(),
        "requirements": list(dict.fromkeys(requirements)),
        "checks": normalized_checks,
        "review_status": review,
        "artifact_sha256": artifact_hash,
    }
