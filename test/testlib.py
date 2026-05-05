from dataclasses import dataclass
import unittest
import lldb
from lldb import (
    SBDebugger,
    SBTarget,
    SBProcess,
    SBThread,
    SBFrame,
    SBCommandInterpreter,
    SBCommandReturnObject,
    SBValue,
    SBError,
    SBBreakpoint,
    SBFileSpec,
    SBLaunchInfo,
)
import gc
import re
import os
import configuration
from pathlib import Path
from typing import Any


class TestCase(unittest.TestCase):
    dbg: SBDebugger
    ci: SBCommandInterpreter
    res: SBCommandReturnObject

    _test_dir: str

    def setUp(self) -> None:
        self.dbg = SBDebugger.Create()
        self.dbg.SetAsync(False)
        self.ci = self.dbg.GetCommandInterpreter()
        self.res = SBCommandReturnObject()
        self._test_dir = os.path.dirname(configuration.test_path)

        root_dir = Path(__file__).parent.parent
        self.runCmd(f"command script import {root_dir}/scripts/nerix_common.py")
        for file in configuration.scripts:
            self.runCmd(f"command script import {file}")

    def tearDown(self) -> None:
        gc.collect()
        targets = []
        for target in self.dbg:
            if target:
                targets.append(target)
                process = target.GetProcess()
                if process:
                    process.Kill()
        for target in targets:
            self.dbg.DeleteTarget(target)

        SBDebugger.Destroy(self.dbg)
        del self.dbg

    def target(self) -> SBTarget:
        if not self.dbg:
            raise Exception("Invalid debugger instance")
        return self.dbg.GetSelectedTarget()

    def process(self) -> SBProcess:
        return self.target().GetProcess()

    def thread(self) -> SBThread:
        return self.process().GetSelectedThread()

    def frame(self) -> SBFrame:
        if not self.dbg:
            raise Exception("Invalid debugger instance")
        return self.thread().GetSelectedFrame()

    def runCmd(self, cmd: str):
        self.ci.HandleCommand(cmd, self.res)
        if self.res.Succeeded():
            return

        output = f"Run: {cmd}"
        if self.res.GetOutput():
            output += "\nCommand output:\n" + self.res.GetOutput()
        if self.res.GetError():
            output += "\nError output:\n" + self.res.GetError()
        self.assertTrue(self.res.Succeeded(), output)

    def assertMatch(self, pattern: str | re.Pattern, target: str, msg=None):
        if isinstance(pattern, re.Pattern):
            self.assertRegex(target, pattern, msg)
        else:
            self.assertEqual(pattern, target, msg)

    def assertSuccess(self, obj: SBError, msg=None):
        if not obj.Success():
            error = obj.GetCString()
            self.fail(self._formatMessage(msg, f"'{error}' is not success"))

    def assertVarPath(self, path: str, check: "ValueCheck"):
        val = self.frame().GetValueForVariablePath(path)
        check.check(self, val, f"Evaluating '{path}'")

    def _setupTarget(self) -> SBTarget:
        tgt = self.dbg.CreateTarget(configuration.binary_path)
        self.assertTrue(tgt, f"{configuration.binary_path} is not a valid target")
        return tgt

    def assertStopped(self, process: SBProcess):
        if process.state != lldb.eStateStopped:
            msg = f"state={process.state}"
            if process.state == lldb.eStateExited:
                msg += f", exit-code={process.GetExitStatus()}"
            self.fail(f"Process is not stopped: {msg}")

    def _launchToBreakpoint(self, tgt: SBTarget, breakpoint: SBBreakpoint):
        launch_info: SBLaunchInfo = tgt.GetLaunchInfo()
        launch_info.SetWorkingDirectory(self._test_dir)
        err = SBError()
        process = tgt.Launch(launch_info, err)

        self.assertTrue(
            process and err.Success(),
            f"Failed to launch {configuration.binary_path}: {err.GetCString()}",
        )
        self.assertStopped(process)
        threads = _get_threads_stopped_at_breakpoint(process, breakpoint)
        self.assertEqual(len(threads), 1, "Expected exactly one thread to be stopped")
        return threads[0]

    def runToRegex(self, pattern: str, source_spec: SBFileSpec | str = "test.cpp"):
        tgt = self._setupTarget()
        if isinstance(source_spec, str):
            source_spec = SBFileSpec(source_spec)
        breakpoint: SBBreakpoint = tgt.BreakpointCreateBySourceRegex(
            pattern, source_spec
        )
        self.assertGreater(
            breakpoint.GetNumLocations(),
            0,
            f'No location for "{pattern}" ({source_spec})',
        )
        thread = self._launchToBreakpoint(tgt, breakpoint)
        return tgt, thread, breakpoint


