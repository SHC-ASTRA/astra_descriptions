FROM ros:humble-ros-base

# Add non-root user
RUN useradd -ms /bin/bash ubuntu

USER ubuntu
RUN rosdep update

# Copy only package.xml files first to cache dependency installation
COPY --chown=ubuntu:ubuntu ../arm_description/package.xml /home/ubuntu/ros2_ws/src/astra_descriptions/arm_description/package.xml
COPY --chown=ubuntu:ubuntu ../arm_moveit_config/package.xml /home/ubuntu/ros2_ws/src/astra_descriptions/arm_moveit_config/package.xml
COPY --chown=ubuntu:ubuntu ../core_description/package.xml /home/ubuntu/ros2_ws/src/astra_descriptions/core_description/package.xml
COPY --chown=ubuntu:ubuntu ../core_gazebo/package.xml /home/ubuntu/ros2_ws/src/astra_descriptions/core_gazebo/package.xml

# Install dependencies
USER root
RUN apt-get update && \
    rosdep install --from-paths /home/ubuntu/ros2_ws/src --ignore-src -y

# Copy full source for build
COPY --chown=ubuntu:ubuntu .. /home/ubuntu/ros2_ws/src/astra_descriptions/

# Build the workspace
USER ubuntu
WORKDIR /home/ubuntu/ros2_ws
RUN bash -c "source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install"

ENTRYPOINT [ "bash" ]
