<div align="center">

<img src="assets/readme/hero.svg" width="100%" alt="AI CODER / EVIDENCE CONTRACTS engineering overview"/>

**Requirement trace; SHA-256 artifact checks; approval gate; canonical repository identifiers**

</div>

# AI CODER / EVIDENCE CONTRACTS

## Original research direction

consume_requirement_trace accepts REQ-prefixed requirements only for affected repositories. check_record optionally hashes evidence bytes with SHA-256. change_evidence_payload records a 40-hex commit reference, unique requirement IDs, PASS/FAIL/SKIP checks, reviewer state and an optional artifact digest. APPROVED requires every check to be PASS.

## Implemented engineering and algorithmic value

This is a compact evidence-contract layer with executable tests, not a complete autonomous coding agent. It is valuable precisely because verification and approval are explicit.

## Scientific and mathematical interpretation

Extend with immutable manifests, signed approvals, repository-specific permissions, CI provenance links, reproducible build artifacts and policy tests.

## Research and application opportunities

undefined

## Evidence context and development maturity

SHA-256(content) is a content identity, not an automatic proof of correctness. Traceability is a relation Requirement -> Change -> Check -> Evidence. Approval is gated by the conjunction of all check statuses PASS.

## Source navigation

- [`runtime/contracts.py`](runtime/contracts.py)
- [`tests/test_contracts.py`](tests/test_contracts.py)

## Publication protocol

Claims must refer to the exact current source commit or an identified experiment artifact. Source code establishes implementation; experiments require frozen inputs, complete costs, successful repeated checks and a labelled evaluation regime. Financial values are attributed to their measurement environment. This page is a scientifically grounded overview and is not an offer of investment returns.
