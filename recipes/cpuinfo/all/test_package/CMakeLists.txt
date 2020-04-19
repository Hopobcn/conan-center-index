cmake_minimum_required(VERSION 2.8.12)
project(test_package CXX)

set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})

find_package(cpuinfo REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cpuinfo::cpuinfo)
