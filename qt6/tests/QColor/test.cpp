#include <QColor>
#include <QDebug>

int main()
{
    QColor invalid;
    QColor rgb(12, 34, 56);
    QColor rgba(1, 2, 3, 4);
    QColor hsl;
    hsl.setHsl(42, 20, 64);
    QColor hsla;
    hsla.setHsl(-1, 0, 64, 5);
    QColor hsv;
    hsv.setHsv(42, 20, 64);
    QColor hsva;
    hsva.setHsv(-1, 0, 64, 5);
    QColor cmyk;
    cmyk.setCmyk(1, 2, 3, 4);
    QColor cmyka;
    cmyka.setCmyk(1, 2, 3, 4, 20);

    QColor extRgb = rgb.toExtendedRgb();
    extRgb.setRedF(-1);
    extRgb.setBlueF(2);
    QColor extRgba = extRgb;
    extRgba.setAlpha(23);

    qDebug() << invalid;
    qDebug() << rgb;
    qDebug() << rgba;
    qDebug() << hsl;
    qDebug() << hsla;
    qDebug() << hsv;
    qDebug() << cmyk;
    qDebug() << cmyka;
    qDebug() << extRgb;
    qDebug() << extRgba;

    return 0;  // break here
}
