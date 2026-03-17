"""Cross-robot procedures for first-stage embodied interactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - Python < 3.11 fallback for local tooling.
    class StrEnum(str, Enum):
        """Fallback for Python versions without enum.StrEnum."""

from roboclaw.embodied.definition.foundation.schema import CapabilityFamily


class ProcedureKind(StrEnum):
    """Procedure category."""

    CONNECT = "connect"
    CALIBRATE = "calibrate"
    MOVE = "move"
    DEBUG = "debug"
    RESET = "reset"


@dataclass(frozen=True)
class ProcedureStep:
    """One executable step in a procedure."""

    id: str
    action: str
    description: str


@dataclass(frozen=True)
class ProcedureDefinition:
    """Named procedure composed from stable steps."""

    id: str
    kind: ProcedureKind
    description: str
    required_capabilities: tuple[CapabilityFamily, ...] = field(default_factory=tuple)
    steps: tuple[ProcedureStep, ...] = field(default_factory=tuple)
