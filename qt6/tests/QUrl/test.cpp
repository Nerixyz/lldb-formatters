#include <QDebug>
#include <QUrl>

int main()
{
    QUrl empty;
    QUrl localFile = QUrl::fromLocalFile("my/local/file.txt");
    QUrl absLocalFile = QUrl::fromLocalFile("/my/local/file.txt");
    QUrl example("https://example.com");
    QUrl allComponents("https://user:pass@example.com:443/path?query#fragment");
    QUrl lessComponents("https://user@example.com:443/path#fragment");

    qDebug() << absLocalFile.toString();
    qDebug() << localFile.toString();
    qDebug() << example.toString();
    qDebug() << allComponents.toString();
    qDebug() << lessComponents.toString();

    return 0;  // break here
}
