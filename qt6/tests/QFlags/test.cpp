#include <QFlags>

enum MyEnum {
    MyVal1 = 1,
    MyVal2 = 2,
    MyVal4 = 4,
    MyVal8 = 8,
};

enum class MyScopedEnum : uint64_t {
    Val1 = 1,
    Val52 = (1ULL << 52),
    Val53 = (1ULL << 53),
};

int main()
{
    using F1 = QFlags<MyEnum>;
    using F2 = QFlags<MyScopedEnum>;

    F1 zero1(0);
    F1 oneFlag1(MyVal1);
    F1 twoFlags1(MyVal1 | MyVal2);
    F1 diffFlag1(MyVal1 | MyVal2 | 0x80);

    F2 zero2(static_cast<MyScopedEnum>(0));
    F2 oneFlag2(MyScopedEnum::Val53);
    F2 twoFlags2{MyScopedEnum::Val1, MyScopedEnum::Val53};
    F2 diffFlag2{MyScopedEnum::Val1, MyScopedEnum::Val52,
                 static_cast<MyScopedEnum>(0x80)};

    return 0;  // break here
}
