import lldb
from lldb import (
    SBValue,
    SBType,
    SBTarget,
    SBData,
    SBError,
    SBDebugger,
    SBProcess,
)
from typing import Callable, Optional, Union
from qt_constants import (
    QDateTimeConstants,
    QHashConstants,
    QCborValueType,
    QtCborElementValueFlag,
    QCBORVALUE_NULL,
    QCBORVALUE_UNDEFINED,
)
import datetime
import re

MIN_LLDB_VERSION = (20, 0, 0)

UNICODE_STR_ARRAY_IS_LIMITED = False
"""charN_t[N] limits the extraction to N characters."""


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    dbg.HandleCommand("type category define -e qt -l c++")

    global UNICODE_STR_ARRAY_IS_LIMITED
    UNICODE_STR_ARRAY_IS_LIMITED = _get_lldb_version(dbg) >= (23, 0, 0)

    def add_summary(
        type_name: str,
        *,
        regex: Optional[str] = None,
        other_names: list[str] = [],
    ):
        type_names = other_names + [type_name]
        cmd = f"type summary add -w qt -F {__name__}.{type_name}SummaryProvider "
        if regex:
            cmd += f' -x "{regex}"'
        else:
            cmd += " ".join(map(lambda it: f'"{it}"', type_names))
        dbg.HandleCommand(cmd)

    def add_synthetic(
        name: str,
        *,
        regex: Optional[str] = None,
        other_names: list[str] = [],
    ):
        cmd = f"type synthetic add -w qt -l {__name__}.{name}SyntheticProvider"
        if regex:
            cmd += f' -x "{regex}"'
        else:
            cmd += f' "{name}" ' + " ".join(map(lambda it: f'"{it}"', other_names))
        dbg.HandleCommand(cmd)

    add_summary("QString")
    add_summary("QStringView")
    add_summary("QUuid")
    add_summary("QRect")
    add_summary("QTime")
    add_summary("QDate")
    add_summary("QDateTime")
    add_summary("QByteArray")
    add_summary("QCborValue")
    add_summary("QJsonDocument")
    add_summary("QJsonValue")
    add_summary("QJsonValueConstRef", other_names=["QJsonValueRef"])
    add_summary("QVariant")
    add_summary("QDir")
    add_summary("QFile")
    add_summary("QFileInfo")
    add_summary("QHostAddress")
    add_summary("QImage")
    add_summary("QObject")
    add_summary("QUrl")
    add_summary("QGenericMatrix", regex="^QGenericMatrix<.*>$")
    _add_summary_string(dbg, ["QPoint", "QPointF"], "(x: ${var.xp}, y: ${var.yp})")
    _add_summary_string(dbg, ["QPolygon", "QPolygonF"], "size=${svar%#}")
    _add_summary_string(dbg, "^QList<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^Q(Multi)?Hash<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^Q(Map|Set)<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^QMultiMap<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^QVarLengthArray<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^QSpan<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(
        dbg, "^QHashPrivate::MultiNodeChain<.*>$", "size=${svar%#}", regex=True
    )
    _add_summary_string(
        dbg, "^QHashPrivate::Node<.*>$", "(${var.key}, ${var.value})", regex=True
    )
    _add_summary_string(
        dbg, "^QHashPrivate::Node<.*, QHashDummyValue>$", "${var.key}", regex=True
    )
    _add_summary_string(dbg, "^QHashPrivate::MultiNode<.*>$", "${var.key}", regex=True)
    _add_summary_string(
        dbg,
        ["QLine", "QLineF"],
        "(${var.pt1.xp}, ${var.pt1.yp}) -> (${var.pt2.xp}, ${var.pt2.yp})",
    )
    _add_summary_string(
        dbg, ["QSize", "QSizeF"], "(width: ${var.wd}, height: ${var.ht})"
    )
    _add_summary_string(
        dbg,
        "QRectF",
        "(x: ${var.xp}, y: ${var.yp}, width: ${var.w}, height: ${var.h})",
    )
    _add_summary_string(
        dbg,
        "QSizePolicy",
        "horizontal=${svar.HorizontalPolicy}, vertical=${svar.VerticalPolicy}",
    )
    _add_summary_string(dbg, "QChar", "${var.ucs}")
    _add_summary_string(dbg, ["QJsonObject", "QCborMap"], "\\{ size=${svar%#} \\}")
    _add_summary_string(dbg, ["QJsonArray", "QCborArray"], "[ size=${svar%#} ]")
    _add_summary_string(dbg, "^QPropertyData<.*>$", "${var.val}", regex=True)
    _add_summary_string(dbg, "^QObjectCompatProperty<.*>$", "${var.val}", regex=True)

    add_synthetic("QCheckedInt", regex="^QtPrivate::QCheckedIntegers::QCheckedInt<.*>$")
    add_synthetic("QBasicAtomicInteger", regex="^QBasicAtomic(Integer|Pointer)<.*>$")
    add_synthetic("QGenericMatrix", regex="^QGenericMatrix<.*>$")
    add_synthetic("QList", regex="^QList<.*>$")
    add_synthetic("QSize", other_names=["QSizeF"])
    add_synthetic("QRect")
    add_synthetic("QRectF")
    add_synthetic("QString")
    add_synthetic("QStringView")
    add_synthetic("QTime")
    add_synthetic("QDate")
    add_synthetic("QDateTime")
    add_synthetic("QChar")
    add_synthetic("QByteArray")
    add_synthetic("QHash", regex="^Q(Multi)?Hash<.*>$")
    add_synthetic("QHashPrivateMultiChain", regex="^QHashPrivate::MultiNodeChain<.*>$")
    add_synthetic("QSet", regex="^QSet<.*>$")
    add_synthetic("QMap", regex="^QMap<.*>$")
    add_synthetic("QMultiMap", regex="^QMultiMap<.*>$")
    add_synthetic("QVarLengthArray", regex="^QVarLengthArray<.*>$")
    add_synthetic("QFlags", regex="^QFlags<.*>$")
    add_synthetic("QJsonDocument")
    add_synthetic("QCborMap", other_names=["QJsonObject"])
    add_synthetic("QCborArray", other_names=["QJsonArray"])
    add_synthetic("QJsonValue")
    add_synthetic("QJsonValueConstRef", other_names=["QJsonValueRef"])
    add_synthetic("QCborValue")
    add_synthetic("QVariant")
    add_synthetic("QDir")
    add_synthetic("QFile")
    add_synthetic("QFileInfo")
    add_synthetic("QHostAddress")
    add_synthetic("QImage")
    add_synthetic("QObject")
    add_synthetic("QPolygon", other_names=["QPolygonF"])
    add_synthetic("QSizePolicy")
    add_synthetic("QSpan", regex="^QSpan<.*>$")
    add_synthetic("QUrl")


def _add_summary_string(
    dbg: SBDebugger,
    type_names: Union[str, list[str]],
    summary: str,
    *,
    regex=False,
    no_value=False,
):
    if isinstance(type_names, str):
        type_names = [type_names]
    cmd = f"type summary add -w qt --summary-string '{summary}' {'-x' if regex else ''} {'-v' if no_value else ''} "
    cmd += " ".join(map(lambda it: f'"{it}"', type_names))
    dbg.HandleCommand(cmd)


