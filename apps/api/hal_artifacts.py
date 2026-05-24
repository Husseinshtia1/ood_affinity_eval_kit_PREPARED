from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .hal_deployment_generator import build_hal_deployment_plan
from .settings import get_settings


@dataclass(frozen=True)
class GeneratedHALArtifact:
    artifact_name: str
    provider: str
    target: str
    path: str
    recommended: bool


def hal_artifacts_dir() -> Path:
    settings = get_settings()
    path = settings.temp_storage_dir / 'hal_artifacts'
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_hal_deployment_artifacts() -> dict:
    plan = build_hal_deployment_plan()
    output_dir = hal_artifacts_dir()
    generated: list[GeneratedHALArtifact] = []

    manifest = {
        'provider': plan.provider,
        'profile': plan.profile,
        'warnings': plan.warnings,
        'artifacts': [],
    }

    for artifact in plan.artifacts:
        safe_name = artifact.artifact_name.replace('/', '_')
        path = output_dir / safe_name
        path.write_text(artifact.content_preview, encoding='utf-8')
        generated_artifact = GeneratedHALArtifact(
            artifact_name=artifact.artifact_name,
            provider=artifact.provider,
            target=artifact.target,
            path=str(path),
            recommended=artifact.recommended,
        )
        generated.append(generated_artifact)
        manifest['artifacts'].append(asdict(generated_artifact))

    manifest_path = output_dir / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding='utf-8')

    return {
        'output_dir': str(output_dir),
        'manifest_path': str(manifest_path),
        'generated': [asdict(item) for item in generated],
    }
