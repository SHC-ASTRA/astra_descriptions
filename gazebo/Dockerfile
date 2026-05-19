FROM ros:humble-ros-base

# Add non-root user
RUN useradd -ms /bin/bash ubuntu

# Copy only package.xml files first to cache dependency installation
COPY --chown=ubuntu:ubuntu --parents ../**/package.xml /home/ubuntu/ros2_ws/src/astra_descriptions/

# Install dependencies
USER ubuntu
RUN rosdep update
USER root
RUN apt-get update && \
    rosdep install --from-paths /home/ubuntu/ros2_ws/src --ignore-src -y

# Build the workspace
USER ubuntu
WORKDIR /home/ubuntu/ros2_ws
RUN --mount=type=bind,source=.,target=src/astra_descriptions \
    bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

ENTRYPOINT [ "bash" ]
