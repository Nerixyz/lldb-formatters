#include <boost/circular_buffer.hpp>

int main()
{
    boost::circular_buffer_space_optimized<int> empty;
    boost::circular_buffer_space_optimized<int> iBuffer10(10);
    boost::circular_buffer_space_optimized<int> iBuffer20(20);
    for (int i = 0; i < 15; ++i)
    {
        iBuffer10.push_back(i);
        iBuffer20.push_back(i);
    }

    auto it = iBuffer10.begin();
    auto cit = std::as_const(iBuffer10).begin();
    auto end = iBuffer10.end();
    auto last = iBuffer10.end() - 1;

    return 0;  // break here
}
