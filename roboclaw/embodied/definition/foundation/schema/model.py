"""Shared schema types used across embodied robots, sensors, carriers, and transports."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - Python < 3.11 fallback for local tooling.
    class StrEnum(str, Enum):
        """Fallback for Python versions without enum.StrEnum."""


class RobotType(StrEnum):
    """High-level robot category."""

    ARM = "arm"
    HUMANOID = "humanoid"
    MOBILE_BASE = "mobile_base"
    HAND = "hand"
    DUAL_ARM = "dual_arm"
    OTHER = "other"


class SensorKind(StrEnum):
    """Sensor family."""

    CAMERA = "camera"
    DEPTH_CAMERA = "depth_camera"
    JOINT_STATE = "joint_state"
    FORCE_TORQUE = "force_torque"
    IMU = "imu"
    LIDAR = "lidar"
    OTHER = "other"


class CarrierKind(StrEnum):
    """Execution carrier family."""

    REAL = "real"
    SIM = "sim"


class SimulatorKind(StrEnum):
    """Simulation backend kind."""

    NONE = "none"
    PYBULLET = "pybullet"
    GAZEBO = "gazebo"
    ISAAC_SIM = "isaac_sim"
    MUJOCO = "mujoco"
    CUSTOM = "custom"


class TransportKind(StrEnum):
    """Transport boundary between RoboClaw and the execution target."""

    ROS2 = "ros2"


class CapabilityFamily(StrEnum):
    """Reusable capability families consumed by semantic skills."""

    LIFECYCLE = "lifecycle"
    JOINT_MOTION = "joint_motion"
    CARTESIAN_MOTION = "cartesian_motion"
    BASE_MOTION = "base_motion"
    HEAD_MOTION = "head_motion"
    END_EFFECTOR = "end_effector"
    CAMERA = "camera"
    CALIBRATION = "calibration"
    DIAGNOSTICS = "diagnostics"
    RECOVERY = "recovery"
    NAMED_POSE = "named_pose"
    TORQUE_CONTROL = "torque_control"


class PrimitiveKind(StrEnum):
    """Primitive intent category."""

    MOTION = "motion"
    END_EFFECTOR = "end_effector"
    POSE = "pose"
    PERCEPTION = "perception"
    MAINTENANCE = "maintenance"


@dataclass(frozen=True)
class ParameterSpec:
    """One primitive parameter."""

    name: str
    value_type: str
    description: str
    required: bool = False


@dataclass(frozen=True)
class SafetyProfile:
    """Default safety policy for a robot or assembly."""

    emergency_stop_required: bool = True
    supports_soft_stop: bool = True
    default_reset_mode: str = "home"
    notes: tuple[str, ...] = field(default_factory=tuple)
