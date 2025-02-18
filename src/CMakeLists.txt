esma_add_subdirectory (Shared)
esma_add_subdirectory (@crtm)
esma_add_subdirectory (@ioda)
esma_add_subdirectory (@ioda-converters)
esma_add_subdirectory (@oops)
esma_add_subdirectory (@ufo)
esma_add_subdirectory (@vader)

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
