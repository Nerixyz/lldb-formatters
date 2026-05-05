#include <QImage>

int main()
{
    QImage null;
    QImage i200x300Pm(QSize(200, 300), QImage::Format_ARGB32_Premultiplied);
    i200x300Pm.fill(Qt::white);

    const uchar *data = std::as_const(i200x300Pm).bits();

    return 0;  // break here
}
