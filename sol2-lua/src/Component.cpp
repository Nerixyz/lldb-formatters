#include "Component.hpp"

#include <sol/raii.hpp>
#include <sol/sol.hpp>
#include <sol/variadic_args.hpp>

namespace mylib {

int MyOwnedToLua::postInc()
{
    return this->val++;
}

void MyOwnedToLua::setToSize(sol::variadic_args args)
{
    this->val = args.size();
}

void initMyLib(sol::table &libTbl)
{
    libTbl.new_usertype<MyTypeWrapper>("MyTypeWrapper", sol::no_constructor);
    libTbl.new_usertype<MyOwnedToLua>("MyOwned", sol::no_constructor,
                                      "post_inc", &MyOwnedToLua::postInc,
                                      "set_to_size", &MyOwnedToLua::setToSize);
}

}  // namespace mylib
