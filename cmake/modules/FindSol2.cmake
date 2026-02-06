include(FindPackageHandleStandardArgs)

set(_sol2_include_dir "${CMAKE_SOURCE_DIR}/third-party/sol2/include")

find_package_handle_standard_args(sol2 DEFAULT_MSG _sol2_include_dir)

# Same as in Chatterino
if (sol2_FOUND)
    add_library(sol2 INTERFACE IMPORTED)
    set_target_properties(sol2 PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${_sol2_include_dir}"
    )
    target_compile_definitions(sol2 INTERFACE 
        SOL_ALL_SAFETIES_ON=1
        SOL_USING_CXX_LUA=1
        SOL_NO_NIL=0
    )
    target_link_libraries(sol2 INTERFACE LuaWrap)
    add_library(sol2::sol2 ALIAS sol2)
endif ()

mark_as_advanced(sol2_INCLUDE_DIR)
