from roboclaw.embodied import (
    RGB_CAMERA,
    SO101_ROBOT,
    build_default_catalog,
    compose_assemblies,
)
from roboclaw.embodied.definition.systems.assemblies import AssemblyBlueprint, RobotAttachment
from roboclaw.embodied.definition.systems.assemblies.model import SensorAttachment
from roboclaw.embodied.execution.orchestration.runtime import RuntimeManager, RuntimeStatus
from roboclaw.embodied.definition.foundation.schema import CarrierKind, RobotType
from roboclaw.embodied.execution.integration.carriers.real import build_real_ros2_target
from roboclaw.embodied.execution.integration.transports.ros2 import build_standard_ros2_contract


def _workspace_blueprint() -> AssemblyBlueprint:
    return AssemblyBlueprint(
        id="workspace_so101",
        name="Workspace SO101",
        description="Workspace-generated embodied assembly.",
        robots=(
            RobotAttachment(
                attachment_id="primary",
                robot_id="so101",
            ),
        ),
        sensors=(
            SensorAttachment(
                attachment_id="wrist_camera",
                sensor_id="rgb_camera",
                mount="wrist",
            ),
        ),
        execution_targets=(
            build_real_ros2_target(
                target_id="real",
                description="Real target",
                ros2=build_standard_ros2_contract("workspace_so101", "real"),
            ),
        ),
        default_execution_target_id="real",
    )


def test_embodied_catalog_contains_reusable_definitions_only() -> None:
    catalog = build_default_catalog()

    assert catalog.robots.get("so101").robot_type == RobotType.ARM
    assert catalog.sensors.get("rgb_camera").default_topic_name == "image_raw"
    assert catalog.assemblies.list() == ()
    assert catalog.adapters.for_assembly("workspace_so101") == ()
    assert catalog.deployments.for_assembly("workspace_so101") == ()
    assert RGB_CAMERA.supports_intrinsics is True


def test_workspace_blueprint_can_be_composed_into_a_variant() -> None:
    base = _workspace_blueprint()
    overhead_variant = base.remap_sensor(
        "wrist_camera",
        to_mount="overhead",
    )
    composed = compose_assemblies(base, overhead_variant).build()

    assert composed.sensors == (
        SensorAttachment(
            attachment_id="wrist_camera",
            sensor_id="rgb_camera",
            mount="overhead",
            config=None,
            optional=False,
        ),
    )
    assert composed.execution_target("real").carrier == CarrierKind.REAL


def test_runtime_manager_tracks_active_session() -> None:
    manager = RuntimeManager()
    session = manager.create(
        session_id="demo",
        assembly_id="workspace_so101",
        target_id="real",
        deployment_id="workspace_local",
        adapter_id="workspace_ros2_adapter",
    )

    manager.mark_status("demo", RuntimeStatus.READY)

    assert session.assembly_id == "workspace_so101"
    assert session.adapter_id == "workspace_ros2_adapter"
    assert session.status == RuntimeStatus.READY
    assert SO101_ROBOT.suggested_sensor_ids == ("rgb_camera",)
