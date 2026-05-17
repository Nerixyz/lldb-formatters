# The algorithms here are based on the GDB printers from Boost.Unordered:
# https://github.com/boostorg/unordered/blob/669918498c3ca6eee91bd4ce29153186d300e005/extra/boost_unordered_printers.py
# By Braden Ganetsky distributed under the Boost Software License, Version 1.0.

import lldb
from lldb import (
    SBError,
    SBType,
    SBTypeMember,
    SBValue,
    SBDebugger,
)
from nerix_common import (
    ExpandingSyntheticProvider,
    make_add_summary,
    make_add_summary_string,
    make_add_synthetic,
    numeric_index,
)
from typing import Optional, Generator


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    dbg.HandleCommand("type category define -e boost-unordered -l c++")

    add_summary = make_add_summary(dbg, "boost-unordered", __name__, include_own=False)
    add_summary_string = make_add_summary_string(dbg, "boost-unordered")
    add_synthetic = make_add_synthetic(dbg, "boost-unordered", __name__)

    # This matches a few too many types
    add_summary_string(
        "^boost::unordered::(unordered|concurrent)(_flat|_node)?_(multi)?(map|set)<.*>$",
        "size=${svar%#}",
        regex=True,
    )

    add_synthetic(
        "UnorderedMap", regex="^boost::unordered::unordered_(multi)?(map|set)<.*>$"
    )
    add_summary(
        "FcaIterator",
        regex="^boost::unordered::detail::iterator_detail::(c_)?iterator<.*>$",
    )
    add_synthetic(
        "FcaIterator",
        regex="^boost::unordered::detail::iterator_detail::(c_)?iterator<.*>$",
    )

    add_synthetic(
        "UnorderedFoa",
        regex="^boost::unordered::(unordered|concurrent)_(node|flat)?_(map|set)<.*>$",
    )
    add_summary(
        "FoaIterator",
        regex="^boost::unordered::detail::foa::table_iterator<.*>$",
    )
    add_synthetic(
        "FoaIterator",
        regex="^boost::unordered::detail::foa::table_iterator<.*>$",
    )


class CachedGeneratorProvider:
    def __init__(self) -> None:
        self._reset()

    def _reset(self):
        self._gen: Optional[Generator[SBValue]] = None
        self._size = 0
        self._cached: list[SBValue] = []

    def _make_generator(self) -> Generator[SBValue, None, None]:
        raise NotImplementedError()

    def get_child_index(self, name: str):
        return numeric_index(name)

    def num_children(self):
        return self._size

    def has_children(self):
        return True

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self._size:
            return
        if idx < len(self._cached):
            return self._cached[idx]
        if self._gen is None:
            return

        while idx + 1 > len(self._cached):
            try:
                v = next(self._gen, None)
            except BaseException as e:
                print(e)
                return
            if v is None:
                self._gen = None
                return
            self._cached.append(v)

        if idx < len(self._cached):
            return self._cached[idx]


class UnorderedMapSyntheticProvider(CachedGeneratorProvider):
    def __init__(self, valobj: SBValue, internal) -> None:
        super().__init__()
        self._valobj = valobj
        self._table = SBValue()

    def _make_generator(self) -> Generator[SBValue, None, None]:
        def gen():
            buckets = self._table.GetChildMemberWithName("buckets_")
            inner_size = buckets.GetChildMemberWithName("size_").GetValueAsUnsigned()
            buckets = buckets.GetChildMemberWithName("buckets")
            next_f = _get_field_by_name(buckets.GetType().GetPointeeType(), "next")
            if next_f is None:
                return
            next_off = next_f.GetOffsetInBytes()
            proc = buckets.GetProcess()
            base_bucket = buckets.GetValueAsAddress()
            ptr_size = buckets.GetTarget().GetAddressByteSize()
            err = SBError()
            i = 0
            for bucket_idx in range(inner_size):
                node_addr = proc.ReadPointerFromMemory(
                    base_bucket + bucket_idx * ptr_size + next_off, err
                )
                if err.Fail():
                    return
                if node_addr == 0:
                    continue
                val = self._valobj.CreateValueFromAddress(
                    "", node_addr, next_f.GetType().GetPointeeType()
                )
                while True:
                    t = (
                        val.GetChildMemberWithName("buf")
                        .GetChildMemberWithName("t_")
                        .Clone(f"[{i}]")
                    )
                    i += 1
                    yield t
                    val = val.GetChildMemberWithName("next")
                    if (
                        val.GetValueAsAddress() == 0
                        or val.GetValueAsAddress() == lldb.LLDB_INVALID_ADDRESS
                    ):
                        break

        return gen()

    def update(self):
        try:
            self._reset()
            self._table = self._valobj.GetChildMemberWithName("table_")
            self._size = self._table.GetChildMemberWithName(
                "size_"
            ).GetValueAsUnsigned()
            self._gen = self._make_generator()
        except BaseException as e:
            print(e)


def FcaIteratorSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
):
    raw = valobj.GetNonSyntheticValue()
    p = raw.GetChildMemberWithName("p")
    if (
        p.GetValueAsAddress() == 0
        or raw.GetChildMemberWithName("itb")
        .GetChildMemberWithName("p")
        .GetValueAsAddress()
        == 0
    ):
        return "end"
    s = p.GetChildMemberWithName("buf").GetChildMemberWithName("t_").GetSummary()
    if s:
        return s
    return ""


