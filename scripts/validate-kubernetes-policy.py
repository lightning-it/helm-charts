#!/usr/bin/env python3
"""Validate rendered Helm manifests against the LIT Kubernetes baseline."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKLOAD_KINDS = frozenset(
    {"CronJob", "DaemonSet", "Deployment", "Job", "Pod", "StatefulSet"}
)
LONG_RUNNING_KINDS = frozenset({"DaemonSet", "Deployment", "StatefulSet"})
RBAC_KINDS = frozenset({"ClusterRole", "Role"})
REQUIRED_RESOURCE_KEYS = ("cpu", "memory")
HELM_TEMPLATE_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class Finding:
    identifier: str
    message: str


def fail(message: str) -> None:
    raise ValueError(message)


def object_name(document: dict[str, Any]) -> str:
    metadata = document.get("metadata")
    if not isinstance(metadata, dict):
        return "<unnamed>"
    namespace = metadata.get("namespace", "default")
    name = metadata.get("name", "<unnamed>")
    return f"{namespace}/{name}"


def workload_spec(document: dict[str, Any]) -> dict[str, Any]:
    kind = document.get("kind")
    spec = document.get("spec")
    if not isinstance(spec, dict):
        return {}
    if kind == "Pod":
        return spec
    if kind == "CronJob":
        job_template = spec.get("jobTemplate")
        if not isinstance(job_template, dict):
            return {}
        job_spec = job_template.get("spec")
        if not isinstance(job_spec, dict):
            return {}
        template = job_spec.get("template")
    else:
        template = spec.get("template")
    if not isinstance(template, dict):
        return {}
    pod_spec = template.get("spec")
    return pod_spec if isinstance(pod_spec, dict) else {}


def finding(
    chart: str,
    document: dict[str, Any],
    rule: str,
    message: str,
    subject: str = "",
) -> Finding:
    kind = str(document.get("kind", "<unknown>"))
    suffix = f":{subject}" if subject else ""
    identifier = f"{chart}:{kind}:{object_name(document)}:{rule}{suffix}"
    return Finding(identifier, message)


def validate_container(
    chart: str,
    document: dict[str, Any],
    container: dict[str, Any],
    *,
    require_probes: bool,
) -> Iterable[Finding]:
    name = str(container.get("name", "<unnamed>"))
    image = container.get("image")
    if not isinstance(image, str) or not image.strip():
        yield finding(chart, document, "image-required", "container image is missing", name)
    elif (
        image.endswith(":latest")
        or ("@" not in image and ":" not in image.rsplit("/", 1)[-1])
    ):
        yield finding(
            chart,
            document,
            "immutable-image",
            f"image is not digest- or version-pinned: {image}",
            name,
        )

    security = container.get("securityContext")
    if not isinstance(security, dict):
        security = {}
    if security.get("allowPrivilegeEscalation") is not False:
        yield finding(
            chart,
            document,
            "no-privilege-escalation",
            "allowPrivilegeEscalation must be false",
            name,
        )
    if security.get("readOnlyRootFilesystem") is not True:
        yield finding(
            chart,
            document,
            "read-only-root-filesystem",
            "readOnlyRootFilesystem must be true",
            name,
        )
    capabilities = security.get("capabilities")
    drops = capabilities.get("drop") if isinstance(capabilities, dict) else None
    if not isinstance(drops, list) or "ALL" not in drops:
        yield finding(
            chart,
            document,
            "drop-all-capabilities",
            "container capabilities must drop ALL",
            name,
        )

    resources = container.get("resources")
    if not isinstance(resources, dict):
        resources = {}
    for resource_class in ("requests", "limits"):
        values = resources.get(resource_class)
        if not isinstance(values, dict):
            values = {}
        for resource in REQUIRED_RESOURCE_KEYS:
            if not values.get(resource):
                yield finding(
                    chart,
                    document,
                    f"resources-{resource_class}-{resource}",
                    f"resources.{resource_class}.{resource} is required",
                    name,
                )

    if require_probes:
        for probe in ("readinessProbe", "livenessProbe"):
            if not isinstance(container.get(probe), dict):
                yield finding(
                    chart,
                    document,
                    probe.replace("Probe", "-probe").lower(),
                    f"{probe} is required for long-running workloads",
                    name,
                )


def validate_document(chart: str, document: object) -> Iterable[Finding]:
    if document is None:
        return
    if not isinstance(document, dict):
        fail(f"{chart}: rendered YAML document must be an object")
    api_version = document.get("apiVersion")
    kind = document.get("kind")
    if not isinstance(api_version, str) or not api_version:
        yield finding(chart, document, "api-version", "apiVersion is required")
    if not isinstance(kind, str) or not kind:
        yield finding(chart, document, "kind", "kind is required")
        return

    if kind == "Secret":
        for field in ("data", "stringData"):
            values = document.get(field)
            if isinstance(values, dict) and any(
                value not in (None, "") for value in values.values()
            ):
                yield finding(
                    chart,
                    document,
                    "no-literal-secret",
                    f"rendered Secret contains non-empty {field}",
                )

    if kind in RBAC_KINDS:
        rules = document.get("rules")
        if not isinstance(rules, list):
            rules = []
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                fail(f"{chart}: {kind} rule {index} must be an object")
            for field in ("apiGroups", "resources", "verbs"):
                values = rule.get(field)
                if isinstance(values, list) and "*" in values:
                    yield finding(
                        chart,
                        document,
                        "no-rbac-wildcards",
                        f"RBAC rule {index} uses wildcard {field}",
                        f"{index}-{field}",
                    )

    if kind not in WORKLOAD_KINDS:
        return
    pod_spec = workload_spec(document)
    if not pod_spec:
        yield finding(chart, document, "pod-spec", "workload pod spec is missing")
        return
    pod_security = pod_spec.get("securityContext")
    if not isinstance(pod_security, dict):
        pod_security = {}
    if pod_security.get("runAsNonRoot") is not True:
        yield finding(
            chart,
            document,
            "run-as-non-root",
            "pod securityContext.runAsNonRoot must be true",
        )
    seccomp = pod_security.get("seccompProfile")
    seccomp_type = seccomp.get("type") if isinstance(seccomp, dict) else None
    if seccomp_type not in ("RuntimeDefault", "Localhost"):
        yield finding(
            chart,
            document,
            "seccomp",
            "pod seccompProfile.type must be RuntimeDefault or Localhost",
        )
    containers = pod_spec.get("containers")
    if not isinstance(containers, list) or not containers:
        yield finding(chart, document, "containers", "workload has no containers")
        return
    for container in containers:
        if not isinstance(container, dict):
            fail(f"{chart}: workload container must be an object")
        yield from validate_container(
            chart,
            document,
            container,
            require_probes=kind in LONG_RUNNING_KINDS,
        )
    init_containers = pod_spec.get("initContainers", [])
    if not isinstance(init_containers, list):
        fail(f"{chart}: initContainers must be an array")
    for container in init_containers:
        if not isinstance(container, dict):
            fail(f"{chart}: init container must be an object")
        yield from validate_container(
            chart,
            document,
            container,
            require_probes=False,
        )


def render_chart(chart_dir: Path) -> list[dict[str, Any]]:
    result = subprocess.run(
        ["helm", "template", "lit-quality", str(chart_dir)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=HELM_TEMPLATE_TIMEOUT_SECONDS,
    )
    return list(yaml.safe_load_all(result.stdout))


def load_waivers(path: Path) -> dict[str, dict[str, Any]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1:
        fail(f"{path}: expected waiver document version 1")
    entries = raw.get("waivers")
    if not isinstance(entries, list):
        fail(f"{path}: waivers must be an array")
    waivers: dict[str, dict[str, Any]] = {}
    today = dt.date.today()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"{path}: waiver {index} must be an object")
        identifier = entry.get("id")
        if not isinstance(identifier, str) or not identifier:
            fail(f"{path}: waiver {index} has no id")
        if identifier in waivers:
            fail(f"{path}: duplicate waiver id: {identifier}")
        for field in ("owner", "reason", "compensating_control"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                fail(f"{path}: waiver {identifier} has no {field}")
        expires = entry.get("expires")
        if not isinstance(expires, dt.date):
            fail(f"{path}: waiver {identifier} expiry must be an ISO date")
        if expires < today:
            fail(f"{path}: waiver {identifier} expired on {expires.isoformat()}")
        waivers[identifier] = entry
    return waivers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--waivers",
        type=Path,
        default=ROOT / ".lit/helm-policy-waivers.yml",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    chart_dirs = sorted(
        path.parent for path in (ROOT / "charts").glob("*/Chart.yaml")
    )
    if not chart_dirs:
        fail("no product charts found under charts/")
    waivers = load_waivers(args.waivers)
    findings: list[Finding] = []
    for chart_dir in chart_dirs:
        chart = chart_dir.relative_to(ROOT).as_posix()
        if not (chart_dir / "values.schema.json").is_file():
            findings.append(
                Finding(
                    f"{chart}:Chart:default/{chart_dir.name}:values-schema",
                    "values.schema.json is required",
                )
            )
        for document in render_chart(chart_dir):
            findings.extend(validate_document(chart, document))

    finding_ids = {item.identifier for item in findings}
    stale_waivers = sorted(set(waivers) - finding_ids)
    if stale_waivers:
        fail("stale waiver ids: " + ", ".join(stale_waivers))
    unwaived = [item for item in findings if item.identifier not in waivers]
    evidence = {
        "charts": len(chart_dirs),
        "findings": len(findings),
        "waived": len(findings) - len(unwaived),
        "unwaived": [
            {"id": item.identifier, "message": item.message}
            for item in unwaived
        ],
    }
    if args.json:
        print(json.dumps(evidence, indent=2, sort_keys=True))
    else:
        print(
            f"Validated {evidence['charts']} charts: "
            f"{evidence['findings']} findings, "
            f"{evidence['waived']} waived, "
            f"{len(unwaived)} unwaived."
        )
        for item in unwaived:
            print(f"ERROR: {item.identifier}: {item.message}", file=sys.stderr)
    return 1 if unwaived else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as exc:
        print(
            "ERROR: helm template timed out after "
            f"{exc.timeout} seconds: {' '.join(str(part) for part in exc.cmd)}",
            file=sys.stderr,
        )
        if exc.stdout:
            print(str(exc.stdout).rstrip(), file=sys.stderr)
        if exc.stderr:
            print(str(exc.stderr).rstrip(), file=sys.stderr)
        raise SystemExit(2) from exc
    except subprocess.CalledProcessError as exc:
        print(
            "ERROR: helm template failed with exit code "
            f"{exc.returncode}: {' '.join(str(part) for part in exc.cmd)}",
            file=sys.stderr,
        )
        if exc.stdout:
            print(str(exc.stdout).rstrip(), file=sys.stderr)
        if exc.stderr:
            print(str(exc.stderr).rstrip(), file=sys.stderr)
        raise SystemExit(2) from exc
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
