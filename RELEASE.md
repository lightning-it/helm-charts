# Release Model

This repository follows the Lightning IT shared release and quality model.

## Repository Classification

- Repository: `helm-charts`
- Type: `helm_chart`
- Release type: `none`
- Artifact type: `helm_chart`
- Visibility: `public`
- Release evidence: `disabled`
- Heavy Incus release validation: `not required`

## Branch Flow

- `develop` is the integration branch for normal work, Renovate updates, and shared-assets-lit synchronization.
- `main` is the protected release branch.
- This repository does not publish release artifacts; `main` still represents the protected stable branch.
- A `develop` to `main` promotion PR is created automatically when releasable changes exist.
- The `develop` to `main` PR is a manual gate and must never be auto-merged.
- After `main` changes, a `main` to `develop` backmerge PR is created or updated automatically.
- Backmerge PRs may auto-merge only when required checks are green and there are no conflicts.

## Mandatory Quality Gates

- Required profiles: `pre-commit, helm-lint, helm-template, values-validation`.
- OS matrix: `ubuntu-latest`.
- Product/runtime matrix: `helm, kubernetes`.
- Fork pull requests run validation without publishing credentials.
- Publishing secrets are available only to trusted `main` release workflows.
- GitHub token permissions must stay least-privilege for each workflow.

## Helm Chart Release

- CI validates chart structure, linting, template rendering, and values examples.
- Chart packages or OCI pushes, when enabled, are produced only from trusted `main` release workflows.
- Values files used in CI must be sanitized examples and must not contain environment secrets.

## Release Evidence

Release evidence is disabled because this repository does not publish release artifacts. Evidence records the repository name, repository type, version, tag, commit SHA, workflow run, tested matrix combinations, passed/failed/skipped jobs, built artifacts, published artifacts, changelog link, security scan result, and SBOM/provenance/signature links when available.

Evidence files must not contain tokens, credentials, private inventory values, or secret material.
