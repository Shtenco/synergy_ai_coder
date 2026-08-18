# SINERGY Engineering Change-Set Review Protocol — 2026-08-18

## Status

Additive engineering-safety layer. The earlier orchestration README and review matrix remain unchanged.

## Purpose

`ai_coder` may coordinate architecture, implementation, review and evidence collection, but it must not turn model confidence or the existence of a test file into merge/deploy authority.

The new `engineering.change-set/v1` object therefore records:

- repositories affected;
- canonical `REQ-*` references;
- draft `HARDEN-*` controls;
- risk domains;
- evidence records and their actual status;
- an explicit `automation_authority = NONE`.

## Evidence semantics

Evidence is one of `PASS`, `FAIL`, `PENDING` or `NOT_RUN`.

`PENDING` is never treated as `PASS`. An existing workflow file is not proof that a runner executed it. A positive CI/integration/fork/schema result requires an immutable digest.

Each risk domain has a minimum evidence matrix. Examples:

- FINANCIAL: unit tests + economic review + schema conformance + human review;
- PAYMENT: integration test + security review + schema conformance + human review;
- SMART_CONTRACT: unit test + fork test + security review + human review;
- AI: unit test + schema conformance + human review.

## Verdict boundary

The deterministic reviewer returns only:

- `DRAFT_BLOCKED`;
- `REVIEWABLE`.

`REVIEWABLE` means that the declared evidence matrix is complete. It is not merge approval, deployment permission, financial authorization or production-readiness certification.

No function in this package merges a PR, changes a protected branch, deploys a contract, signs a transaction or executes monetary policy.

## Namespace separation

`REQ-*` is reserved for canonical requirements owned by the federation requirement registry. `HARDEN-*` identifies engineering hardening controls that may still be draft or pending verification. The namespaces cannot be substituted for each other.

## Non-destructive evolution

This protocol is added on a child branch above the existing `feat/sinergy-engineering-orchestration-20260817` architecture. The previous documentation is preserved unchanged. Future versions should be added side-by-side rather than rewriting historical review evidence.
