cmake_minimum_required(VERSION 3.16)
project(tracking_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(tracking_core
  src/iou.cpp
  src/track_state.cpp
  src/risk_score.cpp
)

target_include_directories(tracking_core
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_options(tracking_core PRIVATE -Wall -Wextra -Wpedantic)

add_executable(test_tracking_core tests/test_tracking_core.cpp)
target_link_libraries(test_tracking_core PRIVATE tracking_core)

add_executable(benchmark_tracking_core benchmarks/benchmark_tracking_core.cpp)
target_link_libraries(benchmark_tracking_core PRIVATE tracking_core)

enable_testing()
add_test(NAME tracking_core_tests COMMAND test_tracking_core)
