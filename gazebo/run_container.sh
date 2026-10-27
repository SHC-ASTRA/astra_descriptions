#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

if [ -z "$(docker images -q astra/gazebo:latest 2>/dev/null)" ]; then
  echo "Docker image 'astra/gazebo' not found. Building the image..."
  $SCRIPT_DIR/build_container.sh
fi

# GPU passthrough: makes Gazebo run way faster, and fixes the fisheye camera.
gpu_args=()
if [ -d /dev/dri ]; then
  gpu_args+=(--device=/dev/dri)
  for grp in render video; do
    gid=$(getent group "$grp" | cut -d: -f3)
    if [ -n "$gid" ]; then gpu_args+=(--group-add="$gid"); fi
  done
else
  echo "Warning: no /dev/dri on the host - Gazebo and RViz will use software rendering."
fi

echo "Running the Gazebo container."
echo "astra_descriptions will be volume mounted to /home/ubuntu/ros2_ws/src/astra_descriptions."
echo "Try running: source install/setup.bash && ros2 launch core_gazebo core.gazebo.launch.py"

docker run -it --rm \
  --net=host \
  --env="DISPLAY" \
  --env="QT_X11_NO_MITSHM=1" \
  --env="FASTDDS_BUILTIN_TRANSPORTS=UDPv4" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --volume="$SCRIPT_DIR/..:/home/ubuntu/ros2_ws/src/astra_descriptions:rw" \
  "${gpu_args[@]}" \
  "$@" astra/gazebo:latest
