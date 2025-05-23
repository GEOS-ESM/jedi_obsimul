esma_add_subdirectory (Shared)

# Instead of just add_subdirectory because ioda, say, depends on
# oops to be built *AND INSTALLED*, we need to use ExternalProject to
# ensure that the dependencies are built in the right order.

include(ExternalProject)

ExternalProject_Add(
  crtm
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@crtm
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
)

ExternalProject_Add(
  oops
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@oops
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
)

ExternalProject_Add(
  vader
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@vader
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
)
ExternalProject_Add_StepDependencies(vader build oops)

ExternalProject_Add(
  ioda
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@ioda
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
    -DENABLE_IODA_DATA:BOOL=ON
)
ExternalProject_Add_StepDependencies(ioda build oops)

ExternalProject_Add(
  ioda-converters
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@ioda-converters
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
)
ExternalProject_Add_StepDependencies(ioda-converters build oops)
ExternalProject_Add_StepDependencies(ioda-converters build ioda)

ExternalProject_Add(
  ufo
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@ufo
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
    -DENABLE_UFO_DATA:BOOL=ON
)
ExternalProject_Add_StepDependencies(ufo build ioda)
ExternalProject_Add_StepDependencies(ufo build oops)
ExternalProject_Add_StepDependencies(ufo build crtm)

file (GLOB obsimul_files obsimul/*.py)
install (
  FILES ${obsimul_files}
  DESTINATION lib/Python/obsimul/
  )

#install (
#  PROGRAMS qfed_l3a.py qfed_l3b.py
#  DESTINATION bin
#  )

#install (
#  FILES config.yaml emission_factors.yaml
#  DESTINATION etc
#  )
