#include "ContainerTypes.hpp"
#include "CoreTypes.hpp"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    auto coreTypes = CoreTypes();

    auto containerTypes = ContainerTypes();

    return 0;  // break here
}
