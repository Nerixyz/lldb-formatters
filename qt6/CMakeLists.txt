find_package(Qt6 REQUIRED
    COMPONENTS
        Core
        Gui
        Widgets
)

qt_add_executable(qt6-app
	src/main.cpp

    src/ContainerTypes.hpp
    src/CoreTypes.hpp
)

target_link_libraries(qt6-app
    PRIVATE
        Qt6::Core
        Qt6::Gui
        Qt6::Widgets
)
