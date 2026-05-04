add_library(qt6tests INTERFACE)
target_include_directories(qt6tests INTERFACE "${CMAKE_CURRENT_LIST_DIR}/include")

create_python_tests(
    DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
    PREFIX qt6
    LIBRARIES
        qt6tests
        Qt6::Core
        Qt6::Gui
        Qt6::Widgets
    SCRIPTS
        "${CMAKE_CURRENT_LIST_DIR}/../scripts/qt6.py"
    TESTS
        QBasicAtomicInteger
        QByteArray
        QChar
        QCheckedInt
        QDate
        QDateTime
        QFlags
        QHash
        QJsonArray
        QJsonDocument
        QJsonObject
        QJsonValue
        QLine
        QLineF
        QList
        QMap
        QMultiHash
        QPoint
        QPointF
        QRect
        QRectF
        QSet
        QSize
        QSizeF
        QString
        QStringView
        QTime
        QUuid
        QVariant
        QVarLengthArray
)
