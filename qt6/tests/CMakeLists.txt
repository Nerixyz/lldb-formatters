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
        Qt6::Network
    SCRIPTS
        "${CMAKE_CURRENT_LIST_DIR}/../scripts/qt6.py"
    TESTS
        QBasicAtomicInteger
        QBasicAtomicPointer
        QByteArray
        QChar
        QCheckedInt
        QColor
        QDate
        QDateTime
        QDir
        QFile
        QFileInfo
        QFlags
        QGenericMatrix
        QHash
        QHostAddress
        QImage
        QJsonArray
        QJsonDocument
        QJsonObject
        QJsonValue
        QJsonValueConstRef
        QJsonValueRef
        QLine
        QLineF
        QList
        QMap
        QMultiHash
        QMultiMap
        QObject
        QPoint
        QPointF
        QPolygon
        QPolygonF
        QRect
        QRectF
        QSet
        QSize
        QSizeF
        QSizePolicy
        QSpan
        QString
        QStringView
        QTime
        QUrl
        QUuid
        QVariant
        QVarLengthArray
)

add_test(
    NAME "qt6-qfloat16-py"
    COMMAND
        "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_LIST_DIR}/../scripts/qfloat16.py"
)
