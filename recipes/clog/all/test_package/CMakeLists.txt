cmake_minimum_required(VERSION 2.8.12)
project(test_package C)

set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})

find_package(clog REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE clog::clog)
