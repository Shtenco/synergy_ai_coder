# SHTENCO AI Coder

**Autonomous engineering orchestration layer for the SINERGY repository federation.**

This repository coordinates engineering roles around existing repository-specific tooling. It is not a financial authority and should not silently merge, deploy or reinterpret economic invariants.

## Intended roles

A reference multi-agent engineering cycle can include:

- Architect — decomposes federation-level requirements and ownership boundaries;
- Implementer — prepares bounded repository changes;
- Reviewer — checks correctness and architectural fit;
- Test Engineer — maps changes to deterministic tests and reproducible evidence;
- Security Reviewer — checks secret, custody, permission and attack-surface boundaries;
- Economic Invariant Reviewer — checks HardNAV, maturity, principal/revenue and settlement constraints for financial changes;
- Documentation/Provenance Reviewer — verifies source refs, legacy preservation and claim status;
- Release Reviewer — verifies that required evidence gates are complete before promotion.

## Relationship to AI Language

`Shtenco/ai_language` provides repository-aware tooling and semantic requirement traceability. AI Coder should orchestrate specialized roles **over** that or equivalent safe workspace interfaces rather than duplicating unrestricted shell/file access.

Reference flow:

```text
federation requirement
 -> REQ-* decomposition
 -> repository ownership map
 -> implementation plan
 -> bounded changes
 -> tests
 -> security/economic review
 -> evidence bundle
 -> human/governance review where required
 -> PR / release
```

## Hard engineering rules

For canonical SINERGY repositories:

- no destructive legacy migration by default;
- no direct modification of unrelated repositories to simplify one task;
- no silent schema changes;
- no financial invariant change without mapped tests;
- no production activation merely because unit tests pass;
- no secrets in prompts, traces, commits or CI artifacts;
- no claim upgrade (`EXPERIMENTAL` -> `CANONICAL`/`PRODUCTION`) without explicit evidence review;
- no autonomous merge/deploy for high-risk financial/custody changes unless separately authorized by governance policy.

## Cross-repository change set

A feature spanning repositories should carry one federation change-set identifier and repository-local traces.

Example:

```text
CHANGESET-FINOS-001
  synergy_financial_os  -> schema/invariant
  synergy_matrix_sota   -> producer adapter
  synergy_pay_system    -> settlement adapter
  synergychain          -> read-only UI consumer
```

## Review gates

A financial feature is incomplete until its required gates pass, for example:

```text
architecture
schema compatibility
unit tests
cross-repo contract tests
accounting conservation
maturity/liquidity checks
security review
negative controls
reproducibility/evidence
production-readiness review (if applicable)
```

## Claims boundary

Autonomous software engineering can produce code and evidence faster. It cannot turn an unverified economic hypothesis into truth, provide legal authorization or replace independent security/accounting review where required.
