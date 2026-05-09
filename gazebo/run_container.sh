#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

if [ -z "$(docker images -q astra/gazebo:latest 2>/dev/null)" ]; then
  echo "Docker image 'astra/gazebo' not found. Building the image..."
  $SCRIPT_DIR/build_container.sh
fi

echo "Running the Gazebo container."
echo "astra_descriptions will be volume mounted to /home/ubuntu/ros2_ws/src/astra_descriptions."
echo "Try running: source install/setup.bash && ros2 launch core_gazebo core.gazebo.launch.py"

docker run -it --rm \
  --net=host \
  --env="DISPLAY" \
  --env="QT_X11_NO_MITSHM=1" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --volume="$SCRIPT_DIR/..:/home/ubuntu/ros2_ws/src/astra_descriptions:rw" \
  astra/gazebo:latest
