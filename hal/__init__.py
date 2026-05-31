"""HAL - Hosting Adaptation Layer.

Standalone self-adaptive infrastructure intelligence package.

This package is intentionally independent from the host SaaS application.
Application-specific integrations should live outside this package and call HAL
through stable public functions/classes.
"""

from .engine import HALEngine
from .models import HALCapabilities, HALDecision, HALProfile

__all__ = [
    "HALEngine",
    "HALCapabilities",
    "HALDecision",
    "HALProfile",
]
