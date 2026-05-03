#include <QMultiHash>

int main()
{
    QMultiHash<int, int> empty;
    QMultiHash<int, int> one;
    one.insert(1, 2);
    one.insert(1, 3);
    one.insert(1, 4);

    QMultiHash<int, int> many;
    for (int i = 1; i <= 10; i++)
    {
        many.insert(i, i);
        many.insert(i, -i);
    }

    return 0;  // break here
}
