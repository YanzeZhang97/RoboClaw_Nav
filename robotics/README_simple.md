# RoboClaw Robotics Quick Setup

This guide assumes that all required ROS packages are already included under:

```text
robotics/ros_ws/src/
```

That means users do not need to clone TurtleBot3 repositories manually. They only need to:

1. install system dependencies
2. install ROS package dependencies
3. build the workspace
4. source the workspace
5. run simulation, SLAM, or navigation

## Assumptions

This quick setup currently assumes:

- Ubuntu 22.04
- ROS 2 Humble
- TurtleBot3 simulation
- all required source packages are already present under `robotics/ros_ws/src/`

In the commands below, assume:

```bash
export REPO_ROOT=/path/to/RoboClaw_Nav
```

## Step 1: Install System Dependencies

Install the main Humble packages used by the TurtleBot3 simulation workflow:

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

## Step 2: Install ROS Package Dependencies

```bash
cd "$REPO_ROOT/robotics/ros_ws"
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

## Step 3: Build the Workspace

```bash
cd "$REPO_ROOT/robotics/ros_ws"
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

## Step 4: Source the Workspace

Every terminal used for simulation, SLAM, or navigation should run:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
```

Replace `burger` if you are using another TurtleBot3 model.

## Step 5: Run Simulation

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

Optional official worlds:

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

## Step 6: Run Teleoperation

Open a new terminal:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

## Step 7: Run SLAM

Keep Gazebo running. Open a new terminal:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

If needed, open another terminal for teleoperation:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

## Step 8: Save a Map

Save the map into the project-owned ROS asset package:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
mkdir -p "$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps"
ros2 run nav2_map_server map_saver_cli -f "$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps/default"
```

This creates:

- `default.yaml`
- `default.pgm`

## Step 9: Run Navigation

Keep Gazebo running. Open a new terminal:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  map:="$REPO_ROOT/robotics/ros_ws/src/roboclaw_tb3_sim/maps/default.yaml"
```

## Verification

The setup should be considered working only if:

- Gazebo launches successfully
- teleoperation works
- SLAM launches successfully
- map saving works
- navigation launches successfully
- a simple navigation goal can be sent and completed

Useful checks:

```bash
source /opt/ros/humble/setup.bash
source "$REPO_ROOT/robotics/ros_ws/install/setup.bash"
ros2 topic list
ros2 topic echo /scan
ros2 topic echo /odom
```

## Troubleshooting

Check these first:

- `/opt/ros/humble/setup.bash` was not sourced
- `"$REPO_ROOT/robotics/ros_ws/install/setup.bash"` was not sourced
- `TURTLEBOT3_MODEL` was not set
- `rosdep install` was skipped
- the workspace was not rebuilt after source changes
- the map path passed to navigation is wrong
