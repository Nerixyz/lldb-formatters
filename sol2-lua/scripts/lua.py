import lldb
from lldb import (
    SBValue,
    SBType,
    SBTarget,
    SBData,
    SBError,
    SBDebugger,
    LLDB_INVALID_ADDRESS,
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
import lua_constants
from typing import Optional


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    dbg.HandleCommand("type category define -e lua -l c++")

    add_summary = make_add_summary(dbg, "lua", __name__)
    add_summary_string = make_add_summary_string(dbg, "lua")
    add_synthetic = make_add_synthetic(dbg, "lua", __name__)

    add_summary("TValue")
    add_summary("TString")
    add_synthetic("TValue")
    add_synthetic("TString")
    add_synthetic("Table")
    add_synthetic("CClosure")
    add_synthetic("GlobalState", type_name="global_State")
    add_synthetic("LuaState", type_name="lua_State")
    add_synthetic("Udata")

    add_synthetic("SolVariadicArgs", type_name="sol::variadic_args")
    any_ref_re = (
        "^sol::basic_(reference|object(_base)?|table_core|protected_function)<.*>$"
    )
    add_synthetic("SolBasicReference", regex=any_ref_re)
    add_summary_string("sol::variadic_args", "size=${svar%#}")
    add_summary("SolBasicReference", regex=any_ref_re)


def _tt_val(v: SBValue):
    return v.GetValueAsUnsigned() & 0b11_1111


def TValueSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    raw: SBValue = valobj.GetNonSyntheticValue()
    tt = _tt_val(raw.GetChildMemberWithName("tt_"))
    match tt:
        case (
            lua_constants.LUA_VNUMFLT
            | lua_constants.LUA_VNUMINT
            | lua_constants.LUA_VLCF
        ):
            return ""
        case lua_constants.LUA_VLIGHTUSERDATA:
            return "lightuserdata"
        case _:
            return _value_summary(raw.GetChildMemberWithName("value_"), tt)


def TStringSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    len = valobj.GetNumChildren()
    raw: SBValue = valobj.GetNonSyntheticValue()
    return (
        raw.GetChildMemberWithName("contents")
        .Cast(valobj.GetTarget().GetBasicType(lldb.eBasicTypeChar).GetArrayType(len))
        .GetSummary()
    )


class TStringSyntheticProvider(ArraySyntheticProvider):
    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue, int]:
        len = valobj.GetChildMemberWithName("shrlen").GetValueAsUnsigned()
        if len == 0xFF:
            len = (
                valobj.GetChildMemberWithName("u")
                .GetChildMemberWithName("lnglen")
                .GetValueAsUnsigned()
            )
        return valobj.GetChildMemberWithName("contents"), len

    def _array_type(self, valobj: SBValue):
        return valobj.GetTarget().GetBasicType(lldb.eBasicTypeChar)