def _get_lldb_version(dbg: SBDebugger) -> tuple[int, int, int]:
    s = dbg.GetVersionString()
    m = re.search(r"\bversion (\d+)\.(\d+)\.(\d+)", s)
    if not m:
        return (20, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def QStringSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    return _qarraydata_summary(valobj, lldb.eBasicTypeChar16, "u")


def QByteArraySummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    return _qarraydata_summary(valobj, lldb.eBasicTypeChar, "")


def _qarraydata_summary(valobj: SBValue, ty, prefix: str):
    d_obj: SBValue = valobj.GetNonSyntheticValue().GetChildMemberWithName("d")
    ptr_obj: SBValue = d_obj.GetChildMemberWithName("ptr")
    size = d_obj.GetChildMemberWithName("size").GetValueAsUnsigned()
    if not ptr_obj.IsValid():
        return None
    if ptr_obj.GetValueAsUnsigned() == 0:
        return prefix + '"" (null)'
    if size == 0:
        return prefix + '""'

    if ty == lldb.eBasicTypeChar16:
        return _make_utf16_valobj(ptr_obj, size).GetSummary()
    array_type = valobj.target.GetBasicType(ty).GetArrayType(size)
    return ptr_obj.deref.Cast(array_type).GetSummary()


def _make_utf16_valobj(ptr: SBValue, size: int):
    tgt = ptr.GetTarget()
    if UNICODE_STR_ARRAY_IS_LIMITED:
        ty = tgt.GetBasicType(lldb.eBasicTypeChar16).GetArrayType(size)
        return ptr.Dereference().Cast(ty)

    limit_obj = tgt.GetDebugger().GetSetting("target.max-string-summary-length")
    if limit_obj:
        size = min(size, limit_obj.GetUnsignedIntegerValue())

    process = ptr.GetProcess()
    s = process.ReadMemory(ptr.GetValueAsAddress(), size * 2, SBError()) or bytes()
    try:
        s = s.decode("utf-16le").encode("utf-8")
    except BaseException as _:
        pass
    data = SBData()
    data.SetData(SBError(), s, lldb.eByteOrderLittle, 8)
    ty = tgt.GetBasicType(lldb.eBasicTypeChar).GetArrayType(len(s))
    return ptr.CreateValueFromData("", data, ty)


def QStringViewSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    valobj = valobj.GetNonSyntheticValue()
    ptr: SBValue = valobj.GetChildMemberWithName("m_data")
    size = valobj.GetChildMemberWithName("m_size").GetValueAsUnsigned()
    if size == 0:
        return 'u""'
    return _make_utf16_valobj(ptr, size).GetSummary()


def QUuidSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    data1 = valobj.GetChildMemberWithName("data1").unsigned
    data2 = valobj.GetChildMemberWithName("data2").unsigned
    data3 = valobj.GetChildMemberWithName("data3").unsigned
    data4 = valobj.GetChildMemberWithName("data4").GetData()
    e = SBError()
    data4 = data4.ReadRawData(e, 0, 8)
    if e.Fail() or data4 is None:
        return None
    return f"{data1:08x}-{data2:04x}-{data3:04x}-{data4[0]:02x}{data4[1]:02x}-{data4[2]:02x}{data4[3]:02x}{data4[4]:02x}{data4[5]:02x}{data4[6]:02x}{data4[7]:02x}"


def QRectSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    valobj = valobj.GetNonSyntheticValue()
    x1 = _prefer_synthetic(valobj.GetChildMemberWithName("x1")).signed
    x2 = _prefer_synthetic(valobj.GetChildMemberWithName("x2")).signed
    y1 = _prefer_synthetic(valobj.GetChildMemberWithName("y1")).signed
    y2 = _prefer_synthetic(valobj.GetChildMemberWithName("y2")).signed
    return f"(x: {x1}, y: {y1}, width: {x2 - x1 + 1}, height: {y2 - y1 + 1})"


def QTimeSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    valobj = valobj.GetNonSyntheticValue()
    time = _QTime(valobj.GetChildMemberWithName("mds").signed)
    if time.null():
        return "(null)"
    if not time.valid():
        return "(invalid)"
    h, m, s, ms = (time.hour(), time.minute(), time.second(), time.msec())
    if ms == 0:
        if s == 0:
            return f"{h:02}:{m:02}"
        return f"{h:02}:{m:02}:{s:02}"
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"


def QDateSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    valobj = valobj.GetNonSyntheticValue()
    date = _QDate(valobj.GetChildMemberWithName("jd").GetValueAsSigned())
    if not date.valid:
        return "(invalid)"
    return f"{date.year}-{date.month:02}-{date.day:02}"


def QDateTimeSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    n_children = valobj.GetNumChildren()
    if n_children == 0:
        return "(invalid)"
    ms = valobj.GetChildMemberWithName("ms").signed
    offset_obj = valobj.GetChildMemberWithName("offset-sec")
    is_local = not offset_obj.IsValid()
    if is_local:
        tz = datetime.UTC
    else:
        tz = datetime.timezone(datetime.timedelta(seconds=offset_obj.signed))
    dt = datetime.datetime.fromtimestamp(0, tz) + datetime.timedelta(
        seconds=ms / 1000.0
    )
    ms = dt.microsecond // 1000
    ms_part = f".{ms:03}" if ms != 0 else ""
    if is_local:
        return dt.strftime(f"%Y-%m-%d %X{ms_part} (Local)")
    return dt.strftime(f"%Y-%m-%d %X{ms_part} %Z")


def get_sizet_ptr(target: SBTarget) -> SBType:
    return target.GetBasicType(lldb.eBasicTypeLongLong).GetPointerType()


def QCborValueSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    raw: SBValue = valobj.GetNonSyntheticValue()
    ty_val = raw.GetChildMemberWithName("t").GetValueAsUnsigned()
    if ty_val == QCborValueType.Integer:
        return ""  # Use synthetic value
    elif ty_val == QCborValueType.Double:
        return ""
    elif ty_val == QCborValueType.String:
        return valobj.GetChildAtIndex(
            QCborValueSyntheticProvider.VALUE_INDEX
        ).GetSummary()
    elif ty_val == QCborValueType.Array:
        return f"[ size={valobj.GetNumChildren()} ]"
    elif ty_val == QCborValueType.Map:
        return f"{{ size={valobj.GetNumChildren()} }}"
    elif ty_val == QCborValueType.CFalse:
        return ""
    elif ty_val == QCborValueType.CTrue:
        return ""
    elif ty_val == QCborValueType.Null:
        return "null"
    elif ty_val == QCborValueType.Undefined:
        return "undefined"
    else:
        return f"(unknown type {ty_val})"


def QJsonDocumentSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    raw: SBValue = valobj.GetNonSyntheticValue()
    void_ptr = valobj.GetTarget().GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
    d_ptr: SBValue = raw.GetChildAtIndex(0).Cast(void_ptr)
    if d_ptr.GetValueAsAddress() == 0:
        return "null"
    size = valobj.GetNumChildren()
    ty = valobj.GetChildAtIndex(QCborValueSyntheticProvider.TYPE_INDEX)
    ty_val = ty.GetValueAsUnsigned()
    if ty_val == QCborValueType.Map:
        return f"{{ size={size} }}"
    elif ty_val == QCborValueType.Array:
        return f"[ size={size} ]"
    else:
        return "(invalid)"


def QJsonValueSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    v: SBValue = valobj.GetNonSyntheticValue().GetChildAtIndex(0).GetSyntheticValue()
    s = v.GetSummary()
    if s is None:
        return ""
    return s


def QJsonValueConstRefSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    v: SBValue = valobj.GetChildAtIndex(QJsonValueConstRefSyntheticProvider.VALUE_IDX)
    s = v.GetSummary()
    if s is None:
        return ""
    return s


class _FirstChildSyntheticProvider(lldb.SBSyntheticValueProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj

    def update(self):
        self._val = self._backend.GetChildAtIndex(0)
        return False

    def get_value(self):
        return self._val


QCheckedIntSyntheticProvider = _FirstChildSyntheticProvider
QCharSyntheticProvider = _FirstChildSyntheticProvider


class QFlagsSyntheticProvider(lldb.SBSyntheticValueProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj
        self._enum_type = valobj.type.FindDirectNestedType("enum_type")

    def update(self):
        self._val = self._backend.GetChildMemberWithName("i").Cast(self._enum_type)
        return False

    def num_children(self):
        return 1

    def get_child_at_index(self, idx):
        return self._backend.GetChildMemberWithName("i").Clone("[int]")

    def has_children(self):
        return True

    def get_value(self):
        return self._val


class QBasicAtomicIntegerSyntheticProvider(lldb.SBSyntheticValueProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj

    def update(self):
        self._val = (
            self._backend.GetChildAtIndex(0).GetSyntheticValue().GetChildAtIndex(0)
        )
        return False

    def get_value(self):
        return self._val


class _ExpandingSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj

    def update(self):
        self._val = self._get_value(self._backend)
        return False

    def _get_value(self, valobj: SBValue) -> SBValue:
        raise NotImplementedError()

    def num_children(self):
        return self._val.GetNumChildren()

    def get_child_index(self, name: str):
        return self._val.GetChildMemberWithName(name)

    def get_child_at_index(self, idx: int):
        return self._val.GetChildAtIndex(idx)

    def has_children(self):
        return True


class QPolygonSyntheticProvider(_ExpandingSyntheticProvider):
    def _get_value(self, valobj: SBValue) -> SBValue:
        return valobj.GetChildAtIndex(0).GetSyntheticValue()  # QList<QPoint>


class QMapSyntheticProvider(_ExpandingSyntheticProvider):
    def _get_value(self, valobj: SBValue) -> SBValue:
        return (
            valobj.GetChildAtIndex(0)
            .GetChildAtIndex(0)
            .GetChildAtIndex(0)
            .GetChildMemberWithName("m")
            .GetSyntheticValue()
        )


class QMultiMapSyntheticProvider(_ExpandingSyntheticProvider):
    def _get_value(self, valobj: SBValue) -> SBValue:
        return (
            valobj.GetChildAtIndex(0)
            .GetChildAtIndex(0)
            .GetChildAtIndex(0)
            .GetChildMemberWithName("m")
            .GetSyntheticValue()
        )


class QSetSyntheticProvider(_ExpandingSyntheticProvider):
    def _get_value(self, valobj: SBValue) -> SBValue:
        return valobj.GetChildAtIndex(0).GetSyntheticValue()


class QJsonDocumentSyntheticProvider(_ExpandingSyntheticProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._cbor_ptr = valobj.GetTarget().FindFirstType("QCborValue").GetPointerType()

    def _get_value(self, valobj: SBValue) -> SBValue:
        d_ptr: SBValue = valobj.GetChildAtIndex(0).Cast(self._cbor_ptr)
        if d_ptr.GetValueAsAddress() == 0:
            return SBValue()
        return d_ptr.Dereference().GetSyntheticValue()


class _ArraySyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj
        self._size = 0
        self._val: Optional[SBValue] = None

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return _numeric_index(name)

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self._size or not self._val:
            return None
        return self._val.GetChildAtIndex(idx).Clone(f"[{idx}]")

    def has_children(self):
        return self._val is not None

    def update(self):
        ptr, size = self._pointer_and_size(self._backend)
        self._size = size
        array_type = self._array_type(ptr).GetArrayType(self._size)
        self._val = ptr.deref.Cast(array_type)
        return False

    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        raise NotImplementedError()

    def _array_type(self, valobj: SBValue):
        raise NotImplementedError()


class QStringSyntheticProvider(_ArraySyntheticProvider):
    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        d_obj: SBValue = valobj.GetChildMemberWithName("d")
        ptr_obj: SBValue = d_obj.GetChildMemberWithName("ptr")
        size = d_obj.GetChildMemberWithName("size").unsigned
        return (ptr_obj, size)

    def _array_type(self, valobj: SBValue):
        return valobj.target.GetBasicType(lldb.eBasicTypeChar16)


class QSpanSyntheticProvider(_ArraySyntheticProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        f = (
            valobj.GetType()
            .GetDirectBaseClassAtIndex(0)
            .GetType()
            .GetStaticFieldWithName("m_size")
        )
        if f:
            self._csize = f.GetConstantValue(valobj.GetTarget()).GetValueAsUnsigned()
        else:
            self._csize = None

    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        ptr: SBValue = valobj.GetChildMemberWithName("m_data")
        if self._csize is not None:
            return (ptr, self._csize)
        return (ptr, valobj.GetChildMemberWithName("m_size").GetValueAsUnsigned())

    def _array_type(self, valobj: SBValue):
        return valobj.type.GetPointeeType()


class QByteArraySyntheticProvider(_ArraySyntheticProvider):
    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        d_obj: SBValue = valobj.GetChildMemberWithName("d")
        ptr_obj: SBValue = d_obj.GetChildMemberWithName("ptr")
        size = d_obj.GetChildMemberWithName("size").unsigned
        return (ptr_obj, size)

    def _array_type(self, valobj: SBValue):
        return valobj.target.GetBasicType(lldb.eBasicTypeChar16)


class QStringViewSyntheticProvider(_ArraySyntheticProvider):
    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        return (
            valobj.GetChildMemberWithName("m_data"),
            valobj.GetChildMemberWithName("m_size").unsigned,
        )

    def _array_type(self, valobj: SBValue):
        return valobj.target.GetBasicType(lldb.eBasicTypeChar16)


class QListSyntheticProvider(_ArraySyntheticProvider):
    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        d_obj: SBValue = valobj.GetChildMemberWithName("d")
        ptr_obj: SBValue = d_obj.GetChildMemberWithName("ptr")
        size = d_obj.GetChildMemberWithName("size").unsigned
        return (ptr_obj, size)

    def _array_type(self, valobj: SBValue):
        return valobj.type.GetPointeeType()


class QVarLengthArraySyntheticProvider(_ArraySyntheticProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._arr_type = valobj.type.FindDirectNestedType(
            "value_type"
        ).GetTypedefedType()

    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        ptr = valobj.GetChildMemberWithName("ptr").Cast(self._arr_type.GetPointerType())
        size = valobj.GetChildMemberWithName("s").unsigned
        return (ptr, size)

    def _array_type(self, valobj: SBValue):
        return self._arr_type


class _DispatchedSynthetic:
    items: list[tuple[str, Union[Callable, str]]] = []

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._cache: dict[int, SBValue] = {}

    def num_children(self):
        return len(self.items)

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]")
        for i, (k, v) in enumerate(self.items):
            if name == k:
                return i
        return None

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= len(self.items):
            return None
        existing = self._cache.get(idx)
        if existing is not None:
            return existing
        v = self._get_at_index(idx)
        self._cache[idx] = SBValue() if v is None else v
        return v

    def _get_at_index(self, idx: int):
        key, item = self.items[idx]
        if isinstance(item, str):
            v = self._valobj.GetChildMemberWithName(item)
        else:
            v = item(self, self._valobj)

        if v is not None:
            return v.Clone(f"[{key}]")

    def update(self):
        self._cache.clear()
        return False

    def has_children(self):
        return len(self.items) > 0


class QSizeSyntheticProvider(_DispatchedSynthetic):
    items = [
        ("width", "wd"),
        ("height", "ht"),
    ]


class QRectSyntheticProvider(_DispatchedSynthetic):
    def _get_width(self, valobj: SBValue):
        x1 = _prefer_synthetic(valobj.GetChildMemberWithName("x1")).signed
        x2 = _prefer_synthetic(valobj.GetChildMemberWithName("x2")).signed
        return _valobj_from_signed(valobj, x2 - x1 + 1)

    def _get_height(self, valobj: SBValue):
        y1 = _prefer_synthetic(valobj.GetChildMemberWithName("y1")).signed
        y2 = _prefer_synthetic(valobj.GetChildMemberWithName("y2")).signed
        return _valobj_from_signed(valobj, y2 - y1 + 1)

    items = [
        ("x", "x1"),
        ("y", "y1"),
        ("width", _get_width),
        ("height", _get_height),
    ]


class QRectFSyntheticProvider(_DispatchedSynthetic):
    items = [
        ("x", "xp"),
        ("y", "yp"),
        ("width", "w"),
        ("height", "h"),
    ]


class QSizePolicySyntheticProvider(_DispatchedSynthetic):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._policy = valobj.GetTarget().FindFirstType("QSizePolicy::Policy")
        self._control = valobj.GetTarget().FindFirstType("QSizePolicy::ControlType")

    def update(self):
        self._bits: SBValue = self._valobj.GetChildAtIndex(0).GetChildMemberWithName(
            "bits"
        )
        return super().update()

    def _get_hstretch(self, valobj: SBValue):
        v = self._bits.GetChildMemberWithName("horStretch").GetValueAsUnsigned()
        return _valobj_from_signed(self._bits, v)

    def _get_vstretch(self, valobj: SBValue):
        v = self._bits.GetChildMemberWithName("verStretch").GetValueAsUnsigned()
        return _valobj_from_signed(self._bits, v)

    def _get_hpolicy(self, valobj: SBValue):
        v = self._bits.GetChildMemberWithName("horPolicy").GetValueAsUnsigned()
        return _valobj_from_signed(self._bits, v).Cast(self._policy)

    def _get_vpolicy(self, valobj: SBValue):
        v = self._bits.GetChildMemberWithName("verPolicy").GetValueAsUnsigned()
        return _valobj_from_signed(self._bits, v).Cast(self._policy)

    def _get_hfw(self, valobj: SBValue):
        v = self._bits.GetChildMemberWithName("hfw").GetValueAsUnsigned()
        return valobj.CreateBoolValue("", v != 0)

    def _get_wfh(self, valobj: SBValue):
        v = self._bits.GetChildMemberWithName("wfh").GetValueAsUnsigned()
        return valobj.CreateBoolValue("", v != 0)

    def _get_control(self, valobj: SBValue):
        v = self._bits.GetChildMemberWithName("ctype").GetValueAsUnsigned()
        return _valobj_from_signed(self._bits, 1 << v).Cast(self._control)

    items = [
        ("HorizontalPolicy", _get_hpolicy),
        ("VerticalPolicy", _get_vpolicy),
        ("HorizontalStretch", _get_hstretch),
        ("VerticalStretch", _get_vstretch),
        ("ControlType", _get_control),
        ("HeightForWidth", _get_hfw),
        ("WidthForHeight", _get_wfh),
    ]


class _QTime:
    def __init__(self, mds: int):
        self._mds = mds
        self._ds = max(0, self._mds)

    def valid(self) -> bool:
        return self._mds > -1 and self._mds < QDateTimeConstants.MSECS_PER_DAY

    def null(self) -> bool:
        return self._mds == -1

    def hour(self):
        return self._ds // QDateTimeConstants.MSECS_PER_HOUR

    def minute(self):
        return (
            self._ds % QDateTimeConstants.MSECS_PER_HOUR
        ) // QDateTimeConstants.MSECS_PER_MIN

    def second(self):
        return (
            self._ds // QDateTimeConstants.MSECS_PER_SEC
        ) % QDateTimeConstants.SECS_PER_MIN

    def msec(self):
        return self._ds % QDateTimeConstants.MSECS_PER_SEC


class _QDate:
    def __init__(self, jd: int):
        self.valid = (
            jd >= QDateTimeConstants.JULIAN_DAY_MIN
            and jd <= QDateTimeConstants.JULIAN_DAY_MAX
        )
        if not self.valid:
            return

        # QGregorianCalendar::partsFromJulian:
        # https://github.com/qt/qtbase/blob/3814e28f00b4d551b4691f40431c0d324e88e55d/src/corelib/time/qgregoriancalendar.cpp#L247-L266

        dayNumber = jd - QDateTimeConstants.BASE_JD
        century = (4 * dayNumber - 1) // QDateTimeConstants.FOUR_CENTURIES
        dayInCentury = dayNumber - (QDateTimeConstants.FOUR_CENTURIES * century) // 4

        yearInCentury = (4 * dayInCentury - 1) // QDateTimeConstants.FOUR_YEARS
        dayInYear = dayInCentury - (QDateTimeConstants.FOUR_YEARS * yearInCentury) // 4
        m = (5 * dayInYear - 3) // QDateTimeConstants.FIVE_MONTHS
        # That m is a month adjusted to March = 0, with Jan = 10, Feb = 11 in the previous year.
        yearOffset = 0 if m < 10 else 1

        self.year = 100 * century + yearInCentury + yearOffset
        if self.year <= 0:
            self.year -= 1
        self.month = m + 3 - 12 * yearOffset
        self.day = dayInYear - (QDateTimeConstants.FIVE_MONTHS * m + 2) // 5


class QTimeSyntheticProvider(_DispatchedSynthetic):
    def update(self):
        self._time = _QTime(self._valobj.GetChildMemberWithName("mds").signed)
        self._valid = self._time.valid()
        return super().update()

    def num_children(self):
        if not self._valid:
            return 0
        return super().num_children()

    def has_children(self):
        return self._valid

    def _hour(self, v):
        return _valobj_from_signed(v, self._time.hour())

    def _minute(self, v):
        return _valobj_from_signed(v, self._time.minute())

    def _second(self, v):
        return _valobj_from_signed(v, self._time.second())

    def _msec(self, v):
        return _valobj_from_signed(v, self._time.msec())

    items = [
        ("hour", _hour),
        ("minute", _minute),
        ("second", _second),
        ("millisecond", _msec),
    ]


class QDateSyntheticProvider(_DispatchedSynthetic):
    def update(self):
        self._date = _QDate(self._valobj.GetChildMemberWithName("jd").signed)
        return super().update()

    def num_children(self):
        if not self._date.valid:
            return 0
        return super().num_children()

    def has_children(self):
        return self._date.valid

    def _year(self, v):
        return _valobj_from_signed(v, self._date.year)

    def _month(self, v):
        return _valobj_from_signed(v, self._date.month)

    def _day(self, v):
        return _valobj_from_signed(v, self._date.day)

    items = [
        ("year", _year),
        ("month", _month),
        ("day", _day),
    ]


class QDateTimeSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._date = None

    def update(self):
        data = _qdatetime_data(self._valobj)
        if data is None:
            self._date = None
        else:
            dt, is_local = data
            self._date = dt
            self._utcdate = round(dt.astimezone(datetime.UTC).timestamp() * 1000)
            self._is_local = is_local
        return False

    def num_children(self):
        if self._date is None:
            return 0
        return 1 if self._is_local else 2

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]")
        if name == "ms":
            return 0
        elif name == "offset-sec":
            return 1
        return None

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self.num_children():
            return None
        if idx == 0:
            return _valobj_from_signed(self._valobj, self._utcdate, "[ms]")
        elif idx == 1:
            assert self._date is not None
            off = self._date.utcoffset()
            assert off is not None
            return _valobj_from_signed(
                self._valobj, int(off.total_seconds()), "[offset-sec]"
            )

    def has_children(self):
        return True


class QHashSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._size = 0
        self._num_buckets = 0
        self._last_bucket: Optional[tuple[int, int]] = None
        self._valobj = valobj

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return _numeric_index(name)

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self._size:
            return None
        cur_idx = -1
        cur_bucket = 0
        if self._last_bucket is not None and self._last_bucket[0] <= idx:
            cur_idx = self._last_bucket[0] - 1
            cur_bucket = self._last_bucket[1]

        proc: SBProcess = self._valobj.process
        err = SBError()
        span_obj = None
        # go through each span
        while cur_idx != idx and cur_bucket < self._num_buckets:
            span_idx = cur_bucket >> QHashConstants.SPAN_SHIFT
            last_bucket = min(
                (span_idx + 1) << QHashConstants.SPAN_SHIFT, self._num_buckets
            )
            span_obj = self._spans.CreateChildAtOffset(
                "", span_idx * self._span_size, self._span_type
            )
            offsets = span_obj.GetChildAtIndex(self._span_offsets_idx)
            buf = proc.ReadMemory(offsets.load_addr, QHashConstants.N_ENTRIES, err)
            if err.Fail() or buf is None:
                return None
            # go through each entry
            while cur_bucket < last_bucket:
                el_idx = cur_bucket & QHashConstants.ELEMENT_MASK
                if buf[el_idx] != 0xFF:
                    cur_idx += 1
                    offset = buf[el_idx]
                    if cur_idx == idx:
                        break
                cur_bucket += 1
        if cur_idx != idx or not span_obj:
            return None  # nothing found
        self._last_bucket = (idx, cur_bucket)

        entries_obj = span_obj.GetChildAtIndex(self._span_entries_idx)
        entry_obj = entries_obj.CreateChildAtOffset(
            "", offset * self._entry_size, self._entry_type
        )
        return (
            entry_obj.GetChildMemberWithName("storage")
            .GetChildAtIndex(0)
            .Cast(self._node_ty)
            .Clone(f"[{idx}]")
        )

    def update(self):
        d: SBValue = self._valobj.GetChildMemberWithName("d")
        self._node_ty = self._valobj.type.FindDirectNestedType("Node")
        self._size = d.GetChildMemberWithName("size").unsigned
        self._num_buckets = d.GetChildMemberWithName("numBuckets").unsigned
        self._spans: SBValue = d.GetChildMemberWithName("spans")
        self._span_type: SBType = self._spans.type.GetPointeeType()
        if not self._spans:
            return
        self._span_size = self._span_type.GetByteSize()
        self._span_offsets_idx = self._spans.GetIndexOfChildWithName("offsets")
        self._span_entries_idx = self._spans.GetIndexOfChildWithName("entries")
        self._entry_type = self._spans.GetChildAtIndex(
            self._span_entries_idx
        ).type.GetPointeeType()
        self._entry_size = self._entry_type.GetByteSize()
        return

    def has_children(self):
        return True


class QHashPrivateMultiChainSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._size = None
        self._valobj = valobj
        self._next_idx = valobj.GetIndexOfChildWithName("next")

    def num_children(self):
        if self._size is None:
            self._calc_size()
        return self._size

    def _calc_size(self):
        self._size = 0
        vo = self._valobj
        max_idx = vo.target.GetMaximumNumberOfChildrenToDisplay()
        while self._size < max_idx:
            vo = vo.GetChildAtIndex(self._next_idx)
            self._size += 1
            if vo.GetValueAsAddress() == 0:
                break

    def get_child_index(self, name: str):
        return _numeric_index(name)

    def get_child_at_index(self, idx: int):
        if idx < 0:
            return None
        cur = 0
        vo = self._valobj
        max_idx = vo.target.GetMaximumNumberOfChildrenToDisplay()
        while cur != idx and cur < max_idx:
            vo = vo.GetChildAtIndex(self._next_idx)
            if vo.GetValueAsAddress() == 0:
                break
            cur += 1
        if cur != idx:
            return None
        return vo.GetChildMemberWithName("value").Clone(f"[{idx}]")

    def update(self):
        self._size = None

    def has_children(self):
        return True


class QHashPrivateNodeSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._size = None
        self._valobj = valobj
        self._is_inline = not self._valobj.GetChildMemberWithName("value").IsValid()

    def num_children(self):
        if self._is_inline:
            return 0
        return 2

    def get_child_index(self, name: str):
        if self._is_inline:
            return None
        return self._valobj.GetIndexOfChildWithName(name)

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= 2 or self._is_inline:
            return None
        return self._valobj.GetChildAtIndex(idx)

    def update(self):
        self._inliner = self._valobj.GetChildAtIndex(0)
        pass

    def has_children(self):
        return not self._is_inline

    def get_value(self):
        if self._is_inline:
            return self._inliner
        return None


class LazyType:
    def __init__(self, tgt: SBTarget, names: str | tuple[str, ...]):
        self.tgt = tgt
        self.names = (names,) if isinstance(names, str) else names
        self.ty = None

    def __call__(self) -> SBType:
        if self.ty is None:
            for n in self.names:
                self.ty = self.tgt.FindFirstType(n)
                if self.ty:
                    break
        return self.ty  # type: ignore


# struct QtCbor::Element {
#   union {
#     qint64 value;
#     QCborContainerPrivate *container;
#   };
#   QCborValue::Type type;
#   ValueFlag flags;
# };

# struct QCborContainerPrivate {
#   qsizetype usedData = 0;
#   QByteArray data;
#   QList<QtCbor::Element> elements;
# };


class _CborContainerSyntheticProviderBase:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._size = 0
        self._target: SBTarget = valobj.target
        self._process: SBProcess = valobj.process
        self._elements_ptr = 0
        self._data_ptr = 0
        self._sizet_ptr = get_sizet_ptr(self._target)
        self._pointer_size = self._process.GetAddressByteSize()
        self._array_ty = LazyType(self._target, ("QJsonArray", "QCborArray"))
        self._map_ty = LazyType(self._target, ("QJsonObject", "QCborMap"))
        self._barray_ty = LazyType(self._target, "QByteArray")
        self._qcborval_ty = LazyType(self._target, "QCborValue")

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return _numeric_index(name)

    def value_at_index(self, idx: int):
        if idx < 0 or idx >= self._size:
            return

        element_ptr = self._elements_ptr + (self._pointer_size * 2) * idx
        err = SBError()
        ty_and_flags = self._process.ReadUnsignedFromMemory(
            element_ptr + self._pointer_size, 8, err
        )
        if err.Fail():
            return
        ty = ty_and_flags & 0xFFFFFFFF
        flags = ty_and_flags >> 32
        if ty == QCborValueType.Integer:
            return self._valobj.CreateValueFromAddress(
                "", element_ptr, self._target.GetBasicType(lldb.eBasicTypeLongLong)
            )
        elif ty == QCborValueType.ByteArray or ty == QCborValueType.String:
            offset = self._process.ReadPointerFromMemory(element_ptr, err)
            if err.Fail():
                return
            size = self._process.ReadPointerFromMemory(self._data_ptr + offset, err)
            if err.Fail():
                return
            if flags & QtCborElementValueFlag.StringIsUtf16:
                ty = self._target.GetBasicType(lldb.eBasicTypeChar16).GetArrayType(
                    size // 2
                )
            else:
                ty = self._target.GetBasicType(lldb.eBasicTypeChar).GetArrayType(size)
            addr = self._data_ptr + offset + self._pointer_size
            if size == 0:
                # Use fixed data for an empty string.
                # Otherwise, LLDB will try to find a null-terminator.
                data = SBData()
                data.SetData(SBError(), b"\0\0", lldb.eByteOrderLittle, 8)
                v = self._valobj.CreateValueFromData("", data, ty)
            else:
                if (
                    flags & QtCborElementValueFlag.StringIsUtf16
                    and not UNICODE_STR_ARRAY_IS_LIMITED
                ):
                    s = self._process.ReadMemory(addr, size, SBError()) or bytes()
                    try:
                        s = s.decode("utf-16le").encode("utf-8")
                    except BaseException as _:
                        pass
                    data = SBData()
                    data.SetData(SBError(), s, lldb.eByteOrderLittle, 8)
                    ty = self._target.GetBasicType(lldb.eBasicTypeChar).GetArrayType(
                        len(s)
                    )
                    v = self._valobj.CreateValueFromData("", data, ty)
                else:
                    v = self._valobj.CreateValueFromAddress("", addr, ty)
            return v
        elif ty == QCborValueType.Array:
            return self._valobj.CreateValueFromAddress(
                "", element_ptr, self._array_ty()
            )
        elif ty == QCborValueType.Map:
            return self._valobj.CreateValueFromAddress("", element_ptr, self._map_ty())
        elif ty == QCborValueType.Tag:
            return _valobj_from_str(self._valobj, "Unsupported Tag")
        elif ty == QCborValueType.CFalse:
            return self._valobj.CreateBoolValue("", False)
        elif ty == QCborValueType.CTrue:
            return self._valobj.CreateBoolValue("", True)
        elif ty == QCborValueType.Null:
            data = SBData()
            # Fixed buffer that contains a null value.
            data.SetData(SBError(), QCBORVALUE_NULL, lldb.eByteOrderLittle, 8)
            return self._valobj.CreateValueFromData("", data, self._qcborval_ty())
        elif ty == QCborValueType.Undefined:
            data = SBData()
            # Fixed buffer that contains an undefined value.
            data.SetData(SBError(), QCBORVALUE_UNDEFINED, lldb.eByteOrderLittle, 8)
            return self._valobj.CreateValueFromData("", data, self._qcborval_ty())
        elif ty == QCborValueType.Double:
            return self._valobj.CreateValueFromAddress(
                "", element_ptr, self._target.GetBasicType(lldb.eBasicTypeDouble)
            )
        elif ty == QCborValueType.DateTime:
            return _valobj_from_str(self._valobj, "Unsupported DateTime")
        elif ty == QCborValueType.Url:
            return _valobj_from_str(self._valobj, "Unsupported URL")
        elif ty == QCborValueType.RegularExpression:
            return _valobj_from_str(self._valobj, "Unsupported regex")
        elif ty == QCborValueType.Uuid:
            return _valobj_from_str(self._valobj, "Unsupported UUID")
        else:
            return _valobj_from_str(self._valobj, f"Unknown cbor type {ty:x}")

        if self._typ == QCborValueType.Array:
            return self._map_el(idx)

        assert self._typ == QCborValueType.Map
        key = self._get_string_at(idx * 2).summary
        return self._map_el(idx * 2 + 1).Clone(f"[{key}]")

    def update(self):
        self._size = 0
        # Always get the first child to make sure we cast the pointer.
        # The pointer is wrapped in a struct, but we might not have debug info for that struct.
        vo = self._valobj
        if self._valobj.TypeIsPointerType():
            vo = vo.Dereference()
        st_ptr = vo.Cast(self._sizet_ptr).GetValueAsAddress()
        if st_ptr == lldb.LLDB_INVALID_ADDRESS:
            return False
        st_ptr += self._pointer_size  # skip QSharedData

        offsetof_qcborvalue_elements = (
            self._pointer_size * 4
        )  # usedData + sizeof(QByteArray)
        # XXX: This changes in Qt7 - [ptr, size, d]; Qt6: [d, ptr, size]
        offsetof_qarrdata_size = self._pointer_size * 2
        offsetof_qarrdata_ptr = self._pointer_size

        # Find the data pointer (pointer to the string data)
        # `data` is at offset sizeof(qsizetype)
        barray: SBValue = self._valobj.CreateValueFromAddress(
            "", st_ptr + self._pointer_size, self._barray_ty()
        ).GetNonSyntheticValue()
        self._data_ptr = (
            barray.GetChildMemberWithName("d")
            .GetChildMemberWithName("ptr")
            .GetValueAsAddress()
        )

        # Find the element count and the element data
        error = SBError()
        self._size = self._process.ReadPointerFromMemory(
            st_ptr + offsetof_qcborvalue_elements + offsetof_qarrdata_size, error
        )
        if error.Fail():
            self._size = 0
            return False

        self._elements_ptr = self._process.ReadPointerFromMemory(
            st_ptr + offsetof_qcborvalue_elements + offsetof_qarrdata_ptr, error
        )
        if error.Fail():
            self._size = 0
            return False

        return False

    def has_children(self):
        return True


class QCborValueSyntheticProvider:
    TYPE_INDEX = (1 << 32) - 1
    VALUE_INDEX = (1 << 32) - 2

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target: SBTarget = valobj.GetTarget()
        self._arr_ty = LazyType(self._target, ("QJsonArray", "QCborArray"))
        self._map_ty = LazyType(self._target, ("QJsonObject", "QCborMap"))
        self._forwarder: Optional[SBValue] = None
        self._synth_val: Optional[SBValue] = None
        self._ty = QCborValueType.Undefined

    def num_children(self):
        if self._forwarder is None or self._synth_val is not None:
            return 0
        return self._forwarder.GetNumChildren()

    def get_child_index(self, name: str):
        if name == "[type]":
            return self.TYPE_INDEX
        if name == "[value]":
            return self.VALUE_INDEX
        if self._forwarder is None:
            return -1
        return self._forwarder.GetIndexOfChildWithName(name)

    def get_child_at_index(self, idx: int):
        if idx == self.TYPE_INDEX:
            return _valobj_from_signed(self._valobj, self._ty)
        if idx == self.VALUE_INDEX:
            return self._synth_val
        if self._forwarder is None or self._synth_val is not None:
            return
        return self._forwarder.GetChildAtIndex(idx)

    def has_children(self):
        return self._forwarder is not None and self._synth_val is None

    def _make_forwarder_array(self) -> SBValue:
        self._forwarder = (
            self._valobj.GetChildMemberWithName("container")
            .Cast(self._arr_ty())
            .GetSyntheticValue()
        )
        return self._forwarder  # type: ignore

    def _make_forwarder_map(self) -> SBValue:
        self._forwarder = (
            self._valobj.GetChildMemberWithName("container")
            .Cast(self._map_ty())
            .GetSyntheticValue()
        )
        return self._forwarder  # type: ignore

    def update(self):
        self._forwarder = None
        self._synth_val = None

        self._ty = self._valobj.GetChildMemberWithName("t").GetValueAsUnsigned()
        if self._ty == QCborValueType.Integer:
            self._synth_val = self._valobj.GetChildMemberWithName("n")
        elif self._ty == QCborValueType.ByteArray or self._ty == QCborValueType.String:
            arr = self._make_forwarder_array()
            n = self._valobj.GetChildMemberWithName("n").GetValueAsUnsigned()
            self._synth_val = arr.GetChildAtIndex(n)
            if not self._synth_val:
                # If the index doesn't exist, it's an empty string.
                data = SBData()
                data.SetData(SBError(), b"\0", lldb.eByteOrderLittle, 8)
                ty = self._target.GetBasicType(lldb.eBasicTypeChar).GetArrayType(0)
                self._synth_val = self._valobj.CreateValueFromData("", data, ty)
        elif self._ty == QCborValueType.Array:
            self._make_forwarder_array()
        elif self._ty == QCborValueType.Map:
            self._make_forwarder_map()
        elif self._ty == QCborValueType.CFalse:
            self._synth_val = self._valobj.CreateBoolValue("", False)
        elif self._ty == QCborValueType.CTrue:
            self._synth_val = self._valobj.CreateBoolValue("", True)
        elif self._ty == QCborValueType.Null or self._ty == QCborValueType.Undefined:
            pass
        elif self._ty == QCborValueType.Double:
            self._synth_val = self._valobj.GetChildMemberWithName("n").Cast(
                self._target.GetBasicType(lldb.eBasicTypeDouble)
            )

    def get_value(self):
        return self._synth_val


class QCborMapSyntheticProvider(_CborContainerSyntheticProviderBase):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)

    def num_children(self):
        return super().num_children() // 2

    def get_child_at_index(self, idx: int):
        key = self.value_at_index(idx * 2)
        val = self.value_at_index(idx * 2 + 1)
        if not key or not val:
            return
        summary = key.GetSummary()
        if not summary:
            summary = key.GetValue()
        return val.Clone(f"[{summary}]")


class QCborArraySyntheticProvider(_CborContainerSyntheticProviderBase):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)

    def get_child_at_index(self, idx: int):
        val = self.value_at_index(idx)
        if not val:
            return
        return val.Clone(f"[{idx}]")


class QJsonValueSyntheticProvider(_ExpandingSyntheticProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._sval = None

    def _get_value(self, valobj: SBValue) -> SBValue:
        v = valobj.GetChildAtIndex(0).GetSyntheticValue()
        self._sval = v.GetChildAtIndex(QCborValueSyntheticProvider.VALUE_INDEX)
        return v

    def get_value(self):
        return self._sval


class QJsonValueConstRefSyntheticProvider(_ExpandingSyntheticProvider):
    VALUE_IDX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._sval = None

    def _get_value(self, valobj: SBValue) -> SBValue:
        # union -> obj / arr
        is_obj = valobj.GetChildMemberWithName("is_object").GetValueAsUnsigned() != 0
        v = valobj.GetChildAtIndex(0).GetChildMemberWithName("o" if is_obj else "a")
        if v.GetValueAsAddress() == 0:
            return SBValue()
        idx = valobj.GetChildMemberWithName("index").GetValueAsUnsigned()
        self._sval = v.Dereference().GetChildAtIndex(idx)
        return self._sval

    def get_child_at_index(self, idx: int):
        if idx == self.VALUE_IDX:
            return self._sval
        return super().get_child_at_index(idx)

    def get_value(self):
        return self._sval


class QVariantType:
    Unknown = 0
    Bool = 1
    Int = 2
    UInt = 3
    LongLong = 4
    ULongLong = 5
    Double = 6
    Long = 32
    Short = 33
    Char = 34
    ULong = 35
    UShort = 36
    UChar = 37
    Float = 38
    VoidStar = 31
    QStringList = 11
    QVariant = 41
    QByteArrayList = 49
    QObjectStar = 39
    SChar = 40
    Void = 43
    Nullptr = 51
    QVariantMap = 8
    QVariantList = 9
    QVariantHash = 28
    QVariantPair = 58
    Char16 = 56
    Char32 = 57
    Int128 = 59
    UInt128 = 60
    Float128 = 61
    BFloat16 = 62
    Float16 = 63

    _is_init = False

    @staticmethod
    def enusure_init(tgt: SBTarget):
        if QVariantType._is_init:
            return
        QVariantType._is_init = True
        ty: SBType = tgt.FindFirstType("QMetaType::Type")
        if not ty:
            print("Failed to find QMetaType::Type")
            return
        members: lldb.SBTypeEnumMemberList = ty.GetEnumMembers()
        for i in range(members.GetSize()):
            member: lldb.SBTypeEnumMember = members.GetTypeEnumMemberAtIndex(i)
            n: str = member.GetName()
            v = member.GetValueAsUnsigned()
            if not n.startswith("_") and n != "ensure_init":
                setattr(QVariantType, n, v)


class QVariantFlag:
    NeedsConstruction = 0x1
    NeedsDestruction = 0x2
    RelocatableType = 0x4
    PointerToQObject = 0x8
    IsEnumeration = 0x10
    SharedPointerToQObject = 0x20
    WeakPointerToQObject = 0x40
    TrackingPointerToQObject = 0x80
    IsUnsignedEnumeration = 0x100
    IsGadget = 0x200
    PointerToGadget = 0x400
    IsPointer = 0x800
    IsQmlList = 0x1000
    IsConst = 0x2000
    NeedsCopyConstruction = 0x4000
    NeedsMoveConstruction = 0x8000


def QVariantSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    raw: SBValue = valobj.GetNonSyntheticValue()
    is_null = (
        raw.GetChildMemberWithName("d")
        .GetChildMemberWithName("is_null")
        .GetValueAsUnsigned()
        != 0
    )
    if is_null:
        return "(null)"
    val = valobj.GetChildAtIndex(QVariantSyntheticProvider.VALUE_INDEX)
    if val:
        return val.GetSummary() or ""
    ty = valobj.GetChildAtIndex(QVariantSyntheticProvider.TYPE_OBJ_INDEX)
    if ty:
        s = ty.GetSummary().removeprefix('"').removesuffix('"')
        return f"type={s}"
    return "error"


class QVariantSyntheticProvider:
    TYPE_OBJ_INDEX = 0
    VALUE_INDEX = 1

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target: SBTarget = valobj.GetTarget()
        self._process: SBProcess = valobj.GetProcess()
        self._forwarder: Optional[SBValue] = None
        self._value_obj: Optional[SBValue] = None
        self._ty = QCborValueType.Undefined
        self._type = QVariantType.Unknown
        self._type_obj: Optional[SBValue] = None
        self._ty_interface = self._target.FindFirstType("QtPrivate::QMetaTypeInterface")
        self._char_arr_ty = self._target.GetBasicType(lldb.eBasicTypeChar).GetArrayType(
            0
        )
        QVariantType.enusure_init(self._target)

    def num_children(self):
        return 2

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]")
        if name == "Type":
            return self.TYPE_OBJ_INDEX
        if name == "Value":
            return self.VALUE_INDEX
        return -1

    def get_child_at_index(self, idx: int):
        if idx == self.TYPE_OBJ_INDEX:
            return self._type_obj
        if idx == self.VALUE_INDEX:
            return self._value_obj
        return

    def has_children(self):
        return True

    def update(self):
        self._type_obj = None
        self._value_obj = None

        d: SBValue = self._valobj.GetChildMemberWithName("d")
        is_null = d.GetChildMemberWithName("is_null").GetValueAsUnsigned() != 0
        if is_null:
            return  # nothing to do
        # Lookup the data address
        is_shared = d.GetChildMemberWithName("is_shared").GetValueAsUnsigned() != 0
        data_union = d.GetChildMemberWithName("data")
        if is_shared:
            shared = data_union.GetChildMemberWithName("shared").GetValueAsAddress()
            err = SBError()
            off = self._process.ReadUnsignedFromMemory(shared + 4, 4, err)
            if err.Fail():
                return
            data_addr = shared + off
        else:
            data_addr = data_union.GetChildMemberWithName("data").GetLoadAddress()

        ty_addr = d.GetChildMemberWithName("packedType").GetValueAsUnsigned() << 2
        ty_intf: SBValue = self._valobj.CreateValueFromAddress(
            "", ty_addr, self._ty_interface
        )
        self._type_obj = (
            ty_intf.GetChildMemberWithName("name")
            .Dereference()
            .Cast(self._char_arr_ty)
            .Clone("[Type]")
        )
        self._type_obj.SetFormat(lldb.eFormatCharArray)  # type: ignore
        self._type = (
            ty_intf.GetChildMemberWithName("typeId")
            .GetSyntheticValue()
            .GetValueAsUnsigned()
        )
        flags = ty_intf.GetChildMemberWithName("flags").GetValueAsUnsigned()
        ty = self._lookup_type(self._type, flags, self._type_obj)  # type: ignore
        if ty:
            self._value_obj = self._valobj.CreateValueFromAddress(
                "[Value]", data_addr, ty
            )
        else:
            # Hacky workaround to get a void* here.
            char = self._target.GetBasicType(lldb.eBasicTypeChar)
            void = self._target.GetBasicType(lldb.eBasicTypeVoid)
            self._value_obj = (
                self._valobj.CreateValueFromAddress("", data_addr, char)
                .AddressOf()
                .Cast(void.GetPointerType())
                .Clone("[Value]")
            )

    def get_value(self):
        return self._value_obj

    def _lookup_type(self, id: int, flags: int, name_obj: SBValue):
        if id == QVariantType.Unknown:
            return None
        elif id == QVariantType.Bool:
            return self._target.GetBasicType(lldb.eBasicTypeBool)
        elif id == QVariantType.Int:
            return self._target.GetBasicType(lldb.eBasicTypeInt)
        elif id == QVariantType.UInt:
            return self._target.GetBasicType(lldb.eBasicTypeUnsignedInt)
        elif id == QVariantType.LongLong:
            return self._target.GetBasicType(lldb.eBasicTypeLongLong)
        elif id == QVariantType.ULongLong:
            return self._target.GetBasicType(lldb.eBasicTypeUnsignedLongLong)
        elif id == QVariantType.Double:
            return self._target.GetBasicType(lldb.eBasicTypeDouble)
        elif id == QVariantType.Long:
            return self._target.GetBasicType(lldb.eBasicTypeLong)
        elif id == QVariantType.Short:
            return self._target.GetBasicType(lldb.eBasicTypeShort)
        elif id == QVariantType.Char:
            return self._target.GetBasicType(lldb.eBasicTypeChar)
        elif id == QVariantType.ULong:
            return self._target.GetBasicType(lldb.eBasicTypeUnsignedLong)
        elif id == QVariantType.UShort:
            return self._target.GetBasicType(lldb.eBasicTypeUnsignedShort)
        elif id == QVariantType.UChar:
            return self._target.GetBasicType(lldb.eBasicTypeUnsignedChar)
        elif id == QVariantType.Float:
            return self._target.GetBasicType(lldb.eBasicTypeFloat)
        elif id == QVariantType.VoidStar:
            return self._target.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        elif id == QVariantType.QStringList:
            return self._target.FindFirstType("QList<QString>")
        elif id == QVariantType.QVariant:
            return self._valobj.GetType()
        elif id == QVariantType.QByteArrayList:
            return self._target.FindFirstType("QList<QByteArray>")
        elif id == QVariantType.QObjectStar:
            return self._target.FindFirstType("QObject").GetPointerType()
        elif id == QVariantType.SChar:
            return self._target.GetBasicType(lldb.eBasicTypeSignedChar)
        elif id == QVariantType.Void:
            return self._target.GetBasicType(lldb.eBasicTypeVoid)
        elif id == QVariantType.Nullptr:
            return self._target.GetBasicType(lldb.eBasicTypeNullPtr)
        elif id == QVariantType.QVariantMap:
            # Sometimes it's with a space and sometimes without
            return self._target.FindFirstType(
                "QMap<QString, QVariant>"
            ) or self._target.FindFirstType("QMap<QString,QVariant>")
        elif id == QVariantType.QVariantList:
            return self._target.FindFirstType("QList<QVariant>")
        elif id == QVariantType.QVariantHash:
            # Sometimes it's with a space and sometimes without
            return self._target.FindFirstType(
                "QHash<QString, QVariant>"
            ) or self._target.FindFirstType("QHash<QString,QVariant>")
        elif id == QVariantType.QVariantPair:
            return self._target.FindFirstType("QPair<QVariant>")
        elif id == QVariantType.Char16:
            return self._target.GetBasicType(lldb.eBasicTypeChar16)
        elif id == QVariantType.Char32:
            return self._target.GetBasicType(lldb.eBasicTypeChar32)
        elif id == QVariantType.Int128:
            return self._target.GetBasicType(lldb.eBasicTypeInt128)
        elif id == QVariantType.UInt128:
            return self._target.GetBasicType(lldb.eBasicTypeUnsignedInt128)
        elif id == QVariantType.Float128:
            return self._target.GetBasicType(lldb.eBasicTypeFloat128)
        elif id == QVariantType.BFloat16:
            pass
        elif id == QVariantType.Float16:
            pass
        # Lookup the type by name
        name_addr = name_obj.GetLoadAddress()
        proc: SBProcess = self._target.GetProcess()
        err = SBError()
        name: str = proc.ReadCStringFromMemory(name_addr, 2048, err)
        if err.Fail():
            return None
        is_pointer = flags & QVariantFlag.IsPointer
        is_const = flags & QVariantFlag.IsConst
        if is_pointer:
            name = name.removesuffix("*")
        if is_const:
            name.removeprefix("const")
        name = name.strip()
        ty = self._target.FindFirstType(name)
        if not ty:
            return None
        if is_pointer:
            ty = ty.GetPointerType()
        return ty


def QDirSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    vo = valobj.GetChildAtIndex(QDirSyntheticProvider.NAME_INDEX)
    if not vo:
        return ""
    return vo.GetSummary() or ""


class QDirSyntheticProvider:
    NAME_INDEX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target: SBTarget = valobj.GetTarget()
        self._d_ptr: Optional[SBValue] = None
        self._name_val: Optional[SBValue] = None
        self._qstring_ty = self._target.FindFirstType("QString")
        self._qdirp_ty = self._target.FindFirstType("QDirPrivate").GetPointerType()
        self._has_priv = bool(self._qdirp_ty)
        self._void_ptr = self._target.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        self._is_64bit = self._target.GetAddressByteSize() == 8

    def num_children(self):
        if self._d_ptr is None:
            return 0
        return self._d_ptr.GetNumChildren()

    def get_child_index(self, name: str):
        if self._d_ptr is None:
            return
        return self._d_ptr.GetIndexOfChildWithName(name)

    def get_child_at_index(self, idx: int):
        if idx == self.NAME_INDEX:
            return self._name_val
        if self._d_ptr is None:
            return
        return self._d_ptr.GetChildAtIndex(idx)

    def has_children(self):
        return True

    def update(self):
        self._d_ptr = None
        self._name_val = None
        if self._has_priv:
            self._d_ptr = self._valobj.Cast(self._qdirp_ty)
            assert self._d_ptr is not None
            self._name_val = self._d_ptr.GetChildMemberWithName(
                "dirEntry"
            ).GetChildMemberWithName("m_filePath")
        elif self._is_64bit:
            # offsetof(QDirPrivate, dirEntry) = 48 (64 bit)
            d = self._valobj.Cast(self._void_ptr).GetValueAsAddress()
            self._name_val = self._valobj.CreateValueFromAddress(
                "", d + 48, self._qstring_ty
            )


def QFileSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    vo = valobj.GetChildAtIndex(QFileSyntheticProvider.NAME_INDEX)
    if not vo:
        return ""
    return vo.GetSummary() or ""


class QFileSyntheticProvider:
    NAME_INDEX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target: SBTarget = valobj.GetTarget()
        self._process: SBProcess = valobj.GetProcess()
        self._d_ptr: Optional[SBValue] = None
        self._name_val: Optional[SBValue] = None
        self._qstring_ty = self._target.FindFirstType("QString")
        self._qfilep_ty = self._target.FindFirstType("QFilePrivate")
        self._has_priv = bool(self._qfilep_ty)
        self._void_ptr = self._target.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        self._addr_bytes = self._target.GetAddressByteSize()

    def num_children(self):
        if self._d_ptr is None:
            return 0
        return self._d_ptr.GetNumChildren()

    def get_child_index(self, name: str):
        if self._d_ptr is None:
            return
        return self._d_ptr.GetIndexOfChildWithName(name)

    def get_child_at_index(self, idx: int):
        if idx == self.NAME_INDEX:
            return self._name_val
        if self._d_ptr is None:
            return
        return self._d_ptr.GetChildAtIndex(idx)

    def has_children(self):
        return True

    def update(self):
        self._d_ptr = None
        self._name_val = None
        d_ptr_ptr = self._valobj.GetLoadAddress() + self._addr_bytes  # skip vtable
        err = SBError()
        d_ptr_val = self._process.ReadPointerFromMemory(d_ptr_ptr, err)
        if err.Fail():
            return
        if self._has_priv:
            self._d_ptr = self._valobj.CreateValueFromAddress(
                "", d_ptr_val, self._qfilep_ty
            )
            assert self._d_ptr is not None
            self._name_val = self._d_ptr.GetChildMemberWithName("fileName")
        elif self._addr_bytes == 8:
            # offsetof(QFilePrivate, fileName) = 424 (64 bit)
            self._name_val = self._valobj.CreateValueFromAddress(
                "", d_ptr_val + 424, self._qstring_ty
            )


def QFileInfoSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    vo = valobj.GetChildAtIndex(QFileInfoSyntheticProvider.NAME_INDEX)
    if not vo:
        return ""
    return vo.GetSummary() or ""


class QFileInfoSyntheticProvider:
    NAME_INDEX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target: SBTarget = valobj.GetTarget()
        self._d_ptr: Optional[SBValue] = None
        self._name_val: Optional[SBValue] = None
        self._qstring_ty = self._target.FindFirstType("QString")
        self._qfip_ty = self._target.FindFirstType("QFileInfoPrivate").GetPointerType()
        self._has_priv = bool(self._qfip_ty)
        self._void_ptr = self._target.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        self._is_64bit = self._target.GetAddressByteSize() == 8

    def num_children(self):
        if self._d_ptr is None:
            return 0
        return self._d_ptr.GetNumChildren()

    def get_child_index(self, name: str):
        if self._d_ptr is None:
            return
        return self._d_ptr.GetIndexOfChildWithName(name)

    def get_child_at_index(self, idx: int):
        if idx == self.NAME_INDEX:
            return self._name_val
        if self._d_ptr is None:
            return
        return self._d_ptr.GetChildAtIndex(idx)

    def has_children(self):
        return True

    def update(self):
        self._d_ptr = None
        self._name_val = None
        if self._has_priv:
            self._d_ptr = self._valobj.Cast(self._qfip_ty)
            assert self._d_ptr is not None
            self._name_val = self._d_ptr.GetChildMemberWithName(
                "fileEntry"
            ).GetChildMemberWithName("m_filePath")
        elif self._is_64bit:
            # offsetof(QFileInfoPrivate, fileEntry) = 8 (64 bit)
            d = self._valobj.Cast(self._void_ptr).GetValueAsAddress()
            self._name_val = self._valobj.CreateValueFromAddress(
                "", d + 8, self._qstring_ty
            )


def QGenericMatrixSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    raw: SBValue = valobj.GetNonSyntheticValue()
    m: SBType = raw.GetChildMemberWithName("m").GetType()
    m_sz = m.GetByteSize()
    m_el: SBType = m.GetArrayElementType()
    m_el_sz = m_el.GetByteSize()
    m_el_el_sz = m_el.GetArrayElementType().GetByteSize()
    rows = m_el_sz // m_el_el_sz
    cols = m_sz // m_el_sz
    return f"{cols}x{rows}"


class QGenericMatrixSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self.m: SBValue = valobj.GetChildMemberWithName("m")
        mt = self.m.GetType()
        m_sz = mt.GetByteSize()
        m_el: SBType = mt.GetArrayElementType()
        m_el_sz = m_el.GetByteSize()
        m_el_el_sz = m_el.GetArrayElementType().GetByteSize()
        self.rows = m_el_sz // m_el_el_sz
        self.cols = m_sz // m_el_sz

    def num_children(self):
        return self.rows * self.cols

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]").removeprefix("m")
        try:
            row = int(name[0]) - 1
            col = int(name[1]) - 1
            return col + row * self.cols
        except BaseException:
            return

    def get_child_at_index(self, idx: int):
        if idx > self.rows * self.cols:
            return
        row = idx // self.cols
        col = idx % self.cols

        return (
            self.m.GetChildAtIndex(col)
            .GetChildAtIndex(row)
            .Clone(f"[m{row + 1}{col + 1}]")
        )

    def has_children(self):
        return True

    def update(self):
        self.m = self._valobj.GetChildMemberWithName("m")


def QHostAddressSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    raw: SBValue = valobj.GetNonSyntheticValue()
    tgt: SBTarget = valobj.GetTarget()
    proc: SBProcess = tgt.GetProcess()
    d_addr = raw.Cast(
        tgt.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
    ).GetValueAsAddress()
    err = SBError()
    proto = proc.ReadUnsignedFromMemory(d_addr + 52, 1, err)
    if err.Fail():
        return err.description
    if proto == 0 or proto == 2:
        # IPv4
        a = proc.ReadUnsignedFromMemory(d_addr + 48, 4, err)
        if err.Fail():
            return err.description
        return f"{a >> 24}.{(a >> 16) & 0xFF}.{(a >> 8) & 0xFF}.{a & 0xFF}"
    elif proto != 1:
        return "(invalid)"

    v0 = proc.ReadUnsignedFromMemory(d_addr + 32, 8, err)
    if err.Fail():
        return err.description
    v1 = proc.ReadUnsignedFromMemory(d_addr + 32 + 8, 8, err)
    if err.Fail():
        return err.description

    def to_ipv6_part(v: int):
        return f"{v & 0xFF:02x}{(v >> 8) & 0xFF:02x}:{(v >> 16) & 0xFF:02x}{(v >> 24) & 0xFF:02x}:{(v >> 32) & 0xFF:02x}{(v >> 40) & 0xFF:02x}:{(v >> 48) & 0xFF:02x}{v >> 56:02x}"

    return f"{to_ipv6_part(v0)}:{to_ipv6_part(v1)}"


class QHostAddressSyntheticProvider:
    NAME_INDEX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        tgt = self._valobj.GetTarget()
        self._process: SBProcess = valobj.GetProcess()
        self._void_ptr = tgt.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        self._proto_ty = tgt.FindFirstType("QAbstractSocket::NetworkLayerProtocol")
        self._qstring_ty = tgt.FindFirstType("QString")
        self._scope_id = None
        self._proto = None

    def num_children(self):
        return 2

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]")
        if name == "Protocol":
            return 0
        elif name == "ScopeID":
            return 1

    def get_child_at_index(self, idx: int):
        if idx == 0:
            return self._proto
        elif idx == 1:
            return self._scope_id

    def has_children(self):
        return True

    def update(self):
        d_addr = self._valobj.Cast(self._void_ptr).GetValueAsAddress()
        self._scope_id = self._valobj.CreateValueFromAddress(
            "[ScopeID]", d_addr + 8, self._qstring_ty
        )
        proto = self._process.ReadUnsignedFromMemory(d_addr + 52, 1, SBError())
        vo = _valobj_from_signed(self._valobj, proto, "[Protocol]")
        self._proto = vo.Cast(self._proto_ty)


def QImageSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    raw: SBValue = valobj.GetNonSyntheticValue()
    if raw.GetChildMemberWithName("d").GetValueAsAddress() == 0:
        return "(null)"
    w = valobj.GetChildAtIndex(QImageSyntheticProvider.WIDTH_INDEX).GetValueAsSigned()
    h = valobj.GetChildAtIndex(QImageSyntheticProvider.HEIGHT_INDEX).GetValueAsSigned()
    return f"{w}x{h}"


class QImageSyntheticProvider:
    WIDTH_INDEX = 0
    HEIGHT_INDEX = 1
    FORMAT_INDEX = 2
    DATA_INDEX = 3
    N_BYTES_INDEX = 4
    STRIDE_INDEX = 5
    DPR_INDEX = 6

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target = self._valobj.GetTarget()
        self._process: SBProcess = valobj.GetProcess()
        self._int = self._target.GetBasicType(lldb.eBasicTypeInt)
        self._format_ty = self._target.FindFirstType("QImage::Format")
        self._uchar_ptr = self._target.GetBasicType(
            lldb.eBasicTypeUnsignedChar
        ).GetPointerType()
        self._priv_ty = self._target.FindFirstType("QImageData").GetPointerType()
        self._has_priv = bool(self._priv_ty)
        self._is_64bit = self._target.GetAddressByteSize() == 8

        self._width = None
        self._height = None
        self._format = None
        self._data = None
        self._n_bytes = None
        self._stride = None
        self._dpr = None

    def num_children(self):
        return 7 if self._width else 0

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]")
        if name == "Width":
            return self.WIDTH_INDEX
        elif name == "Height":
            return self.HEIGHT_INDEX
        elif name == "Format":
            return self.FORMAT_INDEX
        elif name == "Data":
            return self.DATA_INDEX
        elif name == "ByteSize":
            return self.N_BYTES_INDEX
        elif name == "Stride":
            return self.STRIDE_INDEX
        elif name == "DevicePixelRatio":
            return self.DPR_INDEX

    def get_child_at_index(self, idx: int):
        if idx == self.WIDTH_INDEX:
            return self._width
        elif idx == self.HEIGHT_INDEX:
            return self._height
        elif idx == self.FORMAT_INDEX:
            return self._format
        elif idx == self.DATA_INDEX:
            return self._data
        elif idx == self.N_BYTES_INDEX:
            return self._n_bytes
        elif idx == self.STRIDE_INDEX:
            return self._stride
        elif idx == self.DPR_INDEX:
            return self._dpr

    def has_children(self):
        return True

    def update(self):
        self._width = None
        self._height = None
        self._format = None
        self._data = None
        self._n_bytes = None
        self._stride = None
        self._dpr = None

        d = self._valobj.GetChildMemberWithName("d")
        d_addr = d.GetValueAsAddress()
        if d_addr == 0:
            return  # null image
        if self._has_priv:
            d: SBValue = d.Cast(self._priv_ty)
            self._width = d.GetChildMemberWithName("width").Clone("[Width]")
            self._height = d.GetChildMemberWithName("height").Clone("[Height]")
            self._n_bytes = d.GetChildMemberWithName("nbytes").Clone("[ByteSize]")
            self._data = d.GetChildMemberWithName("data").Clone("[Data]")
            self._format = d.GetChildMemberWithName("format").Clone("[Format]")
            self._stride = d.GetChildMemberWithName("bytes_per_line").Clone("[Stride]")
            self._dpr = d.GetChildMemberWithName("devicePixelRatio").Clone(
                "[DevicePixelRatio]"
            )
        elif self._is_64bit:
            width_off = 4  # offsetof(QImageData, width)
            height_off = 8  # offsetof(QImageData, height)
            nbytes_off = 16  # offsetof(QImageData, nbytes)
            dpr_off = 24  # offsetof(QImageData, devicePixelRatio)
            data_off = 56  # offsetof(QImageData, data)
            format_off = 64  # offsetof(QImageData, format)
            stride_off = 72  # offsetof(QImageData, bytes_per_line)

            qsizetype = self._target.GetBasicType(lldb.eBasicTypeLongLong)
            uchar_ptr = self._target.GetBasicType(
                lldb.eBasicTypeUnsignedChar
            ).GetPointerType()
            self._width = self._valobj.CreateValueFromAddress(
                "[Width]", d_addr + width_off, self._int
            )
            self._height = self._valobj.CreateValueFromAddress(
                "[Height]", d_addr + height_off, self._int
            )
            self._n_bytes = self._valobj.CreateValueFromAddress(
                "[ByteSize]",
                d_addr + nbytes_off,
                qsizetype,
            )
            self._dpr = self._valobj.CreateValueFromAddress(
                "[DevicePixelRatio]",
                d_addr + dpr_off,
                self._target.GetBasicType(lldb.eBasicTypeDouble),
            )
            self._data = self._valobj.CreateValueFromAddress(
                "[Data]",
                d_addr + data_off,
                uchar_ptr,
            )
            self._format = self._valobj.CreateValueFromAddress(
                "[Format]", d_addr + format_off, self._format_ty
            )
            self._stride = self._valobj.CreateValueFromAddress(
                "[Stride]", d_addr + stride_off, qsizetype
            )


def QObjectSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    v = valobj.GetChildAtIndex(QObjectSyntheticProvider.NAME_INDEX)
    if not v:
        return ""
    return v.GetSummary()


class QObjectSyntheticProvider:
    PARENT_INDEX = 0
    NAME_INDEX = 1
    PROP_NAMES_INDEX = 2
    PROP_VALUES_INDEX = 3

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target = self._valobj.GetTarget()
        self._process: SBProcess = valobj.GetProcess()
        self._void_ptr = self._target.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        self._qobj_ptr = self._valobj.GetType().GetPointerType()
        self._qstr_ty = LazyType(self._target, "QString")
        self._qbalist_ty = LazyType(self._target, "QList<QByteArray>")
        self._qvlist_ty = LazyType(self._target, "QList<QVariant>")

        self._qpriv = self._target.FindFirstType("QObjectPrivate")
        self._has_priv = bool(self._qpriv)
        self._ptr_size = self._target.GetAddressByteSize()

        self._name = None
        self._parent = None
        self._prop_names = None
        self._prop_values = None

    def num_children(self):
        return 5

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]")
        if name == "Name":
            return self.NAME_INDEX
        elif name == "Parent":
            return self.PARENT_INDEX
        elif name == "PropertyNames":
            return self.PROP_NAMES_INDEX
        elif name == "PropertyValues":
            return self.PROP_VALUES_INDEX

    def get_child_at_index(self, idx: int):
        if idx == self.NAME_INDEX:
            return self._name
        elif idx == self.PARENT_INDEX:
            return self._parent
        elif idx == self.PROP_NAMES_INDEX:
            return self._prop_names
        elif idx == self.PROP_VALUES_INDEX:
            return self._prop_values

    def has_children(self):
        return True

    def update(self):
        self._name = None
        self._parent = None
        self._prop_names = None
        self._prop_values = None

        d_addr_addr = self._valobj.GetLoadAddress() + self._ptr_size  # skip vtable
        err = SBError()
        d_addr = self._process.ReadPointerFromMemory(d_addr_addr, err)
        if err.Fail():
            return
        if d_addr == 0:
            return

        if self._has_priv:
            d: SBValue = self._valobj.CreateValueFromAddress("", d_addr, self._qpriv)
            # FIXME: Add children
            self._parent = d.GetChildMemberWithName("parent").Clone("[Parent]")
            ed: SBValue = d.GetChildMemberWithName("extraData")
            if ed.GetValueAsAddress() != 0:
                self._name = ed.GetChildMemberWithName("objectName").Clone("[Name]")
                self._prop_names = ed.GetChildMemberWithName("propertyNames").Clone(
                    "[PropertyNames]"
                )
                self._prop_values = ed.GetChildMemberWithName("propertyValues").Clone(
                    "[PropertyValues]"
                )
            # pass
        elif self._ptr_size == 8:
            parent_off = 16  # offsetof(QObjectPrivate, parent)
            # children_off = 24  # offsetof(QObjectPrivate, children)
            ed_off = 80  # offsetof(QObjectPrivate, extraData)
            obj_name_off = 96  # offsetof(QObjectPrivate::ExtraData, objectName)
            prop_names_off = 0  # offsetof(QObjectPrivate::ExtraData, propertyNames)
            prop_values_off = 24  # offsetof(QObjectPrivate::ExtraData, propertyValues)

            self._parent = self._valobj.CreateValueFromAddress(
                "[Parent]", d_addr + parent_off, self._qobj_ptr
            )
            ed_addr = self._process.ReadPointerFromMemory(d_addr + ed_off, err)
            if err.Fail() or ed_addr == 0:
                return
            self._name = self._valobj.CreateValueFromAddress(
                "[Name]", ed_addr + obj_name_off, self._qstr_ty()
            )
            self._prop_names = self._valobj.CreateValueFromAddress(
                "[PropertyNames]", ed_addr + prop_names_off, self._qbalist_ty()
            )
            self._prop_values = self._valobj.CreateValueFromAddress(
                "[PropertyValues]", ed_addr + prop_values_off, self._qvlist_ty()
            )


def QUrlSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    v = valobj.GetChildAtIndex(QUrlSyntheticProvider.COMBINED_INDEX)
    if not v:
        return "(null)"
    return v.GetSummary()


class QUrlSyntheticProvider:
    SCHEME_INDEX = 0
    USERNAME_INDEX = 1
    PASS_INDEX = 2
    HOST_INDEX = 3
    PORT_INDEX = 4
    PATH_INDEX = 5
    QUERY_INDEX = 6
    FRAGMENT_INDEX = 7
    COMBINED_INDEX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target = self._valobj.GetTarget()
        self._process: SBProcess = valobj.GetProcess()
        self._void_ptr = self._target.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        self._qstring_ty = self._target.FindFirstType("QString")
        self._ptr_size = self._target.GetAddressByteSize()

        self._scheme = None
        self._user = None
        self._pass = None
        self._host = None
        self._port = None
        self._path = None
        self._query = None
        self._fragment = None
        self._combined = None

    def num_children(self):
        return 8

    def get_child_index(self, name: str):
        name = name.removeprefix("[").removesuffix("]")
        if name == "Scheme":
            return self.SCHEME_INDEX
        elif name == "Username":
            return self.USERNAME_INDEX
        elif name == "Password":
            return self.PASS_INDEX
        elif name == "Host":
            return self.HOST_INDEX
        elif name == "Port":
            return self.PORT_INDEX
        elif name == "Path":
            return self.PATH_INDEX
        elif name == "Query":
            return self.QUERY_INDEX
        elif name == "Fragment":
            return self.FRAGMENT_INDEX

    def get_child_at_index(self, idx: int):
        if idx == self.SCHEME_INDEX:
            return self._scheme
        elif idx == self.USERNAME_INDEX:
            return self._user
        elif idx == self.PASS_INDEX:
            return self._pass
        elif idx == self.HOST_INDEX:
            return self._host
        elif idx == self.PORT_INDEX:
            return self._port
        elif idx == self.PATH_INDEX:
            return self._path
        elif idx == self.QUERY_INDEX:
            return self._query
        elif idx == self.FRAGMENT_INDEX:
            return self._fragment
        elif idx == self.COMBINED_INDEX:
            return self._combined

    def has_children(self):
        return True

    def update(self):
        self._scheme = None
        self._user = None
        self._pass = None
        self._host = None
        self._port = None
        self._path = None
        self._query = None
        self._fragment = None
        self._combined = None

        d_addr = self._valobj.GetChildMemberWithName("d").GetValueAsAddress()
        if d_addr == 0:
            return

        self._port = self._valobj.CreateValueFromAddress(
            "[Port]", d_addr + 4, self._target.GetBasicType(lldb.eBasicTypeInt)
        )
        port = self._port.GetValueAsSigned()
        self._scheme = self._make_nth("[Scheme]", d_addr, 0)
        scheme = self._str_at(d_addr, 0)
        self._user = self._make_nth("[Username]", d_addr, 1)
        user = self._str_at(d_addr, 1)
        self._pass = self._make_nth("[Password]", d_addr, 2)
        _pass = self._str_at(d_addr, 2)
        self._host = self._make_nth("[Host]", d_addr, 3)
        host = self._str_at(d_addr, 3)
        self._path = self._make_nth("[Path]", d_addr, 4)
        path = self._str_at(d_addr, 4)
        self._query = self._make_nth("[Query]", d_addr, 5)
        query = self._str_at(d_addr, 5)
        self._fragment = self._make_nth("[Fragment]", d_addr, 6)
        fragment = self._str_at(d_addr, 6)

        flags = self._process.ReadUnsignedFromMemory(
            d_addr + 2 * 4 + 7 * 3 * self._ptr_size + self._ptr_size + 1, 1, SBError()
        )
        if 2 * 4 + 7 * 3 * self._ptr_size + self._ptr_size + 1 != 185:
            print("XXXXXXXX")

        url = ""
        if scheme:
            url += scheme + ":"
        has_authority = user or _pass or host or port >= 0
        path_is_absolute = path.startswith("/")
        is_local_file = (flags & 0x1) != 0
        if has_authority:
            url += "//"
            if user or _pass:
                url += user
                if _pass:
                    url += ":" + _pass
                url += "@"
            url += host
            if port >= 0:
                url += ":" + str(port)
        elif path_is_absolute and is_local_file:
            url += "//"

        url += path
        if query:
            url += "?" + query
        if fragment:
            url += "#" + fragment

        self._combined = _valobj_from_str(self._valobj, url)

    def _make_nth(self, name: str, base: int, nth: int):
        return self._valobj.CreateValueFromAddress(
            name, base + 2 * 4 + nth * 3 * self._ptr_size, self._qstring_ty
        )

    def _str_at(self, base: int, nth: int) -> str:
        # XXX: This changes in Qt7 - [ptr, size, d]; Qt6: [d, ptr, size]
        err = SBError()
        base_ptr = base + 2 * 4 + nth * 3 * self._ptr_size
        sz = self._process.ReadUnsignedFromMemory(base_ptr + 2 * self._ptr_size, 8, err)
        if sz == 0:
            return ""
        addr = self._process.ReadPointerFromMemory(base_ptr + self._ptr_size, err)
        if addr == 0:
            return ""
        s = self._process.ReadMemory(addr, sz * 2, err) or bytes()
        try:
            return s.decode("utf-16le")
        except BaseException as _:
            return ""


