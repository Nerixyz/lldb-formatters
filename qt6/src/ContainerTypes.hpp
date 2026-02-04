#include <QtCore>

class ContainerTypes : public QObject
{
    Q_OBJECT

public:
    using QObject::QObject;

    QByteArrayList qByteArrayList = {
        "one",
        "two",
        "three",
    };
    QHash<int, QString> qHash = {
        {10, "one"},
        {20, "two"},
        {30, "three"},
    };
    QMap<int, QString> qMap = {
        {10, "one"},
        {20, "two"},
        {30, "three"},
    };
    QMultiHash<int, QString> qMultiHash = {
        {10, "one"},
        {10, "two"},
        {10, "three"},
        {20, "four"},
    };
    QSet<QString> qSet = {
        "one",
        "two",
        "three",
        "four",
    };
    QStringList qStringList = {
        "one",
        "two",
        "three",
    };
    QVarLengthArray<QString, 4> qVarLengthArray = {
        "one",
        "two",
        "three",
        "four",
    };
};