class TableSyntheticProvider:
    MAX_CHILDREN = 1 << 10

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj

        # for tables
        self._metatable: Optional[SBValue] = None
        self._arr_children: list[SBValue] = []
        self._named_children: list[SBValue] = []

        # common types
        self._ty_tvalue: SBType = valobj.GetTarget().FindFirstType("TValue")
        self._ty_node: SBType = valobj.GetTarget().FindFirstType("Node")
        self._ty_tstring_ptr: SBType = (
            valobj.GetTarget().FindFirstType("TString").GetPointerType()
        )
        self._ty_char_arr: SBType = (
            valobj.GetTarget().GetBasicType(lldb.eBasicTypeChar).GetArrayType(0)
        )
        self._tvalue_size = self._ty_tvalue.GetByteSize()
        self._node_size = self._ty_node.GetByteSize()

    def num_children(self):
        return (
            len(self._arr_children)
            + len(self._named_children)
            + (1 if self._metatable is not None else 0)
        )

    def get_child_index(self, name: str):
        return numeric_index(name)

    def get_child_at_index(self, idx: int):
        if idx < 0:
            return None
        if self._metatable is not None:
            if idx == 0:
                return self._metatable
            idx -= 1
        if idx < len(self._arr_children):
            return _maybe_unwrap(self._arr_children[idx])
        idx -= len(self._arr_children)
        if idx >= len(self._named_children):
            return None
        return self._named_child_at_index(self._named_children[idx])

    def _named_child_at_index(self, named: SBValue):
        u = named.GetChildMemberWithName("u")
        key_tt = _tt_val(u.GetChildMemberWithName("key_tt"))
        key_val = u.GetChildMemberWithName("key_val")
        key_name = f"[{_value_summary(key_val, key_tt, self._ty_tstring_ptr)}]"
        return _maybe_unwrap(named.GetChildMemberWithName("i_val")).Clone(key_name)

    def update(self):
        self._arr_children = []
        self._named_children = []
        self._metatable = None
        meta = self._valobj.GetChildMemberWithName("metatable")
        if meta.GetValueAsAddress() != 0:
            self._metatable = meta.Clone("[metatable]")
        alimit = self._valobj.GetChildMemberWithName("alimit").GetValueAsUnsigned()
        array: SBValue = self._valobj.GetChildMemberWithName("array")
        named_size = (
            1 << self._valobj.GetChildMemberWithName("lsizenode").GetValueAsUnsigned()
        )
        node_start: SBValue = self._valobj.GetChildMemberWithName("node")

        # get array children
        if array.GetValueAsAddress() != 0:
            for i in range(min(alimit, self.MAX_CHILDREN)):
                it = array.CreateChildAtOffset(
                    "", self._tvalue_size * i, self._ty_tvalue
                )
                tt = _tt_val(it.GetChildMemberWithName("tt_"))
                if (tt & 0b1111) != 0:
                    self._arr_children.append(it.Clone(f"[{i + 1}]"))
        # get named children
        if node_start.GetValueAsAddress() != 0:
            for i in range(min(named_size, self.MAX_CHILDREN)):
                it = node_start.CreateChildAtOffset(
                    "", self._node_size * i, self._ty_node
                )
                key_tt = _tt_val(
                    it.GetChildMemberWithName("u").GetChildMemberWithName("key_tt")
                )
                if (key_tt & 0b1111) != 0:
                    self._named_children.append(it)

        return False

    def has_children(self):
        return True


def _maybe_unwrap(tvalue: SBValue) -> SBValue:
    tt = _tt_val(tvalue.GetChildMemberWithName("tt_"))
    if tt == lua_constants.LUA_VLCF:
        return tvalue.GetChildMemberWithName("value_").GetChildMemberWithName("f")
    return tvalue


class TValueSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._value = None
        self._expand = None

        # common types
        self._ty_ptr = None
        self._ty_name = ""

    def _inner_ptr(self, name: str) -> SBType:
        if self._ty_ptr is None or self._ty_name != name:
            self._ty_ptr = self._valobj.GetTarget().FindFirstType(name).GetPointerType()
            self._ty_name = name
        return self._ty_ptr

    def num_children(self):
        if self._expand is None:
            return 1 if self._value is not None else 0
        return self._expand.GetNumChildren()

    def get_child_index(self, name: str):
        if self._expand is None:
            return 0
        return self._expand.GetIndexOfChildWithName(name)

    def get_child_at_index(self, idx: int):
        if self._expand is None:
            return self._value
        return self._expand.GetChildAtIndex(idx)

    def _get_gco(self, val_union: SBValue, name: str) -> SBValue:
        return (
            val_union.GetChildMemberWithName("gc")
            .Cast(self._inner_ptr(name))
            .Dereference()
        )

    def update(self):
        self._value = None
        self._expand = None
        tt = _tt_val(self._valobj.GetChildMemberWithName("tt_"))
        self._arr_children = []
        self._named_children = []
        self._metatable = None
        val_union = self._valobj.GetChildMemberWithName("value_")
        match tt:
            case lua_constants.LUA_VTHREAD:
                self._expand = self._get_gco(val_union, "lua_State")
            case lua_constants.LUA_VNUMINT:
                self._value = val_union.GetChildMemberWithName("i")
            case lua_constants.LUA_VNUMFLT:
                self._value = val_union.GetChildMemberWithName("n")
            case lua_constants.LUA_VSHRSTR | lua_constants.LUA_VLNGSTR:
                self._expand = self._get_gco(val_union, "TString")
            case lua_constants.LUA_VLIGHTUSERDATA:
                self._value = val_union.GetChildMemberWithName("p")
            case lua_constants.LUA_VUSERDATA:
                self._expand = self._get_gco(val_union, "Udata")
            case lua_constants.LUA_VPROTO:
                self._expand = self._get_gco(val_union, "Proto")
            case lua_constants.LUA_VUPVAL:
                self._expand = self._get_gco(val_union, "UpVal")
            case lua_constants.LUA_VLCL:
                self._expand = self._get_gco(
                    val_union, "Closure"
                ).GetChildMemberWithName("l")
            case lua_constants.LUA_VLCF:
                self._value = val_union.GetChildMemberWithName("f")
            case lua_constants.LUA_VCCL:
                self._expand = self._get_gco(
                    val_union, "Closure"
                ).GetChildMemberWithName("c")
            case lua_constants.LUA_VTABLE:
                self._expand = self._get_gco(val_union, "Table").GetSyntheticValue()
            case _:
                pass
        if self._expand is not None:
            self._expand.SetPreferSyntheticValue(True)
        if self._value is not None:
            self._value = self._value.Clone("[Value]")
        return False

    def has_children(self):
        return self._expand is not None or self._value is not None

    def get_value(self):
        return self._value


class CClosureSyntheticProvider(DispatchedSynthetic):
    def __init__(self, valobj: SBValue, internal_dict):
        super().__init__(valobj, internal_dict)
        self._tvalue_ty: SBType = (
            self._valobj.GetChildMemberWithName("upvalue")
            .GetType()
            .GetArrayElementType()
        )

    def _get_upvalues(self, valobj: SBValue):
        nup = valobj.GetChildMemberWithName("nupvalues").GetValueAsUnsigned()
        upval = valobj.GetChildMemberWithName("upvalue")
        return upval.Cast(self._tvalue_ty.GetArrayType(nup))

    items = [
        ("function", "f"),
        ("upvalues", _get_upvalues),
    ]


class GlobalStateSyntheticProvider(DispatchedSynthetic):
    items = [
        ("registry", "l_registry"),
        ("main thread", "mainthread"),
    ]


class LuaStateSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._n_stack = 0
        self._stack_begin: Optional[SBValue] = None
        self._global_state = None
        self._ty_tvalue = valobj.GetTarget().FindFirstType("TValue")
        ty_stack_value = valobj.GetTarget().FindFirstType("StackValue")
        self._stack_value_size = ty_stack_value.GetByteSize()

    def num_children(self):
        return 1 + self._n_stack

    def get_child_index(self, name: str):
        name = name.lstrip("[").rstrip("]")
        if name == "Global State":
            return 0
        i = numeric_index(name)
        if i is not None:
            i += 1
        return i

    def get_child_at_index(self, idx: int):
        if idx == 0:
            return self._global_state
        if self._stack_begin is None or (idx - 1) >= self._n_stack:
            return None
        return self._stack_begin.CreateChildAtOffset(
            f"[{idx - 1}]", (idx - 1) * self._stack_value_size, self._ty_tvalue
        )

    def update(self):
        self._global_state = self._valobj.GetChildMemberWithName("l_G").Clone(
            "[Global State]"
        )
        self._n_stack = 0
        ci = self._valobj.GetChildMemberWithName("ci")
        if ci.GetValueAsAddress() == 0:
            return False
        self._stack_begin = ci.GetChildMemberWithName("func").GetChildMemberWithName(
            "p"
        )
        f_addr = self._stack_begin.GetValueAsAddress()  # type: ignore
        top_addr = (
            self._valobj.GetChildMemberWithName("top")
            .GetChildMemberWithName("p")
            .GetValueAsAddress()
        )
        if top_addr < f_addr:
            return False
        self._n_stack = (top_addr - f_addr) // self._stack_value_size
        return False

    def has_children(self):
        return True


class UdataSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        tgt: SBTarget = valobj.GetTarget()
        self._ty_udata0: SBType = tgt.FindFirstType("Udata0")
        self._ty_tvalue: SBType = tgt.FindFirstType("TValue")
        self._tvalue_size = self._ty_tvalue.GetByteSize()
        self._ty_void: SBType = tgt.GetBasicType(lldb.eBasicTypeVoid).GetPointerType()
        self._byte_order = tgt.GetByteOrder()
        self._ptr_byte_size = tgt.GetAddressByteSize()
        self._metatable: Optional[SBValue] = None
        self._ptr = None
        self._uvalues: Optional[SBValue] = None

    def num_children(self):
        return 2 + (1 if self._uvalues is not None else 0)

    def get_child_index(self, name: str):
        name = name.lstrip("[").rstrip("]")
        match name:
            case "value":
                return 0
            case "metatable":
                return 1
            case "user values":
                return 2
        return None

    def get_child_at_index(self, idx: int):
        match idx:
            case 0:
                return self._ptr
            case 1:
                return self._metatable
            case 2:
                return self._uvalues

    def update(self):
        self._metatable = self._valobj.GetChildMemberWithName("metatable").Clone(
            "[metatable]"
        )
        n_uvalues = self._valobj.GetChildMemberWithName("nuvalue").GetValueAsUnsigned()
        if n_uvalues == 0:
            self._uvalues = None
            vo = self._valobj.Cast(self._ty_udata0)
            addr = vo.GetChildMemberWithName("bindata").GetLoadAddress()
        else:
            uv = self._valobj.GetChildMemberWithName("uv")
            self._uvalues = uv.Cast(self._ty_tvalue.GetArrayType(n_uvalues)).Clone(
                "[user values]"
            )
            addr = uv.GetLoadAddress() + (n_uvalues * self._tvalue_size)

        if self._ptr_byte_size == 8:
            data = SBData.CreateDataFromUInt64Array(self._byte_order, 8, [addr])
        else:
            assert self._ptr_byte_size == 4
            data = SBData.CreateDataFromUInt32Array(self._byte_order, 4, [addr])

        self._ptr = self._valobj.CreateValueFromData("[value]", data, self._ty_void)

        return False

    def has_children(self):
        return True


def _value_summary(
    value: SBValue,
    tt: int,
    tstring: Optional[SBType] = None,
):
    match tt:
        case lua_constants.LUA_VNIL:
            return "nil"
        case lua_constants.LUA_VEMPTY:
            return "nil (empty)"
        case lua_constants.LUA_VABSTKEY:
            return "nil (absent key)"
        case lua_constants.LUA_VFALSE:
            return "false"
        case lua_constants.LUA_VTRUE:
            return "true"
        case lua_constants.LUA_VTHREAD:
            return "thread"
        case lua_constants.LUA_VNUMINT:
            i = value.GetChildMemberWithName("i").GetValueAsSigned()
            return str(i)
        case lua_constants.LUA_VNUMFLT:
            n = value.GetChildMemberWithName("n").GetData().GetDouble(SBError(), 0)
            return str(n)
        case lua_constants.LUA_VSHRSTR | lua_constants.LUA_VLNGSTR:
            gc = value.GetChildMemberWithName("gc")
            if tstring is None:
                tstring = value.GetTarget().FindFirstType("TString").GetPointerType()
            return gc.Cast(tstring).GetSummary()
        case lua_constants.LUA_VLIGHTUSERDATA:
            value.GetChildMemberWithName("p").GetSummary()
        case lua_constants.LUA_VUSERDATA:
            return "userdata"
        case lua_constants.LUA_VPROTO:
            return "proto"
        case lua_constants.LUA_VUPVAL:
            return "upvalue"
        case lua_constants.LUA_VLCL:
            return "Lua closure"
        case lua_constants.LUA_VLCF:
            return "light C function"
        case lua_constants.LUA_VCCL:
            return "C closure"
        case lua_constants.LUA_VTABLE:
            return "table"
        case _:
            return "(unknown)"


