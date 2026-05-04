#include <qbasicatomic.h>

int main()
{
    int v = 42;
    QBasicAtomicPointer<int> intP(&v);
    QBasicAtomicPointer<void> voidP(&v);

    return 0;  // break here
}