def _valobj_from_signed(source: SBValue, val: int, name="") -> SBValue:
    ty: SBType = source.target.GetBasicType(lldb.eBasicTypeLongLong)
    data = SBData.CreateDataFromInt(val, ty.GetByteSize())
    return source.CreateValueFromData(name, data, ty)  # type: ignore


def _valobj_from_str(source: SBValue, val: str, name="") -> SBValue:
    ty: SBType = source.target.GetBasicType(lldb.eBasicTypeChar).GetArrayType(len(val))
    data = SBData.CreateDataFromCString(source.process.GetByteOrder(), 8, val)
    return source.CreateValueFromData(name, data, ty)


def _prefer_synthetic(value: SBValue) -> SBValue:
    synth = value.GetSyntheticValue()
    if synth:
        return synth
    return value


def _numeric_index(name: str) -> Optional[int]:
    name = name.removeprefix("[").removesuffix("]")
    try:
        return int(name)
    except ValueError:
        return None


def _qdatetime_data(valobj: SBValue) -> Optional[tuple[datetime.datetime, bool]]:
    tgt: SBTarget = valobj.GetTarget()
    ptr_size: int = tgt.GetAddressByteSize()
    void_ptr = tgt.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
    if valobj.TypeIsPointerType():
        valobj = valobj.Dereference()
    d_val: int = valobj.Cast(void_ptr).GetValueAsAddress()
    is_short = (d_val & 1) != 0
    if is_short:
        status = d_val & 0xFF
        if (status & QDateTimeConstants.STATUS_VALID_DATETIME_MASK) == 0:
            return None
        spec = (
            status & QDateTimeConstants.STATUS_TIME_SPEC_MASK
        ) >> QDateTimeConstants.STATUS_TIME_SPEC_SHIFT
        is_local = spec == QDateTimeConstants.TIME_SPEC_LOCAL
        msec = d_val >> 8
        dt = datetime.datetime.fromtimestamp(msec / 1000.0, datetime.UTC)
        return dt, is_local

    process: SBProcess = valobj.GetProcess()
    # class QDateTimePrivate : public QSharedData {
    #   Status m_status;
    #   qint64 m_msecs;
    #   int m_offsetFromUtc;
    #   QTimeZone m_timeZone;
    # };
    status_addr = d_val + 4
    msecs_addr = d_val + ptr_size
    offset_from_utc_addr = d_val + 16

    err = SBError()
    status = process.ReadUnsignedFromMemory(status_addr, 4, err)
    if err.Fail():
        return None

    if (status & QDateTimeConstants.STATUS_VALID_DATETIME_MASK) == 0:
        return None

    msec = process.ReadUnsignedFromMemory(msecs_addr, 8, err)
    msec = _uint64_to_int64(msec)
    if err.Fail():
        return None

    offset = process.ReadUnsignedFromMemory(offset_from_utc_addr, 4, err)
    offset = _uint32_to_int32(offset)
    if err.Fail():
        return None

    # datetime expects a UTC timestamp
    try:
        dt = datetime.datetime.fromtimestamp(
            0,
            datetime.timezone(datetime.timedelta(seconds=offset)),
        ) + datetime.timedelta(seconds=msec / 1000.0 - offset)
        return dt, False
    except BaseException as e:
        print(e)


def _uint32_to_int32(n):
    n = n & 0xFFFF_FFFF
    return (n ^ 0x8000_0000) - 0x8000_0000


def _uint64_to_int64(n):
    n = n & 0xFFFF_FFFF_FFFF_FFFF
    return (n ^ 0x8000_0000_0000_0000) - 0x8000_0000_0000_0000
