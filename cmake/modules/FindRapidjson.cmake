include(FindPackageHandleStandardArgs)

set(_rapidjson_include_dir "${CMAKE_SOURCE_DIR}/third-party/rapidjson/include")

find_package_handle_standard_args(rapidjson DEFAULT_MSG _rapidjson_include_dir)

if (rapidjson_FOUND)
    add_library(rapidjson INTERFACE IMPORTED)
    set_target_properties(rapidjson PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${_rapidjson_include_dir}"
    )
    target_compile_definitions(rapidjson INTERFACE 
        RAPIDJSON_HAS_STDSTRING=1
    )
    add_library(rapidjson::rapidjson ALIAS rapidjson)
endif ()

mark_as_advanced(rapidjson_INCLUDE_DIR)
