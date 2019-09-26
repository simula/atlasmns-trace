# MELODIC/NorNet Build Scripts
# Copyright (C) 2017-2019 by Thomas Dreibholz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact: dreibh@simula.no

CMAKE_MINIMUM_REQUIRED(VERSION 3.0.2)
PROJECT(atlasmns-trace LANGUAGES CXX)

SET(BUILD_MAJOR "0")
SET(BUILD_MINOR "4")
SET(BUILD_PATCH "1")
SET(BUILD_VERSION ${BUILD_MAJOR}.${BUILD_MINOR}.${BUILD_PATCH})

SET(CMAKE_CXX_STANDARD 14)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
SET(CMAKE_CXX_EXTENSIONS OFF)


#############################################################################
# INSTALLATION_DIRECTORIES
#############################################################################

# See: https://cmake.org/cmake/help/v3.0/module/GNUInstallDirs.html
INCLUDE(GNUInstallDirs)


#############################################################################
# PACKAGING
#############################################################################

SET(CPACK_SOURCE_GENERATOR "TXZ")
SET(CPACK_SOURCE_PACKAGE_FILE_NAME
   "${CMAKE_PROJECT_NAME}-${BUILD_MAJOR}.${BUILD_MINOR}.${BUILD_PATCH}")
SET(CPACK_SOURCE_IGNORE_FILES
   "${PROJECT_SOURCE_DIR}/${CMAKE_PROJECT_NAME}-*;${PROJECT_SOURCE_DIR}/${CMAKE_PROJECT_NAME}_*;/build/;/.git/;.gitmodules$;/.gimp/;/config.log;/CMakeFiles/;CMakeCache.txt$;.cmake$;.tar.gz$;/_CPack_Packages;/Makefile$;~$;/build-deb;/clean-deb;/filter-empty-entries;/make-symbols;/make-ppa;/make-deb;/debian.conf;/make-rpm;/rpm.conf;${CPACK_SOURCE_IGNORE_FILES};/ripe-atlas-cousteau/;setup.py$")
INCLUDE(CPack)

ADD_CUSTOM_TARGET(dist COMMAND ${CMAKE_MAKE_PROGRAM} clean package_source)


INCLUDE(CheckIncludeFile)
INCLUDE(CheckStructHasMember)


#############################################################################
# OS-DEPENDENT
#############################################################################

IF (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    MESSAGE(STATUS ${CMAKE_SYSTEM_NAME} " supported")

ELSEIF (${CMAKE_SYSTEM_NAME} MATCHES "FreeBSD")
    MESSAGE(STATUS ${CMAKE_SYSTEM_NAME} " supported")
    SET(CMAKE_REQUIRED_INCLUDES "/usr/local/include" "/usr/include")
    SET(CMAKE_LIBRARY_PATH "/usr/local/lib")
    INCLUDE_DIRECTORIES("/usr/local/include")

ELSEIF (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    MESSAGE(STATUS ${CMAKE_SYSTEM_NAME} " supported")
    SET(CMAKE_REQUIRED_INCLUDES "/usr/local/include" "/usr/include" "/usr/local/opt/openssl/include")
    SET(CMAKE_LIBRARY_PATH "/usr/local/lib")
    INCLUDE_DIRECTORIES("/usr/local/include" "/usr/local/opt/openssl/include")

ELSEIF (${CMAKE_SYSTEM_NAME} MATCHES "NetBSD")
    MESSAGE(STATUS ${CMAKE_SYSTEM_NAME} " supported")
    LIST(APPEND neat_headers neat_bsd.h)
    LIST(APPEND neat_sources neat_bsd.c)
    SET(CMAKE_REQUIRED_INCLUDES "/usr/pkg/include" "/usr/include" "/usr/local/include")
    SET(CMAKE_LIBRARY_PATH "/usr/local/lib")
    INCLUDE_DIRECTORIES("/usr/pkg/include" "/usr/local/include")

ELSEIF (${CMAKE_SYSTEM_NAME} MATCHES "NetBSD")
    MESSAGE(STATUS ${CMAKE_SYSTEM_NAME} " supported")

ELSE()
    MESSAGE(FATAL_ERROR ${CMAKE_SYSTEM_NAME} " not supported (yet?)")

ENDIF()


#############################################################################
# REQUIREMENTS
#############################################################################

INCLUDE(FindPackageHandleStandardArgs)

# ###### Threads ############################################################
FIND_PACKAGE(Threads REQUIRED)

# ###### Boost ##############################################################
FIND_PACKAGE(Boost REQUIRED COMPONENTS log date_time system thread iostreams filesystem program_options)
IF (NOT Boost_FOUND)
   MESSAGE(FATAL_ERROR "Cannot find Boost libraries!")
ELSE()
  INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS})
ENDIF()
ADD_DEFINITIONS(-DBOOST_ALL_DYN_LINK)   # <<-- Required to handle BOOST Log link problem!

# ###### libhipercontracer ##################################################
FIND_PATH(HiPerConTracer_INCLUDE_DIR hipercontracer/traceroute.h REQUIRED)
FIND_LIBRARY(HiPerConTracer_LIBRARY NAMES hipercontracer REQUIRED)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(HiPerConTracer DEFAULT_MSG HiPerConTracer_INCLUDE_DIR HiPerConTracer_LIBRARY)
MARK_AS_ADVANCED(HiPerConTracer_LIBRARY HiPerConTracer_INCLUDE_DIR)

# ###### Python #############################################################
SET(PYTHON_LIBRARY_PREFIX "${CMAKE_INSTALL_PREFIX}" CACHE PATH   "AtlasMNS Python library prefix")
SET(PYTHON_SETUP_OPTS     ""                        CACHE STRING "")

SET(Python_ADDITIONAL_VERSIONS 3)
INCLUDE(FindPythonInterp)

FIND_PACKAGE(PythonInterp 3.4.0 REQUIRED)

# ###### Python #############################################################
FIND_PACKAGE(PkgConfig)
PKG_CHECK_MODULES(LIBPQXX libpqxx)
IF (NOT LIBPQXX_FOUND)
  MESSAGE(FATAL_ERROR "Cannot find libpqxx library!")
ENDIF()


#############################################################################
# SOURCE DIRECTORIES
#############################################################################

ADD_SUBDIRECTORY(src)
