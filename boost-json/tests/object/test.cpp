#include <boost/json/object.hpp>

int main()
{
    boost::json::object empty;
    boost::json::object one{{"key", "value"}};
    boost::json::object allTypes{
        {"null", nullptr},
        {"true", true},
        {"false", false},
        {"int64", -123},
        {"uint64", 123},
        {"double", 3.25},
        {"string", "string"},
        {"longString", "a-very-long-string-so-we-allocate-it"},
        {
            "object",
            boost::json::object{
                {"key", {"value"}},
                {"something", true},
            },
        },
        {
            "array",
            {1, true, false, boost::json::object{{"key", "value"}}},
        },
    };

    return 0;  // break here
}
