#include <sol/forward.hpp>
#include <sol/sol.hpp>

#include <filesystem>

static std::string localFilePath(std::string_view name)
{
    std::filesystem::path self(__FILE__);
    return (self.parent_path() / name).string();
}

int main()
{
    sol::state lua;
    lua.open_libraries(sol::lib::base);
    lua.set_function(
        "a_c_function", +[](lua_State *L) {
            return 0;
        });
    lua.set_function(
        "a_c_function_from_file", +[](lua_State *L) {
            return 0;
        });
    lua.do_file(localFilePath("file.lua"));
    lua.script(R"(
        local function xd()
            a_c_function()
        end
        function a_lua_function()
            xd()
        end
    )");
    sol::table globals = lua.globals();
    sol::function a_lua_function = lua["a_lua_function"];
    sol::function run_in_file = lua["run_in_file"];
    run_in_file();
    a_lua_function();

    return 0;  // break here
}
