"""SO101 robot definition."""

from __future__ import annotations

from roboclaw.embodied.definition.components.robots.model import PrimitiveSpec, RobotManifest
from roboclaw.embodied.definition.foundation.schema import (
    CapabilityFamily,
    CompletionSemantics,
    CompletionSpec,
    HealthFieldSpec,
    HealthSchema,
    HealthLevel,
    ObservationFieldSpec,
    ObservationSchema,
    ParameterSpec,
    PrimitiveKind,
    RobotType,
    SafetyProfile,
    ToleranceSpec,
    ValueUnit,
)

SO101_PRIMITIVES = (
    PrimitiveSpec(
        name="move_joint",
        kind=PrimitiveKind.MOTION,
        capability_family=CapabilityFamily.JOINT_MOTION,
        description="Move one or more joints to target positions.",
        parameters=(
            ParameterSpec(
                "positions",
                "dict[str,float]",
                "Joint name to target value map.",
                True,
                ValueUnit.RADIAN,
                "joint_space",
            ),
        ),
        tolerance=ToleranceSpec(absolute=0.02, settle_time_s=0.2),
        completion=CompletionSpec(
            semantics=CompletionSemantics.GOAL_REACHED,
            timeout_s=5.0,
        ),
        backed_by=("send_action",),
    ),
    PrimitiveSpec(
        name="move_cartesian_delta",
        kind=PrimitiveKind.MOTION,
        capability_family=CapabilityFamily.CARTESIAN_MOTION,
        description="Move the end effector by a small Cartesian delta in the base frame.",
        parameters=(
            ParameterSpec("dx", "float", "Delta x in meters.", False, ValueUnit.METER, "base_link"),
            ParameterSpec("dy", "float", "Delta y in meters.", False, ValueUnit.METER, "base_link"),
            ParameterSpec("dz", "float", "Delta z in meters.", False, ValueUnit.METER, "base_link"),
        ),
        tolerance=ToleranceSpec(absolute=0.005, settle_time_s=0.15),
        completion=CompletionSpec(
            semantics=CompletionSemantics.GOAL_REACHED,
            timeout_s=3.0,
        ),
        backed_by=("move_ee_delta",),
    ),
    PrimitiveSpec(
        name="spin_wrist",
        kind=PrimitiveKind.MOTION,
        capability_family=CapabilityFamily.JOINT_MOTION,
        description="Spin the wrist roll joint by a relative angle.",
        parameters=(
            ParameterSpec(
                "delta_deg",
                "float",
                "Relative wrist rotation in degrees.",
                True,
                ValueUnit.DEGREE,
                "wrist_roll_joint",
            ),
        ),
        tolerance=ToleranceSpec(absolute=2.0),
        completion=CompletionSpec(
            semantics=CompletionSemantics.GOAL_REACHED,
            timeout_s=2.0,
        ),
        backed_by=("primitive_action:spin_left_or_right",),
    ),
    PrimitiveSpec(
        name="gripper_open",
        kind=PrimitiveKind.END_EFFECTOR,
        capability_family=CapabilityFamily.END_EFFECTOR,
        description="Open the gripper.",
        completion=CompletionSpec(
            semantics=CompletionSemantics.GOAL_REACHED,
            timeout_s=2.0,
        ),
        backed_by=("primitive_action:gripper_open",),
    ),
    PrimitiveSpec(
        name="gripper_close",
        kind=PrimitiveKind.END_EFFECTOR,
        capability_family=CapabilityFamily.END_EFFECTOR,
        description="Close the gripper.",
        completion=CompletionSpec(
            semantics=CompletionSemantics.GOAL_REACHED,
            timeout_s=2.0,
        ),
        backed_by=("primitive_action:gripper_close",),
    ),
    PrimitiveSpec(
        name="save_named_pose",
        kind=PrimitiveKind.POSE,
        capability_family=CapabilityFamily.NAMED_POSE,
        description="Save the current pose under a stable name.",
        parameters=(
            ParameterSpec("name", "str", "Named pose identifier.", True),
        ),
        completion=CompletionSpec(
            semantics=CompletionSemantics.COMMAND_ACCEPTED,
        ),
        backed_by=("save_named_pose",),
    ),
    PrimitiveSpec(
        name="go_named_pose",
        kind=PrimitiveKind.POSE,
        capability_family=CapabilityFamily.NAMED_POSE,
        description="Move to a named pose such as home, ready, rest, or work.",
        parameters=(
            ParameterSpec("name", "str", "Named pose identifier.", True),
        ),
        completion=CompletionSpec(
            semantics=CompletionSemantics.GOAL_REACHED,
            timeout_s=5.0,
        ),
        backed_by=("move_to_named_pose",),
    ),
    PrimitiveSpec(
        name="scan_panorama",
        kind=PrimitiveKind.PERCEPTION,
        capability_family=CapabilityFamily.CAMERA,
        description="Run a shoulder-pan scan using an attached wrist camera.",
        parameters=(
            ParameterSpec("focus", "str", "What the scan should focus on."),
        ),
        completion=CompletionSpec(
            semantics=CompletionSemantics.EVENT_CONFIRMED,
            timeout_s=10.0,
        ),
        backed_by=("look_around_scan",),
    ),
    PrimitiveSpec(
        name="release_torque",
        kind=PrimitiveKind.MAINTENANCE,
        capability_family=CapabilityFamily.TORQUE_CONTROL,
        description="Release torque on the arm while keeping the session alive.",
        completion=CompletionSpec(
            semantics=CompletionSemantics.COMMAND_ACCEPTED,
        ),
        backed_by=("primitive_action:release_torque",),
    ),
    PrimitiveSpec(
        name="lock_torque",
        kind=PrimitiveKind.MAINTENANCE,
        capability_family=CapabilityFamily.TORQUE_CONTROL,
        description="Re-enable torque and hold the current pose.",
        completion=CompletionSpec(
            semantics=CompletionSemantics.COMMAND_ACCEPTED,
        ),
        backed_by=("primitive_action:lock_torque",),
    ),
)

