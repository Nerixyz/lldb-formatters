#include "Component.hpp"

#include <sol/sol.hpp>

#include <cassert>
#include <memory>

namespace {
size_t myBoopFn(std::string foo)
{
    return foo.size();
}
}  // namespace

int main()
{
    sol::state lua;
    int x = 0;
    auto libTbl = lua.create_table();
    lua.set("lib", libTbl);
    mylib::initMyLib(libTbl);

    auto myType = std::make_shared<mylib::MyType>();
    myType->myStr = "foobar";
    lua.set("wrap", mylib::MyTypeWrapper{.myWeak = myType});

    auto myOwned = std::make_shared<mylib::MyOwnedToLua>();
    myOwned->str = "😂😂";
    lua.set("owned", myOwned);

    lua.set_function("boop", myBoopFn);
    lua.set_function("beep", [&x] {
        ++x;
    });
    lua.script(R"(
        owned:post_inc()
        owned:set_to_size(true, false, 42, (1 << 63), "fof", { 1, 2, 3, b = {a = table}}, wrap)
        beep()
        boop("loool😂")
    )");
    assert(x == 1);

    sol::function beep = lua["beep"];
    beep();
    assert(x == 2);

    return 0;
}
