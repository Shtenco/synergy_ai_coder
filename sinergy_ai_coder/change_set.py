from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class ChangeSetInvariantError(ValueError):
    """Raised when an engineering change set is malformed or unsafe."""


ALLOWED_RISK_DOMAINS = frozenset(
    {
        "FINANCIAL",
        "MATURITY",
        "PAYMENT",
        "TRUST",
        "AI",
        "SMART_CONTRACT",
        "PUBLIC_SURFACE",
        "GENERAL",
    }
)
ALLOWED_EVIDENCE_KINDS = frozenset(
    {
        "STATIC_ANALYSIS",
        "UNIT_TEST",
        "INTEGRATION_TEST",
        "FORK_TEST",
        "SECURITY_REVIEW",
        "ECONOMIC_REVIEW",
        "SCHEMA_CONFORMANCE",
        "HUMAN_REVIEW",
        "CI_RUN",
    }
)
ALLOWED_EVIDENCE_STATUS = frozenset({"PASS", "FAIL", "PENDING", "NOT_RUN"})
HEX = frozenset("0123456789abcdef")

REQUIRED_EVIDENCE: dict[str, frozenset[str]] = {
    "FINANCIAL": frozenset(
        {"UNIT_TEST", "ECONOMIC_REVIEW", "SCHEMA_CONFORMANCE", "HUMAN_REVIEW"}
    ),
    "MATURITY": frozenset({"UNIT_TEST", "SCHEMA_CONFORMANCE", "HUMAN_REVIEW"}),
    "PAYMENT": frozenset(
        {"INTEGRATION_TEST", "SECURITY_REVIEW", "SCHEMA_CONFORMANCE", "HUMAN_REVIEW"}
    ),
    "TRUST": frozenset({"UNIT_TEST", "SECURITY_REVIEW", "SCHEMA_CONFORMANCE"}),
    "AI": frozenset({"UNIT_TEST", "SCHEMA_CONFORMANCE", "HUMAN_REVIEW"}),
    "SMART_CONTRACT": frozenset({"UNIT_TEST", "FORK_TEST", "SECURITY_REVIEW", "HUMAN_REVIEW"}),
    "PUBLIC_SURFACE": frozenset({"STATIC_ANALYSIS"}),
    "GENERAL": frozenset({"UNIT_TEST"}),
}


def _text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ChangeSetInvariantError(f"{field_name} must be text")
    normalized = value.strip()
    if not normalized:
        raise ChangeSetInvariantError(f"{field_name} is required")
    return normalized


