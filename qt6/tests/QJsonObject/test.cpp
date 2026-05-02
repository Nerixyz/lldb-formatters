#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>

int main()
{
    QJsonObject empty;
    QJsonObject one{{"key", "value"}};
    QJsonObject two{
        {"key", 1},
        {"value", 2},
    };
    QJsonObject allTypes{
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
        {"stringKeyUtf16🐛", ""},
        {"stringUtf16", "utf16💔"},
        {"true", true},
    };

    return 0;  // break here
}
