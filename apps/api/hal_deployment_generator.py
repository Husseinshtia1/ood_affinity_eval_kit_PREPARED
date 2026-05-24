from __future__ import annotations

from dataclasses import asdict, dataclass

from .hosting_adaptation import detect_hosting_capabilities
from .hal_optimizer import build_runtime_optimization


@dataclass(frozen=True)
class DeploymentArtifactRecommendation:
    provider: str
    artifact_name: str
    target: str
    recommended: bool
    reason: str
    content_preview: str


@dataclass(frozen=True)
class HALDeploymentPlan:
    provider: str
    profile: str
    artifacts: list[DeploymentArtifactRecommendation]
    warnings: list[str]


def railway_preview() -> str:
    return '''{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {"builder": "DOCKERFILE", "dockerfilePath": "Dockerfile.api"},
  "deploy": {"startCommand": "sh scripts/api_entrypoint.sh", "healthcheckPath": "/health"}
}'''


def docker_compose_preview() -> str:
    return '''services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    env_file:
      - .env.production
    ports:
      - "8000:8000"'''


def render_preview() -> str:
    return '''services:
  - type: web
    name: prepared-api
    env: docker
    dockerfilePath: ./Dockerfile.api
    healthCheckPath: /health'''


def fly_preview() -> str:
    return '''app = "prepared-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile.api"

[http_service]
  internal_port = 8000
  force_https = true'''


def build_hal_deployment_plan() -> HALDeploymentPlan:
    capabilities = detect_hosting_capabilities()
    optimization = build_runtime_optimization()
    provider = capabilities.provider
    profile = optimization.profile
    warnings: list[str] = []

    if profile == 'free-demo':
        warnings.append('Generated deployment should keep Redis, worker, SMTP, and persistent object storage optional.')
        warnings.append('Do not process real customer data in this profile.')
    if profile != 'production':
        warnings.append('Use generated artifacts as deployment guidance; review secrets and persistence before production launch.')

    artifacts = [
        DeploymentArtifactRecommendation(
            provider='railway',
            artifact_name='railway.json',
            target='Railway API service',
            recommended=provider in {'railway', 'generic'} or profile == 'free-demo',
            reason='Railway supports Dockerfile deployments and has already been verified for this project.',
            content_preview=railway_preview(),
        ),
        DeploymentArtifactRecommendation(
            provider='generic-vps',
            artifact_name='docker-compose.generated.yml',
            target='VPS / Coolify / Dokploy / CapRover',
            recommended=profile in {'partial-managed', 'production'},
            reason='Docker Compose is best when persistent database, Redis, and storage are available or self-managed.',
            content_preview=docker_compose_preview(),
        ),
        DeploymentArtifactRecommendation(
            provider='render',
            artifact_name='render.yaml',
            target='Render Blueprint',
            recommended=provider in {'render', 'generic'},
            reason='Render supports Docker web services and background workers.',
            content_preview=render_preview(),
        ),
        DeploymentArtifactRecommendation(
            provider='flyio',
            artifact_name='fly.toml',
            target='Fly.io app',
            recommended=provider in {'flyio', 'generic'},
            reason='Fly.io supports Dockerfile apps with small globally deployable services.',
            content_preview=fly_preview(),
        ),
    ]

    return HALDeploymentPlan(provider=provider, profile=profile, artifacts=artifacts, warnings=warnings)


def hal_deployment_plan_dict() -> dict:
    plan = build_hal_deployment_plan()
    return {
        'provider': plan.provider,
        'profile': plan.profile,
        'warnings': plan.warnings,
        'artifacts': [asdict(artifact) for artifact in plan.artifacts],
    }
