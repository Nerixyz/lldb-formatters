from typing import Callable
import lldb
from lldb import SBDebugger, SBValue, SBTarget, SBType


def make_add_summary_string(dbg: SBDebugger, category: str):
    def add_summary_string(
        type_names: str | list[str],
        summary: str,
        *,
        regex=False,
        no_value=False,
    ):
        if isinstance(type_names, str):
            type_names = [type_names]
        cmd = f"type summary add -w {category} --summary-string '{summary}' {'-x' if regex else ''} {'-v' if no_value else ''} "
        cmd += " ".join(map(lambda it: f'"{it}"', type_names))
        dbg.HandleCommand(cmd)

    return add_summary_string


def make_add_summary(dbg: SBDebugger, category: str, modname: str, *, include_own=True):
    def add_summary(
        type_name: str, *, regex: str | None = None, other_names: list[str] = []
    ):
        type_names = other_names + ([type_name] if include_own else [])
        cmd = f"type summary add -w {category} -F {modname}.{type_name}SummaryProvider "
        if regex:
            cmd += f' -x "{regex}"'
        else:
            cmd += " ".join(map(lambda it: f'"{it}"', type_names))
        dbg.HandleCommand(cmd)

    return add_summary


def make_add_synthetic(dbg: SBDebugger, category: str, modname: str):
    def add_synthetic(
        name: str,
        *,
        regex: str | None = None,
        type_name: str | None = None,
        other_names: list[str] = [],
    ):
        cmd = f"type synthetic add -w {category} -l {modname}.{name}SyntheticProvider"
        if regex:
            cmd += f' -x "{regex}"'
        else:
            type_name = type_name if type_name else name
            cmd += f' "{type_name}" ' + " ".join(map(lambda it: f'"{it}"', other_names))
        dbg.HandleCommand(cmd)

    return add_synthetic


def numeric_index(name: str) -> int | None:
    name = name.removeprefix("[").removesuffix("]")
    try:
        return int(name)
    except ValueError:
        return None


class ExpandingSyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj
        self._val = None

    def update(self):
        self._val = self._get_value(self._backend)
        return False

    def _get_value(self, valobj: SBValue) -> SBValue | None:
        raise NotImplementedError()

    def num_children(self):
        if self._val is None:
            return 0
        return self._val.GetNumChildren()

    def get_child_index(self, name: str):
        if self._val is None:
            return 0
        return self._val.GetChildMemberWithName(name)

    def get_child_at_index(self, idx: int):
        if self._val is None:
            return None
        return self._val.GetChildAtIndex(idx)

    def has_children(self):
        return self._val is not None


class DispatchedSynthetic:
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


class ArraySyntheticProvider:
    def __init__(self, valobj: SBValue, internal_dict):
        self._backend = valobj
        self._size = 0
        self._base_addr = 0
        self._resolved_type = None
        self._offset = 0

    def num_children(self):
        return self._size

    def get_child_index(self, name: str):
        return numeric_index(name)

    def get_child_at_index(self, idx: int):
        if idx < 0 or idx >= self._size or self._resolved_type is None:
            return None
        return self._backend.CreateValueFromAddress(
            f"[{idx}]", self._base_addr + self._offset * idx, self._resolved_type
        )

    def has_children(self):
        return self._base_addr != 0 and self._base_addr != lldb.LLDB_INVALID_ADDRESS

    def update(self):
        ptr, size = self._pointer_and_size(self._backend)
        self._size = size
        if isinstance(ptr, int):
            self._resolved_type = self._array_type(SBValue())
            self._base_addr = ptr
        else:
            self._resolved_type = self._array_type(ptr)
            if ptr.TypeIsPointerType():
                self._base_addr = ptr.GetValueAsAddress()
            else:
                self._base_addr = ptr.GetLoadAddress()
        self._offset = self._resolved_type.GetByteSize()
        return False

    def _pointer_and_size(self, valobj: SBValue) -> tuple[SBValue | int, int]:
        raise NotImplementedError()

    def _array_type(self, valobj: SBValue) -> SBType:
        raise NotImplementedError()


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
