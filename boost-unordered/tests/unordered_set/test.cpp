#include <boost/unordered/unordered_set.hpp>

int main()
{
    boost::unordered_set<std::string> set;
    boost::unordered_multiset<std::string> multiset;

    for (int i = 0; i < 5; ++i)
    {
        const auto str = std::to_string(i * 2);

        set.emplace(str);
        multiset.emplace(str);
        multiset.emplace(str);
    }

    auto uit = set.find("6");
    auto uend = set.end();

    auto ucit = std::as_const(set).find("6");
    auto ucend = set.cend();

    return 0;  // break here
}
