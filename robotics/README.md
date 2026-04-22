# RoboClaw Robotics Setup

This guide explains how to set up the TurtleBot3 simulation environment used by this repository on `ROS 2 Humble`.

It is based on the official TurtleBot3 Humble simulation, SLAM, and navigation workflow, but uses this repository layout instead of a workspace under `~/`.

Official references:

- TurtleBot3 Quick Start: https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/
- TurtleBot3 Simulation: https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/
- TurtleBot3 SLAM: https://emanual.robotis.com/docs/en/platform/turtlebot3/slam/
- TurtleBot3 Navigation: https://emanual.robotis.com/docs/en/platform/turtlebot3/navigation/

## Workspace Layout

This repository uses the following ROS workspace:

```text
robotics/ros_ws/
```

ROS packages should be placed under:

```text
robotics/ros_ws/src/
```

In the commands below, assume:

```bash
export REPO_ROOT=/path/to/RoboClaw_Nav
```

## Step 1: Install System Dependencies

Install the main Humble packages used by the official TurtleBot3 simulation workflow:

```bash
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-humble-gazebo-* \
  ros-humble-cartographer \
  ros-humble-cartographer-ros \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup
```

If `rosdep` has not been initialized on this machine yet:

```bash
sudo rosdep init
rosdep update
```

## Step 2: Prepare the ROS Workspace

From the repository root:

```bash
mkdir -p robotics/ros_ws/src
```

Clone the TurtleBot3 source packages into `robotics/ros_ws/src/`:

```bash
cd "$REPO_ROOT/robotics/ros_ws/src"
git clone -b humble https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git
```

## Step 3: Install ROS Package Dependencies

Run `rosdep` from the workspace root:

```bash
cd "$REPO_ROOT/robotics/ros_ws"
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

## Step 4: Build the Workspace

```bash
cd "$REPO_ROOT/robotics/ros_ws"
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

## Step 5: Source the Environment

Every terminal used for simulation, SLAM, or navigation should source ROS and this workspace:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
```

If you use another TurtleBot3 model, replace `burger` with the correct value.

## Step 6: Run Gazebo Simulation

Start Gazebo in a terminal:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

You can also use another world from the official package:

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

## Step 7: Teleoperate the Robot

Open a new terminal and run:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

Use this step to confirm that the simulated robot moves correctly.

## Step 8: Run SLAM

Keep Gazebo running.

Open a new terminal and start SLAM:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

Open another terminal and run teleoperation if needed:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

Drive the robot until the map is complete.

## Step 9: Save the Map

When the map is ready, save it into a project-controlled ROS asset path instead of the home directory.

Recommended target layout:

```text
$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps/
```

Example:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
mkdir -p "$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps"
ros2 run nav2_map_server map_saver_cli -f "$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps/map"
```

This creates:

- `map.yaml`
- `map.pgm`

## Step 10: Run Navigation

Keep Gazebo running.

Open a new terminal and launch navigation with the saved map:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  map:="$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps/default.yaml"
```

## Step 11: Verify the Setup

The setup should be considered working only if all of the following are true:

- Gazebo launches successfully
- the TurtleBot3 model appears in the simulator
- keyboard teleoperation works
- `/scan` is publishing
- `/odom` is publishing
- `/tf` is publishing
- SLAM launches successfully
- map saving works
- navigation launches successfully
- a simple goal can be sent in RViz and completed

## Useful Topic Checks

Use these commands if you need quick verification:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
ros2 topic list
ros2 topic echo /scan
ros2 topic echo /odom
```

## Troubleshooting

Check these first if something does not work:

- `/opt/ros/humble/setup.bash` was not sourced
- `robotics/ros_ws/install/setup.bash` was not sourced
- `TURTLEBOT3_MODEL` was not set
- required packages were not installed
- `rosdep install` was skipped
- the workspace was not rebuilt after source changes
- the wrong map path was passed to navigation

## Notes

- The official TurtleBot3 documentation often assumes a workspace under the home directory. This repository uses `robotics/ros_ws/` instead.
- This README is intentionally focused on the manual setup flow. Agent automation can be added later after the ROS environment is stable and reproducible.
