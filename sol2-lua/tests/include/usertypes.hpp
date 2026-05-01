#pragma once

#include <sol/sol.hpp>

#include <memory>
#include <string>

namespace mylib {

struct MyType {
    int myVal = 42;
    std::string myStr;
};

class MyTypeWrapper
{
public:
    std::weak_ptr<MyType> myWeak;
};

struct MyOwnedToLua {
    std::string str;
    int val = 40;

    int postInc()
    {
        return this->val++;
    }

    void setToSize(sol::variadic_args args)
    {
        this->val = args.size();
    }
};

inline void initMyLib(sol::table &libTbl)
{
    libTbl.new_usertype<MyTypeWrapper>("MyTypeWrapper", sol::no_constructor);
    libTbl.new_usertype<MyOwnedToLua>("MyOwned", sol::no_constructor,
                                      "post_inc", &MyOwnedToLua::postInc,
                                      "set_to_size", &MyOwnedToLua::setToSize);
}

}  // namespace mylib
