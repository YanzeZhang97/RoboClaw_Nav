# Docker Installation

This guide is the Docker installation path.

If you want the non-Docker path instead, use [Installation](./INSTALLATION.md).

For most users, you only need one Docker image.
The recommended default is:

- `ubuntu2404-ros2`: Ubuntu 24.04 + Python 3.11 + ROS2 Jazzy

An alternative image is also available if you specifically want Ubuntu 22.04:

- `ubuntu2204-ros2`: Ubuntu 22.04 + Python 3.11 + ROS2 Humble

All container state lives under `~/.roboclaw-docker/instances/<instance>--<profile>/`.
Each profile instance has its own `config.json`, `workspace/`, and runtime data derived from the config directory.
By default, bootstrap copies `~/.roboclaw/config.json` into the instance once, then the container state diverges from the host.

## Recommended Quick Start

Build the default Docker image:

```bash
./scripts/docker/build-image.sh --profile ubuntu2404-ros2 devbox
```

The build only runs when the Git worktree is clean. Image tags include the
instance name and the current short commit hash, for example
`roboclaw:devbox-ubuntu2404-ros2-10c41db`.

Create or refresh the isolated instance state:

```bash
./scripts/docker/bootstrap-instance.sh --profile ubuntu2404-ros2 devbox
```

Start a long-lived container and enter it:

```bash
./scripts/docker/start-dev.sh --profile ubuntu2404-ros2 devbox
./scripts/docker/exec-dev.sh --profile ubuntu2404-ros2 devbox
```

Run a one-shot RoboClaw task:

```bash
./scripts/docker/run-task.sh --profile ubuntu2404-ros2 devbox status
./scripts/docker/run-task.sh --profile ubuntu2404-ros2 devbox onboard
./scripts/docker/run-task.sh --profile ubuntu2404-ros2 devbox agent -m hello --no-markdown
```

## Choosing the Image

- Use `ubuntu2404-ros2` unless you have a specific reason to stay on Ubuntu 22.04.
- If you want the 22.04 image, replace `ubuntu2404-ros2` with `ubuntu2204-ros2` in the commands above.

## Networking and proxies

The scripts discover a local proxy port on the remote host and export proxy variables automatically when possible.

- Docker builds always use `--network=host`.
- Runtime containers always use host networking.
- This is required when the remote host exposes its VPN or proxy on `127.0.0.1`.
- When the remote host has `~/.codex/auth.json`, the dev and task workflows mount it read-only into the container so `roboclaw agent` can reuse host authentication without copying credentials into the isolated instance state.
