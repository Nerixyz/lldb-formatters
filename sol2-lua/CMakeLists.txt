find_package(LuaWrap REQUIRED)
find_package(sol2 REQUIRED)

add_executable(sol2-lua-test
    src/Component.cpp

    src/main.cpp
)

target_link_libraries(sol2-lua-test PRIVATE
    sol2
    LuaWrap
)
