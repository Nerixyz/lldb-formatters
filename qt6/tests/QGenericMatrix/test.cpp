#include <QGenericMatrix>

int main()
{
    QMatrix2x3 cols2rows3;
    for (int col = 0; col < 2; col++)
    {
        for (int row = 0; row < 3; row++)
        {
            cols2rows3(row, col) = col + row * 2;
        }
    }

    QMatrix3x2 cols3rows2;
    for (int col = 0; col < 3; col++)
    {
        for (int row = 0; row < 2; row++)
        {
            cols3rows2(row, col) = col + row * 3;
        }
    }

    return 0;  // break here
}
