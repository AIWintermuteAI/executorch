# Copyright 2023-2024 Arm Limited and/or its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

cmake_minimum_required(VERSION 3.20)

include(pico_sdk_import.cmake)

project(arm_executor_runner C CXX ASM)
set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

option(SEMIHOSTING "Enable semihosting" OFF)
option(ET_ARM_BAREMETAL_METHOD_ALLOCATOR_POOL_SIZE "Set ET_ARM_BAREMETAL_METHOD_ALLOCATOR_POOL_SIZE to specify memory alloction pool size" OFF)
option(ET_ARM_BAREMETAL_TEMP_ALLOCATOR_POOL_SIZE "Set ET_ARM_BAREMETAL_TEMP_ALLOCATOR_POOL_SIZE to specify temp alloction pool size" OFF)


if(NOT DEFINED ET_PTE_FILE_PATH AND NOT ${SEMIHOSTING})
  message(
    FATAL_ERROR
      "ET_PTE_FILE_PATH must specify a model .pte, for bare metal systems the "
      "model is built into the binary."
  )
endif()

set(TARGET_BOARD "rp2040" CACHE STRING "Target board")

# Example ExecuTorch demo for bare metal Cortex-M based systems
set(ET_DIR_PATH
    "../../.."
    CACHE PATH "Path to ExecuTorch dir"
)
set(ET_BUILD_DIR_PATH
    "${ET_DIR_PATH}/cmake-out"
    CACHE PATH "Path to ExecuTorch build dir"
)
set(ET_INCLUDE_PATH
    "${ET_DIR_PATH}/.."
    CACHE PATH "Path to ExecuTorch headers"
)
set(ET_PTE_FILE_PATH
    ""
    CACHE PATH "Path to ExecuTorch model pte"
)
set(PYTHON_EXECUTABLE
    "python"
    CACHE PATH "Define to override python executable used"
)

get_filename_component(ET_BUILD_DIR_PATH ${ET_BUILD_DIR_PATH} REALPATH)
get_filename_component(ET_DIR_PATH ${ET_DIR_PATH} REALPATH)
get_filename_component(ET_INCLUDE_PATH ${ET_INCLUDE_PATH} REALPATH)
if(NOT ${SEMIHOSTING})
  get_filename_component(ET_PTE_FILE_PATH ${ET_PTE_FILE_PATH} REALPATH)
endif()


# Dependencies from the ExecuTorch build
add_library(executorch STATIC IMPORTED)
set_property(
  TARGET executorch PROPERTY IMPORTED_LOCATION
                             "${ET_BUILD_DIR_PATH}/libexecutorch.a"
)

add_library(executorch_core STATIC IMPORTED)
set_property(
  TARGET executorch_core
  PROPERTY IMPORTED_LOCATION "${ET_BUILD_DIR_PATH}/libexecutorch_core.a"
)
target_link_libraries(executorch INTERFACE executorch_core)

add_library(portable_ops_lib STATIC IMPORTED)
set_property(
  TARGET portable_ops_lib
  PROPERTY IMPORTED_LOCATION
           "${ET_BUILD_DIR_PATH}/examples/arm/libarm_portable_ops_lib.a"
)
add_library(portable_kernels STATIC IMPORTED)
set_property(
  TARGET portable_kernels
  PROPERTY IMPORTED_LOCATION
           "${ET_BUILD_DIR_PATH}/kernels/portable/libportable_kernels.a"
)

add_library(quantized_ops_lib STATIC IMPORTED)
set_property(
  TARGET quantized_ops_lib
  PROPERTY IMPORTED_LOCATION
           "${ET_BUILD_DIR_PATH}/kernels/quantized/libquantized_ops_lib.a"
)
add_library(quantized_kernels STATIC IMPORTED)
set_property(
  TARGET quantized_kernels
  PROPERTY IMPORTED_LOCATION
           "${ET_BUILD_DIR_PATH}/kernels/quantized/libquantized_kernels.a"
)

add_library(extension_runner_util STATIC IMPORTED)
set_property(
  TARGET extension_runner_util
  PROPERTY
    IMPORTED_LOCATION
    "${ET_BUILD_DIR_PATH}/extension/runner_util/libextension_runner_util.a"
)

# Convert pte to header
if(NOT ${SEMIHOSTING})
  add_custom_target(
    gen_model_header DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/model_pte.h
  )

  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/model_pte.h
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_SOURCE_DIR}/pte_to_header.py --pte
            ${ET_PTE_FILE_PATH} --outdir ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS ${ET_PTE_FILE_PATH}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  )
endif()

# The arm_executor_runner executable
add_executable(arm_executor_runner)

target_sources(
  arm_executor_runner PRIVATE arm_executor_runner.cpp arm_perf_monitor.cpp
)

# Need whole-archive to ensure C++ ctor's are called - this may be wasteful for
# bin size as we link in a number of other symbols
target_link_libraries(
  arm_executor_runner
  extension_runner_util
  executorch
  "-Wl,--whole-archive"
  portable_ops_lib
  portable_kernels
  "-Wl,--no-whole-archive"
  -Xlinker -Map=arm_executor_runner.map
  pico_stdlib
)

# ET headers and generated headers includes
target_include_directories(
  arm_executor_runner PRIVATE ${ET_INCLUDE_PATH} ${CMAKE_CURRENT_BINARY_DIR}
)

if(SEMIHOSTING)
  target_compile_definitions(arm_executor_runner PUBLIC SEMIHOSTING)
else()
  add_dependencies(arm_executor_runner gen_model_header)
endif()

if(ET_ARM_BAREMETAL_METHOD_ALLOCATOR_POOL_SIZE)
  target_compile_definitions(arm_executor_runner PUBLIC ET_ARM_BAREMETAL_METHOD_ALLOCATOR_POOL_SIZE=${ET_ARM_BAREMETAL_METHOD_ALLOCATOR_POOL_SIZE})
endif()

if(ET_ARM_BAREMETAL_TEMP_ALLOCATOR_POOL_SIZE)
  target_compile_definitions(arm_executor_runner PUBLIC ET_ARM_BAREMETAL_TEMP_ALLOCATOR_POOL_SIZE=${ET_ARM_BAREMETAL_TEMP_ALLOCATOR_POOL_SIZE})
endif()

# Fixup compilation of retarget.c
if(SEMIHOSTING)
  # Remove this when MLBEDSW-8910 is closed.
  set_source_files_properties(
    ${ETHOS_SDK_PATH}/core_platform/targets/${TARGET_BOARD}/retarget.c
    PROPERTIES HEADER_FILE_ONLY TRUE
  )
endif()

# enable usb output, disable uart output
pico_enable_stdio_usb(arm_executor_runner 1)
pico_enable_stdio_uart(arm_executor_runner 0)

pico_add_extra_outputs(arm_executor_runner)

# cmake -B /Users/dmitrymaslov/github/executorch/examples/arm/executor_runner_rp2040/cmake-out -DET_DIR_PATH:PATH=/Users/dmitrymaslov/github/executorch -DET_BUILD_DIR_PATH:PATH=/Users/dmitrymaslov/github/executorch/cmake-out -DET_PTE_FILE_PATH:PATH=/Users/dmitrymaslov/github/executorch/examples/arm/add_arm_ethos-u55-128.pte -DPYTHON_EXECUTABLE=/Users/dmitrymaslov/miniconda3/envs/excutorch/bin/python3
# cmake --build /Users/dmitrymaslov/github/executorch/examples/arm/executor_runner_rp2040/cmake-out --parallel -- arm_executor_runner