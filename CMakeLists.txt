cmake_minimum_required (VERSION 3.13)
cmake_policy (SET CMP0053 NEW)
cmake_policy (SET CMP0054 NEW)
cmake_policy (SET CMP0132 NEW)

project (
  jedi_obsimul
  VERSION 0.1.0
  LANGUAGES Fortran CXX C)  # Note - CXX is required for ESMF

if ("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
   message(SEND_ERROR "In-source builds are disabled. Please
           issue cmake command in separate build directory.")
endif ("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")

# Set the default build type to release
if (NOT CMAKE_BUILD_TYPE)
  message (STATUS "Setting build type to 'Release' as none was specified.")
  set (CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property (CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "Aggressive")
endif ()

# mepo can now clone subrepos in three styles
set (ESMA_CMAKE_DIRS
  cmake
  @cmake
  cmake@
  )
foreach (dir IN LISTS ESMA_CMAKE_DIRS)
  if (EXISTS ${CMAKE_CURRENT_LIST_DIR}/${dir})
    list (APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/${dir}")
  endif ()
endforeach ()

include (esma)

list (APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/@jedi-cmake")

ecbuild_declare_project()

esma_mepo_style(env env_dir)
esma_add_subdirectory (${env_dir})

# A code in the src tree tries to download a file
# at CMake time. This is antithetical to the idea of
# being able to build on a compute node. If we are on
# a node with no internet, we need to be able to build.

set(CRTM_COEFFICIENTS_DIR /discover/nobackup/projects/gmao/advda/SwellStaticFiles/jedi/crtm_coefficients/2.4.1_skylab_4.0)

if(EXISTS ${CRTM_COEFFICIENTS_DIR})
  message(STATUS "Found CRTM coefficients at ${CRTM_COEFFICIENTS_DIR}. We will symlink in the data files.")
  # first create a directory called 'test-data-release' in the *source* tree
  file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/test-data-release/crtm)
  # then symlink the data files into that directory
  file(CREATE_LINK
    ${CRTM_COEFFICIENTS_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/test-data-release/crtm/2.4.1_skylab_4.0
    SYMBOLIC
    )

  # first create a directory called 'test-data-release' in the *source* tree
  file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/@ufo/test-data-release/crtm)
  # then symlink the data files into that directory
  file(CREATE_LINK
    ${CRTM_COEFFICIENTS_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/src/@ufo/test-data-release/crtm/2.4.1_skylab_4.0
    SYMBOLIC
    )
else()
  message(STATUS "No CRTM coefficients found at ${CRTM_COEFFICIENTS_DIR}. Make sure you are on a node with internet access.")
  execute_process(
    COMMAND ping www.nasa.gov -c 4
    RESULT_VARIABLE NO_CONNECTION
    )
  if(NO_CONNECTION GREATER 0)
    message(FATAL_ERROR "No internet connection detected. Please run on a node with internet access or set CRTM_COEFFICIENTS_DIR to a directory with the CRTM coefficients.")
  endif()
endif()

# Recursively build source tree
esma_add_subdirectory (src)

# https://www.scivision.dev/cmake-auto-gitignore-build-dir/
# --- auto-ignore build directory
if(NOT EXISTS ${PROJECT_BINARY_DIR}/.gitignore)
  file(WRITE ${PROJECT_BINARY_DIR}/.gitignore "*")
endif()

# Piggyback that file into install
install(
   FILES ${PROJECT_BINARY_DIR}/.gitignore
   DESTINATION ${CMAKE_INSTALL_PREFIX}
   )

# Adds ability to tar source
#include(esma_cpack)
