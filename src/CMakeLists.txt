#############################################################################
# PROGRAMS
#############################################################################

INSTALL(PROGRAMS atlastrace-trace-scheduler DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES atlastrace-trace-scheduler.1  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)


ADD_EXECUTABLE(atlasmns-trace-agent atlasmns-trace-agent.cc)
TARGET_INCLUDE_DIRECTORIES(atlasmns-trace-agent PUBLIC ${HiPerConTracer_INCLUDE_DIR})
TARGET_LINK_LIBRARIES(atlasmns-trace-agent ${HiPerConTracer_LIBRARY} ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
INSTALL(TARGETS atlasmns-trace-agent RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES atlasmns-trace-agent.1 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)


#############################################################################
# EXAMPLES
#############################################################################
