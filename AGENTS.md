# Lightning IT Engineering Agent Guide

## Scope and sources of truth

- Inspect the repository, its `README`, `CONTRIBUTING.md`, `.lit/` policy,
  workflows, tests, and build metadata before changing code.
- Preserve repository-specific behavior unless an approved ADR changes it.
- Files distributed by `lightning-it/shared-assets-lit` are centrally managed;
  change their canonical source and synchronize them instead of maintaining
  divergent downstream copies.
- Repository settings and protected environments are managed through
  `lightning-it/github-management-lit`.

## Engineering baseline

- Keep changes small, reviewable, deterministic, and covered by tests that
  exercise success and failure behavior.
- Validate external input, use explicit timeouts, and fail closed when security
  or policy evidence is malformed, missing, or stale.
- Apply least privilege to credentials, workflow permissions, environments,
  network access, and repository access.
- Never commit credentials or sensitive operational data. Avoid exposing them
  in logs, exceptions, fixtures, examples, or generated artifacts.
- Pin third-party GitHub Actions to immutable commit SHAs and pin build/runtime
  dependencies according to the repository's dependency policy.
- Preserve provenance: releases and deployments must be traceable to an exact
  commit, reviewed checks, and immutable artifacts.

## Required standards

- Use the repository's applicable Lightning IT Engineering ADRs as the
  decision record.
- Follow the OpenSSF Scorecard controls and OpenSSF Best Practices criteria
  applicable to the repository.
- Apply secure-development practices from NIST SSDF (SP 800-218), supply-chain
  controls from SLSA, and artifact signing/verification practices from Sigstore
  where the repository builds or publishes artifacts.
- Apply OWASP guidance relevant to the implementation, including secure
  defaults, dependency hygiene, input validation, and secret handling.

## Validation and review

- Run `python3 scripts/lit-push-ready.py push-ready` before pushing when the
  script is present.
- Run the repository-specific lint, test, build, security, and packaging gates
  documented in `.lit/push-ready.json`, `CONTRIBUTING.md`, and CI.
- Treat `AGENTS.md` as the canonical Codex and Copilot contract.
- `.github/copilot-instructions.md` must contain the current managed
  `AGENTS_SHA256` binding.
- Resolve or explicitly disposition every automated-review finding against the
  current commit and rerun affected deterministic checks.
- Do not weaken a required check, branch rule, security control, or test merely
  to make a change pass.

## Branch and change management

- Normal changes target `develop`; stable promotion to `main` uses a reviewed
  pull request unless a repository ADR explicitly defines another model.
- Do not push directly to protected branches or bypass required checks.
- Temporary self-approval is permitted only where ADR-70 applies, must bind to
  the exact immutable SHA or saved plan, and must be recorded separately for
  each protected action.

<!-- LIT AI task governance: start -->

## AI model and token governance

Apply `LIT-GEN-GDR-GOV-30-Budget-Conscious-AI-Model-Selection` to every
substantive Codex or ChatGPT-assisted task. Before investigation, planning,
tool use, implementation, or delegation, record a compact task profile in the
task chat: work item, risk (`low`, `normal`, or `high`), smallest sufficient
model/reasoning choice, rationale, and a concrete escalation condition.

- Use the balanced, lowest reliable capability by default. Escalate to a
  premium/frontier model or higher reasoning only for a high-risk decision,
  complex architecture/debugging/dependencies, or a documented focused failure
  of the standard approach. Restrict that escalation to the difficult subtask.
- Never use Speed Mode. Do not replace verification with a more expensive model
  or sacrifice quality to reduce elapsed time.
- Retrieve only relevant issue, files, logs, and source records; avoid broad
  repository or chat-history loading, speculative analysis, and unbounded retry
  loops. Delegate only independent, bounded work that reduces total effort.
- For GitHub or Jira work, include the task profile in the issue/task record
  when AI assistance materially affects execution. Close with verification and
  remaining risks; preserve durable decisions in Confluence, Jira, or GitHub.

<!-- LIT AI task governance: end -->