# ========================
#           Sol
# ========================


class SolVariadicArgsSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._L: Optional[SBValue] = None
        self._begin = 0
        self._end = 0

    def num_children(self):
        return self._end - self._begin

    def get_child_index(self, name: str):
        return numeric_index(name)

    def get_child_at_index(self, idx: int):
        if self._L is None or idx < 0 or idx >= self.num_children():
            return None
        # +1 for the global state
        return self._L.GetChildAtIndex(idx + 1 + self._begin).Clone(f"[{idx}]")

    def update(self):
        self._L = self._valobj.GetChildMemberWithName("L").GetSyntheticValue()
        self._begin = self._valobj.GetChildMemberWithName("index").GetValueAsUnsigned()
        self._end = (
            self._valobj.GetChildMemberWithName("stacktop").GetValueAsUnsigned() + 1
        )
        if self._end < self._begin:
            self._end = self._begin
        return False

    def has_children(self):
        return True


class SolBasicReferenceSyntheticProvider(ExpandingSyntheticProvider):
    IDX_VALUE = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._val: Optional[SBValue] = None
        self._ty_table = valobj.GetTarget().FindFirstType("Table").GetPointerType()
        self._ty_tvalue: SBType = valobj.GetTarget().FindFirstType("TValue")
        self._tvalue_size = self._ty_tvalue.GetByteSize()

    def update(self):
        self._val = None
        ref = self._valobj.GetChildMemberWithName("ref").GetValueAsSigned()
        if ref <= 0 and ref != lua_constants.LUA_REFNIL:
            return False
        l_g: SBValue = self._valobj.GetChildMemberWithName(
            "luastate"
        ).GetChildMemberWithName("l_G")
        if ref == lua_constants.LUA_REFNIL:
            self._val = l_g.GetChildMemberWithName("nilvalue").GetSyntheticValue()
            return False

        l_reg: SBValue = l_g.GetChildMemberWithName("l_registry")
        l_reg_tt = _tt_val(l_reg.GetChildMemberWithName("tt_"))
        if l_reg_tt != lua_constants.LUA_TTABLE:
            return False  # not a table?
        l_reg_table: SBValue = (
            l_reg.GetChildMemberWithName("value_")
            .GetChildMemberWithName("gc")
            .Cast(self._ty_table)
        )
        alimit = l_reg_table.GetChildMemberWithName("alimit").GetValueAsUnsigned()
        if ref > alimit:
            return False
        array = l_reg_table.GetChildMemberWithName("array")
        addr = array.GetValueAsAddress()
        if addr != 0 and addr != LLDB_INVALID_ADDRESS:
            self._val = array.CreateChildAtOffset(
                "", self._tvalue_size * (ref - 1), self._ty_tvalue
            ).GetSyntheticValue()
        return False

    def num_children(self):
        if self._val is None:
            return 0
        return self._val.GetNumChildren()

    def get_child_index(self, name: str):
        if self._val is None:
            return None
        return self._val.GetIndexOfChildWithName(name)

    def get_child_at_index(self, idx: int):
        if self._val is None:
            return None
        if idx == self.IDX_VALUE:
            return self._val
        return self._val.GetChildAtIndex(idx)

    def has_children(self):
        return True

    def get_value(self):
        return self._val


def SolBasicReferenceSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> Optional[str]:
    child: SBValue = valobj.GetChildAtIndex(
        SolBasicReferenceSyntheticProvider.IDX_VALUE
    )
    if not child:
        return "(empty)"
    s = child.GetSummary()
    return s if s else ""
