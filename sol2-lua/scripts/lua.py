import traceback

import lldb
from lldb import (
    SBFrame,
    SBFrameList,
    SBValue,
    SBType,
    SBTarget,
    SBData,
    SBError,
    SBDebugger,
    LLDB_INVALID_ADDRESS,
    SBValueList,
    SBVariablesOptions,
)
from lldb.plugins.scripted_frame_provider import ScriptedFrameProvider
from lldb.plugins.scripted_process import ScriptedFrame
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
from lua_constants import OpCode


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

    if dbg.GetNumTargets() > 0:
        dbg.HandleCommand("target frame-provider clear")
        dbg.HandleCommand(
            f"target frame-provider register -C {__name__}.LuaFrameProvider"
        )


class LuaFrameProvider(ScriptedFrameProvider):
    def __init__(self, input_frames: SBFrameList, args):
        super().__init__(input_frames, args)
        self._resolved_frames: list[int | LuaFrame] | None = None

    @staticmethod
    def get_description():
        return "Show each frame twice"

    @staticmethod
    def applies_to_thread(thread):
        return True

    def get_frame_at_index(self, index):
        if self._resolved_frames is not None:
            if index < len(self._resolved_frames):
                return self._resolved_frames[index]
            return index
        # return index // 2
        if self.input_frames is None:
            return index
        f = self.input_frames.GetFrameAtIndex(index)
        n = f.GetFunction().GetMangledName()
        # FIXME: just MS mangling right now
        if n == "?luaV_execute@@YAXPEAUlua_State@@PEAUCallInfo@@@Z":
            self._resolve_frames(index)
            return self.get_frame_at_index(index)
        return index

    def _generate_frames(self, from_idx: int):
        assert self.input_frames is not None
        for index in range(from_idx, len(self.input_frames)):
            f = self.input_frames.GetFrameAtIndex(index)
            yield index
            n = f.GetFunction().GetMangledName()
            if n != "?luaV_execute@@YAXPEAUlua_State@@PEAUCallInfo@@@Z":
                continue

            ci = f.FindVariable("ci")
            while _not_nullptr(ci):
                func_closure = (
                    ci.GetChildMemberWithName("func")
                    .GetChildMemberWithName("p")
                    .GetChildMemberWithName("val")
                    .GetSyntheticValue()
                )
                if not func_closure:
                    break
                src = _get_sourcename(func_closure)
                if src is None:
                    break  # C function - should be in call stack before
                line = _try_get_line(ci, func_closure)
                yield LuaFrame(self.thread, ci, func_closure, src, line)
                ci = ci.GetChildMemberWithName("previous")

    def _resolve_frames(self, from_idx: int):
        assert self.input_frames is not None
        self._resolved_frames = [i for i in range(from_idx)]
        try:
            for f in self._generate_frames(from_idx):
                self._resolved_frames.append(f)
        except BaseException:
            print(traceback.format_exc())


def _try_get_line(ci: SBValue, closure: SBValue):
    res = _proto_and_pc(ci, closure)
    if res is None:
        return 0
    proto, pc = res
    lineinfo = proto.GetChildMemberWithName("lineinfo").GetValueAsAddress()
    if lineinfo == 0 or lineinfo == LLDB_INVALID_ADDRESS:
        return 0
    code_start = proto.GetChildMemberWithName("code").GetValueAsAddress()
    # pc and code_start are `uint32_t*`
    pc = (pc - code_start) // 4 - 1
    start_pc, baseline = _get_base_line(proto, pc)

    process = proto.GetProcess()
    err = SBError()

    def get_offset(i: int):
        return process.ReadUnsignedFromMemory(lineinfo + i, 1, err)

    while start_pc < pc:
        start_pc += 1
        baseline += get_offset(start_pc)
    return baseline


def _get_base_line(proto: SBValue, pc: int):
    sz_abslineinfo = proto.GetChildMemberWithName(
        "sizeabslineinfo"
    ).GetValueAsUnsigned()
    abslineinfo_base = proto.GetChildMemberWithName("abslineinfo").GetValueAsAddress()
    if sz_abslineinfo == 0:
        return -1, proto.GetChildMemberWithName("linedefined").GetValueAsUnsigned()
    process = proto.GetProcess()
    err = SBError()

    def get_pc(i: int):
        return process.ReadUnsignedFromMemory(abslineinfo_base + i * 8, 4, err)

    if pc < get_pc(0):
        return -1, proto.GetChildMemberWithName("linedefined").GetValueAsUnsigned()

    i = pc // 128 - 1
    cur_pc = 0
    while i + 1 < sz_abslineinfo:
        next_pc = get_pc(i + 1)
        if pc > next_pc:
            break
        i += 1
        cur_pc = next_pc
    # pc + line
    return cur_pc, process.ReadUnsignedFromMemory(abslineinfo_base + i * 8 + 4, 4, err)


