#############################################################################
# PROGRAMS
#############################################################################

INSTALL(PROGRAMS nornetinfogenerator DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES nornetinfogenerator.1  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)


#############################################################################
# EXAMPLES
#############################################################################

INSTALL(FILES atlasmns-trace-importer DESTINATION ${CMAKE_INSTALL_FULL_SYSCONFDIR}/cron.d)
