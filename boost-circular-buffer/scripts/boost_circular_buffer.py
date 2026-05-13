import lldb
from lldb import (
    SBValue,
    SBDebugger,
)
from nerix_common import (
    make_add_summary,
    make_add_summary_string,
    make_add_synthetic,
    numeric_index,
)


def __lldb_init_module(dbg: SBDebugger, internal_dict):
    dbg.HandleCommand("type category define -e boost-circular-buffer -l c++")

    add_summary = make_add_summary(
        dbg, "boost-circular-buffer", __name__, include_own=False
    )
    add_summary_string = make_add_summary_string(dbg, "boost-circular-buffer")
    add_synthetic = make_add_synthetic(dbg, "boost-circular-buffer", __name__)

    add_summary_string(
        "^boost::circular_buffer(_space_optimized)?<.*>$", "size=${svar%#}", regex=True
    )
    add_synthetic(
        "CircularBuffer", regex="^boost::circular_buffer(_space_optimized)?<.*>$"
    )

    add_summary("Iterator", regex="^boost::cb_details::iterator<.*>$")
    add_synthetic("Iterator", regex="^boost::cb_details::iterator<.*>$")


class CircularBufferSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._valobj = valobj
        self._size = 0
        self._ty = valobj.GetChildMemberWithName("m_first").GetType().GetPointeeType()
        self._ty_size = self._ty.GetByteSize()
        self._m_first = 0
        self._m_end = 0
        self._m_buff = 0

    def update(self):
        self._size = self._valobj.GetChildMemberWithName("m_size").GetValueAsUnsigned()
        self._m_first = self._valobj.GetChildMemberWithName(
            "m_first"
        ).GetValueAsAddress()
        self._m_end = self._valobj.GetChildMemberWithName("m_end").GetValueAsAddress()
        self._m_buff = self._valobj.GetChildMemberWithName("m_buff").GetValueAsAddress()
        return False

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return numeric_index(name)

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self._size:
            return None
        # p = m_first
        # n = idx
        # p + (n < (m_end - p) ? n : n - (m_end - m_buff))

        if idx < (self._m_end - self._m_first) / self._ty_size:
            off = idx
        else:
            off = idx - (self._m_end - self._m_buff) // self._ty_size

        return self._valobj.CreateValueFromAddress(
            f"[{idx}]", self._m_first + off * self._ty_size, self._ty
        )

    def has_children(self):
        return True


def IteratorSummaryProvider(
    valobj: SBValue, internal_dict: dict, options: lldb.SBTypeSummaryOptions
):
    v = valobj.GetChildAtIndex(IteratorSyntheticProvider.VALUE_IDX)
    if not v:
        return "end"
    s = v.GetSummary()
    if s:
        return s
    return ""


class IteratorSyntheticProvider(lldb.SBSyntheticValueProvider):
    VALUE_IDX = (1 << 32) - 1

    def __init__(self, valobj: SBValue, internal):
        self._valobj = valobj
        self._val = None

    def update(self):
        self._val = None
        end = (
            self._valobj.GetChildMemberWithName("m_buff")
            .GetChildMemberWithName("m_end")
            .GetValueAsAddress()
        )
        if end == lldb.LLDB_INVALID_ADDRESS:
            return

        it = self._valobj.GetChildMemberWithName("m_it")
        addr = it.GetValueAsAddress()
        if addr == 0 or addr >= end:
            return
        self._val = it.Dereference()

    def get_child_at_index(self, idx: int):
        if idx == self.VALUE_IDX:
            return self._val

    def has_children(self):
        return True  # Make sure lldb-dap shows the [raw] entry

    def get_value(self):
        return self._val
