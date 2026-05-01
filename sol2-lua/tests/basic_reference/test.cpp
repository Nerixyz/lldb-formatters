#include <sol/forward.hpp>
#include <sol/sol.hpp>

int main()
{
    sol::state lua;
    lua.open_libraries(sol::lib::base);
    lua.script(R"(
        a_bool = true
        a_int = 1234567890123
        a_double = 3.14
        a_nil = nil
        a_string_empty = ""
        a_string_short = "a"
        a_string_long = "foobar abcdef this is some long text make sure it's correct yes"
        a_string_with_nul = "foo bar\0baz"
        a_table_empty = {}
        a_table_array = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
        a_table_named = {a = true, b = false, c = "wow", d = {1, 2, 3}, e = 42}
        a_table_mixed = {0, 1, 2, d = "what", e = "ever"}
        function a_lua_function(a, b)
            -- whatever
        end
    )");
    lua.set_function("a_c_closure", [] {
        return 0;
    });
    lua.set_function(
        "a_c_function", +[](lua_State *L) {
            return 0;
        });
    sol::table globals = lua.globals();
    sol::reference a_bool = lua["a_bool"];
    sol::reference a_int = lua["a_int"];
    sol::reference a_double = lua["a_double"];
    sol::reference a_nil = lua["a_nil"];
    sol::reference a_string_empty = lua["a_string_empty"];
    sol::reference a_string_short = lua["a_string_short"];
    sol::reference a_string_long = lua["a_string_long"];
    sol::reference a_string_with_nul = lua["a_string_with_nul"];
    sol::reference a_table_empty = lua["a_table_empty"];
    sol::reference a_table_array = lua["a_table_array"];
    sol::reference a_table_named = lua["a_table_named"];
    sol::reference a_table_mixed = lua["a_table_mixed"];
    sol::function a_lua_function = lua["a_lua_function"];
    sol::function a_c_closure = lua["a_c_closure"];
    sol::function a_c_function = lua["print"];

    return 0;  // break here
}
