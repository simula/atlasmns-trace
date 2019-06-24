#################################################
# EXAMPLES
#################################################

INSTALL(FILES install-database-and-users database.sql procedures.sql README schema.sql users.sql
        DESTINATION ${CMAKE_INSTALL_DATADIR}/doc/atlasmsn-trace/examples/SQL)
