# helm-charts

<!-- BEGIN LIT_QUALITY_BADGES -->

[![CI](https://github.com/lightning-it/helm-charts/actions/workflows/repository-quality.yml/badge.svg?branch=develop)](https://github.com/lightning-it/helm-charts/actions/workflows/repository-quality.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/lightning-it/helm-charts/badge)](https://scorecard.dev/viewer/?uri=github.com/lightning-it/helm-charts)

<!-- END LIT_QUALITY_BADGES -->

<!-- BEGIN LIT_SHARED_RELEASE_MODEL -->

## Release and Quality Model

This repository follows the Lightning IT shared release and quality model.

See [RELEASE.md](./RELEASE.md) for:

- branch and release flow
- required quality checks
- test matrix
- release evidence
- artifact publishing
- supported repository-specific release behavior

Repository classification: **Helm Chart Repository**.
Required test profiles: `pre-commit, helm-lint, helm-template, values-validation`.
Publishing targets: `none`.

## Supported and Tested Platforms

| Platform / Product | Status | Validation |
|---|---:|---|
| ubuntu-latest | Supported | Helm lint/template |
| helm | Tested where applicable | Helm lint/template |
| kubernetes | Tested where applicable | Helm lint/template |

<!-- END LIT_SHARED_RELEASE_MODEL -->
