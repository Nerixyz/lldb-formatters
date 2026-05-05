#include <QSpan>

#include <vector>

int main()
{
    std::vector<int> i{1, 2, 3, 4, 5};
    QSpan unsized(i);
    QSpan<int, 2> sized(unsized.subspan(0, 2));

    return 0;  // break here
}
