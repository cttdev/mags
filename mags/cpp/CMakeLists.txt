cmake_minimum_required(VERSION 3.18.2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

project(mags VERSION 0.0.1)

# Look for python
set(Python_ROOT_DIR "../../venv/bin")
find_package(Python COMPONENTS Interpreter Development)

# Look for pybind-11
set(pybind11_DIR "../../venv/share/cmake/pybind11")
find_package(pybind11 CONFIG)

# Look for Eigen
find_package(Eigen3 3.3 REQUIRED NO_MODULE)

# # Add files to pybind 11 module
# set(SOURCES src/main.cpp)
# pybind11_add_module(mags ${SOURCES})
# target_include_directories(mags PRIVATE include)

# Link external dependancies
# target_link_libraries(mags PUBLIC Eigen3::Eigen)

# install(
#   TARGETS 
#   mags 
#   DESTINATION ${PROJECT_SOURCE_DIR}
# )

add_executable(mags src/main.cpp)
target_compile_features(mags PUBLIC cxx_std_17)
target_link_libraries(mags PUBLIC Eigen3::Eigen)
target_include_directories(mags PRIVATE include)