def _not_nullptr(v: SBValue):
    addr = v.GetValueAsAddress()
    return addr != 0 and addr != LLDB_INVALID_ADDRESS


def _get_sourcename(closure: SBValue):
    tt = _tt_val(closure.GetNonSyntheticValue().GetChildMemberWithName("tt_"))
    if tt != lua_constants.LUA_VLCL:
        return None
    proto = closure.GetChildMemberWithName("p")
    src = read_tstring(proto.GetChildMemberWithName("source"))
    if src.startswith("@"):
        # filename
        src = src.removeprefix("@").replace("\\", "/").rsplit("/", 1)[1]
        if len(src) < 25:
            return src
        return "[...]" + src[:-20]
    if src.startswith("="):
        src = src.removeprefix("=")
    src = src.strip()
    if len(src) < 25:
        return f'"{src}"'
    return f'"{src[:20]}..."'


# FIXME: This is unused right now.
# Getting the name of the function is a bit more involved.
# We need to interpret the bytecode to get the name.
def _get_funcname(L: SBValue, ci: SBValue):
    """ldebug.c, getfuncname(L, ci, name)"""
    cist = ci.GetChildMemberWithName("callstatus").GetValueAsUnsigned()
    if cist & lua_constants.CIST_TAIL:
        return "(tail call)"
    ci = ci.GetChildMemberWithName("previous")
    if ci.GetValueAsAddress() == 0:
        return "(?)"
    cist = ci.GetChildMemberWithName("callstatus").GetValueAsUnsigned()
    if cist & lua_constants.CIST_HOOKED:
        return "(hooked)"
    if cist & lua_constants.CIST_FIN:
        return "__gc"
    if cist & lua_constants.CIST_C:
        return "(C)"

    ret = _proto_and_pc(ci)
    if ret is None:
        return "(unknown pc)"
    proto, pc = ret

    code_start = proto.GetChildMemberWithName("code").GetValueAsAddress()
    # pc and code_start are `uint32_t*`
    rel_pc = (pc - code_start) // 4 - 1
    if rel_pc < 0:
        return "(invalid pc)"

    process = ci.GetProcess()
    err = SBError()
    insn = process.ReadUnsignedFromMemory(code_start + rel_pc * 4, 4, err)
    if err.Fail():
        return "(failed to read insn)"
    match _get_opcode(insn):
        case OpCode.OP_CALL | OpCode.OP_TAILCALL:
            pass
        case OpCode.OP_TFORCALL:
            return "for iterator"
        case (
            OpCode.OP_SELF
            | OpCode.OP_GETTABUP
            | OpCode.OP_GETTABLE
            | OpCode.OP_GETI
            | OpCode.OP_GETFIELD
        ):
            return "__index"
        case (
            OpCode.OP_SETTABUP
            | OpCode.OP_SETTABLE
            | OpCode.OP_SETI
            | OpCode.OP_SETFIELD
        ):
            return "__newindex"
        case OpCode.OP_MMBIN | OpCode.OP_MMBINI | OpCode.OP_MMBINK:
            c = _get_argc(insn)
            if c < 0 or c >= 25:
                return "(invalid tm)"
            L = L.GetNonSyntheticValue()
            s = (
                L.GetChildMemberWithName("l_G")
                .GetChildMemberWithName("tmname")
                .GetChildAtIndex(c)
                .GetSummary()
            )
            if not s:
                return "(unavailable tm)"
            return s.removeprefix('"').removesuffix('"')
        case OpCode.OP_UNM:
            return "__unm"
        case OpCode.OP_BNOT:
            return "__bnot"
        case OpCode.OP_LEN:
            return "__len"
        case OpCode.OP_CONCAT:
            return "__concat"
        case OpCode.OP_EQ:
            return "__eq"
        case OpCode.OP_LT | OpCode.OP_LTI | OpCode.OP_GTI:
            return "__lt"
        case OpCode.OP_LE | OpCode.OP_LEI | OpCode.OP_GEI:
            return "__le"
        case OpCode.OP_CLOSE | OpCode.OP_RETURN:
            return "__close"
        case x:
            return "(invalid opcode: {x:#x})"


