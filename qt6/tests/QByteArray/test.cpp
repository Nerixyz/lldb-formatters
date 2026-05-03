#include <QByteArray>

int main()
{
    QByteArray null;
    QByteArray empty("");
    QByteArray oneChar("a");
    QByteArray emojis("🪐🪐🪐");
    auto notNullTerminated = QByteArray::fromRawData("abc", 2);

    return 0;  // break here
}
