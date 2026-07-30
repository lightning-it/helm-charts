from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


policy = load_script("validate-kubernetes-policy.py")
schemas = load_script("generate-values-schemas.py")


class SchemaTests(unittest.TestCase):
    def test_schema_is_deterministic_and_preserves_types(self):
        value = {"z": True, "a": ["one", "two"], "count": 2}
        self.assertEqual(
            schemas.schema_for(value),
            {
                "type": "object",
                "properties": {
                    "a": {"type": "array", "items": {"type": "string"}},
                    "count": {"type": "integer"},
                    "z": {"type": "boolean"},
                },
                "additionalProperties": True,
            },
        )


class PolicyTests(unittest.TestCase):
    def test_secure_deployment_has_no_findings(self):
        document = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "secure"},
            "spec": {
                "template": {
                    "spec": {
                        "securityContext": {
                            "runAsNonRoot": True,
                            "seccompProfile": {"type": "RuntimeDefault"},
                        },
                        "containers": [
                            {
                                "name": "app",
                                "image": "example.invalid/app:v1",
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "readOnlyRootFilesystem": True,
                                    "capabilities": {"drop": ["ALL"]},
                                },
                                "resources": {
                                    "requests": {"cpu": "10m", "memory": "16Mi"},
                                    "limits": {"cpu": "100m", "memory": "64Mi"},
                                },
                                "readinessProbe": {"tcpSocket": {"port": 8080}},
                                "livenessProbe": {"tcpSocket": {"port": 8080}},
                            }
                        ],
                    }
                }
            },
        }
        self.assertEqual(list(policy.validate_document("charts/test", document)), [])

    def test_insecure_container_fails_closed(self):
        document = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "insecure"},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {"name": "app", "image": "example.invalid/app:latest"}
                        ]
                    }
                }
            },
        }
        identifiers = [
            finding.identifier
            for finding in policy.validate_document("charts/test", document)
        ]
        self.assertTrue(any(":run-as-non-root" in item for item in identifiers))
        self.assertTrue(any(":seccomp" in item for item in identifiers))
        self.assertTrue(any(":immutable-image" in item for item in identifiers))

    def test_expired_waiver_is_rejected(self):
        content = """\
version: 1
waivers:
  - id: finding
    owner: platform-engineering
    reason: test
    compensating_control: test
    expires: 2000-01-01
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "waivers.yml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expired"):
                policy.load_waivers(path)


if __name__ == "__main__":
    unittest.main()
