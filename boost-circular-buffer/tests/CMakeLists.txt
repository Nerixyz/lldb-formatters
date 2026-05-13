create_python_tests(
    DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
    PREFIX boost-circular-buffer
    LIBRARIES
        Boost::headers
    SCRIPTS
        "${CMAKE_CURRENT_LIST_DIR}/../scripts/boost_circular_buffer.py"
    TESTS
        circular_buffer
        circular_buffer_space_optimized
)
