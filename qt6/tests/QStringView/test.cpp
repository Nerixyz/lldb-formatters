#include <QStringView>

int main()
{
    QStringView defaultC;
    QStringView empty(u"");
    QStringView oneChar(u"a");
    QStringView emojis(u"🪐🪐🪐");
    auto notNullTerminated = QStringView(u"abc").sliced(0, 2);

    return 0;  // break here
}
