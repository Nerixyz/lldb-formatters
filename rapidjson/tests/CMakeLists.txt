create_python_tests(
    DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
    PREFIX rapidjson
    LIBRARIES
        rapidjson::rapidjson
    SCRIPTS
        "${CMAKE_CURRENT_LIST_DIR}/../scripts/rapidjson.py"
    TESTS
        GenericValueUtf8
        GenericValueUtf16
)