def _get_opcode(insn: int):
    return insn & 0b0111_1111


def _get_arga(insn: int):
    return (insn >> (7)) & 0xFF


def _get_argc(insn: int):
    return (insn >> (7 + 8 + 8)) & 0xFF


def _proto_and_pc(ci: SBValue, closure: SBValue | None = None):
    if closure is None:
        closure = (
            ci.GetChildMemberWithName("func")
            .GetChildMemberWithName("p")
            .GetChildMemberWithName("val")
            .GetSyntheticValue()
        )

    pc = (
        ci.GetChildMemberWithName("u")
        .GetChildMemberWithName("l")
        .GetChildMemberWithName("savedpc")
        .GetValueAsAddress()
    )
    proto = closure.GetChildMemberWithName("p")
    if not proto or pc == lldb.LLDB_INVALID_ADDRESS:
        return None
    return proto, pc


def read_tstring(tstr: SBValue):
    tstr = tstr.GetNonSyntheticValue()
    len = tstr.GetChildMemberWithName("shrlen").GetValueAsUnsigned()
    if len == 0xFF:
        len = (
            tstr.GetChildMemberWithName("u")
            .GetChildMemberWithName("lnglen")
            .GetValueAsUnsigned()
        )
    if len == 0:
        return ""
    ptr = tstr.GetChildMemberWithName("contents").GetLoadAddress()
    err = SBError()
    res = tstr.GetProcess().ReadMemory(ptr, len, err)
    if res is None or err.Fail():
        return ""
    return res.decode()


class LuaFrame(ScriptedFrame):
    def __init__(self, thread, ci: SBValue, closure: SBValue, name: str, line: int):
        args = lldb.SBStructuredData()
        super().__init__(thread, args)
        self.id = ci.GetAddress()
        self.ci = ci
        self.name = f"[Lua] {name}"
        if line != 0:
            self.name += f":{line}"
        self.closure = closure
        self._var_cache = None

    def get_id(self):
        return self.id

    def get_pc(self):
        return None

    def get_function_name(self):
        return self.name

    def is_artificial(self):
        return True

    def is_hidden(self):
        return False

    def get_register_context(self):
        return None

    def get_variables(self, *args):
        if self._var_cache is None:
            self._var_cache = self._get_vars_impl()
        return self._var_cache

    def _get_vars_impl(self):
        vars = SBValueList()
        pp = _proto_and_pc(self.ci, self.closure)
        if pp is None:
            return vars
        proto, pc = pp
        code_start = proto.GetChildMemberWithName("code").GetValueAsAddress()
        # pc and code_start are `uint32_t*`
        pc = (pc - code_start) // 4 - 1
        if pc < 0:
            return vars
        sz_locals = proto.GetChildMemberWithName("sizelocvars").GetValueAsUnsigned()
        locvars = proto.GetChildMemberWithName("locvars")
        stack_base = self.ci.GetChildMemberWithName("func").GetChildMemberWithName("p")
        stk_id_ty = stack_base.GetType().GetPointeeType()
        loc_ty = locvars.GetType().GetPointeeType()
        for i in range(sz_locals):
            local = locvars.CreateChildAtOffset("", i * loc_ty.GetByteSize(), loc_ty)
            startpc = local.GetChildMemberWithName("startpc").GetValueAsUnsigned()
            if startpc > pc:
                break
            endpc = local.GetChildMemberWithName("endpc").GetValueAsUnsigned()
            if pc < endpc:
                name = read_tstring(local.GetChildMemberWithName("varname"))
                if not name:
                    name = f"(unnamed local {i})"
                var = stack_base.CreateChildAtOffset(
                    "", (i + 1) * stk_id_ty.GetByteSize(), stk_id_ty
                ).GetChildMemberWithName("val")
                vars.Append(var.Clone(name))
        return vars


def _tt_val(v: SBValue):
    return v.GetValueAsUnsigned() & 0b11_1111


def TValueSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
) -> str | None:
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
) -> str | None:
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
        self._metatable: SBValue | None = None
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
        self._stack_begin: SBValue | None = None
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
        self._metatable: SBValue | None = None
        self._ptr = None
        self._uvalues: SBValue | None = None

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
    tstring: SBType | None = None,
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
        self._L: SBValue | None = None
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
        self._val: SBValue | None = None
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
) -> str | None:
    child: SBValue = valobj.GetChildAtIndex(
        SolBasicReferenceSyntheticProvider.IDX_VALUE
    )
    if not child:
        return "(empty)"
    s = child.GetSummary()
    return s if s else ""
