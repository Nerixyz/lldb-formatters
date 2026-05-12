find_package(rapidjson REQUIRED MODULE)

if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
