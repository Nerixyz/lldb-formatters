#include <boost/json/array.hpp>

int main()
{
    boost::json::array empty;
    boost::json::array one{123};
    boost::json::array allTypes{
        nullptr,
        true,
        false,
        -123,
        123,
        3.25,
        "string",
        "a-very-long-string-so-we-allocate-it",
        boost::json::object{
            {"key", {"value"}},
            {"something", true},
        },
        {1, true, false, boost::json::object{{"key", "value"}}},
    };

    return 0;  // break here
}
