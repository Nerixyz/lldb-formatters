find_package(Python3 COMPONENTS Interpreter)

set(_testlib_dir "${CMAKE_CURRENT_LIST_DIR}/../../test")
cmake_path(NORMAL_PATH _testlib_dir)
set(_scripts_root "${CMAKE_CURRENT_LIST_DIR}/../../scripts")
cmake_path(NORMAL_PATH _scripts_root)

# Find lldb python path
if(NOT LLDB_PYTHON_PATH)
    if(NOT LLDB_PATH)
        find_program(LLDB_PATH lldb REQUIRED)
    endif()
    execute_process(
        COMMAND "${LLDB_PATH}" --python-path
        OUTPUT_VARIABLE _lldb_python_path
        OUTPUT_STRIP_TRAILING_WHITESPACE
        COMMAND_ERROR_IS_FATAL ANY
    )
    set(LLDB_PYTHON_PATH "${_lldb_python_path}" CACHE STRING "Path to lldb.py" FORCE)
endif()
message(STATUS "LLDB Python path: ${LLDB_PYTHON_PATH}")

function(create_python_test)
    set(_options AUTO_QT USE_ALL_SCRIPT)
    set(_one_val DIRECTORY TEST PREFIX)
    set(_multi_val LIBRARIES SCRIPTS)
    cmake_parse_arguments(PARSE_ARGV 0 arg "${_options}" "${_one_val}" "${_multi_val}")

    set(_exe_name "${arg_PREFIX}-${arg_TEST}-bin")
    set(_test_name "${arg_PREFIX}.${arg_TEST}")

    if (arg_USE_ALL_SCRIPT)
        set(arg_SCRIPTS "-s ${_scripts_root}/all.py")
        set(_exe_name "${_exe_name}-with-all-py")
        set(_test_name "${_test_name}-with-all-py")
    else()
        list(TRANSFORM arg_SCRIPTS PREPEND "-s ")
    endif()

    add_executable("${_exe_name}")
    target_sources("${_exe_name}" PRIVATE "${arg_DIRECTORY}/${arg_TEST}/test.cpp")
    target_link_libraries("${_exe_name}" PRIVATE ${arg_LIBRARIES})
    if(arg_AUTO_QT)
        set_target_properties("${_exe_name}" PROPERTIES
            AUTOMOC ON
            AUTOUIC ON
            AUTORCC ON
        )
    endif()

    add_test(
        NAME "${_test_name}"
        COMMAND
            "${Python3_EXECUTABLE}"
            "${_testlib_dir}/runtest.py"
            "${arg_DIRECTORY}/${arg_TEST}/test.py"
            -b $<TARGET_FILE:${_exe_name}>
            --lldb-py "${LLDB_PYTHON_PATH}"
            ${arg_SCRIPTS}
    )

    if(NOT TARGET "${arg_PREFIX}-all")
        add_custom_target("${arg_PREFIX}-all")
    endif()
    add_dependencies("${arg_PREFIX}-all" "${_exe_name}")
endfunction()

function(create_python_tests)
    set(_multi_val TESTS)
    cmake_parse_arguments(PARSE_ARGV 0 arg "" "" "${_multi_val}")

    foreach(test ${arg_TESTS})
        create_python_test(TEST "${test}" ${arg_UNPARSED_ARGUMENTS})
    endforeach()

    list(GET arg_TESTS 0 _first_test)
    if(_first_test)
        create_python_test(TEST "${_first_test}" USE_ALL_SCRIPT ${arg_UNPARSED_ARGUMENTS})
    endif()
endfunction()

