#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>

int main()
{
    QJsonValue emptyDefault;

    QJsonValue emptyNull(QJsonValue::Null);
    QJsonValue emptyBool(QJsonValue::Bool);
    QJsonValue emptyDouble(QJsonValue::Double);
    QJsonValue emptyString(QJsonValue::String);
    QJsonValue emptyArray(QJsonValue::Array);
    QJsonValue emptyObject(QJsonValue::Object);
    QJsonValue emptyUndefined(QJsonValue::Undefined);

    QJsonValue vTrue(true);
    QJsonValue vFalse(false);
    QJsonValue vInt(42);
    QJsonValue vInt64(qint64(-42));
    QJsonValue vDouble(1.75);
    QJsonValue vStr("str");
    QJsonValue vStrUtf16("str🚧");
    QJsonValue vStrEmpty("");
    QJsonValue vArray(QJsonArray{
        1,
        2,
        "string",
        QJsonObject{{"object", true}},
    });
    QJsonValue vObject(QJsonObject{
        {"", false},
        {"a", "value"},
        {"b", QJsonArray{}},
        {"c", 123},
    });

    return 0;  // break here
}
