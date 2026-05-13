create_python_tests(
    DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
    PREFIX boost-unordered
    LIBRARIES
        Boost::headers
    SCRIPTS
        "${CMAKE_CURRENT_LIST_DIR}/../scripts/boost_unordered.py"
    TESTS
        foa_map
        foa_set
        unordered_set
        unordered_map
)
