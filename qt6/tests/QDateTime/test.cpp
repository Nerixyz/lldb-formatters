#include <QDateTime>
#include <QTimeZone>

int main()
{
    QDateTime null;
    QDateTime utc(QDate(2026, 5, 13), QTime(2, 43, 10, 500), QTimeZone::utc());
    QDateTime local(QDate(2026, 5, 13), QTime(2, 43, 10, 500));
    QDateTime offPlus1h(QDate(2026, 5, 13), QTime(2, 43, 10, 500),
                        QTimeZone::fromSecondsAheadOfUtc(60 * 60));
    QDateTime offMinus1h(QDate(2026, 5, 13), QTime(2, 43, 10, 500),
                         QTimeZone::fromSecondsAheadOfUtc(-60 * 60));
    auto negative =
        QDateTime::fromMSecsSinceEpoch(-12345678500, QTimeZone::utc());
    auto invalidZone = QDateTime::currentDateTimeUtc().toTimeZone(
        QTimeZone("Antarctica/Troll"));

    qDebug() << null;
    qDebug() << utc;
    qDebug() << local;
    qDebug() << offPlus1h;
    qDebug() << offMinus1h;
    qDebug() << negative;
    qDebug() << invalidZone;

    return 0;  // break here
}
