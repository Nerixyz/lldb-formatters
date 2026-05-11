#include <boost/json/value.hpp>

int main()
{
    boost::json::key_value_pair kv("key", 1234);
    boost::json::key_value_pair kvStr("key", "a string");

    return 0;  // break here
}
