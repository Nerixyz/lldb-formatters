#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>

int main()
{
    const QJsonObject obj{
        {
            "array",
            QJsonArray{
                1,
                2,
                QJsonValue::Null,
                "foo",
                QJsonObject{{"bar", false}},
                true,
            },
        },
        {"double", 1.25},
        {"emptyArray", QJsonArray()},
        {"emptyObject", QJsonObject()},
        {"false", false},
        {"int", 1234567890},
        {"null", QJsonValue::Null},
        {
            "object",
            QJsonObject{
                {
                    "nested",
                    QJsonObject{
                        {"object", 1},
                    },
                },
            },
        },
        {"stringAscii", "stringAscii"},
        {"stringUtf16", "utf16💔"},
        {"true", true},
    };

    auto oCrArray = obj.constBegin()[0];
    auto oCrDouble = obj.constBegin()[1];
    auto oCrEmptyArray = obj.constBegin()[2];
    auto oCrEmptyObject = obj.constBegin()[3];
    auto oCrFalse = obj.constBegin()[4];
    auto oCrInt = obj.constBegin()[5];
    auto oCrNull = obj.constBegin()[6];
    auto oCrObject = obj.constBegin()[7];
    auto oCrStringAscii = obj.constBegin()[8];
    auto oCrStringUtf16 = obj.constBegin()[9];
    auto oCrTrue = obj.constBegin()[10];

    const QJsonArray arr{
        1.25,
        true,
        false,
        1234567890,
        QJsonValue::Null,
        "stringAscii",
        "utf16💔",
        QJsonArray{
            1,
            2,
            QJsonValue::Null,
            "foo",
            QJsonObject{{"bar", false}},
            true,
        },
        QJsonArray(),
        QJsonObject(),
        QJsonObject{
            {
                "nested",
                QJsonObject{
                    {"object", 1},
                },
            },
        },
    };

    auto aCrDouble = arr.constBegin()[0];
    auto aCrTrue = arr.constBegin()[1];
    auto aCrFalse = arr.constBegin()[2];
    auto aCrInt = arr.constBegin()[3];
    auto aCrNull = arr.constBegin()[4];
    auto aCrStringAscii = arr.constBegin()[5];
    auto aCrStringUtf16 = arr.constBegin()[6];
    auto aCrArray = arr.constBegin()[7];
    auto aCrEmptyArray = arr.constBegin()[8];
    auto aCrEmptyObject = arr.constBegin()[9];
    auto aCrObject = arr.constBegin()[10];

    return 0;  // break here
}
