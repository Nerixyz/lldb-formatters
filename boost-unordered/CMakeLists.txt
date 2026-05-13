find_package(Boost REQUIRED CONFIG COMPONENTS headers)

if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
