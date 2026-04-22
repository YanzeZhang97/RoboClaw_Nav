# RoboClaw Robotics Workspace

## Overview

This directory contains ROS-related assets for RoboClaw.

At the current stage, the robotics workflow is centered on:

- ROS 2 Humble
- TurtleBot3 simulation
- SLAM validation
- Navigation validation

The immediate goal is to keep the ROS workflow reproducible for developers before integrating it into RoboClaw's Agent tools.

## Scope

This document is the broader robotics workspace overview.

It covers:

- system assumptions
- workspace layout
- ROS workspace build steps
- environment setup
- simulation / SLAM / navigation run flow
- minimal verification checklist
- future integration direction

It does not yet cover:

- hardware bringup details
- robot-specific custom packages beyond the current TurtleBot3 baseline
- finalized Agent automation

## References

- TurtleBot3 Simulation: https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/
- TurtleBot3 Quick Start: https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/

## Verified Baseline

The current baseline assumed by this workspace is:

- OS: Ubuntu 22.04
- ROS distribution: ROS 2 Humble
- Robot platform: TurtleBot3
- Simulator: Gazebo

Update this section when the project validates additional environments.

## Directory Layout

```text
robotics/
  README.md
  README.general.md
  deps/
  ros_ws/
    src/
  scripts/
```

Conventions:

- `robotics/ros_ws/` is the ROS 2 workspace root used by this project.
- `robotics/ros_ws/src/` is where ROS packages should live.
- `robotics/scripts/` is reserved for controlled install, build, and run entrypoints.
- `robotics/deps/` is reserved for dependency manifests such as `apt.txt` or `rosdep` files.

In command examples below, assume:

```bash
export REPO_ROOT=/path/to/RoboClaw_Nav
```

Do not commit ROS build artifacts such as:

- `build/`
- `install/`
- `log/`

## Current Workspace Policy

At this stage, the TurtleBot3 simulation flow follows the official TurtleBot3 documentation.

That means:

- the simulation stack is currently based on official TurtleBot3 packages
- this repository does not yet provide a custom TurtleBot3 ROS package
- the main near-term task is to document and stabilize the reproducible workflow

If future work requires custom simulation or bringup logic, project-specific ROS packages can be added under:

```text
robotics/ros_ws/src/
```

Examples:

- `roboclaw_tb3_sim`
- `roboclaw_tb3_bringup`
- `roboclaw_nav_common`

## Prerequisites

Before using this workspace, make sure the following are available:

- ROS 2 Humble
- `colcon`
- `rosdep`
- Gazebo required by the TurtleBot3 Humble simulation flow
- Cartographer
- Navigation2
- TurtleBot3-related packages and dependencies required by the official workflow

This repository may later provide helper scripts under `robotics/scripts/`, but this first version assumes the environment is prepared manually.

## Workspace Setup

Create the workspace layout if needed:

```bash
mkdir -p robotics/ros_ws/src
```

Then place the required ROS packages under:

```text
robotics/ros_ws/src/
```

At the current stage, if you are following the official TurtleBot3 workflow, use the official TurtleBot3 packages and dependencies required by the Humble setup.

## Install Dependencies

Use the official TurtleBot3 and ROS 2 Humble setup instructions as the source of truth for system dependencies.

In practice, this usually includes:

- TurtleBot3-related packages
- Gazebo dependencies
- Cartographer packages
- Navigation2 packages

If you are using a source-based workspace, install unresolved dependencies with:

```bash
cd "$REPO_ROOT/robotics/ros_ws"
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

## Build

Build the ROS workspace with:

```bash
cd "$REPO_ROOT/robotics/ros_ws"
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

After a successful build:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
```

## Environment Setup

At minimum, set the TurtleBot3 model before launching simulation-related commands:

```bash
export TURTLEBOT3_MODEL=burger
```

If you are using another model, replace `burger` with the correct value.

A typical shell session looks like:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
```

## Run Simulation

Run the simulation with the official TurtleBot3 Humble launch flow you have already validated.

Record the exact command used by the project here once finalized.

Example placeholder:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
# ros2 launch ...
```

## Run SLAM

Run SLAM with the official TurtleBot3 Humble flow you have already validated.

Record the exact command used by the project here once finalized.

Example placeholder:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
# ros2 launch ...
```

## Run Navigation

Run navigation with the official TurtleBot3 Humble flow you have already validated.

Record the exact command used by the project here once finalized.

Example placeholder:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
# ros2 launch ...
```

For project-managed workflows, maps should be stored as ROS assets inside the repository rather than under the user's home directory.

Recommended pattern:

```text
$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps/
```

This keeps simulation assets versionable, shareable, and easier to reference later from controlled scripts or Agent tools.

## Minimal Verification Checklist

The workspace should be considered minimally ready only if all of the following are true:

- simulation starts successfully
- the robot model appears correctly in Gazebo
- `/scan` is publishing
- `/odom` is publishing
- `/tf` is publishing
- SLAM can start successfully
- navigation can start successfully
- a simple navigation goal can be sent and completed

## Differences From The Official TurtleBot3 Docs

The official TurtleBot3 documentation often assumes a workspace created directly under the home directory.

This project standardizes on:

```text
robotics/ros_ws/
```

This means the project may differ from the official examples in:

- workspace path
- source path
- helper scripts
- future Agent integration

The validated commands should therefore be adapted to this repository layout and documented here.

## Agent Integration Notes

Agent integration is not the focus of this first version, but the intended direction is:

- `doctor` should check whether the ROS environment is ready
- `bringup` should use controlled project entrypoints instead of ad hoc shell commands
- the Agent should eventually know which setup file to source
- the Agent should not assume the official home-directory layout
- dependency installation should ideally be executed through controlled scripts that the Agent can call after explicit confirmation

For now, the priority is to make the human-operated workflow reproducible.

## Troubleshooting

Common issues to check first:

- `/opt/ros/humble/setup.bash` was not sourced
- `robotics/ros_ws/install/setup.bash` was not sourced
- `TURTLEBOT3_MODEL` was not set
- required packages were not installed
- the workspace was not rebuilt after source changes
- the wrong terminal session was used for launch commands

## Next Step

After the manual workflow is stable, the next steps are:

- add dependency manifests under `robotics/deps/`
- add controlled helper scripts under `robotics/scripts/`
- formalize the exact run commands used by this project
- implement discovery / doctor tooling in RoboClaw
- connect the ROS workflow to `embodied_simulation` and `embodied_navigation`
