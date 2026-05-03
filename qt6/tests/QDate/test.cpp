#include <QDate>

int main()
{
    QDate null;
    QDate someDay(2026, 5, 10);
    QDate min = QDate::fromJulianDay(-784350574879);
    QDate max = QDate::fromJulianDay(784354017364);

    qDebug() << null;
    qDebug() << someDay;
    qDebug() << min;
    qDebug() << max;

    return 0;  // break here
}
