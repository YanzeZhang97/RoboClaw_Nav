"""No-op verification backends."""

from __future__ import annotations

from typing import Any

from roboclaw.embodied.verification.types import VerificationRequest, VerificationResult


class NoOpVerifier:
    """Verifier that never blocks launch."""

    def verify(self, request: VerificationRequest) -> VerificationResult:
        return VerificationResult()


class NoOpSafetyFilter:
    """Placeholder safety filter until runtime action streams are available."""

    def filter(self, proposed_action: Any, context: Any) -> Any:
        return proposed_action


class NoOpRuntimeMonitor:
    """Placeholder runtime monitor until observation/action streams are available."""

    def update(self, observation: Any, action: Any) -> None:
        return None