class ChildCheck:
    def check(self, test: TestCase, val: SBValue, start: int, msg: str) -> int:
        raise NotImplementedError()


@dataclass
class ValueCheck:
    name: str | re.Pattern | None = None
    summary: str | re.Pattern | None = None
    value: str | re.Pattern | None = None
    type: str | re.Pattern | None = None

    # list[Any] should be list[T] where T: ChildCheck
    children: list["ValueCheck"] | list[Any] | ChildCheck | None = None

    def check(self, test: TestCase, val: SBValue, error_msg=None):
        msg = (
            f"{error_msg}\nChecking SBValue: {val}"
            if error_msg
            else f"Checking SBValue: {val}"
        )

        test.assertSuccess(val.GetError(), msg)

        if self.name:
            test.assertMatch(self.name, val.GetName(), msg)
        if self.value is not None:
            test.assertMatch(self.value, val.GetValue(), msg)
        if self.type:
            test.assertMatch(self.type, val.GetDisplayTypeName(), msg)
        if self.summary:
            test.assertMatch(self.summary, val.GetSummary(), msg)
        if self.children is not None:
            if isinstance(self.children, ChildCheck):
                self.children.check(test, val, 0, msg)
            elif len(self.children) == 0:
                test.assertEqual(val.GetNumChildren(), 0, msg)
            elif isinstance(self.children[0], ValueCheck):
                self.check_simple_children(test, val, msg, self.children)  # type: ignore
            else:
                self.check_complex_children(test, val, msg, self.children)  # type: ignore

    @staticmethod
    def check_simple_children(
        test: TestCase, val: SBValue, msg: str, c: list["ValueCheck"]
    ):
        test.assertEqual(len(c), val.GetNumChildren(), msg)

        for i in range(val.GetNumChildren()):
            expected_child = c[i]
            actual_child = val.GetChildAtIndex(i)
            child_error = f"{msg}\nChecking child at index {i}:"
            expected_child.check(test, actual_child, child_error)

    @staticmethod
    def check_complex_children(
        test: TestCase, val: SBValue, msg: str, c: list["ChildCheck"]
    ):
        start = 0
        for check in c:
            start = check.check(test, val, start, msg)
        test.assertEqual(start, val.GetNumChildren())


class ChildrenStartsWith(ChildCheck):
    def __init__(self, children: list[ValueCheck]) -> None:
        self._children = children

    def check(self, test: TestCase, val: SBValue, start: int, msg: str) -> int:
        test.assertGreaterEqual(val.GetNumChildren() - start, len(self._children), msg)
        for i in range(start, start + len(self._children)):
            expected_child = self._children[i]
            actual_child = val.GetChildAtIndex(i)
            child_error = f"{msg}\nChecking child at index {i}:"
            expected_child.check(test, actual_child, child_error)
        return start + len(self._children)


class ChildrenUnordered(ChildCheck):
    def __init__(self, children: list[ValueCheck]) -> None:
        self._children = {c.name: c for c in children if isinstance(c.name, str)}
        assert len(self._children) == len(children)

    def check(self, test: TestCase, val: SBValue, start: int, msg: str) -> int:
        test.assertEqual(val.GetNumChildren() - start, len(self._children), msg)
        for i in range(start, val.GetNumChildren()):
            actual_child = val.GetChildAtIndex(i)
            name = actual_child.GetName()
            check = self._children.get(name)
            check_msg = f"{msg}\nChecking child '{name}' at index {i}:"
            test.assertIsNotNone(check, check_msg)
            check.check(test, actual_child, check_msg)  # type: ignore
        return val.GetNumChildren()


def _get_threads_stopped_at_breakpoint(
    process: SBProcess, breakpoint: SBBreakpoint
) -> list[SBThread]:
    id = breakpoint.GetID()
    threads = []
    for thread in process:
        if thread.GetStopReason() != lldb.eStopReasonBreakpoint:
            continue
        break_ids = [
            thread.GetStopReasonDataAtIndex(idx)
            for idx in range(0, thread.GetStopReasonDataCount(), 2)
        ]
        if id in break_ids:
            threads.append(thread)
    return threads
