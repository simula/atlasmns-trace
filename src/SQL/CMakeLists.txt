#############################################################################
#### EXAMPLES                                                            ####
#############################################################################

INSTALL(FILES install-database-and-users database.sql README schema.sql users.sql
        DESTINATION ${CMAKE_INSTALL_DATADIR}/doc/atlasmns-trace/examples/SQL)
