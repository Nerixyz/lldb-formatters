#include <QtCore>

class CoreTypes : public QObject
{
    Q_OBJECT

public:
    enum SelectionFlag {
        NoUpdate = 0x0000,
        Clear = 0x0001,
        Select = 0x0002,
        Deselect = 0x0004,
        Toggle = 0x0008,
        Current = 0x0010,
        Rows = 0x0020,
        Columns = 0x0040,
        SelectCurrent = Select | Current,
        ToggleCurrent = Toggle | Current,
        ClearAndSelect = Clear | Select
    };
    Q_DECLARE_FLAGS(SelectionFlags, SelectionFlag)
    Q_FLAG(SelectionFlags)

    CoreTypes(QObject *parent = nullptr)
        : QObject(parent)
    {
        setObjectName("CoreTypes");
        setProperty("Foo", "This is a test");
        setProperty("Bar", 2);
    }

    QByteArray qByteArray = QByteArray("Hello World!");
    QChar qChar = QChar('c');
    QDate qDate = QDate::currentDate();

    QDateTime qDateTimeLocal = QDateTime::currentDateTime();
    QDateTime qDateTimeUtc = QDateTime::currentDateTimeUtc();
    QDateTime qDateTimeBrunei =
        QDateTime::currentDateTimeUtc().toTimeZone(QTimeZone("Asia/Brunei"));
    QDateTime qDateTimeSouthPole = QDateTime::currentDateTimeUtc().toTimeZone(
        QTimeZone("Antarctica/South_Pole"));
    QDateTime qDateTimeYukon =
        QDateTime::currentDateTimeUtc().toTimeZone(QTimeZone("Canada/Yukon"));
    QDateTime qDateTimeMarquesas = QDateTime::currentDateTimeUtc().toTimeZone(
        QTimeZone("Pacific/Marquesas"));
    QDateTime qDateTimeShouldFail = QDateTime::currentDateTimeUtc().toTimeZone(
        QTimeZone("Antarctica/Troll"));
    QDateTime qDateTimeSecOffset = QDateTime::currentDateTimeUtc().toTimeZone(
        QTimeZone(12 * 3600 + 34 * 60 + 56));
    QDateTime qDateTimeDefault = QDateTime();

    QDir qDir = QDir::currentPath();
    QFile qFile = QFile(QCoreApplication::applicationFilePath());
    QFileInfo qFileInfo = QFileInfo(QCoreApplication::applicationFilePath());
    SelectionFlags qFlags = SelectionFlag::SelectCurrent;
    QJsonDocument qJsonDocumentEmpty;
    QJsonDocument qJsonDocumentArray{QJsonArray{
        QStringLiteral("😃😃😃"),
        "foo",
        QLatin1String("foo"),
        "empty object->",
        QJsonObject{},
        "empty array ->",
        QJsonArray{},
        QJsonObject{
            {"foo", "bar"},
            {
                "abc",
                QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
            },
            {"def", QJsonArray{1, 2, true, false, 42.5}},
        },
        QJsonArray{
            "foo",
            "bar",
            QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
            QJsonArray{1, 2, true, false, 42.5},
        },
    }};
    QJsonDocument qJsonDocumentObject{QJsonObject{
        {QStringLiteral("😃😃😃"), "foo"},
        {QLatin1String("foo"), QLatin1String("bar")},
        {"empty object->", QJsonObject{}},
        {"empty array ->", QJsonArray{}},
        {"an object",
         QJsonObject{
             {"foo", "bar"},
             {
                 "abc",
                 QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
             },
             {"def", QJsonArray{1, 2, true, false, 42.5}},
         }},
        {"an array",
         QJsonArray{
             "foo",
             "bar",
             QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
             QJsonArray{1, 2, true, false, 42.5},
         }},
    }};
    QJsonObject qJsonObject{
        {"foo", "bar"},
        {QLatin1StringView("baz"), 42},
        {
            "qox",
            QJsonArray{
                1,
                false,
                QJsonValue::Null,
                "foo",
                QJsonObject{{"abc", false}},
            },
        },
    };
    QJsonArray qJsonArray{
        1, false, QJsonValue::Null, "foo", QJsonObject{{"abc", false}},
    };
    QJsonValue qJsonValueUndef{QJsonValue::Undefined};
    QJsonValue qJsonValueNull{QJsonValue::Null};
    QJsonValue qJsonValueInt{42};
    QJsonValue qJsonValueDouble{3.14};
    QJsonValue qJsonValueString{"foobar"};
    QJsonValue qJsonValueL1String{QLatin1StringView("foobaz")};
    QJsonValue qJsonValueTrue{true};
    QJsonValue qJsonValueFalse{false};
    QJsonValue qJsonValueObject{QJsonObject{{"foo", 42}}};
    QJsonValue qJsonValueArray{QJsonArray{"foo", 42, true, false}};
    QLine qLine = QLine(0, 0, 42, 42);
    QPoint qPoint = QPoint(24, 48);
    QPointF qPointF = QPointF(24.5, 48.5);
    QRect qRect = QRect(5, 5, 42, 42);
    QRectF qRectF = QRectF(5.5, 5.5, 4.2, 4.2);
    QSize qSize = QSize(42, 42);
    QSizeF qSizeF = QSizeF(4.2, 4.2);
    QString qString = QString("Hello World!");
    QString qStringEmpty = QString("");
    QString qStringNull;
    QStringView qStringView = QStringView(qString);
    QStringView qStringViewEmpty;

    QTime qTime = QTime(4, 6, 12, 164);
    QTime qTimeNoMs = QTime(4, 6, 12, 0);
    QTime qTimeNoMsNoS = QTime(4, 6, 0, 0);
    QTime qTimeNoS = QTime(12, 6, 0, 53);
    QTime qTimeInvalid;

    QUrl qUrl = QUrl("https://github.com/narnaud/natvis4qt");
    QUuid qUuid = QUuid::createUuid();
};
