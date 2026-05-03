#include <QRect>

int main()
{
    QRect empty;
    QRect rect(10, 20, 30, 40);
    constexpr QRect invalid(QPoint(10, 20), QPoint(0, 0));
    static_assert(invalid.width() == -9);
    static_assert(invalid.height() == -19);

    return 0;  // break here
}
