"""Verification protocols for embodied runtime assurance.

Only preflight verification can run in the current LeRobot subprocess
architecture. The runtime protocols below are intentionally scaffolded for a
future host-visible action/observation stream.
"""

from __future__ import annotations

from typing import Any, Protocol

from roboclaw.embodied.verification.types import VerificationRequest, VerificationResult


class Verifier(Protocol):
    """Validate information available before a managed session starts."""

    def verify(self, request: VerificationRequest) -> VerificationResult:
        """Return violations that should stop launch."""


class SafetyFilter(Protocol):
    """Future pre-execution action filter.

    Activation requires host-visible policy action proposals. Today's inference
    path launches LeRobot as a subprocess, so the host process cannot yet apply
    runtime safety filters to action chunks.
    """

    def filter(self, proposed_action: Any, context: Any) -> Any:
        """Return a safe action or raise once runtime streams are exposed."""


class RuntimeMonitor(Protocol):
    """Future runtime failure monitor.

    Activation requires host-visible observations, actions, and policy-side
    signals such as action chunks, embeddings, or distributions.
    """

    def update(self, observation: Any, action: Any) -> Any | None:
        """Return an alert when runtime monitoring detects a failure risk."""
