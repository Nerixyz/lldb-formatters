cmake_minimum_required(VERSION 3.16)

project(lldb-formatters)

set(CMAKE_CXX_STANDARD 20)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")

add_subdirectory(qt6)
add_subdirectory(sol2-lua)
