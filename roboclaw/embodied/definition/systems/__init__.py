"""System-layer exports for embodied definitions."""

from roboclaw.embodied.definition.systems.assemblies import (
    AssemblyBlueprint,
    AssemblyManifest,
    AssemblyRegistry,
    RobotAttachment,
    SensorAttachment,
    compose_assemblies,
)
from roboclaw.embodied.definition.systems.deployments import (
    DeploymentProfile,
    DeploymentRegistry,
)
from roboclaw.embodied.definition.systems.simulators import (
    SimulatorRegistry,
    SimulatorScenario,
    SimulatorWorld,
)

__all__ = [
    "AssemblyBlueprint",
    "AssemblyManifest",
    "AssemblyRegistry",
    "DeploymentProfile",
    "DeploymentRegistry",
    "RobotAttachment",
    "SensorAttachment",
    "SimulatorRegistry",
    "SimulatorScenario",
    "SimulatorWorld",
    "compose_assemblies",
]
