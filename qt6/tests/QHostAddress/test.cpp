#include <QHostAddress>

int main()
{
    QHostAddress null;
    QHostAddress ipv4("123.5.231.36");
    QHostAddress ipv6("0123:4567:89ab:cdef:1234:5678:9abc:def0");
    ipv6.setScopeId("foobar");
    // Force clang to emit debug info for the type
    auto _unused = ipv6.protocol();

    return 0;  // break here
}
