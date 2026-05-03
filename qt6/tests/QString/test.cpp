#include <QString>

int main()
{
    QString null;
    QString empty(u"");
    QString oneChar(u"a");
    QString emojis(u"🪐🪐🪐");
    auto notNullTerminated = QString::fromRawData(u"abc", 2);

    return 0;  // break here
}
