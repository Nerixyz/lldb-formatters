add_library(boost-json-impl STATIC lib/impl.cpp)
target_link_libraries(boost-json-impl PUBLIC Boost::headers)
target_compile_definitions(boost-json-impl PUBLIC BOOST_ALL_NO_LIB)

create_python_tests(
    DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
    PREFIX boost-json
    LIBRARIES
        Boost::headers
        boost-json-impl
    SCRIPTS
        "${CMAKE_CURRENT_LIST_DIR}/../scripts/boost_json.py"
    TESTS
        array
        key_value_pair
        object
        value
)
