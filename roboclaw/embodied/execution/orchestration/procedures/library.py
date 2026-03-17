"""Built-in first-landscape procedures."""

from __future__ import annotations

from roboclaw.embodied.execution.orchestration.procedures.model import ProcedureDefinition, ProcedureKind, ProcedureStep
from roboclaw.embodied.definition.foundation.schema import CapabilityFamily

CONNECT_PROCEDURE = ProcedureDefinition(
    id="connect_default",
    kind=ProcedureKind.CONNECT,
    description="Probe environment, select target, connect adapter, and verify ready state.",
    required_capabilities=(CapabilityFamily.LIFECYCLE,),
    steps=(
        ProcedureStep("probe_env", "probe_env", "Probe the environment and available transport."),
        ProcedureStep("select_target", "resolve_target", "Resolve the desired execution target."),
        ProcedureStep("connect", "connect", "Connect the adapter to the target."),
        ProcedureStep("verify_state", "get_state", "Verify the runtime is ready."),
    ),
)

CALIBRATE_PROCEDURE = ProcedureDefinition(
    id="calibrate_default",
    kind=ProcedureKind.CALIBRATE,
    description="List calibration targets, launch calibration, and track task progress.",
    required_capabilities=(CapabilityFamily.CALIBRATION,),
    steps=(
        ProcedureStep("list_targets", "list_calibration_targets", "List calibration targets."),
        ProcedureStep("start", "start_calibration", "Start calibration for the selected targets."),
        ProcedureStep("track", "track_calibration", "Track calibration progress until completion."),
    ),
)

MOVE_PROCEDURE = ProcedureDefinition(
    id="move_default",
    kind=ProcedureKind.MOVE,
    description="Resolve a normalized primitive and execute it safely.",
    required_capabilities=(CapabilityFamily.JOINT_MOTION,),
    steps=(
        ProcedureStep("read_state", "get_state", "Read current state before moving."),
        ProcedureStep("resolve_primitive", "resolve_primitive", "Resolve the normalized primitive."),
        ProcedureStep("execute", "execute_primitive", "Execute the primitive through the adapter."),
    ),
)

DEBUG_PROCEDURE = ProcedureDefinition(
    id="debug_default",
    kind=ProcedureKind.DEBUG,
    description="Collect environment probe, state, sensor snapshots, and debug bundle.",
    required_capabilities=(CapabilityFamily.DIAGNOSTICS,),
    steps=(
        ProcedureStep("probe_env", "probe_env", "Probe environment health."),
        ProcedureStep("state", "get_state", "Read normalized state."),
        ProcedureStep("sensor", "capture_sensor", "Capture a primary sensor snapshot if available."),
        ProcedureStep("bundle", "debug_snapshot", "Collect the debug bundle."),
    ),
)

RESET_PROCEDURE = ProcedureDefinition(
    id="reset_default",
    kind=ProcedureKind.RESET,
    description="Stop active work, recover if needed, and reset to the default safe pose.",
    required_capabilities=(CapabilityFamily.RECOVERY,),
    steps=(
        ProcedureStep("stop", "stop", "Stop active motion or tasks."),
        ProcedureStep("recover", "recover", "Run recovery if the system is in a bad state."),
        ProcedureStep("reset", "reset", "Reset to the default safe pose or mode."),
    ),
)

DEFAULT_PROCEDURES = (
    CONNECT_PROCEDURE,
    CALIBRATE_PROCEDURE,
    MOVE_PROCEDURE,
    DEBUG_PROCEDURE,
    RESET_PROCEDURE,
)
