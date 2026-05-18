#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

if [ -z "$(docker images -q astra/gazebo:latest 2>/dev/null)" ]; then
  echo "Docker image 'astra/gazebo' not found. Building the image..."
  $SCRIPT_DIR/build_container.sh
fi

echo "Running the Gazebo container."
echo "astra_descriptions will be volume mounted to /home/ubuntu/ros2_ws/src/astra_descriptions."
echo "Try running: source install/setup.bash && ros2 launch core_gazebo core.gazebo.launch.py"

if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
  echo "Using Wayland for display."
  SESSION_VARS="-e XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR -e WAYLAND_DISPLAY=$WAYLAND_DISPLAY -v $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY:$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY"
else
  echo "Using X11 for display."
  SESSION_VARS="-e DISPLAY -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix"
fi

docker run -it --rm \
  --net=host \
  --env="FASTDDS_BUILTIN_TRANSPORTS=UDPv4" \
  --volume="$SCRIPT_DIR/..:/home/ubuntu/ros2_ws/src/astra_descriptions:rw" \
  $SESSION_VARS \
  astra/gazebo:latest
