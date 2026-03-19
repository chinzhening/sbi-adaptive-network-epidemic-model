cmake_minimum_required(VERSION 3.20)
project(abc_sampler CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

find_package(OpenMP REQUIRED)

include(FetchContent)
FetchContent_Declare(
    tomlplusplus
    GIT_REPOSITORY https://github.com/marzer/tomlplusplus.git
    GIT_TAG        v3.4.0
)
FetchContent_MakeAvailable(tomlplusplus)

add_executable(abc_sampler
    src/main.cpp
    src/config.cpp
    src/io.cpp
    src/simulator.cpp
    src/rejection.cpp
    src/summary.cpp
    src/normalization.cpp
    src/distance.cpp
)

target_include_directories(abc_sampler PRIVATE include)

target_compile_options(abc_sampler PRIVATE
    -O3 -march=native -ffast-math -funroll-loops
)

target_link_libraries(abc_sampler PRIVATE
    OpenMP::OpenMP_CXX
    tomlplusplus::tomlplusplus
)