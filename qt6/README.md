# Qt 6

Most of the formatters and the test files are based on the Nativs files from Qt
([narnaud/natvis4qt](https://github.com/narnaud/natvis4qt/)).

## Types

All types are tested (see [`tests/`](./tests/)).

- [x] `QBasicAtomicInteger<*>`
- [ ] `QBasicAtomicPointer<*>`
- [ ] `QBasicAtomicPointer<void>`
- [x] `QByteArray`
- [ ] `QCborArray` 🟡 (only the JSON subset)
- [ ] `QCborContainerPrivate` 🟡 (only the JSON subset)
- [ ] `QCborMap` 🟡 (only the JSON subset)
- [ ] `QCborValue` 🟡 (only the JSON subset)
- [x] `QCheckedInt<*>`
- [x] `QChar`
- [x] `QDate`
- [x] `QDateTime`
- [ ] `QDir`
- [ ] `QFile`
- [ ] `QFileInfo`
- [x] `QFlags<*>`
- [ ] `QGenericMatrix<*,*,*>`
- [x] `QHash<*,*>`
- [ ] `QHostAddress`
- [ ] `QImage`
- [x] `QJsonArray`
- [x] `QJsonDocument`
- [x] `QJsonObject`
- [x] `QJsonValue`
- [ ] `QJsonValueConstRef`
- [ ] `QJsonValueRef`
- [ ] `QLine`
- [ ] `QLineF`
- [x] `QList<*>`
- [x] `QMap<*,*>`
- [ ] `QMatrix2x2`
- [ ] `QMatrix2x3`
- [ ] `QMatrix2x4`
- [ ] `QMatrix3x2`
- [ ] `QMatrix3x3`
- [ ] `QMatrix3x4`
- [ ] `QMatrix4x2`
- [ ] `QMatrix4x3`
- [ ] `QMatrix4x4`
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
