add_library(soltests INTERFACE)
target_include_directories(soltests INTERFACE "${CMAKE_CURRENT_LIST_DIR}/include")

create_python_tests(
    DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
    PREFIX sol2-lua
    LIBRARIES
        soltests
        sol2
        LuaWrap
    SCRIPTS
        "${CMAKE_CURRENT_LIST_DIR}/../scripts/lua.py"
    TESTS
        basic_reference
        frame_rec
)
