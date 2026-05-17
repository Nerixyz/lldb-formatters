find_package(Rapidjson REQUIRED MODULE)

if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
