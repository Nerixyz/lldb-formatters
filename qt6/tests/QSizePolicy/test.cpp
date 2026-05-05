#include <QSizePolicy>

int main()
{
    QSizePolicy exIg(QSizePolicy::Expanding, QSizePolicy::Ignored);
    exIg.setWidthForHeight(true);
    QSizePolicy hfw(QSizePolicy::Preferred, QSizePolicy::Maximum,
                    QSizePolicy::CheckBox);
    hfw.setHeightForWidth(true);
    hfw.setHorizontalStretch(3);
    hfw.setVerticalStretch(4);

    return 0;  // break here
}
