#include <boost/unordered/concurrent_flat_map.hpp>
#include <boost/unordered/concurrent_node_map.hpp>
#include <boost/unordered/unordered_flat_map.hpp>
#include <boost/unordered/unordered_node_map.hpp>

int main()
{
    boost::unordered_flat_map<std::string, int> flat_map;
    boost::unordered_node_map<std::string, int> node_map;

    boost::concurrent_flat_map<std::string, int> cflat_map;
    boost::concurrent_node_map<std::string, int> cnode_map;

    for (int i = 0; i < 5; ++i)
    {
        const auto str = std::to_string(i * 2);
        const auto num = i * 11;

        flat_map.emplace(str, num);
        node_map.emplace(str, num);
        cflat_map.emplace(str, num);
        cnode_map.emplace(str, num);
    }

    auto foit = flat_map.find("6");
    auto foend = node_map.end();

    return 0;  // break here
}
