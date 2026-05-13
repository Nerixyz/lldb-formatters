#include <boost/unordered/concurrent_flat_set.hpp>
#include <boost/unordered/concurrent_node_set.hpp>
#include <boost/unordered/unordered_flat_set.hpp>
#include <boost/unordered/unordered_node_set.hpp>
int main()
{
    boost::unordered_flat_set<std::string> flat_set;
    boost::unordered_node_set<std::string> node_set;

    boost::concurrent_flat_set<std::string> cflat_set;
    boost::concurrent_node_set<std::string> cnode_set;

    for (int i = 0; i < 5; ++i)
    {
        const auto str = std::to_string(i * 2);

        flat_set.emplace(str);
        node_set.emplace(str);
        cflat_set.emplace(str);
        cnode_set.emplace(str);
    }

    auto foit = flat_set.find("6");
    auto foend = node_set.end();

    return 0;  // break here
}
