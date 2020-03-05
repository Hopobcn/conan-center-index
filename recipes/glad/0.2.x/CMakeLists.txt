cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake")
conan_basic_setup()

add_subdirectory("source_subfolder/cmake")

###############################################
## Options
##
option(GLAD_ALIAS "If true, --alias" OFF)
if (GLAD_ALIAS)
    list(APPEND GLAD_INTERNAL_FLAGS ALIAS)
endif()

option(GLAD_DEBUG "If true, --debug" OFF)
if (GLAD_DEBUG)
    list(APPEND GLAD_INTERNAL_FLAGS DEBUG)
endif()

option(GLAD_HEADERONLY "If true, --header-only" OFF)
if (GLAD_HEADERONLY)
    list(APPEND GLAD_INTERNAL_FLAGS HEADERONLY)
endif()

option(GLAD_LOADER "--loader" OFF)
if (GLAD_LOADER)
    list(APPEND GLAD_INTERNAL_FLAGS LOADER)
endif()

option(GLAD_MX "--mx" OFF)
if (GLAD_MX)
    list(APPEND GLAD_INTERNAL_FLAGS MX)
endif()

option(GLAD_MXGLOBAL "--mx-global" OFF)
if (GLAD_MXGLOBAL)
    list(APPEND GLAD_INTERNAL_FLAGS MXGLOBAL)
endif()

option(GLAD_ONDEMAND "--on-demand" OFF)
if (GLAD_ONDEMAND)
    list(APPEND GLAD_INTERNAL_FLAGS ON_DEMAND)
endif()

#############################################

option(GLAD_MERGE "Merge multiple APIs of the same specitifation into one file." OFF)
if (GLAD_MERGE)
    list(APPEND GLAD_FLAGS MERGE)
endif()

option(GLAD_REPRODUCIBLE "")
if (GLAD_REPRODUCIBLE)
    list(APPEND GLAD_FLAGS REPRODUCIBLE)
endif()

option(GLAD_QUIET "Disable logging")
if (GLAD_QUIET)
    list(APPEND GLAD_FLAGS QUIET)
endif()

#############################################

message("${BUILD_SHARED_LIBS} ${GLAD_FLAGS} ${GLAD_INTERNAL_FLAGS} ${GLAD_INTERNAL_API} ${GLAD_EXTENSIONS}")

glad_add_library(glad ${BUILD_SHARED_LIBS} ${GLAD_FLAGS} ${GLAD_INTERNAL_FLAGS} ${GLAD_API} ${GLAD_EXTENSIONS})

include(GNUInstallDirs)
install(TARGETS glad
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)