def _hex64(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    normalized = _text(value, field_name).lower()
    if len(normalized) != 64 or any(c not in HEX for c in normalized):
        raise ChangeSetInvariantError(f"{field_name} must be a 64-character hex digest")
    return normalized


def _unique_text(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    normalized = tuple(_text(value, field_name) for value in values)
    if len(normalized) != len(set(normalized)):
        raise ChangeSetInvariantError(f"{field_name} must contain unique values")
    return normalized


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    kind: str
    status: str
    digest: str | None = None
    source_ref: str | None = None

    def __post_init__(self) -> None:
        evidence_id = _text(self.evidence_id, "evidence_id")
        kind = _text(self.kind, "kind").upper()
        status = _text(self.status, "status").upper()
        if kind not in ALLOWED_EVIDENCE_KINDS:
            raise ChangeSetInvariantError(f"unsupported evidence kind: {kind}")
        if status not in ALLOWED_EVIDENCE_STATUS:
            raise ChangeSetInvariantError(f"unsupported evidence status: {status}")
        digest = _hex64(self.digest, "digest")
        source_ref = None if self.source_ref is None else _text(self.source_ref, "source_ref")
        if status == "PASS" and digest is None and kind in {
            "CI_RUN",
            "INTEGRATION_TEST",
            "FORK_TEST",
            "SCHEMA_CONFORMANCE",
        }:
            raise ChangeSetInvariantError(
                f"PASS {kind} evidence requires an immutable digest"
            )
        object.__setattr__(self, "evidence_id", evidence_id)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "digest", digest)
        object.__setattr__(self, "source_ref", source_ref)


@dataclass(frozen=True)
class EngineeringChangeSet:
    change_set_id: str
    repositories: tuple[str, ...]
    requirement_refs: tuple[str, ...]
    hardening_refs: tuple[str, ...]
    risk_domains: tuple[str, ...]
    evidence: tuple[EvidenceRecord, ...]
    summary: str
    automation_authority: str = "NONE"

    def __post_init__(self) -> None:
        change_set_id = _text(self.change_set_id, "change_set_id")
        repositories = _unique_text(self.repositories, "repositories")
        if not repositories:
            raise ChangeSetInvariantError("at least one repository is required")
        requirement_refs = _unique_text(self.requirement_refs, "requirement_refs")
        hardening_refs = _unique_text(self.hardening_refs, "hardening_refs")
        for ref in requirement_refs:
            if not ref.startswith("REQ-"):
                raise ChangeSetInvariantError("requirement_refs must use REQ-* identifiers")
        for ref in hardening_refs:
            if not ref.startswith("HARDEN-"):
                raise ChangeSetInvariantError("hardening_refs must use HARDEN-* identifiers")
        domains = tuple(_text(value, "risk_domains").upper() for value in self.risk_domains)
        if not domains or len(domains) != len(set(domains)):
            raise ChangeSetInvariantError("risk_domains must be nonempty and unique")
        unknown = set(domains) - ALLOWED_RISK_DOMAINS
        if unknown:
            raise ChangeSetInvariantError(f"unsupported risk domains: {sorted(unknown)}")
        evidence = tuple(self.evidence)
        evidence_ids = [item.evidence_id for item in evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ChangeSetInvariantError("evidence_id values must be unique")
        summary = _text(self.summary, "summary")
        authority = _text(self.automation_authority, "automation_authority").upper()
        if authority != "NONE":
            raise ChangeSetInvariantError(
                "ai_coder has no autonomous merge, deploy or financial execution authority"
            )
        object.__setattr__(self, "change_set_id", change_set_id)
        object.__setattr__(self, "repositories", repositories)
        object.__setattr__(self, "requirement_refs", requirement_refs)
        object.__setattr__(self, "hardening_refs", hardening_refs)
        object.__setattr__(self, "risk_domains", domains)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "automation_authority", authority)


@dataclass(frozen=True)
class ReviewResult:
    status: str
    blockers: tuple[str, ...]
    required_evidence: tuple[str, ...]
    passed_evidence: tuple[str, ...]

    @property
    def reviewable(self) -> bool:
        return self.status == "REVIEWABLE"


def review_change_set(change_set: EngineeringChangeSet) -> ReviewResult:
    """Return DRAFT_BLOCKED or REVIEWABLE; never merge or deploy anything."""

    required: set[str] = set()
    for domain in change_set.risk_domains:
        required.update(REQUIRED_EVIDENCE[domain])

    by_kind: dict[str, list[EvidenceRecord]] = {}
    for item in change_set.evidence:
        by_kind.setdefault(item.kind, []).append(item)

    blockers: set[str] = set()
    passed: set[str] = set()
    for kind in sorted(required):
        records = by_kind.get(kind, [])
        if any(record.status == "FAIL" for record in records):
            blockers.add(f"EVIDENCE_FAILED:{kind}")
            continue
        if any(record.status == "PASS" for record in records):
            passed.add(kind)
            continue
        if records:
            blockers.add(f"EVIDENCE_PENDING:{kind}")
        else:
            blockers.add(f"EVIDENCE_MISSING:{kind}")

    for item in change_set.evidence:
        if item.status == "FAIL":
            blockers.add(f"EVIDENCE_FAILED:{item.kind}")

    status = "REVIEWABLE" if not blockers else "DRAFT_BLOCKED"
    return ReviewResult(
        status=status,
        blockers=tuple(sorted(blockers)),
        required_evidence=tuple(sorted(required)),
        passed_evidence=tuple(sorted(passed)),
    )
