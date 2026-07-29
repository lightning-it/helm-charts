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
