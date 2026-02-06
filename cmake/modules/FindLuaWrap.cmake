include(FindPackageHandleStandardArgs)

set(LUA_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/third-party/lua")

find_package_handle_standard_args(LuaWrap DEFAULT_MSG LUA_INCLUDE_DIR)

if (LuaWrap_FOUND)
    set(_srcs 
        lapi.c
        lauxlib.c
        lbaselib.c
        lcode.c
        lcorolib.c
        lctype.c
        ldblib.c
        ldebug.c
        ldo.c
        ldump.c
        lfunc.c
        lgc.c
        linit.c
        liolib.c
        llex.c
        lmathlib.c
        lmem.c
        loadlib.c
        lobject.c
        lopcodes.c
        loslib.c
        lparser.c
        lstate.c
        lstring.c
        lstrlib.c
        ltable.c
        ltablib.c
        ltests.c
        ltm.c
        lundump.c
        lutf8lib.c
        lvm.c
        lzio.c
    )
    list(TRANSFORM _srcs PREPEND "${LUA_INCLUDE_DIR}/")

    add_library(LuaWrap STATIC ${_srcs})
    target_include_directories(LuaWrap PUBLIC "${LUA_INCLUDE_DIR}")
    set_target_properties(${liblua} PROPERTIES
        LANGUAGE CXX
        LINKER_LANGUAGE CXX
        CXX_STANDARD 98
        CXX_EXTENSIONS TRUE
    )
    target_compile_options(LuaWrap PRIVATE
        -w # don't warn about c-as-c++
        $<$<AND:$<BOOL:${MSVC}>,$<CXX_COMPILER_ID:Clang>>:/EHsc> # enable exceptions in clang-cl
    )
    set_source_files_properties(${_srcs} PROPERTIES LANGUAGE CXX)
endif ()

mark_as_advanced(LUA_INCLUDE_DIR)