SO101_OBSERVATION_SCHEMA = ObservationSchema(
    id="so101_observation_v1",
    fields=(
        ObservationFieldSpec(
            name="joint_positions",
            value_type="dict[str,float]",
            description="Joint positions for all controllable joints.",
            unit=ValueUnit.RADIAN,
            frame="joint_space",
        ),
        ObservationFieldSpec(
            name="joint_velocities",
            value_type="dict[str,float]",
            description="Joint velocity estimate for all controllable joints.",
            unit=ValueUnit.RADIAN_PER_SECOND,
            frame="joint_space",
        ),
        ObservationFieldSpec(
            name="ee_position",
            value_type="dict[str,float]",
            description="End-effector Cartesian position in base frame.",
            unit=ValueUnit.METER,
            frame="base_link",
        ),
        ObservationFieldSpec(
            name="ee_orientation_rpy",
            value_type="dict[str,float]",
            description="End-effector orientation in roll/pitch/yaw.",
            unit=ValueUnit.RADIAN,
            frame="base_link",
        ),
        ObservationFieldSpec(
            name="gripper_open_ratio",
            value_type="float",
            description="Normalized gripper opening ratio.",
            unit=ValueUnit.PERCENT,
            frame="gripper",
        ),
    ),
    frequency_hz=30.0,
    notes=(
        "Observation schema is transport-independent and consumed by semantic skills.",
    ),
)

SO101_HEALTH_SCHEMA = HealthSchema(
    id="so101_health_v1",
    fields=(
        HealthFieldSpec(
            name="level",
            value_type="str",
            description="Normalized health level.",
        ),
        HealthFieldSpec(
            name="connection_state",
            value_type="str",
            description="Primary control connection state.",
        ),
        HealthFieldSpec(
            name="fault_code",
            value_type="str",
            description="Vendor or adapter fault code.",
        ),
        HealthFieldSpec(
            name="estop_latched",
            value_type="bool",
            description="Emergency stop latch state.",
        ),
    ),
    severity_levels=(
        HealthLevel.OK,
        HealthLevel.WARN,
        HealthLevel.ERROR,
        HealthLevel.STALE,
    ),
    notes=(
        "Health schema remains reusable across real and simulated execution targets.",
    ),
)

SO101_ROBOT = RobotManifest(
    id="so101",
    name="SO101",
    description="Standard SO101 single-arm robot definition independent from carriers and sensors.",
    robot_type=RobotType.ARM,
    capability_families=(
        CapabilityFamily.LIFECYCLE,
        CapabilityFamily.JOINT_MOTION,
        CapabilityFamily.CARTESIAN_MOTION,
        CapabilityFamily.END_EFFECTOR,
        CapabilityFamily.CAMERA,
        CapabilityFamily.CALIBRATION,
        CapabilityFamily.DIAGNOSTICS,
        CapabilityFamily.RECOVERY,
        CapabilityFamily.NAMED_POSE,
        CapabilityFamily.TORQUE_CONTROL,
    ),
    primitives=SO101_PRIMITIVES,
    observation_schema=SO101_OBSERVATION_SCHEMA,
    health_schema=SO101_HEALTH_SCHEMA,
    default_named_poses=("home", "ready", "rest", "work"),
    suggested_sensor_ids=("rgb_camera",),
    safety=SafetyProfile(
        emergency_stop_required=True,
        supports_soft_stop=True,
        default_reset_mode="home",
        notes=(
            "Visual servo flows should stay above the robot manifest and consume normalized primitives.",
        ),
    ),
    notes=(
        "SO101 only defines robot-local motion and maintenance capabilities here.",
        "Sensors and carrier targets are composed separately through assemblies.",
    ),
)
