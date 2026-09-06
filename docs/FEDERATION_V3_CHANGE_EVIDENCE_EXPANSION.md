# Federation V3 — AI Coder / Engineering Change Evidence expansion

AI Coder translates approved semantic requirements into bounded repository changes with evidence.

## Expanded responsibilities
- proposed change sets;
- file/repo impact analysis;
- dependency-aware patch planning;
- test generation/execution requests;
- before/after evidence capture;
- release/commit provenance;
- cross-repo migration sequencing;
- rollback metadata.

## Required objects
`ChangeRequest`, `ImpactGraph`, `PatchSet`, `TestPlan`, `TestEvidence`, `ReviewDecision`, `ReleaseCandidate`, `RollbackPlan`.

## Federation contract
Input requirements come from `ai_language` / `synergy_system`. AI Coder may prepare code and evidence, but merge/deployment authority remains external unless an explicit capability grants it.

## Rule
`generated code != verified implementation`; verification requires tests/evidence appropriate to the domain.
