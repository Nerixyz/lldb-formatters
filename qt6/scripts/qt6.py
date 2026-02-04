import lldb
from lldb import (
    SBValue,
    SBType,
    SBTarget,
    SBData,
    SBError,
    SBDebugger,
    SBProcess,
    SBTypeList,
)
from typing import Callable
from constants import QDateTimeConstants, QHashConstants
import datetime


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    dbg.HandleCommand("type category define -e qt -l c++")

    def add_summary(
        type_name: str, *, regex: str | None = None, other_names: list[str] = []
    ):
        type_names = other_names + [type_name]
        cmd = f"type summary add -w qt -F {__name__}.{type_name}SummaryProvider "
        if regex:
            cmd += f' -x "{regex}"'
        else:
            cmd += " ".join(map(lambda it: f'"{it}"', type_names))
        dbg.HandleCommand(cmd)

    def add_synthetic(
        name: str, *, regex: str | None = None, other_names: list[str] = []
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
    add_summary("QtCborElement", other_names=["QtCbor::Element"])
    _add_summary_string(dbg, ["QPoint", "QPointF"], "(x: ${var.xp}, y: ${var.yp})")
    _add_summary_string(dbg, "^QList<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^Q(Multi)?Hash<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^Q(Map|Set)<.*>$", "size=${svar%#}", regex=True)
    _add_summary_string(dbg, "^QVarLengthArray<.*>$", "size=${svar%#}", regex=True)
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
    _add_summary_string(dbg, "QChar", "${var.ucs}")
    _add_summary_string(dbg, "QJsonValue", "${var.value}")
    _add_summary_string(dbg, "QJsonObject", "\\{ size=${svar%#} \\}")
    _add_summary_string(dbg, "QJsonArray", "[ size=${svar%#} ]")

    add_synthetic("QCheckedInt", regex="^QtPrivate::QCheckedIntegers::QCheckedInt<.*>$")
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
    add_synthetic("QVarLengthArray", regex="^QVarLengthArray<.*>$")
    add_synthetic("QFlags", regex="^QFlags<.*>$")
    add_synthetic("QJsonDocument")
    add_synthetic("QJsonObject")
    add_synthetic("QJsonArray")
    add_synthetic("QJsonValue")
    add_synthetic("QCborValue")
    add_synthetic("QtCborElement", other_names=["QtCbor::Element"])


def _add_summary_string(
    dbg: SBDebugger,
    type_names: str | list[str],
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


def QStringSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
    return _qarraydata_summary(valobj, lldb.eBasicTypeChar16, "u")


def QByteArraySummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
    return _qarraydata_summary(valobj, lldb.eBasicTypeChar, "")


def _qarraydata_summary(valobj: SBValue, ty, prefix: str):
    d_obj: SBValue = valobj.GetNonSyntheticValue().GetChildMemberWithName("d")
    ptr_obj: SBValue = d_obj.GetChildMemberWithName("ptr")
    size = d_obj.GetChildMemberWithName("size").unsigned
    if not ptr_obj.IsValid():
        return None
    if ptr_obj.GetValueAsUnsigned() == 0:
        return prefix + '"" (null)'
    if size == 0:
        return prefix + '""'
    array_type = valobj.target.GetBasicType(ty).GetArrayType(size)
    return ptr_obj.deref.Cast(array_type).summary


def QStringViewSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
    valobj = valobj.GetNonSyntheticValue()
    ptr: SBValue = valobj.GetChildMemberWithName("m_data")
    size = valobj.GetChildMemberWithName("m_size").unsigned
    if size == 0:
        return 'u""'
    array_type = valobj.target.GetBasicType(lldb.eBasicTypeChar16).GetArrayType(size)
    return ptr.deref.Cast(array_type).summary


def QUuidSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
    data1 = valobj.GetChildMemberWithName("data1").unsigned
    data2 = valobj.GetChildMemberWithName("data2").unsigned
    data3 = valobj.GetChildMemberWithName("data3").unsigned
    data4 = valobj.GetChildMemberWithName("data4").GetData()
    e = SBError()
    data4 = data4.ReadRawData(e, 0, 8)
    if e.Fail():
        return None
    return f"{data1:08x}-{data2:04x}-{data3:04x}-{data4[0]:02x}{data4[1]:02x}-{data4[2]:02x}{data4[3]:02x}{data4[4]:02x}{data4[5]:02x}{data4[6]:02x}{data4[7]:02x}"


def QRectSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
    valobj = valobj.GetNonSyntheticValue()
    x1 = _prefer_synthetic(valobj.GetChildMemberWithName("x1")).signed
    x2 = _prefer_synthetic(valobj.GetChildMemberWithName("x2")).signed
    y1 = _prefer_synthetic(valobj.GetChildMemberWithName("y1")).signed
    y2 = _prefer_synthetic(valobj.GetChildMemberWithName("y2")).signed
    return f"(x: {x1}, y: {y1}, width: {x2 - x1 + 1}, height: {y2 - y1 + 1})"


def QTimeSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
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
) -> str | None:
    valobj = valobj.GetNonSyntheticValue()
    date = _QDate(valobj.GetChildMemberWithName("jd").signed)
    if not date.valid:
        return "(invalid)"
    return f"{date.year}-{date.month:02}-{date.day:02}"


def QDateTimeSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
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
    dt = datetime.datetime.fromtimestamp(ms / 1000.0, tz)
    ms = dt.microsecond // 1000
    ms_part = f".{ms:03}" if ms != 0 else ""
    if is_local:
        return dt.strftime(f"%Y-%m-%d %X{ms_part} (Local)")
    return dt.strftime(f"%Y-%m-%d %X{ms_part} %Z")


def QtCborElementSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
    QCborValueType.load(valobj.GetTarget())
    raw: SBValue = valobj.GetNonSyntheticValue()
    ty = raw.GetChildMemberWithName("type").unsigned
    return _QtCborLikeSummary(
        valobj, ty, lambda: raw.GetChildAtIndex(0).GetChildMemberWithName("value")
    )


def QCborValueSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
    QCborValueType.load(valobj.GetTarget())
    raw: SBValue = valobj.GetNonSyntheticValue()
    ty = raw.GetChildMemberWithName("t").unsigned
    if ty == QCborValueType.STRING:
        ptr = valobj.GetTarget().FindFirstType("QCborContainerPrivate").GetPointerType()
        container: SBValue = raw.GetChildMemberWithName("container").Cast(ptr)
        if container:
            el = (
                container.GetChildMemberWithName("elements")
                .GetSyntheticValue()
                .GetChildAtIndex(0)
                .GetNonSyntheticValue()
            )
            data_ptr = (
                container.GetChildMemberWithName("data")
                .GetChildAtIndex(0)
                .GetChildMemberWithName("ptr")
                .GetValueAsAddress()
            )
            return _CborSyntheticProviderBase._static_get_string_for(
                valobj, el, data_ptr
            ).GetSummary()

    return _QtCborLikeSummary(valobj, ty, lambda: raw.GetChildMemberWithName("n"))


def _QtCborLikeSummary(valobj: SBValue, ty: int, v: Callable[[], SBValue]):
    match ty:
        case QCborValueType.INTEGER:
            return v().signed
        case QCborValueType.DOUBLE:
            return v().GetData().double[0]
        case QCborValueType.STRING:
            return "(string)"
        case QCborValueType.ARRAY:
            return f"[ size={valobj.GetNumChildren()} ]"
        case QCborValueType.MAP:
            return f"{{ size={valobj.GetNumChildren()} }}"
        case QCborValueType.FALSE:
            return "false"
        case QCborValueType.TRUE:
            return "true"
        case QCborValueType.NULL:
            return "null"
        case QCborValueType.UNDEFINED:
            return "undefined"
    return "unknown"


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


class QMapSyntheticProvider(_ExpandingSyntheticProvider):
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
        self._priv = valobj.target.FindFirstType(
            "QJsonDocumentPrivate"
        ).GetPointerType()

    def _get_value(self, valobj: SBValue) -> SBValue:
        return (
            valobj.GetChildAtIndex(0)
            .GetSyntheticValue()
            .GetChildAtIndex(0)
            .Cast(self._priv)
            .GetChildMemberWithName("value")
        )


class _ArraySyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj
        self._size = 0
        self._val: SBValue | None = None

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
    items: list[tuple[str, Callable | str]] = []

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
        self._cache[idx] = v
        return v

    def _get_at_index(self, idx: int):
        key, item = self.items[idx]
        if isinstance(item, str):
            return self._valobj.GetChildMemberWithName(item).Clone(f"[{key}]")
        # else: callable
        return item(self, self._valobj).Clone(f"[{key}]")

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
        l = jd + 68569
        n = 4 * l // 146097
        l = l - (146097 * n + 3) // 4
        i = 4000 * (l + 1) // 1461001
        l = l - 1461 * i // 4 + 31
        j = 80 * l // 2447
        k = l - 2447 * j // 80
        l = j // 11
        j = j + 2 - 12 * l
        i = 100 * (n - 49) + i + l
        self.year = i
        self.month = j
        self.day = k


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
        match name:
            case "ms":
                return 0
            case "offset-sec":
                return 1
        return None

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self.num_children():
            return None
        match idx:
            case 0:
                return _valobj_from_signed(self._valobj, self._utcdate, "[ms]")
            case 1:
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
        self._last_bucket: tuple[int, int] | None = None
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
            if err.Fail():
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
        while vo and vo.unsigned != 0 and self._size < max_idx:
            vo = vo.GetChildAtIndex(self._next_idx)
            self._size += 1

    def get_child_index(self, name: str):
        return _numeric_index(name)

    def get_child_at_index(self, idx: int):
        if idx < 0:
            return None
        cur = 0
        vo = self._valobj
        max_idx = vo.target.GetMaximumNumberOfChildrenToDisplay()
        while cur != idx and vo and vo.unsigned != 0 and cur < max_idx:
            vo = vo.GetChildAtIndex(self._next_idx)
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


class QCborValueType:
    INTEGER: int
    DOUBLE: int
    STRING: int
    ARRAY: int
    MAP: int
    FALSE: int
    TRUE: int
    NULL: int
    UNDEFINED: int
    _loaded = False

    @staticmethod
    def load(target: SBTarget):
        if QCborValueType._loaded:
            return
        members = target.FindFirstType("QCborValue::Type").enum_members
        m = {v.name: v.unsigned for v in members}
        QCborValueType.INTEGER = m["Integer"]
        QCborValueType.DOUBLE = m["Double"]
        QCborValueType.STRING = m["String"]
        QCborValueType.ARRAY = m["Array"]
        QCborValueType.MAP = m["Map"]
        QCborValueType.FALSE = m["False"]
        QCborValueType.TRUE = m["True"]
        QCborValueType.NULL = m["Null"]
        QCborValueType.UNDEFINED = m["Undefined"]
        QCborValueType._loaded = True

    @staticmethod
    def is_simple(ty: int):
        return ty != QCborValueType.ARRAY and ty != QCborValueType.MAP


class QCborValueFlag:
    IS_CONTAINER = 1
    HAS_BYTE_DATA = 2
    STRING_IS_UTF16 = 4
    STRING_IS_ASCII = 8


class _CborSyntheticProviderBase:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        QCborValueType.load(valobj.target)
        self._typ = QCborValueType.UNDEFINED
        self._is_simple = True
        self._size = 0
        self._target: SBTarget = valobj.target
        self._process: SBProcess = valobj.process
        self._elements: SBValue | None = None
        self._data_ptr = 0
        self._byte_data_ty = self._target.FindFirstType(
            "QtCbor::ByteData"
        ).GetPointerType()
        self._pointer_size = self._process.GetAddressByteSize()

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return _numeric_index(name)

    def get_child_at_index(self, idx: int):
        if self._is_simple or idx < 0 or idx >= self._size or not self._elements:
            return
        if self._typ == QCborValueType.ARRAY:
            return self._map_el(idx)

        assert self._typ == QCborValueType.MAP
        key = self._get_string_at(idx * 2).summary
        return self._map_el(idx * 2 + 1).Clone(f"[{key}]")

    def _map_el(self, idx: int):
        assert self._elements
        el = self._elements.GetChildAtIndex(idx)
        eln = el.GetNonSyntheticValue()
        ty = eln.GetChildMemberWithName("type").unsigned
        if ty == QCborValueType.STRING:
            return self._get_string_at(idx, eln).Clone(f"[{idx}]")
        return el

    def _get_type_container(self) -> tuple[int, SBValue]:
        raise NotImplementedError()

    def update(self):
        ty, container = self._get_type_container()
        self._typ = ty
        self._is_simple = QCborValueType.is_simple(self._typ)
        if self._is_simple or container.load_addr == 0:
            self._size = 0
            self._data_ptr = 0
            self._elements = None
        else:
            self._elements = container.GetChildMemberWithName(
                "elements"
            ).GetSyntheticValue()
            assert self._elements
            self._size = self._elements.GetNumChildren()
            self._data_ptr = (
                container.GetChildMemberWithName("data")
                .GetChildMemberWithName("d")
                .GetChildMemberWithName("ptr")
                .unsigned
            )
            if self._typ == QCborValueType.MAP:
                self._size = self._size // 2
        return False

    def has_children(self):
        return True

    def _get_string_at(self, n: int, el: None | SBValue = None):
        assert self._elements
        if not el:
            el = self._elements.GetChildAtIndex(n).GetNonSyntheticValue()
        assert el
        return self._static_get_string_for(
            self._valobj,
            el,
            self._data_ptr,
            self._pointer_size,
            self._target,
            self._process,
        )

    @staticmethod
    def _static_get_string_for(
        root_val: SBValue,
        el: SBValue,
        data_ptr: int,
        ptr_size: int | None = None,
        target: SBTarget | None = None,
        process: SBProcess | None = None,
    ):
        if not target:
            target = root_val.GetTarget()
            assert target
        if not process:
            process = root_val.GetProcess()
            assert process
        if not ptr_size:
            ptr_size = target.GetAddressByteSize()
        flags = el.GetChildMemberWithName("flags").GetSyntheticValue().unsigned
        if flags == 0:
            return _valobj_from_str(root_val, "", "")
        value = el.GetChildAtIndex(0).GetChildAtIndex(0).unsigned
        addr = data_ptr + value
        len = process.ReadPointerFromMemory(addr, SBError())
        if flags & QCborValueFlag.STRING_IS_UTF16:
            ty = target.GetBasicType(lldb.eBasicTypeChar16).GetArrayType(len // 2)
        else:
            ty = target.GetBasicType(lldb.eBasicTypeChar).GetArrayType(len)
        return root_val.CreateValueFromAddress("", addr + ptr_size, ty)


class QCborValueSyntheticProvider(_CborSyntheticProviderBase):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._cbor_type = None

    def _get_cbor_type(self):
        if not self._cbor_type:
            self._cbor_type = self._target.FindFirstType(
                "QCborContainerPrivate"
            ).GetPointerType()
        return self._cbor_type

    def _get_type_container(self):
        typ = self._valobj.GetChildMemberWithName("t").unsigned
        container = self._valobj.GetChildMemberWithName("container")
        if container.GetNumChildren() == 0:
            container = container.Cast(self._get_cbor_type())

        return typ, container


class QtCborElementSyntheticProvider(_CborSyntheticProviderBase):
    def _get_type_container(self):
        union = self._valobj.GetChildAtIndex(0)
        typ = self._valobj.GetChildMemberWithName("type").unsigned
        container = union.GetChildMemberWithName("container")
        return typ, container


class QJsonObjectSyntheticProvider(_CborSyntheticProviderBase):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._priv_ptr = valobj.target.FindFirstType(
            "QCborContainerPrivate"
        ).GetPointerType()

    def _get_type_container(self):
        container = (
            self._valobj.GetChildAtIndex(0)
            .GetChildMemberWithName("d")
            .GetChildAtIndex(0)
            .Cast(self._priv_ptr)
        )
        return QCborValueType.MAP, container


class QJsonArraySyntheticProvider(_CborSyntheticProviderBase):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._priv_ptr = valobj.target.FindFirstType(
            "QCborContainerPrivate"
        ).GetPointerType()

    def _get_type_container(self):
        container = (
            self._valobj.GetChildAtIndex(0)
            .GetChildMemberWithName("d")
            .GetChildAtIndex(0)
            .Cast(self._priv_ptr)
        )
        return QCborValueType.ARRAY, container


class QJsonValueSyntheticProvider(_ExpandingSyntheticProvider):
    def _get_value(self, valobj: SBValue) -> SBValue:
        return valobj.GetChildAtIndex(0).GetSyntheticValue()


def _valobj_from_signed(source: SBValue, val: int, name="") -> SBValue:
    ty: SBType = source.target.GetBasicType(lldb.eBasicTypeLongLong)
    data = SBData.CreateDataFromInt(val, ty.GetByteSize())
    return source.CreateValueFromData(name, data, ty)


def _valobj_from_str(source: SBValue, val: str, name="") -> SBValue:
    ty: SBType = source.target.GetBasicType(lldb.eBasicTypeChar).GetArrayType(len(val))
    data = SBData.CreateDataFromCString(source.process.GetByteOrder(), 8, val)
    return source.CreateValueFromData(name, data, ty)


def _prefer_synthetic(value: SBValue) -> SBValue:
    synth = value.GetSyntheticValue()
    if synth:
        return synth
    return value


def _numeric_index(name: str) -> int | None:
    name = name.removeprefix("[").removesuffix("]")
    try:
        return int(name)
    except ValueError:
        return None


def _qdatetime_data(valobj: SBValue) -> tuple[datetime.datetime, bool] | None:
    d: SBValue = valobj.GetChildMemberWithName("d")
    d_ptr: SBValue = d.GetChildMemberWithName("d")
    d_val = d_ptr.unsigned
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

    dt_priv = valobj.target.FindFirstType("QDateTimePrivate").GetPointerType()
    if not dt_priv:
        return
    d_ptr = d_ptr.Cast(dt_priv)
    status = (
        d_ptr.GetChildMemberWithName("m_status").GetChildMemberWithName("i").unsigned
    )
    if (status & QDateTimeConstants.STATUS_VALID_DATETIME_MASK) == 0:
        return None
    msec = d_ptr.GetChildMemberWithName("m_msecs").signed
    offset = d_ptr.GetChildMemberWithName("m_offsetFromUtc").signed
    # datetime expects a UTC timestamp
    dt = datetime.datetime.fromtimestamp(
        msec / 1000.0 - offset, datetime.timezone(datetime.timedelta(seconds=offset))
    )
    return dt, False
