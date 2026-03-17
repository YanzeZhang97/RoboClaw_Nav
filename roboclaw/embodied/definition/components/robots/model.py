"""Robot manifests and primitive contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from roboclaw.embodied.definition.foundation.schema import (
    CapabilityFamily,
    CompletionSpec,
    HealthSchema,
    ObservationSchema,
    ParameterSpec,
    PrimitiveKind,
    RobotType,
    SafetyProfile,
    ToleranceSpec,
)


@dataclass(frozen=True)
class PrimitiveSpec:
    """One reusable primitive exposed by a robot."""

    name: str
    kind: PrimitiveKind
    capability_family: CapabilityFamily
    description: str
    parameters: tuple[ParameterSpec, ...] = field(default_factory=tuple)
    tolerance: ToleranceSpec | None = None
    completion: CompletionSpec | None = None
    backed_by: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RobotManifest:
    """Static robot definition independent from sensors and carriers."""

    id: str
    name: str
    description: str
    robot_type: RobotType
    capability_families: tuple[CapabilityFamily, ...]
    primitives: tuple[PrimitiveSpec, ...]
    observation_schema: ObservationSchema
    health_schema: HealthSchema
    default_named_poses: tuple[str, ...] = field(default_factory=tuple)
    suggested_sensor_ids: tuple[str, ...] = field(default_factory=tuple)
    safety: SafetyProfile = field(default_factory=SafetyProfile)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        primitive_names = [primitive.name for primitive in self.primitives]
        if len(set(primitive_names)) != len(primitive_names):
            raise ValueError(f"Duplicate primitive names in robot '{self.id}'.")
        if not self.observation_schema.fields:
            raise ValueError(f"Robot '{self.id}' must define at least one observation field.")
        if not self.health_schema.fields:
            raise ValueError(f"Robot '{self.id}' must define at least one health field.")

    def supports(self, capability: CapabilityFamily) -> bool:
        return capability in self.capability_families

    def primitive(self, name: str) -> PrimitiveSpec | None:
        return next((primitive for primitive in self.primitives if primitive.name == name), None)
