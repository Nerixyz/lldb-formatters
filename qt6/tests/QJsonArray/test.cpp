#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>

int main()
{
    QJsonArray empty;
    QJsonArray one{"key"};
    QJsonArray two{1, false};
    QJsonArray allTypes{
        1.25,
        true,
        false,
        1234567890,
        QJsonValue::Null,
        "stringAscii",
        "utf16💔",
        "",
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

    return 0;  // break here
}
