#include <QRect>

int main()
{
    QtPrivate::QCheckedIntegers::QCheckedInt<int> zero(0);
    QtPrivate::QCheckedIntegers::QCheckedInt<int> two(2);
    QtPrivate::QCheckedIntegers::QCheckedInt<int> negative(-2);
    QtPrivate::QCheckedIntegers::QCheckedInt<long long> llTwo(2);

    return 0;  // break here
}
