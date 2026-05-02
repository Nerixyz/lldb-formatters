#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonValue>

int main()
{
    QJsonDocument docEmpty;
    QJsonDocument docArray{QJsonArray{
        QStringLiteral("😃😃😃"),
        "foo",
        QLatin1String("foo"),
        "empty object->",
        QJsonObject{},
        "empty array ->",
        QJsonArray{},
        QJsonObject{
            {
                "abc",
                QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
            },
            {"def", QJsonArray{1, 2, true, false, 42.5}},
            {"foo", "bar"},
        },
        QJsonArray{
            "foo",
            "bar",
            QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
            QJsonArray{1, 2, true, false, 42.5},
        },
    }};
    QJsonDocument docObject{QJsonObject{
        {"an array",
         QJsonArray{
             "foo",
             "bar",
             QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
             QJsonArray{1, 2, true, false, 42.5},
         }},
        {"an object",
         QJsonObject{
             {"foo", "bar"},
             {
                 "abc",
                 QJsonObject{{"abc", "def"}, {"ghi", QJsonValue::Null}},
             },
             {"def", QJsonArray{1, 2, true, false, 42.5}},
         }},
        {"empty array ->", QJsonArray{}},
        {"empty object->", QJsonObject{}},
        {QLatin1String("foo"), QLatin1String("bar")},
        {QStringLiteral("😃😃😃"), "foo"},

    }};
    return 0;  // break here
}
