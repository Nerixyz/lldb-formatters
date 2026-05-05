#include <QObject>
#include <QVariant>

int main()
{
    auto *root = new QObject;
    root->setObjectName("Root");

    auto *level1a = new QObject(root);
    auto *level1b = new QObject(root);

    auto *level2a = new QObject(level1a);

    level2a->setObjectName("object");
    level2a->setProperty("prop", false);
    level2a->setProperty("something", 123);

    // Ensure clang generates debug info for these types.
    QList<QByteArray> ensureBa;
    QList<QVariant> ensureV;

    return 0;  // break here
}
