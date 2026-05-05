#include <QDateTime>
#include <QFloat16>
#include <QObject>
#include <QSize>
#include <QVariant>

#include <string>

struct MyType {
    int a = 42;
    int b = 43;
};
Q_DECLARE_METATYPE(MyType)

struct MyLargeType {
    std::string str1;
    std::string str2;
};
Q_DECLARE_METATYPE(MyLargeType)

int main()
{
    QObject qObj;

    QVariant null;
    QVariant vBool = true;
    QVariant vInt = -10;
    QVariant vUint = 10u;
    QVariant vLongLong = QVariant::fromValue<long long>(42);
    QVariant vULongLong = QVariant::fromValue<unsigned long long>(42);

    QVariant vDouble = QVariant::fromValue<double>(3.25);
    QVariant vLong = QVariant::fromValue<long>(42);
    QVariant vShort = QVariant::fromValue<short>(42);
    QVariant vChar = QVariant::fromValue('V');
    QVariant vULong = QVariant::fromValue<unsigned long>(42ul);
    QVariant vUShort = QVariant::fromValue<unsigned short>(42);

    QVariant vUChar = QVariant::fromValue<unsigned char>('U');
    QVariant vFloat = QVariant::fromValue<float>(3.5f);

    QVariant vVoidStar = QVariant::fromValue(static_cast<void *>(&qObj));

    QVariant vQChar = QVariant::fromValue<QChar>(u'ä');
    QVariant vQString = QStringLiteral("Hello World🍳");
    QVariant vQStringList = QVariant::fromValue<QStringList>({"foo", "bar"});
    QVariant vQByteArray = QByteArray("Hello World!");

    QVariant vQDate = QDate(2026, 5, 2);
    QVariant vQTime = QTime(13, 42);

    QVariant vSChar = QVariant::fromValue<signed char>('V');
    QVariant vChar16 = QVariant::fromValue(u'V');
    QVariant vChar32 = QVariant::fromValue(U'V');
    QVariant vNullptr = QVariant::fromValue(nullptr);
    QVariant qObjectStar = QVariant::fromValue(&qObj);
    QVariant qSize = QSize(42, 42);
    QVariant qVList =
        QVariantList{1, true, false, QDateTime::fromMSecsSinceEpoch(10)};

    QVariant qVMap = QVariantMap{
        {"bar", 42},
        {"foo", true},
    };
    QVariant qVHash = QVariantHash{
        {"foo", true},
    };

    QVariant qUserTypeNoTemplate = QVariant::fromValue<MyType>(MyType{});
    MyType stackType{1, 2};
    QVariant qUserPtr = QVariant::fromValue(&stackType);

    QVariant qUserTypeLarge = QVariant::fromValue(MyLargeType{"foo", "bar"});
    MyLargeType *lt = get_if<MyLargeType>(&qUserTypeLarge);

    int value = 1234;
    QVariant qIntPtr = QVariant::fromValue(&value);

    return 0;  // break here
}
