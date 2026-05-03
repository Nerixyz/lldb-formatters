#include <QRectF>

int main()
{
    QRectF empty;
    QRectF rect(1.5, 2.5, 3.5, 4.5);
    constexpr QRectF invalid(QPointF(10.5, 20.5), QPointF(0, 0));
    static_assert(invalid.width() == -10.5);
    static_assert(invalid.height() == -20.5);

    return 0;  // break here
}
