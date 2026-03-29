cmake_minimum_required(VERSION 3.16)

project(clockwerk LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(clockwerk_core
    src/decision/state_machine.cpp
)

target_include_directories(clockwerk_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

add_executable(test_state_machine
    tests/cpp/test_state_machine.cpp
)

target_link_libraries(test_state_machine
    PRIVATE
        clockwerk_core
)

include(CTest)

if(BUILD_TESTING)
    add_test(NAME test_state_machine COMMAND test_state_machine)
endif()
