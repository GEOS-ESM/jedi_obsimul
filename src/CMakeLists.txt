esma_add_subdirectory (Shared)
#esma_add_subdirectory (@crtm)
#esma_add_subdirectory (@oops)
#esma_add_subdirectory (@ioda)
#esma_add_subdirectory (@ioda-converters)
#esma_add_subdirectory (@ufo)
#esma_add_subdirectory (@vader)

# Instead of just add_subdirectory because ioda, say, *depends* on
# oops to be built and installed, we need to use ExternalProject to
# ensure that the dependencies are built in the right order.

message("CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")
include(ExternalProject)
ExternalProject_Add(
  oops
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@oops
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
)

ExternalProject_Add(
  ioda
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/@ioda
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}
)
ExternalProject_Add_StepDependencies(ioda build oops)

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
