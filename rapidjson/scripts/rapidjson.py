import lldb
from lldb import (
    SBValue,
    SBDebugger,
)
from nerix_common import (
    make_add_summary,
    make_add_synthetic,
    numeric_index,
)
from typing import Optional


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    dbg.HandleCommand("type category define -e rapidjson -l c++")

    add_summary = make_add_summary(dbg, "rapidjson", __name__, include_own=False)
    add_synthetic = make_add_synthetic(dbg, "rapidjson", __name__)

    add_summary("GenericValue", regex="^rapidjson::GenericValue<.*>$")
    add_synthetic("GenericValue", regex="^rapidjson::GenericValue<.*>$")


class Type:
    kNullType = 0
    kFalseType = 1
    kTrueType = 2
    kObjectType = 3
    kArrayType = 4
    kStringType = 5
    kNumberType = 6


class BaseFlags:
    kBoolFlag = 0x0008
    kNumberFlag = 0x0010
    kIntFlag = 0x0020
    kUintFlag = 0x0040
    kInt64Flag = 0x0080
    kUint64Flag = 0x0100
    kDoubleFlag = 0x0200
    kStringFlag = 0x0400
    kCopyFlag = 0x0800
    kInlineStrFlag = 0x1000


class Flags:
    kShortStringFlag = (
        Type.kStringType
        | BaseFlags.kStringFlag
        | BaseFlags.kCopyFlag
        | BaseFlags.kInlineStrFlag
    )
    kNumberIntFlag = (
        Type.kNumberType
        | BaseFlags.kNumberFlag
        | BaseFlags.kIntFlag
        | BaseFlags.kInt64Flag
    )
    kNumberUintFlag = (
        Type.kNumberType
        | BaseFlags.kNumberFlag
        | BaseFlags.kUintFlag
        | BaseFlags.kUint64Flag
        | BaseFlags.kInt64Flag
    )
    kNumberInt64Flag = Type.kNumberType | BaseFlags.kNumberFlag | BaseFlags.kInt64Flag
    kNumberUint64Flag = Type.kNumberType | BaseFlags.kNumberFlag | BaseFlags.kUint64Flag
    kNumberDoubleFlag = Type.kNumberType | BaseFlags.kNumberFlag | BaseFlags.kDoubleFlag


_ADDRESS_MASK = 0x0000FFFFFFFFFFFF


def GenericValueSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
):
    raw = valobj.GetNonSyntheticValue()
    data = raw.GetChildMemberWithName("data_")
    flags = (
        data.GetChildMemberWithName("f")
        .GetChildMemberWithName("flags")
        .GetValueAsUnsigned()
    )
    match flags & 0x7:
        case Type.kNullType:
            return "null"
        case Type.kFalseType | Type.kTrueType | Type.kNumberType:
            return ""
        case Type.kObjectType:
            return f"{{ size={valobj.GetNumChildren()} }}"
        case Type.kArrayType:
            return f"[ size={valobj.GetNumChildren()} ]"
        case Type.kStringType:
            return StringSummary(data, flags)
        case x:
            return f"Unknown type {x} (flags={flags:#x})"


def StringSummary(data: SBValue, flags: Optional[int] = None):
    if flags is None:
        flags = (
            data.GetChildMemberWithName("f")
            .GetChildMemberWithName("flags")
            .GetValueAsUnsigned()
        )

    if flags == Flags.kShortStringFlag:
        arr = data.GetChildMemberWithName("ss").GetChildMemberWithName("str")
        ptr = arr.GetType().GetArrayElementType().GetPointerType()
        return arr.AddressOf().Cast(ptr).GetSummary()

    s = data.GetChildMemberWithName("s")
    len = s.GetChildMemberWithName("length").GetValueAsUnsigned()
    if len == 0:
        return '""'
    str = s.GetChildMemberWithName("str")
    char = str.GetType().GetPointeeType()
    ptr = str.GetValueAsAddress() & _ADDRESS_MASK
    return data.CreateValueFromAddress("", ptr, char.GetArrayType(len)).GetSummary()


class GenericValueSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._type = Type.kNullType
        self._target = valobj.GetTarget()
        self._val = None
        self._size = 0
        self._element_base = 0
        self._member_type = None

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self._size or self._member_type is None:
            return
        if self._type == Type.kArrayType:
            return self._valobj.CreateValueFromAddress(
                f"[{idx}]",
                self._element_base + self._member_type.GetByteSize() * idx,
                self._member_type,
            )
        elif self._type == Type.kObjectType:
            member = self._valobj.CreateValueFromAddress(
                "",
                self._element_base + self._member_type.GetByteSize() * idx,
                self._member_type,
            )
            member.SetPreferSyntheticValue(False)
            value = member.GetChildMemberWithName("value")
            name = member.GetChildMemberWithName("name").GetSummary()
            return value.Clone(f"[{name}]")

    def get_value(self):
        return self._val

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return numeric_index(name)  # FIXME: check names here

    def update(self):
        self._size = 0
        self._val = None
        self._element_base = 0
        data = self._valobj.GetChildMemberWithName("data_")
        flags = (
            data.GetChildMemberWithName("f")
            .GetChildMemberWithName("flags")
            .GetValueAsUnsigned()
        )
        self._type = flags & 0x7
        match self._type:
            case Type.kNullType:
                pass
            case Type.kFalseType:
                self._val = self._valobj.CreateBoolValue("", False)
            case Type.kTrueType:
                self._val = self._valobj.CreateBoolValue("", True)
            case Type.kNumberType:
                n = data.GetChildMemberWithName("n")
                if (flags & Flags.kNumberIntFlag) == Flags.kNumberIntFlag:
                    self._val = n.GetChildMemberWithName("i").GetChildMemberWithName(
                        "i"
                    )
                elif (flags & Flags.kNumberUintFlag) == Flags.kNumberUintFlag:
                    self._val = n.GetChildMemberWithName("u").GetChildMemberWithName(
                        "u"
                    )
                elif (flags & Flags.kNumberInt64Flag) == Flags.kNumberInt64Flag:
                    self._val = n.GetChildMemberWithName("i64")
                elif (flags & Flags.kNumberUint64Flag) == Flags.kNumberUint64Flag:
                    self._val = n.GetChildMemberWithName("u64")
                elif (flags & Flags.kNumberDoubleFlag) == Flags.kNumberDoubleFlag:
                    self._val = n.GetChildMemberWithName("d")
            case Type.kObjectType:
                o = data.GetChildMemberWithName("o")
                self._size = o.GetChildMemberWithName("size").GetValueAsUnsigned()
                members = o.GetChildMemberWithName("members")
                self._element_base = members.GetValueAsAddress() & _ADDRESS_MASK
                self._member_type = members.GetType().GetPointeeType()
            case Type.kArrayType:
                a = data.GetChildMemberWithName("a")
                self._size = a.GetChildMemberWithName("size").GetValueAsUnsigned()
                elements = a.GetChildMemberWithName("elements")
                self._element_base = elements.GetValueAsAddress() & _ADDRESS_MASK
                self._member_type = elements.GetType().GetPointeeType()
            case Type.kStringType:
                pass

    def has_children(self):
        return self._size > 0
