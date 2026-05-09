FROM ros:humble-ros-base

# Add non-root user
RUN useradd -ms /bin/bash ubuntu
USER ubuntu

# Copy astra_descriptions package to the workspace
RUN mkdir -p /home/ubuntu/ros2_ws/src/astra_descriptions/
COPY --chown=ubuntu:ubuntu .. /home/ubuntu/ros2_ws/src/astra_descriptions/

# Install dependencies
USER ubuntu
RUN rosdep update
USER root
RUN apt-get update && \
    rosdep install --from-paths /home/ubuntu/ros2_ws/src --ignore-src -y

# Build the workspace
USER ubuntu
WORKDIR /home/ubuntu/ros2_ws
RUN bash -c "source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install"

# Nuke the copied package so it can be volume mounted on run
RUN rm -rf /home/ubuntu/ros2_ws/src/astra_descriptions

ENTRYPOINT [ "bash" ]
