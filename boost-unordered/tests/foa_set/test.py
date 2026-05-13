import testlib
from testlib import ValueCheck
import re
from lldb import SBValue


class TestBoostFoaSet(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self._check_set(self.frame().FindVariable("flat_set"))
        self._check_set(self.frame().FindVariable("node_set"))
        self._check_set(self.frame().FindVariable("cflat_set"))
        self._check_set(self.frame().FindVariable("cnode_set"))

        self.assertVarPath("foit", ValueCheck(summary='"6"'))
        self.assertVarPath("foend", ValueCheck(summary="end", children=[]))

    def _check_set(self, v: SBValue):
        self.assertEqual(v.GetSummary(), "size=5")
        self.assertEqual(v.GetNumChildren(), 5)
        name_re = re.compile(r"^\[\d\]+$")
        s = set()
        for i in range(v.GetNumChildren()):
            c = v.GetChildAtIndex(i)
            s.add(c.GetSummary())
            self.assertMatch(name_re, c.GetName())

        self.assertEqual(
            s,
            {
                '"0"',
                '"2"',
                '"4"',
                '"6"',
                '"8"',
            },
        )
