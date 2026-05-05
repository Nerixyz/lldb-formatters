# Qt 6

Most of the formatters and the test files are based on the Nativs files from Qt
([narnaud/natvis4qt](https://github.com/narnaud/natvis4qt/)).

## Types

All types are tested (see [`tests/`](./tests/)).

Types marked with 🧪 have improved formatting if debug info for private types is available.

- [x] `QBasicAtomicInteger<*>`
- [x] `QBasicAtomicPointer<*>`
- [x] `QBasicAtomicPointer<void>`
- [x] `QByteArray`
- [ ] `QCborArray` 🟡 (only the JSON subset)
- [ ] `QCborContainerPrivate` 🟡 (only the JSON subset)
- [ ] `QCborMap` 🟡 (only the JSON subset)
- [ ] `QCborValue` 🟡 (only the JSON subset)
- [x] `QCheckedInt<*>`
- [x] `QChar`
- [x] `QDate`
- [x] `QDateTime`
- [x] `QDir` (🧪)
- [x] `QFile` (🧪)
- [x] `QFileInfo` (🧪)
- [x] `QFlags<*>`
- [x] `QGenericMatrix<*,*,*>` (`QMatrixNxM`)
- [x] `QHash<*,*>`
- [x] `QHostAddress`
- [x] `QImage`
- [x] `QJsonArray`
- [x] `QJsonDocument`
- [x] `QJsonObject`
- [x] `QJsonValue`
- [x] `QJsonValueConstRef`
- [x] `QJsonValueRef`
- [x] `QLine`
- [x] `QLineF`
- [x] `QList<*>`
- [x] `QMap<*,*>`
- [x] `QMultiHash<*,*>`
- [ ] `QMultiMap<*,*>`
- [ ] `QObject`
- [ ] `QPair<*,*>`
- [ ] `QPixmap`
- [x] `QPoint`
- [x] `QPointF`
- [ ] `QPolygon`
- [ ] `QPolygonF`
- [ ] `QPropertyData<*>`
- [ ] `QQuickItem`
- [ ] `QQuickItemPrivate`
- [x] `QRect`
- [x] `QRectF`
- [x] `QSet<*>`
- [x] `QSize`
- [x] `QSizeF`
- [ ] `QSizePolicy`
- [ ] `QSpan<*>`
- [ ] `QSpecialInteger<*>`
- [x] `QString`
- [ ] `QStringRef`
- [x] `QStringView`
- [x] `QTime`
- [ ] `QUrl`
- [x] `QUuid`
- [x] `QVarLengthArray<*,*>`
- [x] `QVariant`
  > [!WARNING]
  > While the primitive types like `int`, `QString`, or `QVariantMap` are supported, user-defined types that use templates might not work.
  > The formatter looks up the type by the name embedded in the `QMetaType`. If that doesn't return any name, a `void*` is shown. Non-templates should work without problems.
- [ ] `QVector2D`
- [ ] `QVector3D`
- [ ] `QVector4D`
- [ ] `QVector<*>`
