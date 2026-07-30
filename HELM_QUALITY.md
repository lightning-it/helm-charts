# Helm Quality and GitOps Controls

Every product chart under `charts/*/Chart.yaml` is governed by the
repository-owned `helm / quality` gate. The gate is intended to make chart
defaults safe, reviewable, and reproducible before a change reaches the stable
`main` branch.

## Governing Decisions and Standards

- [Mandatory CI Quality and Artifact Assurance][ci-adr]
- [Branching, Review and Release Governance][branch-adr]
- [Repository and Secure SDLC Standard][sdlc-standard]
- [Quality Gates and Definition of Done][quality-standard]
- [OpenSSF and Software Supply Chain Assurance][supply-chain-standard]
- [OpenSSF OSPS Baseline][osps-baseline]
- [Kubernetes Pod Security Standards][pod-security]
- [Kubernetes RBAC good practices][rbac]
- [Kubernetes resource management][resources]
- [Kubernetes liveness, readiness, and startup probes][probes]
- [Helm values schema files][helm-schema]

## Enforced Gate

The required `helm / quality` job:

1. verifies that all generated `values.schema.json` files match their
   corresponding `values.yaml`;
2. runs `helm lint` and `helm template` for every product chart;
3. parses every rendered manifest and fails on missing API metadata, mutable
   images, literal Secret content, RBAC wildcards, missing pod or container
   hardening, incomplete resource requests and limits, or missing probes for
   long-running workloads; and
4. fails when a waiver is missing, expired, duplicated, or no longer matches a
   current finding.

Run the same checks locally:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install \
  --require-hashes \
  --requirement .github/requirements/repository-quality.lock
.venv/bin/python scripts/generate-values-schemas.py --check
bash scripts/validate-helm-charts.sh
.venv/bin/python scripts/validate-kubernetes-policy.py
```

After an intentional `values.yaml` change, regenerate schemas and review their
diff:

```bash
.venv/bin/python scripts/generate-values-schemas.py --write
```

## Waiver Contract

Temporary exceptions live in `.lit/helm-policy-waivers.yml`. Each exact finding
requires an owner, reason, compensating control, and expiry date. Renewal is a
new reviewed decision; an expired or stale entry fails CI.

Vendored chart behavior should be corrected through supported values or an
upstream update wherever possible. A waiver is reserved for behavior that
cannot safely be changed through the pinned upstream chart contract.

## GitOps Promotion, Drift, and Rollback Evidence

- Normal changes and Renovate dependency updates enter through `develop`.
- The stable state moves to `main` only through the reviewed promotion PR.
- A GitOps consumer must pin a chart version or immutable Git commit; tracking
  a floating branch is not an accepted production promotion mechanism.
- The GitOps controller's reconciliation status and diff are the drift
  evidence. A promotion is complete only when the controller reports the
  intended revision healthy and synchronized.
- Rollback uses a reviewed revert or a repin to the last accepted chart version
  or commit. Preserve the PR, exact Git SHA, controller reconciliation, and
  health result as rollback evidence.
- No chart package is published by this repository today. If publishing is
  enabled, release evidence, SBOM, provenance, signature, and consumer-side
  verification become mandatory before the publishing gate can be accepted.

[branch-adr]: https://lit.atlassian.net/wiki/spaces/LIT/pages/2878603438
[ci-adr]: https://lit.atlassian.net/wiki/spaces/LIT/pages/2878636340
[helm-schema]: https://helm.sh/docs/topics/charts/#schema-files
[osps-baseline]: https://baseline.openssf.org/
[pod-security]: https://kubernetes.io/docs/concepts/security/pod-security-standards/
[probes]: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
[quality-standard]: https://lit.atlassian.net/wiki/spaces/LIT/pages/2887123058
[rbac]: https://kubernetes.io/docs/concepts/security/rbac-good-practices/
[resources]: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
[sdlc-standard]: https://lit.atlassian.net/wiki/spaces/LIT/pages/2887778335
[supply-chain-standard]: https://lit.atlassian.net/wiki/spaces/LIT/pages/2887024876
