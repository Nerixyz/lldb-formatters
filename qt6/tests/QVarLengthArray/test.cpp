#include <QVarLengthArray>

int main()
{
    QVarLengthArray<int, 4> empty;
    QVarLengthArray<int, 4> values{1, 2, 3};
    QVarLengthArray<int, 4> heap{1, 2, 3, 4, 5, 6};

    return 0;  // break here
}
