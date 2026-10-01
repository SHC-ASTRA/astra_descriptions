cmake_minimum_required(VERSION 3.14)
project(astra_descriptions)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Required for metapackage to install properly
find_package(ament_cmake REQUIRED)
ament_package()