class FcaIteratorSyntheticProvider(ExpandingSyntheticProvider):
    def _get_value(self, valobj: SBValue) -> Optional[SBValue]:
        p = valobj.GetChildMemberWithName("p")
        if (
            p.GetValueAsAddress() == 0
            or valobj.GetChildMemberWithName("itb")
            .GetChildMemberWithName("p")
            .GetValueAsAddress()
            == 0
        ):
            return None
        return p.GetChildMemberWithName("buf").GetChildMemberWithName("t_")

    def get_value(self):
        return self._val


class UnorderedFoaSyntheticProvider(CachedGeneratorProvider):
    def __init__(self, valobj: SBValue, internal) -> None:
        super().__init__()
        self._valobj = valobj
        self._table = SBValue()
        self.N = 15
        self._sentinel = 1

    def _match_occupied(self, group: SBValue) -> int:
        m = group.GetChildMemberWithName("m")

        def at(i):
            return _unwrap_atomic(m.GetChildAtIndex(i).GetChildAtIndex(0))

        if m.GetNumChildren() == 16:
            bits = [1 << b for b in range(16) if at(b) == 0]
            return 0x7FFF & ~sum(bits)

        xx = at(0) | at(1)
        yy = xx | (xx >> 32)
        return 0x7FFF & (yy | (yy >> 16))

    def _is_sentinel(self, group: SBValue, pos: int) -> bool:
        m = group.GetChildMemberWithName("m")

        def at(i):
            return _unwrap_atomic(m.GetChildAtIndex(i).GetChildAtIndex(0))

        if m.GetNumChildren() == 16:
            return pos == self.N - 1 and at(self.N - 1) == self._sentinel

        return (
            pos == self.N - 1
            and (at(0) & 0x4000400040004000) == 0x4000
            and (at(1) & 0x4000400040004000) == 0
        )

    def _make_generator(self) -> Generator[SBValue, None, None]:
        def gen():
            arrays = self._table.GetChildMemberWithName("arrays")
            arrays.SetPreferSyntheticValue(False)
            groups = arrays.GetChildMemberWithName("groups_")
            elements = arrays.GetChildMemberWithName("elements_")

            p = elements.Dereference()
            pc = groups.Dereference()

            element_size = p.GetType().GetByteSize()
            group_size = pc.GetType().GetByteSize()
            needs_unwrap = _needs_unwrap(p.GetType())

            first = True
            i = 0
            while (
                p.GetLoadAddress() != 0
                and p.GetLoadAddress() != lldb.LLDB_INVALID_ADDRESS
            ):
                if not first or (self._match_occupied(groups) & 1):
                    v = p
                    if needs_unwrap:
                        v = p.GetChildAtIndex(0).Dereference()
                    yield v.Clone(f"[{i}]")
                    i += 1

                first = False

                pc_addr = pc.GetLoadAddress()
                off = pc_addr % group_size
                if off != 0:
                    pc = groups.CreateValueFromAddress("", pc_addr - off, pc.GetType())

                mask = (self._match_occupied(pc) >> (off + 1)) << (off + 1)
                while mask == 0:
                    pc = groups.CreateValueFromAddress(
                        "", pc.GetLoadAddress() + group_size, pc.GetType()
                    )
                    p = elements.CreateValueFromAddress(
                        "", p.GetLoadAddress() + self.N * element_size, p.GetType()
                    )
                    mask = self._match_occupied(pc)

                n = _countr_zero(mask)
                if self._is_sentinel(pc, n):
                    break
                pc = groups.CreateValueFromAddress(
                    "", pc.GetLoadAddress() + n, pc.GetType()
                )
                p = elements.CreateValueFromAddress(
                    "", p.GetLoadAddress() + (n - off) * element_size, p.GetType()
                )

        return gen()

    def update(self):
        try:
            self._reset()
            self._table = self._valobj.GetChildMemberWithName("table_").GetChildAtIndex(
                0
            )
            self._size = _unwrap_atomic(
                self._table.GetChildMemberWithName("size_ctrl").GetChildMemberWithName(
                    "size"
                )
            )
            self._gen = self._make_generator()
        except BaseException as e:
            print(e)


def FoaIteratorSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
):
    raw = valobj.GetNonSyntheticValue()
    p = raw.GetChildMemberWithName("p_")
    if (
        p.GetValueAsAddress() == 0
        or raw.GetChildMemberWithName("pc_").GetValueAsAddress() == 0
    ):
        return "end"
    s = p.Dereference().GetSummary()
    if s:
        return s
    return ""


class FoaIteratorSyntheticProvider(ExpandingSyntheticProvider):
    def _get_value(self, valobj: SBValue) -> Optional[SBValue]:
        p = valobj.GetChildMemberWithName("p_")
        if (
            p.GetValueAsAddress() == 0
            or valobj.GetChildMemberWithName("pc_").GetValueAsAddress() == 0
        ):
            return None
        return p.Dereference()

    def get_value(self):
        return self._val


def _get_field_by_name(ty: SBType, n: str) -> Optional[SBTypeMember]:
    for i in range(ty.GetNumberOfFields()):
        f = ty.GetFieldAtIndex(i)
        if f.GetName() == n:
            return f


def _countr_zero(n: int) -> int:
    for i in range(32):
        if (n & (1 << i)) != 0:
            return i
    return 32


def _needs_unwrap(e: SBType) -> bool:
    if e.IsTypedefType():
        e = e.GetCanonicalType()
    return e.GetName().startswith("boost::unordered::detail::foa::element_type<")


def _unwrap_atomic(v: SBValue) -> int:
    err = SBError()
    res = v.GetValueAsUnsigned(err)
    if err.Success():
        return res
    ty = v.GetType()
    vt = ty.FindDirectNestedType("value_type")
    if not vt:
        vt = ty.GetTemplateArgumentType(0)
    return v.Cast(vt).GetValueAsUnsigned()
