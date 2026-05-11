#include <boost/json/value.hpp>

int main()
{
    boost::json::value defaultC;
    boost::json::value null(nullptr);
    boost::json::value vTrue(true);
    boost::json::value vFalse(false);
    boost::json::value int64(-123456);
    boost::json::value uint64(123456);
    boost::json::value vDouble(123.5);
    boost::json::value vString("abcde");
    boost::json::value vStringLong("a-very-long-string-so-we-allocate-it");
    boost::json::value vObject(boost::json::object{
        {"key", {"value"}},
        {"something", true},
    });
    boost::json::value array{
        1,
        true,
        false,
        boost::json::object{{"key", "value"}},
    };

    return 0;  // break here
}
