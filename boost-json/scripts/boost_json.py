import lldb
from lldb import (
    SBValue,
    SBType,
    SBTarget,
    SBDebugger,
)
from nerix_common import (
    ArraySyntheticProvider,
    make_add_summary,
    make_add_summary_string,
    make_add_synthetic,
    numeric_index,
    ExpandingSyntheticProvider,
    DispatchedSynthetic,
)
from typing import Union, Optional


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    dbg.HandleCommand("type category define -e boost-json -l c++")

    add_summary = make_add_summary(dbg, "boost-json", __name__, include_own=False)
    add_summary_string = make_add_summary_string(dbg, "boost-json")
    add_synthetic = make_add_synthetic(dbg, "boost-json", __name__)

    add_summary("String", other_names=["boost::json::string"])

    add_synthetic("BArray", other_names=["boost::json::array"])
    add_summary_string("boost::json::array", "[ size=${svar%#} ]")

    add_synthetic("Value", other_names=["boost::json::value"])
    add_summary("Value", other_names=["boost::json::value"])

    add_synthetic("Object", other_names=["boost::json::object"])
    add_summary_string("boost::json::object", "\\{ size=${svar%#} \\}")

    add_summary_string("boost::json::key_value_pair", "(${var.key_}, ${var.value_})")
    add_synthetic("KeyValuePair", other_names=["boost::json::key_value_pair"])


def StringSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
):
    impl: SBValue = valobj.GetChildMemberWithName("impl_")
    ity: SBType = impl.GetType()
    impl = impl.GetChildAtIndex(0)
    tgt = impl.GetTarget()
    if hasattr(StringSummaryProvider, "k_short"):
        k_short = StringSummaryProvider.k_short
    else:
        k_short = (
            ity.GetStaticFieldWithName("short_string_")
            .GetConstantValue(tgt)
            .GetValueAsUnsigned()
        )
        if k_short == 0:
            k_short = Kind.String | 0x80  # FIXME: bug in native PDB reader
        StringSummaryProvider.k_short = k_short

    sbo: SBValue = impl.GetChildMemberWithName("s_")
    kind = sbo.GetChildMemberWithName("k").GetValueAsUnsigned()
    if kind == k_short:
        return (
            sbo.GetChildMemberWithName("buf")
            .AddressOf()
            .Cast(valobj.GetTarget().GetBasicType(lldb.eBasicTypeChar).GetPointerType())
            .GetSummary()
        )

    if hasattr(StringSummaryProvider, "k_key"):
        k_key = StringSummaryProvider.k_key
    else:
        k_key = (
            ity.GetStaticFieldWithName("key_string_")
            .GetConstantValue(tgt)
            .GetValueAsUnsigned()
        )
        if k_key == 0:
            k_key = Kind.String | 0x40  # FIXME: bug in native PDB reader
        StringSummaryProvider.k_key = k_key

    char = tgt.GetBasicType(lldb.eBasicTypeChar)
    if kind == k_key:
        k: SBValue = impl.GetChildMemberWithName("k_")
        n = k.GetChildMemberWithName("n").GetValueAsUnsigned()
        ptr = k.GetChildMemberWithName("s")
        if n == 0:
            return '""'
        return ptr.Dereference().Cast(char.GetArrayType(n))

    t = impl.GetChildMemberWithName("p_").GetChildMemberWithName("t")
    n = t.GetChildMemberWithName("size").GetValueAsUnsigned()
    if n == 0:
        return '""'
    return valobj.CreateValueFromAddress(
        "", t.GetValueAsAddress() + 8, char.GetArrayType(n)
    ).GetSummary()


class BArraySyntheticProvider(ArraySyntheticProvider):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._value_ty = valobj.GetTarget().FindFirstType("boost::json::value")

    def _pointer_and_size(self, valobj: SBValue) -> tuple[Union[SBValue, int], int]:
        tbl: SBValue = valobj.GetChildMemberWithName("t_")
        s = tbl.GetChildMemberWithName("size").GetValueAsUnsigned()
        return tbl.GetValueAsAddress() + 8, s

    def _array_type(self, valobj: SBValue):
        return self._value_ty


