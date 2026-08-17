# SINERGY engineering review matrix

## Change classes

### Documentation-only
Required: ownership check, provenance, link/schema consistency.

### Pure internal refactor
Required: existing tests, behavior regression, secret/path safety.

### Cross-repository schema change
Required: versioning, producer/consumer compatibility, migration plan, contract tests.

### Financial/accounting change
Required: balanced-journal tests, HardNAV/profit classification tests, capital-flow controls, stress/negative controls.

### Credit/maturity change
Required: funding-duration tests, LCR/liquidity tests, default/loss behavior, concentration limits.

### Payment/settlement change
Required: idempotency, provider readiness, capacity reservation, reconciliation, reversal behavior, secret boundary.

### Smart-contract/custody change
Required: compile/tests, fork tests where relevant, access-control review, replay/reentrancy/limits, key/custody review, independent audit gate before production.

### AI-policy change
Required: deterministic fallback, authority boundary, uncertainty/failure behavior, no direct ledger mutation, shadow/evaluation evidence.

## Evidence outcome

Reviewers must record both:

```text
implementation_status
claim_status
```

A technically correct implementation may still have an `EXPERIMENTAL` economic claim.
