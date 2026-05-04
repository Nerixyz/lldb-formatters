#include <qbasicatomic.h>

int main()
{
    QBasicAtomicInt qBai(42);
    QBasicAtomicInteger<long long> qBall(-1234567890123);

    return 0;  // break here
}
