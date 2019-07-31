#############################################################################
# PYTHON LIBRARIES
#############################################################################

# Help:
# https://bloerg.net/2012/11/10/cmake-and-distutils.html

# NOTE: setup.py must *not* be packaged, since it is automatically generated!
# It has to be added to CPACK_SOURCE_IGNORE_FILES (i.e. "setup.py$")!

SET(SETUP_PY_IN "${CMAKE_CURRENT_SOURCE_DIR}/setup.py.in")
SET(SETUP_PY    "${CMAKE_CURRENT_BINARY_DIR}/setup.py")
# SET(DEPS        "${CMAKE_CURRENT_SOURCE_DIR}/module/__init__.py")
SET(OUTPUT      "${CMAKE_CURRENT_BINARY_DIR}/build/timestamp")

CONFIGURE_FILE(${SETUP_PY_IN} ${SETUP_PY})

ADD_CUSTOM_COMMAND(OUTPUT ${OUTPUT}
                   COMMAND ${PYTHON_EXECUTABLE} ${SETUP_PY} build && touch ${OUTPUT})
ADD_CUSTOM_TARGET(target ALL DEPENDS ${OUTPUT})

INSTALL(CODE "EXECUTE_PROCESS(COMMAND ${PYTHON_EXECUTABLE} ${SETUP_PY} install ${PYTHON_SETUP_OPTS} --prefix=${PYTHON_LIBRARY_PREFIX})")



#############################################################################
# PROGRAMS
#############################################################################

INSTALL(PROGRAMS atlasmns-trace-controller DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES atlasmns-trace-controller.1  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS atlasmns-trace-scheduler DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES atlasmns-trace-scheduler.1  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

ADD_EXECUTABLE(atlasmns-trace-agent atlasmns-trace-agent.cc)
TARGET_INCLUDE_DIRECTORIES(atlasmns-trace-agent PUBLIC ${LIBPQXX_INCLUDE_DIRS} ${HiPerConTracer_INCLUDE_DIR})
TARGET_LINK_LIBRARIES(atlasmns-trace-agent ${LIBPQXX_LIBRARIES} ${HiPerConTracer_LIBRARY} ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
INSTALL(TARGETS atlasmns-trace-agent RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES atlasmns-trace-agent.1 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)


#############################################################################
# EXAMPLES
#############################################################################

INSTALL(FILES atlasmns-tracedataimporter DESTINATION ${CMAKE_INSTALL_FULL_SYSCONFDIR}/cron.d)

INSTALL(FILES atlasmns-database-configuration atlasmns-tracedataimporter-configuration
        DESTINATION ${CMAKE_INSTALL_DATADIR}/doc/atlasmns-trace/examples)


#############################################################################
# SUBDIRECTORIES
#############################################################################

ADD_SUBDIRECTORY(SQL)
ADD_SUBDIRECTORY(NoSQL)
