"""Default embodied catalog and registries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from roboclaw.embodied.definition import (
    AssemblyRegistry,
    DeploymentRegistry,
    RGB_CAMERA,
    RobotRegistry,
    SO101_ROBOT,
    SensorRegistry,
    SimulatorRegistry,
)
from roboclaw.embodied.execution import (
    AdapterRegistry,
    DEFAULT_PROCEDURES,
    ProcedureRegistry,
)


@dataclass(frozen=True)
class EmbodiedCatalog:
    """One place to access the built-in embodied registries."""

    robots: RobotRegistry
    sensors: SensorRegistry
    assemblies: AssemblyRegistry
    adapters: AdapterRegistry
    procedures: ProcedureRegistry
    deployments: DeploymentRegistry
    simulators: SimulatorRegistry


def build_default_catalog() -> EmbodiedCatalog:
    """Build the default embodied catalog.

    This catalog contains reusable framework definitions only. Concrete
    assemblies, deployments, adapters, and simulator scenarios should be
    generated under the active workspace.
    """

    robots = RobotRegistry()
    robots.register(SO101_ROBOT)

    sensors = SensorRegistry()
    sensors.register(RGB_CAMERA)

    assemblies = AssemblyRegistry()

    adapters = AdapterRegistry()

    procedures = ProcedureRegistry()
    for procedure in DEFAULT_PROCEDURES:
        procedures.register(procedure)

    deployments = DeploymentRegistry()

    simulators = SimulatorRegistry()

    return EmbodiedCatalog(
        robots=robots,
        sensors=sensors,
        assemblies=assemblies,
        adapters=adapters,
        procedures=procedures,
        deployments=deployments,
        simulators=simulators,
    )


def build_catalog(workspace: Path | None = None) -> EmbodiedCatalog:
    """Build the framework catalog and optionally merge workspace assets."""

    catalog = build_default_catalog()
    if workspace is None:
        return catalog

    from roboclaw.embodied.workspace import load_workspace_assets

    return load_workspace_assets(catalog, workspace)
