#include <QSet>

int main()
{
    QSet<int> empty;
    QSet<int> one;
    one.insert(1);

    QSet<int> many{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    return 0;  // break here
}