class Kind:
    Null = 0
    Bool = 1
    Int64 = 2
    Uint64 = 3
    Double = 4
    String = 5
    Array = 6
    Object = 7
    _init = False

    @staticmethod
    def ensure_init(tgt: SBTarget):
        if Kind._init:
            return
        Kind._init = True
        k = tgt.FindFirstType("boost::json::kind").GetEnumMembers()
        for it in k:
            v = it.GetValueAsUnsigned()
            name = it.GetName()
            if name == "null":
                Kind.Null = v
            elif name == "bool_":
                Kind.Bool = v
            elif name == "int64":
                Kind.Int64 = v
            elif name == "uint64":
                Kind.Uint64 = v
            elif name == "double_":
                Kind.Double = v
            elif name == "string":
                Kind.String = v
            elif name == "array":
                Kind.Array = v
            elif name == "object":
                Kind.Object = v


def ValueSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
):
    v = valobj.GetChildAtIndex(ValueSyntheticProvider.VALUE_IDX)
    if not v:
        return "null"
    s = v.GetSummary()
    if s:
        return s
    return ""


class ValueSyntheticProvider(ExpandingSyntheticProvider):
    VALUE_IDX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        Kind.ensure_init(valobj.GetTarget())

    def get_child_at_index(self, idx: int):
        if idx == self.VALUE_IDX:
            return self._val
        return super().get_child_at_index(idx)

    def _get_value(self, valobj: SBValue) -> Optional[SBValue]:
        u: SBValue = valobj.GetChildAtIndex(0)
        sca: SBValue = u.GetChildMemberWithName("sca_")
        kind = sca.GetChildMemberWithName("k").GetValueAsUnsigned()
        kind_tag = kind & 0xF
        if kind_tag == Kind.Null:
            return None
        elif kind_tag == Kind.Bool:
            return sca.GetChildAtIndex(2).GetChildMemberWithName("b")
        elif kind_tag == Kind.Int64:
            return sca.GetChildAtIndex(2).GetChildMemberWithName("i")
        elif kind_tag == Kind.Uint64:
            return sca.GetChildAtIndex(2).GetChildMemberWithName("u")
        elif kind_tag == Kind.Double:
            return sca.GetChildAtIndex(2).GetChildMemberWithName("d")
        elif kind_tag == Kind.String:
            return u.GetChildMemberWithName("str_")
        elif kind_tag == Kind.Array:
            return u.GetChildMemberWithName("arr_").GetSyntheticValue()
        elif kind_tag == Kind.Object:
            return u.GetChildMemberWithName("obj_").GetSyntheticValue()

    def get_value(self):
        return self._val


class ObjectSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._target = valobj.GetTarget()
        self._kv_ty = self._target.FindFirstType("boost::json::key_value_pair")
        self._char_ty = self._target.GetBasicType(lldb.eBasicTypeChar)
        self._kv_size = self._kv_ty.GetByteSize()
        self._size = 0
        self._base_addr = 0

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return numeric_index(name)  # FIXME: check names here

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx > self._size:
            return
        kv: SBValue = self._valobj.CreateValueFromAddress(
            "", self._base_addr + idx * self._kv_size, self._kv_ty
        ).GetNonSyntheticValue()
        len = kv.GetChildMemberWithName("len_").GetValueAsUnsigned()
        key = (
            kv.GetChildMemberWithName("key_")
            .Dereference()
            .Cast(self._char_ty.GetArrayType(len))
            .GetSummary()
        )
        return kv.GetChildMemberWithName("value_").Clone(f"[{key}]")

    def update(self):
        t: SBValue = self._valobj.GetChildMemberWithName("t_")
        self._base_addr = (
            t.GetValueAsAddress() + t.GetType().GetPointeeType().GetByteSize()
        )
        self._size = t.GetChildMemberWithName("size").GetValueAsUnsigned()

    def has_children(self):
        return True


class KeyValuePairSyntheticProvider(DispatchedSynthetic):
    items = [
        ("Key", "key_"),
        ("Value", "value_"),
    ]
