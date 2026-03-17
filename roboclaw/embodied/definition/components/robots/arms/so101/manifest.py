"""SO101 robot definition."""

from __future__ import annotations

from roboclaw.embodied.definition.components.robots.model import PrimitiveSpec, RobotManifest
from roboclaw.embodied.definition.foundation.schema import (
    CapabilityFamily,
    ParameterSpec,
    PrimitiveKind,
    RobotType,
    SafetyProfile,
)

SO101_PRIMITIVES = (
    PrimitiveSpec(
        name="move_joint",
        kind=PrimitiveKind.MOTION,
        capability_family=CapabilityFamily.JOINT_MOTION,
        description="Move one or more joints to target positions.",
        parameters=(
            ParameterSpec("positions", "dict[str,float]", "Joint name to target value map.", True),
        ),
        backed_by=("send_action",),
    ),
    PrimitiveSpec(
        name="move_cartesian_delta",
        kind=PrimitiveKind.MOTION,
        capability_family=CapabilityFamily.CARTESIAN_MOTION,
        description="Move the end effector by a small Cartesian delta in the base frame.",
        parameters=(
            ParameterSpec("dx", "float", "Delta x in meters."),
            ParameterSpec("dy", "float", "Delta y in meters."),
            ParameterSpec("dz", "float", "Delta z in meters."),
        ),
        backed_by=("move_ee_delta",),
    ),
    PrimitiveSpec(
        name="spin_wrist",
        kind=PrimitiveKind.MOTION,
        capability_family=CapabilityFamily.JOINT_MOTION,
        description="Spin the wrist roll joint by a relative angle.",
        parameters=(
            ParameterSpec("delta_deg", "float", "Relative wrist rotation in degrees.", True),
        ),
        backed_by=("primitive_action:spin_left_or_right",),
    ),
    PrimitiveSpec(
        name="gripper_open",
        kind=PrimitiveKind.END_EFFECTOR,
        capability_family=CapabilityFamily.END_EFFECTOR,
        description="Open the gripper.",
        backed_by=("primitive_action:gripper_open",),
    ),
    PrimitiveSpec(
        name="gripper_close",
        kind=PrimitiveKind.END_EFFECTOR,
        capability_family=CapabilityFamily.END_EFFECTOR,
        description="Close the gripper.",
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
        backed_by=("look_around_scan",),
    ),
    PrimitiveSpec(
        name="release_torque",
        kind=PrimitiveKind.MAINTENANCE,
        capability_family=CapabilityFamily.TORQUE_CONTROL,
        description="Release torque on the arm while keeping the session alive.",
        backed_by=("primitive_action:release_torque",),
    ),
    PrimitiveSpec(
        name="lock_torque",
        kind=PrimitiveKind.MAINTENANCE,
        capability_family=CapabilityFamily.TORQUE_CONTROL,
        description="Re-enable torque and hold the current pose.",
        backed_by=("primitive_action:lock_torque",),
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
