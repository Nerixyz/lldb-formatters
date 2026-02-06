#pragma once

#include <sol/forward.hpp>

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

    int postInc();

    void setToSize(sol::variadic_args args);
};

void initMyLib(sol::table &libTbl);

}  // namespace mylib
