#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>

int main()
{
    QJsonObject obj{
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

    auto oit = obj.begin();
    auto oRArray = oit[0];
    auto oRDouble = oit[1];
    auto oREmptyArray = oit[2];
    auto oREmptyObject = oit[3];
    auto oRFalse = oit[4];
    auto oRInt = oit[5];
    auto oRNull = oit[6];
    auto oRObject = oit[7];
    auto oRStringAscii = oit[8];
    auto oRStringUtf16 = oit[9];
    auto oRTrue = oit[10];

    QJsonArray arr{
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

    auto ait = arr.begin();
    auto aRDouble = ait[0];
    auto aRTrue = ait[1];
    auto aRFalse = ait[2];
    auto aRInt = ait[3];
    auto aRNull = ait[4];
    auto aRStringAscii = ait[5];
    auto aRStringUtf16 = ait[6];
    auto aRArray = ait[7];
    auto aREmptyArray = ait[8];
    auto aREmptyObject = ait[9];
    auto aRObject = ait[10];

    return 0;  // break here
}
