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

<!-- LIT REP-60 review governance: start -->
<!-- cspell:ignore litroc -->

## REP-60 current-revision review governance

- Local validation is deterministic only. It must never invoke Codex, GitHub
  Copilot, another model, or an external AI endpoint. Authoritative AI review
  runs only in the protected GitHub pipeline and binds the exact PR head.
- Lightning IT automation may request and fund one GitHub Copilot review only
  when the exact PR author is `litroc`, and only at the finalization boundary;
  intermediate `synchronize` pushes must not trigger AI review. Any finding
  requires correction and a final current-head re-review. The request is
  consumed once per head; unavailable or quota-blocked reviews fail closed
  without an automatic retry. Organization-funded Codex remediation and its
  single re-review are likewise restricted to `litroc`.
- Every other human or external contributor supplies any required current-head
  Copilot review under their own entitlement and cost. Lightning IT verifies
  valid evidence but never requests or funds that review, and personal tokens or
  provider keys never enter Actions.
- A same-repository PR authored exactly by
  `lightning-it-release-automation[bot]` uses only the protected MLX-90 §7.2
  Exact-Revision Codex check. It must never request Copilot or synthesize a
  Copilot success.
- A proven ancestry-only main-to-develop backmerge uses the deterministic
  evidence-bound exemption and performs zero AI calls. Unknown automation
  identities fail closed.
- The only neutral merge-gate result is `Current revision review`. Missing,
  stale, ambiguous, or unresolved review evidence blocks the merge.

<!-- LIT REP-60 review governance: end -->

<!-- LIT REP-60 evidence lifecycle: start -->

### REP-60 evidence lifecycle (mandatory)

- Every pull request into `develop` retains its exact-final-head native GitHub
  CI, required-check, and review history as the authoritative evidence for
  acceptance into `develop`.
- A pull request into `develop` MUST NOT create or retain an additional durable
  release-evidence package, duplicate WORM artifact, or second AI-review
  evidence outside that native GitHub history.
- Only the protected `develop` to `main` promotion creates exactly one durable,
  complete release-evidence package. It binds the full integrated promotion
  diff, base, head, merge base, integration tree, policy, reviewer result, and
  all release and audit checks.
- Agents, workflows, and repository-local rules MUST NOT duplicate that durable
  evidence per `develop` pull request or invoke local AI to create evidence.
  Repository-local rules may only make this lifecycle stricter.

<!-- LIT REP-60 evidence lifecycle: end -->

<!-- LIT Devtools container governance: start -->

## Devtools container execution boundary

- Every deterministic lint, format, type-check, test, build, packaging,
  policy, and validation workload runs in the digest-pinned Lightning IT
  Devtools image, locally and in CI. Host-language runtimes never provide
  acceptance evidence.
- The host boundary is limited to Git, the supported container engine, and the
  centrally managed Devtools, push-ready, and pre-commit dispatchers. A
  dispatcher may inspect Git state and start the pinned container, but it must
  not execute a repository validator through host Python, Node.js, Ansible,
  Ruff, a Python type checker, markdownlint, Renovate, or a comparable host
  runtime.
- If a required command or compatible version is absent, fail closed. Add and
  pin it in `container-ee-wunder-devtools-ubi9`, release that image normally,
  update the centrally managed digest, and rerun the gate. Host fallbacks,
  ad-hoc virtual environments, and unpinned helper images are forbidden.
- Repository-owned tests derive the exact full Devtools image reference from
  the centrally managed push-ready engine when checking the installed wrapper;
  they never hard-code an independent release tag that can drift during a
  normal image rollout.
- Defaults stay read-only, offline, socket-free, capability-dropped, and
  non-privileged. A gate may opt into only its explicit tested minimum. Linked
  Git metadata remains read-only and container Git may trust only
  `/workspace`, never `*`. Executable temporary fixtures use the isolated
  container home while generic `/tmp` remains non-executable.
- The Devtools boundary never makes local Codex, Copilot, or other model calls
  and never receives personal AI credentials.

<!-- LIT Devtools container governance: end -->

<!-- LIT AI task governance: start -->

## AI model and token governance

Apply `LIT-GEN-GDR-GOV-30-Budget-Conscious-AI-Model-Selection` to every
substantive Codex or ChatGPT-assisted task. Before investigation, planning, tool
use, implementation, or delegation, record a compact task profile in the task
chat: work item, risk (`low`, `normal`, or `high`), smallest sufficient
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
