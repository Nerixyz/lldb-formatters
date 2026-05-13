#include <boost/unordered/unordered_map.hpp>

int main()
{
    boost::unordered_map<std::string, int> map;
    boost::unordered_multimap<std::string, int> multimap;

    for (int i = 0; i < 5; ++i)
    {
        const auto str = std::to_string(i * 2);
        const auto num = i * 11;

        map.emplace(str, num);
        multimap.emplace(str, num);
        multimap.emplace(str, num + 1);
    }

    auto uit = map.find("6");
    auto uend = map.end();

    auto ucit = std::as_const(map).find("6");
    auto ucend = map.cend();

    return 0;  // break here
}
