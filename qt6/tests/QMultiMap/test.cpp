#include <QMap>

int main()
{
    QMultiMap<int, int> empty;
    QMultiMap<int, int> one;
    one.insert(1, 2);
    one.insert(1, 3);

    QMultiMap<int, int> many{
        {1, 1}, {2, 2}, {3, 3}, {4, 4}, {5, 5},
        {1, 2}, {2, 3}, {3, 4}, {4, 5}, {5, 6},
    };

    return 0;  // break here
}
